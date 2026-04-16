from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.catalog.models import Author, BibliographicRecord, ItemCopy, Subject
from apps.circulation.models import Loan, Reservation
from apps.inventory.models import InventoryCampaign, InventoryRead
from apps.users.models import Patron, PatronBlock, User

from .models import Campus, Institution, LibraryBranch


class HealthCheckViewTests(TestCase):
    def test_health_endpoint_returns_ok(self):
        response = self.client.get(reverse('health-check'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')


class CoreReferenceApiTests(TestCase):
    def setUp(self):
        self.institution = Institution.objects.create(name='Instituto Federal', code='IF')
        self.campus = Campus.objects.create(
            institution=self.institution,
            name='Campus Campo Grande',
            code='CG',
            city='Campo Grande',
            state='MS',
        )
        self.branch = LibraryBranch.objects.create(
            campus=self.campus,
            name='Biblioteca Central',
            code='BIB-CG',
            email='biblioteca@if.example',
        )

    def test_branch_list_returns_institutional_hierarchy(self):
        response = self.client.get('/api/v1/core/branches/')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]['name'], 'Biblioteca Central')
        self.assertEqual(payload[0]['campus_name'], 'Campus Campo Grande')
        self.assertEqual(payload[0]['institution_name'], 'Instituto Federal')

    def test_campus_list_returns_institution_name(self):
        response = self.client.get('/api/v1/core/campuses/')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]['institution_name'], 'Instituto Federal')


class DashboardOverviewApiTests(APITestCase):
    def setUp(self):
        now = timezone.now()
        self.institution = Institution.objects.create(name='Instituto Federal', code='IF')
        self.campus = Campus.objects.create(
            institution=self.institution,
            name='Campus Campo Grande',
            code='CG',
            city='Campo Grande',
            state='MS',
        )
        self.branch = LibraryBranch.objects.create(
            campus=self.campus,
            name='Biblioteca Central',
            code='BIB-CG',
            email='biblioteca@if.example',
        )
        self.user = User.objects.create_user(
            email='operador@if.example',
            password='SenhaForte!123',
            first_name='Operador',
            last_name='Demo',
            role=User.Role.LIBRARIAN,
            library_branch=self.branch,
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

        author = Author.objects.create(name='Autor Demo')
        subject = Subject.objects.create(name='Assunto Demo')
        record = BibliographicRecord.objects.create(
            title='Titulo Demo',
            subtitle='Subtitulo',
            isbn='9780000000001',
            publication_year=2025,
            publisher='Editora Demo',
            classification_code='000',
            language='pt-BR',
        )
        record.authors.add(author)
        record.subjects.add(subject)

        self.available_copy = ItemCopy.objects.create(
            bibliographic_record=record,
            library_branch=self.branch,
            asset_code='PAT-1000',
            barcode='BAR-1000',
            rfid_tag='RFID-1000',
            status=ItemCopy.Status.AVAILABLE,
        )
        self.loaned_copy = ItemCopy.objects.create(
            bibliographic_record=record,
            library_branch=self.branch,
            asset_code='PAT-1001',
            barcode='BAR-1001',
            rfid_tag='RFID-1001',
            status=ItemCopy.Status.LOANED,
        )

        patron = Patron.objects.create(
            registration_code='REG-1000',
            full_name='Patron Demo',
            email='patron@if.example',
            category=Patron.Category.STUDENT,
            status=Patron.Status.BLOCKED,
            library_branch=self.branch,
        )
        PatronBlock.objects.create(patron=patron, reason='Automatic block due to overdue loans', is_active=True)
        Loan.objects.create(
            patron=patron,
            item_copy=self.loaned_copy,
            checked_out_by=self.user,
            due_at=now - timedelta(days=3),
            status=Loan.Status.OVERDUE,
        )
        Reservation.objects.create(
            patron=patron,
            bibliographic_record=record,
            pickup_branch=self.branch,
            status=Reservation.Status.QUEUED,
            queue_position=1,
        )
        campaign = InventoryCampaign.objects.create(
            library_branch=self.branch,
            name='Inventario Demo',
            status=InventoryCampaign.Status.ACTIVE,
            opened_by=self.user,
            started_at=now - timedelta(hours=2),
        )
        InventoryRead.objects.create(
            campaign=campaign,
            operator=self.user,
            item_copy=self.available_copy,
            scanned_code='PAT-1000',
            scan_source=InventoryRead.ScanSource.PATRIMONY,
            match_status=InventoryRead.MatchStatus.MATCHED,
            device_label='coletor-demo',
        )
        InventoryRead.objects.create(
            campaign=campaign,
            operator=self.user,
            item_copy=None,
            scanned_code='NAO-LOCALIZADO',
            scan_source=InventoryRead.ScanSource.MANUAL,
            match_status=InventoryRead.MatchStatus.UNMATCHED,
            device_label='coletor-demo',
        )

    def test_dashboard_overview_returns_operational_counts(self):
        response = self.client.get('/api/v1/core/dashboard/overview/')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['institutions'], 1)
        self.assertEqual(payload['branches'], 1)
        self.assertEqual(payload['bibliographic_records'], 1)
        self.assertEqual(payload['item_copies'], 2)
        self.assertEqual(payload['available_copies'], 1)
        self.assertEqual(payload['active_loans'], 1)
        self.assertEqual(payload['overdue_loans'], 1)
        self.assertEqual(payload['queued_reservations'], 1)
        self.assertEqual(payload['active_blocks'], 1)
        self.assertEqual(payload['active_inventory_campaigns'], 1)
        self.assertEqual(payload['matched_inventory_reads'], 1)
        self.assertEqual(payload['unmatched_inventory_reads'], 1)
        self.assertEqual(payload['inventory_accuracy_rate'], 50.0)