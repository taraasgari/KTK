from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from shop import auth_views as katika_auth
from django.urls import include, path

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("sysadmin/", admin.site.urls),
    path("accounts/login/", katika_auth.KatikaLoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/register/", katika_auth.register, name="register"),
    path("accounts/profile/", katika_auth.account, name="customer_account"),
    path("owner/", include(("shop.owner_urls", "owner"), namespace="owner")),
    path("", include("shop.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
