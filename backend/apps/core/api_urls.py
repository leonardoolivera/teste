from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CampusViewSet, DashboardOverviewApi, InstitutionViewSet, LibraryBranchViewSet

router = DefaultRouter()
router.register('institutions', InstitutionViewSet, basename='institution')
router.register('campuses', CampusViewSet, basename='campus')
router.register('branches', LibraryBranchViewSet, basename='library-branch')

urlpatterns = [
    path('dashboard/overview/', DashboardOverviewApi.as_view(), name='dashboard-overview'),
] + router.urls