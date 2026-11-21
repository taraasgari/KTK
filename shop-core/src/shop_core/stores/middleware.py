from django.utils.deprecation import MiddlewareMixin

from .models import Store
from .context import set_current_store


class StoreContextMiddleware(MiddlewareMixin):

    def process_request(self, request):

        store = None

        host = request.get_host().split(":")[0]

        # پیدا کردن فروشگاه با دامنه
        if host:
            store = (
                Store.objects
                .filter(domain=host)
                .first()
            )

        # fallback برای توسعه
        if store is None:
            store = (
                Store.objects
                .order_by("id")
                .first()
            )

        request.store = store

        set_current_store(store)


    def process_response(self, request, response):

        set_current_store(None)

        return response