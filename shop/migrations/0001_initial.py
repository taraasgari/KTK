# Initial schema for the standalone KTK storefront.
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='نام فروشگاه')),
                ('slug', models.SlugField(unique=True)),
                ('tagline', models.CharField(blank=True, default='خرید هوشمند، انتخاب ماندگار', max_length=220, verbose_name='شعار')),
                ('description', models.TextField(blank=True, verbose_name='درباره فروشگاه')),
                ('contact_phone', models.CharField(blank=True, max_length=30, verbose_name='تلفن')),
                ('contact_email', models.EmailField(blank=True, max_length=254, verbose_name='ایمیل')),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=110)),
                ('is_active', models.BooleanField(default=True)),
                ('position', models.PositiveIntegerField(default=0)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='shop.store')),
            ],
            options={'ordering': ['position', 'name']},
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('owner', 'مالک'), ('manager', 'مدیر'), ('staff', 'کارمند')], default='staff', max_length=16)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='shop.store')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='store_roles', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=180)),
                ('slug', models.SlugField(max_length=190)),
                ('sku', models.CharField(blank=True, max_length=64)),
                ('description', models.TextField(blank=True)),
                ('price', models.PositiveBigIntegerField(validators=[MinValueValidator(1)])),
                ('stock', models.PositiveIntegerField(default=0)),
                ('image', models.ImageField(blank=True, upload_to='products/%Y/%m/')),
                ('featured', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='shop.category')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='shop.store')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('customer_name', models.CharField(max_length=120)),
                ('customer_phone', models.CharField(max_length=30)),
                ('address', models.TextField()),
                ('notes', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('new', 'جدید'), ('processing', 'در حال پردازش'), ('shipped', 'ارسال‌شده'), ('delivered', 'تحویل‌شده'), ('canceled', 'لغوشده')], default='new', max_length=18)),
                ('total_price', models.PositiveBigIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='shop.store')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='StockMovement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delta', models.IntegerField()),
                ('reason', models.CharField(max_length=160)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('actor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_movements', to='shop.product')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_snapshot', models.CharField(max_length=180)),
                ('price_snapshot', models.PositiveBigIntegerField()),
                ('quantity', models.PositiveIntegerField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='shop.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shop.product')),
            ],
        ),
        migrations.AddConstraint(
            model_name='category',
            constraint=models.UniqueConstraint(fields=('store', 'slug'), name='unique_store_category_slug'),
        ),
        migrations.AddConstraint(
            model_name='membership',
            constraint=models.UniqueConstraint(fields=('store', 'user'), name='unique_store_membership'),
        ),
        migrations.AddConstraint(
            model_name='product',
            constraint=models.UniqueConstraint(fields=('store', 'slug'), name='unique_store_product_slug'),
        ),
        migrations.AddConstraint(
            model_name='product',
            constraint=models.UniqueConstraint(condition=~models.Q(sku=''), fields=('store', 'sku'), name='unique_store_sku'),
        ),
    ]
