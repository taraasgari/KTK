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


class OwnerPanelFeatureTests(TestCase):
    def setUp(self):
        from .models import Review
        User = get_user_model()
        self.store = Store.objects.create(name='KTK', slug='ktk')
        self.product = Product.objects.create(store=self.store, name='محصول آزمون', slug='item', price=250000, stock=4)
        self.owner = User.objects.create_user(username='seller', password='StrongPass123!')
        self.staff = User.objects.create_user(username='staff', password='StrongPass123!')
        self.outsider = User.objects.create_user(username='outsider', password='StrongPass123!')
        self.owner_membership = Membership.objects.create(store=self.store, user=self.owner, role=Membership.OWNER)
        self.staff_membership = Membership.objects.create(store=self.store, user=self.staff, role=Membership.STAFF)

    def test_owner_navigation_is_live_and_independent(self):
        self.client.force_login(self.owner)
        resp = self.client.get(reverse('owner:home'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'پرفروش‌ترین محصولات')
        for name in ['management', 'products', 'orders', 'users', 'reviews', 'inventory', 'analytics', 'appearance', 'profile', 'slides', 'team', 'numbers']:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse('owner:' + name)).status_code, 200)

    def test_staff_permissions_cannot_escape_team_or_edit_inventory(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse('owner:orders')).status_code, 200)
        for name in ['team', 'users', 'products', 'appearance', 'reviews', 'inventory']:
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse('owner:' + name)).status_code, 403)
        self.staff_membership.permissions = ['products_view']
        self.staff_membership.save(update_fields=['permissions'])
        self.assertEqual(self.client.get(reverse('owner:products')).status_code, 200)
        self.assertEqual(self.client.get(reverse('owner:product_new')).status_code, 403)
        self.assertEqual(self.client.get(reverse('owner:orders')).status_code, 403)

    def test_owner_permission_editor_post_works_and_owner_cannot_be_edited(self):
        self.client.force_login(self.owner)
        resp = self.client.post(reverse('owner:permissions', args=[self.staff_membership.pk]), {'permissions': ['products_view']})
        self.assertEqual(resp.status_code, 302)
        self.staff_membership.refresh_from_db()
        self.assertEqual(self.staff_membership.permissions, ['products_view'])
        self.assertEqual(self.client.get(reverse('owner:permissions', args=[self.owner_membership.pk])).status_code, 403)
        self.client.post(reverse('owner:permissions', args=[self.staff_membership.pk]), {'permissions': ['unknown']})
        self.staff_membership.refresh_from_db()
        self.assertEqual(self.staff_membership.permissions, ['products_view'])

    def test_review_requires_approval_and_moderation_is_post_only(self):
        from .models import Review
        url = reverse('review_submit', args=[self.product.pk])
        resp = self.client.post(url, {'author_name': 'خریدار', 'rating': '4', 'text': 'تست پنل مالک'})
        self.assertEqual(resp.status_code, 302)
        review = Review.objects.get(store=self.store)
        self.assertFalse(review.is_approved)
        self.assertNotContains(self.client.get(reverse('product_detail', args=['item'])), 'تست پنل مالک')
        self.client.force_login(self.owner)
        approve_url = reverse('owner:review_action', args=[review.pk, 'approve'])
        self.assertEqual(self.client.get(approve_url).status_code, 405)
        self.assertEqual(self.client.post(approve_url).status_code, 302)
        self.assertContains(self.client.get(reverse('product_detail', args=['item'])), 'تست پنل مالک')

    def test_store_scoped_review_and_slide_actions(self):
        from .models import Review
        other = Store.objects.create(name='Another', slug='another')
        second = Product.objects.create(store=other, name='غریبه', slug='outside', price=500, stock=1)
        review = Review.objects.create(store=other, product=second, author_name='X', rating=3, text='Not mine')
        self.client.force_login(self.owner)
        self.assertEqual(self.client.post(reverse('owner:review_action', args=[review.pk, 'approve'])).status_code, 404)
        self.assertFalse(Review.objects.get(pk=review.pk).is_approved)

    def test_analytics_and_export(self):
        self.client.force_login(self.owner)
        resp = self.client.get(reverse('owner:analytics'))
        self.assertContains(resp, 'آمار و گزارش‌ها')
        resp = self.client.get(reverse('owner:analytics_csv'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('text/csv', resp['Content-Type'])
        self.assertIn('ktk-orders.csv', resp['Content-Disposition'])


class ReferenceOwnerPanelTests(TestCase):
    """The requested reference sidebar is not decorative: its pages and actions work."""

    def setUp(self):
        from .models import SupportTicket
        User = get_user_model()
        self.store = Store.objects.create(name='KTK',slug='ktk')
        self.product = Product.objects.create(store=self.store,name='تست محصول',slug='sample',stock=5,price=340000)
        self.owner = User.objects.create_user('mainowner',password='StrongPass123!')
        self.staff = User.objects.create_user('newstaff',password='StrongPass123!')
        Membership.objects.create(store=self.store,user=self.owner,role=Membership.OWNER)
        Membership.objects.create(store=self.store,user=self.staff,role=Membership.STAFF)
        self.client.force_login(self.owner)

    def test_all_reference_sidebar_pages_render(self):
        names=['home','management','products','categories','orders','inventory','warehouse_products','analytics',
               'users','reviews','support','returns','settings','payment','numbers','email','appearance','slides',
               'customizer','team','access','profile']
        for name in names:
            with self.subTest(name=name):
                response=self.client.get(reverse('owner:'+name))
                self.assertEqual(response.status_code,200)
        html=self.client.get(reverse('owner:home')).content.decode()
        self.assertIn('data-pa-sidebar',html)
        self.assertIn('class="pa-nav"',html)
        self.assertIn('پشتیبانی و تیکت‌ها',html)
        self.assertIn('لغو و مرجوعی',html)

    def test_stock_adjustment_is_logged_and_cannot_go_negative(self):
        from .models import StockMovement
        url=reverse('owner:inventory_adjust',args=[self.product.pk])
        self.assertEqual(self.client.get(url).status_code,405)
        self.assertEqual(self.client.post(url,{'delta':'-3'}).status_code,302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock,2)
        self.assertTrue(StockMovement.objects.filter(product=self.product,delta=-3).exists())
        self.client.post(url,{'delta':'-4'})
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock,2)

    def test_settings_and_visual_customizer_persist(self):
        res=self.client.post(reverse('owner:payment'),{
            'payment_method':'transfer', 'payment_card_number':'6037991234567890',
            'payment_account_name':'آزمایشی','payment_instructions':'با هماهنگی فروشگاه'},follow=True)
        self.assertEqual(res.status_code,200)
        self.store.refresh_from_db()
        self.assertEqual(self.store.payment_method,'transfer')
        self.assertEqual(self.store.payment_card_number,'6037991234567890')
        self.client.post(reverse('owner:customizer'),{
            'hero_title':'عنوان جدید KTK','hero_subtitle':'متن جدید','primary_color':'#CC1122','show_benefits':'on'})
        self.assertContains(self.client.get(reverse('home')),'عنوان جدید KTK')
        self.store.refresh_from_db()
        self.assertFalse(self.store.show_about)

    def test_support_and_return_workflows_are_not_placeholders(self):
        from .models import SupportTicket,SupportReply,ReturnRequest
        self.client.logout()
        resp=self.client.post(reverse('support_request'),{
            'name':'مشتری','contact':'09120000000','subject':'سوال درباره کالا','body':'زمان ارسال چقدر است؟'})
        self.assertEqual(resp.status_code,302)
        ticket=SupportTicket.objects.get(store=self.store)
        self.client.force_login(self.owner)
        self.assertEqual(self.client.post(reverse('owner:support_detail',args=[ticket.pk]),{'reply':'در حال پیگیری','status':'answered'}).status_code,302)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status,'answered')
        self.assertEqual(SupportReply.objects.filter(ticket=ticket).count(),1)
        order=Order.objects.create(store=self.store,customer_name='مشتری',customer_phone='09120000000',address='تهران')
        # Only the session that made an order can request its return.
        self.assertEqual(self.client.get(reverse('return_request',args=[order.public_id])).status_code,404)
        session=self.client.session
        session['ktk_recent_order']=str(order.public_id)
        session.save()
        self.assertEqual(self.client.post(reverse('return_request',args=[order.public_id]),{'reason':'نیاز ندارم'}).status_code,302)
        item=ReturnRequest.objects.get(order=order)
        self.assertEqual(self.client.post(reverse('owner:return_detail',args=[item.pk]),{'status':'reviewing','note':'بررسی در حال انجام'}).status_code,302)
        item.refresh_from_db()
        self.assertEqual(item.status,'reviewing')

    def test_staff_cannot_use_owner_settings_or_admin_mutations(self):
        self.client.force_login(self.staff)
        for name in ['payment','email','customizer','access','support','returns']:
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse('owner:'+name)).status_code,403)
        self.assertEqual(self.client.post(reverse('owner:inventory_adjust',args=[self.product.pk]),{'delta':'6'}).status_code,403)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock,5)

    def test_card_transfer_receipts_are_stored_and_reviewed_without_marking_order_paid(self):
        import io
        import tempfile
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test import override_settings
        from .models import PaymentReceipt
        self.store.payment_method='transfer'
        self.store.save(update_fields=['payment_method'])
        order = Order.objects.create(store=self.store,customer_name='خریدار',customer_phone='09120000000',address='تهران')
        session=self.client.session
        session['ktk_recent_order']=str(order.public_id)
        session.save()
        data=io.BytesIO()
        Image.new('RGB',(5,5),'white').save(data,format='PNG')
        with tempfile.TemporaryDirectory() as media_root,override_settings(MEDIA_ROOT=media_root):
            uploaded=SimpleUploadedFile('proof.png',data.getvalue(),content_type='image/png')
            url=reverse('submit_receipt',args=[order.public_id])
            self.assertEqual(self.client.get(url).status_code,405)
            self.assertEqual(self.client.post(url,{'image':uploaded}).status_code,302)
            receipt=PaymentReceipt.objects.get(order=order)
            self.assertEqual(receipt.status,'pending')
            self.client.post(reverse('owner:receipt_review',args=[receipt.pk]),{'status':'accepted','note':'تصویر خوانا است'})
            receipt.refresh_from_db()
            self.assertEqual(receipt.status,'accepted')
            order.refresh_from_db()
            self.assertEqual(order.status,Order.NEW)
            self.assertEqual(PaymentReceipt.objects.filter(order=order).count(),1)
            self.client.post(url,{'image':SimpleUploadedFile('duplicate.png',data.getvalue(),content_type='image/png')})
            self.assertEqual(PaymentReceipt.objects.filter(order=order).count(),1)

