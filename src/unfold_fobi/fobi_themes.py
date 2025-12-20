__all__ = ('UnfoldSimpleTheme',)

from fobi.base import theme_registry
from fobi.contrib.themes.simple.fobi_themes import SimpleTheme
from django.utils.translation import gettext_lazy as _

class UnfoldSimpleTheme(SimpleTheme):
    """
    Unfold theme for fobi
    """
    uid = 'unfold'
    name = _("Django Unfold admin style")
    html_classes = ['unfold',]
    base_edit_template = 'override_simple_theme/base_edit.html'
    form_edit_snippet_template_name = 'override_simple_theme/snippets/form_edit_snippet.html'
    form_properties_snippet_template_name = 'override_simple_theme/snippets/form_properties_snippet.html'
    form_snippet_template_name = 'override_simple_theme/snippets/form_snippet.html'
    form_wizard_properties_snippet_template_name = 'override_simple_theme/snippets/form_wizard_properties_snippet.html'
    create_form_entry_ajax_template = 'override_simple_theme/create_form_entry_ajax.html'

    media_css = (
        "simple/css/fobi.simple.css",
        "simple/css/fobi.simple.edit.css",
        #"jquery-ui/css/django-admin-theme/jquery-ui-1.10.4.custom.min.css",
    )

    media_js = (
        "js/jquery-1.10.2.min.js",
        "jquery-ui/js/jquery-ui-1.10.4.custom.min.js",
        "js/jquery.slugify.js",
        "js/fobi.core.js",
        "simple/js/fobi.simple.edit.js",
    )

theme_registry.register(UnfoldSimpleTheme, force=True)