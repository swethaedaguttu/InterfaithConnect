# events/admin.py

from django.contrib import admin
from .models import Community

@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'is_interfaith')  # Fields to display
    search_fields = ('name', 'created_by__username')  # Fields to search in the admin interface
