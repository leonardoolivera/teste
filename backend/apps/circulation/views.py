from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsOperator
from .models import Loan, Reservation, ReturnReceipt
from .serializers import LoanRenewSerializer, LoanSerializer, ReservationSerializer, ReturnReceiptLookupSerializer, ReturnReceiptSerializer


class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.select_related('patron', 'item_copy__bibliographic_record', 'checked_out_by').all()
    serializer_class = LoanSerializer
    permission_classes = [IsOperator]
    filterset_fields = ['status', 'patron', 'item_copy']
    search_fields = ['patron__full_name', 'item_copy__asset_code']
    ordering = ['-loaned_at']

    def perform_create(self, serializer):
        serializer.save(checked_out_by=self.request.user)

    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        loan = self.get_object()
        if loan.status != Loan.Status.OPEN:
            return Response({'detail': 'Only open loans can be renewed.'}, status=status.HTTP_400_BAD_REQUEST)

        has_pending_reservation = loan.item_copy.bibliographic_record.reservations.filter(
            status__in=[Reservation.Status.QUEUED, Reservation.Status.AVAILABLE]
        ).exclude(patron=loan.patron).exists()
        if has_pending_reservation:
            return Response({'detail': 'Loan cannot be renewed because a reservation is pending.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LoanRenewSerializer(data=request.data or {}, context={'loan': loan})
        serializer.is_valid(raise_exception=True)
        renewed_loan = serializer.save()
        return Response(LoanSerializer(renewed_loan).data)


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related('patron', 'bibliographic_record', 'pickup_branch', 'fulfilled_item_copy').all()
    serializer_class = ReservationSerializer
    permission_classes = [IsOperator]
    filterset_fields = ['status', 'pickup_branch', 'patron']
    search_fields = ['patron__full_name', 'bibliographic_record__title']
    ordering = ['queue_position', 'created_at']


class ReturnReceiptViewSet(viewsets.ModelViewSet):
    queryset = ReturnReceipt.objects.select_related('loan__item_copy__bibliographic_record', 'loan__patron', 'returned_by').all()
    serializer_class = ReturnReceiptSerializer
    permission_classes = [IsOperator]
    filterset_fields = ['loan', 'returned_by']
    search_fields = ['return_token', 'loan__item_copy__asset_code']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(returned_by=self.request.user)


class ReturnReceiptTokenLookupApi(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, token):
        receipt = get_object_or_404(
            ReturnReceipt.objects.select_related('loan__item_copy__bibliographic_record', 'loan__patron', 'returned_by'),
            return_token=token,
        )
        return Response(ReturnReceiptLookupSerializer(receipt).data)
