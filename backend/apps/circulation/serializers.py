from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from apps.catalog.models import ItemCopy
from apps.notifications.services import notify_loan_created, notify_return_receipt_created
from apps.users.models import Patron

from .models import Loan, Reservation, ReturnReceipt
from .services import (
    fulfill_available_reservation_for_loan,
    make_next_reservation_available,
    set_reservation_available,
    sync_patron_overdue_status,
)


class LoanSerializer(serializers.ModelSerializer):
    patron_name = serializers.CharField(source='patron.full_name', read_only=True)
    item_asset_code = serializers.CharField(source='item_copy.asset_code', read_only=True)

    class Meta:
        model = Loan
        fields = ['id', 'patron', 'patron_name', 'item_copy', 'item_asset_code', 'checked_out_by', 'loaned_at', 'due_at', 'returned_at', 'status', 'fine_amount', 'created_at', 'updated_at']
        read_only_fields = ['id', 'checked_out_by', 'loaned_at', 'created_at', 'updated_at', 'patron_name', 'item_asset_code']

    def validate(self, attrs):
        patron = attrs['patron']
        item_copy = attrs['item_copy']
        available_reservation = Reservation.objects.filter(
            patron=patron,
            bibliographic_record=item_copy.bibliographic_record,
            status=Reservation.Status.AVAILABLE,
        ).filter(
            Q(fulfilled_item_copy=item_copy) | Q(fulfilled_item_copy__isnull=True)
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gte=timezone.now())
        ).order_by('queue_position', 'created_at').first()

        if patron.status != Patron.Status.ACTIVE:
            raise serializers.ValidationError({'patron': 'Patron is not active.'})
        if item_copy.status == ItemCopy.Status.AVAILABLE:
            return attrs
        if item_copy.status == ItemCopy.Status.RESERVED and available_reservation is not None:
            return attrs
        raise serializers.ValidationError({'item_copy': 'Item copy is not available for loan.'})

    def create(self, validated_data):
        loan = super().create(validated_data)
        item_copy = loan.item_copy
        item_copy.status = ItemCopy.Status.LOANED
        item_copy.save(update_fields=['status', 'updated_at'])
        fulfill_available_reservation_for_loan(loan)
        notify_loan_created(loan)
        return loan


class LoanRenewSerializer(serializers.Serializer):
    extra_days = serializers.IntegerField(min_value=1, max_value=30, default=7)

    def save(self, **kwargs):
        loan = self.context['loan']
        loan.due_at = loan.due_at + timedelta(days=self.validated_data['extra_days'])
        loan.save(update_fields=['due_at', 'updated_at'])
        return loan


class ReservationSerializer(serializers.ModelSerializer):
    patron_name = serializers.CharField(source='patron.full_name', read_only=True)
    record_title = serializers.CharField(source='bibliographic_record.title', read_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'patron', 'patron_name', 'bibliographic_record', 'record_title', 'pickup_branch', 'fulfilled_item_copy', 'status', 'queue_position', 'expires_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'queue_position', 'created_at', 'updated_at', 'patron_name', 'record_title']

    def validate(self, attrs):
        patron = attrs['patron']
        bibliographic_record = attrs['bibliographic_record']

        if patron.status != Patron.Status.ACTIVE:
            raise serializers.ValidationError({'patron': 'Patron is not active.'})

        duplicate_reservation = Reservation.objects.filter(
            patron=patron,
            bibliographic_record=bibliographic_record,
            status__in=[Reservation.Status.QUEUED, Reservation.Status.AVAILABLE],
        )
        if self.instance is not None:
            duplicate_reservation = duplicate_reservation.exclude(id=self.instance.id)
        if duplicate_reservation.exists():
            raise serializers.ValidationError({'bibliographic_record': 'An active reservation already exists for this patron and title.'})

        return attrs

    def create(self, validated_data):
        active_reservations = Reservation.objects.filter(
            bibliographic_record=validated_data['bibliographic_record'],
            status__in=[Reservation.Status.QUEUED, Reservation.Status.AVAILABLE],
        ).count()
        validated_data['queue_position'] = active_reservations + 1
        reservation = super().create(validated_data)

        if active_reservations == 0:
            available_copy = ItemCopy.objects.filter(
                bibliographic_record=reservation.bibliographic_record,
                library_branch=reservation.pickup_branch,
                status=ItemCopy.Status.AVAILABLE,
            ).order_by('asset_code').first()
            if available_copy is not None:
                set_reservation_available(reservation, available_copy)

        return reservation


class ReturnReceiptSerializer(serializers.ModelSerializer):
    loan_status = serializers.CharField(source='loan.status', read_only=True)

    class Meta:
        model = ReturnReceipt
        fields = ['id', 'loan', 'loan_status', 'returned_by', 'return_token', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'returned_by', 'return_token', 'created_at', 'updated_at', 'loan_status']

    def create(self, validated_data):
        loan = validated_data['loan']
        if hasattr(loan, 'return_receipt'):
            raise serializers.ValidationError({'loan': 'Return receipt already exists for this loan.'})

        receipt = super().create(validated_data)
        loan.status = Loan.Status.RETURNED
        loan.returned_at = timezone.now()
        loan.save(update_fields=['status', 'returned_at', 'updated_at'])

        item_copy = loan.item_copy
        make_next_reservation_available(item_copy)

        sync_patron_overdue_status(loan.patron)
        notify_return_receipt_created(receipt)
        return receipt


class ReturnReceiptLookupSerializer(ReturnReceiptSerializer):
    patron_name = serializers.CharField(source='loan.patron.full_name', read_only=True)
    item_asset_code = serializers.CharField(source='loan.item_copy.asset_code', read_only=True)
    record_title = serializers.CharField(source='loan.item_copy.bibliographic_record.title', read_only=True)

    class Meta(ReturnReceiptSerializer.Meta):
        fields = ReturnReceiptSerializer.Meta.fields + ['patron_name', 'item_asset_code', 'record_title']

