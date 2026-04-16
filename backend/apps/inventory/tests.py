from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.catalog.models import BibliographicRecord, ItemCopy
from apps.core.models import Campus, Institution, LibraryBranch
from apps.users.models import User

from .models import InventoryCampaign, InventoryRead, InventoryScanSession
from .services import register_scan


class InventoryServicesTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.institution = Institution.objects.create(name='IFMS', code='IFMS')
        self.campus = Campus.objects.create(institution=self.institution, name='Campus CG', code='CG')
        self.branch = LibraryBranch.objects.create(campus=self.campus, name='Biblioteca Central', code='BC')
        self.record = BibliographicRecord.objects.create(title='Engenharia de Software')
        self.item = ItemCopy.objects.create(
            bibliographic_record=self.record,
            library_branch=self.branch,
            asset_code='PAT-001',
            barcode='BAR-001',
        )
        self.operator = User.objects.create_user(
            email='operador@ifms.edu.br',
            password='teste123',
            role='librarian',
            library_branch=self.branch,
        )
        self.campaign = InventoryCampaign.objects.create(
            library_branch=self.branch,
            name='Inventario 2026',
            status=InventoryCampaign.Status.ACTIVE,
            opened_by=self.operator,
        )
        self.session = InventoryScanSession.objects.create(
            campaign=self.campaign,
            operator=self.operator,
            device_label='coletor-01',
        )

    def test_register_scan_matches_item_by_asset_code(self):
        inventory_read = register_scan(
            campaign=self.campaign,
            session=self.session,
            operator=self.operator,
            scanned_code='PAT-001',
            scan_source=InventoryRead.ScanSource.PATRIMONY,
        )

        self.assertEqual(inventory_read.match_status, InventoryRead.MatchStatus.MATCHED)
        self.assertEqual(inventory_read.item_copy, self.item)

    def test_inventory_scan_api_requires_authenticated_operator(self):
        response = self.client.post(
            reverse('inventory-scan-read-create'),
            {
                'campaign_id': str(self.campaign.id),
                'session_id': str(self.session.id),
                'scanned_code': 'PAT-999',
                'scan_source': InventoryRead.ScanSource.PATRIMONY,
                'device_label': 'camera-android',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 401)

    def test_inventory_scan_api_uses_authenticated_operator(self):
        self.client.force_authenticate(user=self.operator)
        response = self.client.post(
            reverse('inventory-scan-read-create'),
            {
                'campaign_id': str(self.campaign.id),
                'session_id': str(self.session.id),
                'scanned_code': 'PAT-999',
                'scan_source': InventoryRead.ScanSource.PATRIMONY,
                'device_label': 'camera-android',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['match_status'], InventoryRead.MatchStatus.UNMATCHED)
        self.assertEqual(response.json()['operator'], str(self.operator.id))
        self.assertEqual(InventoryRead.objects.count(), 1)

    def test_inventory_campaign_create_sets_opened_by(self):
        self.client.force_authenticate(user=self.operator)
        response = self.client.post(
            '/api/v1/inventory/campaigns/',
            {
                'library_branch': str(self.branch.id),
                'name': 'Inventario Especial',
                'status': InventoryCampaign.Status.ACTIVE,
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['opened_by'], str(self.operator.id))

    def test_inventory_export_returns_csv(self):
        register_scan(
            campaign=self.campaign,
            session=self.session,
            operator=self.operator,
            scanned_code='PAT-001',
            scan_source=InventoryRead.ScanSource.PATRIMONY,
            device_label='coletor-01',
        )
        self.client.force_authenticate(user=self.operator)

        response = self.client.get(f'/api/v1/inventory/campaigns/{self.campaign.id}/export-reads/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('PAT-001', response.content.decode())
        self.assertIn('matched', response.content.decode())
