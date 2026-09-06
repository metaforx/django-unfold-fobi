"""Regression tests for the ``UnfoldAdminCheckboxSelectMultiple`` compat shim."""

import re
from pathlib import Path

import unfold.widgets as unfold_widgets
from django import forms
from unfold.widgets import (
    UnfoldAdminCheckboxSelectMultipleWidget,
    UnfoldAdminRadioSelectWidget,
)

from unfold_fobi.forms import widgets


def test_import_smoke():
    """Importing the widgets module must not raise."""
    from unfold_fobi.forms.widgets import apply_unfold_widgets_to_form

    assert callable(apply_unfold_widgets_to_form)


def test_checkbox_select_multiple_mapping():
    """CheckboxSelectMultiple maps to Unfold's styled checkbox widget."""

    class DemoForm(forms.Form):
        colors = forms.MultipleChoiceField(
            choices=[("r", "Red"), ("g", "Green")],
            widget=forms.CheckboxSelectMultiple,
        )

    form = DemoForm()
    widgets.apply_unfold_widgets_to_form(form)

    assert isinstance(
        form.fields["colors"].widget, UnfoldAdminCheckboxSelectMultipleWidget
    )


def test_radio_select_mapping():
    """RadioSelect maps to Unfold's styled radio widget."""

    class DemoForm(forms.Form):
        color = forms.ChoiceField(
            choices=[("r", "Red"), ("g", "Green")],
            widget=forms.RadioSelect,
        )

    form = DemoForm()
    widgets.apply_unfold_widgets_to_form(form)

    assert isinstance(form.fields["color"].widget, UnfoldAdminRadioSelectWidget)


def test_shim_resolves_correctly():
    """Shim resolves to whatever ``unfold.widgets`` exposes (old alias or fallback)."""
    if hasattr(unfold_widgets, "UnfoldAdminCheckboxSelectMultiple"):
        assert (
            widgets.UnfoldAdminCheckboxSelectMultiple
            is unfold_widgets.UnfoldAdminCheckboxSelectMultiple
        )
    else:
        assert (
            widgets.UnfoldAdminCheckboxSelectMultiple
            is unfold_widgets.UnfoldAdminCheckboxSelectMultipleWidget
        )


def test_compat_shim_not_duplicated():
    """The try/except compat shim must live exactly once in the package."""
    src_root = Path(__file__).resolve().parents[2] / "src"
    pattern = re.compile(
        r"from unfold\.widgets import UnfoldAdminCheckboxSelectMultiple\b"
    )

    matches = []
    for path in src_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if pattern.search(text):
            matches.append(path)

    assert matches == [src_root / "unfold_fobi" / "forms" / "widgets.py"]
