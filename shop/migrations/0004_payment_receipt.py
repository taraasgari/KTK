from django.db import migrations,models
from django.conf import settings
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies=[('shop','0003_reference_owner_panel'),migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations=[
        migrations.CreateModel('PaymentReceipt',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('image',models.ImageField(upload_to='payment-receipts/%Y/%m/')),
            ('status',models.CharField(max_length=16,default='pending',choices=[('pending','در انتظار بررسی'),('accepted','فیش بررسی شد'),('rejected','رد شده')])),
            ('note',models.CharField(max_length=500,blank=True)),
            ('created_at',models.DateTimeField(auto_now_add=True)),
            ('reviewed_at',models.DateTimeField(null=True,blank=True)),
            ('order',models.ForeignKey(to='shop.order',related_name='payment_receipts',on_delete=django.db.models.deletion.CASCADE)),
            ('reviewed_by',models.ForeignKey(to=settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=django.db.models.deletion.SET_NULL)),
            ('store',models.ForeignKey(to='shop.store',related_name='payment_receipts',on_delete=django.db.models.deletion.CASCADE))],options={'ordering':['-created_at']})]
