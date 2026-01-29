from django import forms

from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import DynamicModelChoiceField
from .models import (
    GCPOrganization, DiscoveryLog,
    GCPProject, ComputeInstance, InstanceTemplate, InstanceGroup,
    VPCNetwork, Subnet, FirewallRule, CloudRouter, CloudNAT, LoadBalancer,
    CloudSQLInstance, CloudSpannerInstance, FirestoreDatabase, BigtableInstance,
    CloudStorageBucket, PersistentDisk,
    GKECluster, GKENodePool,
    ServiceAccount, IAMRole, IAMBinding,
    CloudFunction, CloudRun, PubSubTopic, PubSubSubscription,
    SecretManagerSecret, CloudDNSZone, CloudDNSRecord, MemorystoreInstance
)


class GCPOrganizationForm(NetBoxModelForm):
    service_account_json = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'class': 'font-monospace'}),
        help_text='Paste the full JSON content of your GCP service account key file'
    )

    class Meta:
        model = GCPOrganization
        fields = [
            'name', 'organization_id', 'service_account_json', 'is_active', 'auto_discover',
            'discover_compute', 'discover_networking', 'discover_databases', 
            'discover_storage', 'discover_kubernetes', 'discover_serverless', 'discover_iam',
            'tags'
        ]


class GCPOrganizationFilterForm(NetBoxModelFilterSetForm):
    model = GCPOrganization
    name = forms.CharField(required=False)
    organization_id = forms.CharField(required=False)
    is_active = forms.NullBooleanField(required=False)
    discovery_status = forms.ChoiceField(
        required=False,
        choices=[('', '---------'), ('pending', 'Pending'), ('running', 'Running'), ('completed', 'Completed'), ('failed', 'Failed')]
    )


class GCPProjectForm(NetBoxModelForm):
    organization = DynamicModelChoiceField(queryset=GCPOrganization.objects.all(), required=False)

    class Meta:
        model = GCPProject
        fields = ['name', 'organization', 'project_id', 'project_number', 'status', 'labels', 'tags']


class GCPProjectFilterForm(NetBoxModelFilterSetForm):
    model = GCPProject
    organization = DynamicModelChoiceField(queryset=GCPOrganization.objects.all(), required=False)
    name = forms.CharField(required=False)
    project_id = forms.CharField(required=False)
    status = forms.CharField(required=False)
    discovered = forms.NullBooleanField(required=False)


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
        fields = ['name', 'project', 'auto_create_subnetworks', 'routing_mode', 'mtu', 'tags']


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
                  'purpose', 'tags']


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
                  'source_subnetwork_ip_ranges_to_nat', 'nat_ips', 'min_ports_per_vm', 'tags']


class LoadBalancerForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())
    network = DynamicModelChoiceField(queryset=VPCNetwork.objects.all(), required=False)

    class Meta:
        model = LoadBalancer
        fields = ['name', 'project', 'scheme', 'lb_type', 'region', 'network', 'ip_address', 'port', 'tags']


class CloudSQLInstanceForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = CloudSQLInstance
        fields = ['name', 'project', 'region', 'database_version', 'database_type', 'tier', 
                  'storage_size_gb', 'storage_type', 'status', 'ip_addresses', 'connection_name', 'tags']


class CloudSQLInstanceFilterForm(NetBoxModelFilterSetForm):
    model = CloudSQLInstance
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    region = forms.CharField(required=False)
    database_type = forms.CharField(required=False)
    status = forms.CharField(required=False)


class CloudSpannerInstanceForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = CloudSpannerInstance
        fields = ['name', 'project', 'config', 'display_name', 'node_count', 'processing_units', 'status', 'tags']


class FirestoreDatabaseForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = FirestoreDatabase
        fields = ['name', 'project', 'location', 'database_type', 'concurrency_mode', 'status', 'tags']


class BigtableInstanceForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = BigtableInstance
        fields = ['name', 'project', 'display_name', 'instance_type', 'storage_type', 'status', 'tags']


class CloudStorageBucketForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = CloudStorageBucket
        fields = ['name', 'project', 'location', 'storage_class', 'versioning_enabled', 
                  'lifecycle_rules', 'labels', 'tags']


class CloudStorageBucketFilterForm(NetBoxModelFilterSetForm):
    model = CloudStorageBucket
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    location = forms.CharField(required=False)
    storage_class = forms.CharField(required=False)


class PersistentDiskForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = PersistentDisk
        fields = ['name', 'project', 'zone', 'disk_type', 'size_gb', 'status', 'source_image', 'tags']


class GKEClusterForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())
    network = DynamicModelChoiceField(queryset=VPCNetwork.objects.all(), required=False)
    subnetwork = DynamicModelChoiceField(queryset=Subnet.objects.all(), required=False)

    class Meta:
        model = GKECluster
        fields = ['name', 'project', 'location', 'network', 'subnetwork', 'master_version', 'status', 
                  'endpoint', 'cluster_ipv4_cidr', 'services_ipv4_cidr', 'enable_autopilot', 'tags']


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
                  'min_node_count', 'max_node_count', 'status', 'version', 'tags']


class ServiceAccountForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = ServiceAccount
        fields = ['email', 'project', 'display_name', 'unique_id', 'disabled', 'tags']


class ServiceAccountFilterForm(NetBoxModelFilterSetForm):
    model = ServiceAccount
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    disabled = forms.NullBooleanField(required=False)


class IAMRoleForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)

    class Meta:
        model = IAMRole
        fields = ['name', 'title', 'description', 'stage', 'permissions', 'is_custom', 'project', 'tags']


class IAMBindingForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())
    role = DynamicModelChoiceField(queryset=IAMRole.objects.all())

    class Meta:
        model = IAMBinding
        fields = ['project', 'role', 'member', 'condition', 'tags']


class CloudFunctionForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = CloudFunction
        fields = ['name', 'project', 'region', 'runtime', 'entry_point', 'trigger_type', 
                  'trigger_url', 'memory_mb', 'timeout_seconds', 'status', 'tags']


class CloudRunForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = CloudRun
        fields = ['name', 'project', 'region', 'image', 'url', 'cpu', 'memory', 'status', 'tags']


class PubSubTopicForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = PubSubTopic
        fields = ['name', 'project', 'tags']


class PubSubSubscriptionForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())
    topic = DynamicModelChoiceField(queryset=PubSubTopic.objects.all())

    class Meta:
        model = PubSubSubscription
        fields = ['name', 'project', 'topic', 'push_endpoint', 'ack_deadline_seconds', 
                  'message_retention_duration', 'tags']


class SecretManagerSecretForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = SecretManagerSecret
        fields = ['name', 'project', 'replication_type', 'tags']


class CloudDNSZoneForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = CloudDNSZone
        fields = ['name', 'project', 'dns_name', 'visibility', 'tags']


class CloudDNSRecordForm(NetBoxModelForm):
    zone = DynamicModelChoiceField(queryset=CloudDNSZone.objects.all())

    class Meta:
        model = CloudDNSRecord
        fields = ['name', 'zone', 'record_type', 'ttl', 'rrdatas', 'tags']


class MemorystoreInstanceForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = MemorystoreInstance
        fields = ['name', 'project', 'region', 'tier', 'memory_size_gb', 'redis_version', 
                  'host', 'port', 'status', 'tags']


from .models import NCCHub, NCCSpoke, VPNGateway, ExternalVPNGateway, VPNTunnel, InterconnectAttachment


class NCCHubForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = NCCHub
        fields = ['name', 'project', 'description', 'labels', 'tags']


class NCCSpokeForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())
    hub = DynamicModelChoiceField(queryset=NCCHub.objects.all())
    linked_vpc_network = DynamicModelChoiceField(queryset=VPCNetwork.objects.all(), required=False)

    class Meta:
        model = NCCSpoke
        fields = ['name', 'project', 'hub', 'location', 'description', 'spoke_type', 
                  'linked_vpc_network', 'linked_vpn_tunnels', 'linked_interconnect_attachments', 'labels', 'tags']


class VPNGatewayForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())
    network = DynamicModelChoiceField(queryset=VPCNetwork.objects.all())

    class Meta:
        model = VPNGateway
        fields = ['name', 'project', 'network', 'region', 'gateway_type', 'ip_addresses', 'labels', 'tags']


class ExternalVPNGatewayForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = ExternalVPNGateway
        fields = ['name', 'project', 'description', 'redundancy_type', 'interfaces', 'labels', 'tags']


class VPNTunnelForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())
    vpn_gateway = DynamicModelChoiceField(queryset=VPNGateway.objects.all(), required=False)
    peer_external_gateway = DynamicModelChoiceField(queryset=ExternalVPNGateway.objects.all(), required=False)
    router = DynamicModelChoiceField(queryset=CloudRouter.objects.all(), required=False)

    class Meta:
        model = VPNTunnel
        fields = ['name', 'project', 'region', 'vpn_gateway', 'vpn_gateway_interface', 
                  'peer_external_gateway', 'peer_external_gateway_interface', 'peer_ip',
                  'ike_version', 'local_traffic_selector', 'remote_traffic_selector', 
                  'router', 'status', 'labels', 'tags']


class InterconnectAttachmentForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())
    router = DynamicModelChoiceField(queryset=CloudRouter.objects.all())

    class Meta:
        model = InterconnectAttachment
        fields = ['name', 'project', 'region', 'router', 'attachment_type', 
                  'edge_availability_domain', 'bandwidth', 'vlan_tag', 'pairing_key',
                  'partner_asn', 'cloud_router_ip_address', 'customer_router_ip_address',
                  'state', 'labels', 'tags']
