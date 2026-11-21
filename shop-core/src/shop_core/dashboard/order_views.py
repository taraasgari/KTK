from django.shortcuts import render
from django.http import HttpResponseForbidden

from .permissions import has_dashboard_access


def admin_orders(request):

    store = getattr(request, "store", None)

    if not has_dashboard_access(
        request.user,
        store
    ):
        return HttpResponseForbidden(
            "Dashboard access denied"
        )

    order_service = getattr(
        request,
        "order_service",
        None
    )

    orders = []

    if order_service:
        orders = order_service.list_orders(
            store
        )

    return render(
        request,
        "dashboard/admin_orders.html",
        {
            "orders": orders,
        }
    )