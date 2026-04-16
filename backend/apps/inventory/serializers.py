from rest_framework import serializers

from .models import InventoryCampaign, InventoryRead, InventoryScanSession
from .services import register_scan


class InventoryCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryCampaign
        fields = ['id', 'library_branch', 'name', 'status', 'opened_by', 'started_at', 'ended_at', 'notes', 'created_at']
        read_only_fields = ['id', 'opened_by', 'created_at']


class InventoryScanSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryScanSession
        fields = ['id', 'campaign', 'operator', 'device_label', 'source_hint', 'started_at', 'ended_at', 'notes']
        read_only_fields = ['id', 'operator', 'started_at']


class InventoryReadSerializer(serializers.ModelSerializer):
    item_asset_code = serializers.CharField(source='item_copy.asset_code', read_only=True)
    item_title = serializers.CharField(source='item_copy.bibliographic_record.title', read_only=True)

    class Meta:
        model = InventoryRead
        fields = ['id', 'campaign', 'session', 'operator', 'item_copy', 'item_asset_code', 'item_title', 'scanned_code', 'scan_source', 'match_status', 'device_label', 'read_at']
        read_only_fields = ['id', 'operator', 'item_copy', 'match_status', 'read_at', 'item_asset_code', 'item_title']


class InventoryScanInputSerializer(serializers.Serializer):
    campaign_id = serializers.UUIDField()
    session_id = serializers.UUIDField(required=False, allow_null=True)
    scanned_code = serializers.CharField(max_length=120)
    scan_source = serializers.ChoiceField(choices=InventoryRead.ScanSource.choices)
    device_label = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate(self, attrs):
        try:
            attrs['campaign'] = InventoryCampaign.objects.get(id=attrs['campaign_id'])
        except InventoryCampaign.DoesNotExist as exc:
            raise serializers.ValidationError({'campaign_id': 'Campaign not found.'}) from exc

        session_id = attrs.get('session_id')
        if session_id:
            try:
                attrs['session'] = InventoryScanSession.objects.get(id=session_id)
            except InventoryScanSession.DoesNotExist as exc:
                raise serializers.ValidationError({'session_id': 'Session not found.'}) from exc
            if attrs['session'].campaign_id != attrs['campaign'].id:
                raise serializers.ValidationError({'session_id': 'Session does not belong to campaign.'})
        else:
            attrs['session'] = None

        request = self.context.get('request')
        attrs['operator'] = request.user if request and request.user.is_authenticated else None

        return attrs

    def create(self, validated_data):
        return register_scan(
            campaign=validated_data['campaign'],
            session=validated_data['session'],
            operator=validated_data['operator'],
            scanned_code=validated_data['scanned_code'],
            scan_source=validated_data['scan_source'],
            device_label=validated_data.get('device_label', ''),
        )
