import json
import logging
import threading
from datetime import datetime

import django_rq
import httplib2
import redis
from django.conf import settings
from django.utils import timezone
from google.oauth2 import service_account
from google_auth_httplib2 import AuthorizedHttp
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GCPDiscoveryService:
    def __init__(self, organization):
        self.organization = organization
        self.credentials = None
        self.log_messages = []
        self.redis_conn = None
        self.log_key = None
        self.stats_key = None
        self.discovery_log = None
        self.stats = {
            'projects': 0,
            'instances': 0,
            'networks': 0,
            'databases': 0,
            'buckets': 0,
            'clusters': 0,
            'total': 0,
        }
        self._lock = threading.Lock()

        # Try to connect to Redis
        try:

            # Try multiple ways to get the connection
            try:
                self.redis_conn = django_rq.get_connection('default')
            except Exception:
                # Fallback: try getting it from the queue object directly
                self.redis_conn = django_rq.get_queue('default').connection

        except Exception as e:
            logger.warning(f'Failed to connect to Redis: {e} - trying manual connection')
            try:

                config = settings.RQ_QUEUES.get('default', {})
                if config:
                    self.redis_conn = redis.Redis(
                        host=config.get('HOST', 'localhost'),
                        port=config.get('PORT', 6379),
                        db=config.get('DB', 0),
                        password=config.get('PASSWORD'),
                        ssl=config.get('SSL', False),
                        socket_timeout=config.get('DEFAULT_TIMEOUT', 300),
                    )
            except Exception as e2:
                logger.error(f'Manual Redis connection also failed: {e2}')

    def _setup_redis(self, log_id):
        if self.redis_conn:
            self.log_key = f'netbox:gcp:discovery:{log_id}:logs'
            self.stats_key = f'netbox:gcp:discovery:{log_id}:stats'
            # expire after 24 hours
            self.redis_conn.expire(self.log_key, 86400)
            self.redis_conn.expire(self.stats_key, 86400)

    def log(self, message, level='info'):
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f'[{timestamp}] {message}'

        if self.redis_conn and self.log_key:
            try:
                self.redis_conn.rpush(self.log_key, log_entry)
            except Exception:
                # Fallback to memory
                with self._lock:
                    self.log_messages.append(log_entry)
        else:
            with self._lock:
                self.log_messages.append(log_entry)

        if level == 'error':
            logger.error(message)
        elif level == 'warning':
            logger.warning(message)
        else:
            logger.info(message)

    def get_log_output(self):
        if self.redis_conn and self.log_key:
            try:
                logs = self.redis_conn.lrange(self.log_key, 0, -1)
                return '\n'.join([log_line.decode('utf-8') for log_line in logs])
            except Exception:
                pass
        return '\n'.join(self.log_messages)

    def _increment_stat(self, resource_type):
        if self.redis_conn and self.stats_key:
            try:
                self.redis_conn.hincrby(self.stats_key, resource_type, 1)
                # usage stats are also memory tracked for final sync if needed,
                # or we just rely on redis.
                # Let's keep memory cache updated too for safety/easy access
                with self._lock:
                    if resource_type in self.stats:
                        self.stats[resource_type] += 1
            except Exception:
                with self._lock:
                    if resource_type in self.stats:
                        self.stats[resource_type] += 1
        else:
            with self._lock:
                if resource_type in self.stats:
                    self.stats[resource_type] += 1

    def _sync_stats_from_redis(self):
        if self.redis_conn and self.stats_key:
            try:
                redis_stats = self.redis_conn.hgetall(self.stats_key)
                with self._lock:
                    for k, v in redis_stats.items():
                        k_str = k.decode('utf-8')
                        if k_str in self.stats:
                            self.stats[k_str] = int(v)
            except Exception:
                pass

    def process_project(self, project):
        try:
            # check cancellation (from redis, usually)
            if self.redis_conn and self.discovery_log:
                if self.redis_conn.get(f'netbox:gcp:discovery:{self.discovery_log.pk}:cancel'):
                    self.organization.cancel_requested = True

            if self.organization.cancel_requested:
                return

            self.log(f'Discovering resources in project: {project.project_id}')
            print(f"DEBUG: [{project.project_id}] Starting discovery", flush=True)

            enabled_services = self._get_enabled_services(project.project_id)

            def is_enabled(service_name):
                if enabled_services is None:
                    return True
                return service_name in enabled_services

            try:
                if self.organization.discover_networking and is_enabled('compute.googleapis.com'):
                    print(f"DEBUG: [{project.project_id}] Discovering Networking", flush=True)
                    self.discover_vpc_networks(project)
                    self.discover_subnets(project)
                    self.discover_firewall_rules(project)
                    self.discover_cloud_routers(project)
                    self.discover_cloud_nats(project)
                    self.discover_vpn_gateways(project)
                    self.discover_external_vpn_gateways(project)
                    self.discover_vpn_tunnels(project)
                    self.discover_load_balancers(project)
                    self.discover_service_attachments(project)
                    self.discover_psc_endpoints(project)
                    self.discover_interconnect_attachments(project)

                    if is_enabled('networkconnectivity.googleapis.com'):
                        self.discover_ncc_hubs(project)
                        self.discover_ncc_spokes(project)

                    if is_enabled('dns.googleapis.com'):
                        print(f"DEBUG: [{project.project_id}] Discovering DNS", flush=True)
                        self.discover_cloud_dns_zones(project)

                    if self.organization.cancel_requested:
                        return

                if self.organization.discover_compute and is_enabled('compute.googleapis.com'):
                    print(f"DEBUG: [{project.project_id}] Discovering Compute", flush=True)
                    self.discover_compute_instances(project)
                    self.discover_instance_templates(project)
                    self.discover_instance_groups(project)
                    self.discover_persistent_disks(project)
                    if self.organization.cancel_requested:
                        return

                if self.organization.discover_databases:
                    print(f"DEBUG: [{project.project_id}] Discovering Databases", flush=True)
                    if is_enabled('sqladmin.googleapis.com'):
                        self.discover_cloud_sql(project)
                    if is_enabled('spanner.googleapis.com'):
                        self.discover_cloud_spanner(project)
                    if is_enabled('firestore.googleapis.com'):
                        self.discover_firestore(project)
                    if is_enabled('bigtableadmin.googleapis.com'):
                        self.discover_bigtable(project)
                    if is_enabled('redis.googleapis.com'):
                        self.discover_memorystore(project)
                    if self.organization.cancel_requested:
                        return

                if self.organization.discover_storage and is_enabled('storage.googleapis.com'):
                    print(f"DEBUG: [{project.project_id}] Discovering Storage", flush=True)
                    self.discover_storage_buckets(project)
                    if self.organization.cancel_requested:
                        return

                if self.organization.discover_kubernetes and is_enabled('container.googleapis.com'):
                    print(f"DEBUG: [{project.project_id}] Discovering Kubernetes", flush=True)
                    self.discover_gke_clusters(project)
                    if self.organization.cancel_requested:
                        return

                if self.organization.discover_serverless:
                    print(f"DEBUG: [{project.project_id}] Discovering Serverless", flush=True)
                    if is_enabled('cloudfunctions.googleapis.com'):
                        print(f"DEBUG: [{project.project_id}] Discovering Cloud Functions", flush=True)
                        self.discover_cloud_functions(project)
                    if is_enabled('run.googleapis.com'):
                        print(f"DEBUG: [{project.project_id}] Discovering Cloud Run", flush=True)
                        self.discover_cloud_run(project)
                    if is_enabled('pubsub.googleapis.com'):
                        print(f"DEBUG: [{project.project_id}] Discovering PubSub", flush=True)
                        self.discover_pubsub(project)
                    if is_enabled('secretmanager.googleapis.com'):
                        print(f"DEBUG: [{project.project_id}] Discovering Secret Manager", flush=True)
                        self.discover_secret_manager_secrets(project)
                    if self.organization.cancel_requested:
                        return

                if self.organization.discover_iam and is_enabled('iam.googleapis.com'):
                    print(f"DEBUG: [{project.project_id}] Discovering IAM", flush=True)
                    self.discover_service_accounts(project)
                    self.discover_iam_roles(project)
                    self.discover_iam_policy(project)

            except Exception as e:
                self.log(f'Error in project {project.project_id} module: {str(e)}', 'error')

        except Exception as e:
            self.log(f'Error discovering project {project.project_id}: {str(e)}', 'error')
        except BaseException as e:
            self.log(f'Critical error discovering project {project.project_id}: {str(e)}', 'error')

    def _handle_http_error(self, context, e, resource_id=None):

        if not isinstance(e, HttpError):
            return False

        try:
            content = json.loads(e.content.decode('utf-8'))
            reason = content.get('error', {}).get('errors', [{}])[0].get('reason')
            message = content.get('error', {}).get('message')
        except Exception:
            reason = 'unknown'
            message = str(e)

        if reason in {'notFound', 'permissionDenied', 'forbidden'}:
            suffix = f' for {resource_id}' if resource_id else ''
            self.log(f'{context}{suffix}: {message}', 'warning')
            return True

        return False

    def setup_credentials(self):
        try:

            sa_info = self.organization.get_service_account_info()
            if not sa_info:
                raise ValueError('Invalid service account JSON')

            self.credentials = service_account.Credentials.from_service_account_info(
                sa_info,
                scopes=[
                    'https://www.googleapis.com/auth/cloud-platform',
                    'https://www.googleapis.com/auth/compute',
                    'https://www.googleapis.com/auth/sqlservice.admin',
                    'https://www.googleapis.com/auth/devstorage.read_only',
                ],
            )
            self.log('Successfully authenticated with service account')
            return True
        except Exception as e:
            self.log(f'Failed to setup credentials: {str(e)}', 'error')
            return False

    def _create_service(self, service_name, version):

        # Set timeout to prevent hanging threads
        http = httplib2.Http(timeout=60)

        # Authorize the http object (http and credentials args are mutually exclusive in build())
        if self.credentials:
            http = AuthorizedHttp(self.credentials, http=http)

        return build(service_name, version, http=http, cache_discovery=False)

    def _normalize_org_id(self):
        org_id = str(self.organization.organization_id).strip()
        if '/' in org_id:
            org_id = org_id.split('/')[-1]
        return org_id

    def _list_projects_by_parent(self, service, parent_type, parent_id):
        projects = []
        page_token = None
        filter_str = f'parent.type:{parent_type} parent.id:{parent_id}'

        while True:
            request = service.projects().list(filter=filter_str, pageSize=1000, pageToken=page_token)
            response = request.execute()
            projects.extend(response.get('projects', []))
            page_token = response.get('nextPageToken')
            if not page_token:
                break

        return projects

    def _list_folders(self, parent):

        folders = []
        page_token = None
        service = self._create_service('cloudresourcemanager', 'v2')

        while True:
            request = service.folders().list(parent=parent, pageToken=page_token)
            response = request.execute()
            folders.extend(response.get('folders', []))
            page_token = response.get('nextPageToken')
            if not page_token:
                break

        return folders

    def _get_enabled_services(self, project_id):

        try:
            service = self._create_service('serviceusage', 'v1')
            request = service.services().list(parent=f'projects/{project_id}', filter='state:ENABLED', pageSize=200)
            enabled_services = set()
            while request is not None:
                response = request.execute()
                for svc in response.get('services', []):
                    # Service name is in the format projects/{project}/services/{service_name}
                    name = svc.get('name', '').split('/')[-1]
                    if name:
                        enabled_services.add(name)
                request = service.services().list_next(previous_request=request, previous_response=response)
            return enabled_services
        except Exception as e:
            # If we can't list services, return None to imply "unknown/try all"
            self.log(f'Warning: Could not list enabled services for {project_id}: {e}', 'warning')
            return None

    def _finish_discovery(self, discovery_log):
        self._sync_stats_from_redis()
        self.stats['total'] = sum(
            [
                self.stats['projects'],
                self.stats['instances'],
                self.stats['networks'],
                self.stats['databases'],
                self.stats['buckets'],
                self.stats['clusters'],
            ]
        )

        discovery_log.status = 'completed'
        discovery_log.completed_at = timezone.now()
        discovery_log.projects_discovered = self.stats['projects']
        discovery_log.instances_discovered = self.stats['instances']
        discovery_log.networks_discovered = self.stats['networks']
        discovery_log.databases_discovered = self.stats['databases']
        discovery_log.buckets_discovered = self.stats['buckets']
        discovery_log.clusters_discovered = self.stats['clusters']
        discovery_log.total_resources = self.stats['total']
        discovery_log.log_output = self.get_log_output()
        discovery_log.save()

        self.organization.discovery_status = 'completed'
        self.organization.last_discovery = timezone.now()
        self.organization.discovery_error = ''
        self.organization.save()

        if self.redis_conn:
            self.redis_conn.delete(self.log_key)
            self.redis_conn.delete(self.stats_key)
            batches_key = f'netbox:gcp:discovery:{discovery_log.pk}:batches'
            self.redis_conn.delete(f'{batches_key}:total')
            self.redis_conn.delete(f'{batches_key}:done')

        self.log(f'Discovery completed. Total resources: {self.stats["total"]}')

    def discover_all(self):
        from .models import DiscoveryLog

        discovery_log = DiscoveryLog.objects.create(organization=self.organization, status='running')
        self.discovery_log = discovery_log
        self._setup_redis(discovery_log.pk)

        self.organization.cancel_requested = False
        self.organization.save(update_fields=['cancel_requested'])

        self.organization.discovery_status = 'running'
        self.organization.save()

        try:
            if not self.setup_credentials():
                raise Exception('Failed to authenticate with GCP')

            self.log('Starting discovery for organization: ' + self.organization.name)

            projects = self.discover_projects()

            if not projects:
                self.log('No projects found, finishing.', 'info')
                self._finish_discovery(discovery_log)
                return True

            # 2. Chunk projects for parallel batch processing
            # 10 projects per batch to distribute better across workers
            batch_size = 10
            project_pks = [p.pk for p in projects]
            chunks = [project_pks[i : i + batch_size] for i in range(0, len(project_pks), batch_size)]

            total_batches = len(chunks)
            self.log(f'Split {len(projects)} projects into {total_batches} batches for workers.')

            if self.redis_conn:
                batches_key = f'netbox:gcp:discovery:{discovery_log.pk}:batches'
                self.redis_conn.set(f'{batches_key}:total', total_batches)
                self.redis_conn.set(f'{batches_key}:done', 0)
                self.redis_conn.expire(f'{batches_key}:total', 86400)
                self.redis_conn.expire(f'{batches_key}:done', 86400)

            # 3. Enqueue batches
            queue = django_rq.get_queue('default')
            for chunk in chunks:
                queue.enqueue(
                    process_discovery_batch,
                    organization_id=self.organization.pk,
                    discovery_log_id=discovery_log.pk,
                    project_pks=chunk,
                )

            return True
        except Exception as e:
            error_msg = str(e)
            self.log(f'Discovery failed: {error_msg}', 'error')

            discovery_log.status = 'failed'
            discovery_log.completed_at = timezone.now()
            discovery_log.error_message = error_msg
            discovery_log.log_output = self.get_log_output()
            discovery_log.save()

            self.organization.discovery_status = 'failed'
            self.organization.discovery_error = error_msg
            self.organization.save()

            return False

    def discover_projects(self):
        from .models import GCPProject

        self.log('Discovering projects...')
        projects = []

        # Cache for folder ownership to avoid repeated API calls
        # Key: folder_id (str), Value: bool (is_owned_by_org)
        folder_ownership_cache = {}

        try:
            service = self._create_service('cloudresourcemanager', 'v1')

            # List all projects accessible to the service account
            request = service.projects().list()
            while request is not None:
                response = request.execute()
                for proj in response.get('projects', []):
                    # Filter by organization ID
                    is_owned_by_org = False
                    parent = proj.get('parent', {})
                    parent_type = parent.get('type')
                    parent_id = str(parent.get('id', ''))

                    # 1. Direct child of the organization
                    if parent_type == 'organization' and parent_id == str(self.organization.organization_id):
                        is_owned_by_org = True
                    # 2. Child of a Folder (nested hierarchy)
                    elif parent_type == 'folder':
                        # Check cache first
                        if parent_id in folder_ownership_cache:
                            is_owned_by_org = folder_ownership_cache[parent_id]
                        else:
                            try:
                                # Use getAncestry to verify organization ownership
                                ancestry = service.projects().getAncestry(projectId=proj['projectId']).execute()
                                is_folder_in_org = False
                                found_folders = []

                                # Walk up the ancestry
                                for ancestor in ancestry.get('ancestor', []):
                                    resource = ancestor.get('resourceId', {})
                                    r_type = resource.get('type')
                                    r_id = str(resource.get('id', ''))

                                    if r_type == 'organization' and r_id == str(self.organization.organization_id):
                                        is_folder_in_org = True
                                    elif r_type == 'folder':
                                        found_folders.append(r_id)

                                # Update cache for all intermediate folders found in this path
                                for f_id in found_folders:
                                    folder_ownership_cache[f_id] = is_folder_in_org

                                is_owned_by_org = is_folder_in_org

                            except Exception:
                                # If we cannot verify ancestry, skip the project to be safe
                                pass

                    if not is_owned_by_org:
                        continue

                    project, created = GCPProject.objects.update_or_create(
                        project_id=proj['projectId'],
                        defaults={
                            'organization': self.organization,
                            'name': proj.get('name', proj['projectId']),
                            'project_number': proj.get('projectNumber', ''),
                            'status': proj.get('lifecycleState', 'ACTIVE'),
                            'labels': proj.get('labels', {}),
                            'discovered': True,
                            'last_synced': timezone.now(),
                        },
                    )
                    projects.append(project)
                    self._increment_stat('projects')
                    action = 'Created' if created else 'Updated'
                    self.log(f'{action} project: {project.project_id}')

                request = service.projects().list_next(previous_request=request, previous_response=response)

            if not projects:
                self.log('No projects found', 'info')

        except HttpError as e:
            if not self._handle_http_error('Discovering projects', e):
                self.log(f'Error discovering projects: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering projects: {str(e)}', 'error')

        return projects

    def discover_vpc_networks(self, project):
        from .models import VPCNetwork

        self.log(f'Discovering VPC networks in {project.project_id}...')

        try:
            service = self._create_service('compute', 'v1')
            request = service.networks().list(project=project.project_id)

            while request is not None:
                response = request.execute()

                for network in response.get('items', []):
                    vpc, created = VPCNetwork.objects.update_or_create(
                        project=project,
                        name=network['name'],
                        defaults={
                            'auto_create_subnetworks': network.get('autoCreateSubnetworks', False),
                            'routing_mode': network.get('routingConfig', {}).get('routingMode', 'REGIONAL'),
                            'mtu': network.get('mtu', 1460),
                            'self_link': network.get('selfLink', ''),
                            'discovered': True,
                            'last_synced': timezone.now(),
                        },
                    )
                    self._increment_stat('networks')
                    self.log(f'{"Created" if created else "Updated"} VPC: {vpc.name}')

                request = service.networks().list_next(previous_request=request, previous_response=response)

        except HttpError as e:
            if not self._handle_http_error('Discovering VPC networks', e, project.project_id):
                self.log(f'Error discovering VPC networks: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering VPC networks: {str(e)}', 'error')

    def discover_subnets(self, project):
        from .models import Subnet, VPCNetwork

        self.log(f'Discovering subnets in {project.project_id}...')

        try:
            service = self._create_service('compute', 'v1')
            request = service.subnetworks().aggregatedList(project=project.project_id)

            while request is not None:
                response = request.execute()

                for region, subnets_data in response.get('items', {}).items():
                    for subnet in subnets_data.get('subnetworks', []):
                        network_name = subnet.get('network', '').split('/')[-1]
                        try:
                            network = VPCNetwork.objects.get(project=project, name=network_name)
                        except VPCNetwork.DoesNotExist:
                            continue

                        region_name = subnet.get('region', '').split('/')[-1]

                        sub, created = Subnet.objects.update_or_create(
                            project=project,
                            network=network,
                            name=subnet['name'],
                            defaults={
                                'region': region_name,
                                'ip_cidr_range': subnet.get('ipCidrRange', ''),
                                'gateway_address': subnet.get('gatewayAddress'),
                                'private_ip_google_access': subnet.get('privateIpGoogleAccess', False),
                                'purpose': subnet.get('purpose', 'PRIVATE'),
                                'self_link': subnet.get('selfLink', ''),
                                'discovered': True,
                                'last_synced': timezone.now(),
                            },
                        )
                        self.log(f'{"Created" if created else "Updated"} subnet: {sub.name}')

                request = service.subnetworks().aggregatedList_next(
                    previous_request=request, previous_response=response
                )

        except HttpError as e:
            if not self._handle_http_error('Discovering subnets', e, project.project_id):
                self.log(f'Error discovering subnets: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering subnets: {str(e)}', 'error')

    def discover_firewall_rules(self, project):
        from .models import FirewallRule, VPCNetwork

        self.log(f'Discovering firewall rules in {project.project_id}...')

        try:
            service = self._create_service('compute', 'v1')
            request = service.firewalls().list(project=project.project_id)

            while request is not None:
                response = request.execute()

                for fw in response.get('items', []):
                    network_name = fw.get('network', '').split('/')[-1]
                    try:
                        network = VPCNetwork.objects.get(project=project, name=network_name)
                    except VPCNetwork.DoesNotExist:
                        continue

                    action = 'allow' if fw.get('allowed') else 'deny'

                    rule, created = FirewallRule.objects.update_or_create(
                        project=project,
                        network=network,
                        name=fw['name'],
                        defaults={
                            'direction': fw.get('direction', 'INGRESS'),
                            'priority': fw.get('priority', 1000),
                            'action': action,
                            'source_ranges': fw.get('sourceRanges'),
                            'destination_ranges': fw.get('destinationRanges'),
                            'source_tags': fw.get('sourceTags'),
                            'target_tags': fw.get('targetTags'),
                            'allowed': fw.get('allowed'),
                            'denied': fw.get('denied'),
                            'disabled': fw.get('disabled', False),
                            'self_link': fw.get('selfLink', ''),
                            'discovered': True,
                            'last_synced': timezone.now(),
                        },
                    )
                    self.log(f'{"Created" if created else "Updated"} firewall rule: {rule.name}')

                request = service.firewalls().list_next(previous_request=request, previous_response=response)

        except HttpError as e:
            if not self._handle_http_error('Discovering firewall rules', e, project.project_id):
                self.log(f'Error discovering firewall rules: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering firewall rules: {str(e)}', 'error')

    def discover_cloud_routers(self, project):
        from .models import CloudRouter, VPCNetwork

        self.log(f'Discovering Cloud Routers in {project.project_id}...')

        try:
            service = self._create_service('compute', 'v1')
            request = service.routers().aggregatedList(project=project.project_id)

            while request is not None:
                response = request.execute()

                for region, routers_data in response.get('items', {}).items():
                    for router in routers_data.get('routers', []):
                        network_name = router.get('network', '').split('/')[-1]
                        try:
                            network = VPCNetwork.objects.get(project=project, name=network_name)
                        except VPCNetwork.DoesNotExist:
                            continue

                        region_name = router.get('region', '').split('/')[-1]
                        bgp = router.get('bgp', {})

                        cr, created = CloudRouter.objects.update_or_create(
                            project=project,
                            network=network,
                            name=router['name'],
                            defaults={
                                'region': region_name,
                                'asn': bgp.get('asn', 64512),
                                'advertise_mode': bgp.get('advertiseMode', 'DEFAULT'),
                                'advertised_groups': bgp.get('advertisedGroups'),
                                'advertised_ip_ranges': bgp.get('advertisedIpRanges'),
                                'self_link': router.get('selfLink', ''),
                                'discovered': True,
                                'last_synced': timezone.now(),
                            },
                        )
                        self.log(f'{"Created" if created else "Updated"} Cloud Router: {cr.name}')

                request = service.routers().aggregatedList_next(previous_request=request, previous_response=response)

        except HttpError as e:
            if not self._handle_http_error('Discovering Cloud Routers', e, project.project_id):
                self.log(f'Error discovering Cloud Routers: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering Cloud Routers: {str(e)}', 'error')

    def discover_vpn_gateways(self, project):
        from .models import VPNGateway, VPCNetwork

        self.log(f'Discovering VPN Gateways in {project.project_id}...')

        try:
            service = self._create_service('compute', 'v1')
            request = service.vpnGateways().aggregatedList(project=project.project_id)

            while request is not None:
                response = request.execute()

                for region, gateways_data in response.get('items', {}).items():
                    for gw in gateways_data.get('vpnGateways', []):
                        network_name = gw.get('network', '').split('/')[-1]
                        try:
                            network = VPCNetwork.objects.get(project=project, name=network_name)
                        except VPCNetwork.DoesNotExist:
                            continue

                        region_name = gw.get('region', '').split('/')[-1]

                        vpn_gw, created = VPNGateway.objects.update_or_create(
                            project=project,
                            network=network,
                            name=gw['name'],
                            defaults={
                                'region': region_name,
                                'gateway_type': 'HA_VPN',
                                'ip_addresses': [iface.get('ipAddress') for iface in gw.get('vpnInterfaces', [])],
                                'labels': gw.get('labels'),
                                'self_link': gw.get('selfLink', ''),
                                'discovered': True,
                                'last_synced': timezone.now(),
                            },
                        )
                        self.log(f'{"Created" if created else "Updated"} VPN Gateway: {vpn_gw.name}')

                request = service.vpnGateways().aggregatedList_next(
                    previous_request=request, previous_response=response
                )

        except HttpError as e:
            if not self._handle_http_error('Discovering VPN Gateways', e, project.project_id):
                self.log(f'Error discovering VPN Gateways: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering VPN Gateways: {str(e)}', 'error')

    def discover_vpn_tunnels(self, project):
        from .models import VPNTunnel, VPNGateway, CloudRouter

        self.log(f'Discovering VPN Tunnels in {project.project_id}...')

        try:
            service = self._create_service('compute', 'v1')
            request = service.vpnTunnels().aggregatedList(project=project.project_id)

            while request is not None:
                response = request.execute()

                for region, tunnels_data in response.get('items', {}).items():
                    for tunnel in tunnels_data.get('vpnTunnels', []):
                        region_name = tunnel.get('region', '').split('/')[-1]

                        vpn_gateway = None
                        vpn_gw_name = tunnel.get('vpnGateway', '').split('/')[-1]
                        if vpn_gw_name:
                            try:
                                vpn_gateway = VPNGateway.objects.get(project=project, name=vpn_gw_name)
                            except VPNGateway.DoesNotExist:
                                pass

                        router = None
                        router_name = tunnel.get('router', '').split('/')[-1]
                        if router_name:
                            try:
                                router = CloudRouter.objects.get(project=project, name=router_name)
                            except CloudRouter.DoesNotExist:
                                pass

                        tun, created = VPNTunnel.objects.update_or_create(
                            project=project,
                            name=tunnel['name'],
                            defaults={
                                'region': region_name,
                                'vpn_gateway': vpn_gateway,
                                'vpn_gateway_interface': tunnel.get('vpnGatewayInterface', 0),
                                'peer_ip': tunnel.get('peerIp'),
                                'shared_secret_hash': tunnel.get('sharedSecretHash', ''),
                                'ike_version': tunnel.get('ikeVersion', 2),
                                'local_traffic_selector': tunnel.get('localTrafficSelector'),
                                'remote_traffic_selector': tunnel.get('remoteTrafficSelector'),
                                'router': router,
                                'status': tunnel.get('status', 'UNKNOWN'),
                                'detailed_status': tunnel.get('detailedStatus', ''),
                                'labels': tunnel.get('labels'),
                                'self_link': tunnel.get('selfLink', ''),
                                'discovered': True,
                                'last_synced': timezone.now(),
                            },
                        )
                        self.log(f'{"Created" if created else "Updated"} VPN Tunnel: {tun.name}')

                request = service.vpnTunnels().aggregatedList_next(previous_request=request, previous_response=response)

        except HttpError as e:
            if not self._handle_http_error('Discovering VPN Tunnels', e, project.project_id):
                self.log(f'Error discovering VPN Tunnels: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering VPN Tunnels: {str(e)}', 'error')

    def discover_compute_instances(self, project):
        from .models import ComputeInstance

        self.log(f'Discovering Compute instances in {project.project_id}...')

        try:
            service = self._create_service('compute', 'v1')
            request = service.instances().aggregatedList(project=project.project_id)

            while request is not None:
                response = request.execute()

                # Check for warnings (e.g. unreachable zones)
                if 'warning' in response:
                    warn_msg = response['warning'].get('message')
                    self.log(f'Warning during Compute discovery in {project.project_id}: {warn_msg}', 'warning')

                for zone, instances_data in response.get('items', {}).items():
                    if 'warning' in instances_data:
                        self.log(
                            f'Warning for zone {zone} in {project.project_id}: '
                            f'{instances_data["warning"].get("message")}',
                            'warning',
                        )

                    for instance in instances_data.get('instances', []):
                        zone_name = instance.get('zone', '').split('/')[-1]
                        machine_type = instance.get('machineType', '').split('/')[-1]

                        internal_ip = None
                        external_ip = None
                        network = ''
                        subnet = ''

                        network_interfaces = instance.get('networkInterfaces', [])
                        if network_interfaces:
                            ni = network_interfaces[0]
                            internal_ip = ni.get('networkIP')
                            network = ni.get('network', '').split('/')[-1]
                            subnet = ni.get('subnetwork', '').split('/')[-1]

                            access_configs = ni.get('accessConfigs', [])
                            if access_configs:
                                external_ip = access_configs[0].get('natIP')

                        disk_size = 0
                        image = ''
                        disks = instance.get('disks', [])
                        if disks:
                            boot_disk = next((d for d in disks if d.get('boot')), None)
                            if boot_disk:
                                disk_size = boot_disk.get('diskSizeGb', 0)
                                if 'initializeParams' in boot_disk and 'sourceImage' in boot_disk['initializeParams']:
                                    image = boot_disk['initializeParams']['sourceImage'].split('/')[-1]
                                elif 'licenses' in boot_disk and boot_disk['licenses']:
                                    image = boot_disk['licenses'][0].split('/')[-1]
                                else:
                                    # Fallback: try to infer from source disk name if it doesn't match instance name
                                    src_disk = boot_disk.get('source', '').split('/')[-1]
                                    if src_disk and src_disk != instance['name']:
                                        image = src_disk

                        inst, created = ComputeInstance.objects.update_or_create(
                            project=project,
                            name=instance['name'],
                            zone=zone_name,
                            defaults={
                                'machine_type': machine_type,
                                'status': instance.get('status', 'UNKNOWN'),
                                'internal_ip': internal_ip,
                                'external_ip': external_ip,
                                'network': network,
                                'subnet': subnet,
                                'disk_size_gb': disk_size,
                                'image': image,
                                'labels': instance.get('labels'),
                                'self_link': instance.get('selfLink', ''),
                                'discovered': True,
                                'last_synced': timezone.now(),
                            },
                        )
                        self._increment_stat('instances')
                        self.log(f'{"Created" if created else "Updated"} instance: {inst.name}')

                request = service.instances().aggregatedList_next(previous_request=request, previous_response=response)

        except HttpError as e:
            if not self._handle_http_error('Discovering Compute instances', e, project.project_id):
                self.log(f'Error discovering Compute instances: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering Compute instances: {str(e)}', 'error')

    def discover_instance_templates(self, project):
        from .models import InstanceTemplate

        self.log(f'Discovering Instance Templates in {project.project_id}...')

        try:
            service = self._create_service('compute', 'v1')
            request = service.instanceTemplates().list(project=project.project_id)

            while request is not None:
                response = request.execute()

                for template in response.get('items', []):
                    props = template.get('properties', {})
                    machine_type = props.get('machineType', '').split('/')[-1]

                    disk_size = 10
                    image = ''
                    disks = props.get('disks', [])
                    if disks:
                        boot_disk = next((d for d in disks if d.get('boot')), None)
                        if boot_disk:
                            init_params = boot_disk.get('initializeParams', {})
                            disk_size = init_params.get('diskSizeGb', 10)
                            image = init_params.get('sourceImage', '').split('/')[-1]

                    network = ''
                    subnet = ''
                    network_interfaces = props.get('networkInterfaces', [])
                    if network_interfaces:
                        ni = network_interfaces[0]
                        network = ni.get('network', '').split('/')[-1]
                        subnet = ni.get('subnetwork', '').split('/')[-1]

                    tmpl, created = InstanceTemplate.objects.update_or_create(
                        project=project,
                        name=template['name'],
                        defaults={
                            'machine_type': machine_type,
                            'disk_size_gb': disk_size,
                            'image': image,
                            'network': network,
                            'subnet': subnet,
                            'labels': props.get('labels'),
                            'self_link': template.get('selfLink', ''),
                            'discovered': True,
                            'last_synced': timezone.now(),
                        },
                    )
                    self.log(f'{"Created" if created else "Updated"} template: {tmpl.name}')

                request = service.instanceTemplates().list_next(previous_request=request, previous_response=response)

        except HttpError as e:
            if not self._handle_http_error('Discovering Instance Templates', e, project.project_id):
                self.log(f'Error discovering Instance Templates: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering Instance Templates: {str(e)}', 'error')

    def discover_persistent_disks(self, project):
        from .models import PersistentDisk

        self.log(f'Discovering Persistent Disks in {project.project_id}...')

        try:
            service = self._create_service('compute', 'v1')
            request = service.disks().aggregatedList(project=project.project_id)

            while request is not None:
                response = request.execute()

                for zone, disks_data in response.get('items', {}).items():
                    for disk in disks_data.get('disks', []):
                        zone_name = disk.get('zone', '').split('/')[-1]
                        disk_type = disk.get('type', '').split('/')[-1]

                        pd, created = PersistentDisk.objects.update_or_create(
                            project=project,
                            name=disk['name'],
                            zone=zone_name,
                            defaults={
                                'disk_type': disk_type,
                                'size_gb': int(disk.get('sizeGb', 10)),
                                'status': disk.get('status', 'UNKNOWN'),
                                'source_image': disk.get('sourceImage', '').split('/')[-1],
                                'users': disk.get('users'),
                                'self_link': disk.get('selfLink', ''),
                                'discovered': True,
                                'last_synced': timezone.now(),
                            },
                        )
                        self.log(f'{"Created" if created else "Updated"} disk: {pd.name}')

                request = service.disks().aggregatedList_next(previous_request=request, previous_response=response)

        except HttpError as e:
            if not self._handle_http_error('Discovering Persistent Disks', e, project.project_id):
                self.log(f'Error discovering Persistent Disks: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering Persistent Disks: {str(e)}', 'error')

    def discover_cloud_sql(self, project):
        from .models import CloudSQLInstance

        self.log(f'Discovering Cloud SQL instances in {project.project_id}...')

        try:
            service = self._create_service('sqladmin', 'v1')
            request = service.instances().list(project=project.project_id)
            response = request.execute()

            for instance in response.get('items', []):
                settings = instance.get('settings', {})

                db_type = 'MYSQL'
                db_version = instance.get('databaseVersion', '')
                if 'POSTGRES' in db_version:
                    db_type = 'POSTGRESQL'
                elif 'SQLSERVER' in db_version:
                    db_type = 'SQLSERVER'

                sql, created = CloudSQLInstance.objects.update_or_create(
                    project=project,
                    name=instance['name'],
                    defaults={
                        'region': instance.get('region', ''),
                        'database_type': db_type,
                        'database_version': db_version,
                        'tier': settings.get('tier', ''),
                        'storage_size_gb': int(settings.get('dataDiskSizeGb', 10)),
                        'storage_type': settings.get('dataDiskType', 'SSD'),
                        'status': instance.get('state', 'UNKNOWN'),
                        'ip_addresses': instance.get('ipAddresses'),
                        'connection_name': instance.get('connectionName', ''),
                        'self_link': instance.get('selfLink', ''),
                        'discovered': True,
                        'last_synced': timezone.now(),
                    },
                )
                self._increment_stat('databases')
                self.log(f'{"Created" if created else "Updated"} Cloud SQL: {sql.name}')

        except HttpError as e:
            if not self._handle_http_error('Discovering Cloud SQL', e, project.project_id):
                self.log(f'Error discovering Cloud SQL: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering Cloud SQL: {str(e)}', 'error')

    def discover_cloud_spanner(self, project):
        from .models import CloudSpannerInstance

        self.log(f'Discovering Cloud Spanner instances in {project.project_id}...')

        try:
            service = self._create_service('spanner', 'v1')
            parent = f'projects/{project.project_id}'
            request = service.projects().instances().list(parent=parent)
            response = request.execute()

            for instance in response.get('instances', []):
                name = instance.get('name', '').split('/')[-1]

                spanner, created = CloudSpannerInstance.objects.update_or_create(
                    project=project,
                    name=name,
                    defaults={
                        'config': instance.get('config', '').split('/')[-1],
                        'display_name': instance.get('displayName', ''),
                        'node_count': instance.get('nodeCount', 0),
                        'processing_units': instance.get('processingUnits', 0),
                        'status': instance.get('state', 'UNKNOWN'),
                        'discovered': True,
                        'last_synced': timezone.now(),
                    },
                )
                self._increment_stat('databases')
                self.log(f'{"Created" if created else "Updated"} Spanner: {spanner.name}')

        except HttpError as e:
            if not self._handle_http_error('Discovering Cloud Spanner', e, project.project_id):
                self.log(f'Error discovering Cloud Spanner: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering Cloud Spanner: {str(e)}', 'error')

    def discover_storage_buckets(self, project):
        from .models import CloudStorageBucket

        self.log(f'Discovering Cloud Storage buckets in {project.project_id}...')

        try:
            service = self._create_service('storage', 'v1')
            request = service.buckets().list(project=project.project_id)

            while request is not None:
                response = request.execute()

                for bucket in response.get('items', []):
                    versioning = bucket.get('versioning', {})

                    bkt, created = CloudStorageBucket.objects.update_or_create(
                        name=bucket['name'],
                        defaults={
                            'project': project,
                            'location': bucket.get('location', ''),
                            'storage_class': bucket.get('storageClass', 'STANDARD'),
                            'versioning_enabled': versioning.get('enabled', False),
                            'lifecycle_rules': bucket.get('lifecycle', {}).get('rule'),
                            'labels': bucket.get('labels'),
                            'self_link': bucket.get('selfLink', ''),
                            'discovered': True,
                            'last_synced': timezone.now(),
                        },
                    )
                    self._increment_stat('buckets')
                    self.log(f'{"Created" if created else "Updated"} bucket: {bkt.name}')

                request = service.buckets().list_next(previous_request=request, previous_response=response)

        except HttpError as e:
            if not self._handle_http_error('Discovering Storage buckets', e, project.project_id):
                self.log(f'Error discovering Storage buckets: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering Storage buckets: {str(e)}', 'error')

    def discover_gke_clusters(self, project):
        from .models import GKECluster, GKENodePool, VPCNetwork, Subnet

        self.log(f'Discovering GKE clusters in {project.project_id}...')

        try:
            service = self._create_service('container', 'v1')
            parent = f'projects/{project.project_id}/locations/-'
            request = service.projects().locations().clusters().list(parent=parent)
            response = request.execute()

            for cluster in response.get('clusters', []):
                network = None
                network_name = cluster.get('network', '')
                if network_name:
                    try:
                        network = VPCNetwork.objects.get(project=project, name=network_name)
                    except VPCNetwork.DoesNotExist:
                        pass

                subnetwork = None
                subnet_name = cluster.get('subnetwork', '')
                if subnet_name:
                    try:
                        subnetwork = Subnet.objects.get(project=project, name=subnet_name)
                    except Subnet.DoesNotExist:
                        pass

                gke, created = GKECluster.objects.update_or_create(
                    project=project,
                    name=cluster['name'],
                    defaults={
                        'location': cluster.get('location', ''),
                        'network': network,
                        'subnetwork': subnetwork,
                        'master_version': cluster.get('currentMasterVersion', ''),
                        'status': cluster.get('status', 'UNKNOWN'),
                        'endpoint': cluster.get('endpoint', ''),
                        'cluster_ipv4_cidr': cluster.get('clusterIpv4Cidr', ''),
                        'services_ipv4_cidr': cluster.get('servicesIpv4Cidr', ''),
                        'enable_autopilot': cluster.get('autopilot', {}).get('enabled', False),
                        'self_link': cluster.get('selfLink', ''),
                        'discovered': True,
                        'last_synced': timezone.now(),
                    },
                )
                self._increment_stat('clusters')
                self.log(f'{"Created" if created else "Updated"} GKE cluster: {gke.name}')

                for pool in cluster.get('nodePools', []):
                    config = pool.get('config', {})
                    autoscaling = pool.get('autoscaling', {})

                    np, np_created = GKENodePool.objects.update_or_create(
                        cluster=gke,
                        name=pool['name'],
                        defaults={
                            'machine_type': config.get('machineType', ''),
                            'disk_size_gb': config.get('diskSizeGb', 100),
                            'disk_type': config.get('diskType', 'pd-standard'),
                            'node_count': pool.get('initialNodeCount', 0),
                            'min_node_count': autoscaling.get('minNodeCount', 0),
                            'max_node_count': autoscaling.get('maxNodeCount', 0),
                            'status': pool.get('status', 'UNKNOWN'),
                            'version': pool.get('version', ''),
                            'self_link': pool.get('selfLink', ''),
                            'discovered': True,
                            'last_synced': timezone.now(),
                        },
                    )
                    self.log(f'{"Created" if np_created else "Updated"} node pool: {np.name}')

        except HttpError as e:
            if not self._handle_http_error('Discovering GKE clusters', e, project.project_id):
                self.log(f'Error discovering GKE clusters: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering GKE clusters: {str(e)}', 'error')

    def discover_cloud_functions(self, project):
        from .models import CloudFunction

        self.log(f'Discovering Cloud Functions in {project.project_id}...')

        try:
            service = self._create_service('cloudfunctions', 'v1')
            parent = f'projects/{project.project_id}/locations/-'
            request = service.projects().locations().functions().list(parent=parent)

            while request is not None:
                response = request.execute()

                for func in response.get('functions', []):
                    name_parts = func.get('name', '').split('/')
                    name = name_parts[-1] if name_parts else ''
                    region = name_parts[3] if len(name_parts) > 3 else ''

                    trigger_type = 'HTTP'
                    trigger_url = ''
                    if func.get('httpsTrigger'):
                        trigger_url = func['httpsTrigger'].get('url', '')
                    elif func.get('eventTrigger'):
                        trigger_type = func['eventTrigger'].get('eventType', 'EVENT')

                    cf, created = CloudFunction.objects.update_or_create(
                        project=project,
                        name=name,
                        region=region,
                        defaults={
                            'runtime': func.get('runtime', ''),
                            'entry_point': func.get('entryPoint', ''),
                            'trigger_type': trigger_type,
                            'trigger_url': trigger_url,
                            'memory_mb': func.get('availableMemoryMb', 256),
                            'timeout_seconds': int(func.get('timeout', '60s').rstrip('s')),
                            'status': func.get('status', 'UNKNOWN'),
                            'discovered': True,
                            'last_synced': timezone.now(),
                        },
                    )
                    self.log(f'{"Created" if created else "Updated"} function: {cf.name}')

                request = (
                    service.projects()
                    .locations()
                    .functions()
                    .list_next(previous_request=request, previous_response=response)
                )

        except HttpError as e:
            if not self._handle_http_error('Discovering Cloud Functions', e, project.project_id):
                self.log(f'Error discovering Cloud Functions: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering Cloud Functions: {str(e)}', 'error')

    def discover_cloud_run(self, project):
        from .models import CloudRun

        self.log(f'Discovering Cloud Run services in {project.project_id}...')

        try:
            service = self._create_service('run', 'v1')
            parent = f'projects/{project.project_id}/locations/-'
            request = service.projects().locations().services().list(parent=parent)
            response = request.execute()

            for svc in response.get('items', []):
                metadata = svc.get('metadata', {})
                name = metadata.get('name', '')
                namespace = metadata.get('namespace', '')

                spec = svc.get('spec', {}).get('template', {}).get('spec', {})
                containers = spec.get('containers', [])

                image = ''
                cpu = '1'
                memory = '512Mi'
                if containers:
                    container = containers[0]
                    image = container.get('image', '')
                    resources = container.get('resources', {}).get('limits', {})
                    cpu = resources.get('cpu', '1')
                    memory = resources.get('memory', '512Mi')

                status = svc.get('status', {})
                url = status.get('url', '')

                cr, created = CloudRun.objects.update_or_create(
                    project=project,
                    name=name,
                    defaults={
                        'region': namespace,
                        'image': image,
                        'url': url,
                        'cpu': cpu,
                        'memory': memory,
                        'status': 'ACTIVE' if status.get('conditions') else 'UNKNOWN',
                        'discovered': True,
                        'last_synced': timezone.now(),
                    },
                )
                self.log(f'{"Created" if created else "Updated"} Cloud Run: {cr.name}')

        except HttpError as e:
            if not self._handle_http_error('Discovering Cloud Run', e, project.project_id):
                self.log(f'Error discovering Cloud Run: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering Cloud Run: {str(e)}', 'error')

    def discover_service_accounts(self, project):
        from .models import ServiceAccount

        self.log(f'Discovering Service Accounts in {project.project_id}...')
        print(f"DEBUG: [{project.project_id}] Discovering Service Accounts", flush=True)

        try:
            service = self._create_service('iam', 'v1')
            name = f'projects/{project.project_id}'
            print(f"DEBUG: [{project.project_id}] IAM: Listing service accounts...", flush=True)
            request = service.projects().serviceAccounts().list(name=name)

            while request is not None:
                print(f"DEBUG: [{project.project_id}] IAM: Executing service accounts request...", flush=True)
                response = request.execute()

                for sa in response.get('accounts', []):
                    svc_acc, created = ServiceAccount.objects.update_or_create(
                        email=sa['email'],
                        defaults={
                            'project': project,
                            'display_name': sa.get('displayName', ''),
                            'unique_id': sa.get('uniqueId', ''),
                            'disabled': sa.get('disabled', False),
                            'discovered': True,
                            'last_synced': timezone.now(),
                        },
                    )
                    self.log(f'{"Created" if created else "Updated"} service account: {svc_acc.email}')

                request = (
                    service.projects().serviceAccounts().list_next(previous_request=request, previous_response=response)
                )

        except HttpError as e:
            if not self._handle_http_error('Discovering Service Accounts', e, project.project_id):
                self.log(f'Error discovering Service Accounts: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering Service Accounts: {str(e)}', 'error')

    def discover_instance_groups(self, project):
        from .models import InstanceGroup, InstanceTemplate

        self.log(f'Discovering Instance Groups in {project.project_id}...')

        try:
            service = self._create_service('compute', 'v1')
            # Managed Instance Groups
            request = service.instanceGroupManagers().aggregatedList(project=project.project_id)
            while request is not None:
                response = request.execute()
                for location, igms in response.get('items', {}).items():
                    for igm in igms.get('instanceGroupManagers', []):
                        # location is usually 'regions/us-central1' or 'zones/us-central1-a'
                        loc_parts = location.split('/')
                        loc_type = loc_parts[0]  # zones or regions
                        loc_name = loc_parts[1] if len(loc_parts) > 1 else ''

                        zone = loc_name if loc_type == 'zones' else ''
                        region = loc_name if loc_type == 'regions' else ''

                        template_name = igm.get('instanceTemplate', '').split('/')[-1]
                        template = None
                        if template_name:
                            try:
                                template = InstanceTemplate.objects.get(project=project, name=template_name)
                            except InstanceTemplate.DoesNotExist:
                                pass

                        ig, created = InstanceGroup.objects.update_or_create(
                            project=project,
                            name=igm['name'],
                            defaults={
                                'zone': zone,
                                'region': region,
                                'template': template,
                                'target_size': igm.get('targetSize', 0),
                                'is_managed': True,
                                'self_link': igm.get('selfLink', ''),
                                'discovered': True,
                                'last_synced': timezone.now(),
                            },
                        )
                        self.log(f'{"Created" if created else "Updated"} Managed Instance Group: {ig.name}')
                request = service.instanceGroupManagers().aggregatedList_next(
                    previous_request=request, previous_response=response
                )

            # Unmanaged Instance Groups (and checking for ones missed by MIGs)
            request = service.instanceGroups().aggregatedList(project=project.project_id)
            while request is not None:
                response = request.execute()
                for location, igs in response.get('items', {}).items():
                    for ig_item in igs.get('instanceGroups', []):
                        # location is usually 'regions/us-central1' or 'zones/us-central1-a'
                        loc_parts = location.split('/')
                        loc_type = loc_parts[0]  # zones or regions
                        loc_name = loc_parts[1] if len(loc_parts) > 1 else ''

                        zone = loc_name if loc_type == 'zones' else ''
                        region = loc_name if loc_type == 'regions' else ''

                        # Check if this IG already exists (likely created by MIG loop above)
                        # If it exists, we skip overwriting is_managed, but ensure other fields are set
                        # If it doesn't exist, it's an unmanaged group

                        # Note: instanceGroupManagers API returns 'name' same as the instanceGroup it manages.

                        try:
                            # Try to find existing one first
                            existing_ig = InstanceGroup.objects.get(project=project, name=ig_item['name'])
                            # It exists, so it was likely a MIG. Just update sync time or small details if needed.
                            # We don't want to overwrite 'is_managed=True' with default if we were to use
                            # update_or_create blindly
                            if not existing_ig.discovered:
                                existing_ig.discovered = True
                                existing_ig.save()
                        except InstanceGroup.DoesNotExist:
                            # It's a new one, so it must be Unmanaged (since we processed all MIGs above)
                            ig, created = InstanceGroup.objects.update_or_create(
                                project=project,
                                name=ig_item['name'],
                                defaults={
                                    'zone': zone,
                                    'region': region,
                                    'template': None,  # Unmanaged groups don't have templates usually in the same way
                                    'target_size': ig_item.get('size', 0),  # 'size' is current size
                                    'is_managed': False,
                                    'self_link': ig_item.get('selfLink', ''),
                                    'discovered': True,
                                    'last_synced': timezone.now(),
                                },
                            )
                            self.log(f'{"Created" if created else "Updated"} Unmanaged Instance Group: {ig.name}')

                request = service.instanceGroups().aggregatedList_next(
                    previous_request=request, previous_response=response
                )
        except HttpError as e:
            if not self._handle_http_error('Discovering Instance Groups', e, project.project_id):
                self.log(f'Error discovering Instance Groups: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering Instance Groups: {str(e)}', 'error')

    def discover_cloud_nats(self, project):
        from .models import CloudNAT, CloudRouter

        self.log(f'Discovering Cloud NATs in {project.project_id}...')

        try:
            service = self._create_service('compute', 'v1')
            request = service.routers().aggregatedList(project=project.project_id)

            while request is not None:
                response = request.execute()
                for region, routers_data in response.get('items', {}).items():
                    for router_data in routers_data.get('routers', []):
                        nats = router_data.get('nats', [])
                        if not nats:
                            continue

                        router_name = router_data['name']
                        try:
                            router_obj = CloudRouter.objects.get(project=project, name=router_name)
                        except CloudRouter.DoesNotExist:
                            continue

                        region_name = router_data.get('region', '').split('/')[-1]

                        for nat in nats:
                            nat_obj, created = CloudNAT.objects.update_or_create(
                                project=project,
                                name=nat['name'],
                                router=router_obj,
                                defaults={
                                    'region': region_name,
                                    'nat_ip_allocate_option': nat.get('natIpAllocateOption', 'AUTO_ONLY'),
                                    'source_subnetwork_ip_ranges_to_nat': nat.get(
                                        'sourceSubnetworkIpRangesToNat', 'ALL_SUBNETWORKS_ALL_IP_RANGES'
                                    ),
                                    'nat_ips': nat.get('natIps'),
                                    'min_ports_per_vm': nat.get('minPortsPerVm', 64),
                                    'self_link': router_data.get(
                                        'selfLink', ''
                                    ),  # NATs don't have unique selfLinks, use router's or construct one?
                                    # simple is empty or router's
                                    'discovered': True,
                                    'last_synced': timezone.now(),
                                },
                            )
                            self.log(f'{"Created" if created else "Updated"} Cloud NAT: {nat_obj.name}')

                request = service.routers().aggregatedList_next(previous_request=request, previous_response=response)
        except HttpError as e:
            if not self._handle_http_error('Discovering Cloud NATs', e, project.project_id):
                self.log(f'Error discovering Cloud NATs: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering Cloud NATs: {str(e)}', 'error')

    def discover_load_balancers(self, project):
        from .models import LoadBalancer, VPCNetwork

        self.log(f'Discovering Load Balancers (Forwarding Rules) in {project.project_id}...')

        try:
            service = self._create_service('compute', 'v1')
            request = service.forwardingRules().aggregatedList(project=project.project_id)

            while request is not None:
                response = request.execute()
                for region, fr_data in response.get('items', {}).items():
                    for fr in fr_data.get('forwardingRules', []):
                        # Skip PSC Endpoints (they are handled in discover_psc_endpoints)
                        target = fr.get('target', '')
                        is_psc = False
                        if target:
                            if '/serviceAttachments/' in target:
                                is_psc = True
                            elif target in ['all-apis', 'vpc-sc']:
                                is_psc = True

                        if is_psc:
                            continue

                        network = None
                        net_name = fr.get('network', '').split('/')[-1]
                        if net_name:
                            try:
                                network = VPCNetwork.objects.get(project=project, name=net_name)
                            except VPCNetwork.DoesNotExist:
                                pass

                        region_name = fr.get('region', '').split('/')[-1]
                        if not region_name and 'global' in fr.get('selfLink', ''):
                            region_name = 'global'

                        lb, created = LoadBalancer.objects.update_or_create(
                            project=project,
                            name=fr['name'],
                            defaults={
                                'scheme': fr.get('loadBalancingScheme', 'EXTERNAL'),
                                'lb_type': fr.get('IPProtocol', 'TCP'),  # Proxy/Protocol
                                'region': region_name,
                                'network': network,
                                'ip_address': fr.get('IPAddress'),
                                'port': int(fr.get('ports', [80])[0])
                                if fr.get('ports')
                                else (int(fr.get('portRange', '0-0').split('-')[0]) if fr.get('portRange') else 0),
                                'self_link': fr.get('selfLink', ''),
                                'discovered': True,
                                'last_synced': timezone.now(),
                            },
                        )
                        self.log(f'{"Created" if created else "Updated"} Load Balancer: {lb.name}')
                request = service.forwardingRules().aggregatedList_next(
                    previous_request=request, previous_response=response
                )
        except HttpError as e:
            if not self._handle_http_error('Discovering Load Balancers', e, project.project_id):
                self.log(f'Error discovering Load Balancers: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering Load Balancers: {str(e)}', 'error')

    def discover_service_attachments(self, project):
        from .models import ServiceAttachment

        self.log(f'Discovering Service Attachments in {project.project_id}...')

        try:
            service = self._create_service('compute', 'v1')
            request = service.serviceAttachments().aggregatedList(project=project.project_id)

            while request is not None:
                response = request.execute()
                for location, sa_data in response.get('items', {}).items():
                    for sa in sa_data.get('serviceAttachments', []):
                        # location is usually 'regions/us-central1'
                        region_name = location.split('/')[-1] if 'regions' in location else ''
                        if not region_name and sa.get('region'):
                            region_name = sa['region'].split('/')[-1]

                        attachment, created = ServiceAttachment.objects.update_or_create(
                            project=project,
                            name=sa['name'],
                            defaults={
                                'region': region_name,
                                'connection_preference': sa.get('connectionPreference', 'ACCEPT_AUTOMATIC'),
                                'nat_subnets': sa.get('natSubnets', []),
                                'target_service': sa.get('targetService', ''),
                                'self_link': sa.get('selfLink', ''),
                                'discovered': True,
                                'last_synced': timezone.now(),
                            },
                        )
                        self.log(f'{"Created" if created else "Updated"} Service Attachment: {attachment.name}')
                request = service.serviceAttachments().aggregatedList_next(
                    previous_request=request, previous_response=response
                )
        except HttpError as e:
            if not self._handle_http_error('Discovering Service Attachments', e, project.project_id):
                self.log(f'Error discovering Service Attachments: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering Service Attachments: {str(e)}', 'error')

    def discover_psc_endpoints(self, project):
        from .models import ServiceConnectEndpoint, VPCNetwork

        self.log(f'Discovering PSC Endpoints in {project.project_id}...')

        try:
            service = self._create_service('compute', 'v1')
            request = service.forwardingRules().aggregatedList(project=project.project_id)

            while request is not None:
                response = request.execute()
                for location, fr_data in response.get('items', {}).items():
                    for fr in fr_data.get('forwardingRules', []):
                        target = fr.get('target', '')
                        is_psc = False

                        if target:
                            if '/serviceAttachments/' in target:
                                is_psc = True
                            elif target in ['all-apis', 'vpc-sc']:
                                is_psc = True

                        if not is_psc:
                            continue

                        # location is usually 'regions/us-central1'
                        region_name = location.split('/')[-1] if 'regions' in location else ''
                        if not region_name and fr.get('region'):
                            region_name = fr['region'].split('/')[-1]

                        network = None
                        net_name = fr.get('network', '').split('/')[-1]
                        if net_name:
                            try:
                                network = VPCNetwork.objects.get(project=project, name=net_name)
                            except VPCNetwork.DoesNotExist:
                                pass

                        psc, created = ServiceConnectEndpoint.objects.update_or_create(
                            project=project,
                            name=fr['name'],
                            defaults={
                                'region': region_name,
                                'network': network,
                                'ip_address': fr.get('IPAddress'),
                                'target_service_attachment': target,
                                'self_link': fr.get('selfLink', ''),
                                'discovered': True,
                                'last_synced': timezone.now(),
                            },
                        )
                        self.log(f'{"Created" if created else "Updated"} PSC Endpoint: {psc.name}')
                request = service.forwardingRules().aggregatedList_next(
                    previous_request=request, previous_response=response
                )
        except HttpError as e:
            if not self._handle_http_error('Discovering PSC Endpoints', e, project.project_id):
                self.log(f'Error discovering PSC Endpoints: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering PSC Endpoints: {str(e)}', 'error')

    def discover_ncc_hubs(self, project):
        from .models import NCCHub

        self.log(f'Discovering NCC Hubs in {project.project_id}...')

        try:
            service = self._create_service('networkconnectivity', 'v1')
            parent = f'projects/{project.project_id}/locations/global'
            request = service.projects().locations().global_().hubs().list(parent=parent)

            while request is not None:
                response = request.execute()
                for hub in response.get('hubs', []):
                    name = hub['name'].split('/')[-1]
                    h, created = NCCHub.objects.update_or_create(
                        project=project,
                        name=name,
                        defaults={
                            'description': hub.get('description', ''),
                            'labels': hub.get('labels'),
                            'self_link': hub.get('name', ''),  # API returns full name resource path
                            'discovered': True,
                            'last_synced': timezone.now(),
                        },
                    )
                    self.log(f'{"Created" if created else "Updated"} NCC Hub: {h.name}')
                request = (
                    service.projects()
                    .locations()
                    .global_()
                    .hubs()
                    .list_next(previous_request=request, previous_response=response)
                )
        except HttpError as e:
            if not self._handle_http_error('Discovering NCC Hubs', e, project.project_id):
                self.log(f'Error discovering NCC Hubs: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering NCC Hubs: {str(e)}', 'error')

    def discover_ncc_spokes(self, project):
        from .models import NCCSpoke, NCCHub, VPCNetwork

        self.log(f'Discovering NCC Spokes in {project.project_id}...')

        try:
            service = self._create_service('networkconnectivity', 'v1')
            parent = f'projects/{project.project_id}/locations/-'
            request = service.projects().locations().spokes().list(parent=parent)

            while request is not None:
                response = request.execute()
                for spoke in response.get('spokes', []):
                    hub_full_name = spoke.get('hub', '')
                    # hub name format: projects/p/locations/global/hubs/hub1
                    hub_name = hub_full_name.split('/')[-1]
                    hub = None
                    if hub_name:
                        try:
                            # NCC Hubs must be global?
                            # Search by name in same project first.
                            # Note: Spokes can attach to hubs in other projects.
                            # We only link if we have the Hub in our DB (NetBox model scoping)
                            # Or we might need to find the Hub by name across all known Hubs?
                            # Optimistic: Hub is in same DB
                            hub = NCCHub.objects.filter(name=hub_name).first()
                        except Exception:
                            pass

                    if not hub:
                        continue  # Can't link without hub

                    location = spoke['name'].split('/')[3]
                    spoke_name = spoke['name'].split('/')[-1]

                    linked_vpc = None
                    vpc_key = spoke.get('linkedVpcNetwork', {}).get('uri')
                    if vpc_key:
                        vpc_name = vpc_key.split('/')[-1]
                        try:
                            linked_vpc = VPCNetwork.objects.get(project=project, name=vpc_name)
                        except VPCNetwork.DoesNotExist:
                            pass

                    s, created = NCCSpoke.objects.update_or_create(
                        project=project,
                        name=spoke_name,
                        defaults={
                            'hub': hub,
                            'location': location,
                            'description': spoke.get('description', ''),
                            'spoke_type': 'VPC_NETWORK'
                            if vpc_key
                            else 'VPN_TUNNEL'
                            if spoke.get('linkedVpnTunnels')
                            else 'INTERCONNECT'
                            if spoke.get('linkedInterconnectAttachments')
                            else 'UNKNOWN',
                            'linked_vpc_network': linked_vpc,
                            'linked_vpn_tunnels': spoke.get('linkedVpnTunnels', {}).get('uris'),
                            'linked_interconnect_attachments': spoke.get('linkedInterconnectAttachments', {}).get(
                                'uris'
                            ),
                            'labels': spoke.get('labels'),
                            'self_link': spoke.get('name', ''),
                            'discovered': True,
                            'last_synced': timezone.now(),
                        },
                    )
                    self.log(f'{"Created" if created else "Updated"} NCC Spoke: {s.name}')
                request = (
                    service.projects()
                    .locations()
                    .spokes()
                    .list_next(previous_request=request, previous_response=response)
                )
        except HttpError as e:
            if not self._handle_http_error('Discovering NCC Spokes', e, project.project_id):
                self.log(f'Error discovering NCC Spokes: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering NCC Spokes: {str(e)}', 'error')

    def discover_interconnect_attachments(self, project):
        from .models import InterconnectAttachment, CloudRouter

        self.log(f'Discovering Interconnect Attachments in {project.project_id}...')

        try:
            service = self._create_service('compute', 'v1')
            request = service.interconnectAttachments().aggregatedList(project=project.project_id)

            while request is not None:
                response = request.execute()
                for region, atts_data in response.get('items', {}).items():
                    for att in atts_data.get('interconnectAttachments', []):
                        router_name = att.get('router', '').split('/')[-1]
                        router = None
                        if router_name:
                            try:
                                router = CloudRouter.objects.get(project=project, name=router_name)
                            except CloudRouter.DoesNotExist:
                                # Required field
                                continue

                        if not router:
                            continue

                        region_name = att.get('region', '').split('/')[-1]

                        ia, created = InterconnectAttachment.objects.update_or_create(
                            project=project,
                            name=att['name'],
                            defaults={
                                'region': region_name,
                                'router': router,
                                'attachment_type': att.get('type', 'DEDICATED'),
                                'edge_availability_domain': att.get('edgeAvailabilityDomain', ''),
                                'bandwidth': att.get('bandwidth', 'BPS_1G'),
                                'vlan_tag': att.get('vlanTag8021q', 0),
                                'pairing_key': att.get('pairingKey', ''),
                                'partner_asn': att.get('partnerAsn'),
                                'cloud_router_ip_address': att.get('cloudRouterIpAddress'),
                                'customer_router_ip_address': att.get('customerRouterIpAddress'),
                                'state': att.get('state', 'ACTIVE'),
                                'labels': att.get('labels'),
                                'self_link': att.get('selfLink', ''),
                                'discovered': True,
                                'last_synced': timezone.now(),
                            },
                        )
                        self.log(f'{"Created" if created else "Updated"} Interconnect Attachment: {ia.name}')
                request = service.interconnectAttachments().aggregatedList_next(
                    previous_request=request, previous_response=response
                )
        except HttpError as e:
            if not self._handle_http_error('Discovering Interconnect Attachments', e, project.project_id):
                self.log(f'Error discovering Interconnect Attachments: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering Interconnect Attachments: {str(e)}', 'error')

    def discover_external_vpn_gateways(self, project):
        from .models import ExternalVPNGateway

        self.log(f'Discovering External VPN Gateways in {project.project_id}...')

        try:
            service = self._create_service('compute', 'v1')
            request = service.externalVpnGateways().list(project=project.project_id)

            while request is not None:
                response = request.execute()
                for gw in response.get('items', []):
                    egw, created = ExternalVPNGateway.objects.update_or_create(
                        project=project,
                        name=gw['name'],
                        defaults={
                            'description': gw.get('description', ''),
                            'redundancy_type': gw.get('redundancyType', 'SINGLE_IP_INTERNALLY_REDUNDANT'),
                            'interfaces': gw.get('interfaces'),
                            'labels': gw.get('labels'),
                            'self_link': gw.get('selfLink', ''),
                            'discovered': True,
                            'last_synced': timezone.now(),
                        },
                    )
                    self.log(f'{"Created" if created else "Updated"} External VPN Gateway: {egw.name}')
                request = service.externalVpnGateways().list_next(previous_request=request, previous_response=response)
        except HttpError as e:
            if not self._handle_http_error('Discovering External VPN Gateways', e, project.project_id):
                self.log(f'Error discovering External VPN Gateways: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering External VPN Gateways: {str(e)}', 'error')

    def discover_firestore(self, project):
        from .models import FirestoreDatabase

        self.log(f'Discovering Firestore Databases in {project.project_id}...')

        try:
            service = self._create_service('firestore', 'v1')
            parent = f'projects/{project.project_id}'
            request = service.projects().databases().list(parent=parent)

            while request is not None:
                response = request.execute()
                for db in response.get('databases', []):
                    # name is fields/p/databases/dbname
                    name = db['name'].split('/')[-1]
                    fdb, created = FirestoreDatabase.objects.update_or_create(
                        project=project,
                        name=name,
                        defaults={
                            'location': db.get('locationId', ''),
                            'database_type': db.get('type', 'FIRESTORE_NATIVE'),
                            'concurrency_mode': db.get('concurrencyMode', 'OPTIMISTIC'),
                            'status': 'ACTIVE',  # API doesn't always return status for active ones
                            'self_link': db.get('name', ''),
                            'discovered': True,
                            'last_synced': timezone.now(),
                        },
                    )
                    self.log(f'{"Created" if created else "Updated"} Firestore DB: {fdb.name}')
                # NO list_next for firestore v1 typically? check docs.
                # It seems firestore().projects().databases().list() returns 'nextPageToken'
                if 'nextPageToken' in response:
                    request = service.projects().databases().list(parent=parent, pageToken=response['nextPageToken'])
                else:
                    request = None
        except HttpError as e:
            if not self._handle_http_error('Discovering Firestore', e, project.project_id):
                self.log(f'Error discovering Firestore: {str(e)}', 'error')
        except Exception as e:
            # Firestore API might not be enabled
            self.log(f'Error discovering Firestore: {str(e)}', 'error')

    def discover_bigtable(self, project):
        from .models import BigtableInstance

        self.log(f'Discovering Bigtable Instances in {project.project_id}...')

        try:
            service = self._create_service('bigtableadmin', 'v2')
            parent = f'projects/{project.project_id}'
            request = service.projects().instances().list(parent=parent)

            while request is not None:
                response = request.execute()
                for instance in response.get('instances', []):
                    name = instance['name'].split('/')[-1]
                    bt, created = BigtableInstance.objects.update_or_create(
                        project=project,
                        name=name,
                        defaults={
                            'display_name': instance.get('displayName', ''),
                            'instance_type': instance.get('type', 'PRODUCTION'),
                            'status': instance.get('state', 'READY'),
                            'self_link': instance.get('name', ''),
                            'discovered': True,
                            'last_synced': timezone.now(),
                        },
                    )
                    self.log(f'{"Created" if created else "Updated"} Bigtable Instance: {bt.name}')

                if 'nextPageToken' in response:
                    request = service.projects().instances().list(parent=parent, pageToken=response['nextPageToken'])
                else:
                    request = None
        except HttpError as e:
            if not self._handle_http_error('Discovering Bigtable', e, project.project_id):
                self.log(f'Error discovering Bigtable: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering Bigtable: {str(e)}', 'error')

    def discover_memorystore(self, project):
        from .models import MemorystoreInstance, VPCNetwork

        self.log(f'Discovering Memorystore (Redis) in {project.project_id}...')

        try:
            service = self._create_service('redis', 'v1')
            parent = f'projects/{project.project_id}/locations/-'
            request = service.projects().locations().instances().list(parent=parent)

            while request is not None:
                response = request.execute()
                for instance in response.get('instances', []):
                    name = instance['name'].split('/')[-1]
                    region = instance['locationId']

                    network = None
                    net_id = instance.get('authorizedNetwork', '').split('/')[-1]
                    if net_id:
                        try:
                            network = VPCNetwork.objects.get(project=project, name=net_id)
                        except VPCNetwork.DoesNotExist:
                            pass

                    ms, created = MemorystoreInstance.objects.update_or_create(
                        project=project,
                        name=name,
                        defaults={
                            'region': region,
                            'tier': instance.get('tier', 'BASIC'),
                            'memory_size_gb': instance.get('memorySizeGb', 1),
                            'redis_version': instance.get('redisVersion', 'REDIS_6_X'),
                            'host': instance.get('host', ''),
                            'port': instance.get('port', 6379),
                            'status': instance.get('state', 'READY'),
                            'network': network,
                            'self_link': instance.get('name', ''),
                            'discovered': True,
                            'last_synced': timezone.now(),
                        },
                    )
                    self.log(f'{"Created" if created else "Updated"} Memorystore: {ms.name}')

                if 'nextPageToken' in response:
                    request = (
                        service.projects()
                        .locations()
                        .instances()
                        .list(parent=parent, pageToken=response['nextPageToken'])
                    )
                else:
                    request = None
        except HttpError as e:
            if not self._handle_http_error('Discovering Memorystore', e, project.project_id):
                self.log(f'Error discovering Memorystore: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering Memorystore: {str(e)}', 'error')

    def discover_pubsub(self, project):
        from .models import PubSubTopic, PubSubSubscription

        self.log(f'Discovering Pub/Sub in {project.project_id}...')

        try:
            service = self._create_service('pubsub', 'v1')
            # Topics
            parent = f'projects/{project.project_id}'
            print(f"DEBUG: [{project.project_id}] PubSub: Listing topics...", flush=True)
            request = service.projects().topics().list(project=parent)

            while request is not None:
                print(f"DEBUG: [{project.project_id}] PubSub: Executing topics request...", flush=True)
                response = request.execute()
                print(
                    f"DEBUG: [{project.project_id}] PubSub: Found {len(response.get('topics', []))} topics", flush=True
                )

                for topic in response.get('topics', []):
                    # name: projects/p/topics/t
                    name = topic['name'].split('/')[-1]
                    t, created = PubSubTopic.objects.update_or_create(
                        project=project,
                        name=name,
                        defaults={
                            'labels': topic.get('labels'),
                            'self_link': topic.get('name', ''),
                            'discovered': True,
                            'last_synced': timezone.now(),
                        },
                    )
                    # self.log(f'{"Created" if created else "Updated"} Topic: {t.name}')

                if 'nextPageToken' in response:
                    print(f"DEBUG: [{project.project_id}] PubSub: Pagination for topics", flush=True)
                    request = service.projects().topics().list(project=parent, pageToken=response['nextPageToken'])
                else:
                    request = None

            print(f"DEBUG: [{project.project_id}] PubSub: Listing subscriptions...", flush=True)
            # Subscriptions
            request = service.projects().subscriptions().list(project=parent)
            while request is not None:
                print(f"DEBUG: [{project.project_id}] PubSub: Executing subscriptions request...", flush=True)
                response = request.execute()
                num_subs = len(response.get('subscriptions', []))
                print(
                    f"DEBUG: [{project.project_id}] PubSub: Found {num_subs} subscriptions",
                    flush=True,
                )

                for sub in response.get('subscriptions', []):
                    name = sub['name'].split('/')[-1]
                    topic_name = sub.get('topic', '').split('/')[-1]
                    topic = None
                    if topic_name:
                        try:
                            topic = PubSubTopic.objects.get(project=project, name=topic_name)
                        except PubSubTopic.DoesNotExist:
                            pass

                    if not topic:
                        # Subscription must have topic? Usually yes.
                        continue

                    s, created = PubSubSubscription.objects.update_or_create(
                        project=project,
                        name=name,
                        defaults={
                            'topic': topic,
                            'ack_deadline_seconds': sub.get('ackDeadlineSeconds', 10),
                            'push_endpoint': sub.get('pushConfig', {}).get('pushEndpoint', ''),
                            'message_retention_duration': sub.get('messageRetentionDuration', '604800s'),
                            'self_link': sub.get('name', ''),
                            'discovered': True,
                            'last_synced': timezone.now(),
                        },
                    )
                    self.log(f'{"Created" if created else "Updated"} Subscription: {s.name}')

                if 'nextPageToken' in response:
                    request = (
                        service.projects().subscriptions().list(project=parent, pageToken=response['nextPageToken'])
                    )
                else:
                    request = None

        except HttpError as e:
            if not self._handle_http_error('Discovering Pub/Sub', e, project.project_id):
                self.log(f'Error discovering Pub/Sub: {str(e)}', 'error')
        except Exception as e:
            self.log(f'Error discovering Pub/Sub: {str(e)}', 'error')

    def discover_secret_manager_secrets(self, project):
        from .models import SecretManagerSecret

        try:
            service = self._create_service('secretmanager', 'v1')
            parent = f'projects/{project.project_id}'

            request = service.projects().secrets().list(parent=parent)
            while request:
                response = request.execute()
                for secret in response.get('secrets', []):
                    name = secret['name'].split('/')[-1]

                    obj, created = SecretManagerSecret.objects.update_or_create(
                        project=project,
                        name=name,
                        defaults={
                            'replication_type': secret.get('replication', {}).get('automatic')
                            and 'AUTOMATIC'
                            or 'USER_MANAGED',
                            'self_link': secret.get('name', ''),
                            'labels': secret.get('labels'),
                            'discovered': True,
                            'last_synced': timezone.now(),
                        },
                    )
                    self._increment_stat('secrets')

                request = service.projects().secrets().list_next(previous_request=request, previous_response=response)

        except Exception as e:
            if not self._handle_http_error('Secret Manager discovery', e):
                self.log(f'Error discovering secrets: {e}', 'error')

    def discover_cloud_dns_zones(self, project):
        from .models import CloudDNSZone

        try:
            service = self._create_service('dns', 'v1')
            project_id = project.project_id

            request = service.managedZones().list(project=project_id)
            while request:
                response = request.execute()
                for zone in response.get('managedZones', []):

                    obj, created = CloudDNSZone.objects.update_or_create(
                        project=project,
                        name=zone['name'],
                        defaults={
                            'dns_name': zone['dnsName'],
                            'description': zone.get('description', ''),
                            'visibility': zone.get('visibility', 'public'),
                            'name_servers': zone.get('nameServers'),
                            'self_link': zone.get('kind', ''),
                            'discovered': True,
                            'last_synced': timezone.now()
                        }
                    )
                    self._increment_stat('dns_zones')

                    self.discover_cloud_dns_records(service, project, obj)

                request = service.managedZones().list_next(previous_request=request, previous_response=response)

        except Exception as e:
            if not self._handle_http_error('Cloud DNS discovery', e):
                self.log(f'Error discovering DNS zones: {e}', 'error')

    def discover_cloud_dns_records(self, service, project, zone):
        from .models import CloudDNSRecord

        try:
            request = service.resourceRecordSets().list(project=project.project_id, managedZone=zone.name)
            while request:
                response = request.execute()
                for rrset in response.get('rrsets', []):

                    CloudDNSRecord.objects.update_or_create(
                        zone=zone,
                        name=rrset['name'],
                        record_type=rrset['type'],
                        defaults={
                            'ttl': rrset.get('ttl', 300),
                            'rrdatas': rrset.get('rrdatas'),
                            'discovered': True,
                            'last_synced': timezone.now()
                        }
                    )
                    self._increment_stat('dns_records')

                request = service.resourceRecordSets().list_next(previous_request=request, previous_response=response)
        except Exception as e:
            self.log(f'Error discovering DNS records for {zone.name}: {e}', 'warning')

    def discover_iam_roles(self, project):
        from .models import IAMRole

        try:
            print(f"DEBUG: [{project.project_id}] Discovering IAM Roles", flush=True)
            service = self._create_service('iam', 'v1')
            parent = f'projects/{project.project_id}'

            # List custom roles for the project
            print(f"DEBUG: [{project.project_id}] IAM: Listing roles...", flush=True)
            request = service.projects().roles().list(parent=parent, view='FULL')
            while request:
                print(f"DEBUG: [{project.project_id}] IAM: Executing roles request...", flush=True)
                response = request.execute()
                for role in response.get('roles', []):
                    IAMRole.objects.update_or_create(
                        name=role['name'],
                        defaults={
                            'title': role.get('title', ''),
                            'description': role.get('description', ''),
                            'stage': role.get('stage', 'GA'),
                            'permissions': role.get('includedPermissions', []),
                            'is_custom': True,
                            'project': project,
                            'discovered': True,
                            'last_synced': timezone.now()
                        }
                    )
                    self._increment_stat('iam_roles')

                request = service.projects().roles().list_next(previous_request=request, previous_response=response)

        except Exception as e:
            if not self._handle_http_error('IAM Roles discovery', e):
                self.log(f'Error discovering IAM roles: {e}', 'error')

    def discover_iam_policy(self, project):
        from .models import IAMBinding, IAMRole

        try:
            print(f"DEBUG: [{project.project_id}] Discovering IAM Policy", flush=True)
            # Use Cloud Resource Manager API to get policy
            service = self._create_service('cloudresourcemanager', 'v1')
            resource = project.project_id

            print(f"DEBUG: [{project.project_id}] IAM: Getting IAM policy...", flush=True)
            policy = service.projects().getIamPolicy(resource=resource).execute()
            bindings = policy.get('bindings', [])
            print(f"DEBUG: [{project.project_id}] IAMPolicy: Found {len(bindings)} bindings", flush=True)

            for binding in bindings:
                role_name = binding['role']
                members = binding['members']

                # Ensure Role exists
                role_obj = IAMRole.objects.filter(name=role_name).first()
                if not role_obj:
                    # If it's a predefined role or org-level role not yet synced
                    role_obj = IAMRole.objects.create(
                        name=role_name,
                        title=role_name,
                        is_custom=False,
                        # project is None for global/predefined roles
                        discovered=True,
                        last_synced=timezone.now()
                    )

                for member in members:
                    IAMBinding.objects.update_or_create(
                        project=project,
                        role=role_obj,
                        member=member,
                        defaults={
                            'condition': binding.get('condition'),
                            'discovered': True,
                            'last_synced': timezone.now()
                        }
                    )
                    self._increment_stat('iam_bindings')

        except Exception as e:
            if not self._handle_http_error('IAM Policy discovery', e):
                self.log(f'Error discovering IAM policy: {e}', 'error')


