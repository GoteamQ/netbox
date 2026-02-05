from netbox.graphql.types import NetBoxObjectType
from . import models, filtersets

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
