import uuid

from django.conf import settings
from django.db import models


class TimestampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Institution(TimestampedModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Campus(TimestampedModel):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='campuses')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['name']
        unique_together = ('institution', 'code')

    def __str__(self) -> str:
        return f'{self.name} ({self.code})'


class LibraryBranch(TimestampedModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name='library_branches')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        unique_together = ('campus', 'code')

    def __str__(self) -> str:
        return f'{self.name} - {self.campus.name}'


class AuditLog(TimestampedModel):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    action = models.CharField(max_length=100)
    target_model = models.CharField(max_length=100)
    target_id = models.CharField(max_length=100)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.action} on {self.target_model}'
