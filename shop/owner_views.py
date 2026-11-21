"""Real owner console with explicitly scoped authorization."""
from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, F, Sum, Q, Value, IntegerField
from django.db.models.functions import Coalesce
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse
from django.utils.http import url_has_allowed_host_and_scheme
import csv
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.conf import settings as django_settings

from .context import active_store
from .forms import (CategoryForm, MembershipForm, OrderStatusForm, ProductForm, StoreForm,
                    AppearanceForm, ProfileForm, NumberFormatForm, StoreSlideForm, OwnerDetailsForm, PaymentSettingsForm, EmailSettingsForm, VisualCustomizerForm)
from .models import Category, Membership, Order, Product, StockMovement, OrderItem, Review, Wishlist, StoreSlide, OwnerProfile, SupportTicket, SupportReply, ReturnRequest, PaymentReceipt, ContactMessage, CooperationRequest


PERMISSION_LABELS = {
    "dashboard_view": "داشبورد", "products_view": "مشاهده محصولات", "products_edit": "ویرایش محصولات",
    "orders_view": "مشاهده سفارش‌ها", "orders_edit": "تغییر وضعیت سفارش",
    "users_view": "مدیریت کاربران", "reviews_view": "مدیریت نظرات",
    "warehouse_view": "مدیریت انبار", "analytics_view": "گزارش‌ها",
    "appearance_edit": "ظاهر و اسلایدر", "category_edit": "دسته‌بندی‌ها",
    "support_view": "مشاهده پشتیبانی", "support_manage": "پاسخ پشتیبانی",
    "returns_manage": "بررسی لغو و مرجوعی",
    "contacts_view": "مشاهده پیام‌های تماس", "contacts_manage": "رسیدگی به پیام‌های تماس",
    "cooperations_view": "مشاهده درخواست‌های همکاری", "cooperations_manage": "رسیدگی به درخواست‌های همکاری",
}
DEFAULT_PERMISSIONS = {
    Membership.MANAGER: set(PERMISSION_LABELS),
    Membership.STAFF: {"dashboard_view", "orders_view", "orders_edit"},
}


def can(member, key):
    if member.role == Membership.OWNER:
        return True
    allowed = (set(member.permissions) if member.permissions is not None
               else DEFAULT_PERMISSIONS.get(member.role, set()))
    return key in allowed


def allow(*roles, permission=None):
    def decorator(fn):
        @login_required
        @wraps(fn)
        def wrapped(request, *args, **kwargs):
            store = active_store()
            if store is None:
                raise Http404("فروشگاه راه‌اندازی نشده است.")
            membership = Membership.objects.filter(store=store, user=request.user).first()
            if membership is None or membership.role not in roles:
                raise PermissionDenied("اجازه دسترسی به این بخش را ندارید.")
            if permission and not can(membership, permission):
                raise PermissionDenied("اجازه دسترسی به این بخش را ندارید.")
            request.ktk_store = store
            request.ktk_membership = membership
            return fn(request, *args, **kwargs)
        return wrapped
    return decorator


FULL = (Membership.OWNER, Membership.MANAGER)
ALL = (*FULL, Membership.STAFF)


def layout(request, **extra):
    member = request.ktk_membership
    return {
        "store": request.ktk_store,
        "member": member,
        "is_owner": member.role == Membership.OWNER,
        "can_products": can(member, "products_view"),
        "can_product_edit": can(member, "products_edit"),
        "can_orders": can(member, "orders_view"),
        "can_users": can(member, "users_view"),
        "can_reviews": can(member, "reviews_view"),
        "can_inventory": can(member, "warehouse_view"),
        "can_analytics": can(member, "analytics_view"),
        "can_appearance": can(member, "appearance_edit"),
        "can_categories": can(member, "category_edit"),
        "can_dashboard": can(member, "dashboard_view"),
        "can_support": can(member, "support_view"),
        "can_returns": can(member, "returns_manage"),
        "can_contacts": can(member, "contacts_view"),
        "can_cooperations": can(member, "cooperations_view"),
        **extra,
    }


