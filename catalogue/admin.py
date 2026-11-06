from django.contrib import admin

from .models import Asset, AuditLog, Project


class AssetInline(admin.TabularInline):
    model = Asset
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at")
    list_filter = ("owner",)
    search_fields = ("name",)
    inlines = [AssetInline]


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "asset_type", "is_public")
    list_filter = ("asset_type", "is_public")
    search_fields = ("name", "project__name")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Read-only view: the audit trail must not be edited or deleted."""

    list_display = (
        "created_at",
        "user",
        "action",
        "object_type",
        "object_id",
        "object_repr",
    )
    list_filter = ("action", "object_type")
    search_fields = ("object_repr", "username")
    readonly_fields = (
        "user",
        "username",
        "action",
        "object_type",
        "object_id",
        "object_repr",
        "changes",
        "created_at",
    )

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
