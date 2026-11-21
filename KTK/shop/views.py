"""Public storefront: one installation, one explicitly configured store."""
from django.contrib import messages
from django.db import transaction
from django.db.models import F, Q
from django.http import Http404, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .context import active_store
from .forms import CheckoutForm
from .models import Category, Order, OrderItem, Product, StockMovement


CART_KEY = "ktk_cart_v1"


def get_store(request):
    store = active_store()
    if store is None:
        raise Http404("فروشگاه فعال هنوز راه‌اندازی نشده است. دستور bootstrap_store را اجرا کنید.")
    request.ktk_store = store
    return store


def _cart_lines(request, store):
    raw = request.session.get(CART_KEY, {})
    if not isinstance(raw, dict):
        raw = {}
    product_ids = [int(k) for k in raw if str(k).isdigit()]
    products = Product.objects.filter(store=store, is_active=True, id__in=product_ids)
    lines = []
    for product in products:
        try:
            qty = int(raw.get(str(product.pk), 0))
        except (ValueError, TypeError):
            continue
        if 1 <= qty <= 20:
            lines.append({"product": product, "quantity": qty, "subtotal": qty * product.price})
    return lines


def home(request):
    store = get_store(request)
    products = Product.objects.filter(store=store, is_active=True).select_related("category")
    categories = Category.objects.filter(store=store, is_active=True)
    q = request.GET.get("q", "").strip()[:100]
    selected_category = request.GET.get("category", "")
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(sku__icontains=q))
    if selected_category:
        products = products.filter(category__slug=selected_category, category__is_active=True)
    return render(request, "shop/home.html", {"store": store, "products": products[:60], "categories": categories, "query": q, "selected_category": selected_category})


def product_detail(request, slug):
    store = get_store(request)
    product = get_object_or_404(Product, store=store, slug=slug, is_active=True)
    return render(request, "shop/detail.html", {"store": store, "product": product})


def cart_page(request):
    store = get_store(request)
    lines = _cart_lines(request, store)
    return render(request, "shop/cart.html", {"store": store, "lines": lines, "total": sum(line["subtotal"] for line in lines)})


@require_POST
def cart_add(request, product_id):
    store = get_store(request)
    product = get_object_or_404(Product, pk=product_id, store=store, is_active=True)
    try:
        quantity = int(request.POST.get("quantity", "1"))
    except (ValueError, TypeError):
        quantity = 0
    if not 1 <= quantity <= 20:
        messages.error(request, "تعداد انتخاب‌شده معتبر نیست.")
        return redirect("product_detail", slug=product.slug)
    cart = request.session.get(CART_KEY, {})
    if not isinstance(cart, dict):
        cart = {}
    current = int(cart.get(str(product.pk), 0)) if str(cart.get(str(product.pk), 0)).isdigit() else 0
    new_quantity = min(20, current + quantity)
    if new_quantity > product.stock:
        messages.error(request, "موجودی برای این تعداد کافی نیست.")
        return redirect("product_detail", slug=product.slug)
    cart[str(product.pk)] = new_quantity
    request.session[CART_KEY] = cart
    messages.success(request, "محصول به سبد خرید اضافه شد.")
    return redirect("cart")


@require_POST
def cart_remove(request, product_id):
    get_store(request)
    cart = request.session.get(CART_KEY, {})
    if isinstance(cart, dict):
        cart.pop(str(product_id), None)
        request.session[CART_KEY] = cart
    return redirect("cart")


def checkout(request):
    store = get_store(request)
    lines = _cart_lines(request, store)
    if not lines:
        messages.error(request, "سبد خرید خالی است.")
        return redirect("cart")
    form = CheckoutForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                total = 0
                # Conditional stock updates prevent overselling even with simultaneous requests.
                for line in lines:
                    prod = line["product"]
                    qty = line["quantity"]
                    updated = Product.objects.filter(pk=prod.pk, store=store, stock__gte=qty, is_active=True).update(stock=F("stock") - qty)
                    if updated != 1:
                        raise ValueError(f"موجودی «{prod.name}» تغییر کرده است.")
                    total += prod.price * qty
                order = Order.objects.create(store=store, total_price=total, **form.cleaned_data)
                for line in lines:
                    prod, qty = line["product"], line["quantity"]
                    OrderItem.objects.create(order=order, product=prod, name_snapshot=prod.name, price_snapshot=prod.price, quantity=qty)
                    StockMovement.objects.create(product=prod, delta=-qty, reason=f"ثبت سفارش {str(order.public_id)[:8]}")
        except ValueError as exc:
            messages.error(request, str(exc))
        else:
            request.session.pop(CART_KEY, None)
            request.session["ktk_recent_order"] = str(order.public_id)
            return redirect("order_success", public_id=order.public_id)
    return render(request, "shop/checkout.html", {"store": store, "lines": lines, "total": sum(line["subtotal"] for line in lines), "form": form})


def order_success(request, public_id):
    store = get_store(request)
    # No public lookup of other orders: receipt requires one-time session authorization.
    order = get_object_or_404(Order, public_id=public_id, store=store)
    if request.session.get("ktk_recent_order") != str(public_id):
        raise Http404()
    return render(request, "shop/success.html", {"store": store, "order": order})
