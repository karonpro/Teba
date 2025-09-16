from django import template

register = template.Library()

@register.filter
def sum_field(queryset, field_name):
    """
    Usage in template:
    {{ queryset|sum_field:"amount" }}
    """
    return sum(getattr(obj, field_name, 0) or 0 for obj in queryset)