class KatikaStorefrontTests(TestCase):
    """Protect the supplied KTK homepage layout and working navigation."""

    def setUp(self):
        from .models import Category
        self.store = Store.objects.create(name='کاتیکا', slug='ktk')
        self.category = Category.objects.create(
            store=self.store, name='تک‌جلد چسبی', slug='book-covers', position=0,
        )
        self.product = Product.objects.create(
            store=self.store, category=self.category,
            name='جلد چسبی نمونه', slug='adhesive-cover', price=200000, stock=4,
        )

    def test_public_home_reference_structure_and_search(self):
        page = self.client.get(reverse('home'))
        self.assertEqual(page.status_code, 200)
        for expected in ['KTK', 'kt-hero', 'kt-benefits', 'kt-categories',
                         'kt-nav-search', 'kt-product-grid', 'جلد چسبی نمونه']:
            self.assertContains(page, expected)
        self.assertContains(page, 'katika-storefront.css')
        self.assertContains(page, '?category=book-covers')
        self.assertContains(self.client.get(reverse('home'), {'q': 'جلد چسبی'}),
                            'جلد چسبی نمونه')
        self.assertNotContains(self.client.get(reverse('home'), {'q': 'ناپیدا'}),
                               '<h3><a href="/products/adhesive-cover/">جلد چسبی نمونه</a></h3>', html=False)

    def test_owner_slide_images_and_pagination_override_default_banner(self):
        from .models import StoreSlide
        StoreSlide.objects.create(store=self.store, title='اسلاید یک', image='slides/one.jpg')
        StoreSlide.objects.create(store=self.store, title='اسلاید دو', image='slides/two.jpg', position=1)
        page = self.client.get(reverse('home'))
        self.assertContains(page, 'اسلاید یک')
        self.assertContains(page, 'اسلاید دو')
        self.assertContains(page, 'data-slide-dot="0"')
        self.assertContains(page, 'data-slide-dot="1"')

    def test_cart_quantity_and_customer_account_navigation(self):
        session = self.client.session
        session['ktk_cart_v1'] = {str(self.product.pk): 2}
        session.save()
        self.assertContains(self.client.get(reverse('home')), 'سبد خرید، 2 کالا')
        self.assertEqual(self.client.get(reverse('register')).status_code, 200)
        self.assertEqual(self.client.get(reverse('customer_account')).status_code, 302)

    def test_public_signup_does_not_grant_owner_access(self):
        url = reverse('register')
        response = self.client.post(url, {
            'username': 'katikacustomer',
            'password1': 'VerySafePass123!',
            'password2': 'VerySafePass123!',
        })
        self.assertRedirects(response, reverse('customer_account'))
        self.assertEqual(self.client.get(reverse('customer_account')).status_code, 200)
        self.assertEqual(self.client.get(reverse('owner:home')).status_code, 403)

    def test_bootstrap_katika_does_not_replace_existing_categories(self):
        from django.core.management import call_command
        from .models import Category
        call_command('bootstrap_katika', verbosity=0)
        self.assertEqual(Category.objects.filter(store=self.store).count(), 3)
        call_command('bootstrap_katika', verbosity=0)
        self.assertEqual(Category.objects.filter(store=self.store).count(), 3)

