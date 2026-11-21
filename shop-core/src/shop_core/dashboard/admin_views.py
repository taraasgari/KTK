from django.shortcuts import render
from django.http import HttpResponseForbidden

from .permissions import has_dashboard_access
from .services import get_dashboard_stats


def admin_dashboard(request):

    store = getattr(request, "store", None)

    if not has_dashboard_access(
        request.user,
        store
    ):
        return HttpResponseForbidden(
            "Dashboard access denied"
        )

    context = get_dashboard_stats(
        store
    )

    return render(
        request,
        "dashboard/admin_dashboard.html",
        context
    )