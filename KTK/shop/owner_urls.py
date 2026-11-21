from django.urls import path
from . import owner_views as views

urlpatterns = [
    path("", views.dashboard, name="home"),
    path("products/", views.products, name="products"),
    path("products/new/", views.product_edit, name="product_new"),
    path("products/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("categories/", views.categories, name="categories"),
    path("categories/new/", views.category_edit, name="category_new"),
    path("categories/<int:pk>/edit/", views.category_edit, name="category_edit"),
    path("orders/", views.orders, name="orders"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
    path("inventory/", views.inventory, name="inventory"),
    path("settings/", views.settings_page, name="settings"),
    path("team/", views.team, name="team"),
    path("team/<int:pk>/remove/", views.team_remove, name="team_remove"),
]
