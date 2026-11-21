"""Real owner console with explicitly scoped authorization."""
from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, F, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .context import active_store
from .forms import CategoryForm, MembershipForm, OrderStatusForm, ProductForm, StoreForm
from .models import Category, Membership, Order, Product, StockMovement


def allow(*roles):
    def decorator(fn):
        @login_required
        @wraps(fn)
        def wrapped(request, *args, **kwargs):
            store = active_store()
            if not store:
                raise Http404("فروشگاه راه‌اندازی نشده است.")
            membership = Membership.objects.filter(store=store, user=request.user).first()
            if membership is None or membership.role not in roles:
                raise PermissionDenied("اجازه دسترسی به این بخش را ندارید.")
            request.ktk_store = store
            request.ktk_membership = membership
            return fn(request, *args, **kwargs)
        return wrapped
    return decorator


FULL = (Membership.OWNER, Membership.MANAGER)
ALL = (*FULL, Membership.STAFF)


def layout(request, **extra):
    return {"store": request.ktk_store, "member": request.ktk_membership, **extra}


@allow(*ALL)
def dashboard(request):
    store = request.ktk_store
    recent = Order.objects.filter(store=store)[:8]
    completed_total = Order.objects.filter(store=store, status=Order.DELIVERED).aggregate(total=Sum("total_price"))["total"] or 0
    return render(request, "owner/dashboard.html", layout(request,
        product_count=Product.objects.filter(store=store).count(),
        order_count=Order.objects.filter(store=store).count(),
        pending_count=Order.objects.filter(store=store, status=Order.NEW).count(),
        delivered_value=completed_total, recent=recent))


@allow(*FULL)
def products(request):
    queryset = Product.objects.filter(store=request.ktk_store).select_related("category")
    return render(request, "owner/products.html", layout(request, products=queryset))


@allow(*FULL)
def product_edit(request, pk=None):
    store = request.ktk_store
    product = get_object_or_404(Product, store=store, pk=pk) if pk else None
    form = ProductForm(request.POST or None, request.FILES or None, instance=product, store=store)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            previous_stock = Product.objects.select_for_update().get(pk=product.pk).stock if product else 0
            record = form.save(commit=False)
            record.store = store
            record.save()
            diff = record.stock - previous_stock
            if diff:
                StockMovement.objects.create(product=record, delta=diff, reason="ویرایش موجودی از پنل", actor=request.user)
        messages.success(request, "محصول ذخیره شد.")
        return redirect("owner:products")
    return render(request, "owner/form.html", layout(request, form=form, heading="ویرایش محصول" if product else "محصول جدید", back="owner:products"))


@allow(*FULL)
def categories(request):
    return render(request, "owner/categories.html", layout(request, categories=Category.objects.filter(store=request.ktk_store)))


@allow(*FULL)
def category_edit(request, pk=None):
    instance = get_object_or_404(Category, store=request.ktk_store, pk=pk) if pk else None
    form = CategoryForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        category = form.save(commit=False)
        category.store = request.ktk_store
        category.save()
        messages.success(request, "دسته‌بندی ذخیره شد.")
        return redirect("owner:categories")
    return render(request, "owner/form.html", layout(request, form=form, heading="ویرایش دسته‌بندی" if instance else "دسته‌بندی جدید", back="owner:categories"))


@allow(*ALL)
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


@allow(*ALL)
def order_detail(request, pk):
    order = get_object_or_404(Order, store=request.ktk_store, pk=pk)
    if request.method == "POST":
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


@allow(*FULL)
def inventory(request):
    products = Product.objects.filter(store=request.ktk_store).order_by("stock", "name")
    movements = StockMovement.objects.filter(product__store=request.ktk_store).select_related("product", "actor")[:20]
    return render(request, "owner/inventory.html", layout(request, products=products, movements=movements))


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
