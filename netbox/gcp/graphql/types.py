from netbox.graphql.types import NetBoxObjectType
from gcp import models, filtersets


class GCPOrganizationType(NetBoxObjectType):
    class Meta:
        model = models.GCPOrganization
        filterset_class = filtersets.GCPOrganizationFilterSet


class DiscoveryLogType(NetBoxObjectType):
    class Meta:
        model = models.DiscoveryLog
        filterset_class = filtersets.DiscoveryLogFilterSet


class GCPProjectType(NetBoxObjectType):
    class Meta:
        model = models.GCPProject
        filterset_class = filtersets.GCPProjectFilterSet


class ComputeInstanceType(NetBoxObjectType):
    class Meta:
        model = models.ComputeInstance
        filterset_class = filtersets.ComputeInstanceFilterSet


class InstanceTemplateType(NetBoxObjectType):
    class Meta:
        model = models.InstanceTemplate
        filterset_class = filtersets.InstanceTemplateFilterSet


class InstanceGroupType(NetBoxObjectType):
    class Meta:
        model = models.InstanceGroup
        filterset_class = filtersets.InstanceGroupFilterSet


class VPCNetworkType(NetBoxObjectType):
    class Meta:
        model = models.VPCNetwork
        filterset_class = filtersets.VPCNetworkFilterSet


class SubnetType(NetBoxObjectType):
    class Meta:
        model = models.Subnet
        filterset_class = filtersets.SubnetFilterSet


class FirewallRuleType(NetBoxObjectType):
    class Meta:
        model = models.FirewallRule
        filterset_class = filtersets.FirewallRuleFilterSet


class CloudRouterType(NetBoxObjectType):
    class Meta:
        model = models.CloudRouter
        filterset_class = filtersets.CloudRouterFilterSet


class CloudNATType(NetBoxObjectType):
    class Meta:
        model = models.CloudNAT
        filterset_class = filtersets.CloudNATFilterSet


class LoadBalancerType(NetBoxObjectType):
    class Meta:
        model = models.LoadBalancer
        filterset_class = filtersets.LoadBalancerFilterSet


class CloudSQLInstanceType(NetBoxObjectType):
    class Meta:
        model = models.CloudSQLInstance
        filterset_class = filtersets.CloudSQLInstanceFilterSet


class CloudSpannerInstanceType(NetBoxObjectType):
    class Meta:
        model = models.CloudSpannerInstance
        filterset_class = filtersets.CloudSpannerInstanceFilterSet


class FirestoreDatabaseType(NetBoxObjectType):
    class Meta:
        model = models.FirestoreDatabase
        filterset_class = filtersets.FirestoreDatabaseFilterSet


class BigtableInstanceType(NetBoxObjectType):
    class Meta:
        model = models.BigtableInstance
        filterset_class = filtersets.BigtableInstanceFilterSet


class CloudStorageBucketType(NetBoxObjectType):
    class Meta:
        model = models.CloudStorageBucket
        filterset_class = filtersets.CloudStorageBucketFilterSet


class PersistentDiskType(NetBoxObjectType):
    class Meta:
        model = models.PersistentDisk
        filterset_class = filtersets.PersistentDiskFilterSet


class GKEClusterType(NetBoxObjectType):
    class Meta:
        model = models.GKECluster
        filterset_class = filtersets.GKEClusterFilterSet


class GKENodePoolType(NetBoxObjectType):
    class Meta:
        model = models.GKENodePool
        filterset_class = filtersets.GKENodePoolFilterSet


class ServiceAccountType(NetBoxObjectType):
    class Meta:
        model = models.ServiceAccount
        filterset_class = filtersets.ServiceAccountFilterSet


class IAMRoleType(NetBoxObjectType):
    class Meta:
        model = models.IAMRole
        filterset_class = filtersets.IAMRoleFilterSet


class IAMBindingType(NetBoxObjectType):
    class Meta:
        model = models.IAMBinding
        filterset_class = filtersets.IAMBindingFilterSet


class CloudFunctionType(NetBoxObjectType):
    class Meta:
        model = models.CloudFunction
        filterset_class = filtersets.CloudFunctionFilterSet


class CloudRunType(NetBoxObjectType):
    class Meta:
        model = models.CloudRun
        filterset_class = filtersets.CloudRunFilterSet


class PubSubTopicType(NetBoxObjectType):
    class Meta:
        model = models.PubSubTopic
        filterset_class = filtersets.PubSubTopicFilterSet


class PubSubSubscriptionType(NetBoxObjectType):
    class Meta:
        model = models.PubSubSubscription
        filterset_class = filtersets.PubSubSubscriptionFilterSet


class SecretManagerSecretType(NetBoxObjectType):
    class Meta:
        model = models.SecretManagerSecret
        filterset_class = filtersets.SecretManagerSecretFilterSet


class CloudDNSZoneType(NetBoxObjectType):
    class Meta:
        model = models.CloudDNSZone
        filterset_class = filtersets.CloudDNSZoneFilterSet


class CloudDNSRecordType(NetBoxObjectType):
    class Meta:
        model = models.CloudDNSRecord
        filterset_class = filtersets.CloudDNSRecordFilterSet


class MemorystoreInstanceType(NetBoxObjectType):
    class Meta:
        model = models.MemorystoreInstance
        filterset_class = filtersets.MemorystoreInstanceFilterSet


class NCCHubType(NetBoxObjectType):
    class Meta:
        model = models.NCCHub
        filterset_class = filtersets.NCCHubFilterSet


class NCCSpokeType(NetBoxObjectType):
    class Meta:
        model = models.NCCSpoke
        filterset_class = filtersets.NCCSpokeFilterSet


class VPNGatewayType(NetBoxObjectType):
    class Meta:
        model = models.VPNGateway
        filterset_class = filtersets.VPNGatewayFilterSet


class ExternalVPNGatewayType(NetBoxObjectType):
    class Meta:
        model = models.ExternalVPNGateway
        filterset_class = filtersets.ExternalVPNGatewayFilterSet


class VPNTunnelType(NetBoxObjectType):
    class Meta:
        model = models.VPNTunnel
        filterset_class = filtersets.VPNTunnelFilterSet


class InterconnectAttachmentType(NetBoxObjectType):
    class Meta:
        model = models.InterconnectAttachment
        filterset_class = filtersets.InterconnectAttachmentFilterSet


class ServiceAttachmentType(NetBoxObjectType):
    class Meta:
        model = models.ServiceAttachment
        filterset_class = filtersets.ServiceAttachmentFilterSet


class ServiceConnectEndpointType(NetBoxObjectType):
    class Meta:
        model = models.ServiceConnectEndpoint
        filterset_class = filtersets.ServiceConnectEndpointFilterSet
