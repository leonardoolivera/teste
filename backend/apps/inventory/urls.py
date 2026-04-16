from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import InventoryCampaignViewSet, InventoryReadViewSet, InventoryScanReadCreateApi, InventoryScanSessionViewSet

router = DefaultRouter()
router.register('campaigns', InventoryCampaignViewSet, basename='inventory-campaign')
router.register('scan-sessions', InventoryScanSessionViewSet, basename='inventory-scan-session')
router.register('reads', InventoryReadViewSet, basename='inventory-read')

urlpatterns = [
    path('', include(router.urls)),
    path('scan-reads/', InventoryScanReadCreateApi.as_view(), name='inventory-scan-read-create'),
]
