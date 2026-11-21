"""Idempotent, opt-in category setup for the KTK brand."""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from shop.models import Category, Store


class Command(BaseCommand):
    help = "Set up KTK storefront categories and initial brand details without replacing products."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        store = Store.objects.filter(slug=settings.KTK_STORE_SLUG).first()
        if store is None:
            raise CommandError("ابتدا bootstrap_store را اجرا کنید.")
        changed = []
        if store.name == "KTK":
            store.name = "کاتیکا"
            changed.append("name")
        if store.tagline == "خرید هوشمند، انتخاب ماندگار":
            store.tagline = "پوشش حرفه‌ای برای کتاب‌ها و دفترهای شما"
            changed.append("tagline")
        if changed:
            store.save(update_fields=changed)
        for index, (name, slug, name_en, name_zh) in enumerate([
            ("پخش عمده (رول و متراژ)", "bulk-rolls", "Wholesale rolls & lengths", "卷材批发与定尺"),
            ("تک‌جلد چسبی", "book-covers", "Self-adhesive book covers", "自粘书皮"),
            ("لوازم تحریر", "stationery", "Stationery", "文具用品"),
        ]):
            category, _ = Category.objects.get_or_create(
                store=store, slug=slug,
                defaults={"name": name, "name_en": name_en, "name_zh": name_zh, "position": index},
            )
            changes = []
            if not category.name_en:
                category.name_en = name_en; changes.append("name_en")
            if not category.name_zh:
                category.name_zh = name_zh; changes.append("name_zh")
            if changes: category.save(update_fields=changes)
        self.stdout.write(self.style.SUCCESS("برند و دسته‌بندی‌های اولیه کاتیکا آماده‌اند."))
