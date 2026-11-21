from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.catalog, name="catalog"),
    path("contact-us/", views.contact_us, name="contact_us"),
    path("about/", views.about_katika, name="about_katika"),
    path("news-events/", views.news_events, name="news_events"),
    path("news-events/<slug:slug>/", views.news_detail, name="news_detail"),
    path("cooperation/", views.cooperation, name="cooperation"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("products/<int:product_id>/review/", views.review_submit, name="review_submit"),
    path("products/<int:product_id>/favorite/", views.wishlist_toggle, name="wishlist_toggle"),
    path("compare/", views.compare_page, name="compare_page"),
    path("products/<int:product_id>/compare/", views.compare_toggle, name="compare_toggle"),
    path("cart/", views.cart_page, name="cart"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("order/receipt/<uuid:public_id>/",views.submit_receipt,name="submit_receipt"),
    path("support/",views.support_request,name="support_request"),
    path("order/return/<uuid:public_id>/",views.return_request,name="return_request"),
    path("order/success/<uuid:public_id>/", views.order_success, name="order_success"),
]