class KatikaCatalogTests(TestCase):
    """The requested product catalog works in both modes with actual database values."""

    def setUp(self):
        from .models import Category
        self.store = Store.objects.create(name="کاتیکا", slug="ktk")
        self.covers = Category.objects.create(store=self.store, name="جلد چسبی", slug="book-covers")
        self.rolls = Category.objects.create(store=self.store, name="پخش عمده", slug="bulk-rolls")
        self.one = Product.objects.create(store=self.store, category=self.covers, name="جلد A4", slug="a4", price=120000, compare_at_price=150000, size="a4", stock=5, featured=True)
        self.two = Product.objects.create(store=self.store, category=self.rolls, name="رول A5", slug="roll", price=350000, size="a5", stock=3)
        self.hidden = Product.objects.create(store=self.store, category=self.covers, name="پنهان", slug="hidden", price=1000, stock=6, is_active=False)

    def test_catalog_layout_theme_switcher_and_real_counts(self):
        resp = self.client.get(reverse("catalog"))
        self.assertEqual(resp.status_code, 200)
        for expected in ("kt-catalog-sidebar", "kt-catalog-tiles", "kt-catalog-hero", "kt-catalog-products", "data-kt-theme-toggle", "katika-catalog.css", "katika-theme.js", "۱۲ کالا", "از 2 محصول"):
            self.assertContains(resp, expected)
        self.assertNotContains(resp, 'ناموجود ساختگی')
        self.assertNotContains(resp, 'پنهان')
        self.assertContains(resp, "٪20")

    def test_category_size_search_price_and_combined_filters(self):
        def names(params):
            response = self.client.get(reverse("catalog"), params)
            self.assertEqual(response.status_code, 200)
            return [obj.name for obj in response.context["page_obj"]]
        self.assertEqual(names({"category": "book-covers"}), ["جلد A4"])
        self.assertEqual(names({"category": "book-covers", "size": "a5"}), [])
        self.assertEqual(names({"size": "a5"}), ["رول A5"])
        self.assertEqual(names({"price_min": "100000", "price_max": "200000"}), ["جلد A4"])
        self.assertEqual(names({"q": "رول"}), ["رول A5"])
        self.assertEqual(names({"sort": "price_desc"}), ["رول A5", "جلد A4"])
        self.assertEqual(names({"category": "invalid"}), ["رول A5", "جلد A4"])
        self.assertEqual(names({"price_min": "oops", "sort": "unknown"}), ["رول A5", "جلد A4"])

    def test_add_to_cart_from_catalog_returns_to_catalog(self):
        resp = self.client.post(reverse('cart_add', args=[self.one.pk]), {'quantity': 2, 'next': '/products/?category=book-covers'})
        self.assertRedirects(resp, '/products/?category=book-covers')
        self.assertEqual(self.client.session['ktk_cart_v1'][str(self.one.pk)], 2)
        resp = self.client.post(reverse('cart_add', args=[self.one.pk]), {'quantity': 1, 'next': 'https://example.com/steal'})
        self.assertEqual(resp.url, '/cart/')

    def test_wishlist_from_listing_keeps_view_and_is_post_only(self):
        User = get_user_model()
        user = User.objects.create_user('cataloguser', password='StrongPass123!')
        self.client.force_login(user)
        resp = self.client.post(reverse('wishlist_toggle', args=[self.one.pk]), {'next': '/products/'})
        self.assertRedirects(resp, '/products/')
        self.assertContains(self.client.get(reverse('catalog')), 'حذف جلد A4 از علاقه‌مندی‌ها')
        self.assertEqual(self.client.get(reverse('wishlist_toggle', args=[self.one.pk])).status_code, 405)

    def test_pagination_query_keeps_filters(self):
        for n in range(16):
            Product.objects.create(store=self.store, category=self.covers, name=f"جلد شماره {n}", slug=f"cover-{n}", price=70000+n, stock=2)
        page1 = self.client.get(reverse('catalog'), {'category': 'book-covers', 'sort':'price_asc'})
        self.assertContains(page1, 'page=2')
        page2 = self.client.get(reverse('catalog'), {'category': 'book-covers', 'sort':'price_asc', 'page':2})
        self.assertEqual(page2.status_code, 200)
        self.assertEqual(page2.context['page_obj'].number, 2)
        self.assertEqual(page2.context['total_count'], 17)

