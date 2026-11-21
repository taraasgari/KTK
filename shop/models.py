"""Owned KTK data models (no imports from other shop packages)."""
import uuid

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Store(models.Model):
    name = models.CharField("نام فروشگاه", max_length=120)
    slug = models.SlugField(unique=True)
    tagline = models.CharField("شعار", max_length=220, blank=True, default="خرید هوشمند، انتخاب ماندگار")
    description = models.TextField("درباره فروشگاه", blank=True)
    description_en = models.TextField("درباره فروشگاه انگلیسی", blank=True)
    description_zh = models.TextField("درباره فروشگاه چینی", blank=True)
    contact_phone = models.CharField("تلفن", max_length=30, blank=True)
    contact_email = models.EmailField("ایمیل", blank=True)
    contact_address = models.TextField("آدرس تماس", blank=True)
    contact_address_en = models.TextField("آدرس تماس انگلیسی", blank=True)
    contact_address_zh = models.TextField("آدرس تماس چینی", blank=True)
    is_active = models.BooleanField(default=True)
    logo = models.ImageField("لوگو", upload_to="branding/", blank=True)
    favicon = models.ImageField("فاوآیکون", upload_to="branding/", blank=True)
    instagram = models.URLField("اینستاگرام", blank=True)
    telegram = models.URLField("تلگرام", blank=True)
    footer_text = models.CharField("متن فوتر", max_length=240, blank=True)
    footer_text_en = models.CharField("متن فوتر انگلیسی", max_length=240, blank=True)
    footer_text_zh = models.CharField("متن فوتر چینی", max_length=240, blank=True)
    primary_color = models.CharField("رنگ اصلی", max_length=7, default="#C8102E")
    payment_method = models.CharField("روش پرداخت", max_length=24, choices=[("cod", "پرداخت هنگام تحویل"), ("transfer", "کارت به کارت")], default="cod")
    payment_card_number = models.CharField("شماره کارت", max_length=24, blank=True)
    payment_account_name = models.CharField("نام صاحب حساب", max_length=120, blank=True)
    payment_instructions = models.TextField("توضیحات پرداخت", blank=True)
    email_sender_name = models.CharField("نام فرستنده ایمیل", max_length=120, blank=True)
    support_email = models.EmailField("ایمیل پشتیبانی", blank=True)
    hero_title = models.CharField("عنوان اصلی سایت", max_length=160, blank=True)
    hero_title_en = models.CharField("عنوان اصلی انگلیسی", max_length=160, blank=True)
    hero_title_zh = models.CharField("عنوان اصلی چینی", max_length=160, blank=True)
    hero_subtitle = models.CharField("توضیح اصلی سایت", max_length=300, blank=True)
    hero_subtitle_en = models.CharField("توضیح اصلی انگلیسی", max_length=300, blank=True)
    hero_subtitle_zh = models.CharField("توضیح اصلی چینی", max_length=300, blank=True)

    def _localized(self, field):
        from django.utils.translation import get_language
        lang = get_language() or "fa"
        suffix = "_en" if lang.startswith("en") else "_zh" if lang.startswith("zh") else ""
        return getattr(self, field + suffix, "") or getattr(self, field, "")

    @property
    def display_contact_address(self): return self._localized("contact_address")

    @property
    def display_description(self): return self._localized("description")

    @property
    def display_footer_text(self): return self._localized("footer_text")

    @property
    def display_hero_title(self): return self._localized("hero_title")

    @property
    def display_hero_subtitle(self): return self._localized("hero_subtitle")
    show_benefits = models.BooleanField("نمایش مزیت‌ها", default=True)
    show_about = models.BooleanField("نمایش درباره فروشگاه", default=True)
    number_format = models.CharField("نمایش اعداد", max_length=8, choices=[("fa", "فارسی"), ("en", "انگلیسی")], default="fa")

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
    permissions = models.JSONField(default=None, null=True, blank=True, help_text="دسترسی‌های اختصاصی؛ فهرست خالی یعنی دسترسی پیش‌فرض نقش")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["store", "user"], name="unique_store_membership")]

    def __str__(self):
        return f"{self.user} / {self.store} ({self.role})"


class Category(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)
    name_en = models.CharField("دسته‌بندی انگلیسی", max_length=100, blank=True)
    name_zh = models.CharField("دسته‌بندی چینی", max_length=100, blank=True)

    @property
    def display_name(self):
        from django.utils.translation import get_language
        lang = get_language() or "fa"
        if lang.startswith("en") and self.name_en:
            return self.name_en
        if lang.startswith("zh") and self.name_zh:
            return self.name_zh
        return self.name

    slug = models.SlugField(max_length=110)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    image = models.ImageField("تصویر دسته‌بندی", upload_to="categories/", blank=True)

    class Meta:
        ordering = ["position", "name"]
        constraints = [models.UniqueConstraint(fields=["store", "slug"], name="unique_store_category_slug")]

    def __str__(self):
        return self.name


