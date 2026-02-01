from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from netbox.views import generic
from utilities.views import register_model_view
from . import filtersets, forms, tables
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
    NCCHub,
    NCCSpoke,
    VPNGateway,
    ExternalVPNGateway,
    VPNTunnel,
    InterconnectAttachment,
    ServiceAttachment,
    ServiceConnectEndpoint,
)


class GCPOrganizationListView(generic.ObjectListView):
    queryset = GCPOrganization.objects.all()
    table = tables.GCPOrganizationTable
    filterset = filtersets.GCPOrganizationFilterSet
    filterset_form = forms.GCPOrganizationFilterForm


@register_model_view(GCPOrganization)
class GCPOrganizationView(generic.ObjectView):
    queryset = GCPOrganization.objects.all()
    template_name = 'gcp/gcporganization.html'

    def get_extra_context(self, request, instance):
        discovery_logs = DiscoveryLog.objects.filter(organization=instance).order_by('-started_at')[:10]
        projects = GCPProject.objects.filter(organization=instance)
        return {
            'discovery_logs': discovery_logs,
            'projects': projects,
            'project_count': projects.count(),
        }


@register_model_view(GCPOrganization, 'edit')
class GCPOrganizationEditView(generic.ObjectEditView):
    queryset = GCPOrganization.objects.all()
    form = forms.GCPOrganizationForm


@register_model_view(GCPOrganization, 'delete')
class GCPOrganizationDeleteView(generic.ObjectDeleteView):
    queryset = GCPOrganization.objects.all()


class GCPOrganizationBulkDeleteView(generic.BulkDeleteView):
    queryset = GCPOrganization.objects.all()
    table = tables.GCPOrganizationTable


class GCPOrganizationDiscoverView(View):
    def post(self, request, pk):
        organization = get_object_or_404(GCPOrganization, pk=pk)

        if organization.discovery_status in ('running', 'canceling'):
            messages.warning(
                request,
                f'Discovery cannot be started while status is {organization.discovery_status} for {organization.name}',
            )
            return redirect('gcp:gcporganization', pk=pk)

        from .discovery import run_discovery
        import django_rq

        queue = django_rq.get_queue('default')
        queue.enqueue(run_discovery, organization.pk)

        messages.success(request, f'Discovery queued for {organization.name}. Refresh the page to see progress.')
        return redirect('gcp:gcporganization', pk=pk)


class GCPOrganizationCancelView(View):
    def post(self, request, pk):
        organization = get_object_or_404(GCPOrganization, pk=pk)

        if organization.discovery_status == 'canceling':
            messages.info(request, 'Cancellation is already in progress.')
            return redirect('gcp:gcporganization', pk=pk)

        if organization.discovery_status != 'running':
            messages.info(request, 'No running discovery to cancel.')
            return redirect('gcp:gcporganization', pk=pk)

        organization.cancel_requested = True
        organization.discovery_status = 'canceling'
        organization.save()

        messages.warning(request, f'Cancellation requested for {organization.name}.')
        return redirect('gcp:gcporganization', pk=pk)


class GCPOrganizationClearView(generic.ObjectDeleteView):
    queryset = GCPOrganization.objects.all()
    template_name = 'gcp/gcporganization_clear.html'

    def post(self, request, pk):
        organization = get_object_or_404(GCPOrganization, pk=pk)

        # Delete logs
        logs = DiscoveryLog.objects.filter(organization=organization)
        logs_count = logs.count()
        logs.delete()

        # Delete projects (cascades)
        projects = GCPProject.objects.filter(organization=organization)
        proj_count = projects.count()

        # Iterate and delete to avoid OOM on large datasets
        for project in projects:
            project.delete()

        # Reset org status
        organization.discovery_status = 'pending'
        organization.last_discovery = None
        organization.discovery_error = ''
        organization.save()

        messages.success(request, f'Cleared {proj_count} projects and {logs_count} logs for {organization.name}.')
        return redirect('gcp:gcporganization', pk=pk)


class DiscoveryLogListView(generic.ObjectListView):
    queryset = DiscoveryLog.objects.all()
    table = tables.DiscoveryLogTable
    filterset = filtersets.DiscoveryLogFilterSet


@register_model_view(DiscoveryLog)
class DiscoveryLogView(generic.ObjectView):
    queryset = DiscoveryLog.objects.all()


@register_model_view(DiscoveryLog, 'delete')
class DiscoveryLogDeleteView(generic.ObjectDeleteView):
    queryset = DiscoveryLog.objects.all()


class DiscoveryLogBulkDeleteView(generic.BulkDeleteView):
    queryset = DiscoveryLog.objects.all()
    table = tables.DiscoveryLogTable


class GCPProjectListView(generic.ObjectListView):
    queryset = GCPProject.objects.all()
    table = tables.GCPProjectTable
    filterset = filtersets.GCPProjectFilterSet
    filterset_form = forms.GCPProjectFilterForm


@register_model_view(GCPProject)
class GCPProjectView(generic.ObjectView):
    queryset = GCPProject.objects.all()


@register_model_view(GCPProject, 'edit')
class GCPProjectEditView(generic.ObjectEditView):
    queryset = GCPProject.objects.all()
    form = forms.GCPProjectForm


@register_model_view(GCPProject, 'delete')
class GCPProjectDeleteView(generic.ObjectDeleteView):
    queryset = GCPProject.objects.all()


class GCPProjectBulkImportView(generic.BulkImportView):
    queryset = GCPProject.objects.all()
    model_form = forms.GCPProjectForm


