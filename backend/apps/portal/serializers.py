from rest_framework import serializers

from apps.circulation.models import Loan, Reservation
from apps.users.models import Patron


class PatronLoginSerializer(serializers.Serializer):
    registration_code = serializers.CharField()
    password = serializers.CharField(trim_whitespace=False)


class PatronSetPasswordSerializer(serializers.Serializer):
    registration_code = serializers.CharField()
    password = serializers.CharField(min_length=6, trim_whitespace=False)


class PatronMeSerializer(serializers.ModelSerializer):
    library_branch_name = serializers.SerializerMethodField()

    class Meta:
        model = Patron
        fields = [
            'id', 'registration_code', 'full_name', 'email',
            'category', 'status', 'expires_at',
            'library_branch', 'library_branch_name',
        ]

    def get_library_branch_name(self, obj):
        if obj.library_branch:
            return f'{obj.library_branch.campus.name} - {obj.library_branch.name}'
        return None


class PatronPortalLoanSerializer(serializers.ModelSerializer):
    record_title = serializers.CharField(source='item_copy.bibliographic_record.title', read_only=True)
    record_subtitle = serializers.CharField(source='item_copy.bibliographic_record.subtitle', read_only=True)
    asset_code = serializers.CharField(source='item_copy.asset_code', read_only=True)
    branch_name = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = [
            'id', 'record_title', 'record_subtitle', 'asset_code',
            'branch_name', 'loaned_at', 'due_at', 'returned_at',
            'status', 'fine_amount',
        ]

    def get_branch_name(self, obj):
        branch = obj.item_copy.library_branch
        if branch:
            return f'{branch.campus.name} - {branch.name}'
        return None


class PatronPortalReservationSerializer(serializers.ModelSerializer):
    record_title = serializers.CharField(source='bibliographic_record.title', read_only=True)
    pickup_branch_name = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = [
            'id', 'record_title', 'pickup_branch', 'pickup_branch_name',
            'status', 'queue_position', 'expires_at', 'created_at',
        ]

    def get_pickup_branch_name(self, obj):
        branch = obj.pickup_branch
        return f'{branch.campus.name} - {branch.name}'
