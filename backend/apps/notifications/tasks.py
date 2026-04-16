from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import EmailNotificationLog


@shared_task
def deliver_email_notification(notification_id: str) -> None:
    notification = EmailNotificationLog.objects.get(id=notification_id)

    if not notification.recipient_email:
        notification.status = EmailNotificationLog.Status.SKIPPED
        notification.error_message = 'Recipient email is empty.'
        notification.save(update_fields=['status', 'error_message', 'updated_at'])
        return

    try:
        send_mail(
            subject=notification.subject,
            message=notification.body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.recipient_email],
            fail_silently=False,
        )
        notification.status = EmailNotificationLog.Status.SENT
        notification.sent_at = timezone.now()
        notification.error_message = ''
        notification.save(update_fields=['status', 'sent_at', 'error_message', 'updated_at'])
    except Exception as exc:
        notification.status = EmailNotificationLog.Status.FAILED
        notification.error_message = str(exc)
        notification.save(update_fields=['status', 'error_message', 'updated_at'])
