from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import translation
from shop.models import Store, Product, Category


class EnglishBrandOnlyTests(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name='کاتیکا', slug='ktk',
            description_en='Katika products. Visit support@katika.ir for KATIKA help.',
            tagline='برند کاتیکا',
        )

    def test_owner_content_changes_only_english_brand(self):
        product = Product.objects.create(
            store=self.store, name='جلد چسبی کاتیکا',
            name_en='KATIKA book covers', slug='old-katika-roll', price=1000,
        )
        call_command('update_english_brand_to_ktk', verbosity=0)
        self.store.refresh_from_db()
        product.refresh_from_db()
        self.assertEqual(self.store.name, 'کاتیکا')
        self.assertEqual(self.store.tagline, 'برند کاتیکا')
        self.assertEqual(self.store.description_en,
                         'KTK products. Visit support@katika.ir for KTK help.')
        self.assertEqual(product.name, 'جلد چسبی کاتیکا')
        self.assertEqual(product.name_en, 'KTK book covers')
        self.assertEqual(product.slug, 'old-katika-roll')
        call_command('update_english_brand_to_ktk', verbosity=0)
        product.refresh_from_db()
        self.assertEqual(product.name_en, 'KTK book covers')

    def test_public_labels_use_ktk_in_each_language(self):
        for lang in ('fa', 'en', 'zh-hans'):
            with self.subTest(lang=lang), translation.override(lang):
                response = self.client.get(reverse('home'))
                self.assertEqual(response.status_code, 200)
                markup = response.content.decode('utf-8')
                self.assertNotIn('>KATIKA<', markup)
                self.assertNotIn('>Katika<', markup)
                self.assertIn('KTK', markup)
