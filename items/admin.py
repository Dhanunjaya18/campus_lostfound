from django.contrib import admin
from .models import Category, Item


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'category', 'location', 'posted_by', 'date_posted']
    list_filter = ['status', 'category']
    search_fields = ['title', 'description', 'location']
    list_editable = ['status']
    date_hierarchy = 'date_posted'
    readonly_fields = ['date_posted']
