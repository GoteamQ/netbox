from django.urls import include, path

from utilities.urls import get_model_urls
from . import views

app_name = 'gcp'

urlpatterns = [
    path('organizations/', views.GCPOrganizationListView.as_view(), name='gcporganization_list'),
    path('organizations/add/', views.GCPOrganizationEditView.as_view(), name='gcporganization_add'),
    path('organizations/delete/', views.GCPOrganizationBulkDeleteView.as_view(), name='gcporganization_bulk_delete'),
    path('organizations/<int:pk>/', include(get_model_urls('gcp', 'gcporganization'))),
    path('organizations/<int:pk>/discover/', views.GCPOrganizationDiscoverView.as_view(), name='gcporganization_discover'),

    path('discovery-logs/', views.DiscoveryLogListView.as_view(), name='discoverylog_list'),
    path('discovery-logs/delete/', views.DiscoveryLogBulkDeleteView.as_view(), name='discoverylog_bulk_delete'),
    path('discovery-logs/<int:pk>/', include(get_model_urls('gcp', 'discoverylog'))),

    path('projects/', views.GCPProjectListView.as_view(), name='gcpproject_list'),
    path('projects/add/', views.GCPProjectEditView.as_view(), name='gcpproject_add'),
    path('projects/import/', views.GCPProjectBulkImportView.as_view(), name='gcpproject_bulk_import'),
    path('projects/delete/', views.GCPProjectBulkDeleteView.as_view(), name='gcpproject_bulk_delete'),
    path('projects/<int:pk>/', include(get_model_urls('gcp', 'gcpproject'))),

    path('compute-instances/', views.ComputeInstanceListView.as_view(), name='computeinstance_list'),
    path('compute-instances/add/', views.ComputeInstanceEditView.as_view(), name='computeinstance_add'),
    path('compute-instances/import/', views.ComputeInstanceBulkImportView.as_view(), name='computeinstance_bulk_import'),
    path('compute-instances/delete/', views.ComputeInstanceBulkDeleteView.as_view(), name='computeinstance_bulk_delete'),
    path('compute-instances/<int:pk>/', include(get_model_urls('gcp', 'computeinstance'))),

    path('instance-templates/', views.InstanceTemplateListView.as_view(), name='instancetemplate_list'),
    path('instance-templates/add/', views.InstanceTemplateEditView.as_view(), name='instancetemplate_add'),
    path('instance-templates/import/', views.InstanceTemplateBulkImportView.as_view(), name='instancetemplate_bulk_import'),
    path('instance-templates/delete/', views.InstanceTemplateBulkDeleteView.as_view(), name='instancetemplate_bulk_delete'),
    path('instance-templates/<int:pk>/', include(get_model_urls('gcp', 'instancetemplate'))),

    path('instance-groups/', views.InstanceGroupListView.as_view(), name='instancegroup_list'),
    path('instance-groups/add/', views.InstanceGroupEditView.as_view(), name='instancegroup_add'),
    path('instance-groups/import/', views.InstanceGroupBulkImportView.as_view(), name='instancegroup_bulk_import'),
    path('instance-groups/delete/', views.InstanceGroupBulkDeleteView.as_view(), name='instancegroup_bulk_delete'),
    path('instance-groups/<int:pk>/', include(get_model_urls('gcp', 'instancegroup'))),

    path('vpc-networks/', views.VPCNetworkListView.as_view(), name='vpcnetwork_list'),
    path('vpc-networks/add/', views.VPCNetworkEditView.as_view(), name='vpcnetwork_add'),
    path('vpc-networks/import/', views.VPCNetworkBulkImportView.as_view(), name='vpcnetwork_bulk_import'),
    path('vpc-networks/delete/', views.VPCNetworkBulkDeleteView.as_view(), name='vpcnetwork_bulk_delete'),
    path('vpc-networks/<int:pk>/', include(get_model_urls('gcp', 'vpcnetwork'))),

    path('subnets/', views.SubnetListView.as_view(), name='subnet_list'),
    path('subnets/add/', views.SubnetEditView.as_view(), name='subnet_add'),
    path('subnets/import/', views.SubnetBulkImportView.as_view(), name='subnet_bulk_import'),
    path('subnets/delete/', views.SubnetBulkDeleteView.as_view(), name='subnet_bulk_delete'),
    path('subnets/<int:pk>/', include(get_model_urls('gcp', 'subnet'))),

    path('firewall-rules/', views.FirewallRuleListView.as_view(), name='firewallrule_list'),
    path('firewall-rules/add/', views.FirewallRuleEditView.as_view(), name='firewallrule_add'),
    path('firewall-rules/import/', views.FirewallRuleBulkImportView.as_view(), name='firewallrule_bulk_import'),
    path('firewall-rules/delete/', views.FirewallRuleBulkDeleteView.as_view(), name='firewallrule_bulk_delete'),
    path('firewall-rules/<int:pk>/', include(get_model_urls('gcp', 'firewallrule'))),

    path('cloud-routers/', views.CloudRouterListView.as_view(), name='cloudrouter_list'),
    path('cloud-routers/add/', views.CloudRouterEditView.as_view(), name='cloudrouter_add'),
    path('cloud-routers/import/', views.CloudRouterBulkImportView.as_view(), name='cloudrouter_bulk_import'),
    path('cloud-routers/delete/', views.CloudRouterBulkDeleteView.as_view(), name='cloudrouter_bulk_delete'),
    path('cloud-routers/<int:pk>/', include(get_model_urls('gcp', 'cloudrouter'))),

    path('cloud-nats/', views.CloudNATListView.as_view(), name='cloudnat_list'),
    path('cloud-nats/add/', views.CloudNATEditView.as_view(), name='cloudnat_add'),
    path('cloud-nats/import/', views.CloudNATBulkImportView.as_view(), name='cloudnat_bulk_import'),
    path('cloud-nats/delete/', views.CloudNATBulkDeleteView.as_view(), name='cloudnat_bulk_delete'),
    path('cloud-nats/<int:pk>/', include(get_model_urls('gcp', 'cloudnat'))),

    path('load-balancers/', views.LoadBalancerListView.as_view(), name='loadbalancer_list'),
    path('load-balancers/add/', views.LoadBalancerEditView.as_view(), name='loadbalancer_add'),
    path('load-balancers/import/', views.LoadBalancerBulkImportView.as_view(), name='loadbalancer_bulk_import'),
    path('load-balancers/delete/', views.LoadBalancerBulkDeleteView.as_view(), name='loadbalancer_bulk_delete'),
    path('load-balancers/<int:pk>/', include(get_model_urls('gcp', 'loadbalancer'))),

    path('cloud-sql/', views.CloudSQLInstanceListView.as_view(), name='cloudsqlinstance_list'),
    path('cloud-sql/add/', views.CloudSQLInstanceEditView.as_view(), name='cloudsqlinstance_add'),
    path('cloud-sql/import/', views.CloudSQLInstanceBulkImportView.as_view(), name='cloudsqlinstance_bulk_import'),
    path('cloud-sql/delete/', views.CloudSQLInstanceBulkDeleteView.as_view(), name='cloudsqlinstance_bulk_delete'),
    path('cloud-sql/<int:pk>/', include(get_model_urls('gcp', 'cloudsqlinstance'))),

    path('cloud-spanner/', views.CloudSpannerInstanceListView.as_view(), name='cloudspannerinstance_list'),
    path('cloud-spanner/add/', views.CloudSpannerInstanceEditView.as_view(), name='cloudspannerinstance_add'),
    path('cloud-spanner/import/', views.CloudSpannerInstanceBulkImportView.as_view(), name='cloudspannerinstance_bulk_import'),
    path('cloud-spanner/delete/', views.CloudSpannerInstanceBulkDeleteView.as_view(), name='cloudspannerinstance_bulk_delete'),
    path('cloud-spanner/<int:pk>/', include(get_model_urls('gcp', 'cloudspannerinstance'))),

    path('firestore/', views.FirestoreDatabaseListView.as_view(), name='firestoredatabase_list'),
    path('firestore/add/', views.FirestoreDatabaseEditView.as_view(), name='firestoredatabase_add'),
    path('firestore/import/', views.FirestoreDatabaseBulkImportView.as_view(), name='firestoredatabase_bulk_import'),
    path('firestore/delete/', views.FirestoreDatabaseBulkDeleteView.as_view(), name='firestoredatabase_bulk_delete'),
    path('firestore/<int:pk>/', include(get_model_urls('gcp', 'firestoredatabase'))),

    path('bigtable/', views.BigtableInstanceListView.as_view(), name='bigtableinstance_list'),
    path('bigtable/add/', views.BigtableInstanceEditView.as_view(), name='bigtableinstance_add'),
    path('bigtable/import/', views.BigtableInstanceBulkImportView.as_view(), name='bigtableinstance_bulk_import'),
    path('bigtable/delete/', views.BigtableInstanceBulkDeleteView.as_view(), name='bigtableinstance_bulk_delete'),
    path('bigtable/<int:pk>/', include(get_model_urls('gcp', 'bigtableinstance'))),

    path('storage-buckets/', views.CloudStorageBucketListView.as_view(), name='cloudstoragebucket_list'),
    path('storage-buckets/add/', views.CloudStorageBucketEditView.as_view(), name='cloudstoragebucket_add'),
    path('storage-buckets/import/', views.CloudStorageBucketBulkImportView.as_view(), name='cloudstoragebucket_bulk_import'),
    path('storage-buckets/delete/', views.CloudStorageBucketBulkDeleteView.as_view(), name='cloudstoragebucket_bulk_delete'),
    path('storage-buckets/<int:pk>/', include(get_model_urls('gcp', 'cloudstoragebucket'))),

    path('persistent-disks/', views.PersistentDiskListView.as_view(), name='persistentdisk_list'),
    path('persistent-disks/add/', views.PersistentDiskEditView.as_view(), name='persistentdisk_add'),
    path('persistent-disks/import/', views.PersistentDiskBulkImportView.as_view(), name='persistentdisk_bulk_import'),
    path('persistent-disks/delete/', views.PersistentDiskBulkDeleteView.as_view(), name='persistentdisk_bulk_delete'),
    path('persistent-disks/<int:pk>/', include(get_model_urls('gcp', 'persistentdisk'))),

    path('gke-clusters/', views.GKEClusterListView.as_view(), name='gkecluster_list'),
    path('gke-clusters/add/', views.GKEClusterEditView.as_view(), name='gkecluster_add'),
    path('gke-clusters/import/', views.GKEClusterBulkImportView.as_view(), name='gkecluster_bulk_import'),
    path('gke-clusters/delete/', views.GKEClusterBulkDeleteView.as_view(), name='gkecluster_bulk_delete'),
    path('gke-clusters/<int:pk>/', include(get_model_urls('gcp', 'gkecluster'))),

    path('gke-node-pools/', views.GKENodePoolListView.as_view(), name='gkenodepool_list'),
    path('gke-node-pools/add/', views.GKENodePoolEditView.as_view(), name='gkenodepool_add'),
    path('gke-node-pools/import/', views.GKENodePoolBulkImportView.as_view(), name='gkenodepool_bulk_import'),
    path('gke-node-pools/delete/', views.GKENodePoolBulkDeleteView.as_view(), name='gkenodepool_bulk_delete'),
    path('gke-node-pools/<int:pk>/', include(get_model_urls('gcp', 'gkenodepool'))),

    path('service-accounts/', views.ServiceAccountListView.as_view(), name='serviceaccount_list'),
    path('service-accounts/add/', views.ServiceAccountEditView.as_view(), name='serviceaccount_add'),
    path('service-accounts/import/', views.ServiceAccountBulkImportView.as_view(), name='serviceaccount_bulk_import'),
    path('service-accounts/delete/', views.ServiceAccountBulkDeleteView.as_view(), name='serviceaccount_bulk_delete'),
    path('service-accounts/<int:pk>/', include(get_model_urls('gcp', 'serviceaccount'))),

    path('iam-roles/', views.IAMRoleListView.as_view(), name='iamrole_list'),
    path('iam-roles/add/', views.IAMRoleEditView.as_view(), name='iamrole_add'),
    path('iam-roles/import/', views.IAMRoleBulkImportView.as_view(), name='iamrole_bulk_import'),
    path('iam-roles/delete/', views.IAMRoleBulkDeleteView.as_view(), name='iamrole_bulk_delete'),
    path('iam-roles/<int:pk>/', include(get_model_urls('gcp', 'iamrole'))),

    path('iam-bindings/', views.IAMBindingListView.as_view(), name='iambinding_list'),
    path('iam-bindings/add/', views.IAMBindingEditView.as_view(), name='iambinding_add'),
    path('iam-bindings/import/', views.IAMBindingBulkImportView.as_view(), name='iambinding_bulk_import'),
    path('iam-bindings/delete/', views.IAMBindingBulkDeleteView.as_view(), name='iambinding_bulk_delete'),
    path('iam-bindings/<int:pk>/', include(get_model_urls('gcp', 'iambinding'))),

    path('cloud-functions/', views.CloudFunctionListView.as_view(), name='cloudfunction_list'),
    path('cloud-functions/add/', views.CloudFunctionEditView.as_view(), name='cloudfunction_add'),
    path('cloud-functions/import/', views.CloudFunctionBulkImportView.as_view(), name='cloudfunction_bulk_import'),
    path('cloud-functions/delete/', views.CloudFunctionBulkDeleteView.as_view(), name='cloudfunction_bulk_delete'),
    path('cloud-functions/<int:pk>/', include(get_model_urls('gcp', 'cloudfunction'))),

    path('cloud-run/', views.CloudRunListView.as_view(), name='cloudrun_list'),
    path('cloud-run/add/', views.CloudRunEditView.as_view(), name='cloudrun_add'),
    path('cloud-run/import/', views.CloudRunBulkImportView.as_view(), name='cloudrun_bulk_import'),
    path('cloud-run/delete/', views.CloudRunBulkDeleteView.as_view(), name='cloudrun_bulk_delete'),
    path('cloud-run/<int:pk>/', include(get_model_urls('gcp', 'cloudrun'))),

    path('pubsub-topics/', views.PubSubTopicListView.as_view(), name='pubsubtopic_list'),
    path('pubsub-topics/add/', views.PubSubTopicEditView.as_view(), name='pubsubtopic_add'),
    path('pubsub-topics/import/', views.PubSubTopicBulkImportView.as_view(), name='pubsubtopic_bulk_import'),
    path('pubsub-topics/delete/', views.PubSubTopicBulkDeleteView.as_view(), name='pubsubtopic_bulk_delete'),
    path('pubsub-topics/<int:pk>/', include(get_model_urls('gcp', 'pubsubtopic'))),

    path('pubsub-subscriptions/', views.PubSubSubscriptionListView.as_view(), name='pubsubsubscription_list'),
    path('pubsub-subscriptions/add/', views.PubSubSubscriptionEditView.as_view(), name='pubsubsubscription_add'),
    path('pubsub-subscriptions/import/', views.PubSubSubscriptionBulkImportView.as_view(), name='pubsubsubscription_bulk_import'),
    path('pubsub-subscriptions/delete/', views.PubSubSubscriptionBulkDeleteView.as_view(), name='pubsubsubscription_bulk_delete'),
    path('pubsub-subscriptions/<int:pk>/', include(get_model_urls('gcp', 'pubsubsubscription'))),

    path('secrets/', views.SecretManagerSecretListView.as_view(), name='secretmanagersecret_list'),
    path('secrets/add/', views.SecretManagerSecretEditView.as_view(), name='secretmanagersecret_add'),
    path('secrets/import/', views.SecretManagerSecretBulkImportView.as_view(), name='secretmanagersecret_bulk_import'),
    path('secrets/delete/', views.SecretManagerSecretBulkDeleteView.as_view(), name='secretmanagersecret_bulk_delete'),
    path('secrets/<int:pk>/', include(get_model_urls('gcp', 'secretmanagersecret'))),

    path('dns-zones/', views.CloudDNSZoneListView.as_view(), name='clouddnszone_list'),
    path('dns-zones/add/', views.CloudDNSZoneEditView.as_view(), name='clouddnszone_add'),
    path('dns-zones/import/', views.CloudDNSZoneBulkImportView.as_view(), name='clouddnszone_bulk_import'),
    path('dns-zones/delete/', views.CloudDNSZoneBulkDeleteView.as_view(), name='clouddnszone_bulk_delete'),
    path('dns-zones/<int:pk>/', include(get_model_urls('gcp', 'clouddnszone'))),

    path('dns-records/', views.CloudDNSRecordListView.as_view(), name='clouddnsrecord_list'),
    path('dns-records/add/', views.CloudDNSRecordEditView.as_view(), name='clouddnsrecord_add'),
    path('dns-records/import/', views.CloudDNSRecordBulkImportView.as_view(), name='clouddnsrecord_bulk_import'),
    path('dns-records/delete/', views.CloudDNSRecordBulkDeleteView.as_view(), name='clouddnsrecord_bulk_delete'),
    path('dns-records/<int:pk>/', include(get_model_urls('gcp', 'clouddnsrecord'))),

    path('memorystore/', views.MemorystoreInstanceListView.as_view(), name='memorystoreinstance_list'),
    path('memorystore/add/', views.MemorystoreInstanceEditView.as_view(), name='memorystoreinstance_add'),
    path('memorystore/import/', views.MemorystoreInstanceBulkImportView.as_view(), name='memorystoreinstance_bulk_import'),
    path('memorystore/delete/', views.MemorystoreInstanceBulkDeleteView.as_view(), name='memorystoreinstance_bulk_delete'),
    path('memorystore/<int:pk>/', include(get_model_urls('gcp', 'memorystoreinstance'))),

    path('ncc-hubs/', views.NCCHubListView.as_view(), name='ncchub_list'),
    path('ncc-hubs/add/', views.NCCHubEditView.as_view(), name='ncchub_add'),
    path('ncc-hubs/import/', views.NCCHubBulkImportView.as_view(), name='ncchub_bulk_import'),
    path('ncc-hubs/delete/', views.NCCHubBulkDeleteView.as_view(), name='ncchub_bulk_delete'),
    path('ncc-hubs/<int:pk>/', include(get_model_urls('gcp', 'ncchub'))),

    path('ncc-spokes/', views.NCCSpokeListView.as_view(), name='nccspoke_list'),
    path('ncc-spokes/add/', views.NCCSpokeEditView.as_view(), name='nccspoke_add'),
    path('ncc-spokes/import/', views.NCCSpokeBulkImportView.as_view(), name='nccspoke_bulk_import'),
    path('ncc-spokes/delete/', views.NCCSpokeBulkDeleteView.as_view(), name='nccspoke_bulk_delete'),
    path('ncc-spokes/<int:pk>/', include(get_model_urls('gcp', 'nccspoke'))),

    path('vpn-gateways/', views.VPNGatewayListView.as_view(), name='vpngateway_list'),
    path('vpn-gateways/add/', views.VPNGatewayEditView.as_view(), name='vpngateway_add'),
    path('vpn-gateways/import/', views.VPNGatewayBulkImportView.as_view(), name='vpngateway_bulk_import'),
    path('vpn-gateways/delete/', views.VPNGatewayBulkDeleteView.as_view(), name='vpngateway_bulk_delete'),
    path('vpn-gateways/<int:pk>/', include(get_model_urls('gcp', 'vpngateway'))),

    path('external-vpn-gateways/', views.ExternalVPNGatewayListView.as_view(), name='externalvpngateway_list'),
    path('external-vpn-gateways/add/', views.ExternalVPNGatewayEditView.as_view(), name='externalvpngateway_add'),
    path('external-vpn-gateways/import/', views.ExternalVPNGatewayBulkImportView.as_view(), name='externalvpngateway_bulk_import'),
    path('external-vpn-gateways/delete/', views.ExternalVPNGatewayBulkDeleteView.as_view(), name='externalvpngateway_bulk_delete'),
    path('external-vpn-gateways/<int:pk>/', include(get_model_urls('gcp', 'externalvpngateway'))),

    path('vpn-tunnels/', views.VPNTunnelListView.as_view(), name='vpntunnel_list'),
    path('vpn-tunnels/add/', views.VPNTunnelEditView.as_view(), name='vpntunnel_add'),
    path('vpn-tunnels/import/', views.VPNTunnelBulkImportView.as_view(), name='vpntunnel_bulk_import'),
    path('vpn-tunnels/delete/', views.VPNTunnelBulkDeleteView.as_view(), name='vpntunnel_bulk_delete'),
    path('vpn-tunnels/<int:pk>/', include(get_model_urls('gcp', 'vpntunnel'))),

    path('interconnect-attachments/', views.InterconnectAttachmentListView.as_view(), name='interconnectattachment_list'),
    path('interconnect-attachments/add/', views.InterconnectAttachmentEditView.as_view(), name='interconnectattachment_add'),
    path('interconnect-attachments/import/', views.InterconnectAttachmentBulkImportView.as_view(), name='interconnectattachment_bulk_import'),
    path('interconnect-attachments/delete/', views.InterconnectAttachmentBulkDeleteView.as_view(), name='interconnectattachment_bulk_delete'),
    path('interconnect-attachments/<int:pk>/', include(get_model_urls('gcp', 'interconnectattachment'))),
]
