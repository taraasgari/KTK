from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from shop.models import Membership, Store


class Command(BaseCommand):
    help = "Create/configure the single store and grant an existing user ownership."

    def add_arguments(self, parser):
        parser.add_argument("--name", default="KTK")
        parser.add_argument("--owner", required=True, help="Existing Django username")

    def handle(self, *args, **opts):
        User = get_user_model()
        try:
            user = User.objects.get(username=opts["owner"])
        except User.DoesNotExist as exc:
            raise CommandError(f"User '{opts['owner']}' not found. Run createsuperuser first.") from exc
        store, created = Store.objects.get_or_create(slug=settings.KTK_STORE_SLUG, defaults={"name": opts["name"]})
        membership, _ = Membership.objects.update_or_create(store=store, user=user, defaults={"role": Membership.OWNER})
        self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Configured'} store {store.slug}; owner={membership.user.username}"))
