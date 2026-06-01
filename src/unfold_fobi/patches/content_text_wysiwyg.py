"""WYSIWYG support for the Fobi ``content_text`` plugin.

Swaps the default single-line widget for "InlineToolbarWysiwygWidget" and
widens the bleach allowlist so Trix's output survives sanitization. Must run
after "apply_widgets" so our wrappers go on top of its ones.
"""

from django.conf import settings

_TRIX_ALLOWED_TAGS = [
    "a", "abbr", "acronym", "b", "blockquote", "br", "code", "div",
    "em", "h1", "h2", "h3", "i", "li", "ol", "p", "pre", "s", "strike",
    "strong", "u", "ul",
]
_TRIX_ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "target", "rel"],
    "abbr": ["title"],
    "acronym": ["title"],
}


def apply():
    """Install the content_text WYSIWYG swap — idempotent.

    Silently no-ops if the "content_text" plugin isn't installed.
    """
    try:
        from fobi import base as fobi_base
        from fobi.contrib.plugins.form_elements.content.content_text import (
            forms as content_text_forms,
        )
    except ImportError:
        return

    from unfold_fobi.forms.widgets import InlineToolbarWysiwygWidget

    content_text_form_class = content_text_forms.ContentTextForm

    if getattr(content_text_form_class, "_wysiwyg_widget_applied", False):
        return

    def force_wysiwyg(form):
        if not isinstance(form, content_text_form_class):
            return form
        text_field = form.fields.get("text")
        if text_field is not None and not isinstance(
            text_field.widget, InlineToolbarWysiwygWidget
        ):
            text_field.widget = InlineToolbarWysiwygWidget()
        return form

    # --- Patch ContentTextForm.__init__ for direct instantiation paths ---
    original_init = content_text_form_class.__init__

    def patched_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        force_wysiwyg(self)

    content_text_form_class.__init__ = patched_init
    content_text_form_class._wysiwyg_widget_applied = True
    # Sentinel that short-circuits apply_widgets' lazy __init__ re-wrap.
    content_text_form_class._unfold_widgets_applied = True

    # --- Re-wrap BasePlugin.get_initialised_{edit,create}_form_or_404 ---
    def wrap_method(cls, name):
        orig = getattr(cls, name, None)
        if orig is None:
            return

        def wrapped(self, *args, **kwargs):
            form = orig(self, *args, **kwargs)
            return force_wysiwyg(form) if form is not None else form

        setattr(cls, name, wrapped)

    wrap_method(fobi_base.BasePlugin, "get_initialised_edit_form_or_404")
    wrap_method(fobi_base.BasePlugin, "get_initialised_create_form_or_404")

    # --- Widen bleach allowlist unless the project already overrode it ---
    if not hasattr(settings, "FOBI_PLUGIN_CONTENT_TEXT_ALLOWED_TAGS"):
        content_text_forms.ALLOWED_TAGS = _TRIX_ALLOWED_TAGS
    if not hasattr(settings, "FOBI_PLUGIN_CONTENT_TEXT_ALLOWED_ATTRIBUTES"):
        content_text_forms.ALLOWED_ATTRIBUTES = _TRIX_ALLOWED_ATTRIBUTES
