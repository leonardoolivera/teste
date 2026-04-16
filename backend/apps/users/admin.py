from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Patron, PatronBlock, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'role', 'library_branch', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active', 'library_branch')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'library_branch', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2', 'role', 'is_staff', 'is_superuser'),
            },
        ),
    )


@admin.register(Patron)
class PatronAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'registration_code', 'category', 'status', 'library_branch')
    list_filter = ('category', 'status', 'library_branch')
    search_fields = ('full_name', 'registration_code', 'email')


@admin.register(PatronBlock)
class PatronBlockAdmin(admin.ModelAdmin):
    list_display = ('patron', 'reason', 'is_active', 'expires_at', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('patron__full_name', 'reason')
