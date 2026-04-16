import uuid

from django.conf import settings
from django.db import models

from apps.core.models import TimestampedModel


def generate_return_token() -> str:
    return uuid.uuid4().hex


class Loan(TimestampedModel):
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        RETURNED = 'returned', 'Returned'
        OVERDUE = 'overdue', 'Overdue'

    patron = models.ForeignKey('users.Patron', on_delete=models.PROTECT, related_name='loans')
    item_copy = models.ForeignKey('catalog.ItemCopy', on_delete=models.PROTECT, related_name='loans')
    checked_out_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_loans',
    )
    loaned_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.OPEN)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['-loaned_at']

    def __str__(self) -> str:
        return f'{self.patron.full_name} -> {self.item_copy.asset_code}'


class Reservation(TimestampedModel):
    class Status(models.TextChoices):
        QUEUED = 'queued', 'Queued'
        AVAILABLE = 'available', 'Available'
        FULFILLED = 'fulfilled', 'Fulfilled'
        EXPIRED = 'expired', 'Expired'
        CANCELED = 'canceled', 'Canceled'

    patron = models.ForeignKey('users.Patron', on_delete=models.CASCADE, related_name='reservations')
    bibliographic_record = models.ForeignKey('catalog.BibliographicRecord', on_delete=models.CASCADE, related_name='reservations')
    pickup_branch = models.ForeignKey('core.LibraryBranch', on_delete=models.PROTECT, related_name='reservations')
    fulfilled_item_copy = models.ForeignKey(
        'catalog.ItemCopy',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fulfilled_reservations',
    )
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.QUEUED)
    queue_position = models.PositiveIntegerField(default=1)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['queue_position', 'created_at']

    def __str__(self) -> str:
        return f'{self.bibliographic_record.title} for {self.patron.full_name}'


class ReturnReceipt(TimestampedModel):
    loan = models.OneToOneField(Loan, on_delete=models.CASCADE, related_name='return_receipt')
    returned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_returns',
    )
    return_token = models.CharField(max_length=64, unique=True, default=generate_return_token)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.return_token
