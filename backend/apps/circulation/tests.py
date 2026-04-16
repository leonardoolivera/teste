from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from rest_framework.test import APITestCase

from apps.catalog.models import BibliographicRecord, ItemCopy
from apps.core.models import Campus, Institution, LibraryBranch
from apps.notifications.models import EmailNotificationLog
from apps.users.models import Patron, PatronBlock, User

from .models import Loan, Reservation, ReturnReceipt
from .services import process_expired_reservations, process_overdue_loans


class CirculationApiTests(APITestCase):
    def setUp(self):
        self.institution = Institution.objects.create(name='IFMS', code='IFMS')
        self.campus = Campus.objects.create(institution=self.institution, name='Campus CG', code='CG')
        self.branch = LibraryBranch.objects.create(campus=self.campus, name='Biblioteca Central', code='BC')
        self.record = BibliographicRecord.objects.create(title='Dominando Django')
        self.item = ItemCopy.objects.create(
            bibliographic_record=self.record,
            library_branch=self.branch,
            asset_code='PAT-200',
            barcode='BAR-200',
            status='available',
        )
        self.operator = User.objects.create_user(
            email='bibliotecario@ifms.edu.br',
            password='teste123',
            role='librarian',
            library_branch=self.branch,
        )
        self.other_patron = Patron.objects.create(
            library_branch=self.branch,
            registration_code='2026003',
            full_name='Ana Costa',
            email='ana@ifms.edu.br',
            category='student',
            status='active',
        )
        self.third_patron = Patron.objects.create(
            library_branch=self.branch,
            registration_code='2026004',
            full_name='Paulo Dias',
            email='paulo@ifms.edu.br',
            category='student',
            status='active',
        )
        self.patron = Patron.objects.create(
            library_branch=self.branch,
            registration_code='2026002',
            full_name='Joao Lima',
            email='joao@ifms.edu.br',
            category='student',
            status='active',
        )

    def create_loan(self, *, patron=None, item=None, due_at=None, status='open'):
        return Loan.objects.create(
            patron=patron or self.patron,
            item_copy=item or self.item,
            checked_out_by=self.operator,
            due_at=due_at or timezone.now() + timedelta(days=7),
            status=status,
            fine_amount='0.00',
        )

    def test_create_loan_requires_authenticated_operator(self):
        response = self.client.post(
            '/api/v1/circulation/loans/',
            {
                'patron': str(self.patron.id),
                'item_copy': str(self.item.id),
                'due_at': (timezone.now() + timedelta(days=7)).isoformat(),
                'status': 'open',
                'fine_amount': '0.00',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 401)

    def test_create_loan_updates_copy_status_operator_and_notification(self):
        self.client.force_authenticate(user=self.operator)
        response = self.client.post(
            '/api/v1/circulation/loans/',
            {
                'patron': str(self.patron.id),
                'item_copy': str(self.item.id),
                'due_at': (timezone.now() + timedelta(days=7)).isoformat(),
                'status': 'open',
                'fine_amount': '0.00',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, 'loaned')
        self.assertEqual(response.json()['checked_out_by'], str(self.operator.id))
        notification = EmailNotificationLog.objects.get(notification_type=EmailNotificationLog.NotificationType.LOAN_CREATED)
        self.assertEqual(notification.status, EmailNotificationLog.Status.SENT)
        self.assertEqual(notification.recipient_email, 'joao@ifms.edu.br')

    def test_create_reservation_immediately_holds_available_copy_and_notifies_patron(self):
        self.client.force_authenticate(user=self.operator)

        response = self.client.post(
            '/api/v1/circulation/reservations/',
            {
                'patron': str(self.other_patron.id),
                'bibliographic_record': str(self.record.id),
                'pickup_branch': str(self.branch.id),
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.item.refresh_from_db()
        reservation = Reservation.objects.get(id=response.json()['id'])
        self.assertEqual(self.item.status, 'reserved')
        self.assertEqual(reservation.status, Reservation.Status.AVAILABLE)
        self.assertEqual(reservation.fulfilled_item_copy_id, self.item.id)
        notification = EmailNotificationLog.objects.get(notification_type=EmailNotificationLog.NotificationType.RESERVATION_AVAILABLE)
        self.assertEqual(notification.status, EmailNotificationLog.Status.SENT)
        self.assertEqual(notification.recipient_email, 'ana@ifms.edu.br')

    def test_return_receipt_marks_loan_returned_uses_operator_and_sends_notification(self):
        loan = self.create_loan()
        self.item.status = 'loaned'
        self.item.save(update_fields=['status', 'updated_at'])
        self.client.force_authenticate(user=self.operator)

        response = self.client.post(
            '/api/v1/circulation/return-receipts/',
            {
                'loan': str(loan.id),
                'notes': 'Devolucao sem avarias',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        loan.refresh_from_db()
        self.item.refresh_from_db()
        self.assertEqual(loan.status, 'returned')
        self.assertEqual(self.item.status, 'available')
        self.assertEqual(response.json()['returned_by'], str(self.operator.id))
        notification = EmailNotificationLog.objects.get(notification_type=EmailNotificationLog.NotificationType.RETURN_RECEIPT)
        self.assertEqual(notification.status, EmailNotificationLog.Status.SENT)
        self.assertIn(response.json()['return_token'], notification.body)

    def test_return_receipt_promotes_next_reservation_and_reserves_copy(self):
        loan = self.create_loan()
        self.item.status = 'loaned'
        self.item.save(update_fields=['status', 'updated_at'])
        reservation = Reservation.objects.create(
            patron=self.other_patron,
            bibliographic_record=self.record,
            pickup_branch=self.branch,
            status=Reservation.Status.QUEUED,
            queue_position=1,
        )
        self.client.force_authenticate(user=self.operator)

        response = self.client.post(
            '/api/v1/circulation/return-receipts/',
            {
                'loan': str(loan.id),
                'notes': 'Item devolvido para fila de reserva',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.item.refresh_from_db()
        reservation.refresh_from_db()
        self.assertEqual(self.item.status, 'reserved')
        self.assertEqual(reservation.status, Reservation.Status.AVAILABLE)
        self.assertEqual(reservation.fulfilled_item_copy_id, self.item.id)
        notification = EmailNotificationLog.objects.filter(
            notification_type=EmailNotificationLog.NotificationType.RESERVATION_AVAILABLE,
            recipient_email='ana@ifms.edu.br',
        ).latest('created_at')
        self.assertEqual(notification.status, EmailNotificationLog.Status.SENT)

    def test_reserved_copy_can_be_loaned_to_patron_with_available_reservation(self):
        Reservation.objects.create(
            patron=self.other_patron,
            bibliographic_record=self.record,
            pickup_branch=self.branch,
            fulfilled_item_copy=self.item,
            status=Reservation.Status.AVAILABLE,
            queue_position=1,
            expires_at=timezone.now() + timedelta(hours=24),
        )
        self.item.status = 'reserved'
        self.item.save(update_fields=['status', 'updated_at'])
        self.client.force_authenticate(user=self.operator)

        response = self.client.post(
            '/api/v1/circulation/loans/',
            {
                'patron': str(self.other_patron.id),
                'item_copy': str(self.item.id),
                'due_at': (timezone.now() + timedelta(days=7)).isoformat(),
                'status': 'open',
                'fine_amount': '0.00',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.item.refresh_from_db()
        reservation = Reservation.objects.get(patron=self.other_patron, bibliographic_record=self.record)
        self.assertEqual(self.item.status, 'loaned')
        self.assertEqual(reservation.status, Reservation.Status.FULFILLED)

    def test_can_renew_open_loan(self):
        loan = self.create_loan()
        original_due_at = loan.due_at
        self.item.status = 'loaned'
        self.item.save(update_fields=['status', 'updated_at'])
        self.client.force_authenticate(user=self.operator)

        response = self.client.post(f'/api/v1/circulation/loans/{loan.id}/renew/', {'extra_days': 5}, format='json')

        self.assertEqual(response.status_code, 200)
        loan.refresh_from_db()
        self.assertGreater(loan.due_at, original_due_at)

    def test_renew_is_blocked_by_pending_reservation(self):
        loan = self.create_loan()
        self.item.status = 'loaned'
        self.item.save(update_fields=['status', 'updated_at'])
        Reservation.objects.create(
            patron=self.other_patron,
            bibliographic_record=self.record,
            pickup_branch=self.branch,
            status=Reservation.Status.QUEUED,
            queue_position=1,
        )
        self.client.force_authenticate(user=self.operator)

        response = self.client.post(f'/api/v1/circulation/loans/{loan.id}/renew/', {'extra_days': 5}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('reservation', response.json()['detail'].lower())

    def test_can_lookup_return_token(self):
        loan = self.create_loan()
        self.item.status = 'loaned'
        self.item.save(update_fields=['status', 'updated_at'])
        receipt = ReturnReceipt.objects.create(loan=loan, returned_by=self.operator, notes='ok')

        response = self.client.get(f'/api/v1/circulation/return-token/{receipt.return_token}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['return_token'], receipt.return_token)
        self.assertEqual(response.json()['item_asset_code'], 'PAT-200')

    def test_process_overdue_loans_marks_overdue_and_blocks_patron(self):
        loan = self.create_loan(due_at=timezone.now() - timedelta(days=2))
        self.item.status = 'loaned'
        self.item.save(update_fields=['status', 'updated_at'])

        summary = process_overdue_loans()

        loan.refresh_from_db()
        self.patron.refresh_from_db()
        block = PatronBlock.objects.get(patron=self.patron, reason='Automatic block due to overdue loans')
        notification = EmailNotificationLog.objects.get(notification_type=EmailNotificationLog.NotificationType.OVERDUE_REMINDER)
        self.assertEqual(loan.status, 'overdue')
        self.assertEqual(loan.fine_amount, Decimal('3.00'))
        self.assertEqual(self.patron.status, 'blocked')
        self.assertTrue(block.is_active)
        self.assertEqual(summary['loans_marked_overdue'], 1)
        self.assertEqual(summary['overdue_notifications_sent'], 1)
        self.assertEqual(notification.recipient_email, 'joao@ifms.edu.br')

    def test_return_of_overdue_loan_releases_automatic_block(self):
        loan = self.create_loan(due_at=timezone.now() - timedelta(days=2))
        self.item.status = 'loaned'
        self.item.save(update_fields=['status', 'updated_at'])
        process_overdue_loans()
        self.client.force_authenticate(user=self.operator)

        response = self.client.post(
            '/api/v1/circulation/return-receipts/',
            {
                'loan': str(loan.id),
                'notes': 'Devolucao de item atrasado',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.patron.refresh_from_db()
        block = PatronBlock.objects.get(patron=self.patron, reason='Automatic block due to overdue loans')
        self.assertEqual(self.patron.status, 'active')
        self.assertFalse(block.is_active)

    def test_process_expired_reservations_promotes_next_patron(self):
        expired_reservation = Reservation.objects.create(
            patron=self.other_patron,
            bibliographic_record=self.record,
            pickup_branch=self.branch,
            fulfilled_item_copy=self.item,
            status=Reservation.Status.AVAILABLE,
            queue_position=1,
            expires_at=timezone.now() - timedelta(hours=2),
        )
        next_reservation = Reservation.objects.create(
            patron=self.third_patron,
            bibliographic_record=self.record,
            pickup_branch=self.branch,
            status=Reservation.Status.QUEUED,
            queue_position=2,
        )
        self.item.status = 'reserved'
        self.item.save(update_fields=['status', 'updated_at'])

        summary = process_expired_reservations()

        expired_reservation.refresh_from_db()
        next_reservation.refresh_from_db()
        self.item.refresh_from_db()
        notification = EmailNotificationLog.objects.filter(
            notification_type=EmailNotificationLog.NotificationType.RESERVATION_AVAILABLE,
            recipient_email='paulo@ifms.edu.br',
        ).latest('created_at')
        self.assertEqual(summary['reservations_expired'], 1)
        self.assertEqual(summary['reservations_promoted'], 1)
        self.assertEqual(expired_reservation.status, Reservation.Status.EXPIRED)
        self.assertEqual(next_reservation.status, Reservation.Status.AVAILABLE)
        self.assertEqual(next_reservation.queue_position, 1)
        self.assertEqual(next_reservation.fulfilled_item_copy_id, self.item.id)
        self.assertEqual(self.item.status, 'reserved')
        self.assertEqual(notification.status, EmailNotificationLog.Status.SENT)
