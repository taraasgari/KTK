"""Basic self-checks; execute with manage.py test after installing requirements."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Membership, Order, OrderItem, Product, Store


class StoreAndShopTests(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='KTK', slug='ktk')
        self.product = Product.objects.create(store=self.store, name='نمونه', slug='sample', price=120_000, stock=3)
        User = get_user_model()
        self.owner = User.objects.create_user(username='owner', password='TestPass123!')
        self.stranger = User.objects.create_user(username='stranger', password='TestPass123!')
        Membership.objects.create(store=self.store, user=self.owner, role=Membership.OWNER)

    def test_storefront_home_and_product(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get(reverse('product_detail', args=['sample'])).status_code, 200)

    def test_owner_access_is_restricted(self):
        self.client.force_login(self.stranger)
        self.assertEqual(self.client.get(reverse('owner:home')).status_code, 403)
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(reverse('owner:home')).status_code, 200)

    def test_checkout_reserves_stock_and_creates_order(self):
        response = self.client.post(reverse('cart_add', args=[self.product.pk]), {'quantity': 2})
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse('checkout'), {
            'customer_name': 'خریدار', 'customer_phone': '09120000000', 'address': 'تهران', 'notes': '',
        })
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 1)
        order = Order.objects.get(store=self.store)
        self.assertEqual(order.total_price, 240_000)
        item = OrderItem.objects.get(order=order)
        self.assertEqual(item.quantity, 2)

    def test_cart_rejects_stock_excess(self):
        self.client.post(reverse('cart_add', args=[self.product.pk]), {'quantity': 4})
        response = self.client.get(reverse('cart'))
        self.assertContains(response, 'سبد خرید خالی است')

    def test_store_fallback_is_not_used(self):
        self.store.slug = 'other'
        self.store.save(update_fields=['slug'])
        self.assertEqual(self.client.get('/').status_code, 404)
