from django.conf import settings
from django.db import models


class Store(models.Model):

    name = models.CharField(
        max_length=100
    )

    slug = models.SlugField(
        unique=True,
        max_length=100
    )

    domain = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    theme = models.CharField(
        max_length=100,
        default="default"
    )

    settings = models.JSONField(
        default=dict,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name



class StoreMembership(models.Model):

    OWNER = "owner"
    ADMIN = "admin"
    STAFF = "staff"

    ROLE_CHOICES = [
        (OWNER, "Owner"),
        (ADMIN, "Admin"),
        (STAFF, "Staff"),
    ]

    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="store_memberships"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=STAFF
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = [
            ("store", "user")
        ]

    def __str__(self):
        return f"{self.user} - {self.store} - {self.role}"