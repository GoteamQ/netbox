from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm, NetBoxModelBulkEditForm, NetBoxModelImportForm
from utilities.forms.fields import DynamicModelChoiceField
from .models import (
    GCPOrganization,
    DiscoveryLog,
    GCPProject,
    ComputeInstance,
    InstanceTemplate,
    InstanceGroup,
    VPCNetwork,
    Subnet,
    FirewallRule,
    CloudRouter,
    CloudNAT,
    LoadBalancer,
    CloudSQLInstance,
    CloudSpannerInstance,
    FirestoreDatabase,
    BigtableInstance,
    CloudStorageBucket,
    PersistentDisk,
    GKECluster,
    GKENodePool,
    ServiceAccount,
    IAMRole,
    IAMBinding,
    CloudFunction,
    CloudRun,
    PubSubTopic,
    PubSubSubscription,
    SecretManagerSecret,
    CloudDNSZone,
    CloudDNSRecord,
    MemorystoreInstance,
    ServiceAttachment,
    ServiceConnectEndpoint,
    NCCHub,
    NCCSpoke,
    VPNGateway,
    ExternalVPNGateway,
    VPNTunnel,
    InterconnectAttachment,
)


class GCPOrganizationForm(NetBoxModelForm):
    service_account_json = forms.CharField(
        widget=forms.PasswordInput(render_value=False),
        required=False,
        help_text='Paste the full JSON content of your GCP service account key file. Leave blank to keep unchanged.',
    )

    class Meta:
        model = GCPOrganization
        fields = [
            'name',
            'organization_id',
            'service_account_json',
            'is_active',
            'auto_discover',
            'discover_compute',
            'discover_networking',
            'discover_databases',
            'discover_storage',
            'discover_kubernetes',
            'discover_serverless',
            'discover_iam',
            'tags',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['service_account_json'].required = True

    def clean_service_account_json(self):
        data = self.cleaned_data['service_account_json']
        if not data and self.instance.pk:
            return self.instance.service_account_json
        return data


class GCPOrganizationFilterForm(NetBoxModelFilterSetForm):
    model = GCPOrganization
    name = forms.CharField(required=False)
    organization_id = forms.CharField(required=False)
    is_active = forms.NullBooleanField(required=False)
    discovery_status = forms.ChoiceField(
        required=False,
        choices=[
            ('', '---------'),
            ('pending', 'Pending'),
            ('running', 'Running'),
            ('canceling', 'Canceling'),
            ('canceled', 'Canceled'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
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
        fields = [
            'name',
            'project',
            'zone',
            'machine_type',
            'status',
            'internal_ip',
            'external_ip',
            'network',
            'subnet',
            'disk_size_gb',
            'image',
            'labels',
            'tags',
        ]


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
        fields = [
            'name',
            'project',
            'network',
            'region',
            'ip_cidr_range',
            'private_ip_google_access',
            'purpose',
            'tags',
        ]


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
        fields = [
            'name',
            'project',
            'network',
            'direction',
            'priority',
            'action',
            'source_ranges',
            'destination_ranges',
            'source_tags',
            'target_tags',
            'allowed',
            'denied',
            'disabled',
            'tags',
        ]


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
        fields = [
            'name',
            'project',
            'router',
            'region',
            'nat_ip_allocate_option',
            'source_subnetwork_ip_ranges_to_nat',
            'nat_ips',
            'min_ports_per_vm',
            'tags',
        ]


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
        fields = [
            'name',
            'project',
            'region',
            'database_version',
            'database_type',
            'tier',
            'storage_size_gb',
            'storage_type',
            'status',
            'ip_addresses',
            'connection_name',
            'tags',
        ]


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
        fields = [
            'name',
            'project',
            'location',
            'storage_class',
            'versioning_enabled',
            'lifecycle_rules',
            'labels',
            'tags',
        ]


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
        fields = [
            'name',
            'project',
            'location',
            'network',
            'subnetwork',
            'master_version',
            'status',
            'endpoint',
            'cluster_ipv4_cidr',
            'services_ipv4_cidr',
            'enable_autopilot',
            'tags',
        ]


class GKEClusterFilterForm(NetBoxModelFilterSetForm):
    model = GKECluster
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    location = forms.CharField(required=False)
    status = forms.CharField(required=False)


class GKENodePoolForm(NetBoxModelForm):
    cluster = DynamicModelChoiceField(queryset=GKECluster.objects.all())

    class Meta:
        model = GKENodePool
        fields = [
            'name',
            'cluster',
            'machine_type',
            'disk_size_gb',
            'disk_type',
            'node_count',
            'min_node_count',
            'max_node_count',
            'status',
            'version',
            'tags',
        ]


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
        fields = [
            'name',
            'project',
            'region',
            'runtime',
            'entry_point',
            'trigger_type',
            'trigger_url',
            'memory_mb',
            'timeout_seconds',
            'status',
            'tags',
        ]


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
        fields = [
            'name',
            'project',
            'topic',
            'push_endpoint',
            'ack_deadline_seconds',
            'message_retention_duration',
            'tags',
        ]


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
        fields = [
            'name',
            'project',
            'region',
            'tier',
            'memory_size_gb',
            'redis_version',
            'host',
            'port',
            'status',
            'tags',
        ]


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
        fields = [
            'name',
            'project',
            'hub',
            'location',
            'description',
            'spoke_type',
            'linked_vpc_network',
            'linked_vpn_tunnels',
            'linked_interconnect_attachments',
            'labels',
            'tags',
        ]


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
        fields = [
            'name',
            'project',
            'region',
            'vpn_gateway',
            'vpn_gateway_interface',
            'peer_external_gateway',
            'peer_external_gateway_interface',
            'peer_ip',
            'ike_version',
            'local_traffic_selector',
            'remote_traffic_selector',
            'router',
            'status',
            'labels',
            'tags',
        ]


class InterconnectAttachmentForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())
    router = DynamicModelChoiceField(queryset=CloudRouter.objects.all())

    class Meta:
        model = InterconnectAttachment
        fields = [
            'name',
            'project',
            'region',
            'router',
            'attachment_type',
            'edge_availability_domain',
            'bandwidth',
            'vlan_tag',
            'pairing_key',
            'partner_asn',
            'cloud_router_ip_address',
            'customer_router_ip_address',
            'state',
            'labels',
            'tags',
        ]


class ServiceAttachmentForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())

    class Meta:
        model = ServiceAttachment
        fields = ('name', 'project', 'region', 'connection_preference', 'target_service', 'nat_subnets', 'tags')


class ServiceAttachmentFilterForm(NetBoxModelFilterSetForm):
    model = ServiceAttachment
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)
    region = forms.CharField(required=False)


class ServiceConnectEndpointForm(NetBoxModelForm):
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all())
    network = DynamicModelChoiceField(queryset=VPCNetwork.objects.all())

    class Meta:
        model = ServiceConnectEndpoint
        fields = ('name', 'project', 'region', 'network', 'ip_address', 'target_service_attachment', 'tags')