@allow(*ALL, permission="dashboard_view")
def dashboard(request):
    if request.ktk_membership.role != Membership.OWNER:
        return redirect("owner:management")
    store = request.ktk_store
    orders = Order.objects.filter(store=store)
    best = (Product.objects.filter(store=store)
            .annotate(sales_count=Coalesce(Sum("orderitem__quantity", filter=~Q(orderitem__order__status=Order.CANCELED)), Value(0), output_field=IntegerField()))
            .filter(sales_count__gt=0).order_by("-sales_count", "name")[:5])
    users = get_user_model().objects.order_by("-date_joined")
    delivered_total = orders.filter(status=Order.DELIVERED).aggregate(value=Sum("total_price"))["value"] or 0
    return render(request, "owner/dashboard.html", layout(request,
        total_products=Product.objects.filter(store=store).count(),
        total_users=users.count(),
        total_orders=orders.count(),
        total_revenue=delivered_total,
        pending_orders=orders.filter(status=Order.NEW).count(),
        total_reviews=Review.objects.filter(store=store).count(),
        total_wishlist=Wishlist.objects.filter(store=store).count(),
        best_products=best,
        owner_details=OwnerProfile.objects.filter(user=request.user).first(),
        recent_users=users[:5],
        recent_orders=orders.order_by("-created_at")[:5],
    ))


@allow(*ALL, permission="products_view")
def products(request):
    queryset = Product.objects.filter(store=request.ktk_store).select_related("category")
    query = request.GET.get("q", "").strip()[:80]
    category_id = request.GET.get("category", "")
    if query:
        queryset = queryset.filter(Q(name__icontains=query) | Q(sku__icontains=query))
    if category_id.isdigit():
        queryset = queryset.filter(category_id=category_id)
    return render(request, "owner/products.html", layout(request, products=queryset[:150],
        query=query, selected_category=category_id,
        categories=Category.objects.filter(store=request.ktk_store)))


@allow(*ALL, permission="products_edit")
def product_edit(request, pk=None):
    store = request.ktk_store
    product = get_object_or_404(Product, store=store, pk=pk) if pk else None
    form = ProductForm(request.POST or None, request.FILES or None, instance=product, store=store)
    # Multiple gallery files are validated independently from the main photo. Do not save
    # anything if an image is corrupt, oversized, or the gallery would exceed 12 images.
    from .models import ProductImage
    from django.core.files.images import get_image_dimensions
    files = request.FILES.getlist("gallery_images") if request.method == "POST" else []
    delete_ids = request.POST.getlist("delete_gallery") if request.method == "POST" else []
    remaining = (product.gallery.exclude(pk__in=delete_ids).count() if product else 0)
    if request.method == "POST":
        if remaining + len(files) > 12:
            form.add_error(None, "برای هر محصول حداکثر ۱۲ تصویر گالری مجاز است.")
        for upload in files:
            if upload.size > 6 * 1024 * 1024 or upload.size == 0:
                form.add_error(None, "حجم هر تصویر باید حداکثر ۶ مگابایت باشد.")
                break
            try:
                width, height = get_image_dimensions(upload)
                if not width or not height:
                    raise ValueError("invalid image")
            except (ValueError, OSError, TypeError):
                form.add_error(None, "یکی از فایل‌های گالری تصویر معتبر نیست.")
                break
            upload.seek(0)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            previous_stock = Product.objects.select_for_update().get(pk=product.pk).stock if product else 0
            record = form.save(commit=False)
            record.store = store
            record.save()
            diff = record.stock - previous_stock
            if diff:
                StockMovement.objects.create(product=record, delta=diff, reason="ویرایش موجودی از پنل", actor=request.user)
            if delete_ids:
                ProductImage.objects.filter(product=record, pk__in=delete_ids).delete()
            start = (ProductImage.objects.filter(product=record).order_by("-position").values_list("position", flat=True).first() or 0) + 1
            for i, upload in enumerate(files):
                ProductImage.objects.create(product=record, image=upload, position=start + i)
        messages.success(request, "محصول ذخیره شد.")
        return redirect("owner:products")
    return render(request, "owner/form.html", layout(request, form=form,
        heading="ویرایش محصول" if product else "محصول جدید", back="owner:products",
        gallery_mode=True, product_gallery=list(product.gallery.all()) if product else []))


