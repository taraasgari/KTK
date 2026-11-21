from django.shortcuts import render
from django.http import HttpResponseForbidden

from .permissions import has_dashboard_access


def admin_users(request):

    store = getattr(request, "store", None)

    if not has_dashboard_access(
        request.user,
        store
    ):
        return HttpResponseForbidden(
            "Dashboard access denied"
        )

    user_service = getattr(
        request,
        "user_service",
        None
    )

    users = []

    if user_service:
        users = user_service.list_users(
            store
        )

    return render(
        request,
        "dashboard/admin_users.html",
        {
            "users": users,
        }
    )