class ServiceConnectEndpointFilterForm(NetBoxModelFilterSetForm):
    model = ServiceConnectEndpoint
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    network = DynamicModelChoiceField(queryset=VPCNetwork.objects.all(), required=False)
    name = forms.CharField(required=False)
    region = forms.CharField(required=False)


class GCPOrganizationBulkEditForm(NetBoxModelBulkEditForm):
    is_active = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=[
            (None, '---------'),
            (True, 'Yes'),
            (False, 'No'),
        ]),
        label='Active'
    )
    auto_discover = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=[
            (None, '---------'),
            (True, 'Yes'),
            (False, 'No'),
        ]),
        label='Auto Discover'
    )

    model = GCPOrganization
    fieldsets = (
        (None, ('is_active', 'auto_discover')),
    )


class GCPOrganizationImportForm(NetBoxModelImportForm):
    class Meta:
        model = GCPOrganization
        fields = (
            'name', 'organization_id', 'service_account_json', 'is_active', 'auto_discover',
        )


class DiscoveryLogForm(NetBoxModelForm):
    organization = DynamicModelChoiceField(
        queryset=GCPOrganization.objects.all()
    )

    class Meta:
        model = DiscoveryLog
        fields = (
            'organization', 'status', 'error_message', 'log_output',
        )


class DiscoveryLogFilterForm(NetBoxModelFilterSetForm):
    model = DiscoveryLog
    organization = DynamicModelChoiceField(
        queryset=GCPOrganization.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        choices=[('', '---------')] + list(DiscoveryLog.status.field.choices),
        required=False
    )


# ============================================================
# BulkEdit Forms
# ============================================================