class GCPProjectBulkDeleteView(generic.BulkDeleteView):
    queryset = GCPProject.objects.all()
    table = tables.GCPProjectTable


class ComputeInstanceListView(generic.ObjectListView):
    queryset = ComputeInstance.objects.all()
    table = tables.ComputeInstanceTable
    filterset = filtersets.ComputeInstanceFilterSet
    filterset_form = forms.ComputeInstanceFilterForm


@register_model_view(ComputeInstance)
class ComputeInstanceView(generic.ObjectView):
    queryset = ComputeInstance.objects.all()


@register_model_view(ComputeInstance, 'edit')
class ComputeInstanceEditView(generic.ObjectEditView):
    queryset = ComputeInstance.objects.all()
    form = forms.ComputeInstanceForm


@register_model_view(ComputeInstance, 'delete')
class ComputeInstanceDeleteView(generic.ObjectDeleteView):
    queryset = ComputeInstance.objects.all()


class ComputeInstanceBulkImportView(generic.BulkImportView):
    queryset = ComputeInstance.objects.all()
    model_form = forms.ComputeInstanceForm


class ComputeInstanceBulkDeleteView(generic.BulkDeleteView):
    queryset = ComputeInstance.objects.all()
    table = tables.ComputeInstanceTable


class InstanceTemplateListView(generic.ObjectListView):
    queryset = InstanceTemplate.objects.all()
    table = tables.InstanceTemplateTable
    filterset = filtersets.InstanceTemplateFilterSet


@register_model_view(InstanceTemplate)
class InstanceTemplateView(generic.ObjectView):
    queryset = InstanceTemplate.objects.all()


@register_model_view(InstanceTemplate, 'edit')
class InstanceTemplateEditView(generic.ObjectEditView):
    queryset = InstanceTemplate.objects.all()
    form = forms.InstanceTemplateForm


@register_model_view(InstanceTemplate, 'delete')
class InstanceTemplateDeleteView(generic.ObjectDeleteView):
    queryset = InstanceTemplate.objects.all()


class InstanceTemplateBulkImportView(generic.BulkImportView):
    queryset = InstanceTemplate.objects.all()
    model_form = forms.InstanceTemplateForm


class InstanceTemplateBulkDeleteView(generic.BulkDeleteView):
    queryset = InstanceTemplate.objects.all()
    table = tables.InstanceTemplateTable


class InstanceGroupListView(generic.ObjectListView):
    queryset = InstanceGroup.objects.all()
    table = tables.InstanceGroupTable
    filterset = filtersets.InstanceGroupFilterSet


@register_model_view(InstanceGroup)
class InstanceGroupView(generic.ObjectView):
    queryset = InstanceGroup.objects.all()


@register_model_view(InstanceGroup, 'edit')
class InstanceGroupEditView(generic.ObjectEditView):
    queryset = InstanceGroup.objects.all()
    form = forms.InstanceGroupForm


@register_model_view(InstanceGroup, 'delete')
class InstanceGroupDeleteView(generic.ObjectDeleteView):
    queryset = InstanceGroup.objects.all()


class InstanceGroupBulkImportView(generic.BulkImportView):
    queryset = InstanceGroup.objects.all()
    model_form = forms.InstanceGroupForm


class InstanceGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = InstanceGroup.objects.all()
    table = tables.InstanceGroupTable


class VPCNetworkListView(generic.ObjectListView):
    queryset = VPCNetwork.objects.all()
    table = tables.VPCNetworkTable
    filterset = filtersets.VPCNetworkFilterSet
    filterset_form = forms.VPCNetworkFilterForm


@register_model_view(VPCNetwork)
class VPCNetworkView(generic.ObjectView):
    queryset = VPCNetwork.objects.all()


@register_model_view(VPCNetwork, 'edit')
class VPCNetworkEditView(generic.ObjectEditView):
    queryset = VPCNetwork.objects.all()
    form = forms.VPCNetworkForm


@register_model_view(VPCNetwork, 'delete')
class VPCNetworkDeleteView(generic.ObjectDeleteView):
    queryset = VPCNetwork.objects.all()


class VPCNetworkBulkImportView(generic.BulkImportView):
    queryset = VPCNetwork.objects.all()
    model_form = forms.VPCNetworkForm


class VPCNetworkBulkDeleteView(generic.BulkDeleteView):
    queryset = VPCNetwork.objects.all()
    table = tables.VPCNetworkTable


class SubnetListView(generic.ObjectListView):
    queryset = Subnet.objects.all()
    table = tables.SubnetTable
    filterset = filtersets.SubnetFilterSet
    filterset_form = forms.SubnetFilterForm


@register_model_view(Subnet)
class SubnetView(generic.ObjectView):
    queryset = Subnet.objects.all()


@register_model_view(Subnet, 'edit')
class SubnetEditView(generic.ObjectEditView):
    queryset = Subnet.objects.all()
    form = forms.SubnetForm


@register_model_view(Subnet, 'delete')
class SubnetDeleteView(generic.ObjectDeleteView):
    queryset = Subnet.objects.all()


class SubnetBulkImportView(generic.BulkImportView):
    queryset = Subnet.objects.all()
    model_form = forms.SubnetForm


class SubnetBulkDeleteView(generic.BulkDeleteView):
    queryset = Subnet.objects.all()
    table = tables.SubnetTable


class FirewallRuleListView(generic.ObjectListView):
    queryset = FirewallRule.objects.all()
    table = tables.FirewallRuleTable
    filterset = filtersets.FirewallRuleFilterSet