class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name="products")
    name = models.CharField(max_length=180)
    name_en = models.CharField("نام انگلیسی", max_length=180, blank=True)
    name_zh = models.CharField("نام چینی", max_length=180, blank=True)
    description_en = models.TextField("توضیحات انگلیسی", blank=True)
    description_zh = models.TextField("توضیحات چینی", blank=True)
    features_fa = models.TextField("ویژگی‌ها (هر خط یک مورد)", blank=True)
    features_en = models.TextField("ویژگی‌ها انگلیسی", blank=True)
    features_zh = models.TextField("ویژگی‌ها چینی", blank=True)
    material = models.CharField("جنس", max_length=120, blank=True)
    material_en = models.CharField("جنس انگلیسی", max_length=120, blank=True)
    material_zh = models.CharField("جنس چینی", max_length=120, blank=True)
    dimensions = models.CharField("ابعاد", max_length=120, blank=True)
    dimensions_en = models.CharField("ابعاد انگلیسی", max_length=120, blank=True)
    dimensions_zh = models.CharField("ابعاد چینی", max_length=120, blank=True)
    packaging = models.CharField("بسته‌بندی", max_length=120, blank=True)
    packaging_en = models.CharField("بسته‌بندی انگلیسی", max_length=120, blank=True)
    packaging_zh = models.CharField("بسته‌بندی چینی", max_length=120, blank=True)
    usage = models.CharField("کاربرد", max_length=150, blank=True)
    usage_en = models.CharField("کاربرد انگلیسی", max_length=150, blank=True)
    usage_zh = models.CharField("کاربرد چینی", max_length=150, blank=True)
    slug = models.SlugField(max_length=190)
    sku = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)
    price = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    stock = models.PositiveIntegerField(default=0)
    SIZE_CHOICES = [("a4", "A4"), ("a5", "A5"), ("custom", "سفارشی")]
    size = models.CharField("ابعاد محصول", max_length=16, choices=SIZE_CHOICES, blank=True)
    compare_at_price = models.PositiveBigIntegerField("قیمت پیش از تخفیف", blank=True, null=True)
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

    def _localized(self, field):
        from django.utils.translation import get_language
        lang = get_language() or "fa"
        suffix = "_en" if lang.startswith("en") else "_zh" if lang.startswith("zh") else ""
        return getattr(self, field + suffix, "") or getattr(self, field, "")

    @property
    def display_name(self):
        return self._localized("name")

    @property
    def display_description(self):
        return self._localized("description")

    @property
    def display_features(self):
        from django.utils.translation import get_language
        lang = get_language() or "fa"
        value = self.features_en if lang.startswith("en") else self.features_zh if lang.startswith("zh") else ""
        return [line.strip() for line in (value or self.features_fa).splitlines() if line.strip()]

    @property
    def display_usage(self): return self._localized("usage")

    @property
    def display_material(self): return self._localized("material")

    @property
    def display_dimensions(self): return self._localized("dimensions")

    @property
    def display_packaging(self): return self._localized("packaging")

    @property
    def display_specs(self):
        from django.utils.translation import gettext as _
        specs = [(str(_("Brand")), "KTK"),
                 (str(_("SKU")), self.sku),
                 (str(_("Material")), self._localized("material")),
                 (str(_("Dimensions")), self._localized("dimensions")),
                 (str(_("Packaging")), self._localized("packaging")),
                 (str(_("Application")), self._localized("usage"))]
        return [(a, b) for a, b in specs if b]

    @property
    def discount_percent(self):
        if self.compare_at_price and self.compare_at_price > self.price:
            return round((self.compare_at_price - self.price) * 100 / self.compare_at_price)
        return 0

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField("تصویر گالری", upload_to="product_gallery/%Y/%m/")
    alt_fa = models.CharField("توضیح تصویر", max_length=140, blank=True)
    alt_en = models.CharField("توضیح انگلیسی تصویر", max_length=140, blank=True)
    alt_zh = models.CharField("توضیح چینی تصویر", max_length=140, blank=True)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "pk"]

    @property
    def display_alt(self):
        from django.utils.translation import get_language
        lang = get_language() or "fa"
        return (self.alt_en if lang.startswith("en") else self.alt_zh if lang.startswith("zh") else self.alt_fa) or self.product.display_name

    def __str__(self):
        return str(self.product) + " / " + str(self.pk)


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


class Review(models.Model):
    """Moderated real customer feedback; no fabricated review counters."""
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    author_name = models.CharField(max_length=100)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField(max_length=2000)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Wishlist(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="wishlist_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlist_items")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist_items")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["store", "user", "product"], name="unique_ktk_wishlist")]


