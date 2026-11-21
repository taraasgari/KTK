from django.shortcuts import render
from django.http import HttpResponseForbidden

from .permissions import has_dashboard_access


def admin_add_product(request):

    store = getattr(request, "store", None)

    if not has_dashboard_access(request.user, store):
        return HttpResponseForbidden(
            "Dashboard access denied"
        )

    product_service = getattr(
        request,
        "product_service",
        None
    )

    if request.method == "POST" and product_service:
        product_service.create_product(
            store,
            request.POST,
            request.FILES
        )

    return render(
        request,
        "dashboard/admin_add_product.html"
    )



def admin_edit_product(request, product_id):

    store = getattr(request, "store", None)

    if not has_dashboard_access(request.user, store):
        return HttpResponseForbidden(
            "Dashboard access denied"
        )

    product_service = getattr(
        request,
        "product_service",
        None
    )

    product = None

    if product_service:
        product = product_service.get_product(
            store,
            product_id
        )

    return render(
        request,
        "dashboard/admin_edit_product.html",
        {
            "product": product
        }
    )