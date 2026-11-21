from django.db import models


class StoreDesign(models.Model):

    store = models.OneToOneField(
        "stores.Store",
        on_delete=models.CASCADE,
        related_name="design"
    )

    colors = models.JSONField(
        default=dict,
        blank=True
    )

    typography = models.JSONField(
        default=dict,
        blank=True
    )

    layout = models.JSONField(
        default=dict,
        blank=True
    )

    components = models.JSONField(
        default=dict,
        blank=True
    )

    homepage = models.JSONField(
        default=dict,
        blank=True
    )


    def __str__(self):
        return f"{self.store.name} Design"