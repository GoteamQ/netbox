from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer

from gcp.models import (
    BigtableInstance,
    CloudDNSRecord,
    CloudDNSZone,
    CloudFunction,
    CloudNAT,
    CloudRouter,
    CloudRun,
    CloudSQLInstance,
    CloudSpannerInstance,
    CloudStorageBucket,
    ComputeInstance,
    DiscoveryLog,
    ExternalVPNGateway,
    FirewallRule,
    FirestoreDatabase,
    GCPOrganization,
    GCPProject,
    GKECluster,
    GKENodePool,
    IAMBinding,
    IAMRole,
    InstanceGroup,
    InstanceTemplate,
    InterconnectAttachment,
    LoadBalancer,
    MemorystoreInstance,
    NCCHub,
    NCCSpoke,
    PersistentDisk,
    PubSubSubscription,
    PubSubTopic,
    SecretManagerSecret,
    ServiceAccount,
    ServiceAttachment,
    ServiceConnectEndpoint,
    Subnet,
    VPCNetwork,
    VPNGateway,
    VPNTunnel,
)


class GCPOrganizationSerializer(NetBoxModelSerializer):
    class Meta:
        model = GCPOrganization
        fields = [
            'id',
            'url',
            'display',
            'name',
            'organization_id',
            'is_active',
            'auto_discover',
            'discover_compute',
            'discover_networking',
            'discover_databases',
            'discover_storage',
            'discover_kubernetes',
            'discover_serverless',
            'discover_iam',
            'discovery_status',
            'last_discovery',
            'tags',
        ]
        read_only_fields = ['discovery_status', 'last_discovery']


class GCPOrganizationWriteSerializer(NetBoxModelSerializer):
    service_account_json = serializers.CharField(write_only=True)

    class Meta:
        model = GCPOrganization
        fields = [
            'id',
            'url',
            'display',
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


class DiscoveryLogSerializer(NetBoxModelSerializer):
    class Meta:
        model = DiscoveryLog
        fields = [
            'id',
            'url',
            'display',
            'organization',
            'started_at',
            'completed_at',
            'status',
            'projects_discovered',
            'instances_discovered',
            'networks_discovered',
            'databases_discovered',
            'buckets_discovered',
            'clusters_discovered',
            'total_resources',
            'error_message',
        ]
        read_only_fields = fields


class GCPProjectSerializer(NetBoxModelSerializer):
    class Meta:
        model = GCPProject
        fields = [
            'id',
            'url',
            'display',
            'name',
            'organization',
            'project_id',
            'project_number',
            'status',
            'discovered',
            'last_synced',
            'labels',
            'tags',
        ]


class ComputeInstanceSerializer(NetBoxModelSerializer):
    class Meta:
        model = ComputeInstance
        fields = [
            'id',
            'url',
            'display',
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


class InstanceTemplateSerializer(NetBoxModelSerializer):
    class Meta:
        model = InstanceTemplate
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'machine_type',
            'disk_size_gb',
            'image',
            'network',
            'subnet',
            'labels',
            'tags',
        ]


class InstanceGroupSerializer(NetBoxModelSerializer):
    class Meta:
        model = InstanceGroup
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'zone',
            'region',
            'template',
            'target_size',
            'is_managed',
            'tags',
        ]


class VPCNetworkSerializer(NetBoxModelSerializer):
    class Meta:
        model = VPCNetwork
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'auto_create_subnetworks',
            'routing_mode',
            'mtu',
            'tags',
        ]


class SubnetSerializer(NetBoxModelSerializer):
    class Meta:
        model = Subnet
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'network',
            'region',
            'ip_cidr_range',
            'private_ip_google_access',
            'purpose',
            'tags',
        ]


class FirewallRuleSerializer(NetBoxModelSerializer):
    class Meta:
        model = FirewallRule
        fields = [
            'id',
            'url',
            'display',
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


class CloudRouterSerializer(NetBoxModelSerializer):
    class Meta:
        model = CloudRouter
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'network',
            'region',
            'asn',
            'advertise_mode',
            'advertised_ip_ranges',
            'tags',
        ]


class CloudNATSerializer(NetBoxModelSerializer):
    class Meta:
        model = CloudNAT
        fields = [
            'id',
            'url',
            'display',
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


class LoadBalancerSerializer(NetBoxModelSerializer):
    class Meta:
        model = LoadBalancer
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'scheme',
            'lb_type',
            'region',
            'ip_address',
            'port',
            'tags',
        ]


class CloudSQLInstanceSerializer(NetBoxModelSerializer):
    class Meta:
        model = CloudSQLInstance
        fields = [
            'id',
            'url',
            'display',
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


class CloudSpannerInstanceSerializer(NetBoxModelSerializer):
    class Meta:
        model = CloudSpannerInstance
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'config',
            'display_name',
            'node_count',
            'processing_units',
            'status',
            'tags',
        ]


class FirestoreDatabaseSerializer(NetBoxModelSerializer):
    class Meta:
        model = FirestoreDatabase
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'location',
            'database_type',
            'concurrency_mode',
            'status',
            'tags',
        ]


class BigtableInstanceSerializer(NetBoxModelSerializer):
    class Meta:
        model = BigtableInstance
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'display_name',
            'instance_type',
            'storage_type',
            'status',
            'tags',
        ]


class CloudStorageBucketSerializer(NetBoxModelSerializer):
    class Meta:
        model = CloudStorageBucket
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'location',
            'storage_class',
            'versioning_enabled',
            'lifecycle_rules',
            'labels',
            'tags',
        ]