class StoreSlide(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="slides")
    title = models.CharField("عنوان اسلاید", max_length=140)
    title_en = models.CharField("عنوان اسلاید انگلیسی", max_length=140, blank=True)
    title_zh = models.CharField("عنوان اسلاید چینی", max_length=140, blank=True)
    subtitle = models.CharField("زیرعنوان", max_length=220, blank=True)
    subtitle_en = models.CharField("زیرعنوان انگلیسی", max_length=220, blank=True)
    subtitle_zh = models.CharField("زیرعنوان چینی", max_length=220, blank=True)

    @property
    def display_title(self):
        from django.utils.translation import get_language
        lang = get_language() or 'fa'
        return (self.title_en if lang.startswith('en') else self.title_zh if lang.startswith('zh') else self.title) or self.title

    @property
    def display_subtitle(self):
        from django.utils.translation import get_language
        lang = get_language() or 'fa'
        return (self.subtitle_en if lang.startswith('en') else self.subtitle_zh if lang.startswith('zh') else self.subtitle) or self.subtitle
    image = models.ImageField("تصویر", upload_to="slides/")
    link = models.CharField("لینک", max_length=250, blank=True)
    position = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["position", "pk"]


class OwnerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ktk_profile")
    image = models.ImageField("تصویر پروفایل", upload_to="profiles/", blank=True)
    phone = models.CharField("تلفن", max_length=30, blank=True)
    address = models.TextField("آدرس", blank=True)


class SupportTicket(models.Model):
    STATUSES = [("open", "باز"), ("answered", "پاسخ داده شده"), ("closed", "بسته")]
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="support_tickets")
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField("نام", max_length=120)
    contact = models.CharField("شماره تماس", max_length=160)
    email = models.EmailField("ایمیل", blank=True)
    order_number = models.CharField("شماره سفارش", max_length=36, blank=True)
    subject = models.CharField("موضوع", max_length=160)
    body = models.TextField("متن درخواست", max_length=5000)
    status = models.CharField(max_length=16, choices=STATUSES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.subject


class SupportReply(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="replies")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    body = models.TextField("پاسخ", max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


class ReturnRequest(models.Model):
    STATUSES = [("pending", "در انتظار"), ("reviewing", "در حال بررسی"), ("approved", "تأیید"), ("rejected", "رد شده")]
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="return_requests")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="return_requests")
    reason = models.TextField("علت درخواست", max_length=4000)
    status = models.CharField(max_length=16, choices=STATUSES, default="pending")
    owner_note = models.TextField("یادداشت رسیدگی", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


class PaymentReceipt(models.Model):
    """Customer-supplied transfer image; review does not confirm an actual bank deposit."""
    STATUSES = [('pending','در انتظار بررسی'),('accepted','فیش بررسی شد'),('rejected','رد شده')]
    store = models.ForeignKey(Store,on_delete=models.CASCADE,related_name='payment_receipts')
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='payment_receipts')
    image = models.ImageField(upload_to='payment-receipts/%Y/%m/')
    status = models.CharField(max_length=16,choices=STATUSES,default='pending')
    note = models.CharField(max_length=500,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True,blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True)

    class Meta:
        ordering = ['-created_at']


class ContactMessage(models.Model):
    SUBJECTS = [("consultation", "مشاوره خرید"), ("order", "پیگیری سفارش"), ("support", "پشتیبانی محصولات"), ("wholesale", "خرید عمده"), ("cooperation", "همکاری"), ("other", "سایر موارد")]
    STATUSES = [("new", "جدید"), ("read", "بررسی شده"), ("replied", "پاسخ داده شده")]
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="contact_messages")
    full_name = models.CharField("نام و نام خانوادگی", max_length=120)
    phone = models.CharField("شماره تماس", max_length=20)
    subject = models.CharField("موضوع پیام", max_length=24, choices=SUBJECTS)
    message = models.TextField("متن پیام", max_length=3000)
    status = models.CharField("وضعیت", max_length=16, choices=STATUSES, default="new")
    owner_note = models.TextField("یادداشت داخلی", max_length=2000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.get_subject_display()}"


class CooperationRequest(models.Model):
    TYPES = [("distribution", "پخش و توزیع"), ("agency", "نمایندگی فروش"), ("corporate", "همکاری سازمانی"), ("supply", "تأمین محصول"), ("marketing", "تبلیغات و بازاریابی"), ("other", "سایر همکاری‌ها")]
    STATUSES = [("new", "جدید"), ("reviewing", "در حال بررسی"), ("contacted", "تماس گرفته شد"), ("approved", "پذیرفته شده"), ("rejected", "رد شده")]
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="cooperation_requests")
    full_name = models.CharField("نام و نام خانوادگی", max_length=120)
    company = models.CharField("نام مجموعه", max_length=160, blank=True)
    cooperation_type = models.CharField("نوع همکاری", max_length=24, choices=TYPES)
    phone = models.CharField("شماره تماس", max_length=20)
    details = models.TextField("توضیحات", max_length=3000, blank=True)
    status = models.CharField("وضعیت", max_length=16, choices=STATUSES, default="new")
    owner_note = models.TextField("یادداشت داخلی", max_length=2000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.get_cooperation_type_display()}"
