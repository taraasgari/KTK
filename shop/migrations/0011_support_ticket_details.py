from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('shop', '0010_store_contact_address_en_store_contact_address_zh')]

    operations = [
        migrations.AddField(
            model_name='supportticket', name='email',
            field=models.EmailField('ایمیل', max_length=254, blank=True),
        ),
        migrations.AddField(
            model_name='supportticket', name='order_number',
            field=models.CharField('شماره سفارش', max_length=36, blank=True),
        ),
        migrations.AlterField(
            model_name='supportticket', name='contact',
            field=models.CharField('شماره تماس', max_length=160),
        ),
    ]
