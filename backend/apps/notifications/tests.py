from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from apps.catalog.models import BibliographicRecord, ItemCopy
from apps.core.models import Campus, Institution, LibraryBranch
from apps.users.models import Patron, User

from .models import EmailNotificationLog
from .services import notify_loan_created, notify_overdue_loan, notify_reservation_available


class NotificationServicesTests(APITestCase):
    def setUp(self):
        self.institution = Institution.objects.create(name='IFMS', code='IFMS')
        self.campus = Campus.objects.create(institution=self.institution, name='Campus CG', code='CG')
        self.branch = LibraryBranch.objects.create(campus=self.campus, name='Biblioteca Central', code='BC')
        self.record = BibliographicRecord.objects.create(title='Python Aplicado')
        self.item = ItemCopy.objects.create(
            bibliographic_record=self.record,
            library_branch=self.branch,
            asset_code='PAT-500',
            barcode='BAR-500',
        )
        self.operator = User.objects.create_user(
            email='bibliotecario@ifms.edu.br',
            password='teste123',
            role='librarian',
            library_branch=self.branch,
        )
        self.patron = Patron.objects.create(
            library_branch=self.branch,
            registration_code='2026500',
            full_name='Clara Reis',
            email='clara@ifms.edu.br',
            category='student',
            status='active',
        )

    def test_notify_loan_created_creates_sent_notification_log(self):
        from apps.circulation.models import Loan

        loan = Loan.objects.create(
            patron=self.patron,
            item_copy=self.item,
            checked_out_by=self.operator,
            due_at=timezone.now() + timedelta(days=7),
            status='open',
            fine_amount='0.00',
        )

        notification = notify_loan_created(loan)
        notification.refresh_from_db()

        self.assertEqual(notification.notification_type, EmailNotificationLog.NotificationType.LOAN_CREATED)
        self.assertEqual(notification.status, EmailNotificationLog.Status.SENT)
        self.assertEqual(EmailNotificationLog.objects.count(), 1)

    def test_notify_overdue_loan_creates_sent_notification_log(self):
        from apps.circulation.models import Loan

        loan = Loan.objects.create(
            patron=self.patron,
            item_copy=self.item,
            checked_out_by=self.operator,
            due_at=timezone.now() - timedelta(days=3),
            status='overdue',
            fine_amount='4.50',
        )

        notification = notify_overdue_loan(loan, days_overdue=3)
        notification.refresh_from_db()

        self.assertEqual(notification.notification_type, EmailNotificationLog.NotificationType.OVERDUE_REMINDER)
        self.assertEqual(notification.status, EmailNotificationLog.Status.SENT)
        self.assertIn('Dias em atraso: 3', notification.body)

    def test_notify_reservation_available_creates_sent_notification_log(self):
        from apps.circulation.models import Reservation

        reservation = Reservation.objects.create(
            patron=self.patron,
            bibliographic_record=self.record,
            pickup_branch=self.branch,
            fulfilled_item_copy=self.item,
            status=Reservation.Status.AVAILABLE,
            queue_position=1,
            expires_at=timezone.now() + timedelta(hours=24),
        )

        notification = notify_reservation_available(reservation)
        notification.refresh_from_db()

        self.assertEqual(notification.notification_type, EmailNotificationLog.NotificationType.RESERVATION_AVAILABLE)
        self.assertEqual(notification.status, EmailNotificationLog.Status.SENT)
        self.assertIn('reserva esta disponivel', notification.body.lower())
