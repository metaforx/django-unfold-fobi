"""WSGI config for the unfold_fobi test server."""
import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
sys.dont_write_bytecode = True
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testapp.settings")

application = get_wsgi_application()
