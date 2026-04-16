from rest_framework import serializers

from .models import Patron, PatronBlock, User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'role', 'library_branch', 'is_active', 'is_staff']
        read_only_fields = ['id']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class AuthLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False)


class PatronSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patron
        fields = ['id', 'user', 'library_branch', 'registration_code', 'full_name', 'email', 'category', 'status', 'expires_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PatronBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatronBlock
        fields = ['id', 'patron', 'reason', 'is_active', 'expires_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