@allow(*ALL, permission="category_edit")
def categories(request):
    return render(request, "owner/categories.html", layout(request, categories=Category.objects.filter(store=request.ktk_store)))


@allow(*ALL, permission="category_edit")
def category_edit(request, pk=None):
    instance = get_object_or_404(Category, store=request.ktk_store, pk=pk) if pk else None
    form = CategoryForm(request.POST or None, request.FILES or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        category = form.save(commit=False)
        category.store = request.ktk_store
        category.save()
        messages.success(request, "دسته‌بندی ذخیره شد.")
        return redirect("owner:categories")
    return render(request, "owner/form.html", layout(request, form=form, heading="ویرایش دسته‌بندی" if instance else "دسته‌بندی جدید", back="owner:categories"))


@allow(*ALL, permission="orders_view")
def orders(request):
    status = request.GET.get("status", "")
    queryset = Order.objects.filter(store=request.ktk_store).prefetch_related("items")
    if status in dict(Order.STATUSES):
        queryset = queryset.filter(status=status)
    return render(request, "owner/orders.html", layout(request, orders=queryset, statuses=Order.STATUSES, selected=status))


TRANSITIONS = {
    Order.NEW: {Order.PROCESSING, Order.CANCELED},
    Order.PROCESSING: {Order.SHIPPED, Order.CANCELED},
    Order.SHIPPED: {Order.DELIVERED},
    Order.DELIVERED: set(),
    Order.CANCELED: set(),
}


@allow(*ALL, permission="orders_view")
def order_detail(request, pk):
    order = get_object_or_404(Order, store=request.ktk_store, pk=pk)
    if request.method == "POST":
        if not can(request.ktk_membership, "orders_edit"):
            raise PermissionDenied("اجازه تغییر وضعیت سفارش را ندارید.")
        form = OrderStatusForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data["status"]
            with transaction.atomic():
                locked = Order.objects.select_for_update().get(pk=order.pk, store=request.ktk_store)
                if status not in TRANSITIONS[locked.status]:
                    messages.error(request, "تغییر وضعیت در این مرحله مجاز نیست.")
                else:
                    if status == Order.CANCELED:
                        for item in locked.items.select_related("product"):
                            Product.objects.filter(pk=item.product_id, store=request.ktk_store).update(stock=F("stock") + item.quantity)
                            StockMovement.objects.create(product_id=item.product_id, delta=item.quantity, reason=f"لغو سفارش {str(locked.public_id)[:8]}", actor=request.user)
                    locked.status = status
                    locked.save(update_fields=["status"])
                    messages.success(request, "وضعیت سفارش تغییر کرد.")
            return redirect("owner:order_detail", pk=pk)
    else:
        form = OrderStatusForm(initial={"status": order.status})
    return render(request, "owner/order_detail.html", layout(request, order=order, form=form, allowed=TRANSITIONS[order.status]))


@allow(*ALL, permission="warehouse_view")
def inventory(request):
    products = Product.objects.filter(store=request.ktk_store).order_by("stock", "name")
    movements = StockMovement.objects.filter(product__store=request.ktk_store).select_related("product", "actor")[:20]
    return render(request, "owner/inventory.html", layout(request, products=products, movements=movements,
        low_stock=products.filter(stock__gt=0, stock__lte=5).count(),
        out_stock=products.filter(stock=0).count()))


@allow(Membership.OWNER)
def settings_page(request):
    form = StoreForm(request.POST or None, instance=request.ktk_store)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "تنظیمات فروشگاه ذخیره شد.")
        return redirect("owner:settings")
    return render(request, "owner/form.html", layout(request, form=form, heading="تنظیمات فروشگاه", back="owner:home"))


