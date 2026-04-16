from rest_framework import viewsets

from apps.core.permissions import IsReadOnlyOrOperator
from .models import Author, BibliographicRecord, ItemCopy, Subject
from .serializers import AuthorSerializer, BibliographicRecordSerializer, ItemCopySerializer, SubjectSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsReadOnlyOrOperator]
    search_fields = ['name']
    ordering = ['name']


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsReadOnlyOrOperator]
    search_fields = ['name']
    ordering = ['name']


class BibliographicRecordViewSet(viewsets.ModelViewSet):
    queryset = BibliographicRecord.objects.prefetch_related('authors', 'subjects').all()
    serializer_class = BibliographicRecordSerializer
    permission_classes = [IsReadOnlyOrOperator]
    search_fields = ['title', 'isbn', 'publisher']
    ordering = ['title']


class ItemCopyViewSet(viewsets.ModelViewSet):
    queryset = ItemCopy.objects.select_related('bibliographic_record', 'library_branch').all()
    serializer_class = ItemCopySerializer
    permission_classes = [IsReadOnlyOrOperator]
    filterset_fields = ['status', 'library_branch', 'bibliographic_record']
    search_fields = ['asset_code', 'barcode', 'rfid_tag', 'bibliographic_record__title']
    ordering = ['asset_code']
