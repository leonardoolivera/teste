from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from apps.catalog.models import BibliographicRecord, ItemCopy
from apps.core.models import Campus, Institution, LibraryBranch
from apps.users.models import Patron
from apps.circulation.models import Loan, Reservation


class PatronPortalAuthTests(APITestCase):
    def setUp(self):
        self.institution = Institution.objects.create(name='IFMS', code='IFMS')
        self.campus = Campus.objects.create(institution=self.institution, name='Campus CG', code='CG')
        self.branch = LibraryBranch.objects.create(campus=self.campus, name='Biblioteca Central', code='BC')
        self.patron = Patron.objects.create(
            library_branch=self.branch,
            registration_code='2026001',
            full_name='Maria Silva',
            email='maria@ifms.edu.br',
            category='student',
            status='active',
        )

    def test_set_password_creates_user_and_returns_token(self):
        response = self.client.post('/api/v1/portal/auth/set-password/', {
            'registration_code': '2026001',
            'password': 'senha123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['patron']['registration_code'], '2026001')
        self.patron.refresh_from_db()
        self.assertIsNotNone(self.patron.user)

    def test_login_after_set_password(self):
        self.client.post('/api/v1/portal/auth/set-password/', {
            'registration_code': '2026001',
            'password': 'senha123',
        })
        response = self.client.post('/api/v1/portal/auth/login/', {
            'registration_code': '2026001',
            'password': 'senha123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_login_wrong_password_returns_400(self):
        self.client.post('/api/v1/portal/auth/set-password/', {
            'registration_code': '2026001',
            'password': 'senha123',
        })
        response = self.client.post('/api/v1/portal/auth/login/', {
            'registration_code': '2026001',
            'password': 'senhaerrada',
        })
        self.assertEqual(response.status_code, 400)

    def test_login_without_password_returns_403_must_set(self):
        response = self.client.post('/api/v1/portal/auth/login/', {
            'registration_code': '2026001',
            'password': 'qualquercoisa',
        })
        self.assertEqual(response.status_code, 403)
        self.assertTrue(response.data.get('must_set_password'))

    def test_me_requires_auth(self):
        response = self.client.get('/api/v1/portal/auth/me/')
        self.assertEqual(response.status_code, 401)

    def test_me_returns_patron_data(self):
        self.client.post('/api/v1/portal/auth/set-password/', {
            'registration_code': '2026001',
            'password': 'senha123',
        })
        login = self.client.post('/api/v1/portal/auth/login/', {
            'registration_code': '2026001',
            'password': 'senha123',
        })
        token = login.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.get('/api/v1/portal/auth/me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['full_name'], 'Maria Silva')

    def test_inactive_patron_cannot_login(self):
        self.patron.status = Patron.Status.INACTIVE
        self.patron.save()
        response = self.client.post('/api/v1/portal/auth/login/', {
            'registration_code': '2026001',
            'password': 'qualquer',
        })
        self.assertEqual(response.status_code, 403)


class PatronPortalMyAccountTests(APITestCase):
    def setUp(self):
        self.institution = Institution.objects.create(name='IFMS', code='IFMS2')
        self.campus = Campus.objects.create(institution=self.institution, name='Campus Aquidauana', code='AQ')
        self.branch = LibraryBranch.objects.create(campus=self.campus, name='Biblioteca AQ', code='BAQ')
        self.record = BibliographicRecord.objects.create(title='Python Fluente')
        self.item = ItemCopy.objects.create(
            bibliographic_record=self.record,
            library_branch=self.branch,
            asset_code='PAT-AQ-001',
            status='loaned',
        )
        self.patron = Patron.objects.create(
            library_branch=self.branch,
            registration_code='2026010',
            full_name='Carlos Rocha',
            email='carlos@ifms.edu.br',
            category='student',
            status='active',
        )
        self.client.post('/api/v1/portal/auth/set-password/', {
            'registration_code': '2026010',
            'password': 'senha456',
        })
        login = self.client.post('/api/v1/portal/auth/login/', {
            'registration_code': '2026010',
            'password': 'senha456',
        })
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {login.data["token"]}')
        self.loan = Loan.objects.create(
            patron=self.patron,
            item_copy=self.item,
            due_at=timezone.now() + timedelta(days=14),
            status='open',
        )

    def test_my_loans_returns_loan(self):
        response = self.client.get('/api/v1/portal/my/loans/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['record_title'], 'Python Fluente')

    def test_my_reservations_empty(self):
        response = self.client.get('/api/v1/portal/my/reservations/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_renew_loan_extends_due_date(self):
        original_due = self.loan.due_at
        response = self.client.post(f'/api/v1/portal/my/loans/{self.loan.id}/renew/')
        self.assertEqual(response.status_code, 200)
        self.loan.refresh_from_db()
        self.assertGreater(self.loan.due_at, original_due)

    def test_renew_blocks_when_reservation_pending(self):
        other_patron = Patron.objects.create(
            library_branch=self.branch,
            registration_code='2026011',
            full_name='Beatriz Melo',
            email='beatriz@ifms.edu.br',
            category='student',
            status='active',
        )
        Reservation.objects.create(
            patron=other_patron,
            bibliographic_record=self.record,
            pickup_branch=self.branch,
            status=Reservation.Status.QUEUED,
            queue_position=1,
        )
        response = self.client.post(f'/api/v1/portal/my/loans/{self.loan.id}/renew/')
        self.assertEqual(response.status_code, 400)
