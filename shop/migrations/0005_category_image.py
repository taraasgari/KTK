from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("shop", "0004_payment_receipt")]

    operations = [
        migrations.AddField(
            model_name="category",
            name="image",
            field=models.ImageField(blank=True, upload_to="categories/", verbose_name="تصویر دسته‌بندی"),
        ),
    ]
