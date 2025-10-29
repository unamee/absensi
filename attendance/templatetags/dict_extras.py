# attendance/templatetags/dict_extras.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Ambil nilai dictionary berdasarkan key di template"""
    if dictionary and key in dictionary:
        return dictionary.get(key)
    return None
