from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Category, Membership, Order, Product, Store, ContactMessage, CooperationRequest


class CheckoutForm(forms.Form):
    customer_name = forms.CharField(label=_("نام و نام خانوادگی"), max_length=120)
    customer_phone = forms.CharField(label=_("شماره تماس"), max_length=30)
    address = forms.CharField(label=_("آدرس تحویل"), widget=forms.Textarea(attrs={"rows": 3}))
    notes = forms.CharField(label=_("توضیحات"), required=False, widget=forms.Textarea(attrs={"rows": 2}))


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "name_en", "name_zh", "slug", "position", "image", "is_active"]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["category", "name", "name_en", "name_zh", "slug", "sku",
                  "description", "description_en", "description_zh",
                  "features_fa", "features_en", "features_zh", "material", "material_en", "material_zh",
                  "dimensions", "dimensions_en", "dimensions_zh", "packaging", "packaging_en", "packaging_zh",
                  "usage", "usage_en", "usage_zh", "price", "compare_at_price", "size", "stock", "image", "featured", "is_active"]
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, store, **kwargs):
        self.store = store
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.filter(store=store)

    def clean(self):
        data = super().clean()
        if data.get("compare_at_price") is not None and data.get("price") is not None:
            if data["compare_at_price"] <= data["price"]:
                self.add_error("compare_at_price", "قیمت قبل از تخفیف باید بیشتر از قیمت فروش باشد.")
        return data

    def clean_category(self):
        category = self.cleaned_data.get("category")
        if category and category.store_id != self.store.pk:
            raise ValidationError("دسته‌بندی متعلق به این فروشگاه نیست.")
        return category


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ["name", "tagline", "description", "description_en", "description_zh", "contact_phone", "contact_email", "contact_address", "contact_address_en", "contact_address_zh"]


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


class AppearanceForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ["name", "tagline", "description", "description_en", "description_zh", "logo", "favicon", "primary_color", "contact_phone", "contact_email", "contact_address", "contact_address_en", "contact_address_zh", "instagram", "telegram", "footer_text", "footer_text_en", "footer_text_zh"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3}), "primary_color": forms.TextInput(attrs={"type": "color"})}

    def clean_primary_color(self):
        import re
        value = self.cleaned_data["primary_color"]
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            raise forms.ValidationError("کد رنگ باید در قالب #RRGGBB باشد.")
        return value.upper()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "email"]


class ReviewForm(forms.ModelForm):
    class Meta:
        from .models import Review
        model = Review
        fields = ["author_name", "rating", "text"]
        widgets = {
            "rating": forms.Select(choices=[(i, str(i)) for i in range(1, 6)]),
            "text": forms.Textarea(attrs={"rows": 3}),
        }


class StoreSlideForm(forms.ModelForm):
    def clean_link(self):
        value = self.cleaned_data.get("link", "").strip()
        if value and not (value.startswith("/") and not value.startswith("//") and not value.startswith("/\\")):
            from urllib.parse import urlsplit
            parts = urlsplit(value)
            if parts.scheme != "https" or not parts.netloc:
                raise forms.ValidationError("لینک باید مسیر داخلی با / یا آدرس معتبر https باشد.")
        return value

    class Meta:
        from .models import StoreSlide
        model = StoreSlide
        fields = ["title", "title_en", "title_zh", "subtitle", "subtitle_en", "subtitle_zh", "image", "link", "position", "is_active"]


class NumberFormatForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ["number_format"]


class OwnerDetailsForm(forms.ModelForm):
    class Meta:
        from .models import OwnerProfile
        model = OwnerProfile
        fields = ["image", "phone", "address"]
        widgets = {"address": forms.Textarea(attrs={"rows": 3})}


class PaymentSettingsForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ["payment_method", "payment_card_number", "payment_account_name", "payment_instructions"]
        widgets = {"payment_instructions": forms.Textarea(attrs={"rows": 3})}

    def clean(self):
        data = super().clean()
        if data.get("payment_method") == "transfer":
            card = (data.get("payment_card_number") or "").replace("-", "").replace(" ", "")
            if not (card.isdigit() and len(card) == 16):
                self.add_error("payment_card_number", "برای کارت به کارت، شماره کارت ۱۶ رقمی لازم است.")
            if not data.get("payment_account_name"):
                self.add_error("payment_account_name", "نام صاحب کارت را وارد کنید.")
        return data


class EmailSettingsForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ["email_sender_name", "support_email", "contact_email"]


class VisualCustomizerForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ["hero_title", "hero_title_en", "hero_title_zh", "hero_subtitle", "hero_subtitle_en", "hero_subtitle_zh", "show_benefits", "show_about", "primary_color"]
        widgets = {"primary_color": forms.TextInput(attrs={"type":"color"}), "hero_subtitle": forms.Textarea(attrs={"rows": 3})}

    def clean_primary_color(self):
        import re
        value = self.cleaned_data["primary_color"]
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            raise ValidationError("کد رنگ نامعتبر است.")
        return value.upper()


