from django.contrib import admin

from .models import InventoryCampaign, InventoryRead, InventoryScanSession


@admin.register(InventoryCampaign)
class InventoryCampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'library_branch', 'status', 'started_at', 'ended_at')
    list_filter = ('status', 'library_branch')
    search_fields = ('name',)


@admin.register(InventoryScanSession)
class InventoryScanSessionAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'operator', 'device_label', 'started_at', 'ended_at')
    list_filter = ('campaign',)
    search_fields = ('device_label', 'source_hint')


@admin.register(InventoryRead)
class InventoryReadAdmin(admin.ModelAdmin):
    list_display = ('scanned_code', 'campaign', 'match_status', 'scan_source', 'read_at')
    list_filter = ('match_status', 'scan_source', 'campaign')
    search_fields = ('scanned_code', 'item_copy__asset_code', 'item_copy__bibliographic_record__title')
