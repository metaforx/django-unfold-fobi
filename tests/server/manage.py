#!/usr/bin/env python
"""Django's command-line utility for the unfold_fobi test server."""
import os
import sys
from pathlib import Path


def main():
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    sys.dont_write_bytecode = True
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testapp.settings")

    # Ensure src/ and tests/server/ are on sys.path so that
    # `unfold_fobi` and `testapp` packages are importable when
    # running manage.py directly (without pytest pythonpath config).
    repo_root = Path(__file__).resolve().parent.parent.parent
    for extra in [str(repo_root / "src"), str(Path(__file__).resolve().parent)]:
        if extra not in sys.path:
            sys.path.insert(0, extra)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
