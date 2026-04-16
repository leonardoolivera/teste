import csv

from django.http import HttpResponse
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsOperator
from .models import InventoryCampaign, InventoryRead, InventoryScanSession
from .serializers import InventoryCampaignSerializer, InventoryReadSerializer, InventoryScanInputSerializer, InventoryScanSessionSerializer


class InventoryCampaignViewSet(viewsets.ModelViewSet):
    queryset = InventoryCampaign.objects.select_related('library_branch', 'opened_by').all()
    serializer_class = InventoryCampaignSerializer
    permission_classes = [IsOperator]
    search_fields = ['name']
    filterset_fields = ['status', 'library_branch']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(opened_by=self.request.user)

    @action(detail=True, methods=['get'], url_path='export-reads')
    def export_reads(self, request, pk=None):
        campaign = self.get_object()
        reads = campaign.reads.select_related('session', 'operator', 'item_copy__bibliographic_record').all()

        match_status = request.query_params.get('match_status')
        scan_source = request.query_params.get('scan_source')
        if match_status:
            reads = reads.filter(match_status=match_status)
        if scan_source:
            reads = reads.filter(scan_source=scan_source)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="inventory_{campaign.id}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'campaign',
            'session',
            'operator',
            'scanned_code',
            'scan_source',
            'match_status',
            'item_asset_code',
            'item_title',
            'device_label',
            'read_at',
        ])
        for read in reads:
            writer.writerow([
                campaign.name,
                read.session_id or '',
                read.operator.email if read.operator else '',
                read.scanned_code,
                read.scan_source,
                read.match_status,
                read.item_copy.asset_code if read.item_copy else '',
                read.item_copy.bibliographic_record.title if read.item_copy else '',
                read.device_label,
                read.read_at.isoformat(),
            ])

        return response


class InventoryScanSessionViewSet(viewsets.ModelViewSet):
    queryset = InventoryScanSession.objects.select_related('campaign', 'operator').all()
    serializer_class = InventoryScanSessionSerializer
    permission_classes = [IsOperator]
    filterset_fields = ['campaign', 'operator']
    ordering = ['-started_at']

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user)


class InventoryReadViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = InventoryRead.objects.select_related('campaign', 'session', 'operator', 'item_copy__bibliographic_record').all()
    serializer_class = InventoryReadSerializer
    permission_classes = [IsOperator]
    filterset_fields = ['campaign', 'session', 'match_status', 'scan_source']
    search_fields = ['scanned_code', 'item_copy__asset_code', 'item_copy__bibliographic_record__title']
    ordering = ['-read_at']


class InventoryScanReadCreateApi(APIView):
    permission_classes = [IsOperator]

    def post(self, request):
        serializer = InventoryScanInputSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        inventory_read = serializer.save()
        output = InventoryReadSerializer(inventory_read)
        return Response(output.data, status=status.HTTP_201_CREATED)
