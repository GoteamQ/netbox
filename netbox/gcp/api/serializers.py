from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from gcp.models import (
    GCPProject, ComputeInstance, InstanceTemplate, InstanceGroup,
    VPCNetwork, Subnet, FirewallRule, CloudRouter, CloudNAT, LoadBalancer,
    CloudSQLInstance, CloudSpannerInstance, FirestoreDatabase, BigtableInstance,
    CloudStorageBucket, PersistentDisk,
    GKECluster, GKENodePool,
    ServiceAccount, IAMRole, IAMBinding,
    CloudFunction, CloudRun, PubSubTopic, PubSubSubscription,
    SecretManagerSecret, CloudDNSZone, CloudDNSRecord, MemorystoreInstance
)


class GCPProjectSerializer(NetBoxModelSerializer):
    class Meta:
        model = GCPProject
        fields = ['id', 'url', 'display', 'name', 'project_id', 'project_number', 'status', 'labels', 'tags']


class ComputeInstanceSerializer(NetBoxModelSerializer):
    class Meta:
        model = ComputeInstance
        fields = ['id', 'url', 'display', 'name', 'project', 'zone', 'machine_type', 'status', 
                  'internal_ip', 'external_ip', 'network', 'subnet', 'disk_size_gb', 'image', 'labels', 'tags']


class InstanceTemplateSerializer(NetBoxModelSerializer):
    class Meta:
        model = InstanceTemplate
        fields = ['id', 'url', 'display', 'name', 'project', 'machine_type', 'disk_size_gb', 
                  'image', 'network', 'subnet', 'labels', 'tags']


class InstanceGroupSerializer(NetBoxModelSerializer):
    class Meta:
        model = InstanceGroup
        fields = ['id', 'url', 'display', 'name', 'project', 'zone', 'region', 'template', 
                  'target_size', 'is_managed', 'tags']


class VPCNetworkSerializer(NetBoxModelSerializer):
    class Meta:
        model = VPCNetwork
        fields = ['id', 'url', 'display', 'name', 'project', 'auto_create_subnetworks', 
                  'routing_mode', 'mtu', 'description', 'tags']


class SubnetSerializer(NetBoxModelSerializer):
    class Meta:
        model = Subnet
        fields = ['id', 'url', 'display', 'name', 'project', 'network', 'region', 'ip_cidr_range',
                  'private_ip_google_access', 'secondary_ip_ranges', 'purpose', 'tags']


class FirewallRuleSerializer(NetBoxModelSerializer):
    class Meta:
        model = FirewallRule
        fields = ['id', 'url', 'display', 'name', 'project', 'network', 'direction', 'priority',
                  'action', 'source_ranges', 'destination_ranges', 'source_tags', 'target_tags',
                  'allowed', 'denied', 'disabled', 'tags']


class CloudRouterSerializer(NetBoxModelSerializer):
    class Meta:
        model = CloudRouter
        fields = ['id', 'url', 'display', 'name', 'project', 'network', 'region', 'asn',
                  'advertise_mode', 'advertised_ip_ranges', 'tags']


class CloudNATSerializer(NetBoxModelSerializer):
    class Meta:
        model = CloudNAT
        fields = ['id', 'url', 'display', 'name', 'project', 'router', 'region', 'nat_ip_allocate_option',
                  'source_subnetwork_ip_ranges', 'nat_ips', 'min_ports_per_vm', 'tags']


class LoadBalancerSerializer(NetBoxModelSerializer):
    class Meta:
        model = LoadBalancer
        fields = ['id', 'url', 'display', 'name', 'project', 'scheme', 'lb_type', 'region',
                  'ip_address', 'port', 'backend_services', 'health_check', 'tags']


class CloudSQLInstanceSerializer(NetBoxModelSerializer):
    class Meta:
        model = CloudSQLInstance
        fields = ['id', 'url', 'display', 'name', 'project', 'region', 'database_version', 'database_type',
                  'tier', 'storage_size_gb', 'storage_type', 'status', 'ip_address', 'private_ip',
                  'connection_name', 'high_availability', 'backup_enabled', 'labels', 'tags']


class CloudSpannerInstanceSerializer(NetBoxModelSerializer):
    class Meta:
        model = CloudSpannerInstance
        fields = ['id', 'url', 'display', 'name', 'project', 'config', 'display_name', 'node_count',
                  'processing_units', 'status', 'labels', 'tags']


class FirestoreDatabaseSerializer(NetBoxModelSerializer):
    class Meta:
        model = FirestoreDatabase
        fields = ['id', 'url', 'display', 'name', 'project', 'location', 'database_type',
                  'concurrency_mode', 'status', 'tags']


class BigtableInstanceSerializer(NetBoxModelSerializer):
    class Meta:
        model = BigtableInstance
        fields = ['id', 'url', 'display', 'name', 'project', 'display_name', 'instance_type',
                  'storage_type', 'status', 'labels', 'tags']


