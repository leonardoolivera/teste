from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AuthorViewSet, BibliographicRecordViewSet, ItemCopyViewSet, SubjectViewSet

router = DefaultRouter()
router.register('authors', AuthorViewSet, basename='catalog-author')
router.register('subjects', SubjectViewSet, basename='catalog-subject')
router.register('records', BibliographicRecordViewSet, basename='catalog-record')
router.register('copies', ItemCopyViewSet, basename='catalog-copy')

urlpatterns = [
    path('', include(router.urls)),
]
