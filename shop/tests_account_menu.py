"""Guard against regressions in the KTK account dropdown and access controls."""
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Membership, Store


class HeaderAccountMenuTests(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name="KTK", slug="ktk")
        user = get_user_model()
        self.owner = user.objects.create_user(username="my-owner", password="TestOwner123!")
        self.customer = user.objects.create_user(username="my-customer", password="TestCustomer123!")
        self.staff = user.objects.create_user(username="my-staff", password="TestStaff123!")
        Membership.objects.create(store=self.store, user=self.owner, role=Membership.OWNER)
        Membership.objects.create(store=self.store, user=self.staff, role=Membership.STAFF)

    def test_anonymous_user_sees_login_not_private_dropdown(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'data-kt-account-menu')
        self.assertContains(response, f'href="{reverse("login")}"')

    def test_customer_sees_username_and_four_menu_actions(self):
        self.client.force_login(self.customer)
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'data-kt-account-menu')
        self.assertContains(response, 'my-customer')
        self.assertContains(response, 'پروفایل')
        self.assertContains(response, f'href="{reverse("customer_account")}"')
        self.assertContains(response, f'href="{reverse("support_request")}"')
        self.assertContains(response, f'href="{reverse("cart")}"')
        self.assertContains(response, f'action="{reverse("logout")}"')
        self.assertNotContains(response, f'href="{reverse("owner:home")}"')

    def test_owner_sees_owner_panel_and_owner_profile(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'my-owner')
        self.assertContains(response, f'href="{reverse("owner:profile")}"')
        self.assertContains(response, f'href="{reverse("owner:home")}"')
        self.assertContains(response, 'پنل مالکیت')

    def test_staff_has_profile_but_not_owner_panel_shortcut(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("home"))
        self.assertContains(response, f'href="{reverse("owner:profile")}"')
        self.assertNotContains(response, f'href="{reverse("owner:home")}"')

    def test_logout_is_post_only_with_csrf_token(self):
        self.client.force_login(self.customer)
        page = self.client.get(reverse("home"))
        self.assertContains(page, 'name="csrfmiddlewaretoken"')
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        result = self.client.post(reverse("logout"))
        self.assertEqual(result.status_code, 302)
        self.assertFalse("_auth_user_id" in self.client.session)

    def test_translated_menu_labels_for_english_and_chinese(self):
        self.client.force_login(self.owner)
        for language, profile, panel in (
            ("en", "Profile", "Owner panel"),
            ("zh-hans", "个人资料", "店主后台"),
        ):
            self.client.post(reverse("set_language"), {"language": language, "next": reverse("home")})
            response = self.client.get(reverse("home"))
            self.assertContains(response, profile)
            self.assertContains(response, panel)
