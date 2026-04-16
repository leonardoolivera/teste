from rest_framework import serializers

from .models import Author, BibliographicRecord, ItemCopy, Subject


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BibliographicRecordSerializer(serializers.ModelSerializer):
    author_ids = serializers.PrimaryKeyRelatedField(source='authors', queryset=Author.objects.all(), many=True, required=False)
    subject_ids = serializers.PrimaryKeyRelatedField(source='subjects', queryset=Subject.objects.all(), many=True, required=False)

    class Meta:
        model = BibliographicRecord
        fields = [
            'id',
            'title',
            'subtitle',
            'isbn',
            'publication_year',
            'publisher',
            'language',
            'edition_statement',
            'classification_code',
            'cutter',
            'description',
            'author_ids',
            'subject_ids',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ItemCopySerializer(serializers.ModelSerializer):
    bibliographic_title = serializers.CharField(source='bibliographic_record.title', read_only=True)

    class Meta:
        model = ItemCopy
        fields = [
            'id',
            'bibliographic_record',
            'bibliographic_title',
            'library_branch',
            'asset_code',
            'tomb_number',
            'barcode',
            'rfid_tag',
            'shelf_location',
            'status',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'bibliographic_title']