class SupportTicketForm(forms.Form):
    """Public ticket details. Existing 'contact' field remains compatible with old tickets."""
    name = forms.CharField(label=_("نام"), max_length=120)
    contact = forms.CharField(label=_("شماره تماس"), max_length=160)
    email = forms.EmailField(label=_("ایمیل"), required=False)
    order_number = forms.CharField(label=_("شماره سفارش"), max_length=36, required=False)
    subject = forms.CharField(label=_("موضوع"), max_length=160)
    body = forms.CharField(label=_("شرح درخواست"), max_length=1000, widget=forms.Textarea(attrs={"rows": 4}))

    def clean_contact(self):
        import re
        from unicodedata import decimal
        raw = self.cleaned_data["contact"].strip()
        normalized = "".join(str(decimal(ch)) if ch.isdecimal() else ch for ch in raw)
        normalized = re.sub(r"[\s()\-]", "", normalized)
        if not re.fullmatch(r"\+?[0-9]{8,15}", normalized):
            raise ValidationError(_("شماره تماس معتبر وارد کنید (۸ تا ۱۵ رقم)."))
        return normalized


class ReturnRequestForm(forms.Form):
    reason = forms.CharField(label=_("دلیل لغو یا مرجوعی"), max_length=4000, widget=forms.Textarea(attrs={"rows":4}))


class PaymentReceiptForm(forms.Form):
    image = forms.ImageField(label='تصویر فیش کارت به کارت')

    def clean_image(self):
        image = self.cleaned_data['image']
        if image.size > 5 * 1024 * 1024:
            raise ValidationError('حجم تصویر باید کمتر از ۵ مگابایت باشد.')
        if getattr(image, 'content_type', None) not in ['image/png','image/jpeg','image/webp']:
            raise ValidationError('فقط تصویر PNG یا JPEG یا WEBP مجاز است.')
        return image


class PublicPhoneMixin:
    def clean_phone(self):
        import re
        from unicodedata import decimal
        value = self.cleaned_data["phone"].strip()
        digits = "".join(str(decimal(ch)) if ch.isdecimal() else ch for ch in value)
        normalized = re.sub(r"[\s()\-]", "", digits)
        if not re.fullmatch(r"\+?[0-9]{8,15}", normalized):
            raise ValidationError(_("شماره تماس معتبر وارد کنید (۸ تا ۱۵ رقم)."))
        return normalized


class ContactMessageForm(PublicPhoneMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key in self.fields:
            self.fields[key].label = gettext(str(self.fields[key].label))
            widget = self.fields[key].widget
            if widget.attrs.get("placeholder"):
                widget.attrs["placeholder"] = gettext(widget.attrs["placeholder"])
        self.fields["subject"].choices = [("", gettext("موضوع پیام *")), *[(value, gettext(label)) for value, label in ContactMessage.SUBJECTS]]

    class Meta:
        model = ContactMessage
        fields = ["full_name", "phone", "subject", "message"]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "نام و نام خانوادگی *", "autocomplete": "name"}),
            "phone": forms.TextInput(attrs={"placeholder": "شماره تماس *", "autocomplete": "tel", "inputmode": "tel", "dir": "ltr"}),
            "subject": forms.Select(attrs={"aria-label": "موضوع پیام"}),
            "message": forms.Textarea(attrs={"placeholder": "متن پیام خود را بنویسید ...", "rows": 6}),
        }


class CooperationRequestForm(PublicPhoneMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key in self.fields:
            self.fields[key].label = gettext(str(self.fields[key].label))
            widget = self.fields[key].widget
            if widget.attrs.get("placeholder"):
                widget.attrs["placeholder"] = gettext(widget.attrs["placeholder"])
        self.fields["cooperation_type"].choices = [("", gettext("نوع همکاری *")), *[(value, gettext(label)) for value, label in CooperationRequest.TYPES]]

    class Meta:
        model = CooperationRequest
        fields = ["full_name", "company", "cooperation_type", "phone", "details"]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "نام و نام خانوادگی *", "autocomplete": "name"}),
            "company": forms.TextInput(attrs={"placeholder": "نام مجموعه (در صورت وجود)"}),
            "cooperation_type": forms.Select(attrs={"aria-label": "نوع همکاری"}),
            "phone": forms.TextInput(attrs={"placeholder": "شماره تماس *", "autocomplete": "tel", "inputmode": "tel", "dir": "ltr"}),
            "details": forms.Textarea(attrs={"placeholder": "توضیحات تکمیلی (اختیاری)", "rows": 4}),
        }
