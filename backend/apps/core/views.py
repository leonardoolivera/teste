from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import BibliographicRecord, ItemCopy
from apps.circulation.models import Loan, Reservation
from apps.inventory.models import InventoryCampaign, InventoryRead
from apps.users.models import PatronBlock

from apps.core.permissions import IsOperator, IsReadOnlyOrOperator

from .models import Campus, Institution, LibraryBranch
from .serializers import CampusSerializer, InstitutionSerializer, LibraryBranchSerializer


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                'status': 'ok',
                'app': 'IFMS Biblioteca Plataforma',
                'version': '0.1.0',
                'debug': settings.DEBUG,
                'time_zone': settings.TIME_ZONE,
            }
        )


class DashboardOverviewApi(APIView):
    permission_classes = [IsOperator]

    def get(self, request):
        matched_reads = InventoryRead.objects.filter(match_status=InventoryRead.MatchStatus.MATCHED).count()
        unmatched_reads = InventoryRead.objects.filter(match_status=InventoryRead.MatchStatus.UNMATCHED).count()
        total_reads = matched_reads + unmatched_reads
        inventory_accuracy_rate = round((matched_reads / total_reads) * 100, 1) if total_reads else 0.0

        return Response(
            {
                'generated_at': timezone.now().isoformat(),
                'institutions': Institution.objects.count(),
                'branches': LibraryBranch.objects.count(),
                'active_branches': LibraryBranch.objects.filter(is_active=True).count(),
                'bibliographic_records': BibliographicRecord.objects.count(),
                'item_copies': ItemCopy.objects.count(),
                'available_copies': ItemCopy.objects.filter(status=ItemCopy.Status.AVAILABLE).count(),
                'active_loans': Loan.objects.filter(returned_at__isnull=True).count(),
                'overdue_loans': Loan.objects.filter(status=Loan.Status.OVERDUE, returned_at__isnull=True).count(),
                'queued_reservations': Reservation.objects.filter(status=Reservation.Status.QUEUED).count(),
                'active_blocks': PatronBlock.objects.filter(is_active=True).count(),
                'active_inventory_campaigns': InventoryCampaign.objects.filter(status=InventoryCampaign.Status.ACTIVE).count(),
                'matched_inventory_reads': matched_reads,
                'unmatched_inventory_reads': unmatched_reads,
                'inventory_accuracy_rate': inventory_accuracy_rate,
            }
        )


class InstitutionViewSet(viewsets.ModelViewSet):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    permission_classes = [IsReadOnlyOrOperator]
    search_fields = ['name', 'code']
    filterset_fields = ['is_active']
    ordering = ['name']


class CampusViewSet(viewsets.ModelViewSet):
    queryset = Campus.objects.select_related('institution').all()
    serializer_class = CampusSerializer
    permission_classes = [IsReadOnlyOrOperator]
    search_fields = ['name', 'code', 'city', 'state', 'institution__name']
    filterset_fields = ['institution']
    ordering = ['name']


class LibraryBranchViewSet(viewsets.ModelViewSet):
    queryset = LibraryBranch.objects.select_related('campus', 'campus__institution').all()
    serializer_class = LibraryBranchSerializer
    permission_classes = [IsReadOnlyOrOperator]
    search_fields = ['name', 'code', 'email', 'phone', 'campus__name', 'campus__institution__name']
    filterset_fields = ['campus', 'campus__institution', 'is_active']
    ordering = ['name']