@allow(Membership.OWNER)
def team(request):
    form = MembershipForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        User = get_user_model()
        username = form.cleaned_data["username"]
        role = form.cleaned_data["role"]
        password = form.cleaned_data["password"]
        with transaction.atomic():
            user = User.objects.filter(username=username).first()
            if user is not None and Membership.objects.filter(store=request.ktk_store, user=user, role=Membership.OWNER).exists():
                form.add_error("username", "نقش مالک را نمی‌توان از بخش اعضای تیم تغییر داد.")
            else:
                if user is None:
                    user = User.objects.create_user(username=username, password=password)
                Membership.objects.update_or_create(store=request.ktk_store, user=user, defaults={"role": role})
                messages.success(request, "دسترسی عضو تیم ثبت شد.")
                return redirect("owner:team")
    members = Membership.objects.filter(store=request.ktk_store).select_related("user")
    return render(request, "owner/team.html", layout(request, form=form, members=members))


@allow(Membership.OWNER)
@require_POST
def team_remove(request, pk):
    membership = get_object_or_404(Membership, store=request.ktk_store, pk=pk)
    if membership.role == Membership.OWNER:
        messages.error(request, "حذف دسترسی مالک از این قسمت ممکن نیست.")
    else:
        membership.delete()
        messages.success(request, "دسترسی عضو تیم لغو شد.")
    return redirect("owner:team")


@allow(*ALL, permission="dashboard_view")
def management(request):
    store = request.ktk_store
    return render(request, "owner/management.html", layout(request,
        total_products=Product.objects.filter(store=store).count(),
        total_orders=Order.objects.filter(store=store).count(),
        total_users=get_user_model().objects.count(),
        pending_orders=Order.objects.filter(store=store, status=Order.NEW).count(),
    ))


@allow(*ALL, permission="users_view")
def users(request):
    accounts = get_user_model().objects.order_by("-date_joined")[:150]
    return render(request, "owner/users.html", layout(request, users=accounts,
        memberships={m.user_id: m for m in Membership.objects.filter(store=request.ktk_store)}))


@allow(*ALL, permission="reviews_view")
def reviews(request):
    queryset = Review.objects.filter(store=request.ktk_store).select_related("product")
    return render(request, "owner/reviews.html", layout(request, reviews=queryset))


@allow(*ALL, permission="reviews_view")
@require_POST
def review_action(request, pk, action):
    review = get_object_or_404(Review, store=request.ktk_store, pk=pk)
    if action == "approve":
        review.is_approved = True
        review.save(update_fields=["is_approved"])
        messages.success(request, "نظر تأیید شد.")
    elif action == "reject":
        review.is_approved = False
        review.save(update_fields=["is_approved"])
        messages.success(request, "تأیید نظر برداشته شد.")
    elif action == "delete":
        review.delete()
        messages.success(request, "نظر حذف شد.")
    else:
        raise Http404()
    return redirect("owner:reviews")


@allow(*ALL, permission="analytics_view")
def analytics(request):
    store = request.ktk_store
    orders = Order.objects.filter(store=store)
    by_status = list(orders.values("status").annotate(count=Count("id"), value=Sum("total_price")).order_by("status"))
    top_products = (Product.objects.filter(store=store)
        .annotate(units=Coalesce(Sum("orderitem__quantity", filter=~Q(orderitem__order__status=Order.CANCELED)), Value(0), output_field=IntegerField()))
        .order_by("-units")[:10])
    for row in by_status:
        row["status_title"] = dict(Order.STATUSES).get(row["status"], row["status"])
    return render(request, "owner/analytics.html", layout(request,
        total_orders=orders.count(), delivered_orders=orders.filter(status=Order.DELIVERED).count(),
        delivered_value=orders.filter(status=Order.DELIVERED).aggregate(s=Sum("total_price"))["s"] or 0,
        by_status=by_status, top_products=top_products))