class KatikaDemoDataTests(TestCase):
    def test_demo_is_opt_in_idempotent_and_rejected_in_production(self):
        from django.core.management import call_command
        from django.core.management.base import CommandError
        from django.test import override_settings
        Store.objects.create(name="کاتیکا", slug="ktk")
        with override_settings(DEBUG=True):
            call_command('bootstrap_katika_catalog_demo', verbosity=0)
            self.assertEqual(Product.objects.filter(slug__startswith='demo-').count(), 8)
            call_command('bootstrap_katika_catalog_demo', verbosity=0)
            self.assertEqual(Product.objects.filter(slug__startswith='demo-').count(), 8)
        with override_settings(DEBUG=False):
            with self.assertRaises(CommandError):
                call_command('bootstrap_katika_catalog_demo', verbosity=0)

class ContactAndCooperationTests(TestCase):
    def setUp(self):
        from .models import ContactMessage, CooperationRequest
        self.store = Store.objects.create(name="KTK", slug="ktk", contact_phone="02112345678", contact_email="example@example.com", contact_address="نشانی نمونه تست")
        self.owner = get_user_model().objects.create_user(username="contactowner", password="StrongPass123!")
        self.staff = get_user_model().objects.create_user(username="contactstaff", password="StrongPass123!")
        self.outsider = get_user_model().objects.create_user(username="outside", password="StrongPass123!")
        Membership.objects.create(store=self.store, user=self.owner, role=Membership.OWNER)
        self.member = Membership.objects.create(store=self.store, user=self.staff, role=Membership.STAFF)

    def test_public_pages_and_store_contact_information(self):
        for name in ("contact_us", "cooperation"):
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "kt-contact-shell")
                self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(self.client.get(reverse("contact_us")), "نشانی نمونه تست")
        self.assertContains(self.client.get(reverse("cooperation")), "همکاری بلندمدت")

    def test_contact_message_saved_and_session_cooldown(self):
        from .models import ContactMessage
        payload = {"full_name": "نام آزمایش", "phone": "۰۹۱۲۱۲۳۴۵۶۷", "subject": "consultation", "message": "درخواست مشاوره محصول"}
        self.assertEqual(self.client.post(reverse("contact_us"), payload).status_code, 302)
        record = ContactMessage.objects.get(store=self.store)
        self.assertEqual(record.phone, "09121234567")
        self.assertEqual(record.status, "new")
        self.assertEqual(self.client.post(reverse("contact_us"), payload).status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_cooperation_request_saved_and_invalid_phone_rejected(self):
        from .models import CooperationRequest
        payload = {"full_name": "همکار", "company": "مجموعه آزمایشی", "cooperation_type": "distribution", "phone": "09121234567", "details": "مایلیم پخش کنیم"}
        self.assertEqual(self.client.post(reverse("cooperation"), dict(payload, phone="abc")).status_code, 200)
        self.assertEqual(CooperationRequest.objects.count(), 0)
        self.assertEqual(self.client.post(reverse("cooperation"), payload).status_code, 302)
        self.assertEqual(CooperationRequest.objects.get().store, self.store)

    def test_owner_can_list_and_update_status_but_staff_cannot(self):
        from .models import ContactMessage, CooperationRequest
        contact = ContactMessage.objects.create(store=self.store, full_name="مشتری", phone="09121234567", subject="other", message="پیام")
        cooperation = CooperationRequest.objects.create(store=self.store, full_name="مشتری", phone="09121234567", cooperation_type="agency")
        self.client.force_login(self.staff)
        for name in ("contacts", "cooperations"):
            self.assertEqual(self.client.get(reverse("owner:" + name)).status_code, 403)
        self.client.force_login(self.owner)
        self.assertContains(self.client.get(reverse("owner:contacts")), "پیام‌های تماس")
        self.assertContains(self.client.get(reverse("owner:cooperations")), "درخواست‌های همکاری")
        self.assertEqual(self.client.post(reverse("owner:contact_detail", args=[contact.pk]), {"status":"replied", "owner_note":"پاسخ داده شد"}).status_code, 302)
        self.assertEqual(self.client.post(reverse("owner:cooperation_detail", args=[cooperation.pk]), {"status":"contacted", "owner_note":"تماس گرفته شد"}).status_code, 302)
        contact.refresh_from_db(); cooperation.refresh_from_db()
        self.assertEqual(contact.status, "replied")
        self.assertEqual(cooperation.status, "contacted")
        self.member.permissions = ["contacts_view", "cooperations_view"]
        self.member.save(update_fields=["permissions"])
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse("owner:contacts")).status_code, 200)
        self.assertEqual(self.client.get(reverse("owner:cooperations")).status_code, 200)
        self.assertEqual(self.client.post(reverse("owner:contact_detail", args=[contact.pk]), {"status":"new"}).status_code, 403)
        self.assertEqual(self.client.post(reverse("owner:cooperation_detail", args=[cooperation.pk]), {"status":"new"}).status_code, 403)

    def test_inquiries_isolated_by_store_and_no_default_store_fallback(self):
        from .models import ContactMessage, CooperationRequest
        second = Store.objects.create(name="Second", slug="second")
        c = ContactMessage.objects.create(store=second, full_name="Other", phone="09121234567", subject="other", message="Other message")
        co = CooperationRequest.objects.create(store=second, full_name="Other", phone="09121234567", cooperation_type="supply")
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(reverse("owner:contact_detail", args=[c.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse("owner:cooperation_detail", args=[co.pk])).status_code, 404)
        self.assertNotContains(self.client.get(reverse("owner:contacts")), "Other message")
        self.store.is_active = False; self.store.save(update_fields=["is_active"])
        self.assertEqual(self.client.get(reverse("contact_us")).status_code, 404)
        self.assertEqual(self.client.get(reverse("cooperation")).status_code, 404)
