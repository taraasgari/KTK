"""Public storefront: one installation, one explicitly configured store."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.translation import gettext as _
from datetime import timedelta
from django.db import transaction
from django.db.models import F, Q, Count, Min, Max, Avg
from django.http import Http404, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.utils.http import url_has_allowed_host_and_scheme

from .context import active_store
from .forms import CheckoutForm, ReviewForm
from .models import Category, Order, OrderItem, Product, StockMovement, Review, Wishlist, StoreSlide


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
        products = products.filter(Q(name__icontains=q) | Q(name_en__icontains=q) | Q(name_zh__icontains=q) | Q(description__icontains=q) | Q(description_en__icontains=q) | Q(description_zh__icontains=q) | Q(sku__icontains=q))
    if selected_category:
        products = products.filter(category__slug=selected_category, category__is_active=True)
    return render(request, "shop/home.html", {"store": store, "products": products[:60], "categories": categories, "query": q, "selected_category": selected_category, "slides": StoreSlide.objects.filter(store=store, is_active=True)})


def catalog(request):
    """Searchable, true-data product catalog matching the supplied dark/light references."""
    store = get_store(request)
    all_products = Product.objects.filter(store=store, is_active=True)
    categories = (Category.objects.filter(store=store, is_active=True)
                  .annotate(product_count=Count("products", filter=Q(products__is_active=True)))
                  .order_by("position", "name"))
    q = request.GET.get("q", "").strip()[:100]
    selected_categories = request.GET.getlist("category")[:20]
    valid_slugs = set(categories.values_list("slug", flat=True))
    selected_categories = [slug for slug in selected_categories if slug in valid_slugs]
    valid_sizes = dict(Product.SIZE_CHOICES)
    selected_sizes = [s for s in request.GET.getlist("size")[:10] if s in valid_sizes]
    sort = request.GET.get("sort", "newest")
    valid_sort = {"newest": "-created_at", "oldest": "created_at", "price_asc": "price", "price_desc": "-price", "name": "name"}
    if sort not in valid_sort:
        sort = "newest"
    try:
        per_page = int(request.GET.get("per_page", "12"))
    except (TypeError, ValueError):
        per_page = 12
    if per_page not in (12, 24, 36):
        per_page = 12

    # Bounds come from the actual catalog, not hardcoded screenshot prices.
    bounds = all_products.aggregate(lower=Min("price"), upper=Max("price"))
    floor = bounds["lower"] or 0
    ceiling = bounds["upper"] or 0
    price_min = request.GET.get("price_min", "")
    price_max = request.GET.get("price_max", "")
    def parse_price(value):
        try:
            parsed = int(value)
            return max(0, parsed)
        except (TypeError, ValueError):
            return None
    min_value = parse_price(price_min)
    max_value = parse_price(price_max)
    products = all_products.select_related("category")
    if q:
        products = products.filter(Q(name__icontains=q) | Q(name_en__icontains=q) | Q(name_zh__icontains=q) | Q(description__icontains=q) | Q(description_en__icontains=q) | Q(description_zh__icontains=q) | Q(sku__icontains=q))
    if selected_categories:
        products = products.filter(category__slug__in=selected_categories, category__is_active=True)
    if selected_sizes:
        products = products.filter(size__in=selected_sizes)
    if min_value is not None:
        products = products.filter(price__gte=min_value)
    if max_value is not None:
        products = products.filter(price__lte=max_value)
    products = products.order_by(valid_sort[sort], "pk")
    paginator = Paginator(products, per_page)
    page = paginator.get_page(request.GET.get("page"))
    first_index = page.start_index()
    last_index = page.end_index()
    base_query = request.GET.copy()
    base_query.pop("page", None)
    base_querystring = base_query.urlencode()
    size_counts = {row["size"]: row["count"] for row in all_products.exclude(size="").values("size").annotate(count=Count("pk"))}
    size_options = [{"value": val, "label": label, "count": size_counts.get(val, 0)} for val, label in Product.SIZE_CHOICES]
    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(Wishlist.objects.filter(store=store, user=request.user,
                     product_id__in=[p.pk for p in page.object_list]).values_list("product_id", flat=True))
    return render(request, "shop/catalog.html", {
        "store": store, "categories": categories, "query": q, "page_obj": page,
        "total_count": paginator.count, "first_index": first_index, "last_index": last_index,
        "selected_categories": selected_categories, "selected_sizes": selected_sizes,
        "size_options": size_options, "sort": sort, "per_page": per_page,
        "price_floor": floor, "price_ceiling": ceiling,
        "price_min": min_value if min_value is not None else floor,
        "price_max": max_value if max_value is not None else ceiling,
        "pagination_query": base_querystring, "wishlist_ids": wishlist_ids,
        "active_filters": bool(q or selected_categories or selected_sizes or min_value is not None or max_value is not None),
    })


def product_detail(request, slug):
    store = get_store(request)
    product = get_object_or_404(Product.objects.select_related("category").prefetch_related("gallery"), store=store, slug=slug, is_active=True)
    reviews = Review.objects.filter(store=store, product=product, is_approved=True).order_by("-created_at")
    rating_stats = reviews.aggregate(avg=Avg("rating"), count=Count("id"))
    rating_avg = round(float(rating_stats["avg"] or 0), 1)
    review_count = rating_stats["count"]
    rating_counts = dict(reviews.values_list("rating").annotate(n=Count("id")))
    distribution = [{"stars": n, "count": rating_counts.get(n, 0), "percent": round(rating_counts.get(n, 0) * 100 / review_count) if review_count else 0} for n in range(5, 0, -1)]
    related = Product.objects.filter(store=store, is_active=True).exclude(pk=product.pk)
    if product.category_id:
        related = related.filter(category_id=product.category_id)
    related = list(related.order_by("-featured", "-created_at")[:4])
    return render(request, "shop/detail.html", {
        "store": store, "product": product, "reviews": reviews[:10], "review_form": ReviewForm(),
        "rating_avg": rating_avg, "review_count": review_count, "distribution": distribution,
        "related": related, "gallery_images": list(product.gallery.all()),
        "is_favorite": request.user.is_authenticated and Wishlist.objects.filter(store=store, product=product, user=request.user).exists(),
        "is_compared": product.pk in _compared_ids(request, store),
        "compare_count": len(_compared_ids(request, store)),
    })


def _safe_next(request, fallback):
    destination = request.POST.get("next", "")
    if destination and url_has_allowed_host_and_scheme(destination, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return destination
    return fallback


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
        messages.error(request, _("تعداد انتخاب‌شده معتبر نیست."))
        return redirect(_safe_next(request, f"/products/{product.slug}/"))
    cart = request.session.get(CART_KEY, {})
    if not isinstance(cart, dict):
        cart = {}
    current = int(cart.get(str(product.pk), 0)) if str(cart.get(str(product.pk), 0)).isdigit() else 0
    new_quantity = min(20, current + quantity)
    if new_quantity > product.stock:
        messages.error(request, _("موجودی برای این تعداد کافی نیست."))
        return redirect(_safe_next(request, "/products/"))
    cart[str(product.pk)] = new_quantity
    request.session[CART_KEY] = cart
    messages.success(request, _("محصول به سبد خرید اضافه شد."))
    return redirect(_safe_next(request, "/cart/"))


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
        messages.error(request, _("سبد خرید خالی است."))
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
    from .models import PaymentReceipt
    return render(request, "shop/success.html", {"store": store, "order": order,
        "receipts": PaymentReceipt.objects.filter(store=store,order=order),
        "has_receipt": PaymentReceipt.objects.filter(store=store,order=order,status__in=['pending','accepted']).exists()})


@require_POST
def review_submit(request, product_id):
    store = get_store(request)
    product = get_object_or_404(Product, pk=product_id, store=store, is_active=True)
    form = ReviewForm(request.POST)
    # Simple session cooldown; not a substitute for edge rate limiting in production.
    now = timezone.now().timestamp()
    last = request.session.get("ktk_last_review_time", 0)
    if not isinstance(last, (int, float)) or now - last < 60:
        messages.error(request, _("لطفاً کمی بعد دوباره نظر ثبت کنید."))
    elif request.POST.get("website", ""):
        messages.error(request, _("ارسال نظر نامعتبر است."))
    elif form.is_valid():
        Review.objects.create(store=store, product=product, **form.cleaned_data)
        request.session["ktk_last_review_time"] = now
        messages.success(request, _("نظر شما ثبت شد و پس از تأیید نمایش داده می‌شود."))
    else:
        messages.error(request, _("اطلاعات نظر معتبر نیست. همه فیلدها و امتیاز را بررسی کنید."))
    return redirect("product_detail", slug=product.slug)


@login_required
@require_POST
def wishlist_toggle(request, product_id):
    store = get_store(request)
    product = get_object_or_404(Product, pk=product_id, store=store, is_active=True)
    wishlist, created = Wishlist.objects.get_or_create(store=store, product=product, user=request.user)
    if not created:
        wishlist.delete()
        messages.info(request, _("محصول از علاقه‌مندی‌ها حذف شد."))
    else:
        messages.success(request, _("محصول به علاقه‌مندی‌ها اضافه شد."))
    return redirect(_safe_next(request, f"/products/{product.slug}/"))


def support_request(request):
    from .forms import SupportTicketForm
    from .models import SupportTicket
    from django.utils.translation import get_language
    from .support_copy import SUBJECTS, support_context
    store=get_store(request)
    form=SupportTicketForm(request.POST or None)
    copy, subjects = support_context(get_language())
    valid_subjects = {item[0] for item in SUBJECTS}
    selected_subject = request.GET.get('subject', '') if request.method == 'GET' else request.POST.get('subject', '')
    if selected_subject not in valid_subjects:
        selected_subject = ''
    if request.method=='POST' and form.is_valid():
        # A honeypot and short session cooldown reduce casual automated spam.
        now=timezone.now().timestamp()
        if request.POST.get('website','') or now-float(request.session.get('ktk_last_support_time',0))<90:
            messages.error(request,_("لطفاً کمی بعد دوباره تلاش کنید."))
        else:
            SupportTicket.objects.create(store=store,**form.cleaned_data)
            request.session['ktk_last_support_time']=now
            messages.success(request,_("درخواست پشتیبانی ثبت شد. فروشگاه از طریق اطلاعات تماس شما پیگیری خواهد کرد."))
            return redirect('support_request')
    return render(request,'shop/support.html',{
        'store': store, 'form': form, 'support_copy': copy,
        'support_subjects': subjects, 'selected_subject': selected_subject,
    })


def return_request(request, public_id):
    from .forms import ReturnRequestForm
    from .models import ReturnRequest
    store=get_store(request)
    order=get_object_or_404(Order,store=store,public_id=public_id)
    if request.session.get('ktk_recent_order')!=str(public_id):
        raise Http404()
    form=ReturnRequestForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        if ReturnRequest.objects.filter(order=order,status__in=['pending','reviewing','approved']).exists():
            messages.error(request,_("برای این سفارش یک درخواست باز یا تأییدشده وجود دارد."))
        else:
            ReturnRequest.objects.create(store=store,order=order,reason=form.cleaned_data['reason'])
            messages.success(request,_("درخواست شما ثبت شد و پس از بررسی پاسخ داده می‌شود."))
            return redirect('order_success',public_id=public_id)
    return render(request,'shop/return.html',{'store':store,'form':form,'order':order})


@require_POST
def submit_receipt(request, public_id):
    from .forms import PaymentReceiptForm
    from .models import PaymentReceipt
    store=get_store(request)
    order=get_object_or_404(Order,store=store,public_id=public_id)
    if request.session.get('ktk_recent_order')!=str(public_id) or store.payment_method!='transfer':
        raise Http404()
    if PaymentReceipt.objects.filter(order=order,status__in=['pending','accepted']).exists():
        messages.error(request,_("برای این سفارش فیش در انتظار بررسی یا پذیرفته‌شده دارید."))
        return redirect('order_success',public_id=public_id)
    form=PaymentReceiptForm(request.POST,request.FILES)
    if form.is_valid():
        PaymentReceipt.objects.create(store=store,order=order,image=form.cleaned_data['image'])
        messages.success(request,_("تصویر فیش بارگذاری شد و در انتظار بررسی قرار دارد."))
    else:
        messages.error(request,_("تصویر فیش معتبر نیست؛ فقط PNG، JPEG یا WEBP تا ۵ مگابایت."))
    return redirect('order_success',public_id=public_id)


def _form_page(request, form_cls, model_cls, template, session_key, success_text):
    """Persist valid inquiry forms only for the configured active store."""
    store = get_store(request)
    form = form_cls(request.POST or None)
    if request.method == "POST" and form.is_valid():
        current = timezone.now().timestamp()
        last = request.session.get(session_key, 0)
        try:
            recently_submitted = current - float(last) < 60
        except (ValueError, TypeError):
            recently_submitted = False
        if request.POST.get("website", "").strip() or recently_submitted:
            form.add_error(None, _("لطفاً کمی بعد دوباره تلاش کنید."))
        else:
            model_cls.objects.create(store=store, **form.cleaned_data)
            request.session[session_key] = current
            messages.success(request, _(success_text))
            return redirect(request.path)
    return render(request, template, {"store": store, "form": form, "categories": Category.objects.filter(store=store, is_active=True)})


def contact_us(request):
    from .forms import ContactMessageForm
    from .models import ContactMessage
    return _form_page(request, ContactMessageForm, ContactMessage, "shop/contact.html", "ktk_contact_time", "پیام شما با موفقیت ثبت شد. در اولین فرصت با شما تماس خواهیم گرفت.")


def cooperation(request):
    from .forms import CooperationRequestForm
    from .models import CooperationRequest
    return _form_page(request, CooperationRequestForm, CooperationRequest, "shop/cooperation.html", "ktk_cooperation_time", "درخواست همکاری شما ثبت شد. پس از بررسی با شما تماس می‌گیریم.")


def _compared_ids(request, store):
    values = request.session.get('ktk_compare_v1', {})
    if not isinstance(values, dict):
        return []
    ids = values.get(str(store.pk), [])
    if not isinstance(ids, list):
        return []
    return [value for value in ids[:4] if type(value) is int and value > 0]


@require_POST
def compare_toggle(request, product_id):
    store = get_store(request)
    product = get_object_or_404(Product, pk=product_id, store=store, is_active=True)
    values = request.session.get('ktk_compare_v1', {})
    if not isinstance(values, dict):
        values = {}
    ids = _compared_ids(request, store)
    if product.pk in ids:
        ids.remove(product.pk)
        messages.info(request, _('محصول از مقایسه حذف شد.'))
    elif len(ids) >= 4:
        messages.error(request, _('حداکثر چهار محصول قابل مقایسه هستند.'))
    else:
        ids.append(product.pk)
        messages.success(request, _('محصول به مقایسه اضافه شد.'))
    values[str(store.pk)] = ids
    request.session['ktk_compare_v1'] = values
    return redirect(_safe_next(request, reverse('compare_page')))


def compare_page(request):
    store = get_store(request)
    ids = _compared_ids(request, store)
    existing = {p.pk:p for p in Product.objects.filter(store=store, is_active=True, pk__in=ids).select_related('category')}
    products = [existing[key] for key in ids if key in existing]
    return render(request, 'shop/compare.html', {'store':store, 'products':products})

# The two reference-driven editorial pages are intentionally separate from
# product/catalog models. All demo statements are copied from the supplied UI.
def about_katika(request):
    from django.utils.translation import get_language
    from .reference_pages import lang_copy
    store = get_store(request)
    language = (get_language() or 'fa').lower()
    return render(request, 'shop/about_katika.html', {'store': store, 'ref': lang_copy(language)})


def news_events(request):
    from django.utils.translation import get_language
    from .reference_pages import lang_copy, news_cards, NEWS_GROUPS
    store = get_store(request)
    language = (get_language() or 'fa').lower()
    group = request.GET.get('category', 'all')
    if group not in NEWS_GROUPS:
        group = 'all'
    order = request.GET.get('sort', 'latest')
    all_cards = news_cards(language)
    cards = [card for card in all_cards if group == 'all' or card['group'] == group]
    if order == 'oldest':
        cards = cards[::-1]
    return render(request, 'shop/news_events.html', {'store':store, 'ref':lang_copy(language), 'news':cards,
        'group':group, 'sort':order, 'total':len(cards)})


def news_detail(request, slug):
    from django.utils.translation import get_language
    from .reference_pages import lang_copy, news_cards
    store = get_store(request)
    language = (get_language() or 'fa').lower()
    article = next((card for card in news_cards(language) if card['slug'] == slug), None)
    if slug == 'tehran-exhibition':
        copy = lang_copy(language)
        article = {'slug':slug,'group':'event','image':'news-featured.webp','title':copy['featured_title'],'excerpt':copy['featured_excerpt'],'date':copy['featured_date']}
    if article is None:
        raise Http404('News item not found')
    return render(request, 'shop/news_detail.html', {'store':store, 'ref':lang_copy(language),'article':article})
