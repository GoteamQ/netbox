from django.db import models
from django.urls import reverse

from netbox.models import NetBoxModel


class GCPProject(NetBoxModel):
    name = models.CharField(max_length=255)
    project_id = models.CharField(max_length=255, unique=True)
    project_number = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=50, default='ACTIVE')
    labels = models.JSONField(blank=True, null=True)

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

    class Meta:
        ordering = ['name']
        verbose_name = 'Compute Instance'
        verbose_name_plural = 'Compute Instances'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:computeinstance', args=[self.pk])


class InstanceTemplate(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='instance_templates')
    machine_type = models.CharField(max_length=100)
    disk_size_gb = models.IntegerField(default=10)
    image = models.CharField(max_length=255, blank=True)
    network = models.CharField(max_length=255, blank=True)
    subnet = models.CharField(max_length=255, blank=True)
    labels = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Instance Template'
        verbose_name_plural = 'Instance Templates'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:instancetemplate', args=[self.pk])


class InstanceGroup(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='instance_groups')
    zone = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    template = models.ForeignKey(InstanceTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    target_size = models.IntegerField(default=1)
    is_managed = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Instance Group'
        verbose_name_plural = 'Instance Groups'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:instancegroup', args=[self.pk])


class VPCNetwork(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='vpc_networks')
    auto_create_subnetworks = models.BooleanField(default=False)
    routing_mode = models.CharField(max_length=50, default='REGIONAL')
    mtu = models.IntegerField(default=1460)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'VPC Network'
        verbose_name_plural = 'VPC Networks'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:vpcnetwork', args=[self.pk])


class Subnet(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='subnets')
    network = models.ForeignKey(VPCNetwork, on_delete=models.CASCADE, related_name='subnets')
    region = models.CharField(max_length=100)
    ip_cidr_range = models.CharField(max_length=50)
    private_ip_google_access = models.BooleanField(default=False)
    secondary_ip_ranges = models.JSONField(blank=True, null=True)
    purpose = models.CharField(max_length=50, default='PRIVATE')

    class Meta:
        ordering = ['name']
        verbose_name = 'Subnet'
        verbose_name_plural = 'Subnets'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:subnet', args=[self.pk])


class FirewallRule(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='firewall_rules')
    network = models.ForeignKey(VPCNetwork, on_delete=models.CASCADE, related_name='firewall_rules')
    direction = models.CharField(max_length=20, default='INGRESS')
    priority = models.IntegerField(default=1000)
    action = models.CharField(max_length=20, default='ALLOW')
    source_ranges = models.JSONField(blank=True, null=True)
    destination_ranges = models.JSONField(blank=True, null=True)
    source_tags = models.JSONField(blank=True, null=True)
    target_tags = models.JSONField(blank=True, null=True)
    allowed = models.JSONField(blank=True, null=True)
    denied = models.JSONField(blank=True, null=True)
    disabled = models.BooleanField(default=False)

    class Meta:
        ordering = ['priority', 'name']
        verbose_name = 'Firewall Rule'
        verbose_name_plural = 'Firewall Rules'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:firewallrule', args=[self.pk])


class CloudRouter(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='cloud_routers')
    network = models.ForeignKey(VPCNetwork, on_delete=models.CASCADE, related_name='cloud_routers')
    region = models.CharField(max_length=100)
    asn = models.IntegerField(default=64512)
    advertise_mode = models.CharField(max_length=50, default='DEFAULT')
    advertised_ip_ranges = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Cloud Router'
        verbose_name_plural = 'Cloud Routers'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:cloudrouter', args=[self.pk])


class CloudNAT(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='cloud_nats')
    router = models.ForeignKey(CloudRouter, on_delete=models.CASCADE, related_name='nat_configs')
    region = models.CharField(max_length=100)
    nat_ip_allocate_option = models.CharField(max_length=50, default='AUTO_ONLY')
    source_subnetwork_ip_ranges = models.CharField(max_length=100, default='ALL_SUBNETWORKS_ALL_IP_RANGES')
    nat_ips = models.JSONField(blank=True, null=True)
    min_ports_per_vm = models.IntegerField(default=64)

    class Meta:
        ordering = ['name']
        verbose_name = 'Cloud NAT'
        verbose_name_plural = 'Cloud NATs'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:cloudnat', args=[self.pk])


class LoadBalancer(NetBoxModel):
    SCHEME_CHOICES = [
        ('EXTERNAL', 'External'),
        ('INTERNAL', 'Internal'),
        ('INTERNAL_MANAGED', 'Internal Managed'),
    ]
    TYPE_CHOICES = [
        ('HTTP', 'HTTP(S)'),
        ('TCP', 'TCP'),
        ('UDP', 'UDP'),
        ('SSL', 'SSL Proxy'),
        ('TCP_PROXY', 'TCP Proxy'),
    ]

    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='load_balancers')
    scheme = models.CharField(max_length=50, choices=SCHEME_CHOICES, default='EXTERNAL')
    lb_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='HTTP')
    region = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    port = models.IntegerField(default=80)
    backend_services = models.JSONField(blank=True, null=True)
    health_check = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Load Balancer'
        verbose_name_plural = 'Load Balancers'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:loadbalancer', args=[self.pk])


