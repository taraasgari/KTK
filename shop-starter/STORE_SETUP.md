# Shop Starter

این پروژه قالب شروع فروشگاه‌های جدید است.

## معماری

- منطق مشترک فروشگاه در `shop-core` خصوصی نگهداری می‌شود.
- این repo فقط storefront، branding، templateها، content و config مخصوص مشتری را نگه می‌دارد.
- مدل‌ها و migration history فعلاً با app label فعلی حفظ شده‌اند تا سازگاری دیتابیس خراب نشود.
- مسیر local `../shop-core` داخل Git commit نمی‌شود.

## ساخت فروشگاه جدید

داخل venv پروژه جدید:

```powershell
pip install -r requirements.txt
pip install -e ..\shop-core
python manage.py migrate
python manage.py apply_store_profile store_profile.json
python manage.py createsuperuser
python manage.py runserver
```

هنگام فروش/تحویل پروژه، نسخه standalone/freeze ساخته شود تا مشتری به Core خصوصی دسترسی لازم نداشته باشد.
