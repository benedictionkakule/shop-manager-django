from django.contrib import admin

from .models import Category, Customer, Product, Sale, SaleItem, Supplier


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "price", "quantity", "reorder_level")
    list_filter = ("category", "supplier")
    search_fields = ("name", "sku")


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "customer", "served_by")
    inlines = [SaleItemInline]


admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(Customer)

from django.contrib.admin.models import LogEntry


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ("action_time", "user", "content_type", "object_repr", "action_flag")
    list_filter = ("action_flag", "user")
    date_hierarchy = "action_time"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
