# KTK — فروشگاه مستقل Django

**این نسخه، پایهٔ مستقل و قابل‌توسعهٔ فروشگاه KTK است.** رنگ‌بندی قرمز، سفید و مشکی دارد و شامل صفحات فروشگاه، سبد خرید، ثبت سفارش بدون پرداخت بانکی، و پنل مالک برای محصولات، دسته‌بندی‌ها، موجودی، سفارش‌ها، اعضای تیم و تنظیمات است. این نسخه به `shop-core` یا `shop-starter` وابسته نیست؛ هیچ‌کدام لازم نیست نصب شوند یا کنار پروژه باشند.

> **وضعیت:** نسخهٔ توسعه‌ای است؛ پرداخت آنلاین، ارسال پیامک، حساب مشتری و امکانات کامل یک فروشگاه Production در این نسخه پیاده‌سازی نشده‌اند. سفارش در سایت ثبت می‌شود اما هیچ وجهی دریافت نمی‌شود. قبل از ارائه عمومی، تست و امن‌سازی نهایی لازم است.

## ساختار

```text
KTK/
├── manage.py             # دستور Django در پوشهٔ اصلی
├── config/               # settings و URLهای پروژه
├── shop/                 # مدل‌ها، منطق فروش و مدیریت
│   ├── migrations/       # ساخت جدول‌های دیتابیس
│   └── management/commands/bootstrap_store.py
├── templates/            # صفحات فارسی و راست‌به‌چپ
├── static/css/site.css   # پوستهٔ قرمز/سفید/مشکی
├── scripts/              # نصب توسعه‌ای روی Windows/Linux
├── requirements.txt
├── requirements-prod.txt
├── .env.example
├── Dockerfile
└── docker-compose.yml
```

## راه‌اندازی روی ویندوز (PowerShell / Python 3.12)

1. ZIP را Extract کنید. PowerShell را **در پوشه‌ای باز کنید که فایل `manage.py` داخل آن است**.
2. دستورات زیر را بزنید (برای نصب پکیج‌ها اینترنت لازم است):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py bootstrap_store --name KTK --owner YOUR_USERNAME
.\.venv\Scripts\python.exe manage.py runserver
```

`YOUR_USERNAME` را با همان نام کاربری‌ای که در مرحلهٔ `createsuperuser` ساخته‌اید جایگزین کنید. برای اجرای مجدد کافی است وارد پوشهٔ KTK شوید و دستور آخر را بزنید.

- فروشگاه: http://127.0.0.1:8000/
- پنل مالک: http://127.0.0.1:8000/owner/
- پنل Django Admin (در صورت نیاز): http://127.0.0.1:8000/sysadmin/

**گزینهٔ کوتاه:** به‌جای مراحل نصب و مهاجرت در بالا می‌توانید در PowerShell دستور `powershell -ExecutionPolicy Bypass -File .\scripts\setup-windows.ps1` را اجرا کنید؛ سپس دستورهای `createsuperuser` و `bootstrap_store` را انجام دهید.

## راه‌اندازی روی Linux / macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py bootstrap_store --name KTK --owner YOUR_USERNAME
.venv/bin/python manage.py runserver
```

## تست بعد از نصب

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py test
```

## استقرار برای مشتری

`.venv` را **هرگز** از سیستم توسعه‌دهنده به سیستم مشتری کپی نکنید؛ این پوشه وابسته به سیستم‌عامل و نسخه Python است. برای مشتری فقط کد و فایل‌های الزامی را منتقل کنید و محیط مجازی را روی مقصد بسازید. پیش از استقرار، فایل `.env` ویژهٔ مشتری با کلید تصادفی قوی، `DJANGO_DEBUG=0`، دامنهٔ مجاز، HTTPS و دیتابیس مخصوص آن مشتری تنظیم کنید. `.env`، پایگاه داده واقعی و فایل‌های شخصی را در Git یا ZIP عمومی قرار ندهید.

معماری فعلی **یک نصب مستقل برای هر فروشگاه** است؛ اگر چند مشتری داشته باشید، برای هرکدام یک نصب جدا، دیتابیس جدا و فایل `.env` جدا در نظر بگیرید. این پروژه یک سرویس چندمستاجری مشترک نیست. Docker/Compose یک نقطه شروع برای استقرار است و به تنظیم Reverse Proxy، HTTPS و سیاست پشتیبان‌گیری نیاز دارد.

## وابستگی‌ها و محدودیت‌ها

- Python 3.12 و Django 5.2.x
- SQLite در حالت توسعه، PostgreSQL در حالت استقرار
- هیچ import یا وابستگی به `shop-core` و `shop-starter` وجود ندارد
- اجرا/تست کامل Django در محیط تهیه فایل به علت در دسترس نبودن بسته‌های نصب Django تایید نشده است
