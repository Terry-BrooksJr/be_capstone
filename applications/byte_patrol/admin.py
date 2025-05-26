from django.contrib import admin

from .models import IPAllowList, ProtectedPath


@admin.register(IPAllowList)
class IPAllowListAdmin(admin.ModelAdmin):
    list_display = ("ip_address", "description", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("ip_address", "description")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ProtectedPath)
class ProtectedPathAdmin(admin.ModelAdmin):
    list_display = ("path_pattern", "description", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("path_pattern", "description")
    readonly_fields = ("created_at", "updated_at")
