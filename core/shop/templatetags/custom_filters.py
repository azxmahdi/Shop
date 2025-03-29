from django import template

register = template.Library()

@register.filter
def get_by_id(queryset, id_str):
    try:
        return queryset.get(id=int(id_str))
    except:
        return None

@register.filter
def get_value(dictionary, key):
    """گرفتن مقدار متنی فیلتر"""
    values = dictionary.get(key, [])
    return values[0] if values else ''

@register.filter
def get_list(dictionary, key):
    """گرفتن لیست مقادیر فیلتر"""
    return dictionary.get(key, [])

@register.filter
def startswith(text, prefix):
    """بررسی شروعشدن با پیشوند"""
    return text.startswith(prefix)