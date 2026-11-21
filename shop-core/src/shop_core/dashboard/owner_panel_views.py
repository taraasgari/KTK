from django.shortcuts import render
from django.http import HttpResponseForbidden

from .permissions import has_dashboard_access


def owner_panel(request):

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
            "Owner access denied"
        )

    owner_service = getattr(
        request,
        "owner_service",
        None
    )

    context = {}

    if owner_service:
        context = owner_service.get_owner_context(
            store
        )

    return render(
        request,
        "dashboard/owner_panel.html",
        context
    )



def owner_profile_edit(request):

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
            "Owner access denied"
        )

    return render(
        request,
        "dashboard/owner_profile_edit.html"
    )