class PersistentDiskSerializer(NetBoxModelSerializer):
    class Meta:
        model = PersistentDisk
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'zone',
            'disk_type',
            'size_gb',
            'status',
            'source_image',
            'tags',
        ]


class GKEClusterSerializer(NetBoxModelSerializer):
    class Meta:
        model = GKECluster
        fields = [
            'id',
            'url',
            'display',
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


class GKENodePoolSerializer(NetBoxModelSerializer):
    class Meta:
        model = GKENodePool
        fields = [
            'id',
            'url',
            'display',
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


class ServiceAccountSerializer(NetBoxModelSerializer):
    class Meta:
        model = ServiceAccount
        fields = [
            'id',
            'url',
            'display',
            'email',
            'project',
            'display_name',
            'disabled',
            'unique_id',
            'tags',
        ]


class IAMRoleSerializer(NetBoxModelSerializer):
    class Meta:
        model = IAMRole
        fields = [
            'id',
            'url',
            'display',
            'name',
            'title',
            'description',
            'stage',
            'permissions',
            'is_custom',
            'project',
            'tags',
        ]


class IAMBindingSerializer(NetBoxModelSerializer):
    class Meta:
        model = IAMBinding
        fields = [
            'id',
            'url',
            'display',
            'project',
            'role',
            'member',
            'condition',
            'tags',
        ]


class CloudFunctionSerializer(NetBoxModelSerializer):
    class Meta:
        model = CloudFunction
        fields = [
            'id',
            'url',
            'display',
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


class CloudRunSerializer(NetBoxModelSerializer):
    class Meta:
        model = CloudRun
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'region',
            'image',
            'url',
            'cpu',
            'memory',
            'max_instances',
            'min_instances',
            'status',
            'tags',
        ]


class PubSubTopicSerializer(NetBoxModelSerializer):
    class Meta:
        model = PubSubTopic
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'labels',
            'tags',
        ]


class PubSubSubscriptionSerializer(NetBoxModelSerializer):
    class Meta:
        model = PubSubSubscription
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'topic',
            'ack_deadline_seconds',
            'message_retention_duration',
            'push_endpoint',
            'tags',
        ]


class SecretManagerSecretSerializer(NetBoxModelSerializer):
    class Meta:
        model = SecretManagerSecret
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'replication_type',
            'replication_locations',
            'labels',
            'version_count',
            'latest_version',
            'tags',
        ]


class CloudDNSZoneSerializer(NetBoxModelSerializer):
    class Meta:
        model = CloudDNSZone
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'dns_name',
            'visibility',
            'description',
            'name_servers',
            'tags',
        ]


class CloudDNSRecordSerializer(NetBoxModelSerializer):
    class Meta:
        model = CloudDNSRecord
        fields = [
            'id',
            'url',
            'display',
            'zone',
            'name',
            'record_type',
            'ttl',
            'rrdatas',
            'tags',
        ]


class MemorystoreInstanceSerializer(NetBoxModelSerializer):
    class Meta:
        model = MemorystoreInstance
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'region',
            'tier',
            'memory_size_gb',
            'redis_version',
            'host',
            'port',
            'status',
            'network',
            'tags',
        ]


class NCCHubSerializer(NetBoxModelSerializer):
    class Meta:
        model = NCCHub
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'description',
            'labels',
            'tags',
        ]


class NCCSpokeSerializer(NetBoxModelSerializer):
    class Meta:
        model = NCCSpoke
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'hub',
            'spoke_type',
            'location',
            'description',
            'linked_vpn_tunnels',
            'linked_interconnect_attachments',
            'linked_vpc_network',
            'labels',
            'tags',
        ]


class VPNGatewaySerializer(NetBoxModelSerializer):
    class Meta:
        model = VPNGateway
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'network',
            'region',
            'gateway_type',
            'ip_addresses',
            'labels',
            'tags',
        ]


class ExternalVPNGatewaySerializer(NetBoxModelSerializer):
    class Meta:
        model = ExternalVPNGateway
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'redundancy_type',
            'interfaces',
            'description',
            'labels',
            'tags',
        ]


class VPNTunnelSerializer(NetBoxModelSerializer):
    class Meta:
        model = VPNTunnel
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'region',
            'vpn_gateway',
            'vpn_gateway_interface',
            'peer_external_gateway',
            'peer_external_gateway_interface',
            'peer_ip',
            'shared_secret_hash',
            'ike_version',
            'local_traffic_selector',
            'remote_traffic_selector',
            'router',
            'status',
            'detailed_status',
            'labels',
            'tags',
        ]


class InterconnectAttachmentSerializer(NetBoxModelSerializer):
    class Meta:
        model = InterconnectAttachment
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'region',
            'router',
            'attachment_type',
            'bandwidth',
            'vlan_tag',
            'pairing_key',
            'partner_asn',
            'cloud_router_ip_address',
            'customer_router_ip_address',
            'state',
            'edge_availability_domain',
            'labels',
            'tags',
        ]


class ServiceAttachmentSerializer(NetBoxModelSerializer):
    class Meta:
        model = ServiceAttachment
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'region',
            'connection_preference',
            'nat_subnets',
            'target_service',
            'tags',
        ]


class ServiceConnectEndpointSerializer(NetBoxModelSerializer):
    class Meta:
        model = ServiceConnectEndpoint
        fields = [
            'id',
            'url',
            'display',
            'name',
            'project',
            'region',
            'network',
            'ip_address',
            'target_service_attachment',
            'tags',
        ]
