from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("shop", "0006_catalog_product_attributes")]

    operations = [
        migrations.AddField(
            model_name="store", name="contact_address",
            field=models.TextField(blank=True, verbose_name="آدرس تماس"),
        ),
        migrations.CreateModel(
            name="ContactMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=120, verbose_name="نام و نام خانوادگی")),
                ("phone", models.CharField(max_length=20, verbose_name="شماره تماس")),
                ("subject", models.CharField(choices=[("consultation", "مشاوره خرید"), ("order", "پیگیری سفارش"), ("support", "پشتیبانی محصولات"), ("wholesale", "خرید عمده"), ("cooperation", "همکاری"), ("other", "سایر موارد")], max_length=24, verbose_name="موضوع پیام")),
                ("message", models.TextField(max_length=3000, verbose_name="متن پیام")),
                ("status", models.CharField(choices=[("new", "جدید"), ("read", "بررسی شده"), ("replied", "پاسخ داده شده")], default="new", max_length=16, verbose_name="وضعیت")),
                ("owner_note", models.TextField(blank=True, max_length=2000, verbose_name="یادداشت داخلی")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("store", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="contact_messages", to="shop.store")),
            ], options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="CooperationRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=120, verbose_name="نام و نام خانوادگی")),
                ("company", models.CharField(blank=True, max_length=160, verbose_name="نام مجموعه")),
                ("cooperation_type", models.CharField(choices=[("distribution", "پخش و توزیع"), ("agency", "نمایندگی فروش"), ("corporate", "همکاری سازمانی"), ("supply", "تأمین محصول"), ("marketing", "تبلیغات و بازاریابی"), ("other", "سایر همکاری‌ها")], max_length=24, verbose_name="نوع همکاری")),
                ("phone", models.CharField(max_length=20, verbose_name="شماره تماس")),
                ("details", models.TextField(blank=True, max_length=3000, verbose_name="توضیحات")),
                ("status", models.CharField(choices=[("new", "جدید"), ("reviewing", "در حال بررسی"), ("contacted", "تماس گرفته شد"), ("approved", "پذیرفته شده"), ("rejected", "رد شده")], default="new", max_length=16, verbose_name="وضعیت")),
                ("owner_note", models.TextField(blank=True, max_length=2000, verbose_name="یادداشت داخلی")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("store", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="cooperation_requests", to="shop.store")),
            ], options={"ordering": ["-created_at"]},
        ),
    ]
