"""Regression tests for KTK three-language storefront and detail gallery."""
from io import BytesIO
from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import override
from shop.models import Category, Membership, Product, ProductImage, Review, Store


def sample_image(name):
    image = Image.new('RGB', (200, 160), (245, 245, 245))
    buffer = BytesIO(); image.save(buffer, format='JPEG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/jpeg')


class ProductDetailAndLanguageTests(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='کاتیکا', slug='ktk')
        self.category = Category.objects.create(store=self.store, name='رول', name_en='Rolls', name_zh='卷材', slug='rolls')
        self.product = Product.objects.create(store=self.store, category=self.category, name='جلد کتاب', name_en='Book cover', name_zh='书皮', slug='sample-cover', sku='KTK-01', price=80000, stock=15,
            description='توضیح فارسی',description_en='English product description',description_zh='中文商品介绍', material='پی‌وی‌سی', material_en='PVC', material_zh='PVC')
        self.other = Product.objects.create(store=self.store, category=self.category, name='رول مرتبط', name_en='Related roll', name_zh='相关卷材', slug='related-roll',price=110000,stock=4)

    def test_gallery_tabs_price_and_real_reviews_only(self):
        ProductImage.objects.create(product=self.product, image=sample_image('detail1.jpg'), position=1)
        ProductImage.objects.create(product=self.product, image=sample_image('detail2.jpg'), position=2)
        Review.objects.create(store=self.store, product=self.product,author_name='Customer', rating=5, text='private',is_approved=False)
        Review.objects.create(store=self.store, product=self.product,author_name='Customer',rating=4,text='approved',is_approved=True)
        response=self.client.get(reverse('product_detail',args=['sample-cover']))
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'data-gallery-thumb',count=2)
        self.assertContains(response,'data-product-tab="reviews"')
        self.assertContains(response,'related-roll')
        self.assertContains(response,'approved')
        self.assertNotContains(response,'private')
        self.assertEqual(response.context['rating_avg'],4.0)
        self.assertEqual(response.context['review_count'],1)

    def test_language_selector_cookie_and_page_direction(self):
        url=reverse('product_detail',args=['sample-cover'])
        fa=self.client.get(url)
        self.assertContains(fa,'lang="fa" dir="rtl"')
        self.assertContains(fa,'جلد کتاب')
        response=self.client.post(reverse('set_language'),{'language':'en','next':url})
        self.assertRedirects(response,url,fetch_redirect_response=False)
        en=self.client.get(url)
        self.assertContains(en,'lang="en" dir="ltr"')
        self.assertContains(en,'Book cover')
        self.assertContains(en,'English product description')
        self.assertContains(en,'Add to cart')
        self.assertContains(self.client.get(reverse('catalog')),'Rolls')
        response=self.client.post(reverse('set_language'),{'language':'zh-hans','next':url})
        self.assertEqual(response.status_code,302)
        zh=self.client.get(url)
        self.assertContains(zh,'lang="zh-hans" dir="ltr"')
        self.assertContains(zh,'书皮')
        self.assertContains(zh,'中文商品介绍')
        self.assertContains(zh,'加入购物车')

    def test_languages_use_localized_product_in_cart_and_search(self):
        with override('en'):
            self.assertEqual(self.product.display_name,'Book cover')
        self.client.post(reverse('cart_add',args=[self.product.pk]),{'quantity':2})
        self.client.post(reverse('set_language'),{'language':'en','next':'/cart/'})
        self.assertContains(self.client.get(reverse('cart')),'Book cover')
        self.assertContains(self.client.get(reverse('catalog')+'?q=Book+cover'),'Book cover')
        self.client.post(reverse('set_language'),{'language':'zh-hans','next':'/cart/'})
        self.assertContains(self.client.get(reverse('cart')),'书皮')

    def test_owner_gallery_upload_delete_and_scope(self):
        owner=get_user_model().objects.create_user(username='galleryowner', password='SecurePass123!')
        Membership.objects.create(store=self.store,user=owner,role=Membership.OWNER)
        self.client.force_login(owner)
        url=reverse('owner:product_edit',args=[self.product.pk])
        payload={'category':str(self.category.pk),'name':'جلد کتاب','name_en':'Book cover','name_zh':'书皮','slug':'sample-cover',
            'sku':'KTK-01','description':'توضیح فارسی','price':'80000','stock':'15','gallery_images':[sample_image('one.jpg'),sample_image('two.jpg')], 'is_active':'on'}
        res=self.client.post(url,payload)
        self.assertEqual(res.status_code,302, res.content.decode()[:500])
        self.assertEqual(self.product.gallery.count(),2)
        delete=self.product.gallery.first()
        payload.pop('gallery_images')
        payload['delete_gallery']=[str(delete.pk)]
        response=self.client.post(url,payload)
        self.assertEqual(response.status_code,302)
        self.assertEqual(self.product.gallery.count(),1)
        self.assertFalse(self.product.gallery.filter(pk=delete.pk).exists())

class ComparisonTests(TestCase):
    def setUp(self):
        self.store=Store.objects.create(slug='ktk',name='KTK')
        self.products=[Product.objects.create(store=self.store,name=f'محصول {i}',slug=f'comparison-{i}',price=1000+i,stock=2) for i in range(5)]

    def test_compare_is_limited_scoped_and_uses_post(self):
        product=self.products[0]
        url=reverse('compare_toggle',args=[product.pk])
        self.assertEqual(self.client.get(url).status_code,405)
        self.client.post(url,{'next':reverse('product_detail',args=[product.slug])})
        self.assertContains(self.client.get(reverse('compare_page')),product.name)
        for other in self.products[1:]:
            self.client.post(reverse('compare_toggle',args=[other.pk]))
        self.assertEqual(len(self.client.session['ktk_compare_v1'][str(self.store.pk)]),4)
        self.client.post(url)
        self.assertNotIn(product.pk,self.client.session['ktk_compare_v1'][str(self.store.pk)])
        third=Store.objects.create(slug='elsewhere',name='Another store')
        foreign=Product.objects.create(store=third,name='Other',slug='foreign',price=500,stock=2)
        self.assertEqual(self.client.post(reverse('compare_toggle',args=[foreign.pk])).status_code,404)
