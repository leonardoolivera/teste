from django.contrib import admin

from .models import Loan, Reservation, ReturnReceipt


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('patron', 'item_copy', 'status', 'due_at', 'returned_at')
    list_filter = ('status',)
    search_fields = ('patron__full_name', 'item_copy__asset_code')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('bibliographic_record', 'patron', 'pickup_branch', 'status', 'queue_position')
    list_filter = ('status', 'pickup_branch')
    search_fields = ('bibliographic_record__title', 'patron__full_name')


@admin.register(ReturnReceipt)
class ReturnReceiptAdmin(admin.ModelAdmin):
    list_display = ('loan', 'return_token', 'returned_by', 'created_at')
    search_fields = ('return_token', 'loan__item_copy__asset_code')
