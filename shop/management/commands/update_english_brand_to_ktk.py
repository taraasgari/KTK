"""Change only the English display brand in existing owner-managed content.

Never change Persian 'کاتیکا', URLs, emails, SKUs, slugs or customer data.
Idempotent: safe to run more than once.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import CharField, TextField
from shop.models import Store, Product, ProductImage, Category, StoreSlide
import re

# Not a substring rewrite: old names in identifiers and emails must stay intact.
OLD = re.compile(r'(?<![A-Za-z0-9_./@-])katika(?![A-Za-z0-9_./@-])', re.IGNORECASE)

OWNER_EDITABLE = {
    Store: ("name", "tagline", "description", "description_en", "description_zh",
            "footer_text", "footer_text_en", "footer_text_zh",
            "hero_title", "hero_title_en", "hero_title_zh",
            "hero_subtitle", "hero_subtitle_en", "hero_subtitle_zh"),
    Category: ("name", "name_en", "name_zh"),
    Product: ("name", "name_en", "name_zh", "description", "description_en", "description_zh",
              "features_fa", "features_en", "features_zh",
              "material", "material_en", "material_zh",
              "dimensions", "dimensions_en", "dimensions_zh",
              "packaging", "packaging_en", "packaging_zh",
              "usage", "usage_en", "usage_zh"),
    ProductImage: ("alt_fa", "alt_en", "alt_zh"),
    StoreSlide: ("title", "title_en", "title_zh", "subtitle", "subtitle_en", "subtitle_zh"),
}

class Command(BaseCommand):
    help = "Replace standalone English Katika/KATIKA with KTK in owner-maintained display text only"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        counts = {}
        for model, fields in OWNER_EDITABLE.items():
            count = 0
            for obj in model.objects.all().iterator():
                modified = []
                for field in fields:
                    value = getattr(obj, field)
                    if isinstance(value, str):
                        replacement = OLD.sub("KTK", value)
                        if replacement != value:
                            setattr(obj, field, replacement)
                            modified.append(field)
                if modified:
                    obj.save(update_fields=modified)
                    count += 1
            counts[model.__name__] = count
        self.stdout.write(self.style.SUCCESS("English display brand refreshed: " + str(counts)))
