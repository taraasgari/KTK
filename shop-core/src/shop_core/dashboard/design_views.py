from django.shortcuts import render
from django.http import HttpResponseForbidden

from .permissions import has_dashboard_access


def design_editor(request):

    store = getattr(request, "store", None)

    if not has_dashboard_access(
        request.user,
        store
    ):
        return HttpResponseForbidden(
            "Design access denied"
        )

    design_service = getattr(
        request,
        "design_service",
        None
    )

    design = {}

    if design_service:
        design = design_service.get_design(
            store
        )

    return render(
        request,
        "dashboard/customizer.html",
        {
            "design": design,
        }
    )