@register_model_view(FirewallRule)
class FirewallRuleView(generic.ObjectView):
    queryset = FirewallRule.objects.all()


@register_model_view(FirewallRule, 'edit')
class FirewallRuleEditView(generic.ObjectEditView):
    queryset = FirewallRule.objects.all()
    form = forms.FirewallRuleForm


@register_model_view(FirewallRule, 'delete')
class FirewallRuleDeleteView(generic.ObjectDeleteView):
    queryset = FirewallRule.objects.all()


class FirewallRuleBulkImportView(generic.BulkImportView):
    queryset = FirewallRule.objects.all()
    model_form = forms.FirewallRuleForm


class FirewallRuleBulkDeleteView(generic.BulkDeleteView):
    queryset = FirewallRule.objects.all()
    table = tables.FirewallRuleTable


class CloudRouterListView(generic.ObjectListView):
    queryset = CloudRouter.objects.all()
    table = tables.CloudRouterTable
    filterset = filtersets.CloudRouterFilterSet


@register_model_view(CloudRouter)
class CloudRouterView(generic.ObjectView):
    queryset = CloudRouter.objects.all()


@register_model_view(CloudRouter, 'edit')
class CloudRouterEditView(generic.ObjectEditView):
    queryset = CloudRouter.objects.all()
    form = forms.CloudRouterForm


@register_model_view(CloudRouter, 'delete')
class CloudRouterDeleteView(generic.ObjectDeleteView):
    queryset = CloudRouter.objects.all()


class CloudRouterBulkImportView(generic.BulkImportView):
    queryset = CloudRouter.objects.all()
    model_form = forms.CloudRouterForm


class CloudRouterBulkDeleteView(generic.BulkDeleteView):
    queryset = CloudRouter.objects.all()
    table = tables.CloudRouterTable


class CloudNATListView(generic.ObjectListView):
    queryset = CloudNAT.objects.all()
    table = tables.CloudNATTable
    filterset = filtersets.CloudNATFilterSet


@register_model_view(CloudNAT)
class CloudNATView(generic.ObjectView):
    queryset = CloudNAT.objects.all()


@register_model_view(CloudNAT, 'edit')
class CloudNATEditView(generic.ObjectEditView):
    queryset = CloudNAT.objects.all()
    form = forms.CloudNATForm


@register_model_view(CloudNAT, 'delete')
class CloudNATDeleteView(generic.ObjectDeleteView):
    queryset = CloudNAT.objects.all()


class CloudNATBulkImportView(generic.BulkImportView):
    queryset = CloudNAT.objects.all()
    model_form = forms.CloudNATForm


class CloudNATBulkDeleteView(generic.BulkDeleteView):
    queryset = CloudNAT.objects.all()
    table = tables.CloudNATTable


class LoadBalancerListView(generic.ObjectListView):
    queryset = LoadBalancer.objects.all()
    table = tables.LoadBalancerTable
    filterset = filtersets.LoadBalancerFilterSet


@register_model_view(LoadBalancer)
class LoadBalancerView(generic.ObjectView):
    queryset = LoadBalancer.objects.all()


@register_model_view(LoadBalancer, 'edit')
class LoadBalancerEditView(generic.ObjectEditView):
    queryset = LoadBalancer.objects.all()
    form = forms.LoadBalancerForm


@register_model_view(LoadBalancer, 'delete')
class LoadBalancerDeleteView(generic.ObjectDeleteView):
    queryset = LoadBalancer.objects.all()


class LoadBalancerBulkImportView(generic.BulkImportView):
    queryset = LoadBalancer.objects.all()
    model_form = forms.LoadBalancerForm


class LoadBalancerBulkDeleteView(generic.BulkDeleteView):
    queryset = LoadBalancer.objects.all()
    table = tables.LoadBalancerTable


class CloudSQLInstanceListView(generic.ObjectListView):
    queryset = CloudSQLInstance.objects.all()
    table = tables.CloudSQLInstanceTable
    filterset = filtersets.CloudSQLInstanceFilterSet
    filterset_form = forms.CloudSQLInstanceFilterForm


@register_model_view(CloudSQLInstance)
class CloudSQLInstanceView(generic.ObjectView):
    queryset = CloudSQLInstance.objects.all()


@register_model_view(CloudSQLInstance, 'edit')
class CloudSQLInstanceEditView(generic.ObjectEditView):
    queryset = CloudSQLInstance.objects.all()
    form = forms.CloudSQLInstanceForm


@register_model_view(CloudSQLInstance, 'delete')
class CloudSQLInstanceDeleteView(generic.ObjectDeleteView):
    queryset = CloudSQLInstance.objects.all()


class CloudSQLInstanceBulkImportView(generic.BulkImportView):
    queryset = CloudSQLInstance.objects.all()
    model_form = forms.CloudSQLInstanceForm


class CloudSQLInstanceBulkDeleteView(generic.BulkDeleteView):
    queryset = CloudSQLInstance.objects.all()
    table = tables.CloudSQLInstanceTable


class CloudSpannerInstanceListView(generic.ObjectListView):
    queryset = CloudSpannerInstance.objects.all()
    table = tables.CloudSpannerInstanceTable
    filterset = filtersets.CloudSpannerInstanceFilterSet


@register_model_view(CloudSpannerInstance)
class CloudSpannerInstanceView(generic.ObjectView):
    queryset = CloudSpannerInstance.objects.all()


