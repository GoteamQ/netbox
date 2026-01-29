import django_filters

from netbox.filtersets import NetBoxModelFilterSet
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


class GCPProjectFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = GCPProject
        fields = ['id', 'name', 'project_id', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value) | queryset.filter(project_id__icontains=value)


class ComputeInstanceFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = ComputeInstance
        fields = ['id', 'name', 'project', 'zone', 'machine_type', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class InstanceTemplateFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = InstanceTemplate
        fields = ['id', 'name', 'project', 'machine_type']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class InstanceGroupFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = InstanceGroup
        fields = ['id', 'name', 'project', 'zone', 'region', 'is_managed']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class VPCNetworkFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = VPCNetwork
        fields = ['id', 'name', 'project', 'routing_mode']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class SubnetFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())
    network = django_filters.ModelChoiceFilter(queryset=VPCNetwork.objects.all())

    class Meta:
        model = Subnet
        fields = ['id', 'name', 'project', 'network', 'region', 'ip_cidr_range']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class FirewallRuleFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())
    network = django_filters.ModelChoiceFilter(queryset=VPCNetwork.objects.all())

    class Meta:
        model = FirewallRule
        fields = ['id', 'name', 'project', 'network', 'direction', 'action']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class CloudRouterFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())
    network = django_filters.ModelChoiceFilter(queryset=VPCNetwork.objects.all())

    class Meta:
        model = CloudRouter
        fields = ['id', 'name', 'project', 'network', 'region']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class CloudNATFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())
    router = django_filters.ModelChoiceFilter(queryset=CloudRouter.objects.all())

    class Meta:
        model = CloudNAT
        fields = ['id', 'name', 'project', 'router', 'region']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class LoadBalancerFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = LoadBalancer
        fields = ['id', 'name', 'project', 'scheme', 'lb_type', 'region']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class CloudSQLInstanceFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = CloudSQLInstance
        fields = ['id', 'name', 'project', 'region', 'database_type', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class CloudSpannerInstanceFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = CloudSpannerInstance
        fields = ['id', 'name', 'project', 'config', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class FirestoreDatabaseFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = FirestoreDatabase
        fields = ['id', 'name', 'project', 'location', 'database_type', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class BigtableInstanceFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = BigtableInstance
        fields = ['id', 'name', 'project', 'instance_type', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class CloudStorageBucketFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = CloudStorageBucket
        fields = ['id', 'name', 'project', 'location', 'storage_class']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class PersistentDiskFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = PersistentDisk
        fields = ['id', 'name', 'project', 'zone', 'disk_type', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class GKEClusterFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = GKECluster
        fields = ['id', 'name', 'project', 'location', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class GKENodePoolFilterSet(NetBoxModelFilterSet):
    cluster = django_filters.ModelChoiceFilter(queryset=GKECluster.objects.all())

    class Meta:
        model = GKENodePool
        fields = ['id', 'name', 'cluster', 'machine_type', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class ServiceAccountFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = ServiceAccount
        fields = ['id', 'email', 'project', 'disabled']

    def search(self, queryset, name, value):
        return queryset.filter(email__icontains=value) | queryset.filter(display_name__icontains=value)


class IAMRoleFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = IAMRole
        fields = ['id', 'name', 'title', 'stage', 'is_custom', 'project']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value) | queryset.filter(title__icontains=value)


class IAMBindingFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())
    role = django_filters.ModelChoiceFilter(queryset=IAMRole.objects.all())

    class Meta:
        model = IAMBinding
        fields = ['id', 'project', 'role', 'member']

    def search(self, queryset, name, value):
        return queryset.filter(member__icontains=value)


class CloudFunctionFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = CloudFunction
        fields = ['id', 'name', 'project', 'region', 'runtime', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class CloudRunFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = CloudRun
        fields = ['id', 'name', 'project', 'region', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class PubSubTopicFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = PubSubTopic
        fields = ['id', 'name', 'project']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class PubSubSubscriptionFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())
    topic = django_filters.ModelChoiceFilter(queryset=PubSubTopic.objects.all())

    class Meta:
        model = PubSubSubscription
        fields = ['id', 'name', 'project', 'topic']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class SecretManagerSecretFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = SecretManagerSecret
        fields = ['id', 'name', 'project', 'replication_type']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class CloudDNSZoneFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = CloudDNSZone
        fields = ['id', 'name', 'project', 'dns_name', 'visibility']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value) | queryset.filter(dns_name__icontains=value)


class CloudDNSRecordFilterSet(NetBoxModelFilterSet):
    zone = django_filters.ModelChoiceFilter(queryset=CloudDNSZone.objects.all())

    class Meta:
        model = CloudDNSRecord
        fields = ['id', 'name', 'zone', 'record_type']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class MemorystoreInstanceFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = MemorystoreInstance
        fields = ['id', 'name', 'project', 'region', 'tier', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)
