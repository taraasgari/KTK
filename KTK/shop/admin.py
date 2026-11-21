from django.contrib import admin
from .models import Category, Membership, Order, OrderItem, Product, StockMovement, Store


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active"]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ["store", "user", "role"]
    list_filter = ["store", "role"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "store", "is_active"]
    list_filter = ["store"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "store", "price", "stock", "is_active"]
    list_filter = ["store", "is_active"]
    search_fields = ["name", "sku"]


class ItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product", "name_snapshot", "price_snapshot", "quantity"]
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["public_id", "store", "customer_name", "total_price", "status", "created_at"]
    list_filter = ["store", "status"]
    inlines = [ItemInline]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ["product", "delta", "reason", "created_at"]
    readonly_fields = ["product", "delta", "reason", "actor", "created_at"]