@register_model_view(CloudSpannerInstance, 'edit')
class CloudSpannerInstanceEditView(generic.ObjectEditView):
    queryset = CloudSpannerInstance.objects.all()
    form = forms.CloudSpannerInstanceForm


@register_model_view(CloudSpannerInstance, 'delete')
class CloudSpannerInstanceDeleteView(generic.ObjectDeleteView):
    queryset = CloudSpannerInstance.objects.all()


class CloudSpannerInstanceBulkImportView(generic.BulkImportView):
    queryset = CloudSpannerInstance.objects.all()
    model_form = forms.CloudSpannerInstanceForm


class CloudSpannerInstanceBulkDeleteView(generic.BulkDeleteView):
    queryset = CloudSpannerInstance.objects.all()
    table = tables.CloudSpannerInstanceTable


class FirestoreDatabaseListView(generic.ObjectListView):
    queryset = FirestoreDatabase.objects.all()
    table = tables.FirestoreDatabaseTable
    filterset = filtersets.FirestoreDatabaseFilterSet


@register_model_view(FirestoreDatabase)
class FirestoreDatabaseView(generic.ObjectView):
    queryset = FirestoreDatabase.objects.all()


@register_model_view(FirestoreDatabase, 'edit')
class FirestoreDatabaseEditView(generic.ObjectEditView):
    queryset = FirestoreDatabase.objects.all()
    form = forms.FirestoreDatabaseForm


@register_model_view(FirestoreDatabase, 'delete')
class FirestoreDatabaseDeleteView(generic.ObjectDeleteView):
    queryset = FirestoreDatabase.objects.all()


class FirestoreDatabaseBulkImportView(generic.BulkImportView):
    queryset = FirestoreDatabase.objects.all()
    model_form = forms.FirestoreDatabaseForm


class FirestoreDatabaseBulkDeleteView(generic.BulkDeleteView):
    queryset = FirestoreDatabase.objects.all()
    table = tables.FirestoreDatabaseTable


class BigtableInstanceListView(generic.ObjectListView):
    queryset = BigtableInstance.objects.all()
    table = tables.BigtableInstanceTable
    filterset = filtersets.BigtableInstanceFilterSet


@register_model_view(BigtableInstance)
class BigtableInstanceView(generic.ObjectView):
    queryset = BigtableInstance.objects.all()


@register_model_view(BigtableInstance, 'edit')
class BigtableInstanceEditView(generic.ObjectEditView):
    queryset = BigtableInstance.objects.all()
    form = forms.BigtableInstanceForm


@register_model_view(BigtableInstance, 'delete')
class BigtableInstanceDeleteView(generic.ObjectDeleteView):
    queryset = BigtableInstance.objects.all()


class BigtableInstanceBulkImportView(generic.BulkImportView):
    queryset = BigtableInstance.objects.all()
    model_form = forms.BigtableInstanceForm


class BigtableInstanceBulkDeleteView(generic.BulkDeleteView):
    queryset = BigtableInstance.objects.all()
    table = tables.BigtableInstanceTable


class CloudStorageBucketListView(generic.ObjectListView):
    queryset = CloudStorageBucket.objects.all()
    table = tables.CloudStorageBucketTable
    filterset = filtersets.CloudStorageBucketFilterSet
    filterset_form = forms.CloudStorageBucketFilterForm


@register_model_view(CloudStorageBucket)
class CloudStorageBucketView(generic.ObjectView):
    queryset = CloudStorageBucket.objects.all()


@register_model_view(CloudStorageBucket, 'edit')
class CloudStorageBucketEditView(generic.ObjectEditView):
    queryset = CloudStorageBucket.objects.all()
    form = forms.CloudStorageBucketForm


@register_model_view(CloudStorageBucket, 'delete')
class CloudStorageBucketDeleteView(generic.ObjectDeleteView):
    queryset = CloudStorageBucket.objects.all()


class CloudStorageBucketBulkImportView(generic.BulkImportView):
    queryset = CloudStorageBucket.objects.all()
    model_form = forms.CloudStorageBucketForm


class CloudStorageBucketBulkDeleteView(generic.BulkDeleteView):
    queryset = CloudStorageBucket.objects.all()
    table = tables.CloudStorageBucketTable


class PersistentDiskListView(generic.ObjectListView):
    queryset = PersistentDisk.objects.all()
    table = tables.PersistentDiskTable
    filterset = filtersets.PersistentDiskFilterSet


@register_model_view(PersistentDisk)
class PersistentDiskView(generic.ObjectView):
    queryset = PersistentDisk.objects.all()


@register_model_view(PersistentDisk, 'edit')
class PersistentDiskEditView(generic.ObjectEditView):
    queryset = PersistentDisk.objects.all()
    form = forms.PersistentDiskForm


@register_model_view(PersistentDisk, 'delete')
class PersistentDiskDeleteView(generic.ObjectDeleteView):
    queryset = PersistentDisk.objects.all()


class PersistentDiskBulkImportView(generic.BulkImportView):
    queryset = PersistentDisk.objects.all()
    model_form = forms.PersistentDiskForm


class PersistentDiskBulkDeleteView(generic.BulkDeleteView):
    queryset = PersistentDisk.objects.all()
    table = tables.PersistentDiskTable


class GKEClusterListView(generic.ObjectListView):
    queryset = GKECluster.objects.all()
    table = tables.GKEClusterTable
    filterset = filtersets.GKEClusterFilterSet
    filterset_form = forms.GKEClusterFilterForm


@register_model_view(GKECluster)
class GKEClusterView(generic.ObjectView):
    queryset = GKECluster.objects.all()


