from rest_framework.routers import APIRootView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from netbox.api.viewsets import NetBoxModelViewSet
from gcp.models import (
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
from gcp import filtersets
from . import serializers


class GCPRootView(APIRootView):
    """
    GCP API root view
    """
    def get_view_name(self):
        return 'GCP'


class GCPOrganizationViewSet(NetBoxModelViewSet):
    queryset = GCPOrganization.objects.all()
    serializer_class = serializers.GCPOrganizationSerializer
    filterset_class = filtersets.GCPOrganizationFilterSet

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers.GCPOrganizationWriteSerializer
        return serializers.GCPOrganizationSerializer

    @action(detail=True, methods=['post'])
    def discover(self, request, pk=None):
        organization = self.get_object()
        
        if organization.discovery_status == 'running':
            return Response(
                {'error': 'Discovery is already running for this organization'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from gcp.discovery import run_discovery
        import threading
        
        thread = threading.Thread(target=run_discovery, args=(organization.pk,))
        thread.start()
        
        return Response(
            {'status': 'Discovery started', 'organization': organization.name},
            status=status.HTTP_202_ACCEPTED
        )


class DiscoveryLogViewSet(NetBoxModelViewSet):
    queryset = DiscoveryLog.objects.all()
    serializer_class = serializers.DiscoveryLogSerializer
    filterset_class = filtersets.DiscoveryLogFilterSet


class GCPProjectViewSet(NetBoxModelViewSet):
    queryset = GCPProject.objects.all()
    serializer_class = serializers.GCPProjectSerializer
    filterset_class = filtersets.GCPProjectFilterSet


class ComputeInstanceViewSet(NetBoxModelViewSet):
    queryset = ComputeInstance.objects.all()
    serializer_class = serializers.ComputeInstanceSerializer
    filterset_class = filtersets.ComputeInstanceFilterSet


class InstanceTemplateViewSet(NetBoxModelViewSet):
    queryset = InstanceTemplate.objects.all()
    serializer_class = serializers.InstanceTemplateSerializer
    filterset_class = filtersets.InstanceTemplateFilterSet


class InstanceGroupViewSet(NetBoxModelViewSet):
    queryset = InstanceGroup.objects.all()
    serializer_class = serializers.InstanceGroupSerializer
    filterset_class = filtersets.InstanceGroupFilterSet


class VPCNetworkViewSet(NetBoxModelViewSet):
    queryset = VPCNetwork.objects.all()
    serializer_class = serializers.VPCNetworkSerializer
    filterset_class = filtersets.VPCNetworkFilterSet


class SubnetViewSet(NetBoxModelViewSet):
    queryset = Subnet.objects.all()
    serializer_class = serializers.SubnetSerializer
    filterset_class = filtersets.SubnetFilterSet


class FirewallRuleViewSet(NetBoxModelViewSet):
    queryset = FirewallRule.objects.all()
    serializer_class = serializers.FirewallRuleSerializer
    filterset_class = filtersets.FirewallRuleFilterSet


class CloudRouterViewSet(NetBoxModelViewSet):
    queryset = CloudRouter.objects.all()
    serializer_class = serializers.CloudRouterSerializer
    filterset_class = filtersets.CloudRouterFilterSet


class CloudNATViewSet(NetBoxModelViewSet):
    queryset = CloudNAT.objects.all()
    serializer_class = serializers.CloudNATSerializer
    filterset_class = filtersets.CloudNATFilterSet


class LoadBalancerViewSet(NetBoxModelViewSet):
    queryset = LoadBalancer.objects.all()
    serializer_class = serializers.LoadBalancerSerializer
    filterset_class = filtersets.LoadBalancerFilterSet


class CloudSQLInstanceViewSet(NetBoxModelViewSet):
    queryset = CloudSQLInstance.objects.all()
    serializer_class = serializers.CloudSQLInstanceSerializer
    filterset_class = filtersets.CloudSQLInstanceFilterSet


class CloudSpannerInstanceViewSet(NetBoxModelViewSet):
    queryset = CloudSpannerInstance.objects.all()
    serializer_class = serializers.CloudSpannerInstanceSerializer
    filterset_class = filtersets.CloudSpannerInstanceFilterSet


class FirestoreDatabaseViewSet(NetBoxModelViewSet):
    queryset = FirestoreDatabase.objects.all()
    serializer_class = serializers.FirestoreDatabaseSerializer
    filterset_class = filtersets.FirestoreDatabaseFilterSet


class BigtableInstanceViewSet(NetBoxModelViewSet):
    queryset = BigtableInstance.objects.all()
    serializer_class = serializers.BigtableInstanceSerializer
    filterset_class = filtersets.BigtableInstanceFilterSet


class CloudStorageBucketViewSet(NetBoxModelViewSet):
    queryset = CloudStorageBucket.objects.all()
    serializer_class = serializers.CloudStorageBucketSerializer
    filterset_class = filtersets.CloudStorageBucketFilterSet


class PersistentDiskViewSet(NetBoxModelViewSet):
    queryset = PersistentDisk.objects.all()
    serializer_class = serializers.PersistentDiskSerializer
    filterset_class = filtersets.PersistentDiskFilterSet


class GKEClusterViewSet(NetBoxModelViewSet):
    queryset = GKECluster.objects.all()
    serializer_class = serializers.GKEClusterSerializer
    filterset_class = filtersets.GKEClusterFilterSet


class GKENodePoolViewSet(NetBoxModelViewSet):
    queryset = GKENodePool.objects.all()
    serializer_class = serializers.GKENodePoolSerializer
    filterset_class = filtersets.GKENodePoolFilterSet


class ServiceAccountViewSet(NetBoxModelViewSet):
    queryset = ServiceAccount.objects.all()
    serializer_class = serializers.ServiceAccountSerializer
    filterset_class = filtersets.ServiceAccountFilterSet


class IAMRoleViewSet(NetBoxModelViewSet):
    queryset = IAMRole.objects.all()
    serializer_class = serializers.IAMRoleSerializer
    filterset_class = filtersets.IAMRoleFilterSet


class IAMBindingViewSet(NetBoxModelViewSet):
    queryset = IAMBinding.objects.all()
    serializer_class = serializers.IAMBindingSerializer
    filterset_class = filtersets.IAMBindingFilterSet


class CloudFunctionViewSet(NetBoxModelViewSet):
    queryset = CloudFunction.objects.all()
    serializer_class = serializers.CloudFunctionSerializer
    filterset_class = filtersets.CloudFunctionFilterSet


class CloudRunViewSet(NetBoxModelViewSet):
    queryset = CloudRun.objects.all()
    serializer_class = serializers.CloudRunSerializer
    filterset_class = filtersets.CloudRunFilterSet


class PubSubTopicViewSet(NetBoxModelViewSet):
    queryset = PubSubTopic.objects.all()
    serializer_class = serializers.PubSubTopicSerializer
    filterset_class = filtersets.PubSubTopicFilterSet


class PubSubSubscriptionViewSet(NetBoxModelViewSet):
    queryset = PubSubSubscription.objects.all()
    serializer_class = serializers.PubSubSubscriptionSerializer
    filterset_class = filtersets.PubSubSubscriptionFilterSet


class SecretManagerSecretViewSet(NetBoxModelViewSet):
    queryset = SecretManagerSecret.objects.all()
    serializer_class = serializers.SecretManagerSecretSerializer
    filterset_class = filtersets.SecretManagerSecretFilterSet


class CloudDNSZoneViewSet(NetBoxModelViewSet):
    queryset = CloudDNSZone.objects.all()
    serializer_class = serializers.CloudDNSZoneSerializer
    filterset_class = filtersets.CloudDNSZoneFilterSet


class CloudDNSRecordViewSet(NetBoxModelViewSet):
    queryset = CloudDNSRecord.objects.all()
    serializer_class = serializers.CloudDNSRecordSerializer
    filterset_class = filtersets.CloudDNSRecordFilterSet


class MemorystoreInstanceViewSet(NetBoxModelViewSet):
    queryset = MemorystoreInstance.objects.all()
    serializer_class = serializers.MemorystoreInstanceSerializer
    filterset_class = filtersets.MemorystoreInstanceFilterSet


from gcp.models import NCCHub, NCCSpoke, VPNGateway, ExternalVPNGateway, VPNTunnel, InterconnectAttachment


class NCCHubViewSet(NetBoxModelViewSet):
    queryset = NCCHub.objects.all()
    serializer_class = serializers.NCCHubSerializer
    filterset_class = filtersets.NCCHubFilterSet


class NCCSpokeViewSet(NetBoxModelViewSet):
    queryset = NCCSpoke.objects.all()
    serializer_class = serializers.NCCSpokeSerializer
    filterset_class = filtersets.NCCSpokeFilterSet


class VPNGatewayViewSet(NetBoxModelViewSet):
    queryset = VPNGateway.objects.all()
    serializer_class = serializers.VPNGatewaySerializer
    filterset_class = filtersets.VPNGatewayFilterSet


class ExternalVPNGatewayViewSet(NetBoxModelViewSet):
    queryset = ExternalVPNGateway.objects.all()
    serializer_class = serializers.ExternalVPNGatewaySerializer
    filterset_class = filtersets.ExternalVPNGatewayFilterSet


class VPNTunnelViewSet(NetBoxModelViewSet):
    queryset = VPNTunnel.objects.all()
    serializer_class = serializers.VPNTunnelSerializer
    filterset_class = filtersets.VPNTunnelFilterSet


class InterconnectAttachmentViewSet(NetBoxModelViewSet):
    queryset = InterconnectAttachment.objects.all()
    serializer_class = serializers.InterconnectAttachmentSerializer
    filterset_class = filtersets.InterconnectAttachmentFilterSet
