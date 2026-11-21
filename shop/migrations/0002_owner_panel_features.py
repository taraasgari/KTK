"""Owner dashboard features retained from the original reference, independently modeled."""
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('shop', '0001_initial'), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.AddField(model_name='store', name='logo', field=models.ImageField(blank=True, upload_to='branding/', verbose_name='لوگو')),
        migrations.AddField(model_name='store', name='favicon', field=models.ImageField(blank=True, upload_to='branding/', verbose_name='فاوآیکون')),
        migrations.AddField(model_name='store', name='instagram', field=models.URLField(blank=True, verbose_name='اینستاگرام')),
        migrations.AddField(model_name='store', name='telegram', field=models.URLField(blank=True, verbose_name='تلگرام')),
        migrations.AddField(model_name='store', name='footer_text', field=models.CharField(blank=True, max_length=240, verbose_name='متن فوتر')),
        migrations.AddField(model_name='store', name='primary_color', field=models.CharField(default='#C8102E', max_length=7, verbose_name='رنگ اصلی')),
        migrations.AddField(model_name='store', name='number_format', field=models.CharField(choices=[('fa', 'فارسی'), ('en', 'انگلیسی')], default='fa', max_length=8, verbose_name='نمایش اعداد')),
        migrations.AddField(model_name='membership', name='permissions', field=models.JSONField(blank=True, default=None, null=True, help_text='دسترسی‌های اختصاصی؛ فهرست خالی یعنی دسترسی پیش‌فرض نقش')),
        migrations.CreateModel(name='Review', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('author_name', models.CharField(max_length=100)),
            ('rating', models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])),
            ('text', models.TextField(max_length=2000)),
            ('is_approved', models.BooleanField(default=False)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='shop.product')),
            ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='shop.store')),
        ], options={'ordering': ['-created_at']}),
        migrations.CreateModel(name='Wishlist', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlist_items', to='shop.product')),
            ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlist_items', to='shop.store')),
            ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlist_items', to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.AddConstraint(model_name='wishlist', constraint=models.UniqueConstraint(fields=('store', 'user', 'product'), name='unique_ktk_wishlist')),
        migrations.CreateModel(name='OwnerProfile', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('image', models.ImageField(blank=True, upload_to='profiles/', verbose_name='تصویر پروفایل')),
            ('phone', models.CharField(blank=True, max_length=30, verbose_name='تلفن')),
            ('address', models.TextField(blank=True, verbose_name='آدرس')),
            ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ktk_profile', to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='StoreSlide', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('title', models.CharField(max_length=140, verbose_name='عنوان اسلاید')),
            ('subtitle', models.CharField(blank=True, max_length=220, verbose_name='زیرعنوان')),
            ('image', models.ImageField(upload_to='slides/', verbose_name='تصویر')),
            ('link', models.CharField(blank=True, max_length=250, verbose_name='لینک')),
            ('position', models.PositiveIntegerField(default=0)),
            ('is_active', models.BooleanField(default=True)),
            ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='slides', to='shop.store')),
        ], options={'ordering': ['position', 'pk']}),
    ]