class DiscoveryLogBulkEditForm(NetBoxModelBulkEditForm):
    model = DiscoveryLog
    fieldsets = ()


class GCPProjectBulkEditForm(NetBoxModelBulkEditForm):
    status = forms.CharField(max_length=50, required=False)

    model = GCPProject
    fieldsets = (
        (None, ('status',)),
    )


class ComputeInstanceBulkEditForm(NetBoxModelBulkEditForm):
    status = forms.CharField(max_length=50, required=False)

    model = ComputeInstance
    fieldsets = (
        (None, ('status',)),
    )


class InstanceTemplateBulkEditForm(NetBoxModelBulkEditForm):
    model = InstanceTemplate
    fieldsets = ()


class InstanceGroupBulkEditForm(NetBoxModelBulkEditForm):
    target_size = forms.IntegerField(required=False)

    model = InstanceGroup
    fieldsets = (
        (None, ('target_size',)),
    )


class VPCNetworkBulkEditForm(NetBoxModelBulkEditForm):
    routing_mode = forms.CharField(max_length=50, required=False)

    model = VPCNetwork
    fieldsets = (
        (None, ('routing_mode',)),
    )


class SubnetBulkEditForm(NetBoxModelBulkEditForm):
    model = Subnet
    fieldsets = ()


class FirewallRuleBulkEditForm(NetBoxModelBulkEditForm):
    disabled = forms.NullBooleanField(required=False)

    model = FirewallRule
    fieldsets = (
        (None, ('disabled',)),
    )


class CloudRouterBulkEditForm(NetBoxModelBulkEditForm):
    model = CloudRouter
    fieldsets = ()


class CloudNATBulkEditForm(NetBoxModelBulkEditForm):
    model = CloudNAT
    fieldsets = ()


class LoadBalancerBulkEditForm(NetBoxModelBulkEditForm):
    model = LoadBalancer
    fieldsets = ()


class CloudSQLInstanceBulkEditForm(NetBoxModelBulkEditForm):
    status = forms.CharField(max_length=50, required=False)

    model = CloudSQLInstance
    fieldsets = (
        (None, ('status',)),
    )


class CloudSpannerInstanceBulkEditForm(NetBoxModelBulkEditForm):
    model = CloudSpannerInstance
    fieldsets = ()


class FirestoreDatabaseBulkEditForm(NetBoxModelBulkEditForm):
    model = FirestoreDatabase
    fieldsets = ()


class BigtableInstanceBulkEditForm(NetBoxModelBulkEditForm):
    model = BigtableInstance
    fieldsets = ()


class CloudStorageBucketBulkEditForm(NetBoxModelBulkEditForm):
    storage_class = forms.CharField(max_length=50, required=False)

    model = CloudStorageBucket
    fieldsets = (
        (None, ('storage_class',)),
    )


class PersistentDiskBulkEditForm(NetBoxModelBulkEditForm):
    model = PersistentDisk
    fieldsets = ()


class GKEClusterBulkEditForm(NetBoxModelBulkEditForm):
    status = forms.CharField(max_length=50, required=False)

    model = GKECluster
    fieldsets = (
        (None, ('status',)),
    )


class GKENodePoolBulkEditForm(NetBoxModelBulkEditForm):
    model = GKENodePool
    fieldsets = ()


class ServiceAccountBulkEditForm(NetBoxModelBulkEditForm):
    disabled = forms.NullBooleanField(required=False)

    model = ServiceAccount
    fieldsets = (
        (None, ('disabled',)),
    )


class IAMRoleBulkEditForm(NetBoxModelBulkEditForm):
    model = IAMRole
    fieldsets = ()


class IAMBindingBulkEditForm(NetBoxModelBulkEditForm):
    model = IAMBinding
    fieldsets = ()


class CloudFunctionBulkEditForm(NetBoxModelBulkEditForm):
    status = forms.CharField(max_length=50, required=False)

    model = CloudFunction
    fieldsets = (
        (None, ('status',)),
    )


class CloudRunBulkEditForm(NetBoxModelBulkEditForm):
    status = forms.CharField(max_length=50, required=False)

    model = CloudRun
    fieldsets = (
        (None, ('status',)),
    )


class PubSubTopicBulkEditForm(NetBoxModelBulkEditForm):
    model = PubSubTopic
    fieldsets = ()


class PubSubSubscriptionBulkEditForm(NetBoxModelBulkEditForm):
    model = PubSubSubscription
    fieldsets = ()


