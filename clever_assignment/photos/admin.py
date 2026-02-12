from django.contrib import admin
from .models import Photo

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'alt', 'photographer', 'owner', 'width', 'height', 'created_at']
    list_filter = ['photographer', 'owner']
    search_fields = ['alt', 'photographer__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
