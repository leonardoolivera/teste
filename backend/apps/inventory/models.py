from django.conf import settings
from django.db import models

from apps.core.models import TimestampedModel


class InventoryCampaign(TimestampedModel):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        ACTIVE = 'active', 'Active'
        CLOSED = 'closed', 'Closed'

    library_branch = models.ForeignKey('core.LibraryBranch', on_delete=models.CASCADE, related_name='inventory_campaigns')
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)
    opened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='opened_inventory_campaigns',
    )
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.name


class InventoryScanSession(TimestampedModel):
    campaign = models.ForeignKey(InventoryCampaign, on_delete=models.CASCADE, related_name='scan_sessions')
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_scan_sessions',
    )
    device_label = models.CharField(max_length=100, blank=True)
    source_hint = models.CharField(max_length=50, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self) -> str:
        return f'{self.campaign.name} / {self.device_label or self.id}'


class InventoryRead(TimestampedModel):
    class ScanSource(models.TextChoices):
        PATRIMONY = 'patrimony', 'Patrimony'
        BARCODE = 'barcode', 'Barcode'
        RFID = 'rfid', 'RFID'
        CAMERA = 'camera', 'Camera'
        MANUAL = 'manual', 'Manual'

    class MatchStatus(models.TextChoices):
        MATCHED = 'matched', 'Matched'
        UNMATCHED = 'unmatched', 'Unmatched'

    campaign = models.ForeignKey(InventoryCampaign, on_delete=models.CASCADE, related_name='reads')
    session = models.ForeignKey(InventoryScanSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='reads')
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_reads',
    )
    item_copy = models.ForeignKey('catalog.ItemCopy', on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_reads')
    scanned_code = models.CharField(max_length=120)
    scan_source = models.CharField(max_length=30, choices=ScanSource.choices, default=ScanSource.PATRIMONY)
    match_status = models.CharField(max_length=30, choices=MatchStatus.choices, default=MatchStatus.UNMATCHED)
    device_label = models.CharField(max_length=100, blank=True)
    read_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-read_at']

    def __str__(self) -> str:
        return f'{self.scanned_code} ({self.match_status})'
