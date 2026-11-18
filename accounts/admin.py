"""
Accounts Admin Registration
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import BeekeeperProfile


class BeekeeperProfileInline(admin.StackedInline):
    """Show beekeeper profile fields inline on the User admin page."""
    model = BeekeeperProfile
    can_delete = False
    verbose_name_plural = 'Beekeeper Profile'
    fields = ('phone', 'address', 'created_at')
    readonly_fields = ('created_at',)


class UserAdmin(BaseUserAdmin):
    """Extended User admin with BeekeeperProfile inline."""
    inlines = [BeekeeperProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')


# Re-register User with our extended admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(BeekeeperProfile)
class BeekeeperProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'phone', 'address', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone')
    readonly_fields = ('created_at',)

