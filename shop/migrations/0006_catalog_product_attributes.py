from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("shop", "0005_category_image")]
    operations = [
        migrations.AddField(model_name="product", name="size", field=models.CharField(blank=True, choices=[("a4", "A4"), ("a5", "A5"), ("custom", "سفارشی")], max_length=16, verbose_name="ابعاد محصول")),
        migrations.AddField(model_name="product", name="compare_at_price", field=models.PositiveBigIntegerField(blank=True, null=True, verbose_name="قیمت پیش از تخفیف")),
    ]
