import importlib
import unittest

from unittest.mock import MagicMock, patch
from django.test import TestCase
from gcp.models import GCPProject, GCPOrganization, InstanceGroup, ServiceAttachment, ServiceConnectEndpoint

# Only skip when the base Google packages are genuinely absent (local dev).
# If the packages ARE installed but a transitive dependency is broken,
# let the ImportError propagate so the test fails loudly.
HAS_GCP_DEPS = importlib.util.find_spec('googleapiclient') is not None

if HAS_GCP_DEPS:
    from gcp.discovery import GCPDiscoveryService


@unittest.skipUnless(HAS_GCP_DEPS, 'GCP dependencies (httplib2, google-api-python-client) not installed')
class GCPDiscoveryTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.org = GCPOrganization.objects.create(name='Test Org', organization_id='12345678')
        cls.project = GCPProject.objects.create(
            name='Test Project', project_id='test-project-123', organization=cls.org
        )

    def setUp(self):
        self.service = GCPDiscoveryService(self.org)
        self.service.credentials = MagicMock()  # Mock credentials

    @patch('gcp.discovery.build')
    def test_discover_instance_groups_unmanaged(self, mock_build):
        # Setup mock for Managed Instance Groups (MIGs) - return empty
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # MIG mock
        mock_mig_req = MagicMock()
        mock_service.instanceGroupManagers().aggregatedList.return_value = mock_mig_req
        mock_mig_req.execute.return_value = {}  # No MIGs
        mock_service.instanceGroupManagers().aggregatedList_next.return_value = None

        # Unmanaged Instance Group Mock
        mock_ig_req = MagicMock()
        mock_service.instanceGroups().aggregatedList.return_value = mock_ig_req

        # Define response for Unmanaged IGs
        unmanaged_response = {
            'items': {
                'zones/us-central1-a': {
                    'instanceGroups': [
                        {
                            'name': 'unmanaged-ig-1',
                            'size': 5,
                            'selfLink': 'https://www.googleapis.com/compute/v1/projects/test-project-123/zones/us-central1-a/instanceGroups/unmanaged-ig-1',
                        }
                    ]
                }
            }
        }
        mock_ig_req.execute.return_value = unmanaged_response
        mock_service.instanceGroups().aggregatedList_next.return_value = None

        # Run discovery
        self.service.discover_instance_groups(self.project)

        # Assertions
        ig = InstanceGroup.objects.get(name='unmanaged-ig-1')
        self.assertTrue(ig.discovered)
        self.assertFalse(ig.is_managed)
        self.assertEqual(ig.target_size, 5)

    @patch('gcp.discovery.build')
    def test_discover_psc_resources(self, mock_build):
        # This test ensures we are discovering Service Attachments and PSC Endpoints
        # Since the logic isn't implemented yet, this test is expected to fail or we need to add the logic.
        # But if the user says "shown in the tests", maybe they want to see the lack of coverage or failure?
        # I will implement the test expecting success, so it fails if the logic is missing.

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock Service Attachments (Producer)
        # Using compute API usually? Or networkconnectivity?
        # Service Attachments are Regional. compute.serviceAttachments
        mock_sa_req = MagicMock()
        mock_service.serviceAttachments().aggregatedList.return_value = mock_sa_req

        sa_response = {
            'items': {
                'regions/us-central1': {
                    'serviceAttachments': [
                        {
                            'name': 'test-sa',
                            'region': 'https://www.googleapis.com/compute/v1/projects/xx/regions/us-central1',
                            'connectionPreference': 'ACCEPT_AUTOMATIC',
                            'targetService': 'projects/xx/regions/us-central1/serviceAttachments/test-sa',
                            'selfLink': 'link-sa',
                        }
                    ]
                }
            }
        }
        mock_sa_req.execute.return_value = sa_response
        mock_service.serviceAttachments().aggregatedList_next.return_value = None

        # Mock PSC Endpoints (Consumer - Forwarding Rules with specific target)
        # PSC Endpoints are Forwarding Rules with targetServiceAttachment?
        # OR is there a specific API? Usually it's forwarding rules.
        mock_fr_req = MagicMock()
        mock_service.forwardingRules().aggregatedList.return_value = mock_fr_req

        fr_response = {
            'items': {
                'regions/us-central1': {
                    'forwardingRules': [
                        {
                            'name': 'test-psc-endpoint',
                            'region': 'https://www.googleapis.com/compute/v1/projects/xx/regions/us-central1',
                            'IPAddress': '10.0.0.5',
                            'target': 'https://www.googleapis.com/compute/v1/projects/xx/regions/us-central1/serviceAttachments/target-sa',
                            # This field varies for PSC
                            'PSCConnectionStatus': 'ACCEPTED',  # Hint it's PSC?
                            'selfLink': 'link-psc',
                        }
                    ]
                }
            }
        }
        mock_fr_req.execute.return_value = fr_response
        mock_service.forwardingRules().aggregatedList_next.return_value = None

        # Note: Logic to distinguish LoadBalancer from PSC Endpoint needs to be robust.
        # For now let's assume discover_psc() method exists or should exist.

        # If I call discover_all(), it would take too long/too many mocks.
        # I'll try to call `discover_service_attachments` and `discover_psc_endpoints`
        # assuming they exist or will exist.

        if not hasattr(self.service, 'discover_service_attachments'):
            self.fail('discover_service_attachments method not implemented in GCPDiscoveryService')
        self.service.discover_service_attachments(self.project)
        sa = ServiceAttachment.objects.get(name='test-sa')
        self.assertTrue(sa.discovered)

        if not hasattr(self.service, 'discover_psc_endpoints'):
            self.fail('discover_psc_endpoints method not implemented in GCPDiscoveryService')
        self.service.discover_psc_endpoints(self.project)
        psc = ServiceConnectEndpoint.objects.get(name='test-psc-endpoint')
        self.assertTrue(psc.discovered)

    @patch('gcp.discovery.build')
    def test_discover_service_attachment_update(self, mock_build):
        # Create existing SA
        sa = ServiceAttachment.objects.create(
            project=self.project,
            name='test-sa',
            region='us-central1',
            connection_preference='ACCEPT_AUTOMATIC',
            discovered=True,
        )

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # New data
        mock_sa_req = MagicMock()
        mock_service.serviceAttachments().aggregatedList.return_value = mock_sa_req

        sa_response = {
            'items': {
                'regions/us-central1': {
                    'serviceAttachments': [
                        {
                            'name': 'test-sa',
                            'region': 'regions/us-central1',
                            'connectionPreference': 'ACCEPT_MANUAL',  # Changed
                            'targetService': 'new-target',
                            'selfLink': 'link-sa',
                        }
                    ]
                }
            }
        }
        mock_sa_req.execute.return_value = sa_response
        mock_service.serviceAttachments().aggregatedList_next.return_value = None

        self.service.discover_service_attachments(self.project)

        sa.refresh_from_db()
        self.assertEqual(sa.connection_preference, 'ACCEPT_MANUAL')
        self.assertEqual(sa.target_service, 'new-target')

    @patch('gcp.discovery.build')
    def test_discovery_error_handling(self, mock_build):
        from googleapiclient.errors import HttpError

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock error response
        mock_resp = MagicMock()
        mock_resp.status = 403
        mock_resp.reason = 'Forbidden'
        # Proper GCP Error Structure
        content = (
            b'{"error": {"errors": [{"reason": "forbidden", "message": "Access Denied"}], '
            b'"code": 403, "message": "Access Denied"}}'
        )

        error = HttpError(mock_resp, content)

        mock_sa_req = MagicMock()
        mock_sa_req.execute.side_effect = error
        mock_service.serviceAttachments().aggregatedList.return_value = mock_sa_req

        # Should not raise exception
        try:
            self.service.discover_service_attachments(self.project)
        except Exception as e:
            self.fail(f'Discovery raised exception on API error: {e}')

        # Check logs
        found = False
        for msg in self.service.log_messages:
            if 'Access Denied' in msg:
                found = True
                break
        self.assertTrue(found, f'Error message not found in logs: {self.service.log_messages}')
