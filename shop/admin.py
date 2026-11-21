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


from .models import Review, Wishlist, StoreSlide, OwnerProfile


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["product", "author_name", "rating", "is_approved", "created_at"]
    list_filter = ["store", "is_approved"]
    search_fields = ["author_name", "product__name", "text"]


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ["user", "product", "store", "created_at"]
    list_filter = ["store"]


@admin.register(StoreSlide)
class StoreSlideAdmin(admin.ModelAdmin):
    list_display = ["title", "store", "position", "is_active"]
    list_filter = ["store", "is_active"]


@admin.register(OwnerProfile)
class OwnerProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "phone"]


from .models import SupportTicket, SupportReply, ReturnRequest, PaymentReceipt

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display=['subject','name','contact','status','created_at']
    list_filter=['store','status']
    search_fields=['subject','name','contact']

@admin.register(SupportReply)
class SupportReplyAdmin(admin.ModelAdmin):
    list_display=['ticket','actor','created_at']
    readonly_fields=['ticket','actor','body','created_at']

@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display=['order','status','created_at']
    list_filter=['store','status']

@admin.register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display=['order','status','created_at','reviewed_by']
    list_filter=['store','status']
    readonly_fields=['store','order','image','created_at','reviewed_at','reviewed_by']


from .models import ContactMessage, CooperationRequest

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["full_name", "store", "subject", "status", "created_at"]
    list_filter = ["store", "subject", "status"]
    search_fields = ["full_name", "phone"]
    readonly_fields = ["store", "full_name", "phone", "subject", "message", "created_at", "updated_at"]

@admin.register(CooperationRequest)
class CooperationRequestAdmin(admin.ModelAdmin):
    list_display = ["full_name", "company", "store", "cooperation_type", "status", "created_at"]
    list_filter = ["store", "cooperation_type", "status"]
    search_fields = ["full_name", "company", "phone"]
    readonly_fields = ["store", "full_name", "phone", "company", "cooperation_type", "details", "created_at", "updated_at"]