def run_discovery(organization_id):
    from .models import GCPOrganization

    try:
        organization = GCPOrganization.objects.get(pk=organization_id)
        discovery_service = GCPDiscoveryService(organization)
        return discovery_service.discover_all()
    except GCPOrganization.DoesNotExist:
        return False


def process_discovery_batch(organization_id, discovery_log_id, project_pks):
    from .models import GCPOrganization, GCPProject, DiscoveryLog
    import logging

    logger = logging.getLogger(__name__)

    try:
        organization = GCPOrganization.objects.get(pk=organization_id)
        discovery_log = DiscoveryLog.objects.get(pk=discovery_log_id)

        service = GCPDiscoveryService(organization)
        service.discovery_log = discovery_log
        service._setup_redis(discovery_log.pk)

        if not service.setup_credentials():
            service.log('Batch worker failed to authenticate', 'error')
            return

        projects = GCPProject.objects.filter(pk__in=project_pks)

        # Process projects in parallel within the batch
        # This speeds up the batch significantly
        from concurrent.futures import ThreadPoolExecutor, as_completed

        # Increase threads to speed up processing (IO bound)
        max_threads = min(20, len(projects))

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [executor.submit(service.process_project, project) for project in projects]
            for future in as_completed(futures):
                try:
                    future.result()

                    # Update progress incrementally and sync logs
                    service._sync_stats_from_redis()
                    try:
                        discovery_log.refresh_from_db()
                        # Ensure status is running (fixes UI showing failed if parent process errored)
                        if discovery_log.status == 'failed':
                            discovery_log.status = 'running'

                        discovery_log.log_output = service.get_log_output()
                        discovery_log.projects_discovered = service.stats.get('projects', 0)
                        discovery_log.instances_discovered = service.stats.get('instances', 0)
                        discovery_log.networks_discovered = service.stats.get('networks', 0)
                        discovery_log.databases_discovered = service.stats.get('databases', 0)
                        discovery_log.buckets_discovered = service.stats.get('buckets', 0)
                        discovery_log.clusters_discovered = service.stats.get('clusters', 0)
                        discovery_log.total_resources = service.stats.get('total', 0)

                        discovery_log.save(
                            update_fields=[
                                'status',
                                'log_output',
                                'projects_discovered',
                                'instances_discovered',
                                'networks_discovered',
                                'databases_discovered',
                                'buckets_discovered',
                                'clusters_discovered',
                                'total_resources',
                            ]
                        )
                    except Exception:
                        pass

                except Exception as e:
                    service.log(f'Thread execution failed: {e}', 'error')

        if service.redis_conn:
            batches_key = f'netbox:gcp:discovery:{discovery_log.pk}:batches'
            done_count = service.redis_conn.incr(f'{batches_key}:done')
            total_count = int(service.redis_conn.get(f'{batches_key}:total') or 0)

            service.log(f'Worker finished batch {done_count}/{total_count}')

            # Sync logs to DB so UI updates
            try:
                discovery_log.refresh_from_db()
                discovery_log.log_output = service.get_log_output()
                discovery_log.save(update_fields=['log_output'])
            except Exception:
                pass

            if done_count >= total_count:
                service.log('All batches finished. Finalizing discovery.')
                service._finish_discovery(discovery_log)

    except Exception as e:
        logger.error(f'Batch processing failed: {e}')
        if 'service' in locals() and hasattr(service, 'log'):
            service.log(f'Batch processing failed: {str(e)}', 'error')
            try:
                # Try to sync the error to the log
                discovery_log.refresh_from_db()
                discovery_log.log_output = service.get_log_output()
                discovery_log.save(update_fields=['log_output'])
            except Exception:
                pass
