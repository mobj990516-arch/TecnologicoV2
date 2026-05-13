# proyectos/templatetags/proyecto_tags.py
from django import template

register = template.Library()

@register.filter
def corta(value, max_length=100):
    try:
        max_length = int(max_length)
    except Exception:
        max_length = 100
    if not value:
        return ''
    if len(value) > max_length:
        return value[:max_length].rstrip() + '...'
    return value
