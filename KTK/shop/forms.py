from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Category, Membership, Order, Product, Store


class CheckoutForm(forms.Form):
    customer_name = forms.CharField(label="نام و نام خانوادگی", max_length=120)
    customer_phone = forms.CharField(label="شماره تماس", max_length=30)
    address = forms.CharField(label="آدرس تحویل", widget=forms.Textarea(attrs={"rows": 3}))
    notes = forms.CharField(label="توضیحات", required=False, widget=forms.Textarea(attrs={"rows": 2}))


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "slug", "position", "is_active"]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["category", "name", "slug", "sku", "description", "price", "stock", "image", "featured", "is_active"]
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, store, **kwargs):
        self.store = store
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.filter(store=store)

    def clean_category(self):
        category = self.cleaned_data.get("category")
        if category and category.store_id != self.store.pk:
            raise ValidationError("دسته‌بندی متعلق به این فروشگاه نیست.")
        return category


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ["name", "tagline", "description", "contact_phone", "contact_email"]


class MembershipForm(forms.Form):
    username = forms.CharField(label="نام کاربری")
    password = forms.CharField(label="رمز کاربر جدید (اگر وجود ندارد)", widget=forms.PasswordInput, required=False)
    role = forms.ChoiceField(label="نقش", choices=Membership.ROLES[1:])

    def clean(self):
        data = super().clean()
        username, password = data.get("username"), data.get("password")
        if username and not get_user_model().objects.filter(username=username).exists():
            if not password:
                self.add_error("password", "برای ساخت کاربر جدید رمز عبور وارد کنید.")
            else:
                try:
                    validate_password(password)
                except ValidationError as exc:
                    self.add_error("password", exc)
        return data


class OrderStatusForm(forms.Form):
    status = forms.ChoiceField(label="وضعیت سفارش", choices=Order.STATUSES)
