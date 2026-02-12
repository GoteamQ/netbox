import django_filters
from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet
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


class GCPOrganizationFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = GCPOrganization
        fields = ['id', 'name', 'organization_id', 'is_active', 'discovery_status']

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value) | queryset.filter(organization_id__icontains=value)


class DiscoveryLogFilterSet(NetBoxModelFilterSet):
    organization = django_filters.ModelChoiceFilter(queryset=GCPOrganization.objects.all())

    class Meta:
        model = DiscoveryLog
        fields = ['id', 'organization', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(organization__name__icontains=value)


class GCPProjectFilterSet(NetBoxModelFilterSet):
    organization = django_filters.ModelChoiceFilter(queryset=GCPOrganization.objects.all())

    class Meta:
        model = GCPProject
        fields = ['id', 'name', 'project_id', 'status', 'organization', 'discovered']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(project_id__icontains=value)
            | Q(project_number__icontains=value)
            | Q(organization__name__icontains=value)
            | Q(status__icontains=value)
        )


class ComputeInstanceFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = ComputeInstance
        fields = ['id', 'name', 'project', 'zone', 'machine_type', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(zone__icontains=value)
            | Q(machine_type__icontains=value)
            | Q(internal_ip__icontains=value)
            | Q(external_ip__icontains=value)
            | Q(status__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
            | Q(image__icontains=value)
            | Q(network__icontains=value)
        )


class InstanceTemplateFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = InstanceTemplate
        fields = ['id', 'name', 'project', 'machine_type']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(machine_type__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
            | Q(image__icontains=value)
        )


class InstanceGroupFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = InstanceGroup
        fields = ['id', 'name', 'project', 'zone', 'region', 'is_managed']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(zone__icontains=value)
            | Q(region__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
        )


class VPCNetworkFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = VPCNetwork
        fields = ['id', 'name', 'project', 'routing_mode']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value)
            | Q(routing_mode__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
        )
        if value.strip().isdigit():
            qs_filter |= Q(mtu=int(value.strip()))
        return queryset.filter(qs_filter)


class SubnetFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())
    network = django_filters.ModelChoiceFilter(queryset=VPCNetwork.objects.all())

    class Meta:
        model = Subnet
        fields = ['id', 'name', 'project', 'network', 'region', 'ip_cidr_range']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(region__icontains=value)
            | Q(ip_cidr_range__icontains=value)
            | Q(gateway_address__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(network__name__icontains=value)
            | Q(project__organization__name__icontains=value)
            | Q(purpose__icontains=value)
        )


class FirewallRuleFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())
    network = django_filters.ModelChoiceFilter(queryset=VPCNetwork.objects.all())

    class Meta:
        model = FirewallRule
        fields = ['id', 'name', 'project', 'network', 'direction', 'action']

    def search(self, queryset, name, value):
        qs_filter = (
            Q(name__icontains=value)
            | Q(action__icontains=value)
            | Q(direction__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(network__name__icontains=value)
            | Q(project__organization__name__icontains=value)
        )
        if value.strip().isdigit():
            qs_filter |= Q(priority=int(value.strip()))
        return queryset.filter(qs_filter)


class CloudRouterFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())
    network = django_filters.ModelChoiceFilter(queryset=VPCNetwork.objects.all())

    class Meta:
        model = CloudRouter
        fields = ['id', 'name', 'project', 'network', 'region']

    def search(self, queryset, name, value):
        qs_filter = (
            Q(name__icontains=value)
            | Q(region__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(network__name__icontains=value)
            | Q(project__organization__name__icontains=value)
        )
        if value.strip().isdigit():
            qs_filter |= Q(asn=int(value.strip()))
            qs_filter |= Q(asn__icontains=value.strip())
        return queryset.filter(qs_filter)


class CloudNATFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())
    router = django_filters.ModelChoiceFilter(queryset=CloudRouter.objects.all())

    class Meta:
        model = CloudNAT
        fields = ['id', 'name', 'project', 'router', 'region']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(region__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(router__name__icontains=value)
            | Q(project__organization__name__icontains=value)
            | Q(nat_ip_allocate_option__icontains=value)
        )


class LoadBalancerFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = LoadBalancer
        fields = ['id', 'name', 'project', 'scheme', 'lb_type', 'region']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(ip_address__icontains=value)
            | Q(region__icontains=value)
            | Q(lb_type__icontains=value)
            | Q(scheme__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
        )


class CloudSQLInstanceFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = CloudSQLInstance
        fields = ['id', 'name', 'project', 'region', 'database_type', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(region__icontains=value)
            | Q(database_type__icontains=value)
            | Q(database_version__icontains=value)
            | Q(tier__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
            | Q(status__icontains=value)
        )


class CloudSpannerInstanceFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = CloudSpannerInstance
        fields = ['id', 'name', 'project', 'config', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(config__icontains=value)
            | Q(display_name__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
        )


class FirestoreDatabaseFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = FirestoreDatabase
        fields = ['id', 'name', 'project', 'location', 'database_type', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(location__icontains=value)
            | Q(database_type__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
            | Q(status__icontains=value)
        )


class BigtableInstanceFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = BigtableInstance
        fields = ['id', 'name', 'project', 'instance_type', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(display_name__icontains=value)
            | Q(instance_type__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
        )


class CloudStorageBucketFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = CloudStorageBucket
        fields = ['id', 'name', 'project', 'location', 'storage_class']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(location__icontains=value)
            | Q(storage_class__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
        )


class PersistentDiskFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = PersistentDisk
        fields = ['id', 'name', 'project', 'zone', 'disk_type', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(zone__icontains=value)
            | Q(disk_type__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
            | Q(status__icontains=value)
        )


class GKEClusterFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = GKECluster
        fields = ['id', 'name', 'project', 'location', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(location__icontains=value)
            | Q(endpoint__icontains=value)
            | Q(master_version__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
            | Q(status__icontains=value)
        )


class GKENodePoolFilterSet(NetBoxModelFilterSet):
    cluster = django_filters.ModelChoiceFilter(queryset=GKECluster.objects.all())

    class Meta:
        model = GKENodePool
        fields = ['id', 'name', 'cluster', 'machine_type', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(machine_type__icontains=value)
            | Q(version__icontains=value)
            | Q(cluster__name__icontains=value)
            | Q(cluster__project__name__icontains=value)
            | Q(cluster__project__project_id__icontains=value)
            | Q(cluster__project__organization__name__icontains=value)
            | Q(status__icontains=value)
        )


class ServiceAccountFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = ServiceAccount
        fields = ['id', 'email', 'project', 'disabled']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(email__icontains=value)
            | Q(display_name__icontains=value)
            | Q(unique_id__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
        )


class IAMRoleFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = IAMRole
        fields = ['id', 'name', 'title', 'stage', 'is_custom', 'project']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(title__icontains=value)
            | Q(description__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
        )


class IAMBindingFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())
    role = django_filters.ModelChoiceFilter(queryset=IAMRole.objects.all())

    class Meta:
        model = IAMBinding
        fields = ['id', 'project', 'role', 'member']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(member__icontains=value)
            | Q(role__name__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
        )


class CloudFunctionFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = CloudFunction
        fields = ['id', 'name', 'project', 'region', 'runtime', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(region__icontains=value)
            | Q(runtime__icontains=value)
            | Q(entry_point__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
        )


class CloudRunFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = CloudRun
        fields = ['id', 'name', 'project', 'region', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(region__icontains=value)
            | Q(image__icontains=value)
            | Q(url__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
            | Q(status__icontains=value)
            | Q(cpu__icontains=value)
            | Q(memory__icontains=value)
        )


class PubSubTopicFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = PubSubTopic
        fields = ['id', 'name', 'project']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
        )


class PubSubSubscriptionFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())
    topic = django_filters.ModelChoiceFilter(queryset=PubSubTopic.objects.all())

    class Meta:
        model = PubSubSubscription
        fields = ['id', 'name', 'project', 'topic']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(topic__name__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
        )


class SecretManagerSecretFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = SecretManagerSecret
        fields = ['id', 'name', 'project', 'replication_type']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
            | Q(replication_type__icontains=value)
        )


class CloudDNSZoneFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = CloudDNSZone
        fields = ['id', 'name', 'project', 'dns_name', 'visibility']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(dns_name__icontains=value)
            | Q(description__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
            | Q(visibility__icontains=value)
        )


class CloudDNSRecordFilterSet(NetBoxModelFilterSet):
    zone = django_filters.ModelChoiceFilter(queryset=CloudDNSZone.objects.all())

    class Meta:
        model = CloudDNSRecord
        fields = ['id', 'name', 'zone', 'record_type']

    def search(self, queryset, name, value):
        qs_filter = (
            Q(name__icontains=value)
            | Q(record_type__icontains=value)
            | Q(zone__name__icontains=value)
            | Q(zone__project__name__icontains=value)
            | Q(zone__project__project_id__icontains=value)
            | Q(zone__project__organization__name__icontains=value)
        )
        if value.strip().isdigit():
            qs_filter |= Q(ttl=int(value.strip()))
        return queryset.filter(qs_filter)


class MemorystoreInstanceFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = MemorystoreInstance
        fields = ['id', 'name', 'project', 'region', 'tier', 'status']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(region__icontains=value)
            | Q(tier__icontains=value)
            | Q(host__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
            | Q(status__icontains=value)
            | Q(redis_version__icontains=value)
        )


class NCCHubFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = NCCHub
        fields = ['id', 'name', 'project']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(description__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
        )


class NCCSpokeFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())
    hub = django_filters.ModelChoiceFilter(queryset=NCCHub.objects.all())

    class Meta:
        model = NCCSpoke
        fields = ['id', 'name', 'project', 'hub', 'spoke_type', 'location']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(description__icontains=value)
            | Q(location__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
            | Q(hub__name__icontains=value)
            | Q(spoke_type__icontains=value)
            | Q(linked_vpc_network__name__icontains=value)
        )


class VPNGatewayFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())
    network = django_filters.ModelChoiceFilter(queryset=VPCNetwork.objects.all())

    class Meta:
        model = VPNGateway
        fields = ['id', 'name', 'project', 'network', 'region', 'gateway_type']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(region__icontains=value)
            | Q(gateway_type__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
        )


class ExternalVPNGatewayFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())

    class Meta:
        model = ExternalVPNGateway
        fields = ['id', 'name', 'project', 'redundancy_type']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(description__icontains=value)
            | Q(redundancy_type__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
        )


class VPNTunnelFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())
    vpn_gateway = django_filters.ModelChoiceFilter(queryset=VPNGateway.objects.all())

    class Meta:
        model = VPNTunnel
        fields = ['id', 'name', 'project', 'region', 'vpn_gateway', 'status', 'ike_version']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(region__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
            | Q(router__name__icontains=value)
            | Q(status__icontains=value)
            | Q(peer_ip__icontains=value)
            | Q(vpn_gateway__name__icontains=value)
        )


class InterconnectAttachmentFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelChoiceFilter(queryset=GCPProject.objects.all())
    router = django_filters.ModelChoiceFilter(queryset=CloudRouter.objects.all())

    class Meta:
        model = InterconnectAttachment
        fields = ['id', 'name', 'project', 'region', 'router', 'attachment_type', 'bandwidth', 'state']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(region__icontains=value)
            | Q(attachment_type__icontains=value)
            | Q(bandwidth__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
        )


class ServiceAttachmentFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelMultipleChoiceFilter(
        queryset=GCPProject.objects.all(),
        label='Project',
    )

    class Meta:
        model = ServiceAttachment
        fields = ['id', 'name', 'project', 'region', 'connection_preference']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(region__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
            | Q(connection_preference__icontains=value)
            | Q(nat_subnets__icontains=value)
        )


class ServiceConnectEndpointFilterSet(NetBoxModelFilterSet):
    project = django_filters.ModelMultipleChoiceFilter(
        queryset=GCPProject.objects.all(),
        label='Project',
    )
    network = django_filters.ModelMultipleChoiceFilter(
        queryset=VPCNetwork.objects.all(),
        label='Network',
    )

    class Meta:
        model = ServiceConnectEndpoint
        fields = ['id', 'name', 'project', 'region', 'network', 'ip_address']

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(ip_address__icontains=value)
            | Q(region__icontains=value)
            | Q(project__name__icontains=value)
            | Q(project__project_id__icontains=value)
            | Q(project__organization__name__icontains=value)
            | Q(network__name__icontains=value)
            | Q(target_service_attachment__icontains=value)
        )