class CloudSQLInstance(NetBoxModel):
    DATABASE_CHOICES = [
        ('MYSQL', 'MySQL'),
        ('POSTGRES', 'PostgreSQL'),
        ('SQLSERVER', 'SQL Server'),
    ]

    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='cloudsql_instances')
    region = models.CharField(max_length=100)
    database_version = models.CharField(max_length=50)
    database_type = models.CharField(max_length=20, choices=DATABASE_CHOICES, default='MYSQL')
    tier = models.CharField(max_length=50)
    storage_size_gb = models.IntegerField(default=10)
    storage_type = models.CharField(max_length=20, default='SSD')
    status = models.CharField(max_length=50, default='RUNNABLE')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    private_ip = models.GenericIPAddressField(blank=True, null=True)
    connection_name = models.CharField(max_length=255, blank=True)
    high_availability = models.BooleanField(default=False)
    backup_enabled = models.BooleanField(default=True)
    labels = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Cloud SQL Instance'
        verbose_name_plural = 'Cloud SQL Instances'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:cloudsqlinstance', args=[self.pk])


class CloudSpannerInstance(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='spanner_instances')
    config = models.CharField(max_length=100)
    display_name = models.CharField(max_length=255)
    node_count = models.IntegerField(default=1)
    processing_units = models.IntegerField(default=100)
    status = models.CharField(max_length=50, default='READY')
    labels = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Cloud Spanner Instance'
        verbose_name_plural = 'Cloud Spanner Instances'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:cloudspannerinstance', args=[self.pk])


class FirestoreDatabase(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='firestore_databases')
    location = models.CharField(max_length=100)
    database_type = models.CharField(max_length=50, default='FIRESTORE_NATIVE')
    concurrency_mode = models.CharField(max_length=50, default='OPTIMISTIC')
    status = models.CharField(max_length=50, default='ACTIVE')

    class Meta:
        ordering = ['name']
        verbose_name = 'Firestore Database'
        verbose_name_plural = 'Firestore Databases'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:firestoredatabase', args=[self.pk])


class BigtableInstance(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='bigtable_instances')
    display_name = models.CharField(max_length=255)
    instance_type = models.CharField(max_length=50, default='PRODUCTION')
    storage_type = models.CharField(max_length=20, default='SSD')
    status = models.CharField(max_length=50, default='READY')
    labels = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Bigtable Instance'
        verbose_name_plural = 'Bigtable Instances'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:bigtableinstance', args=[self.pk])


class CloudStorageBucket(NetBoxModel):
    STORAGE_CLASS_CHOICES = [
        ('STANDARD', 'Standard'),
        ('NEARLINE', 'Nearline'),
        ('COLDLINE', 'Coldline'),
        ('ARCHIVE', 'Archive'),
    ]

    name = models.CharField(max_length=255, unique=True)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='storage_buckets')
    location = models.CharField(max_length=100)
    storage_class = models.CharField(max_length=20, choices=STORAGE_CLASS_CHOICES, default='STANDARD')
    versioning_enabled = models.BooleanField(default=False)
    uniform_bucket_level_access = models.BooleanField(default=True)
    public_access_prevention = models.CharField(max_length=50, default='enforced')
    lifecycle_rules = models.JSONField(blank=True, null=True)
    labels = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Cloud Storage Bucket'
        verbose_name_plural = 'Cloud Storage Buckets'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:cloudstoragebucket', args=[self.pk])


