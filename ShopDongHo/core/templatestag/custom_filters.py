from django import template
register = template.Library()

@register.filter
def format_vnd(value):
    try:
        numeric_value = float(value)
        return "{:,.0f}₫".format(numeric_value).replace(",", ".")
    except (TypeError, ValueError):
        return value