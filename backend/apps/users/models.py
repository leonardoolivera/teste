import uuid

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import TimestampedModel


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The email field must be set.')
        email = self.normalize_email(email)
        username = extra_fields.pop('username', email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        LIBRARIAN = 'librarian', 'Librarian'
        ASSISTANT = 'assistant', 'Assistant'
        MANAGER = 'manager', 'Manager'
        INTEGRATION = 'integration', 'Integration'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True, blank=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=30, choices=Role.choices, default=Role.ASSISTANT)
    library_branch = models.ForeignKey(
        'core.LibraryBranch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff_users',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.email


class Patron(TimestampedModel):
    class Category(models.TextChoices):
        STUDENT = 'student', 'Student'
        TEACHER = 'teacher', 'Teacher'
        STAFF = 'staff', 'Staff'
        EXTERNAL = 'external', 'External'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        BLOCKED = 'blocked', 'Blocked'
        INACTIVE = 'inactive', 'Inactive'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patron_profile',
    )
    library_branch = models.ForeignKey(
        'core.LibraryBranch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patrons',
    )
    registration_code = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.STUDENT)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.ACTIVE)
    expires_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['full_name']

    def __str__(self) -> str:
        return f'{self.full_name} ({self.registration_code})'


class PatronBlock(TimestampedModel):
    patron = models.ForeignKey(Patron, on_delete=models.CASCADE, related_name='blocks')
    reason = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.patron.full_name}: {self.reason}'
