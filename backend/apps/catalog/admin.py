from django.contrib import admin

from .models import Author, BibliographicRecord, ItemCopy, Subject


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(BibliographicRecord)
class BibliographicRecordAdmin(admin.ModelAdmin):
    list_display = ('title', 'isbn', 'publication_year', 'publisher')
    search_fields = ('title', 'isbn', 'publisher')
    filter_horizontal = ('authors', 'subjects')


@admin.register(ItemCopy)
class ItemCopyAdmin(admin.ModelAdmin):
    list_display = ('asset_code', 'bibliographic_record', 'library_branch', 'status', 'barcode')
    list_filter = ('status', 'library_branch')
    search_fields = ('asset_code', 'barcode', 'rfid_tag', 'bibliographic_record__title')
