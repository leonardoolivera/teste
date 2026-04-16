from django.db import models

from apps.core.models import TimestampedModel


class EmailNotificationLog(TimestampedModel):
    class NotificationType(models.TextChoices):
        LOAN_CREATED = 'loan_created', 'Loan Created'
        RETURN_RECEIPT = 'return_receipt', 'Return Receipt'
        OVERDUE_REMINDER = 'overdue_reminder', 'Overdue Reminder'
        RESERVATION_AVAILABLE = 'reservation_available', 'Reservation Available'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SENT = 'sent', 'Sent'
        SKIPPED = 'skipped', 'Skipped'
        FAILED = 'failed', 'Failed'

    notification_type = models.CharField(max_length=50, choices=NotificationType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    recipient_email = models.EmailField(blank=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    target_model = models.CharField(max_length=100)
    target_id = models.CharField(max_length=100)
    payload = models.JSONField(default=dict, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.notification_type} -> {self.recipient_email or "no-email"}'