@allow(*ALL, permission="analytics_view")
def analytics_csv(request):
    resp = HttpResponse(content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = 'attachment; filename="ktk-orders.csv"'
    resp.write("\\ufeff".encode("utf-8").decode("unicode_escape")) if False else None
    resp.write("\ufeff")
    w = csv.writer(resp)
    w.writerow(["شناسه", "نام مشتری", "تاریخ", "وضعیت", "مبلغ سفارش (تومان)"])
    for order in Order.objects.filter(store=request.ktk_store).iterator():
        w.writerow([str(order.public_id), order.customer_name, order.created_at.isoformat(), order.get_status_display(), order.total_price])
    return resp


@allow(*ALL, permission="appearance_edit")
def appearance(request):
    store = request.ktk_store
    form = AppearanceForm(request.POST or None, request.FILES or None, instance=store)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "ظاهر و اطلاعات فروشگاه ذخیره شد.")
        return redirect("owner:appearance")
    return render(request, "owner/appearance.html", layout(request, form=form, slides=StoreSlide.objects.filter(store=store)))


@allow(*ALL, permission="appearance_edit")
def slides(request):
    return render(request, "owner/slides.html", layout(request, slides=StoreSlide.objects.filter(store=request.ktk_store)))


@allow(*ALL, permission="appearance_edit")
def slide_edit(request, pk=None):
    slide = get_object_or_404(StoreSlide, store=request.ktk_store, pk=pk) if pk else None
    form = StoreSlideForm(request.POST or None, request.FILES or None, instance=slide)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.store = request.ktk_store
        obj.save()
        messages.success(request, "اسلایدر ذخیره شد.")
        return redirect("owner:slides")
    return render(request, "owner/form.html", layout(request, form=form, heading="ویرایش اسلاید" if slide else "افزودن اسلاید", back="owner:slides"))


@allow(*ALL, permission="appearance_edit")
@require_POST
def slide_delete(request, pk):
    slide = get_object_or_404(StoreSlide, store=request.ktk_store, pk=pk)
    slide.delete()
    messages.success(request, "اسلایدر حذف شد.")
    return redirect("owner:slides")


@allow(*ALL)
def profile(request):
    details, _ = OwnerProfile.objects.get_or_create(user=request.user)
    account_form = ProfileForm(request.POST or None, instance=request.user, prefix="account")
    details_form = OwnerDetailsForm(request.POST or None, request.FILES or None, instance=details, prefix="details")
    pwd_form = PasswordChangeForm(request.user, request.POST or None, prefix="password")
    if request.method == "POST":
        kind = request.POST.get("action")
        if kind == "account" and account_form.is_valid() and details_form.is_valid():
            account_form.save()
            details_form.save()
            messages.success(request, "پروفایل ذخیره شد.")
            return redirect("owner:profile")
        if kind == "password" and pwd_form.is_valid():
            user = pwd_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "رمز عبور تغییر کرد.")
            return redirect("owner:profile")
    return render(request, "owner/profile.html", layout(request,
        account_form=account_form, details_form=details_form, password_form=pwd_form, owner_details=details))


@allow(Membership.OWNER)
def numbers(request):
    form = NumberFormatForm(request.POST or None, instance=request.ktk_store)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "تنظیمات نمایش اعداد ثبت شد.")
        return redirect("owner:numbers")
    return render(request, "owner/form.html", layout(request, form=form, heading="تنظیمات فرمت اعداد", back="owner:home"))