@register_model_view(GKECluster, 'edit')
class GKEClusterEditView(generic.ObjectEditView):
    queryset = GKECluster.objects.all()
    form = forms.GKEClusterForm


@register_model_view(GKECluster, 'delete')
class GKEClusterDeleteView(generic.ObjectDeleteView):
    queryset = GKECluster.objects.all()


class GKEClusterBulkImportView(generic.BulkImportView):
    queryset = GKECluster.objects.all()
    model_form = forms.GKEClusterForm


class GKEClusterBulkDeleteView(generic.BulkDeleteView):
    queryset = GKECluster.objects.all()
    table = tables.GKEClusterTable


class GKENodePoolListView(generic.ObjectListView):
    queryset = GKENodePool.objects.all()
    table = tables.GKENodePoolTable
    filterset = filtersets.GKENodePoolFilterSet


@register_model_view(GKENodePool)
class GKENodePoolView(generic.ObjectView):
    queryset = GKENodePool.objects.all()


@register_model_view(GKENodePool, 'edit')
class GKENodePoolEditView(generic.ObjectEditView):
    queryset = GKENodePool.objects.all()
    form = forms.GKENodePoolForm


@register_model_view(GKENodePool, 'delete')
class GKENodePoolDeleteView(generic.ObjectDeleteView):
    queryset = GKENodePool.objects.all()


class GKENodePoolBulkImportView(generic.BulkImportView):
    queryset = GKENodePool.objects.all()
    model_form = forms.GKENodePoolForm


class GKENodePoolBulkDeleteView(generic.BulkDeleteView):
    queryset = GKENodePool.objects.all()
    table = tables.GKENodePoolTable


class ServiceAccountListView(generic.ObjectListView):
    queryset = ServiceAccount.objects.all()
    table = tables.ServiceAccountTable
    filterset = filtersets.ServiceAccountFilterSet
    filterset_form = forms.ServiceAccountFilterForm


@register_model_view(ServiceAccount)
class ServiceAccountView(generic.ObjectView):
    queryset = ServiceAccount.objects.all()


@register_model_view(ServiceAccount, 'edit')
class ServiceAccountEditView(generic.ObjectEditView):
    queryset = ServiceAccount.objects.all()
    form = forms.ServiceAccountForm


@register_model_view(ServiceAccount, 'delete')
class ServiceAccountDeleteView(generic.ObjectDeleteView):
    queryset = ServiceAccount.objects.all()


class ServiceAccountBulkImportView(generic.BulkImportView):
    queryset = ServiceAccount.objects.all()
    model_form = forms.ServiceAccountForm


class ServiceAccountBulkDeleteView(generic.BulkDeleteView):
    queryset = ServiceAccount.objects.all()
    table = tables.ServiceAccountTable


class IAMRoleListView(generic.ObjectListView):
    queryset = IAMRole.objects.all()
    table = tables.IAMRoleTable
    filterset = filtersets.IAMRoleFilterSet


@register_model_view(IAMRole)
class IAMRoleView(generic.ObjectView):
    queryset = IAMRole.objects.all()


@register_model_view(IAMRole, 'edit')
class IAMRoleEditView(generic.ObjectEditView):
    queryset = IAMRole.objects.all()
    form = forms.IAMRoleForm


@register_model_view(IAMRole, 'delete')
class IAMRoleDeleteView(generic.ObjectDeleteView):
    queryset = IAMRole.objects.all()


class IAMRoleBulkImportView(generic.BulkImportView):
    queryset = IAMRole.objects.all()
    model_form = forms.IAMRoleForm


class IAMRoleBulkDeleteView(generic.BulkDeleteView):
    queryset = IAMRole.objects.all()
    table = tables.IAMRoleTable


class IAMBindingListView(generic.ObjectListView):
    queryset = IAMBinding.objects.all()
    table = tables.IAMBindingTable
    filterset = filtersets.IAMBindingFilterSet


@register_model_view(IAMBinding)
class IAMBindingView(generic.ObjectView):
    queryset = IAMBinding.objects.all()


@register_model_view(IAMBinding, 'edit')
class IAMBindingEditView(generic.ObjectEditView):
    queryset = IAMBinding.objects.all()
    form = forms.IAMBindingForm


@register_model_view(IAMBinding, 'delete')
class IAMBindingDeleteView(generic.ObjectDeleteView):
    queryset = IAMBinding.objects.all()


class IAMBindingBulkImportView(generic.BulkImportView):
    queryset = IAMBinding.objects.all()
    model_form = forms.IAMBindingForm


class IAMBindingBulkDeleteView(generic.BulkDeleteView):
    queryset = IAMBinding.objects.all()
    table = tables.IAMBindingTable


class CloudFunctionListView(generic.ObjectListView):
    queryset = CloudFunction.objects.all()
    table = tables.CloudFunctionTable
    filterset = filtersets.CloudFunctionFilterSet


@register_model_view(CloudFunction)
class CloudFunctionView(generic.ObjectView):
    queryset = CloudFunction.objects.all()


@register_model_view(CloudFunction, 'edit')
class CloudFunctionEditView(generic.ObjectEditView):
    queryset = CloudFunction.objects.all()
    form = forms.CloudFunctionForm


@register_model_view(CloudFunction, 'delete')
class CloudFunctionDeleteView(generic.ObjectDeleteView):
    queryset = CloudFunction.objects.all()


class CloudFunctionBulkImportView(generic.BulkImportView):
    queryset = CloudFunction.objects.all()
    model_form = forms.CloudFunctionForm


