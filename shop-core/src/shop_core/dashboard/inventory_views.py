from django.shortcuts import render
from django.http import HttpResponseForbidden

from .permissions import has_dashboard_access


def warehouse(request):

    store = getattr(request, "store", None)

    if not has_dashboard_access(
        request.user,
        store
    ):
        return HttpResponseForbidden(
            "Dashboard access denied"
        )

    inventory_service = getattr(
        request,
        "inventory_service",
        None
    )

    data = {}

    if inventory_service:
        data = inventory_service.get_inventory(
            store
        )

    return render(
        request,
        "dashboard/warehouse.html",
        data
    )



def warehouse_products(request):

    store = getattr(request, "store", None)

    if not has_dashboard_access(
        request.user,
        store
    ):
        return HttpResponseForbidden(
            "Dashboard access denied"
        )

    inventory_service = getattr(
        request,
        "inventory_service",
        None
    )

    products = []

    if inventory_service:
        products = inventory_service.get_products(
            store
        )

    return render(
        request,
        "dashboard/warehouse_products.html",
        {
            "products": products,
        }
    )