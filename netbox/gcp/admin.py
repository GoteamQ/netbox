from django.contrib import admin
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


@admin.register(GCPProject)
class GCPProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'project_id', 'status']
    search_fields = ['name', 'project_id']


@admin.register(ComputeInstance)
class ComputeInstanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'zone', 'machine_type', 'status']
    list_filter = ['project', 'status']
    search_fields = ['name']


@admin.register(InstanceTemplate)
class InstanceTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'machine_type']
    list_filter = ['project']
    search_fields = ['name']


@admin.register(InstanceGroup)
class InstanceGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'zone', 'target_size']
    list_filter = ['project', 'is_managed']
    search_fields = ['name']


@admin.register(VPCNetwork)
class VPCNetworkAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'routing_mode']
    list_filter = ['project']
    search_fields = ['name']


@admin.register(Subnet)
class SubnetAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'network', 'region', 'ip_cidr_range']
    list_filter = ['project', 'network']
    search_fields = ['name', 'ip_cidr_range']


@admin.register(FirewallRule)
class FirewallRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'network', 'direction', 'priority']
    list_filter = ['project', 'network', 'direction']
    search_fields = ['name']


@admin.register(CloudRouter)
class CloudRouterAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'network', 'region']
    list_filter = ['project', 'network']
    search_fields = ['name']


@admin.register(CloudNAT)
class CloudNATAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'router', 'region']
    list_filter = ['project']
    search_fields = ['name']


@admin.register(LoadBalancer)
class LoadBalancerAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'scheme', 'lb_type']
    list_filter = ['project', 'scheme', 'lb_type']
    search_fields = ['name']


@admin.register(CloudSQLInstance)
class CloudSQLInstanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'region', 'database_type', 'tier', 'status']
    list_filter = ['project', 'database_type', 'status']
    search_fields = ['name']


@admin.register(CloudSpannerInstance)
class CloudSpannerInstanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'config', 'node_count', 'status']
    list_filter = ['project', 'status']
    search_fields = ['name']


@admin.register(FirestoreDatabase)
class FirestoreDatabaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'location', 'database_type', 'status']
    list_filter = ['project', 'status']
    search_fields = ['name']


@admin.register(BigtableInstance)
class BigtableInstanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'instance_type', 'status']
    list_filter = ['project', 'status']
    search_fields = ['name']


@admin.register(CloudStorageBucket)
class CloudStorageBucketAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'location', 'storage_class']
    list_filter = ['project', 'storage_class']
    search_fields = ['name']


@admin.register(PersistentDisk)
class PersistentDiskAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'zone', 'disk_type', 'size_gb', 'status']
    list_filter = ['project', 'disk_type', 'status']
    search_fields = ['name']


@admin.register(GKECluster)
class GKEClusterAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'location', 'master_version', 'status']
    list_filter = ['project', 'status']
    search_fields = ['name']


@admin.register(GKENodePool)
class GKENodePoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'cluster', 'machine_type', 'node_count', 'status']
    list_filter = ['cluster', 'status']
    search_fields = ['name']


@admin.register(ServiceAccount)
class ServiceAccountAdmin(admin.ModelAdmin):
    list_display = ['email', 'project', 'display_name', 'disabled']
    list_filter = ['project', 'disabled']
    search_fields = ['email', 'display_name']


@admin.register(IAMRole)
class IAMRoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'stage', 'is_custom']
    list_filter = ['stage', 'is_custom']
    search_fields = ['name', 'title']


@admin.register(IAMBinding)
class IAMBindingAdmin(admin.ModelAdmin):
    list_display = ['project', 'role', 'member']
    list_filter = ['project', 'role']
    search_fields = ['member']


@admin.register(CloudFunction)
class CloudFunctionAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'region', 'runtime', 'status']
    list_filter = ['project', 'runtime', 'status']
    search_fields = ['name']


@admin.register(CloudRun)
class CloudRunAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'region', 'status']
    list_filter = ['project', 'status']
    search_fields = ['name']


@admin.register(PubSubTopic)
class PubSubTopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'project']
    list_filter = ['project']
    search_fields = ['name']


@admin.register(PubSubSubscription)
class PubSubSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'topic']
    list_filter = ['project', 'topic']
    search_fields = ['name']


@admin.register(SecretManagerSecret)
class SecretManagerSecretAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'replication_type', 'version_count']
    list_filter = ['project', 'replication_type']
    search_fields = ['name']


@admin.register(CloudDNSZone)
class CloudDNSZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'dns_name', 'visibility']
    list_filter = ['project', 'visibility']
    search_fields = ['name', 'dns_name']


@admin.register(CloudDNSRecord)
class CloudDNSRecordAdmin(admin.ModelAdmin):
    list_display = ['name', 'zone', 'record_type', 'ttl']
    list_filter = ['zone', 'record_type']
    search_fields = ['name']


@admin.register(MemorystoreInstance)
class MemorystoreInstanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'region', 'tier', 'memory_size_gb', 'status']
    list_filter = ['project', 'tier', 'status']
    search_fields = ['name']
