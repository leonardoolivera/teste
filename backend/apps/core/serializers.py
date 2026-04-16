from rest_framework import serializers

from .models import Campus, Institution, LibraryBranch


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ['id', 'name', 'code', 'email', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CampusSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source='institution.name', read_only=True)

    class Meta:
        model = Campus
        fields = ['id', 'institution', 'institution_name', 'name', 'code', 'city', 'state', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'institution_name']


class LibraryBranchSerializer(serializers.ModelSerializer):
    campus_name = serializers.CharField(source='campus.name', read_only=True)
    institution_name = serializers.CharField(source='campus.institution.name', read_only=True)

    class Meta:
        model = LibraryBranch
        fields = [
            'id',
            'campus',
            'campus_name',
            'institution_name',
            'name',
            'code',
            'email',
            'phone',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'campus_name', 'institution_name']