class SecretManagerSecretBulkEditForm(NetBoxModelBulkEditForm):
    model = SecretManagerSecret
    fieldsets = ()


class CloudDNSZoneBulkEditForm(NetBoxModelBulkEditForm):
    model = CloudDNSZone
    fieldsets = ()


class CloudDNSRecordBulkEditForm(NetBoxModelBulkEditForm):
    model = CloudDNSRecord
    fieldsets = ()


class MemorystoreInstanceBulkEditForm(NetBoxModelBulkEditForm):
    model = MemorystoreInstance
    fieldsets = ()


class NCCHubBulkEditForm(NetBoxModelBulkEditForm):
    model = NCCHub
    fieldsets = ()


class NCCSpokeBulkEditForm(NetBoxModelBulkEditForm):
    model = NCCSpoke
    fieldsets = ()


class VPNGatewayBulkEditForm(NetBoxModelBulkEditForm):
    model = VPNGateway
    fieldsets = ()


class ExternalVPNGatewayBulkEditForm(NetBoxModelBulkEditForm):
    model = ExternalVPNGateway
    fieldsets = ()


class VPNTunnelBulkEditForm(NetBoxModelBulkEditForm):
    model = VPNTunnel
    fieldsets = ()


class InterconnectAttachmentBulkEditForm(NetBoxModelBulkEditForm):
    model = InterconnectAttachment
    fieldsets = ()


class ServiceAttachmentBulkEditForm(NetBoxModelBulkEditForm):
    model = ServiceAttachment
    fieldsets = ()


class ServiceConnectEndpointBulkEditForm(NetBoxModelBulkEditForm):
    model = ServiceConnectEndpoint
    fieldsets = ()


# ============================================================
# Import Forms
# ============================================================

class DiscoveryLogImportForm(NetBoxModelImportForm):
    class Meta:
        model = DiscoveryLog
        fields = ('organization', 'status', 'error_message')


class GCPProjectImportForm(NetBoxModelImportForm):
    class Meta:
        model = GCPProject
        fields = ('name', 'project_id', 'project_number', 'status')


class ComputeInstanceImportForm(NetBoxModelImportForm):
    class Meta:
        model = ComputeInstance
        fields = ('name', 'project', 'zone', 'machine_type', 'status', 'internal_ip', 'external_ip')


class InstanceTemplateImportForm(NetBoxModelImportForm):
    class Meta:
        model = InstanceTemplate
        fields = ('name', 'project', 'machine_type', 'disk_size_gb')


class InstanceGroupImportForm(NetBoxModelImportForm):
    class Meta:
        model = InstanceGroup
        fields = ('name', 'project', 'zone', 'region', 'target_size', 'is_managed')


class VPCNetworkImportForm(NetBoxModelImportForm):
    class Meta:
        model = VPCNetwork
        fields = ('name', 'project', 'auto_create_subnetworks', 'routing_mode', 'mtu')


class SubnetImportForm(NetBoxModelImportForm):
    class Meta:
        model = Subnet
        fields = ('name', 'project', 'network', 'region', 'ip_cidr_range')


class FirewallRuleImportForm(NetBoxModelImportForm):
    class Meta:
        model = FirewallRule
        fields = ('name', 'project', 'network', 'direction', 'priority', 'action', 'disabled')


class CloudRouterImportForm(NetBoxModelImportForm):
    class Meta:
        model = CloudRouter
        fields = ('name', 'project', 'network', 'region', 'asn')


class CloudNATImportForm(NetBoxModelImportForm):
    class Meta:
        model = CloudNAT
        fields = ('name', 'project', 'router', 'region')


class LoadBalancerImportForm(NetBoxModelImportForm):
    class Meta:
        model = LoadBalancer
        fields = ('name', 'project', 'scheme', 'lb_type', 'region')


class CloudSQLInstanceImportForm(NetBoxModelImportForm):
    class Meta:
        model = CloudSQLInstance
        fields = ('name', 'project', 'region', 'database_type', 'database_version', 'tier', 'status')


class CloudSpannerInstanceImportForm(NetBoxModelImportForm):
    class Meta:
        model = CloudSpannerInstance
        fields = ('name', 'project', 'config', 'display_name', 'node_count', 'status')


class FirestoreDatabaseImportForm(NetBoxModelImportForm):
    class Meta:
        model = FirestoreDatabase
        fields = ('name', 'project', 'location', 'database_type', 'status')


