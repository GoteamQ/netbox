from django.utils.translation import gettext_lazy as _

from netbox.navigation import Menu, MenuGroup, MenuItem, MenuItemButton, get_model_buttons


def get_gcp_model_item(model_name, label, actions=('add', 'bulk_import')):
    return MenuItem(
        link=f'gcp:{model_name}_list',
        link_text=label,
        permissions=[f'gcp.view_{model_name}'],
        buttons=get_gcp_model_buttons(model_name, actions)
    )


def get_gcp_model_buttons(model_name, actions=('add', 'bulk_import')):
    buttons = []
    if 'add' in actions:
        buttons.append(
            MenuItemButton(
                link=f'gcp:{model_name}_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                permissions=[f'gcp.add_{model_name}']
            )
        )
    if 'bulk_import' in actions:
        buttons.append(
            MenuItemButton(
                link=f'gcp:{model_name}_bulk_import',
                title='Import',
                icon_class='mdi mdi-upload',
                permissions=[f'gcp.add_{model_name}']
            )
        )
    return buttons


GCP_MENU = Menu(
    label=_('Google Cloud'),
    icon_class='mdi mdi-google-cloud',
    groups=(
        MenuGroup(
            label=_('Organizations'),
            items=(
                get_gcp_model_item('gcporganization', _('GCP Organizations'), actions=('add',)),
                MenuItem(
                    link='gcp:discoverylog_list',
                    link_text=_('Discovery Logs'),
                    permissions=['gcp.view_discoverylog'],
                ),
            ),
        ),
        MenuGroup(
            label=_('Projects'),
            items=(
                get_gcp_model_item('gcpproject', _('GCP Projects')),
            ),
        ),
        MenuGroup(
            label=_('Compute'),
            items=(
                get_gcp_model_item('computeinstance', _('Compute Instances')),
                get_gcp_model_item('instancetemplate', _('Instance Templates')),
                get_gcp_model_item('instancegroup', _('Instance Groups')),
            ),
        ),
        MenuGroup(
            label=_('Networking'),
            items=(
                get_gcp_model_item('vpcnetwork', _('VPC Networks')),
                get_gcp_model_item('subnet', _('Subnets')),
                get_gcp_model_item('firewallrule', _('Firewall Rules')),
                get_gcp_model_item('cloudrouter', _('Cloud Routers')),
                get_gcp_model_item('cloudnat', _('Cloud NAT')),
                get_gcp_model_item('loadbalancer', _('Load Balancers')),
            ),
        ),
        MenuGroup(
            label=_('Network Connectivity'),
            items=(
                get_gcp_model_item('ncchub', _('NCC Hubs')),
                get_gcp_model_item('nccspoke', _('NCC Spokes')),
                get_gcp_model_item('interconnectattachment', _('Interconnect Attachments')),
            ),
        ),
        MenuGroup(
            label=_('Private Service Connect'),
            items=(
                get_gcp_model_item('serviceattachment', _('Service Attachments')),
                get_gcp_model_item('serviceconnectendpoint', _('PSC Endpoints')),
            ),
        ),
        MenuGroup(
            label=_('Hybrid Connectivity'),
            items=(
                get_gcp_model_item('vpngateway', _('VPN Gateways')),
                get_gcp_model_item('externalvpngateway', _('External VPN Gateways')),
                get_gcp_model_item('vpntunnel', _('VPN Tunnels')),
            ),
        ),
        MenuGroup(
            label=_('Databases'),
            items=(
                get_gcp_model_item('cloudsqlinstance', _('Cloud SQL')),
                get_gcp_model_item('cloudspannerinstance', _('Cloud Spanner')),
                get_gcp_model_item('firestoredatabase', _('Firestore')),
                get_gcp_model_item('bigtableinstance', _('Bigtable')),
                get_gcp_model_item('memorystoreinstance', _('Memorystore')),
            ),
        ),
        MenuGroup(
            label=_('Storage'),
            items=(
                get_gcp_model_item('cloudstoragebucket', _('Cloud Storage Buckets')),
                get_gcp_model_item('persistentdisk', _('Persistent Disks')),
            ),
        ),
        MenuGroup(
            label=_('Kubernetes'),
            items=(
                get_gcp_model_item('gkecluster', _('GKE Clusters')),
                get_gcp_model_item('gkenodepool', _('Node Pools')),
            ),
        ),
        MenuGroup(
            label=_('Serverless'),
            items=(
                get_gcp_model_item('cloudfunction', _('Cloud Functions')),
                get_gcp_model_item('cloudrun', _('Cloud Run')),
            ),
        ),
        MenuGroup(
            label=_('Messaging'),
            items=(
                get_gcp_model_item('pubsubtopic', _('Pub/Sub Topics')),
                get_gcp_model_item('pubsubsubscription', _('Pub/Sub Subscriptions')),
            ),
        ),
        MenuGroup(
            label=_('Security'),
            items=(
                get_gcp_model_item('secretmanagersecret', _('Secret Manager')),
            ),
        ),
        MenuGroup(
            label=_('DNS'),
            items=(
                get_gcp_model_item('clouddnszone', _('DNS Zones')),
                get_gcp_model_item('clouddnsrecord', _('DNS Records')),
            ),
        ),
        MenuGroup(
            label=_('IAM'),
            items=(
                get_gcp_model_item('serviceaccount', _('Service Accounts')),
                get_gcp_model_item('iamrole', _('IAM Roles')),
                get_gcp_model_item('iambinding', _('IAM Bindings')),
            ),
        ),
    ),
)
