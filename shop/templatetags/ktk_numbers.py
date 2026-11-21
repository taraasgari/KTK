"""Format numbers using the store owner's independent KTK preferences."""
from decimal import Decimal, InvalidOperation
from django import template
from django.utils.translation import get_language

register = template.Library()
FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


@register.filter
def ktk_number(value, store=None):
    try:
        result = f"{int(Decimal(str(value))):,}"
    except (InvalidOperation, ValueError, TypeError):
        return value
    if get_language() and not get_language().startswith("fa"):
        return result
    if store is not None and getattr(store, "number_format", "fa") == "fa":
        return result.translate(FA_DIGITS)
    return result
