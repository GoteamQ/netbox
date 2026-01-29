from netbox.api.routers import NetBoxRouter
from . import views

router = NetBoxRouter()
router.APIRootView = views.GCPProjectViewSet

router.register('projects', views.GCPProjectViewSet)
router.register('compute-instances', views.ComputeInstanceViewSet)
router.register('instance-templates', views.InstanceTemplateViewSet)
router.register('instance-groups', views.InstanceGroupViewSet)
router.register('vpc-networks', views.VPCNetworkViewSet)
router.register('subnets', views.SubnetViewSet)
router.register('firewall-rules', views.FirewallRuleViewSet)
router.register('cloud-routers', views.CloudRouterViewSet)
router.register('cloud-nats', views.CloudNATViewSet)
router.register('load-balancers', views.LoadBalancerViewSet)
router.register('cloud-sql', views.CloudSQLInstanceViewSet)
router.register('cloud-spanner', views.CloudSpannerInstanceViewSet)
router.register('firestore', views.FirestoreDatabaseViewSet)
router.register('bigtable', views.BigtableInstanceViewSet)
router.register('storage-buckets', views.CloudStorageBucketViewSet)
router.register('persistent-disks', views.PersistentDiskViewSet)
router.register('gke-clusters', views.GKEClusterViewSet)
router.register('gke-node-pools', views.GKENodePoolViewSet)
router.register('service-accounts', views.ServiceAccountViewSet)
router.register('iam-roles', views.IAMRoleViewSet)
router.register('iam-bindings', views.IAMBindingViewSet)
router.register('cloud-functions', views.CloudFunctionViewSet)
router.register('cloud-run', views.CloudRunViewSet)
router.register('pubsub-topics', views.PubSubTopicViewSet)
router.register('pubsub-subscriptions', views.PubSubSubscriptionViewSet)
router.register('secrets', views.SecretManagerSecretViewSet)
router.register('dns-zones', views.CloudDNSZoneViewSet)
router.register('dns-records', views.CloudDNSRecordViewSet)
router.register('memorystore', views.MemorystoreInstanceViewSet)

urlpatterns = router.urls
