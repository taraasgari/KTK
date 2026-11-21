"""Minimal smoke/regression tests for the user-supplied About & News screens."""
from django.test import TestCase
from django.urls import reverse
from .models import Store


class ReferencePageTests(TestCase):
    def setUp(self):
        Store.objects.create(name='KTK', slug='ktk')

    def test_about_page_and_navigation(self):
        response = self.client.get(reverse('about_katika'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'مهندس کامبیز کیانی')
        self.assertContains(response, 'about-ceo.webp')
        self.assertContains(response, 'kt-about-values')
        self.assertContains(self.client.get(reverse('home')), reverse('about_katika'))

    def test_language_menu_labels_stay_fixed_and_theme_is_shared(self):
        url = reverse('about_katika')
        for language, active_code in [('fa', 'FA'), ('en', 'EN'), ('zh-hans', 'ZH')]:
            self.client.post(reverse('set_language'), {'language': language, 'next': url})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            html = response.content.decode('utf-8')
            self.assertIn('class="kt-language-menu"', html)
            self.assertIn('>فارسی</strong>', html)
            self.assertIn('>English</strong>', html)
            self.assertIn('>中文</strong>', html)
            self.assertIn(f'class="kt-language-current-code">{active_code}</span>', html)
            self.assertIn("localStorage.getItem('ktk-theme')", html)
            self.assertIn('data-ktk-theme', html)

    def test_brand_intro_is_only_injected_on_homepage(self):
        home = self.client.get(reverse('home'))
        self.assertEqual(home.status_code, 200)
        self.assertContains(home, 'id="ktk-brand-intro"')
        self.assertContains(home, 'images/brand-intro/katika-intro-screen.png')
        self.assertContains(home, 'images/brand-intro/katika-intro-screen-mobile.png')
        self.assertContains(home, 'ktk-brand-intro-seen')
        self.assertContains(home, 'js/katika-brand-intro.js')

        about = self.client.get(reverse('about_katika'))
        self.assertEqual(about.status_code, 200)
        self.assertNotContains(about, 'id="ktk-brand-intro"')

    def test_news_page_cards_and_links(self):
        response = self.client.get(reverse('news_events'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'حضور کاتیکا در نمایشگاه')
        self.assertContains(response, 'class="kt-news-card"', count=6)
        self.assertContains(response, reverse('news_detail', args=['sustainable']))
        self.assertEqual(self.client.get(reverse('news_detail', args=['sustainable'])).status_code, 200)
        self.assertEqual(self.client.get(reverse('news_detail', args=['unknown-slug'])).status_code, 404)

    def test_news_filters_are_restricted_and_real(self):
        response = self.client.get(reverse('news_events') + '?category=product')
        self.assertEqual(response.context['total'], 2)
        self.assertNotContains(response, 'حرکت به سوی تولید پایدار')
        response = self.client.get(reverse('news_events') + '?category=arbitrary')
        self.assertEqual(response.context['total'], 6)
        response = self.client.get(reverse('news_events') + '?category=company&sort=oldest')
        self.assertEqual(response.context['news'][0]['slug'], 'distribution')

    def test_english_and_chinese_localization(self):
        for lang, heading, direction in [('en','News & Events','ltr'),('zh-hans','新闻与活动','ltr'),('fa','اخبار و رویدادها','rtl')]:
            response = self.client.post(reverse('set_language'), {'language':lang, 'next':reverse('news_events')})
            self.assertEqual(response.status_code, 302)
            page = self.client.get(reverse('news_events'))
            self.assertContains(page, f'dir="{direction}"')
            self.assertContains(page, heading)
            about = self.client.get(reverse('about_katika'))
            self.assertEqual(about.status_code, 200)
