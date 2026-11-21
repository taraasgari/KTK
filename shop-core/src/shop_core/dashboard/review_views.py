from django.shortcuts import render
from django.http import HttpResponseForbidden

from .permissions import has_dashboard_access


def admin_reviews(request):

    store = getattr(request, "store", None)

    if not has_dashboard_access(
        request.user,
        store
    ):
        return HttpResponseForbidden(
            "Dashboard access denied"
        )

    review_service = getattr(
        request,
        "review_service",
        None
    )

    reviews = []

    if review_service:
        reviews = review_service.list_reviews(
            store
        )

    return render(
        request,
        "dashboard/admin_reviews.html",
        {
            "reviews": reviews,
        }
    )