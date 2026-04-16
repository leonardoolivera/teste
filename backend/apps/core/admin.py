from django.contrib import admin

from .models import AuditLog, Campus, Institution, LibraryBranch


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'institution', 'city', 'state')
    list_filter = ('institution',)
    search_fields = ('name', 'code', 'city', 'state')


@admin.register(LibraryBranch)
class LibraryBranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'campus', 'email', 'is_active')
    list_filter = ('campus', 'is_active')
    search_fields = ('name', 'code', 'email')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'target_model', 'target_id', 'actor', 'created_at')
    list_filter = ('action', 'target_model')
    search_fields = ('target_model', 'target_id')
    readonly_fields = ('created_at', 'updated_at')
