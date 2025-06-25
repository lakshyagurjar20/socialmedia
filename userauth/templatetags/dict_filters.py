# userauth/templatetags/dict_filters.py

from django import template

register = template.Library()

@register.filter
def dictkey(dict_data, key):
    """Allows template access: dict|dictkey:key"""
    return dict_data.get(key)
