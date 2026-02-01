from django.test import TestCase
from gcp.models import GCPProject, VPCNetwork, ServiceAttachment, ServiceConnectEndpoint, GCPOrganization, InstanceGroup

class PrivateServiceConnectTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.org = GCPOrganization.objects.create(name='Test Org', organization_id='12345678')
        cls.project = GCPProject.objects.create(name='Test Project', project_id='test-project-123', organization=cls.org)
        cls.network = VPCNetwork.objects.create(name='test-network', project=cls.project)

    def test_service_attachment_creation(self):
        sa = ServiceAttachment.objects.create(
            name='test-sa',
            project=self.project,
            region='us-central1',
            connection_preference='ACCEPT_AUTOMATIC',
            target_service='projects/test-project/regions/us-central1/serviceAttachments/test-sa'
        )
        self.assertEqual(sa.name, 'test-sa')
        self.assertEqual(sa.project, self.project)
        self.assertEqual(str(sa), 'test-sa')

    def test_service_connect_endpoint_creation(self):
        psc = ServiceConnectEndpoint.objects.create(
            name='test-psc',
            project=self.project,
            region='us-central1',
            network=self.network,
            ip_address='10.0.0.5',
            target_service_attachment='projects/other-project/regions/us-central1/serviceAttachments/target-sa'
        )
        self.assertEqual(psc.name, 'test-psc')
        self.assertEqual(psc.project, self.project)
        self.assertEqual(psc.network, self.network)
        self.assertEqual(str(psc), 'test-psc')

    def test_instance_group_creation(self):
        ig = InstanceGroup.objects.create(
            name='test-ig',
            project=self.project,
            zone='us-central1-a',
            target_size=3,
            is_managed=True
        )
        self.assertEqual(ig.name, 'test-ig')
        self.assertEqual(ig.target_size, 3)
        self.assertTrue(ig.is_managed)
        self.assertEqual(str(ig), 'test-ig')

    def test_unmanaged_instance_group_creation(self):
        ig = InstanceGroup.objects.create(
            name='test-unmanaged-ig',
            project=self.project,
            zone='us-central1-b',
            target_size=5,
            is_managed=False
        )
        self.assertEqual(ig.name, 'test-unmanaged-ig')
        self.assertFalse(ig.is_managed)