@allow(Membership.OWNER)
def permissions(request, pk):
    member = get_object_or_404(Membership, pk=pk, store=request.ktk_store)
    if member.role == Membership.OWNER:
        raise PermissionDenied("مجوزهای مالک قابل تغییر نیست.")
    if request.method == "POST":
        allowed_codes = set(PERMISSION_LABELS)
        selected = request.POST.getlist("permissions")
        if any(code not in allowed_codes for code in selected):
            raise PermissionDenied("مجوز نامعتبر است.")
        if request.POST.get("default_role") == "1":
            member.permissions = None
        else:
            member.permissions = sorted(set(selected))
        member.save(update_fields=["permissions"])
        messages.success(request, "دسترسی‌ها ذخیره شد.")
        return redirect("owner:permissions", pk=pk)
    selected = set(member.permissions if member.permissions is not None else DEFAULT_PERMISSIONS.get(member.role, set()))
    return render(request, "owner/permissions.html", layout(request, target=member,
        permission_items=[(code, title, code in selected) for code, title in PERMISSION_LABELS.items()],
        default_role=member.permissions is None))


@allow(*ALL, permission="warehouse_view")
def warehouse_products(request):
    products = Product.objects.filter(store=request.ktk_store)
    query = request.GET.get("q", "").strip()[:100]
    status = request.GET.get("stock_status", "")
    if query:
        products = products.filter(Q(name__icontains=query) | Q(sku__icontains=query))
    if status == "low_stock":
        products = products.filter(stock__gt=0, stock__lt=6)
    elif status == "out_of_stock":
        products = products.filter(stock=0)
    elif status == "in_stock":
        products = products.filter(stock__gt=0)
    return render(request,"owner/warehouse_products.html",layout(request,products=products.order_by('stock','name')[:300],query=query,status=status))


@allow(*ALL, permission="warehouse_view")
@require_POST
def inventory_adjust(request, pk):
    if not can(request.ktk_membership,"warehouse_view"):
        raise PermissionDenied()
    try:
        delta = int(request.POST.get('delta', '0'))
    except (TypeError,ValueError):
        delta = 0
    if not -10000 <= delta <= 10000 or delta == 0:
        messages.error(request,"تعداد تغییر باید عددی غیرصفر بین منفی و مثبت ده‌هزار باشد.")
        return redirect('owner:warehouse_products')
    with transaction.atomic():
        product = get_object_or_404(Product.objects.select_for_update(), pk=pk, store=request.ktk_store)
        if product.stock + delta < 0:
            messages.error(request,"موجودی نمی‌تواند منفی شود.")
            return redirect('owner:warehouse_products')
        product.stock += delta
        product.save(update_fields=['stock'])
        StockMovement.objects.create(product=product, delta=delta, reason="اصلاح موجودی توسط مالک",actor=request.user)
    messages.success(request,"موجودی محصول تغییر کرد.")
    return redirect('owner:warehouse_products')


@allow(Membership.OWNER)
def payment(request):
    form = PaymentSettingsForm(request.POST or None, instance=request.ktk_store)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request,"اطلاعات پرداخت آفلاین ذخیره شد.")
        return redirect('owner:payment')
    return render(request,'owner/payment.html',layout(request,form=form,receipts=PaymentReceipt.objects.filter(store=request.ktk_store).select_related('order')[:100]))


@allow(Membership.OWNER)
def email(request):
    form = EmailSettingsForm(request.POST or None,instance=request.ktk_store)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request,"اطلاعات ایمیل فروشگاه ذخیره شد.")
        return redirect('owner:email')
    return render(request,'owner/email.html',layout(request,form=form,
        email_backend=django_settings.EMAIL_BACKEND,
        email_host=getattr(django_settings,'EMAIL_HOST',''),
        enabled=getattr(django_settings,'KTK_EMAIL_ENABLED',False)))


@allow(Membership.OWNER)
def customizer(request):
    form = VisualCustomizerForm(request.POST or None,instance=request.ktk_store)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request,"تنظیمات طراحی صفحه اصلی ذخیره شد.")
        return redirect('owner:customizer')
    return render(request,'owner/customizer.html',layout(request,form=form))


