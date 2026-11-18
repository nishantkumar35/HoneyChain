from django.contrib import admin
from .models import Apiary


@admin.register(Apiary)
class ApiaryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'beekeeper', 'location', 'get_colony_count', 'created_at')
    list_filter   = ('beekeeper',)
    search_fields = ('name', 'location', 'beekeeper__username')
    readonly_fields = ('created_at',)

    def get_colony_count(self, obj):
        return obj.get_colony_count()
    get_colony_count.short_description = 'Colonies'