class BigtableInstanceImportForm(NetBoxModelImportForm):
    class Meta:
        model = BigtableInstance
        fields = ('name', 'project', 'display_name', 'instance_type', 'storage_type', 'status')


class CloudStorageBucketImportForm(NetBoxModelImportForm):
    class Meta:
        model = CloudStorageBucket
        fields = ('name', 'project', 'location', 'storage_class', 'versioning_enabled')


class PersistentDiskImportForm(NetBoxModelImportForm):
    class Meta:
        model = PersistentDisk
        fields = ('name', 'project', 'zone', 'disk_type', 'size_gb', 'status')


class GKEClusterImportForm(NetBoxModelImportForm):
    class Meta:
        model = GKECluster
        fields = ('name', 'project', 'location', 'master_version', 'status')


class GKENodePoolImportForm(NetBoxModelImportForm):
    class Meta:
        model = GKENodePool
        fields = ('name', 'cluster', 'machine_type', 'disk_size_gb', 'node_count')


class ServiceAccountImportForm(NetBoxModelImportForm):
    class Meta:
        model = ServiceAccount
        fields = ('email', 'project', 'display_name', 'disabled')


class IAMRoleImportForm(NetBoxModelImportForm):
    class Meta:
        model = IAMRole
        fields = ('name', 'title', 'description', 'stage', 'is_custom')


class IAMBindingImportForm(NetBoxModelImportForm):
    class Meta:
        model = IAMBinding
        fields = ('project', 'role', 'member')


class CloudFunctionImportForm(NetBoxModelImportForm):
    class Meta:
        model = CloudFunction
        fields = ('name', 'project', 'region', 'runtime', 'entry_point', 'trigger_type', 'status')


class CloudRunImportForm(NetBoxModelImportForm):
    class Meta:
        model = CloudRun
        fields = ('name', 'project', 'region', 'image', 'cpu', 'memory', 'status')


class PubSubTopicImportForm(NetBoxModelImportForm):
    class Meta:
        model = PubSubTopic
        fields = ('name', 'project')


class PubSubSubscriptionImportForm(NetBoxModelImportForm):
    class Meta:
        model = PubSubSubscription
        fields = ('name', 'project', 'topic', 'ack_deadline_seconds')


class SecretManagerSecretImportForm(NetBoxModelImportForm):
    class Meta:
        model = SecretManagerSecret
        fields = ('name', 'project', 'replication_type')


class CloudDNSZoneImportForm(NetBoxModelImportForm):
    class Meta:
        model = CloudDNSZone
        fields = ('name', 'project', 'dns_name', 'description', 'visibility')


class CloudDNSRecordImportForm(NetBoxModelImportForm):
    class Meta:
        model = CloudDNSRecord
        fields = ('name', 'zone', 'record_type', 'ttl')


class MemorystoreInstanceImportForm(NetBoxModelImportForm):
    class Meta:
        model = MemorystoreInstance
        fields = ('name', 'project', 'region', 'tier', 'memory_size_gb', 'redis_version', 'status')


class NCCHubImportForm(NetBoxModelImportForm):
    class Meta:
        model = NCCHub
        fields = ('name', 'project', 'description')


class NCCSpokeImportForm(NetBoxModelImportForm):
    class Meta:
        model = NCCSpoke
        fields = ('name', 'project', 'hub', 'location', 'description', 'spoke_type')


class VPNGatewayImportForm(NetBoxModelImportForm):
    class Meta:
        model = VPNGateway
        fields = ('name', 'project', 'network', 'region', 'gateway_type')


class ExternalVPNGatewayImportForm(NetBoxModelImportForm):
    class Meta:
        model = ExternalVPNGateway
        fields = ('name', 'project', 'description', 'redundancy_type')


class VPNTunnelImportForm(NetBoxModelImportForm):
    class Meta:
        model = VPNTunnel
        fields = ('name', 'project', 'region', 'vpn_gateway', 'peer_ip', 'ike_version', 'status')


class InterconnectAttachmentImportForm(NetBoxModelImportForm):
    class Meta:
        model = InterconnectAttachment
        fields = ('name', 'project', 'region', 'router', 'attachment_type', 'bandwidth', 'state')


class ServiceAttachmentImportForm(NetBoxModelImportForm):
    class Meta:
        model = ServiceAttachment
        fields = ('name', 'project', 'region', 'connection_preference', 'target_service')