@allow(Membership.OWNER)
def access(request):
    members=Membership.objects.filter(store=request.ktk_store).select_related('user').exclude(role=Membership.OWNER)
    return render(request,'owner/access.html',layout(request,members=members))


@allow(*ALL, permission="support_view")
def support(request):
    tickets=SupportTicket.objects.filter(store=request.ktk_store)
    status=request.GET.get('status','')
    if status in dict(SupportTicket.STATUSES):
        tickets=tickets.filter(status=status)
    return render(request,'owner/support.html',layout(request,tickets=tickets[:200],statuses=SupportTicket.STATUSES,selected=status))


@allow(*ALL, permission="support_view")
def support_detail(request, pk):
    ticket=get_object_or_404(SupportTicket,store=request.ktk_store,pk=pk)
    if request.method=='POST':
        if not can(request.ktk_membership,'support_manage'):
            raise PermissionDenied()
        body=request.POST.get('reply','').strip()
        status=request.POST.get('status',ticket.status)
        if status not in dict(SupportTicket.STATUSES):
            raise PermissionDenied('وضعیت نامعتبر است.')
        if len(body)>5000:
            messages.error(request,'پاسخ بیش از حد طولانی است.')
        else:
            with transaction.atomic():
                if body:
                    SupportReply.objects.create(ticket=ticket,actor=request.user,body=body)
                ticket.status=status
                ticket.save(update_fields=['status','updated_at'])
            messages.success(request,'تغییرات تیکت ذخیره شد.')
            return redirect('owner:support_detail',pk=pk)
    return render(request,'owner/support_detail.html',layout(request,ticket=ticket,replies=ticket.replies.select_related('actor'),statuses=SupportTicket.STATUSES,can_reply=can(request.ktk_membership,'support_manage')))


@allow(*ALL, permission="returns_manage")
def returns(request):
    requests=ReturnRequest.objects.filter(store=request.ktk_store).select_related('order')[:250]
    return render(request,'owner/returns.html',layout(request,return_requests=requests))


@allow(*ALL, permission="returns_manage")
def return_detail(request, pk):
    item=get_object_or_404(ReturnRequest.objects.select_related('order'),pk=pk,store=request.ktk_store)
    if request.method=='POST':
        status=request.POST.get('status','')
        note=request.POST.get('note','').strip()
        if status not in dict(ReturnRequest.STATUSES) or len(note)>3000:
            messages.error(request,'اطلاعات رسیدگی معتبر نیست.')
        else:
            item.status=status
            item.owner_note=note
            item.reviewed_at=timezone.now()
            item.save(update_fields=['status','owner_note','reviewed_at'])
            messages.success(request,'وضعیت درخواست ثبت شد. این عمل به‌تنهایی وجهی را بازپرداخت نمی‌کند.')
            return redirect('owner:return_detail',pk=pk)
    return render(request,'owner/return_detail.html',layout(request,item=item,statuses=ReturnRequest.STATUSES))


@allow(Membership.OWNER)
@require_POST
def receipt_review(request, pk):
    item = get_object_or_404(PaymentReceipt,pk=pk,store=request.ktk_store)
    status = request.POST.get('status','')
    note = request.POST.get('note','').strip()
    if status not in ('accepted','rejected') or len(note)>500:
        messages.error(request,'اطلاعات بررسی معتبر نیست.')
        return redirect('owner:payment')
    item.status=status
    item.note=note
    item.reviewed_at=timezone.now()
    item.reviewed_by=request.user
    item.save(update_fields=['status','note','reviewed_at','reviewed_by'])
    messages.success(request,'وضعیت بررسی فیش ثبت شد. تأیید فیش، سند واریز قطعی بانکی محسوب نمی‌شود.')
    return redirect('owner:payment')


