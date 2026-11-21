from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Membership, Store, SupportTicket


class SupportReferencePageTests(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name='KTK', slug='ktk', contact_phone='02112345678',
            support_email='help@example.test',
        )
        user = get_user_model().objects.create_user(username='seller', password='ExamplePassword123!')
        Membership.objects.create(store=self.store, user=user, role=Membership.OWNER)
        self.owner = user

    def test_support_page_has_reference_layout_and_live_contacts(self):
        resp = self.client.get(reverse('support_request'))
        self.assertEqual(resp.status_code, 200)
        for text in ['مرکز پشتیبانی کاتیکا', 'ثبت درخواست پشتیبانی', 'سوالات متداول', 'راه‌های ارتباط با پشتیبانی', '02112345678', 'help@example.test']:
            self.assertContains(resp, text)
        self.assertContains(resp, 'name="order_number"')
        self.assertContains(resp, 'name="email"')
        self.assertContains(resp, 'katika-support.css')
        self.assertContains(resp, 'id="kt-support-faq"')

    def test_ticket_submission_keeps_structured_contact_and_owner_can_read(self):
        resp = self.client.post(reverse('support_request'), {
            'name': 'مشتری', 'contact': '۰۹۱۲۰۰۰۰۰۰۰',
            'email': 'customer@example.com', 'order_number': 'KTK-129456',
            'subject': 'پیگیری سفارش', 'body': 'لطفا سفارش من را بررسی کنید.',
        })
        self.assertRedirects(resp, reverse('support_request'))
        ticket = SupportTicket.objects.get(store=self.store)
        self.assertEqual(ticket.contact, '09120000000')
        self.assertEqual(ticket.email, 'customer@example.com')
        self.assertEqual(ticket.order_number, 'KTK-129456')
        self.client.force_login(self.owner)
        detail = self.client.get(reverse('owner:support_detail', args=[ticket.pk]))
        self.assertContains(detail, 'KTK-129456')
        self.assertContains(detail, 'customer@example.com')
        self.assertContains(detail, '09120000000')

    def test_invalid_phone_is_not_saved_and_error_is_visible(self):
        resp = self.client.post(reverse('support_request'), {
            'name': 'Tester', 'contact': 'invalid', 'subject': 'پیگیری سفارش',
            'body': 'Need help.',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(SupportTicket.objects.count(), 0)
        self.assertContains(resp, 'aria-invalid="true"')

    def test_honeypot_blocks_ticket(self):
        resp = self.client.post(reverse('support_request'), {
            'name': 'Bot', 'contact': '09120000000', 'subject': 'سایر موارد',
            'body': 'Hello', 'website': 'https://spam.invalid',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(SupportTicket.objects.count(), 0)

    def test_order_tracking_shortcut_preselects_subject(self):
        resp = self.client.get(reverse('support_request'), {'subject':'پیگیری سفارش'})
        self.assertContains(resp, 'value="پیگیری سفارش" selected')

    def test_support_page_renders_in_three_languages(self):
        for code, title, direction in [
            ('fa', 'مرکز پشتیبانی کاتیکا', 'rtl'),
            ('en', 'KTK Support Center', 'ltr'),
            ('zh-hans', 'KTK 客服中心', 'ltr'),
        ]:
            with self.subTest(code=code):
                resp = self.client.post(reverse('set_language'), {'language':code, 'next':reverse('support_request')})
                self.assertEqual(resp.status_code, 302)
                page = self.client.get(reverse('support_request'))
                self.assertContains(page, title)
                self.assertContains(page, f'dir="{direction}"')
                self.assertContains(page, 'data-kt-theme-toggle')
