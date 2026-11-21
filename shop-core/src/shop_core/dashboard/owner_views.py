from django.shortcuts import render
from django.http import HttpResponseForbidden

from .permissions import has_dashboard_access


def manage_admins(request):

    store = getattr(request, "store", None)

    if not has_dashboard_access(
        request.user,
        store
    ):
        return HttpResponseForbidden(
            "Dashboard access denied"
        )

    admin_service = getattr(
        request,
        "admin_service",
        None
    )

    admins = []

    if admin_service:
        admins = admin_service.list_admins(
            store
        )

    return render(
        request,
        "dashboard/manage_admins.html",
        {
            "admins": admins,
        }
    )



def manage_permissions(request):

    store = getattr(request, "store", None)

    if not has_dashboard_access(
        request.user,
        store
    ):
        return HttpResponseForbidden(
            "Dashboard access denied"
        )

    permission_service = getattr(
        request,
        "permission_service",
        None
    )

    permissions = []

    if permission_service:
        permissions = permission_service.list_permissions(
            store
        )

    return render(
        request,
        "dashboard/manage_admin_permissions.html",
        {
            "permissions": permissions,
        }
    )