@allow(Membership.OWNER)
@require_POST
def user_toggle(request, pk):
    user=get_object_or_404(get_user_model(),pk=pk)
    # Never disable the acting owner or any store owner, or a Django superuser.
    if user.pk==request.user.pk or user.is_superuser or Membership.objects.filter(user=user,store=request.ktk_store,role=Membership.OWNER).exists():
        raise PermissionDenied('مدیریت وضعیت مالک و سوپریوزر از این بخش مجاز نیست.')
    action=request.POST.get('action')
    if action not in ('activate','deactivate'):
        raise PermissionDenied('عملیات نامعتبر است.')
    user.is_active=(action=='activate')
    user.save(update_fields=['is_active'])
    messages.success(request,'وضعیت حساب کاربر تغییر کرد.')
    return redirect('owner:users')


@allow(*ALL, permission="contacts_view")
def contacts(request):
    items = ContactMessage.objects.filter(store=request.ktk_store)
    status = request.GET.get("status", "")
    if status in dict(ContactMessage.STATUSES):
        items = items.filter(status=status)
    q = request.GET.get("q", "").strip()[:100]
    if q:
        items = items.filter(Q(full_name__icontains=q) | Q(phone__icontains=q))
    return render(request, "owner/inquiries.html", layout(request, items=items[:200], heading="پیام‌های تماس", kind="contacts", statuses=ContactMessage.STATUSES, selected=status, query=q))


@allow(*ALL, permission="contacts_view")
def contact_detail(request, pk):
    item = get_object_or_404(ContactMessage, store=request.ktk_store, pk=pk)
    can_edit = can(request.ktk_membership, "contacts_manage")
    if request.method == "POST":
        if not can_edit:
            raise PermissionDenied()
        status = request.POST.get("status", "")
        note = request.POST.get("owner_note", "").strip()
        if status not in dict(ContactMessage.STATUSES) or len(note) > 2000:
            messages.error(request, "وضعیت یا یادداشت معتبر نیست.")
        else:
            item.status = status
            item.owner_note = note
            item.save(update_fields=["status", "owner_note", "updated_at"])
            messages.success(request, "تغییرات پیام ذخیره شد.")
            return redirect("owner:contact_detail", pk=pk)
    return render(request, "owner/inquiry_detail.html", layout(request, item=item, kind="contacts", can_edit=can_edit, statuses=ContactMessage.STATUSES))


@allow(*ALL, permission="cooperations_view")
def cooperations(request):
    items = CooperationRequest.objects.filter(store=request.ktk_store)
    status = request.GET.get("status", "")
    if status in dict(CooperationRequest.STATUSES):
        items = items.filter(status=status)
    q = request.GET.get("q", "").strip()[:100]
    if q:
        items = items.filter(Q(full_name__icontains=q) | Q(company__icontains=q) | Q(phone__icontains=q))
    return render(request, "owner/inquiries.html", layout(request, items=items[:200], heading="درخواست‌های همکاری", kind="cooperations", statuses=CooperationRequest.STATUSES, selected=status, query=q))


@allow(*ALL, permission="cooperations_view")
def cooperation_detail(request, pk):
    item = get_object_or_404(CooperationRequest, store=request.ktk_store, pk=pk)
    can_edit = can(request.ktk_membership, "cooperations_manage")
    if request.method == "POST":
        if not can_edit:
            raise PermissionDenied()
        status = request.POST.get("status", "")
        note = request.POST.get("owner_note", "").strip()
        if status not in dict(CooperationRequest.STATUSES) or len(note) > 2000:
            messages.error(request, "وضعیت یا یادداشت معتبر نیست.")
        else:
            item.status = status
            item.owner_note = note
            item.save(update_fields=["status", "owner_note", "updated_at"])
            messages.success(request, "تغییرات درخواست ذخیره شد.")
            return redirect("owner:cooperation_detail", pk=pk)
    return render(request, "owner/inquiry_detail.html", layout(request, item=item, kind="cooperations", can_edit=can_edit, statuses=CooperationRequest.STATUSES))