class PersistentDisk(NetBoxModel):
    DISK_TYPE_CHOICES = [
        ('pd-standard', 'Standard'),
        ('pd-balanced', 'Balanced'),
        ('pd-ssd', 'SSD'),
        ('pd-extreme', 'Extreme'),
    ]

    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='persistent_disks')
    zone = models.CharField(max_length=100)
    disk_type = models.CharField(max_length=50, choices=DISK_TYPE_CHOICES, default='pd-balanced')
    size_gb = models.IntegerField(default=10)
    status = models.CharField(max_length=50, default='READY')
    source_image = models.CharField(max_length=255, blank=True)
    source_snapshot = models.CharField(max_length=255, blank=True)
    attached_instances = models.JSONField(blank=True, null=True)
    labels = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Persistent Disk'
        verbose_name_plural = 'Persistent Disks'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:persistentdisk', args=[self.pk])


class GKECluster(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='gke_clusters')
    location = models.CharField(max_length=100)
    network = models.ForeignKey(VPCNetwork, on_delete=models.SET_NULL, null=True, blank=True)
    subnet = models.ForeignKey(Subnet, on_delete=models.SET_NULL, null=True, blank=True)
    master_version = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default='RUNNING')
    endpoint = models.CharField(max_length=255, blank=True)
    cluster_ipv4_cidr = models.CharField(max_length=50, blank=True)
    services_ipv4_cidr = models.CharField(max_length=50, blank=True)
    enable_autopilot = models.BooleanField(default=False)
    private_cluster = models.BooleanField(default=False)
    labels = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'GKE Cluster'
        verbose_name_plural = 'GKE Clusters'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:gkecluster', args=[self.pk])


class GKENodePool(NetBoxModel):
    name = models.CharField(max_length=255)
    cluster = models.ForeignKey(GKECluster, on_delete=models.CASCADE, related_name='node_pools')
    machine_type = models.CharField(max_length=100)
    disk_size_gb = models.IntegerField(default=100)
    disk_type = models.CharField(max_length=50, default='pd-standard')
    node_count = models.IntegerField(default=3)
    min_node_count = models.IntegerField(default=1)
    max_node_count = models.IntegerField(default=10)
    autoscaling_enabled = models.BooleanField(default=True)
    preemptible = models.BooleanField(default=False)
    spot = models.BooleanField(default=False)
    status = models.CharField(max_length=50, default='RUNNING')
    version = models.CharField(max_length=50, blank=True)
    labels = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'GKE Node Pool'
        verbose_name_plural = 'GKE Node Pools'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:gkenodepool', args=[self.pk])


class ServiceAccount(NetBoxModel):
    email = models.EmailField(unique=True)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='service_accounts')
    display_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    disabled = models.BooleanField(default=False)
    unique_id = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['email']
        verbose_name = 'Service Account'
        verbose_name_plural = 'Service Accounts'

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse('gcp:serviceaccount', args=[self.pk])


class IAMRole(NetBoxModel):
    name = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    stage = models.CharField(max_length=20, default='GA')
    included_permissions = models.JSONField(blank=True, null=True)
    is_custom = models.BooleanField(default=False)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, null=True, blank=True, related_name='custom_roles')

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

    class Meta:
        ordering = ['project', 'role']
        verbose_name = 'IAM Binding'
        verbose_name_plural = 'IAM Bindings'
        unique_together = ['project', 'role', 'member']

    def __str__(self):
        return f"{self.member} -> {self.role.name}"

    def get_absolute_url(self):
        return reverse('gcp:iambinding', args=[self.pk])


class CloudFunction(NetBoxModel):
    RUNTIME_CHOICES = [
        ('python39', 'Python 3.9'),
        ('python310', 'Python 3.10'),
        ('python311', 'Python 3.11'),
        ('nodejs16', 'Node.js 16'),
        ('nodejs18', 'Node.js 18'),
        ('nodejs20', 'Node.js 20'),
        ('go119', 'Go 1.19'),
        ('go121', 'Go 1.21'),
        ('java11', 'Java 11'),
        ('java17', 'Java 17'),
    ]

    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='cloud_functions')
    region = models.CharField(max_length=100)
    runtime = models.CharField(max_length=20, choices=RUNTIME_CHOICES)
    entry_point = models.CharField(max_length=255)
    trigger_type = models.CharField(max_length=50, default='HTTP')
    trigger_url = models.URLField(blank=True)
    memory_mb = models.IntegerField(default=256)
    timeout_seconds = models.IntegerField(default=60)
    max_instances = models.IntegerField(default=100)
    min_instances = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default='ACTIVE')
    service_account = models.ForeignKey(ServiceAccount, on_delete=models.SET_NULL, null=True, blank=True)
    environment_variables = models.JSONField(blank=True, null=True)
    labels = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Cloud Function'
        verbose_name_plural = 'Cloud Functions'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:cloudfunction', args=[self.pk])


