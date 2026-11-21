"""Opt-in visual demo. Never run this command in a customer's production database."""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from pathlib import Path
from shop.models import ProductImage
from django.db import transaction
from shop.models import Category, Product, Store


class Command(BaseCommand):
    help = "Create example products for LOCAL preview of the KTK collection page only."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        if not settings.DEBUG:
            raise CommandError("محصولات نمایشی فقط در محیط توسعه (DJANGO_DEBUG=1) قابل ایجاد هستند.")
        store = Store.objects.filter(slug=settings.KTK_STORE_SLUG).first()
        if not store:
            raise CommandError("ابتدا فروشگاه را با bootstrap_store ایجاد کنید.")
        categories = {}
        for idx, (name, slug, name_en, name_zh) in enumerate([
            ("پخش عمده (رول و متراژ)", "bulk-rolls", "Wholesale rolls & lengths", "卷材批发与定尺"),
            ("تک‌جلد چسبی", "book-covers", "Self-adhesive book covers", "自粘书皮"),
            ("لوازم تحریر", "stationery", "Stationery", "文具用品"),
        ]):
            categories[slug], _ = Category.objects.get_or_create(
                store=store, slug=slug, defaults={"name": name, "name_en": name_en, "name_zh": name_zh, "position": idx})
            category = categories[slug]
            if not category.name_en or not category.name_zh:
                category.name_en = category.name_en or name_en
                category.name_zh = category.name_zh or name_zh
                category.save(update_fields=['name_en','name_zh'])
        examples = [
            ("بسته لوازم تحریر کاتیکا", "demo-stationery", "stationery", 319000, 380000, "", 8, False),
            ("رول جلد چسبی اقتصادی", "demo-roll-economy", "bulk-rolls", 1790000, None, "", 5, False),
            ("جلد چسبی تک‌جلدی A4", "demo-covers-a4", "book-covers", 135000, None, "a4", 9, False),
            ("رول جلد چسبی شفاف کاتیکا", "demo-roll-clear", "bulk-rolls", 2890000, None, "", 6, True),
            ("جلد چسبی A5", "demo-covers-a5", "book-covers", 125000, None, "a5", 12, False),
            ("جلد چسبی سفارشی", "demo-covers-custom", "book-covers", 195000, None, "custom", 7, False),
            ("رول جلد چسبی ضخیم", "demo-roll-thick", "bulk-rolls", 2100000, None, "", 5, False),
            ("لوازم تحریر اقتصادی", "demo-stationery-economy", "stationery", 80000, None, "", 10, False),
        ]
        created = 0
        for i, (name, slug, category_slug, price, compare_price, size, stock, featured) in enumerate(examples, 1):
            _, was_created = Product.objects.get_or_create(
                store=store, slug=slug,
                defaults={"name": name, "category": categories[category_slug],
                          "price": price, "compare_at_price": compare_price, "size": size,
                          "stock": stock, "featured": featured, "sku": f"KTK-DEMO-{i:03d}"})
            created += bool(was_created)
            demo_translations = [
                ('KTK stationery set', '卡蒂卡文具套装', 'Office and school stationery demo set.', '办公与学校文具示例套装。', 'Stationery set', '文具套装'),
                ('Economy self-adhesive cover roll', '经济型自粘书皮卷', 'Affordable protective self-adhesive film roll.', '经济型自粘保护膜卷。', 'Book protection', '书本保护'),
                ('A4 self-adhesive book covers', 'A4 自粘书皮', 'Clear A4 book covers for books and notebooks.', '适用于书籍和笔记本的透明 A4 书皮。', 'Book covers', '书皮'),
                ('KTK clear adhesive roll', '卡蒂卡透明自粘卷材', 'Transparent roll for books and notebooks.', '用于图书和笔记本的透明卷材。', 'Covering books', '包书'),
                ('A5 self-adhesive book cover', 'A5 自粘书皮', 'Protective book cover in A5 size.', 'A5 尺寸保护书皮。', 'Notebook cover', '笔记本封面'),
                ('Custom book cover', '定制书皮', 'Book-cover demo for custom sizes.', '定制尺寸书皮示例。', 'Custom use', '定制用途'),
                ('Thick adhesive film roll', '加厚自粘膜卷', 'Sample of a thicker protective roll.', '加厚型保护膜卷示例。', 'Protection', '保护'),
                ('Economy stationery', '经济型文具', 'Affordable everyday stationery.', '经济实用的日常文具。', 'Stationery', '文具'),
            ]
            en_name, zh_name, en_description, zh_description, en_usage, zh_usage = demo_translations[i - 1]
            product = Product.objects.get(store=store, slug=slug)
            product.name_en = en_name
            product.name_zh = zh_name
            product.description_en = en_description
            product.description_zh = zh_description
            if not product.description:
                product.description = f'محصول نمایشی {name} برای بررسی چیدمان فروشگاه و صفحه جزئیات.'
            if not product.features_fa:
                product.features_fa = 'تصاویر نمایشی برای بررسی ظاهر سایت\nاطلاعات قابل ویرایش از پنل مالک'
                product.features_en = 'Demo imagery for layout preview\nEditable in the owner panel'
                product.features_zh = '示例图片用于布局预览\n可在店主后台编辑'
            product.usage = 'محافظت و استفاده روزمره' if category_slug != 'stationery' else 'لوازم تحریر'
            product.usage_en = en_usage
            product.usage_zh = zh_usage
            product.material = 'فیلم شفاف نمونه' if category_slug != 'stationery' else 'لوازم تحریر نمونه'
            product.material_en = 'Sample transparent film' if category_slug != 'stationery' else 'Sample stationery'
            product.material_zh = '示例透明膜' if category_slug != 'stationery' else '示例文具'
            product.packaging = 'بسته‌بندی نمایشی'
            product.packaging_en = 'Sample packaging'
            product.packaging_zh = '示例包装'
            product.dimensions = product.get_size_display() if product.size else 'ابعاد نمونه'
            product.dimensions_en = product.get_size_display() if product.size else 'Sample size'
            product.dimensions_zh = product.get_size_display() if product.size else '示例尺寸'
            product.save(update_fields=['name_en','name_zh','description','description_en','description_zh',
                'features_fa','features_en','features_zh','usage','usage_en','usage_zh','material','material_en','material_zh',
                'packaging','packaging_en','packaging_zh','dimensions','dimensions_en','dimensions_zh'])
            images = Path(settings.BASE_DIR) / 'static' / 'images' / 'demo-gallery'
            if not product.image:
                photo = images / f'product-{i:02d}-view-1.webp'
                product.image.save(f'demo-ktk-{i:02d}-cover.webp', ContentFile(photo.read_bytes()), save=True)
            if not product.gallery.exists():
                for n in range(2, 5):
                    photo = images / f'product-{i:02d}-view-{n}.webp'
                    gallery = ProductImage(product=product, position=n, alt_fa=f'{name}، نمای {n}',
                        alt_en=f'{en_name}, view {n}', alt_zh=f'{zh_name}，视图 {n}')
                    gallery.image.save(f'demo-ktk-{i:02d}-view-{n}.webp', ContentFile(photo.read_bytes()), save=True)
            
        self.stdout.write(self.style.SUCCESS(
            f"{created} محصول نمونه افزوده شد. قیمت و موجودی این محصولات فقط برای پیش‌نمایش هستند."))
