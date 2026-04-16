from django.contrib import admin

from .models import EmailNotificationLog


@admin.register(EmailNotificationLog)
class EmailNotificationLogAdmin(admin.ModelAdmin):
    list_display = ('notification_type', 'recipient_email', 'status', 'target_model', 'sent_at', 'created_at')
    list_filter = ('notification_type', 'status')
    search_fields = ('recipient_email', 'subject', 'target_model', 'target_id')
    readonly_fields = ('sent_at', 'created_at', 'updated_at')
