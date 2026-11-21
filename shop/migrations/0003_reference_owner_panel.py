
from django.db import migrations, models
import django.db.models.deletion
import uuid
from django.conf import settings

class Migration(migrations.Migration):
    dependencies = [('shop','0002_owner_panel_features'), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.AddField('store','payment_method',models.CharField(max_length=24,default='cod',choices=[('cod','پرداخت هنگام تحویل'),('transfer','کارت به کارت')],verbose_name='روش پرداخت')),
        migrations.AddField('store','payment_card_number',models.CharField(max_length=24,blank=True,verbose_name='شماره کارت')),
        migrations.AddField('store','payment_account_name',models.CharField(max_length=120,blank=True,verbose_name='نام صاحب حساب')),
        migrations.AddField('store','payment_instructions',models.TextField(blank=True,verbose_name='توضیحات پرداخت')),
        migrations.AddField('store','email_sender_name',models.CharField(max_length=120,blank=True,verbose_name='نام فرستنده ایمیل')),
        migrations.AddField('store','support_email',models.EmailField(max_length=254,blank=True,verbose_name='ایمیل پشتیبانی')),
        migrations.AddField('store','hero_title',models.CharField(max_length=160,blank=True,verbose_name='عنوان اصلی سایت')),
        migrations.AddField('store','hero_subtitle',models.CharField(max_length=300,blank=True,verbose_name='توضیح اصلی سایت')),
        migrations.AddField('store','show_benefits',models.BooleanField(default=True,verbose_name='نمایش مزیت‌ها')),
        migrations.AddField('store','show_about',models.BooleanField(default=True,verbose_name='نمایش درباره فروشگاه')),
        migrations.CreateModel('SupportTicket',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),('public_id',models.UUIDField(default=uuid.uuid4,editable=False,unique=True)),('name',models.CharField(max_length=120,verbose_name='نام')),('contact',models.CharField(max_length=160,verbose_name='ایمیل یا تلفن')),('subject',models.CharField(max_length=160,verbose_name='موضوع')),('body',models.TextField(max_length=5000,verbose_name='متن درخواست')),('status',models.CharField(max_length=16,default='open',choices=[('open','باز'),('answered','پاسخ داده شده'),('closed','بسته')])),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),('store',models.ForeignKey(to='shop.store',related_name='support_tickets',on_delete=django.db.models.deletion.CASCADE))],options={'ordering':['-created_at']}),
        migrations.CreateModel('SupportReply',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),('body',models.TextField(max_length=5000,verbose_name='پاسخ')),('created_at',models.DateTimeField(auto_now_add=True)),('actor',models.ForeignKey(to=settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=django.db.models.deletion.SET_NULL)),('ticket',models.ForeignKey(to='shop.supportticket',related_name='replies',on_delete=django.db.models.deletion.CASCADE))],options={'ordering':['created_at']}),
        migrations.CreateModel('ReturnRequest',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),('reason',models.TextField(max_length=4000,verbose_name='علت درخواست')),('status',models.CharField(max_length=16,default='pending',choices=[('pending','در انتظار'),('reviewing','در حال بررسی'),('approved','تأیید'),('rejected','رد شده')])),('owner_note',models.TextField(blank=True,verbose_name='یادداشت رسیدگی')),('created_at',models.DateTimeField(auto_now_add=True)),('reviewed_at',models.DateTimeField(blank=True,null=True)),('order',models.ForeignKey(to='shop.order',related_name='return_requests',on_delete=django.db.models.deletion.CASCADE)),('store',models.ForeignKey(to='shop.store',related_name='return_requests',on_delete=django.db.models.deletion.CASCADE))],options={'ordering':['-created_at']}),
    ]