class CloudFunctionBulkDeleteView(generic.BulkDeleteView):
    queryset = CloudFunction.objects.all()
    table = tables.CloudFunctionTable


class CloudRunListView(generic.ObjectListView):
    queryset = CloudRun.objects.all()
    table = tables.CloudRunTable
    filterset = filtersets.CloudRunFilterSet


@register_model_view(CloudRun)
class CloudRunView(generic.ObjectView):
    queryset = CloudRun.objects.all()


@register_model_view(CloudRun, 'edit')
class CloudRunEditView(generic.ObjectEditView):
    queryset = CloudRun.objects.all()
    form = forms.CloudRunForm


@register_model_view(CloudRun, 'delete')
class CloudRunDeleteView(generic.ObjectDeleteView):
    queryset = CloudRun.objects.all()


class CloudRunBulkImportView(generic.BulkImportView):
    queryset = CloudRun.objects.all()
    model_form = forms.CloudRunForm


class CloudRunBulkDeleteView(generic.BulkDeleteView):
    queryset = CloudRun.objects.all()
    table = tables.CloudRunTable


class PubSubTopicListView(generic.ObjectListView):
    queryset = PubSubTopic.objects.all()
    table = tables.PubSubTopicTable
    filterset = filtersets.PubSubTopicFilterSet


@register_model_view(PubSubTopic)
class PubSubTopicView(generic.ObjectView):
    queryset = PubSubTopic.objects.all()


@register_model_view(PubSubTopic, 'edit')
class PubSubTopicEditView(generic.ObjectEditView):
    queryset = PubSubTopic.objects.all()
    form = forms.PubSubTopicForm


@register_model_view(PubSubTopic, 'delete')
class PubSubTopicDeleteView(generic.ObjectDeleteView):
    queryset = PubSubTopic.objects.all()


class PubSubTopicBulkImportView(generic.BulkImportView):
    queryset = PubSubTopic.objects.all()
    model_form = forms.PubSubTopicForm


class PubSubTopicBulkDeleteView(generic.BulkDeleteView):
    queryset = PubSubTopic.objects.all()
    table = tables.PubSubTopicTable


class PubSubSubscriptionListView(generic.ObjectListView):
    queryset = PubSubSubscription.objects.all()
    table = tables.PubSubSubscriptionTable
    filterset = filtersets.PubSubSubscriptionFilterSet


@register_model_view(PubSubSubscription)
class PubSubSubscriptionView(generic.ObjectView):
    queryset = PubSubSubscription.objects.all()


@register_model_view(PubSubSubscription, 'edit')
class PubSubSubscriptionEditView(generic.ObjectEditView):
    queryset = PubSubSubscription.objects.all()
    form = forms.PubSubSubscriptionForm


@register_model_view(PubSubSubscription, 'delete')
class PubSubSubscriptionDeleteView(generic.ObjectDeleteView):
    queryset = PubSubSubscription.objects.all()


class PubSubSubscriptionBulkImportView(generic.BulkImportView):
    queryset = PubSubSubscription.objects.all()
    model_form = forms.PubSubSubscriptionForm


class PubSubSubscriptionBulkDeleteView(generic.BulkDeleteView):
    queryset = PubSubSubscription.objects.all()
    table = tables.PubSubSubscriptionTable


class SecretManagerSecretListView(generic.ObjectListView):
    queryset = SecretManagerSecret.objects.all()
    table = tables.SecretManagerSecretTable
    filterset = filtersets.SecretManagerSecretFilterSet


@register_model_view(SecretManagerSecret)
class SecretManagerSecretView(generic.ObjectView):
    queryset = SecretManagerSecret.objects.all()


@register_model_view(SecretManagerSecret, 'edit')
class SecretManagerSecretEditView(generic.ObjectEditView):
    queryset = SecretManagerSecret.objects.all()
    form = forms.SecretManagerSecretForm


@register_model_view(SecretManagerSecret, 'delete')
class SecretManagerSecretDeleteView(generic.ObjectDeleteView):
    queryset = SecretManagerSecret.objects.all()


class SecretManagerSecretBulkImportView(generic.BulkImportView):
    queryset = SecretManagerSecret.objects.all()
    model_form = forms.SecretManagerSecretForm


class SecretManagerSecretBulkDeleteView(generic.BulkDeleteView):
    queryset = SecretManagerSecret.objects.all()
    table = tables.SecretManagerSecretTable


class CloudDNSZoneListView(generic.ObjectListView):
    queryset = CloudDNSZone.objects.all()
    table = tables.CloudDNSZoneTable
    filterset = filtersets.CloudDNSZoneFilterSet


@register_model_view(CloudDNSZone)
class CloudDNSZoneView(generic.ObjectView):
    queryset = CloudDNSZone.objects.all()


@register_model_view(CloudDNSZone, 'edit')
class CloudDNSZoneEditView(generic.ObjectEditView):
    queryset = CloudDNSZone.objects.all()
    form = forms.CloudDNSZoneForm


@register_model_view(CloudDNSZone, 'delete')
class CloudDNSZoneDeleteView(generic.ObjectDeleteView):
    queryset = CloudDNSZone.objects.all()


class CloudDNSZoneBulkImportView(generic.BulkImportView):
    queryset = CloudDNSZone.objects.all()
    model_form = forms.CloudDNSZoneForm


class CloudDNSZoneBulkDeleteView(generic.BulkDeleteView):
    queryset = CloudDNSZone.objects.all()
    table = tables.CloudDNSZoneTable


