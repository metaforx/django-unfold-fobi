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


class CaptureAsNode(template.Node):
    def __init__(self, nodelist, var_name):
        self.nodelist = nodelist
        self.var_name = var_name

    def render(self, context):
        context[self.var_name] = self.nodelist.render(context)
        return ""


@register.tag
def captureas(parser, token):
    """
    Capture template block into a context variable.

    Usage:
        {% captureas var_name %}...{% endcaptureas %}
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise template.TemplateSyntaxError(
            "captureas tag requires a single variable name."
        )
    nodelist = parser.parse(("endcaptureas",))
    parser.delete_first_token()
    return CaptureAsNode(nodelist, bits[1])
