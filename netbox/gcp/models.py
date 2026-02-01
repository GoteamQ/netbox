from django.db import models
from django.urls import reverse
from django.core.validators import MinLengthValidator

from netbox.models import NetBoxModel


class GCPOrganization(NetBoxModel):
    name = models.CharField(max_length=255, help_text='Display name for this GCP organization')
    organization_id = models.CharField(
        max_length=50, unique=True, validators=[MinLengthValidator(1)], help_text='GCP Organization ID (numeric)'
    )
    service_account_json = models.TextField(help_text='Service account JSON key content for API authentication')
    is_active = models.BooleanField(default=True, help_text='Enable/disable discovery for this organization')
    last_discovery = models.DateTimeField(null=True, blank=True, help_text='Last successful discovery timestamp')
    discovery_status = models.CharField(
        max_length=50,
        default='pending',
        choices=[
            ('pending', 'Pending'),
            ('running', 'Running'),
            ('canceling', 'Canceling'),
            ('canceled', 'Canceled'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
    )
    cancel_requested = models.BooleanField(default=False, help_text='Cancel the current discovery run')
    discovery_error = models.TextField(blank=True, help_text='Last discovery error message if any')
    auto_discover = models.BooleanField(default=False, help_text='Automatically discover assets on schedule')
    discover_compute = models.BooleanField(default=True, help_text='Discover Compute Engine resources')
    discover_networking = models.BooleanField(default=True, help_text='Discover VPC and networking resources')
    discover_databases = models.BooleanField(default=True, help_text='Discover Cloud SQL and database resources')
    discover_storage = models.BooleanField(default=True, help_text='Discover Cloud Storage resources')
    discover_kubernetes = models.BooleanField(default=True, help_text='Discover GKE clusters')
    discover_serverless = models.BooleanField(default=True, help_text='Discover Cloud Functions and Cloud Run')
    discover_iam = models.BooleanField(default=True, help_text='Discover IAM resources')

    class Meta:
        ordering = ['name']
        verbose_name = 'GCP Organization'
        verbose_name_plural = 'GCP Organizations'

    def __str__(self):
        return f'{self.name} ({self.organization_id})'

    def get_absolute_url(self):
        return reverse('gcp:gcporganization', args=[self.pk])

    def get_service_account_info(self):
        import json

        try:
            return json.loads(self.service_account_json)
        except json.JSONDecodeError:
            return None


class DiscoveryLog(NetBoxModel):
    organization = models.ForeignKey(GCPOrganization, on_delete=models.CASCADE, related_name='discovery_logs')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=50,
        default='running',
        choices=[
            ('running', 'Running'),
            ('canceled', 'Canceled'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
    )
    projects_discovered = models.IntegerField(default=0)
    instances_discovered = models.IntegerField(default=0)
    networks_discovered = models.IntegerField(default=0)
    databases_discovered = models.IntegerField(default=0)
    buckets_discovered = models.IntegerField(default=0)
    clusters_discovered = models.IntegerField(default=0)
    total_resources = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    log_output = models.TextField(blank=True)

    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Discovery Log'
        verbose_name_plural = 'Discovery Logs'

    def __str__(self):
        return f'Discovery {self.organization.name} - {self.started_at}'

    def get_absolute_url(self):
        return reverse('gcp:discoverylog', args=[self.pk])


class GCPProject(NetBoxModel):
    organization = models.ForeignKey(
        GCPOrganization, on_delete=models.CASCADE, related_name='projects', null=True, blank=True
    )
    name = models.CharField(max_length=255)
    project_id = models.CharField(max_length=255, unique=True)
    project_number = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=50, default='ACTIVE')
    labels = models.JSONField(blank=True, null=True)
    discovered = models.BooleanField(default=False, help_text='Was this project auto-discovered')
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'GCP Project'
        verbose_name_plural = 'GCP Projects'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:gcpproject', args=[self.pk])


class ComputeInstance(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='compute_instances')
    zone = models.CharField(max_length=100)
    machine_type = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default='RUNNING')
    internal_ip = models.GenericIPAddressField(blank=True, null=True)
    external_ip = models.GenericIPAddressField(blank=True, null=True)
    network = models.CharField(max_length=255, blank=True)
    subnet = models.CharField(max_length=255, blank=True)
    disk_size_gb = models.IntegerField(default=10)
    image = models.CharField(max_length=255, blank=True)
    labels = models.JSONField(blank=True, null=True)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Compute Instance'
        verbose_name_plural = 'Compute Instances'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:computeinstance', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class InstanceTemplate(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='instance_templates')
    machine_type = models.CharField(max_length=100)
    disk_size_gb = models.IntegerField(default=10)
    image = models.CharField(max_length=255, blank=True)
    network = models.CharField(max_length=255, blank=True)
    subnet = models.CharField(max_length=255, blank=True)
    labels = models.JSONField(blank=True, null=True)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Instance Template'
        verbose_name_plural = 'Instance Templates'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:instancetemplate', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class InstanceGroup(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='instance_groups')
    zone = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    template = models.ForeignKey(InstanceTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    target_size = models.IntegerField(default=1)
    is_managed = models.BooleanField(default=True)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Instance Group'
        verbose_name_plural = 'Instance Groups'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:instancegroup', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class VPCNetwork(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='vpc_networks')
    auto_create_subnetworks = models.BooleanField(default=False)
    routing_mode = models.CharField(max_length=50, default='REGIONAL')
    mtu = models.IntegerField(default=1460)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'VPC Network'
        verbose_name_plural = 'VPC Networks'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:vpcnetwork', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class Subnet(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='subnets')
    network = models.ForeignKey(VPCNetwork, on_delete=models.CASCADE, related_name='subnets')
    region = models.CharField(max_length=100)
    ip_cidr_range = models.CharField(max_length=50)
    gateway_address = models.GenericIPAddressField(blank=True, null=True)
    private_ip_google_access = models.BooleanField(default=False)
    purpose = models.CharField(max_length=50, default='PRIVATE')
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Subnet'
        verbose_name_plural = 'Subnets'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:subnet', args=[self.pk])

    def get_utilization(self):
        # Calculate subnet utilization based on IP range and used IPs
        import ipaddress

        try:
            network = ipaddress.ip_network(self.ip_cidr_range)
            total_ips = network.num_addresses - 2  # Network and Broadcast
            if total_ips < 1:
                total_ips = 1
        except ValueError:
            return 'N/A'

        # Count used IPs (approximation)
        used_count = 0

        # 1. Compute Instances
        # Note: We access ComputeInstance from the global scope (defined above)
        used_count += ComputeInstance.objects.filter(project=self.project, subnet=self.name).count()

        # 2. Other resources (Load Balancers, Cloud SQL) can be added here

        percentage = (used_count / total_ips) * 100
        return f'{percentage:.1f}% ({used_count}/{total_ips})'

    @property
    def organization(self):
        return self.project.organization if self.project else None


class FirewallRule(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='firewall_rules')
    network = models.ForeignKey(VPCNetwork, on_delete=models.CASCADE, related_name='firewall_rules')
    direction = models.CharField(max_length=20, default='INGRESS')
    priority = models.IntegerField(default=1000)
    action = models.CharField(max_length=20, default='allow')
    source_ranges = models.JSONField(blank=True, null=True)
    destination_ranges = models.JSONField(blank=True, null=True)
    source_tags = models.JSONField(blank=True, null=True)
    target_tags = models.JSONField(blank=True, null=True)
    allowed = models.JSONField(blank=True, null=True)
    denied = models.JSONField(blank=True, null=True)
    disabled = models.BooleanField(default=False)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['priority', 'name']
        verbose_name = 'Firewall Rule'
        verbose_name_plural = 'Firewall Rules'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:firewallrule', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class CloudRouter(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='cloud_routers')
    network = models.ForeignKey(VPCNetwork, on_delete=models.CASCADE, related_name='cloud_routers')
    region = models.CharField(max_length=100)
    asn = models.BigIntegerField(default=64512)
    advertise_mode = models.CharField(max_length=50, default='DEFAULT')
    advertised_groups = models.JSONField(blank=True, null=True)
    advertised_ip_ranges = models.JSONField(blank=True, null=True)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Cloud Router'
        verbose_name_plural = 'Cloud Routers'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:cloudrouter', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class CloudNAT(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='cloud_nats')
    router = models.ForeignKey(CloudRouter, on_delete=models.CASCADE, related_name='nats')
    region = models.CharField(max_length=100)
    nat_ip_allocate_option = models.CharField(max_length=50, default='AUTO_ONLY')
    source_subnetwork_ip_ranges_to_nat = models.CharField(max_length=100, default='ALL_SUBNETWORKS_ALL_IP_RANGES')
    nat_ips = models.JSONField(blank=True, null=True)
    min_ports_per_vm = models.IntegerField(default=64)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Cloud NAT'
        verbose_name_plural = 'Cloud NATs'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:cloudnat', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class LoadBalancer(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='load_balancers')
    scheme = models.CharField(max_length=50, default='EXTERNAL')
    lb_type = models.CharField(max_length=50, default='HTTP')
    region = models.CharField(max_length=100, blank=True)
    network = models.ForeignKey(VPCNetwork, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    port = models.IntegerField(default=80)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Load Balancer'
        verbose_name_plural = 'Load Balancers'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:loadbalancer', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class CloudSQLInstance(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='cloud_sql_instances')
    region = models.CharField(max_length=100)
    database_type = models.CharField(max_length=50, default='MYSQL')
    database_version = models.CharField(max_length=50)
    tier = models.CharField(max_length=50)
    storage_size_gb = models.IntegerField(default=10)
    storage_type = models.CharField(max_length=20, default='SSD')
    status = models.CharField(max_length=50, default='RUNNABLE')
    ip_addresses = models.JSONField(blank=True, null=True)
    connection_name = models.CharField(max_length=255, blank=True)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Cloud SQL Instance'
        verbose_name_plural = 'Cloud SQL Instances'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:cloudsqlinstance', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class CloudSpannerInstance(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='cloud_spanner_instances')
    config = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255, blank=True)
    node_count = models.IntegerField(default=1)
    processing_units = models.IntegerField(default=100)
    status = models.CharField(max_length=50, default='READY')
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Cloud Spanner Instance'
        verbose_name_plural = 'Cloud Spanner Instances'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:cloudspannerinstance', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class FirestoreDatabase(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='firestore_databases')
    location = models.CharField(max_length=100)
    database_type = models.CharField(max_length=50, default='FIRESTORE_NATIVE')
    concurrency_mode = models.CharField(max_length=50, default='OPTIMISTIC')
    status = models.CharField(max_length=50, default='ACTIVE')
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Firestore Database'
        verbose_name_plural = 'Firestore Databases'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:firestoredatabase', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class BigtableInstance(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='bigtable_instances')
    display_name = models.CharField(max_length=255, blank=True)
    instance_type = models.CharField(max_length=50, default='PRODUCTION')
    storage_type = models.CharField(max_length=50, default='SSD')
    status = models.CharField(max_length=50, default='READY')
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Bigtable Instance'
        verbose_name_plural = 'Bigtable Instances'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:bigtableinstance', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class CloudStorageBucket(NetBoxModel):
    name = models.CharField(max_length=255, unique=True)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='storage_buckets')
    location = models.CharField(max_length=100)
    storage_class = models.CharField(max_length=50, default='STANDARD')
    versioning_enabled = models.BooleanField(default=False)
    lifecycle_rules = models.JSONField(blank=True, null=True)
    labels = models.JSONField(blank=True, null=True)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Cloud Storage Bucket'
        verbose_name_plural = 'Cloud Storage Buckets'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:cloudstoragebucket', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class PersistentDisk(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='persistent_disks')
    zone = models.CharField(max_length=100)
    disk_type = models.CharField(max_length=50, default='pd-standard')
    size_gb = models.IntegerField(default=10)
    status = models.CharField(max_length=50, default='READY')
    source_image = models.CharField(max_length=255, blank=True)
    users = models.JSONField(blank=True, null=True)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Persistent Disk'
        verbose_name_plural = 'Persistent Disks'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:persistentdisk', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class GKECluster(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='gke_clusters')
    location = models.CharField(max_length=100)
    network = models.ForeignKey(VPCNetwork, on_delete=models.SET_NULL, null=True, blank=True)
    subnetwork = models.ForeignKey(Subnet, on_delete=models.SET_NULL, null=True, blank=True)
    master_version = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default='RUNNING')
    endpoint = models.CharField(max_length=255, blank=True)
    cluster_ipv4_cidr = models.CharField(max_length=50, blank=True)
    services_ipv4_cidr = models.CharField(max_length=50, blank=True)
    enable_autopilot = models.BooleanField(default=False)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'GKE Cluster'
        verbose_name_plural = 'GKE Clusters'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:gkecluster', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class GKENodePool(NetBoxModel):
    name = models.CharField(max_length=255)
    cluster = models.ForeignKey(GKECluster, on_delete=models.CASCADE, related_name='node_pools')
    machine_type = models.CharField(max_length=100)
    disk_size_gb = models.IntegerField(default=100)
    disk_type = models.CharField(max_length=50, default='pd-standard')
    node_count = models.IntegerField(default=3)
    min_node_count = models.IntegerField(default=1)
    max_node_count = models.IntegerField(default=10)
    status = models.CharField(max_length=50, default='RUNNING')
    version = models.CharField(max_length=50, blank=True)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'GKE Node Pool'
        verbose_name_plural = 'GKE Node Pools'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:gkenodepool', args=[self.pk])

    @property
    def organization(self):
        return self.cluster.project.organization if self.cluster and self.cluster.project else None