class CloudDNSRecordListView(generic.ObjectListView):
    queryset = CloudDNSRecord.objects.all()
    table = tables.CloudDNSRecordTable
    filterset = filtersets.CloudDNSRecordFilterSet


@register_model_view(CloudDNSRecord)
class CloudDNSRecordView(generic.ObjectView):
    queryset = CloudDNSRecord.objects.all()


@register_model_view(CloudDNSRecord, 'edit')
class CloudDNSRecordEditView(generic.ObjectEditView):
    queryset = CloudDNSRecord.objects.all()
    form = forms.CloudDNSRecordForm


@register_model_view(CloudDNSRecord, 'delete')
class CloudDNSRecordDeleteView(generic.ObjectDeleteView):
    queryset = CloudDNSRecord.objects.all()


class CloudDNSRecordBulkImportView(generic.BulkImportView):
    queryset = CloudDNSRecord.objects.all()
    model_form = forms.CloudDNSRecordForm


class CloudDNSRecordBulkDeleteView(generic.BulkDeleteView):
    queryset = CloudDNSRecord.objects.all()
    table = tables.CloudDNSRecordTable


class MemorystoreInstanceListView(generic.ObjectListView):
    queryset = MemorystoreInstance.objects.all()
    table = tables.MemorystoreInstanceTable
    filterset = filtersets.MemorystoreInstanceFilterSet


@register_model_view(MemorystoreInstance)
class MemorystoreInstanceView(generic.ObjectView):
    queryset = MemorystoreInstance.objects.all()


@register_model_view(MemorystoreInstance, 'edit')
class MemorystoreInstanceEditView(generic.ObjectEditView):
    queryset = MemorystoreInstance.objects.all()
    form = forms.MemorystoreInstanceForm


@register_model_view(MemorystoreInstance, 'delete')
class MemorystoreInstanceDeleteView(generic.ObjectDeleteView):
    queryset = MemorystoreInstance.objects.all()


class MemorystoreInstanceBulkImportView(generic.BulkImportView):
    queryset = MemorystoreInstance.objects.all()
    model_form = forms.MemorystoreInstanceForm


class MemorystoreInstanceBulkDeleteView(generic.BulkDeleteView):
    queryset = MemorystoreInstance.objects.all()
    table = tables.MemorystoreInstanceTable


class NCCHubListView(generic.ObjectListView):
    queryset = NCCHub.objects.all()
    table = tables.NCCHubTable
    filterset = filtersets.NCCHubFilterSet


@register_model_view(NCCHub)
class NCCHubView(generic.ObjectView):
    queryset = NCCHub.objects.all()


@register_model_view(NCCHub, 'edit')
class NCCHubEditView(generic.ObjectEditView):
    queryset = NCCHub.objects.all()
    form = forms.NCCHubForm


@register_model_view(NCCHub, 'delete')
class NCCHubDeleteView(generic.ObjectDeleteView):
    queryset = NCCHub.objects.all()


class NCCHubBulkImportView(generic.BulkImportView):
    queryset = NCCHub.objects.all()
    model_form = forms.NCCHubForm


class NCCHubBulkDeleteView(generic.BulkDeleteView):
    queryset = NCCHub.objects.all()
    table = tables.NCCHubTable


class NCCSpokeListView(generic.ObjectListView):
    queryset = NCCSpoke.objects.all()
    table = tables.NCCSpokeTable
    filterset = filtersets.NCCSpokeFilterSet


@register_model_view(NCCSpoke)
class NCCSpokeView(generic.ObjectView):
    queryset = NCCSpoke.objects.all()


@register_model_view(NCCSpoke, 'edit')
class NCCSpokeEditView(generic.ObjectEditView):
    queryset = NCCSpoke.objects.all()
    form = forms.NCCSpokeForm


@register_model_view(NCCSpoke, 'delete')
class NCCSpokeDeleteView(generic.ObjectDeleteView):
    queryset = NCCSpoke.objects.all()


class NCCSpokeBulkImportView(generic.BulkImportView):
    queryset = NCCSpoke.objects.all()
    model_form = forms.NCCSpokeForm


class NCCSpokeBulkDeleteView(generic.BulkDeleteView):
    queryset = NCCSpoke.objects.all()
    table = tables.NCCSpokeTable


class VPNGatewayListView(generic.ObjectListView):
    queryset = VPNGateway.objects.all()
    table = tables.VPNGatewayTable
    filterset = filtersets.VPNGatewayFilterSet


@register_model_view(VPNGateway)
class VPNGatewayView(generic.ObjectView):
    queryset = VPNGateway.objects.all()


@register_model_view(VPNGateway, 'edit')
class VPNGatewayEditView(generic.ObjectEditView):
    queryset = VPNGateway.objects.all()
    form = forms.VPNGatewayForm


@register_model_view(VPNGateway, 'delete')
class VPNGatewayDeleteView(generic.ObjectDeleteView):
    queryset = VPNGateway.objects.all()


class VPNGatewayBulkImportView(generic.BulkImportView):
    queryset = VPNGateway.objects.all()
    model_form = forms.VPNGatewayForm


class VPNGatewayBulkDeleteView(generic.BulkDeleteView):
    queryset = VPNGateway.objects.all()
    table = tables.VPNGatewayTable


class ExternalVPNGatewayListView(generic.ObjectListView):
    queryset = ExternalVPNGateway.objects.all()
    table = tables.ExternalVPNGatewayTable
    filterset = filtersets.ExternalVPNGatewayFilterSet


