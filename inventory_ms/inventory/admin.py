from django.contrib import admin
from .models import InventoryItem, Category, InventoryChange

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'quantity', 'price', 'created_by', 'date_added']
    list_filter = ['category', 'date_added']
    search_fields = ['name', 'description']
    readonly_fields = ['date_added', 'last_updated']

@admin.register(InventoryChange)
class InventoryChangeAdmin(admin.ModelAdmin):
    list_display = ['item', 'change_type', 'user', 'previous_quantity', 'new_quantity', 'timestamp']
    list_filter = ['change_type', 'timestamp']
    readonly_fields = ['item', 'user', 'change_type', 'previous_quantity', 'new_quantity', 'change_amount', 'timestamp', 'notes']
    
    def has_add_permission(self, request):
        return False