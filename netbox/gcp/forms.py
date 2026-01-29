from django import forms

from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import DynamicModelChoiceField
from .models import (
    GCPProject, ComputeInstance, InstanceTemplate, InstanceGroup,
    VPCNetwork, Subnet, FirewallRule, CloudRouter, CloudNAT, LoadBalancer,
    CloudSQLInstance, CloudSpannerInstance, FirestoreDatabase, BigtableInstance,
    CloudStorageBucket, PersistentDisk,
    GKECluster, GKENodePool,
    ServiceAccount, IAMRole, IAMBinding,
    CloudFunction, CloudRun, PubSubTopic, PubSubSubscription,
    SecretManagerSecret, CloudDNSZone, CloudDNSRecord, MemorystoreInstance
)


class GCPProjectForm(NetBoxModelForm):
    class Meta:
        model = GCPProject
        fields = ['name', 'project_id', 'project_number', 'status', 'labels', 'tags']


class GCPProjectFilterForm(NetBoxModelFilterSetForm):
    model = GCPProject
    name = forms.CharField(required=False)
    project_id = forms.CharField(required=False)
    status = forms.CharField(required=False)


class ComputeInstanceForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = ComputeInstance
        fields = ['name', 'project', 'zone', 'machine_type', 'status', 'internal_ip', 'external_ip', 
                  'network', 'subnet', 'disk_size_gb', 'image', 'labels', 'tags']


class ComputeInstanceFilterForm(NetBoxModelFilterSetForm):
    model = ComputeInstance
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)
    zone = forms.CharField(required=False)
    status = forms.CharField(required=False)


class InstanceTemplateForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = InstanceTemplate
        fields = ['name', 'project', 'machine_type', 'disk_size_gb', 'image', 'network', 'subnet', 'labels', 'tags']


class InstanceGroupForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())
    template = DynamicModelChoiceField(queryset=InstanceTemplate.objects.all(), required=False)

    class Meta:
        model = InstanceGroup
        fields = ['name', 'project', 'zone', 'region', 'template', 'target_size', 'is_managed', 'tags']


class VPCNetworkForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = VPCNetwork
        fields = ['name', 'project', 'auto_create_subnetworks', 'routing_mode', 'mtu', 'description', 'tags']


class VPCNetworkFilterForm(NetBoxModelFilterSetForm):
    model = VPCNetwork
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)
    routing_mode = forms.CharField(required=False)


class SubnetForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())
    network = DynamicModelChoiceField(queryset=VPCNetwork.objects.all())

    class Meta:
        model = Subnet
        fields = ['name', 'project', 'network', 'region', 'ip_cidr_range', 'private_ip_google_access', 
                  'secondary_ip_ranges', 'purpose', 'tags']


class SubnetFilterForm(NetBoxModelFilterSetForm):
    model = Subnet
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    network = DynamicModelChoiceField(queryset=VPCNetwork.objects.all(), required=False)
    region = forms.CharField(required=False)


class FirewallRuleForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())
    network = DynamicModelChoiceField(queryset=VPCNetwork.objects.all())

    class Meta:
        model = FirewallRule
        fields = ['name', 'project', 'network', 'direction', 'priority', 'action', 'source_ranges', 
                  'destination_ranges', 'source_tags', 'target_tags', 'allowed', 'denied', 'disabled', 'tags']


class CloudRouterForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())
    network = DynamicModelChoiceField(queryset=VPCNetwork.objects.all())

    class Meta:
        model = CloudRouter
        fields = ['name', 'project', 'network', 'region', 'asn', 'advertise_mode', 'advertised_ip_ranges', 'tags']


class CloudNATForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())
    router = DynamicModelChoiceField(queryset=CloudRouter.objects.all())

    class Meta:
        model = CloudNAT
        fields = ['name', 'project', 'router', 'region', 'nat_ip_allocate_option', 
                  'source_subnetwork_ip_ranges', 'nat_ips', 'min_ports_per_vm', 'tags']


class LoadBalancerForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = LoadBalancer
        fields = ['name', 'project', 'scheme', 'lb_type', 'region', 'ip_address', 'port', 
                  'backend_services', 'health_check', 'tags']


class CloudSQLInstanceForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = CloudSQLInstance
        fields = ['name', 'project', 'region', 'database_version', 'database_type', 'tier', 
                  'storage_size_gb', 'storage_type', 'status', 'ip_address', 'private_ip', 
                  'connection_name', 'high_availability', 'backup_enabled', 'labels', 'tags']


class CloudSQLInstanceFilterForm(NetBoxModelFilterSetForm):
    model = CloudSQLInstance
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    region = forms.CharField(required=False)
    database_type = forms.ChoiceField(choices=[('', '---------')] + list(CloudSQLInstance.DATABASE_CHOICES), required=False)
    status = forms.CharField(required=False)


class CloudSpannerInstanceForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = CloudSpannerInstance
        fields = ['name', 'project', 'config', 'display_name', 'node_count', 'processing_units', 'status', 'labels', 'tags']


class FirestoreDatabaseForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = FirestoreDatabase
        fields = ['name', 'project', 'location', 'database_type', 'concurrency_mode', 'status', 'tags']


class BigtableInstanceForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = BigtableInstance
        fields = ['name', 'project', 'display_name', 'instance_type', 'storage_type', 'status', 'labels', 'tags']


class CloudStorageBucketForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = CloudStorageBucket
        fields = ['name', 'project', 'location', 'storage_class', 'versioning_enabled', 
                  'uniform_bucket_level_access', 'public_access_prevention', 'lifecycle_rules', 'labels', 'tags']


class CloudStorageBucketFilterForm(NetBoxModelFilterSetForm):
    model = CloudStorageBucket
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    location = forms.CharField(required=False)
    storage_class = forms.ChoiceField(choices=[('', '---------')] + list(CloudStorageBucket.STORAGE_CLASS_CHOICES), required=False)


class PersistentDiskForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = PersistentDisk
        fields = ['name', 'project', 'zone', 'disk_type', 'size_gb', 'status', 
                  'source_image', 'source_snapshot', 'attached_instances', 'labels', 'tags']


class GKEClusterForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())
    network = DynamicModelChoiceField(queryset=VPCNetwork.objects.all(), required=False)
    subnet = DynamicModelChoiceField(queryset=Subnet.objects.all(), required=False)

    class Meta:
        model = GKECluster
        fields = ['name', 'project', 'location', 'network', 'subnet', 'master_version', 'status', 
                  'endpoint', 'cluster_ipv4_cidr', 'services_ipv4_cidr', 'enable_autopilot', 'private_cluster', 'labels', 'tags']


class GKEClusterFilterForm(NetBoxModelFilterSetForm):
    model = GKECluster
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    location = forms.CharField(required=False)
    status = forms.CharField(required=False)


class GKENodePoolForm(NetBoxModelForm):
    cluster = DynamicModelChoiceField(queryset=GKECluster.objects.all())

    class Meta:
        model = GKENodePool
        fields = ['name', 'cluster', 'machine_type', 'disk_size_gb', 'disk_type', 'node_count', 
                  'min_node_count', 'max_node_count', 'autoscaling_enabled', 'preemptible', 'spot', 
                  'status', 'version', 'labels', 'tags']


class ServiceAccountForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = ServiceAccount
        fields = ['email', 'project', 'display_name', 'description', 'disabled', 'unique_id', 'tags']


class ServiceAccountFilterForm(NetBoxModelFilterSetForm):
    model = ServiceAccount
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    disabled = forms.NullBooleanField(required=False)


class IAMRoleForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)

    class Meta:
        model = IAMRole
        fields = ['name', 'title', 'description', 'stage', 'included_permissions', 'is_custom', 'project', 'tags']


class IAMBindingForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())
    role = DynamicModelChoiceField(queryset=IAMRole.objects.all())

    class Meta:
        model = IAMBinding
        fields = ['project', 'role', 'member', 'condition', 'tags']


class CloudFunctionForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())
    service_account = DynamicModelChoiceField(queryset=ServiceAccount.objects.all(), required=False)

    class Meta:
        model = CloudFunction
        fields = ['name', 'project', 'region', 'runtime', 'entry_point', 'trigger_type', 'trigger_url',
                  'memory_mb', 'timeout_seconds', 'max_instances', 'min_instances', 'status', 
                  'service_account', 'environment_variables', 'labels', 'tags']


class CloudRunForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())
    service_account = DynamicModelChoiceField(queryset=ServiceAccount.objects.all(), required=False)

    class Meta:
        model = CloudRun
        fields = ['name', 'project', 'region', 'image', 'url', 'port', 'cpu', 'memory', 
                  'max_instances', 'min_instances', 'concurrency', 'timeout_seconds', 'status', 
                  'service_account', 'ingress', 'labels', 'tags']


class PubSubTopicForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = PubSubTopic
        fields = ['name', 'project', 'labels', 'message_retention_duration', 'schema_settings', 'tags']


class PubSubSubscriptionForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())
    topic = DynamicModelChoiceField(queryset=PubSubTopic.objects.all())
    dead_letter_topic = DynamicModelChoiceField(queryset=PubSubTopic.objects.all(), required=False)

    class Meta:
        model = PubSubSubscription
        fields = ['name', 'project', 'topic', 'ack_deadline_seconds', 'message_retention_duration', 
                  'push_endpoint', 'filter_expression', 'dead_letter_topic', 'labels', 'tags']


class SecretManagerSecretForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = SecretManagerSecret
        fields = ['name', 'project', 'replication_type', 'replication_locations', 'labels', 
                  'version_count', 'latest_version', 'tags']


class CloudDNSZoneForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = CloudDNSZone
        fields = ['name', 'project', 'dns_name', 'visibility', 'description', 'name_servers', 'labels', 'tags']


class CloudDNSRecordForm(NetBoxModelForm):
    zone = DynamicModelChoiceField(queryset=CloudDNSZone.objects.all())

    class Meta:
        model = CloudDNSRecord
        fields = ['zone', 'name', 'record_type', 'ttl', 'rrdatas', 'tags']


class MemorystoreInstanceForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())
    authorized_network = DynamicModelChoiceField(queryset=VPCNetwork.objects.all(), required=False)

    class Meta:
        model = MemorystoreInstance
        fields = ['name', 'project', 'region', 'tier', 'memory_size_gb', 'redis_version', 
                  'host', 'port', 'status', 'authorized_network', 'labels', 'tags']
