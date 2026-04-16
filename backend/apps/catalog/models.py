from django.db import models

from apps.core.models import TimestampedModel


class Author(TimestampedModel):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Subject(TimestampedModel):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class BibliographicRecord(TimestampedModel):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    isbn = models.CharField(max_length=32, blank=True)
    publication_year = models.PositiveIntegerField(null=True, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    language = models.CharField(max_length=30, default='pt-BR')
    edition_statement = models.CharField(max_length=100, blank=True)
    classification_code = models.CharField(max_length=50, blank=True)
    cutter = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    authors = models.ManyToManyField(Author, related_name='records', blank=True)
    subjects = models.ManyToManyField(Subject, related_name='records', blank=True)

    class Meta:
        ordering = ['title']

    def __str__(self) -> str:
        return self.title


class ItemCopy(TimestampedModel):
    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        LOANED = 'loaned', 'Loaned'
        RESERVED = 'reserved', 'Reserved'
        PROCESSING = 'processing', 'Processing'
        LOST = 'lost', 'Lost'
        DISCARDED = 'discarded', 'Discarded'

    bibliographic_record = models.ForeignKey(BibliographicRecord, on_delete=models.CASCADE, related_name='copies')
    library_branch = models.ForeignKey('core.LibraryBranch', on_delete=models.CASCADE, related_name='copies')
    asset_code = models.CharField(max_length=50, unique=True)
    tomb_number = models.CharField(max_length=50, blank=True)
    barcode = models.CharField(max_length=80, unique=True, null=True, blank=True)
    rfid_tag = models.CharField(max_length=80, unique=True, null=True, blank=True)
    shelf_location = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.AVAILABLE)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['asset_code']

    def __str__(self) -> str:
        return f'{self.asset_code} - {self.bibliographic_record.title}'