@register_model_view(ExternalVPNGateway)
class ExternalVPNGatewayView(generic.ObjectView):
    queryset = ExternalVPNGateway.objects.all()


@register_model_view(ExternalVPNGateway, 'edit')
class ExternalVPNGatewayEditView(generic.ObjectEditView):
    queryset = ExternalVPNGateway.objects.all()
    form = forms.ExternalVPNGatewayForm


@register_model_view(ExternalVPNGateway, 'delete')
class ExternalVPNGatewayDeleteView(generic.ObjectDeleteView):
    queryset = ExternalVPNGateway.objects.all()


class ExternalVPNGatewayBulkImportView(generic.BulkImportView):
    queryset = ExternalVPNGateway.objects.all()
    model_form = forms.ExternalVPNGatewayForm


class ExternalVPNGatewayBulkDeleteView(generic.BulkDeleteView):
    queryset = ExternalVPNGateway.objects.all()
    table = tables.ExternalVPNGatewayTable


class VPNTunnelListView(generic.ObjectListView):
    queryset = VPNTunnel.objects.all()
    table = tables.VPNTunnelTable
    filterset = filtersets.VPNTunnelFilterSet


@register_model_view(VPNTunnel)
class VPNTunnelView(generic.ObjectView):
    queryset = VPNTunnel.objects.all()


@register_model_view(VPNTunnel, 'edit')
class VPNTunnelEditView(generic.ObjectEditView):
    queryset = VPNTunnel.objects.all()
    form = forms.VPNTunnelForm


@register_model_view(VPNTunnel, 'delete')
class VPNTunnelDeleteView(generic.ObjectDeleteView):
    queryset = VPNTunnel.objects.all()


class VPNTunnelBulkImportView(generic.BulkImportView):
    queryset = VPNTunnel.objects.all()
    model_form = forms.VPNTunnelForm


class VPNTunnelBulkDeleteView(generic.BulkDeleteView):
    queryset = VPNTunnel.objects.all()
    table = tables.VPNTunnelTable


class InterconnectAttachmentListView(generic.ObjectListView):
    queryset = InterconnectAttachment.objects.all()
    table = tables.InterconnectAttachmentTable
    filterset = filtersets.InterconnectAttachmentFilterSet


@register_model_view(InterconnectAttachment)
class InterconnectAttachmentView(generic.ObjectView):
    queryset = InterconnectAttachment.objects.all()


@register_model_view(InterconnectAttachment, 'edit')
class InterconnectAttachmentEditView(generic.ObjectEditView):
    queryset = InterconnectAttachment.objects.all()
    form = forms.InterconnectAttachmentForm


@register_model_view(InterconnectAttachment, 'delete')
class InterconnectAttachmentDeleteView(generic.ObjectDeleteView):
    queryset = InterconnectAttachment.objects.all()


class InterconnectAttachmentBulkImportView(generic.BulkImportView):
    queryset = InterconnectAttachment.objects.all()
    model_form = forms.InterconnectAttachmentForm


class InterconnectAttachmentBulkDeleteView(generic.BulkDeleteView):
    queryset = InterconnectAttachment.objects.all()
    table = tables.InterconnectAttachmentTable


class ServiceAttachmentListView(generic.ObjectListView):
    queryset = ServiceAttachment.objects.all()
    table = tables.ServiceAttachmentTable
    filterset = filtersets.ServiceAttachmentFilterSet


@register_model_view(ServiceAttachment)
class ServiceAttachmentView(generic.ObjectView):
    queryset = ServiceAttachment.objects.all()


@register_model_view(ServiceAttachment, 'edit')
class ServiceAttachmentEditView(generic.ObjectEditView):
    queryset = ServiceAttachment.objects.all()
    form = forms.ServiceAttachmentForm


@register_model_view(ServiceAttachment, 'delete')
class ServiceAttachmentDeleteView(generic.ObjectDeleteView):
    queryset = ServiceAttachment.objects.all()


class ServiceAttachmentBulkImportView(generic.BulkImportView):
    queryset = ServiceAttachment.objects.all()
    model_form = forms.ServiceAttachmentForm


class ServiceAttachmentBulkDeleteView(generic.BulkDeleteView):
    queryset = ServiceAttachment.objects.all()
    table = tables.ServiceAttachmentTable


class ServiceConnectEndpointListView(generic.ObjectListView):
    queryset = ServiceConnectEndpoint.objects.all()
    table = tables.ServiceConnectEndpointTable
    filterset = filtersets.ServiceConnectEndpointFilterSet


@register_model_view(ServiceConnectEndpoint)
class ServiceConnectEndpointView(generic.ObjectView):
    queryset = ServiceConnectEndpoint.objects.all()


@register_model_view(ServiceConnectEndpoint, 'edit')
class ServiceConnectEndpointEditView(generic.ObjectEditView):
    queryset = ServiceConnectEndpoint.objects.all()
    form = forms.ServiceConnectEndpointForm


@register_model_view(ServiceConnectEndpoint, 'delete')
class ServiceConnectEndpointDeleteView(generic.ObjectDeleteView):
    queryset = ServiceConnectEndpoint.objects.all()


class ServiceConnectEndpointBulkImportView(generic.BulkImportView):
    queryset = ServiceConnectEndpoint.objects.all()
    model_form = forms.ServiceConnectEndpointForm


class ServiceConnectEndpointBulkDeleteView(generic.BulkDeleteView):
    queryset = ServiceConnectEndpoint.objects.all()
    table = tables.ServiceConnectEndpointTable
