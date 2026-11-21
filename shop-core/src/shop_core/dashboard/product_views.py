from django.shortcuts import render
from django.http import HttpResponseForbidden

from .permissions import has_dashboard_access


def admin_products(request):

    store = getattr(request, "store", None)

    if not has_dashboard_access(
        request.user,
        store
    ):
        return HttpResponseForbidden(
            "Dashboard access denied"
        )

    product_service = getattr(
        request,
        "product_service",
        None
    )

    products = []

    if product_service:
        products = product_service.list_products(
            store
        )

    return render(
        request,
        "dashboard/admin_products.html",
        {
            "products": products,
        }
    )