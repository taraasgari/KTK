"""Owned KTK data models (no imports from other shop packages)."""
import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Store(models.Model):
    name = models.CharField("نام فروشگاه", max_length=120)
    slug = models.SlugField(unique=True)
    tagline = models.CharField("شعار", max_length=220, blank=True, default="خرید هوشمند، انتخاب ماندگار")
    description = models.TextField("درباره فروشگاه", blank=True)
    contact_phone = models.CharField("تلفن", max_length=30, blank=True)
    contact_email = models.EmailField("ایمیل", blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Membership(models.Model):
    OWNER = "owner"
    MANAGER = "manager"
    STAFF = "staff"
    ROLES = [(OWNER, "مالک"), (MANAGER, "مدیر"), (STAFF, "کارمند")]
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="store_roles")
    role = models.CharField(max_length=16, choices=ROLES, default=STAFF)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["store", "user"], name="unique_store_membership")]

    def __str__(self):
        return f"{self.user} / {self.store} ({self.role})"


class Category(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=110)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "name"]
        constraints = [models.UniqueConstraint(fields=["store", "slug"], name="unique_store_category_slug")]

    def __str__(self):
        return self.name


class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name="products")
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=190)
    sku = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)
    price = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/%Y/%m/", blank=True)
    featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["store", "slug"], name="unique_store_product_slug"),
            models.UniqueConstraint(fields=["store", "sku"], condition=~models.Q(sku=""), name="unique_store_sku"),
        ]

    def __str__(self):
        return self.name


class StockMovement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock_movements")
    delta = models.IntegerField()
    reason = models.CharField(max_length=160)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Order(models.Model):
    NEW = "new"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELED = "canceled"
    STATUSES = [(NEW, "جدید"), (PROCESSING, "در حال پردازش"), (SHIPPED, "ارسال‌شده"), (DELIVERED, "تحویل‌شده"), (CANCELED, "لغوشده")]
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    store = models.ForeignKey(Store, on_delete=models.PROTECT, related_name="orders")
    customer_name = models.CharField(max_length=120)
    customer_phone = models.CharField(max_length=30)
    address = models.TextField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=18, choices=STATUSES, default=NEW)
    total_price = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.public_id)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    name_snapshot = models.CharField(max_length=180)
    price_snapshot = models.PositiveBigIntegerField()
    quantity = models.PositiveIntegerField()

    @property
    def line_total(self):
        return self.price_snapshot * self.quantity
