from django.contrib import admin
from .models import BeeColony


@admin.register(BeeColony)
class BeeColonyAdmin(admin.ModelAdmin):
    list_display  = ('colony_name', 'apiary', 'colony_type', 'health_status', 'establishment_date')
    list_filter   = ('colony_type', 'health_status', 'apiary')
    search_fields = ('colony_name', 'apiary__name', 'apiary__beekeeper__username')
    readonly_fields = ('created_at',)

