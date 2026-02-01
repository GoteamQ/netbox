import django_tables2 as tables

from netbox.tables import NetBoxTable, columns
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
    InterconnectAttachment,
    VPNTunnel,
    NCCHub,
    NCCSpoke,
    ServiceAttachment,
    ServiceConnectEndpoint,
    VPNGateway,
    ExternalVPNGateway,
)


class GCPOrganizationTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization_id = tables.Column()
    is_active = tables.BooleanColumn()
    discovery_status = tables.Column()
    last_discovery = tables.DateTimeColumn()

    class Meta(NetBoxTable.Meta):
        model = GCPOrganization
        fields = ('pk', 'name', 'organization_id', 'is_active', 'discovery_status', 'last_discovery', 'auto_discover')
        default_columns = ('name', 'organization_id', 'is_active', 'discovery_status', 'last_discovery')


class DiscoveryLogTable(NetBoxTable):
    organization = tables.Column(linkify=True)
    started_at = tables.DateTimeColumn()
    completed_at = tables.DateTimeColumn()
    status = tables.Column()
    total_resources = tables.Column()
    actions = columns.ActionsColumn(actions=('delete', 'changelog'), split_actions=False)

    class Meta(NetBoxTable.Meta):
        model = DiscoveryLog
        fields = (
            'pk',
            'organization',
            'started_at',
            'completed_at',
            'status',
            'projects_discovered',
            'instances_discovered',
            'networks_discovered',
            'total_resources',
        )
        default_columns = ('organization', 'started_at', 'status', 'total_resources')


class GCPProjectTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(linkify=True)
    project_id = tables.Column()
    status = tables.Column()
    discovered = tables.BooleanColumn()

    class Meta(NetBoxTable.Meta):
        model = GCPProject
        fields = ('pk', 'name', 'organization', 'project_id', 'project_number', 'status', 'discovered', 'last_synced')
        default_columns = ('name', 'organization', 'project_id', 'status', 'discovered')


class ComputeInstanceTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    zone = tables.Column()
    machine_type = tables.Column()
    status = tables.Column()
    internal_ip = tables.Column()
    external_ip = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = ComputeInstance
        fields = (
            'pk',
            'name',
            'organization',
            'project',
            'zone',
            'machine_type',
            'status',
            'internal_ip',
            'external_ip',
            'network',
        )
        default_columns = ('name', 'organization', 'project', 'zone', 'machine_type', 'status', 'internal_ip')


class InstanceTemplateTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    machine_type = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = InstanceTemplate
        fields = ('pk', 'name', 'organization', 'project', 'machine_type', 'disk_size_gb', 'image')
        default_columns = ('name', 'organization', 'project', 'machine_type', 'disk_size_gb')


class InstanceGroupTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    zone = tables.Column()
    region = tables.Column()
    target_size = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = InstanceGroup
        fields = ('pk', 'name', 'organization', 'project', 'zone', 'region', 'template', 'target_size', 'is_managed')
        default_columns = ('name', 'organization', 'project', 'zone', 'target_size', 'is_managed')


class VPCNetworkTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    routing_mode = tables.Column()
    mtu = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = VPCNetwork
        fields = ('pk', 'name', 'organization', 'project', 'auto_create_subnetworks', 'routing_mode', 'mtu')
        default_columns = ('name', 'organization', 'project', 'routing_mode', 'mtu')


class SubnetTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    network = tables.Column(linkify=True)
    region = tables.Column()
    ip_cidr_range = tables.Column()
    utilization = tables.Column(empty_values=(), verbose_name='Utilization')

    def render_utilization(self, value, record):
        return record.get_utilization()

    class Meta(NetBoxTable.Meta):
        model = Subnet
        fields = (
            'pk',
            'name',
            'organization',
            'project',
            'network',
            'region',
            'ip_cidr_range',
            'purpose',
            'utilization',
        )
        default_columns = ('name', 'organization', 'project', 'network', 'region', 'ip_cidr_range', 'utilization')


class FirewallRuleTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    network = tables.Column(linkify=True)
    direction = tables.Column()
    priority = tables.Column()
    action = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = FirewallRule
        fields = ('pk', 'name', 'organization', 'project', 'network', 'direction', 'priority', 'action', 'disabled')
        default_columns = ('name', 'organization', 'project', 'network', 'direction', 'priority', 'action')


class CloudRouterTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    network = tables.Column(linkify=True)
    region = tables.Column()
    asn = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = CloudRouter
        fields = ('pk', 'name', 'organization', 'project', 'network', 'region', 'asn', 'advertise_mode')
        default_columns = ('name', 'organization', 'project', 'network', 'region', 'asn')


class CloudNATTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    router = tables.Column(linkify=True)
    region = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = CloudNAT
        fields = ('pk', 'name', 'organization', 'project', 'router', 'region', 'nat_ip_allocate_option')
        default_columns = ('name', 'organization', 'project', 'router', 'region')


class LoadBalancerTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    scheme = tables.Column()
    lb_type = tables.Column()
    ip_address = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = LoadBalancer
        fields = ('pk', 'name', 'organization', 'project', 'scheme', 'lb_type', 'region', 'ip_address', 'port')
        default_columns = ('name', 'organization', 'project', 'scheme', 'lb_type', 'ip_address')


class CloudSQLInstanceTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    region = tables.Column()
    database_type = tables.Column()
    database_version = tables.Column()
    tier = tables.Column()
    status = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = CloudSQLInstance
        fields = (
            'pk',
            'name',
            'organization',
            'project',
            'region',
            'database_type',
            'database_version',
            'tier',
            'status',
            'storage_size_gb',
        )
        default_columns = ('name', 'organization', 'project', 'region', 'database_type', 'tier', 'status')


class CloudSpannerInstanceTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    config = tables.Column()
    node_count = tables.Column()
    status = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = CloudSpannerInstance
        fields = (
            'pk',
            'name',
            'organization',
            'project',
            'config',
            'display_name',
            'node_count',
            'processing_units',
            'status',
        )
        default_columns = ('name', 'organization', 'project', 'config', 'node_count', 'status')


class FirestoreDatabaseTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    location = tables.Column()
    database_type = tables.Column()
    status = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = FirestoreDatabase
        fields = ('pk', 'name', 'organization', 'project', 'location', 'database_type', 'concurrency_mode', 'status')
        default_columns = ('name', 'organization', 'project', 'location', 'database_type', 'status')


class BigtableInstanceTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    display_name = tables.Column()
    instance_type = tables.Column()
    status = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = BigtableInstance
        fields = ('pk', 'name', 'organization', 'project', 'display_name', 'instance_type', 'storage_type', 'status')
        default_columns = ('name', 'organization', 'project', 'display_name', 'instance_type', 'status')


class CloudStorageBucketTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    location = tables.Column()
    storage_class = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = CloudStorageBucket
        fields = ('pk', 'name', 'organization', 'project', 'location', 'storage_class', 'versioning_enabled')
        default_columns = ('name', 'organization', 'project', 'location', 'storage_class')


class PersistentDiskTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    zone = tables.Column()
    disk_type = tables.Column()
    size_gb = tables.Column()
    status = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = PersistentDisk
        fields = ('pk', 'name', 'organization', 'project', 'zone', 'disk_type', 'size_gb', 'status')
        default_columns = ('name', 'organization', 'project', 'zone', 'disk_type', 'size_gb', 'status')


class GKEClusterTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    location = tables.Column()
    master_version = tables.Column()
    status = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = GKECluster
        fields = (
            'pk',
            'name',
            'organization',
            'project',
            'location',
            'network',
            'master_version',
            'status',
            'enable_autopilot',
        )
        default_columns = ('name', 'organization', 'project', 'location', 'master_version', 'status')


class GKENodePoolTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='cluster.project.organization', linkify=True)
    cluster = tables.Column(linkify=True)
    machine_type = tables.Column()
    node_count = tables.Column()
    status = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = GKENodePool
        fields = (
            'pk',
            'name',
            'organization',
            'cluster',
            'machine_type',
            'node_count',
            'min_node_count',
            'max_node_count',
            'status',
        )
        default_columns = ('name', 'organization', 'cluster', 'machine_type', 'node_count', 'status')


class ServiceAccountTable(NetBoxTable):
    email = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    display_name = tables.Column()
    disabled = tables.BooleanColumn()

    class Meta(NetBoxTable.Meta):
        model = ServiceAccount
        fields = ('pk', 'email', 'organization', 'project', 'display_name', 'disabled')
        default_columns = ('email', 'organization', 'project', 'display_name', 'disabled')


class IAMRoleTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    title = tables.Column()
    stage = tables.Column()
    is_custom = tables.BooleanColumn()

    class Meta(NetBoxTable.Meta):
        model = IAMRole
        fields = ('pk', 'name', 'organization', 'title', 'stage', 'is_custom', 'project')
        default_columns = ('name', 'organization', 'title', 'stage', 'is_custom')


class IAMBindingTable(NetBoxTable):
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    role = tables.Column(linkify=True)
    member = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = IAMBinding
        fields = ('pk', 'organization', 'project', 'role', 'member')
        default_columns = ('organization', 'project', 'role', 'member')


class CloudFunctionTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    region = tables.Column()
    runtime = tables.Column()
    status = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = CloudFunction
        fields = ('pk', 'name', 'organization', 'project', 'region', 'runtime', 'trigger_type', 'memory_mb', 'status')
        default_columns = ('name', 'organization', 'project', 'region', 'runtime', 'status')


class CloudRunTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    region = tables.Column()
    status = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = CloudRun
        fields = ('pk', 'name', 'organization', 'project', 'region', 'cpu', 'memory', 'status')
        default_columns = ('name', 'organization', 'project', 'region', 'status')


class PubSubTopicTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = PubSubTopic
        fields = ('pk', 'name', 'organization', 'project')
        default_columns = ('name', 'organization', 'project')


class PubSubSubscriptionTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    topic = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = PubSubSubscription
        fields = ('pk', 'name', 'organization', 'project', 'topic', 'ack_deadline_seconds')
        default_columns = ('name', 'organization', 'project', 'topic')


class SecretManagerSecretTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    replication_type = tables.Column()
    version_count = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = SecretManagerSecret
        fields = ('pk', 'name', 'organization', 'project', 'replication_type', 'version_count', 'latest_version')
        default_columns = ('name', 'organization', 'project', 'replication_type', 'version_count')


class CloudDNSZoneTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    dns_name = tables.Column()
    visibility = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = CloudDNSZone
        fields = ('pk', 'name', 'organization', 'project', 'dns_name', 'visibility')
        default_columns = ('name', 'organization', 'project', 'dns_name', 'visibility')


class CloudDNSRecordTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='zone.project.organization', linkify=True)
    zone = tables.Column(linkify=True)
    record_type = tables.Column()
    ttl = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = CloudDNSRecord
        fields = ('pk', 'name', 'organization', 'zone', 'record_type', 'ttl')
        default_columns = ('name', 'organization', 'zone', 'record_type', 'ttl')


class MemorystoreInstanceTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    region = tables.Column()
    tier = tables.Column()
    memory_size_gb = tables.Column()
    status = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = MemorystoreInstance
        fields = (
            'pk',
            'name',
            'organization',
            'project',
            'region',
            'tier',
            'memory_size_gb',
            'redis_version',
            'status',
        )
        default_columns = ('name', 'organization', 'project', 'region', 'tier', 'memory_size_gb', 'status')


class NCCHubTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = NCCHub
        fields = ('pk', 'name', 'organization', 'project', 'description')
        default_columns = ('name', 'organization', 'project')


class NCCSpokeTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    hub = tables.Column(linkify=True)
    spoke_type = tables.Column()
    location = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = NCCSpoke
        fields = ('pk', 'name', 'organization', 'project', 'hub', 'spoke_type', 'location', 'linked_vpc_network')
        default_columns = ('name', 'organization', 'project', 'hub', 'spoke_type', 'location')


class VPNGatewayTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    network = tables.Column(linkify=True)
    region = tables.Column()
    gateway_type = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = VPNGateway
        fields = ('pk', 'name', 'organization', 'project', 'network', 'region', 'gateway_type')
        default_columns = ('name', 'organization', 'project', 'network', 'region', 'gateway_type')


class ExternalVPNGatewayTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    redundancy_type = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = ExternalVPNGateway
        fields = ('pk', 'name', 'organization', 'project', 'redundancy_type', 'description')
        default_columns = ('name', 'organization', 'project', 'redundancy_type')


class VPNTunnelTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    region = tables.Column()
    vpn_gateway = tables.Column(linkify=True)
    peer_ip = tables.Column()
    status = tables.Column()
    ike_version = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = VPNTunnel
        fields = (
            'pk',
            'name',
            'organization',
            'project',
            'region',
            'vpn_gateway',
            'peer_ip',
            'status',
            'ike_version',
            'router',
        )
        default_columns = ('name', 'organization', 'project', 'region', 'vpn_gateway', 'peer_ip', 'status')


class InterconnectAttachmentTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    region = tables.Column()
    router = tables.Column(linkify=True)
    attachment_type = tables.Column()
    bandwidth = tables.Column()
    state = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = InterconnectAttachment
        fields = (
            'pk',
            'name',
            'organization',
            'project',
            'region',
            'router',
            'attachment_type',
            'bandwidth',
            'vlan_tag',
            'state',
        )
        default_columns = ('name', 'organization', 'project', 'region', 'attachment_type', 'bandwidth', 'state')


class ServiceAttachmentTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    region = tables.Column()
    connection_preference = tables.Column()
    target_service = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = ServiceAttachment
        fields = (
            'pk',
            'name',
            'organization',
            'project',
            'region',
            'connection_preference',
            'target_service',
            'nat_subnets',
        )
        default_columns = ('name', 'organization', 'project', 'region', 'connection_preference', 'target_service')


class ServiceConnectEndpointTable(NetBoxTable):
    name = tables.Column(linkify=True)
    organization = tables.Column(accessor='project.organization', linkify=True)
    project = tables.Column(linkify=True)
    region = tables.Column()
    network = tables.Column(linkify=True)
    ip_address = tables.Column()
    target_service_attachment = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = ServiceConnectEndpoint
        fields = (
            'pk',
            'name',
            'organization',
            'project',
            'region',
            'network',
            'ip_address',
            'target_service_attachment',
        )
        default_columns = (
            'name',
            'organization',
            'project',
            'region',
            'network',
            'ip_address',
            'target_service_attachment',
        )
