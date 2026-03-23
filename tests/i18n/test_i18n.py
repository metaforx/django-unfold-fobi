"""Minimal i18n smoke test coverage for the shipped German catalog."""

from pathlib import Path

from django.conf import settings
from django.core.management import call_command


def test_german_catalog_compiles_and_loads():
    """Ensure the German catalog can be compiled and resolved at runtime."""
    from django.utils import translation
    from django.utils.translation import gettext
    from django.utils.translation import trans_real

    repo_root = Path(__file__).resolve().parents[2]
    locale_dir = repo_root / "src" / "unfold_fobi" / "locale" / "de" / "LC_MESSAGES"
    po_path = locale_dir / "django.po"
    mo_path = locale_dir / "django.mo"

    assert po_path.exists(), f"German PO file not found at {po_path}"

    if (not mo_path.exists()) or mo_path.stat().st_mtime < po_path.stat().st_mtime:
        call_command("compilemessages", locale=["de"], verbosity=0)

    assert mo_path.exists(), f"Compiled German MO file not found at {mo_path}"

    # Reload Django's in-process translation cache after compiling.
    trans_real._translations.clear()
    trans_real._default = None

    try:
        with translation.override("de"):
            assert gettext("Basic information") == "Allgemeine Informationen"
    finally:
        translation.activate(settings.LANGUAGE_CODE)
