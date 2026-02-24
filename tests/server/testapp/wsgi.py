"""WSGI config for the unfold_fobi test server."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testapp.settings")

application = get_wsgi_application()