class ServiceConnectEndpointImportForm(NetBoxModelImportForm):
    class Meta:
        model = ServiceConnectEndpoint
        fields = ('name', 'project', 'region', 'ip_address', 'target_service_attachment')


# ============================================================
# Filter Forms (missing ones)
# ============================================================

class InstanceTemplateFilterForm(NetBoxModelFilterSetForm):
    model = InstanceTemplate
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)


class InstanceGroupFilterForm(NetBoxModelFilterSetForm):
    model = InstanceGroup
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)


class FirewallRuleFilterForm(NetBoxModelFilterSetForm):
    model = FirewallRule
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)
    direction = forms.CharField(required=False)


class CloudRouterFilterForm(NetBoxModelFilterSetForm):
    model = CloudRouter
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)
    region = forms.CharField(required=False)


class CloudNATFilterForm(NetBoxModelFilterSetForm):
    model = CloudNAT
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)


class LoadBalancerFilterForm(NetBoxModelFilterSetForm):
    model = LoadBalancer
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)
    scheme = forms.CharField(required=False)


class CloudSpannerInstanceFilterForm(NetBoxModelFilterSetForm):
    model = CloudSpannerInstance
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)
    status = forms.CharField(required=False)


class FirestoreDatabaseFilterForm(NetBoxModelFilterSetForm):
    model = FirestoreDatabase
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)


class BigtableInstanceFilterForm(NetBoxModelFilterSetForm):
    model = BigtableInstance
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)


class PersistentDiskFilterForm(NetBoxModelFilterSetForm):
    model = PersistentDisk
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)
    zone = forms.CharField(required=False)


class GKENodePoolFilterForm(NetBoxModelFilterSetForm):
    model = GKENodePool
    cluster = DynamicModelChoiceField(queryset=GKECluster.objects.all(), required=False)
    name = forms.CharField(required=False)


class IAMRoleFilterForm(NetBoxModelFilterSetForm):
    model = IAMRole
    name = forms.CharField(required=False)
    is_custom = forms.NullBooleanField(required=False)


class IAMBindingFilterForm(NetBoxModelFilterSetForm):
    model = IAMBinding
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    member = forms.CharField(required=False)


class CloudFunctionFilterForm(NetBoxModelFilterSetForm):
    model = CloudFunction
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)
    region = forms.CharField(required=False)


class CloudRunFilterForm(NetBoxModelFilterSetForm):
    model = CloudRun
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)
    region = forms.CharField(required=False)


class PubSubTopicFilterForm(NetBoxModelFilterSetForm):
    model = PubSubTopic
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)


class PubSubSubscriptionFilterForm(NetBoxModelFilterSetForm):
    model = PubSubSubscription
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)


class SecretManagerSecretFilterForm(NetBoxModelFilterSetForm):
    model = SecretManagerSecret
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)


class CloudDNSZoneFilterForm(NetBoxModelFilterSetForm):
    model = CloudDNSZone
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)


class CloudDNSRecordFilterForm(NetBoxModelFilterSetForm):
    model = CloudDNSRecord
    zone = DynamicModelChoiceField(queryset=CloudDNSZone.objects.all(), required=False)
    name = forms.CharField(required=False)
    record_type = forms.CharField(required=False)


class MemorystoreInstanceFilterForm(NetBoxModelFilterSetForm):
    model = MemorystoreInstance
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)
    region = forms.CharField(required=False)


class NCCHubFilterForm(NetBoxModelFilterSetForm):
    model = NCCHub
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)


class NCCSpokeFilterForm(NetBoxModelFilterSetForm):
    model = NCCSpoke
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)


class VPNGatewayFilterForm(NetBoxModelFilterSetForm):
    model = VPNGateway
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)
    region = forms.CharField(required=False)


class ExternalVPNGatewayFilterForm(NetBoxModelFilterSetForm):
    model = ExternalVPNGateway
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)


class VPNTunnelFilterForm(NetBoxModelFilterSetForm):
    model = VPNTunnel
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)
    status = forms.CharField(required=False)


class InterconnectAttachmentFilterForm(NetBoxModelFilterSetForm):
    model = InterconnectAttachment
    project = DynamicModelChoiceField(queryset=GCPProject.objects.all(), required=False)
    name = forms.CharField(required=False)
    region = forms.CharField(required=False)
