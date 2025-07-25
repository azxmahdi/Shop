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
    """Get the text value of the filter"""
    values = dictionary.get(key, [])
    return values[0] if values else ""


@register.filter
def get_list(dictionary, key):
    """Getting a list of filter values"""
    return dictionary.get(key, [])


@register.filter
def startswith(text, prefix):
    """Check if it starts with a prefix"""
    return text.startswith(prefix)
