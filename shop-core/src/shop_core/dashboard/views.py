from django.http import HttpResponseForbidden
from django.shortcuts import render

from .permissions import has_dashboard_access
from .services import get_dashboard_stats


def dashboard_home(request):
    store = getattr(request, "store", None)

    if not has_dashboard_access(request.user, store):
        return HttpResponseForbidden("Dashboard access denied")

    return render(
        request,
        "dashboard/index.html",
        {"stats": get_dashboard_stats(store)},
    )
