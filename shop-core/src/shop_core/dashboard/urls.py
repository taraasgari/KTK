from django.urls import path

from .views import dashboard_home
from .admin_views import admin_dashboard
from .product_views import admin_products
from .order_views import admin_orders
from .user_views import admin_users
from .inventory_views import warehouse, warehouse_products
from .owner_views import manage_admins, manage_permissions
from .design_views import design_editor
from .product_manage_views import admin_add_product, admin_edit_product
from .review_views import admin_reviews
from .settings_views import site_settings
from .owner_panel_views import owner_panel, owner_profile_edit

app_name = "dashboard"


urlpatterns = [

    path(
        "",
        dashboard_home,
        name="dashboard_home"
    ),

    path(
        "admin-panel/",
        admin_dashboard,
        name="admin_dashboard"
    ),

    path(
        "admin-panel/products/",
        admin_products,
        name="admin_products"
    ),

    path(
        "admin-panel/orders/",
        admin_orders,
        name="admin_orders"
    ),

    path(
        "admin-panel/users/",
        admin_users,
        name="admin_users"
    ),

    path(
        "admin-panel/warehouse/",
        warehouse,
        name="warehouse"
    ),

    path(
        "admin-panel/warehouse/products/",
        warehouse_products,
        name="warehouse_products"
    ),

    path(
        "admin-panel/manage-admins/",
        manage_admins,
        name="manage_admins"
    ),

    path(
        "admin-panel/manage-permissions/",
        manage_permissions,
        name="manage_permissions"
    ),

    path(
        "admin-panel/design/",
        design_editor,
        name="design_editor"
    ),
path(
    "admin-panel/add-product/",
    admin_add_product,
    name="admin_add_product"
),

path(
    "admin-panel/product-edit/<int:product_id>/",
    admin_edit_product,
    name="admin_edit_product"
),
path(
    "admin-panel/reviews/",
    admin_reviews,
    name="admin_reviews"
),
path(
    "admin-panel/site-settings/",
    site_settings,
    name="site_settings"
),
path(
    "owner-panel/",
    owner_panel,
    name="owner_panel"
),

path(
    "owner-panel/profile-edit/",
    owner_profile_edit,
    name="owner_profile_edit"
),
]