"""Public customer access; does not grant any owner or staff permissions."""
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse

from .models import Membership


class KatikaLoginView(LoginView):
    template_name = "registration/login.html"

    def get_success_url(self):
        # Honor safe ?next= destinations using Django's built-in validator.
        redirect_url = self.get_redirect_url()
        if redirect_url:
            return redirect_url
        if Membership.objects.filter(
            user=self.request.user, store__slug=settings.KTK_STORE_SLUG,
            store__is_active=True
        ).exists():
            return reverse("owner:home")
        return reverse("customer_account")


def register(request):
    if request.user.is_authenticated:
        return redirect("customer_account")
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("customer_account")
    return render(request, "registration/register.html", {"form": form})


@login_required
def account(request):
    return render(request, "shop/account.html")