class CloudStorageBucketSerializer(NetBoxModelSerializer):
    class Meta:
        model = CloudStorageBucket
        fields = ['id', 'url', 'display', 'name', 'project', 'location', 'storage_class',
                  'versioning_enabled', 'uniform_bucket_level_access', 'public_access_prevention',
                  'lifecycle_rules', 'labels', 'tags']


class PersistentDiskSerializer(NetBoxModelSerializer):
    class Meta:
        model = PersistentDisk
        fields = ['id', 'url', 'display', 'name', 'project', 'zone', 'disk_type', 'size_gb',
                  'status', 'source_image', 'source_snapshot', 'attached_instances', 'labels', 'tags']


class GKEClusterSerializer(NetBoxModelSerializer):
    class Meta:
        model = GKECluster
        fields = ['id', 'url', 'display', 'name', 'project', 'location', 'network', 'subnet',
                  'master_version', 'status', 'endpoint', 'cluster_ipv4_cidr', 'services_ipv4_cidr',
                  'enable_autopilot', 'private_cluster', 'labels', 'tags']


class GKENodePoolSerializer(NetBoxModelSerializer):
    class Meta:
        model = GKENodePool
        fields = ['id', 'url', 'display', 'name', 'cluster', 'machine_type', 'disk_size_gb', 'disk_type',
                  'node_count', 'min_node_count', 'max_node_count', 'autoscaling_enabled', 'preemptible',
                  'spot', 'status', 'version', 'labels', 'tags']


class ServiceAccountSerializer(NetBoxModelSerializer):
    class Meta:
        model = ServiceAccount
        fields = ['id', 'url', 'display', 'email', 'project', 'display_name', 'description',
                  'disabled', 'unique_id', 'tags']


class IAMRoleSerializer(NetBoxModelSerializer):
    class Meta:
        model = IAMRole
        fields = ['id', 'url', 'display', 'name', 'title', 'description', 'stage',
                  'included_permissions', 'is_custom', 'project', 'tags']


class IAMBindingSerializer(NetBoxModelSerializer):
    class Meta:
        model = IAMBinding
        fields = ['id', 'url', 'display', 'project', 'role', 'member', 'condition', 'tags']


class CloudFunctionSerializer(NetBoxModelSerializer):
    class Meta:
        model = CloudFunction
        fields = ['id', 'url', 'display', 'name', 'project', 'region', 'runtime', 'entry_point',
                  'trigger_type', 'trigger_url', 'memory_mb', 'timeout_seconds', 'max_instances',
                  'min_instances', 'status', 'service_account', 'environment_variables', 'labels', 'tags']


class CloudRunSerializer(NetBoxModelSerializer):
    class Meta:
        model = CloudRun
        fields = ['id', 'url', 'display', 'name', 'project', 'region', 'image', 'url', 'port',
                  'cpu', 'memory', 'max_instances', 'min_instances', 'concurrency', 'timeout_seconds',
                  'status', 'service_account', 'ingress', 'labels', 'tags']


class PubSubTopicSerializer(NetBoxModelSerializer):
    class Meta:
        model = PubSubTopic
        fields = ['id', 'url', 'display', 'name', 'project', 'labels', 'message_retention_duration',
                  'schema_settings', 'tags']


class PubSubSubscriptionSerializer(NetBoxModelSerializer):
    class Meta:
        model = PubSubSubscription
        fields = ['id', 'url', 'display', 'name', 'project', 'topic', 'ack_deadline_seconds',
                  'message_retention_duration', 'push_endpoint', 'filter_expression', 'dead_letter_topic',
                  'labels', 'tags']


class SecretManagerSecretSerializer(NetBoxModelSerializer):
    class Meta:
        model = SecretManagerSecret
        fields = ['id', 'url', 'display', 'name', 'project', 'replication_type', 'replication_locations',
                  'labels', 'version_count', 'latest_version', 'tags']


class CloudDNSZoneSerializer(NetBoxModelSerializer):
    class Meta:
        model = CloudDNSZone
        fields = ['id', 'url', 'display', 'name', 'project', 'dns_name', 'visibility', 'description',
                  'name_servers', 'labels', 'tags']


class CloudDNSRecordSerializer(NetBoxModelSerializer):
    class Meta:
        model = CloudDNSRecord
        fields = ['id', 'url', 'display', 'zone', 'name', 'record_type', 'ttl', 'rrdatas', 'tags']


class MemorystoreInstanceSerializer(NetBoxModelSerializer):
    class Meta:
        model = MemorystoreInstance
        fields = ['id', 'url', 'display', 'name', 'project', 'region', 'tier', 'memory_size_gb',
                  'redis_version', 'host', 'port', 'status', 'authorized_network', 'labels', 'tags']