class ServiceAccount(NetBoxModel):
    email = models.EmailField(unique=True)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='service_accounts')
    display_name = models.CharField(max_length=255, blank=True)
    unique_id = models.CharField(max_length=50, blank=True)
    disabled = models.BooleanField(default=False)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['email']
        verbose_name = 'Service Account'
        verbose_name_plural = 'Service Accounts'

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse('gcp:serviceaccount', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class IAMRole(NetBoxModel):
    name = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    permissions = models.JSONField(blank=True, null=True)
    stage = models.CharField(max_length=50, default='GA')
    is_custom = models.BooleanField(default=False)
    project = models.ForeignKey(
        GCPProject, on_delete=models.CASCADE, null=True, blank=True, related_name='custom_roles'
    )
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'IAM Role'
        verbose_name_plural = 'IAM Roles'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:iamrole', args=[self.pk])


class IAMBinding(NetBoxModel):
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='iam_bindings')
    role = models.ForeignKey(IAMRole, on_delete=models.CASCADE, related_name='bindings')
    member = models.CharField(max_length=255)
    condition = models.JSONField(blank=True, null=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['project', 'role']
        verbose_name = 'IAM Binding'
        verbose_name_plural = 'IAM Bindings'
        unique_together = ['project', 'role', 'member']

    def __str__(self):
        return f'{self.project} - {self.role} - {self.member}'

    def get_absolute_url(self):
        return reverse('gcp:iambinding', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class CloudFunction(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='cloud_functions')
    region = models.CharField(max_length=100)
    runtime = models.CharField(max_length=50)
    entry_point = models.CharField(max_length=255, blank=True)
    trigger_type = models.CharField(max_length=50, default='HTTP')
    trigger_url = models.URLField(max_length=500, blank=True)
    memory_mb = models.IntegerField(default=256)
    timeout_seconds = models.IntegerField(default=60)
    status = models.CharField(max_length=50, default='ACTIVE')
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Cloud Function'
        verbose_name_plural = 'Cloud Functions'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:cloudfunction', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class CloudRun(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='cloud_run_services')
    region = models.CharField(max_length=100)
    image = models.CharField(max_length=500, blank=True)
    url = models.URLField(max_length=500, blank=True)
    cpu = models.CharField(max_length=20, default='1')
    memory = models.CharField(max_length=20, default='512Mi')
    max_instances = models.IntegerField(default=100)
    min_instances = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default='ACTIVE')
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Cloud Run Service'
        verbose_name_plural = 'Cloud Run Services'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:cloudrun', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class PubSubTopic(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='pubsub_topics')
    labels = models.JSONField(blank=True, null=True)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Pub/Sub Topic'
        verbose_name_plural = 'Pub/Sub Topics'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:pubsubtopic', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class PubSubSubscription(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='pubsub_subscriptions')
    topic = models.ForeignKey(PubSubTopic, on_delete=models.CASCADE, related_name='subscriptions')
    ack_deadline_seconds = models.IntegerField(default=10)
    push_endpoint = models.URLField(max_length=500, blank=True)
    message_retention_duration = models.CharField(max_length=50, default='604800s')
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Pub/Sub Subscription'
        verbose_name_plural = 'Pub/Sub Subscriptions'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:pubsubsubscription', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class SecretManagerSecret(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='secrets')
    replication_type = models.CharField(max_length=50, default='AUTOMATIC')
    replication_locations = models.JSONField(blank=True, null=True)
    labels = models.JSONField(blank=True, null=True)
    version_count = models.IntegerField(default=0)
    latest_version = models.CharField(max_length=50, blank=True)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Secret Manager Secret'
        verbose_name_plural = 'Secret Manager Secrets'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:secretmanagersecret', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class CloudDNSZone(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='dns_zones')
    dns_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    visibility = models.CharField(max_length=50, default='public')
    name_servers = models.JSONField(blank=True, null=True)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Cloud DNS Zone'
        verbose_name_plural = 'Cloud DNS Zones'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:clouddnszone', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class CloudDNSRecord(NetBoxModel):
    name = models.CharField(max_length=255)
    zone = models.ForeignKey(CloudDNSZone, on_delete=models.CASCADE, related_name='records')
    record_type = models.CharField(max_length=20)
    ttl = models.IntegerField(default=300)
    rrdatas = models.JSONField(blank=True, null=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Cloud DNS Record'
        verbose_name_plural = 'Cloud DNS Records'

    def __str__(self):
        return f'{self.name} ({self.record_type})'

    def get_absolute_url(self):
        return reverse('gcp:clouddnsrecord', args=[self.pk])

    @property
    def organization(self):
        return self.zone.project.organization if self.zone and self.zone.project else None


class MemorystoreInstance(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='memorystore_instances')
    region = models.CharField(max_length=100)
    tier = models.CharField(max_length=50, default='BASIC')
    memory_size_gb = models.IntegerField(default=1)
    redis_version = models.CharField(max_length=50, default='REDIS_6_X')
    host = models.CharField(max_length=255, blank=True)
    port = models.IntegerField(default=6379)
    status = models.CharField(max_length=50, default='READY')
    network = models.ForeignKey(VPCNetwork, on_delete=models.SET_NULL, null=True, blank=True)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Memorystore Instance'
        verbose_name_plural = 'Memorystore Instances'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:memorystoreinstance', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class NCCHub(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='ncc_hubs')
    description = models.TextField(blank=True)
    labels = models.JSONField(blank=True, null=True)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'NCC Hub'
        verbose_name_plural = 'NCC Hubs'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:ncchub', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class NCCSpoke(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='ncc_spokes')
    hub = models.ForeignKey(NCCHub, on_delete=models.CASCADE, related_name='spokes')
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    spoke_type = models.CharField(max_length=50, default='VPC_NETWORK')
    linked_vpc_network = models.ForeignKey(
        VPCNetwork, on_delete=models.SET_NULL, null=True, blank=True, related_name='ncc_spokes'
    )
    linked_vpn_tunnels = models.JSONField(blank=True, null=True)
    linked_interconnect_attachments = models.JSONField(blank=True, null=True)
    labels = models.JSONField(blank=True, null=True)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'NCC Spoke'
        verbose_name_plural = 'NCC Spokes'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:nccspoke', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class VPNGateway(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='vpn_gateways')
    network = models.ForeignKey(VPCNetwork, on_delete=models.CASCADE, related_name='vpn_gateways')
    region = models.CharField(max_length=100)
    gateway_type = models.CharField(max_length=50, default='HA_VPN')
    ip_addresses = models.JSONField(blank=True, null=True)
    labels = models.JSONField(blank=True, null=True)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'VPN Gateway'
        verbose_name_plural = 'VPN Gateways'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:vpngateway', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class ExternalVPNGateway(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='external_vpn_gateways')
    description = models.TextField(blank=True)
    redundancy_type = models.CharField(max_length=50, default='SINGLE_IP_INTERNALLY_REDUNDANT')
    interfaces = models.JSONField(blank=True, null=True)
    labels = models.JSONField(blank=True, null=True)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'External VPN Gateway'
        verbose_name_plural = 'External VPN Gateways'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:externalvpngateway', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class VPNTunnel(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='vpn_tunnels')
    region = models.CharField(max_length=100)
    vpn_gateway = models.ForeignKey(VPNGateway, on_delete=models.CASCADE, related_name='tunnels', null=True, blank=True)
    vpn_gateway_interface = models.IntegerField(default=0)
    peer_external_gateway = models.ForeignKey(
        ExternalVPNGateway, on_delete=models.SET_NULL, null=True, blank=True, related_name='tunnels'
    )
    peer_external_gateway_interface = models.IntegerField(default=0)
    peer_ip = models.GenericIPAddressField(blank=True, null=True)
    shared_secret_hash = models.CharField(max_length=255, blank=True)
    ike_version = models.IntegerField(default=2)
    local_traffic_selector = models.JSONField(blank=True, null=True)
    remote_traffic_selector = models.JSONField(blank=True, null=True)
    router = models.ForeignKey(
        CloudRouter, on_delete=models.SET_NULL, null=True, blank=True, related_name='vpn_tunnels'
    )
    status = models.CharField(max_length=50, default='ESTABLISHED')
    detailed_status = models.CharField(max_length=255, blank=True)
    labels = models.JSONField(blank=True, null=True)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'VPN Tunnel'
        verbose_name_plural = 'VPN Tunnels'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:vpntunnel', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class InterconnectAttachment(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='interconnect_attachments')
    region = models.CharField(max_length=100)
    router = models.ForeignKey(CloudRouter, on_delete=models.CASCADE, related_name='interconnect_attachments')
    attachment_type = models.CharField(max_length=50, default='DEDICATED')
    edge_availability_domain = models.CharField(max_length=50, blank=True)
    bandwidth = models.CharField(max_length=50, default='BPS_1G')
    vlan_tag = models.IntegerField(default=0)
    pairing_key = models.CharField(max_length=255, blank=True)
    partner_asn = models.BigIntegerField(null=True, blank=True)
    cloud_router_ip_address = models.GenericIPAddressField(blank=True, null=True)
    customer_router_ip_address = models.GenericIPAddressField(blank=True, null=True)
    state = models.CharField(max_length=50, default='ACTIVE')
    labels = models.JSONField(blank=True, null=True)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Interconnect Attachment'
        verbose_name_plural = 'Interconnect Attachments'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:interconnectattachment', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class ServiceAttachment(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='service_attachments')
    region = models.CharField(max_length=100)
    connection_preference = models.CharField(max_length=50, default='ACCEPT_AUTOMATIC')
    nat_subnets = models.JSONField(blank=True, null=True)
    target_service = models.CharField(max_length=500, blank=True)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Service Attachment'
        verbose_name_plural = 'Service Attachments'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:serviceattachment', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None


class ServiceConnectEndpoint(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='psc_endpoints')
    region = models.CharField(max_length=100)
    network = models.ForeignKey(VPCNetwork, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    target_service_attachment = models.CharField(max_length=500, blank=True)
    self_link = models.URLField(max_length=500, blank=True)
    discovered = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'PSC Endpoint'
        verbose_name_plural = 'PSC Endpoints'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:serviceconnectendpoint', args=[self.pk])

    @property
    def organization(self):
        return self.project.organization if self.project else None
