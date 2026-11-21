from __future__ import annotations

import json
from pathlib import Path

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify


def _model(name):
    try:
        return apps.get_model("first", name)
    except LookupError:
        return None


def _has_field(model, name):
    if model is None:
        return False

    try:
        model._meta.get_field(name)
        return True
    except Exception:
        return False


def _set_if_field(obj, field, value):
    if value is None:
        return

    if _has_field(type(obj), field):
        setattr(obj, field, value)


def _build_slug(model, name):
    base = slugify(
        name,
        allow_unicode=True,
    ) or "item"

    candidate = base
    counter = 2

    while model.objects.filter(
        slug=candidate
    ).exists():

        candidate = f"{base}-{counter}"
        counter += 1

    return candidate


def _upsert_named(
    model,
    name,
    *,
    store=None,
    parent=None,
):
    if model is None:
        return None

    filters = {
        "name": name,
    }

    if store and _has_field(model, "store"):
        filters["store"] = store

    obj = model.objects.filter(
        **filters
    ).first()

    if obj is None:

        values = {
            "name": name,
        }

        if store and _has_field(model, "store"):
            values["store"] = store

        obj = model(**values)

    if _has_field(model, "slug") and not obj.slug:
        obj.slug = _build_slug(
            model,
            name,
        )

    if _has_field(model, "is_active"):
        obj.is_active = True

    if parent and _has_field(model, "parent"):
        obj.parent = parent

    obj.save()

    return obj


class Command(BaseCommand):

    help = (
        "Create/update a store and apply storefront profile."
    )


    def add_arguments(self, parser):

        parser.add_argument(
            "profile",
            nargs="?",
            default="store_profile.json",
        )


    def handle(
        self,
        *args,
        **options,
    ):

        profile_path = Path(
            options["profile"]
        ).resolve()


        if not profile_path.exists():
            raise CommandError(
                f"Profile not found: {profile_path}"
            )


        try:
            data = json.loads(
                profile_path.read_text(
                    encoding="utf-8"
                )
            )

        except Exception as exc:
            raise CommandError(
                f"Invalid profile JSON: {exc}"
            )


        Store = apps.get_model(
            "stores",
            "Store",
        )


        if Store is None:
            raise CommandError(
                "Store model not found."
            )


        store_data = data.get(
            "store",
            {}
        )


        store_slug = (
            store_data.get("slug")
            or slugify(
                store_data.get(
                    "name",
                    "store"
                ),
                allow_unicode=True,
            )
        )


        store, created = Store.objects.get_or_create(
            slug=store_slug,
            defaults={
                "name": store_data.get(
                    "name",
                    "New Store",
                ),
                "domain": store_data.get(
                    "domain"
                ),
                "theme": store_data.get(
                    "theme",
                    "default",
                ),
                "settings": data.get(
                    "branding",
                    {},
                ),
            },
        )


        store.settings = data.get(
            "branding",
            store.settings,
        )

        store.save()


        SiteSettings = _model(
            "SiteSettings"
        )

        Category = _model(
            "Category"
        )

        ProductType = _model(
            "ProductType"
        )

        Tag = _model(
            "Tag"
        )


        if SiteSettings:

            if hasattr(
                SiteSettings,
                "get_settings",
            ):
                site = SiteSettings.get_settings()

            else:
                site = (
                    SiteSettings.objects.first()
                    or SiteSettings()
                )


            branding = data.get(
                "branding",
                {}
            )


            for field in [
                "site_name",
                "site_title",
                "site_description",
                "primary_color",
                "secondary_color",
                "accent_color",
                "background_color",
                "text_color",
                "footer_text",
            ]:

                _set_if_field(
                    site,
                    field,
                    branding.get(field),
                )


            site.save()


        category_count = 0

        for name in data.get(
            "categories",
            [],
        ):

            if isinstance(
                name,
                str
            ) and name.strip():

                _upsert_named(
                    Category,
                    name.strip(),
                    store=store,
                )

                category_count += 1



        type_count = 0

        for name in data.get(
            "product_types",
            [],
        ):

            if isinstance(
                name,
                str
            ) and name.strip():

                _upsert_named(
                    ProductType,
                    name.strip(),
                    store=store,
                )

                type_count += 1



        tag_count = 0

        for name in data.get(
            "tags",
            [],
        ):

            if isinstance(
                name,
                str
            ) and name.strip():

                _upsert_named(
                    Tag,
                    name.strip(),
                    store=store,
                )

                tag_count += 1



        self.stdout.write(
            self.style.SUCCESS(
                "Store profile applied successfully."
            )
        )

        self.stdout.write(
            f"Store: {store.name}"
        )

        self.stdout.write(
            f"Categories seeded: {category_count}"
        )

        self.stdout.write(
            f"Product types seeded: {type_count}"
        )

        self.stdout.write(
            f"Tags seeded: {tag_count}"
        )