class CloudRun(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='cloud_run_services')
    region = models.CharField(max_length=100)
    image = models.CharField(max_length=500)
    url = models.URLField(blank=True)
    port = models.IntegerField(default=8080)
    cpu = models.CharField(max_length=10, default='1')
    memory = models.CharField(max_length=20, default='512Mi')
    max_instances = models.IntegerField(default=100)
    min_instances = models.IntegerField(default=0)
    concurrency = models.IntegerField(default=80)
    timeout_seconds = models.IntegerField(default=300)
    status = models.CharField(max_length=50, default='ACTIVE')
    service_account = models.ForeignKey(ServiceAccount, on_delete=models.SET_NULL, null=True, blank=True)
    ingress = models.CharField(max_length=50, default='all')
    labels = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Cloud Run Service'
        verbose_name_plural = 'Cloud Run Services'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:cloudrun', args=[self.pk])


class PubSubTopic(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='pubsub_topics')
    labels = models.JSONField(blank=True, null=True)
    message_retention_duration = models.CharField(max_length=50, blank=True)
    schema_settings = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Pub/Sub Topic'
        verbose_name_plural = 'Pub/Sub Topics'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:pubsubtopic', args=[self.pk])


class PubSubSubscription(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='pubsub_subscriptions')
    topic = models.ForeignKey(PubSubTopic, on_delete=models.CASCADE, related_name='subscriptions')
    ack_deadline_seconds = models.IntegerField(default=10)
    message_retention_duration = models.CharField(max_length=50, default='604800s')
    push_endpoint = models.URLField(blank=True)
    filter_expression = models.TextField(blank=True)
    dead_letter_topic = models.ForeignKey(PubSubTopic, on_delete=models.SET_NULL, null=True, blank=True, related_name='dead_letter_subscriptions')
    labels = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Pub/Sub Subscription'
        verbose_name_plural = 'Pub/Sub Subscriptions'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:pubsubsubscription', args=[self.pk])


class SecretManagerSecret(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='secrets')
    replication_type = models.CharField(max_length=50, default='automatic')
    replication_locations = models.JSONField(blank=True, null=True)
    labels = models.JSONField(blank=True, null=True)
    version_count = models.IntegerField(default=0)
    latest_version = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Secret Manager Secret'
        verbose_name_plural = 'Secret Manager Secrets'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:secretmanagersecret', args=[self.pk])


class CloudDNSZone(NetBoxModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='dns_zones')
    dns_name = models.CharField(max_length=255)
    visibility = models.CharField(max_length=20, default='public')
    description = models.TextField(blank=True)
    name_servers = models.JSONField(blank=True, null=True)
    labels = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Cloud DNS Zone'
        verbose_name_plural = 'Cloud DNS Zones'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:clouddnszone', args=[self.pk])


class CloudDNSRecord(NetBoxModel):
    zone = models.ForeignKey(CloudDNSZone, on_delete=models.CASCADE, related_name='records')
    name = models.CharField(max_length=255)
    record_type = models.CharField(max_length=10)
    ttl = models.IntegerField(default=300)
    rrdatas = models.JSONField()

    class Meta:
        ordering = ['name', 'record_type']
        verbose_name = 'Cloud DNS Record'
        verbose_name_plural = 'Cloud DNS Records'

    def __str__(self):
        return f"{self.name} ({self.record_type})"

    def get_absolute_url(self):
        return reverse('gcp:clouddnsrecord', args=[self.pk])


class MemorystoreInstance(NetBoxModel):
    TIER_CHOICES = [
        ('BASIC', 'Basic'),
        ('STANDARD_HA', 'Standard HA'),
    ]

    name = models.CharField(max_length=255)
    project = models.ForeignKey(GCPProject, on_delete=models.CASCADE, related_name='memorystore_instances')
    region = models.CharField(max_length=100)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='BASIC')
    memory_size_gb = models.IntegerField(default=1)
    redis_version = models.CharField(max_length=20, default='REDIS_6_X')
    host = models.CharField(max_length=255, blank=True)
    port = models.IntegerField(default=6379)
    status = models.CharField(max_length=50, default='READY')
    authorized_network = models.ForeignKey(VPCNetwork, on_delete=models.SET_NULL, null=True, blank=True)
    labels = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Memorystore Instance'
        verbose_name_plural = 'Memorystore Instances'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gcp:memorystoreinstance', args=[self.pk])
