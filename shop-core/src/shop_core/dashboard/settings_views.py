from django.shortcuts import render
from django.http import HttpResponseForbidden

from .permissions import has_dashboard_access


def site_settings(request):

    store = getattr(
        request,
        "store",
        None
    )

    if not has_dashboard_access(
        request.user,
        store
    ):
        return HttpResponseForbidden(
            "Dashboard access denied"
        )

    settings_service = getattr(
        request,
        "settings_service",
        None
    )

    settings_data = {}

    if settings_service:
        settings_data = settings_service.get_settings(
            store
        )

    return render(
        request,
        "dashboard/site_settings.html",
        {
            "settings": settings_data,
        }
    )