from django.conf import settings
from .models import Store


def active_store():
    """Exact slug lookup; never fall back to another client's store."""
    return Store.objects.filter(slug=settings.KTK_STORE_SLUG, is_active=True).first()


def store_info(request):
    # On initial migration/error pages templates should remain renderable.
    store = getattr(request, "ktk_store", None)
    return {"site_store": store}
