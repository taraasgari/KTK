KTK - اصلاح کش بنر صفحه اصلی (V13)

علت: فایل بنر از static/css/katika-storefront.css به static/images/katika-hero-product.webp ارجاع دارد، نه از media.

این آپدیت فقط یک تصویر جدید اضافه می‌کند و در دو فایل، ارجاع به تصویر و لینک CSS را تغییر می‌دهد:
  static/images/ktk-hero-product-v13.webp (جدید)
  static/css/katika-storefront.css (فقط آدرس تصویر)
  templates/base.html (فقط نسخه لینک CSS برای دور زدن کش)

نصب در PowerShell از پوشه فایل استخراج‌شده:
  Set-ExecutionPolicy -Scope Process Bypass -Force
  .\INSTALL-UPDATE.ps1 -ProjectPath 'C:\Users\Tara\Desktop\KTK' -RunServer

اسکریپت قبل از اعمال تغییرات، فایل‌های اصلاح‌شده را در پوشه‌ای با نام KTK-v13-changed-files-backup-* کنار پروژه ذخیره می‌کند.
بدون تغییر دیتابیس، media، .env، .venv، اطلاعات محصولات یا قالب اسلایدر.

اگر باز هم تصویر قدیمی دیده شد: صفحه را با Ctrl+F5 باز کنید. اگر اسلاید اختصاصی ثبت شده باشد و از image.url استفاده کند، این آپدیت فقط تصویر پیش‌فرض را عوض می‌کند؛ مسیر عکس قابل مشاهده را از Inspect > Network می‌توان یافت.
