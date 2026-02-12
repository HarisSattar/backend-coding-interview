from django.contrib import admin
from .models import Photographer

@admin.register(Photographer)
class PhotographerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'url', 'created_at']
    search_fields = ['name']
    readonly_fields = ['id', 'created_at', 'updated_at']
