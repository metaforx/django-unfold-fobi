"""
Template tags and filters for unfold_fobi.

Provides Django 5.0+ compatibility filters for fobi templates.
"""
from django import template

register = template.Library()


@register.filter
def length_is(value, arg):
    """
    Compatibility filter for Django 5.0+ where length_is was removed.
    
    Checks if the length of a value equals the given argument.
    
    Usage:
        {% if form.fields|length_is:'1' %}...{% endif %}
    """
    try:
        length = len(value)
        arg = int(arg)
        return length == arg
    except (TypeError, ValueError):
        return False


@register.simple_tag
def get_form_classes():
    """
    Provides form_classes dictionary for Unfold crispy forms template pack.
    
    Returns a dictionary with CSS classes for form elements.
    """
    return {
        'switch': 'switch',
        'radio': 'radio',
        'checkbox': 'checkbox',
        'input': 'input',
        'select': 'select',
        'textarea': 'textarea',
    }
