import json
import logging
from datetime import datetime
from django.utils import timezone

logger = logging.getLogger(__name__)


class GCPDiscoveryService:
    def __init__(self, organization):
        self.organization = organization
        self.credentials = None
        self.log_messages = []
        self.stats = {
            'projects': 0,
            'instances': 0,
            'networks': 0,
            'databases': 0,
            'buckets': 0,
            'clusters': 0,
            'total': 0
        }

    def log(self, message, level='info'):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log_messages.append(f"[{timestamp}] [{level.upper()}] {message}")
        if level == 'error':
            logger.error(message)
        else:
            logger.info(message)

    def get_log_output(self):
        return '\n'.join(self.log_messages)

    def setup_credentials(self):
        try:
            from google.oauth2 import service_account
            
            sa_info = self.organization.get_service_account_info()
            if not sa_info:
                raise ValueError("Invalid service account JSON")
            
            self.credentials = service_account.Credentials.from_service_account_info(
                sa_info,
                scopes=[
                    'https://www.googleapis.com/auth/cloud-platform',
                    'https://www.googleapis.com/auth/compute',
                    'https://www.googleapis.com/auth/sqlservice.admin',
                    'https://www.googleapis.com/auth/devstorage.read_only',
                ]
            )
            self.log("Successfully authenticated with service account")
            return True
        except Exception as e:
            self.log(f"Failed to setup credentials: {str(e)}", 'error')
            return False

    def discover_all(self):
        from .models import DiscoveryLog
        
        discovery_log = DiscoveryLog.objects.create(
            organization=self.organization,
            status='running'
        )
        
        self.organization.discovery_status = 'running'
        self.organization.save()
        
        try:
            if not self.setup_credentials():
                raise Exception("Failed to authenticate with GCP")
            
            self.log("Starting discovery for organization: " + self.organization.name)
            
            projects = self.discover_projects()
            
            for project in projects:
                self.log(f"Discovering resources in project: {project.project_id}")
                
                if self.organization.discover_networking:
                    self.discover_vpc_networks(project)
                    self.discover_subnets(project)
                    self.discover_firewall_rules(project)
                    self.discover_cloud_routers(project)
                    self.discover_vpn_gateways(project)
                    self.discover_vpn_tunnels(project)
                
                if self.organization.discover_compute:
                    self.discover_compute_instances(project)
                    self.discover_instance_templates(project)
                    self.discover_persistent_disks(project)
                
                if self.organization.discover_databases:
                    self.discover_cloud_sql(project)
                    self.discover_cloud_spanner(project)
                
                if self.organization.discover_storage:
                    self.discover_storage_buckets(project)
                
                if self.organization.discover_kubernetes:
                    self.discover_gke_clusters(project)
                
                if self.organization.discover_serverless:
                    self.discover_cloud_functions(project)
                    self.discover_cloud_run(project)
                
                if self.organization.discover_iam:
                    self.discover_service_accounts(project)
            
            self.stats['total'] = sum([
                self.stats['projects'],
                self.stats['instances'],
                self.stats['networks'],
                self.stats['databases'],
                self.stats['buckets'],
                self.stats['clusters']
            ])
            
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
            
            self.log(f"Discovery completed. Total resources: {self.stats['total']}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            self.log(f"Discovery failed: {error_msg}", 'error')
            
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
        from googleapiclient.discovery import build
        
        self.log("Discovering projects...")
        projects = []
        
        try:
            service = build('cloudresourcemanager', 'v1', credentials=self.credentials)
            
            filter_str = f'parent.type:organization parent.id:{self.organization.organization_id}'
            request = service.projects().list(filter=filter_str)
            
            while request is not None:
                response = request.execute()
                
                for proj in response.get('projects', []):
                    project, created = GCPProject.objects.update_or_create(
                        project_id=proj['projectId'],
                        defaults={
                            'organization': self.organization,
                            'name': proj.get('name', proj['projectId']),
                            'project_number': proj.get('projectNumber', ''),
                            'status': proj.get('lifecycleState', 'ACTIVE'),
                            'labels': proj.get('labels', {}),
                            'discovered': True,
                            'last_synced': timezone.now()
                        }
                    )
                    projects.append(project)
                    self.stats['projects'] += 1
                    action = 'Created' if created else 'Updated'
                    self.log(f"{action} project: {project.project_id}")
                
                request = service.projects().list_next(previous_request=request, previous_response=response)
                
        except Exception as e:
            self.log(f"Error discovering projects: {str(e)}", 'error')
        
        return projects

    def discover_vpc_networks(self, project):
        from .models import VPCNetwork
        from googleapiclient.discovery import build
        
        self.log(f"Discovering VPC networks in {project.project_id}...")
        
        try:
            service = build('compute', 'v1', credentials=self.credentials)
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
                            'last_synced': timezone.now()
                        }
                    )
                    self.stats['networks'] += 1
                    self.log(f"{'Created' if created else 'Updated'} VPC: {vpc.name}")
                
                request = service.networks().list_next(previous_request=request, previous_response=response)
                
        except Exception as e:
            self.log(f"Error discovering VPC networks: {str(e)}", 'error')

    def discover_subnets(self, project):
        from .models import Subnet, VPCNetwork
        from googleapiclient.discovery import build
        
        self.log(f"Discovering subnets in {project.project_id}...")
        
        try:
            service = build('compute', 'v1', credentials=self.credentials)
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
                                'last_synced': timezone.now()
                            }
                        )
                        self.log(f"{'Created' if created else 'Updated'} subnet: {sub.name}")
                
                request = service.subnetworks().aggregatedList_next(previous_request=request, previous_response=response)
                
        except Exception as e:
            self.log(f"Error discovering subnets: {str(e)}", 'error')

    def discover_firewall_rules(self, project):
        from .models import FirewallRule, VPCNetwork
        from googleapiclient.discovery import build
        
        self.log(f"Discovering firewall rules in {project.project_id}...")
        
        try:
            service = build('compute', 'v1', credentials=self.credentials)
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
                            'last_synced': timezone.now()
                        }
                    )
                    self.log(f"{'Created' if created else 'Updated'} firewall rule: {rule.name}")
                
                request = service.firewalls().list_next(previous_request=request, previous_response=response)
                
        except Exception as e:
            self.log(f"Error discovering firewall rules: {str(e)}", 'error')

    def discover_cloud_routers(self, project):
        from .models import CloudRouter, VPCNetwork
        from googleapiclient.discovery import build
        
        self.log(f"Discovering Cloud Routers in {project.project_id}...")
        
        try:
            service = build('compute', 'v1', credentials=self.credentials)
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
                                'last_synced': timezone.now()
                            }
                        )
                        self.log(f"{'Created' if created else 'Updated'} Cloud Router: {cr.name}")
                
                request = service.routers().aggregatedList_next(previous_request=request, previous_response=response)
                
        except Exception as e:
            self.log(f"Error discovering Cloud Routers: {str(e)}", 'error')

    def discover_vpn_gateways(self, project):
        from .models import VPNGateway, VPCNetwork
        from googleapiclient.discovery import build
        
        self.log(f"Discovering VPN Gateways in {project.project_id}...")
        
        try:
            service = build('compute', 'v1', credentials=self.credentials)
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
                                'last_synced': timezone.now()
                            }
                        )
                        self.log(f"{'Created' if created else 'Updated'} VPN Gateway: {vpn_gw.name}")
                
                request = service.vpnGateways().aggregatedList_next(previous_request=request, previous_response=response)
                
        except Exception as e:
            self.log(f"Error discovering VPN Gateways: {str(e)}", 'error')

    def discover_vpn_tunnels(self, project):
        from .models import VPNTunnel, VPNGateway, CloudRouter
        from googleapiclient.discovery import build
        
        self.log(f"Discovering VPN Tunnels in {project.project_id}...")
        
        try:
            service = build('compute', 'v1', credentials=self.credentials)
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
                                'last_synced': timezone.now()
                            }
                        )
                        self.log(f"{'Created' if created else 'Updated'} VPN Tunnel: {tun.name}")
                
                request = service.vpnTunnels().aggregatedList_next(previous_request=request, previous_response=response)
                
        except Exception as e:
            self.log(f"Error discovering VPN Tunnels: {str(e)}", 'error')

    def discover_compute_instances(self, project):
        from .models import ComputeInstance
        from googleapiclient.discovery import build
        
        self.log(f"Discovering Compute instances in {project.project_id}...")
        
        try:
            service = build('compute', 'v1', credentials=self.credentials)
            request = service.instances().aggregatedList(project=project.project_id)
            
            while request is not None:
                response = request.execute()
                
                for zone, instances_data in response.get('items', {}).items():
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
                                image = boot_disk.get('source', '').split('/')[-1]
                        
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
                                'last_synced': timezone.now()
                            }
                        )
                        self.stats['instances'] += 1
                        self.log(f"{'Created' if created else 'Updated'} instance: {inst.name}")
                
                request = service.instances().aggregatedList_next(previous_request=request, previous_response=response)
                
        except Exception as e:
            self.log(f"Error discovering Compute instances: {str(e)}", 'error')

    def discover_instance_templates(self, project):
        from .models import InstanceTemplate
        from googleapiclient.discovery import build
        
        self.log(f"Discovering Instance Templates in {project.project_id}...")
        
        try:
            service = build('compute', 'v1', credentials=self.credentials)
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
                            'last_synced': timezone.now()
                        }
                    )
                    self.log(f"{'Created' if created else 'Updated'} template: {tmpl.name}")
                
                request = service.instanceTemplates().list_next(previous_request=request, previous_response=response)
                
        except Exception as e:
            self.log(f"Error discovering Instance Templates: {str(e)}", 'error')

    def discover_persistent_disks(self, project):
        from .models import PersistentDisk
        from googleapiclient.discovery import build
        
        self.log(f"Discovering Persistent Disks in {project.project_id}...")
        
        try:
            service = build('compute', 'v1', credentials=self.credentials)
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
                                'last_synced': timezone.now()
                            }
                        )
                        self.log(f"{'Created' if created else 'Updated'} disk: {pd.name}")
                
                request = service.disks().aggregatedList_next(previous_request=request, previous_response=response)
                
        except Exception as e:
            self.log(f"Error discovering Persistent Disks: {str(e)}", 'error')

    def discover_cloud_sql(self, project):
        from .models import CloudSQLInstance
        from googleapiclient.discovery import build
        
        self.log(f"Discovering Cloud SQL instances in {project.project_id}...")
        
        try:
            service = build('sqladmin', 'v1', credentials=self.credentials)
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
                        'last_synced': timezone.now()
                    }
                )
                self.stats['databases'] += 1
                self.log(f"{'Created' if created else 'Updated'} Cloud SQL: {sql.name}")
                
        except Exception as e:
            self.log(f"Error discovering Cloud SQL: {str(e)}", 'error')

    def discover_cloud_spanner(self, project):
        from .models import CloudSpannerInstance
        from googleapiclient.discovery import build
        
        self.log(f"Discovering Cloud Spanner instances in {project.project_id}...")
        
        try:
            service = build('spanner', 'v1', credentials=self.credentials)
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
                        'last_synced': timezone.now()
                    }
                )
                self.stats['databases'] += 1
                self.log(f"{'Created' if created else 'Updated'} Spanner: {spanner.name}")
                
        except Exception as e:
            self.log(f"Error discovering Cloud Spanner: {str(e)}", 'error')

    def discover_storage_buckets(self, project):
        from .models import CloudStorageBucket
        from googleapiclient.discovery import build
        
        self.log(f"Discovering Cloud Storage buckets in {project.project_id}...")
        
        try:
            service = build('storage', 'v1', credentials=self.credentials)
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
                            'last_synced': timezone.now()
                        }
                    )
                    self.stats['buckets'] += 1
                    self.log(f"{'Created' if created else 'Updated'} bucket: {bkt.name}")
                
                request = service.buckets().list_next(previous_request=request, previous_response=response)
                
        except Exception as e:
            self.log(f"Error discovering Storage buckets: {str(e)}", 'error')

    def discover_gke_clusters(self, project):
        from .models import GKECluster, GKENodePool, VPCNetwork, Subnet
        from googleapiclient.discovery import build
        
        self.log(f"Discovering GKE clusters in {project.project_id}...")
        
        try:
            service = build('container', 'v1', credentials=self.credentials)
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
                        'last_synced': timezone.now()
                    }
                )
                self.stats['clusters'] += 1
                self.log(f"{'Created' if created else 'Updated'} GKE cluster: {gke.name}")
                
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
                            'last_synced': timezone.now()
                        }
                    )
                    self.log(f"{'Created' if np_created else 'Updated'} node pool: {np.name}")
                
        except Exception as e:
            self.log(f"Error discovering GKE clusters: {str(e)}", 'error')

    def discover_cloud_functions(self, project):
        from .models import CloudFunction
        from googleapiclient.discovery import build
        
        self.log(f"Discovering Cloud Functions in {project.project_id}...")
        
        try:
            service = build('cloudfunctions', 'v1', credentials=self.credentials)
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
                            'last_synced': timezone.now()
                        }
                    )
                    self.log(f"{'Created' if created else 'Updated'} function: {cf.name}")
                
                request = service.projects().locations().functions().list_next(previous_request=request, previous_response=response)
                
        except Exception as e:
            self.log(f"Error discovering Cloud Functions: {str(e)}", 'error')

    def discover_cloud_run(self, project):
        from .models import CloudRun
        from googleapiclient.discovery import build
        
        self.log(f"Discovering Cloud Run services in {project.project_id}...")
        
        try:
            service = build('run', 'v1', credentials=self.credentials)
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
                        'last_synced': timezone.now()
                    }
                )
                self.log(f"{'Created' if created else 'Updated'} Cloud Run: {cr.name}")
                
        except Exception as e:
            self.log(f"Error discovering Cloud Run: {str(e)}", 'error')

    def discover_service_accounts(self, project):
        from .models import ServiceAccount
        from googleapiclient.discovery import build
        
        self.log(f"Discovering Service Accounts in {project.project_id}...")
        
        try:
            service = build('iam', 'v1', credentials=self.credentials)
            name = f'projects/{project.project_id}'
            request = service.projects().serviceAccounts().list(name=name)
            
            while request is not None:
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
                            'last_synced': timezone.now()
                        }
                    )
                    self.log(f"{'Created' if created else 'Updated'} service account: {svc_acc.email}")
                
                request = service.projects().serviceAccounts().list_next(previous_request=request, previous_response=response)
                
        except Exception as e:
            self.log(f"Error discovering Service Accounts: {str(e)}", 'error')


def run_discovery(organization_id):
    from .models import GCPOrganization
    
    try:
        organization = GCPOrganization.objects.get(pk=organization_id)
        discovery_service = GCPDiscoveryService(organization)
        return discovery_service.discover_all()
    except GCPOrganization.DoesNotExist:
        return False
