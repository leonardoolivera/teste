from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LoanViewSet, ReservationViewSet, ReturnReceiptTokenLookupApi, ReturnReceiptViewSet

router = DefaultRouter()
router.register('loans', LoanViewSet, basename='circulation-loan')
router.register('reservations', ReservationViewSet, basename='circulation-reservation')
router.register('return-receipts', ReturnReceiptViewSet, basename='circulation-return-receipt')

urlpatterns = [
    path('', include(router.urls)),
    path('return-token/<str:token>/', ReturnReceiptTokenLookupApi.as_view(), name='circulation-return-token-lookup'),
]
