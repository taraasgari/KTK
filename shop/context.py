from django.conf import settings
from .models import Store, Membership


def active_store():
    """Exact slug lookup; never fall back to another client's store."""
    return Store.objects.filter(slug=settings.KTK_STORE_SLUG, is_active=True).first()


def store_info(request):
    # On initial migration/error pages templates should remain renderable.
    store = getattr(request, "ktk_store", None)
    raw_cart = request.session.get("ktk_cart_v1", {}) if hasattr(request, "session") else {}
    cart_count = 0
    if isinstance(raw_cart, dict):
        for value in raw_cart.values():
            try:
                quantity = int(value)
            except (TypeError, ValueError):
                continue
            if 1 <= quantity <= 20:
                cart_count += quantity
    is_store_member = False
    is_store_owner = False
    if request.user.is_authenticated:
        # Account routes may not have called get_store(), unlike public shop views.
        # Resolve only the explicitly configured active store (never a different store).
        if store is None:
            store = active_store()
        if store is not None:
            role = Membership.objects.filter(store=store, user=request.user).values_list("role", flat=True).first()
            is_store_member = role is not None
            is_store_owner = role == Membership.OWNER
    return {"site_store": store, "cart_count": cart_count,
            "is_store_member": is_store_member, "is_store_owner": is_store_owner}
