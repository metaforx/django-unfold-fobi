"""ALTCHA challenge endpoint for frontend clients."""

from django.views.decorators.cache import never_cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .challenge import create_challenge


@api_view(["GET"])
@never_cache
@permission_classes([AllowAny])
def altcha_challenge(request):
    """Return a fresh ALTCHA challenge for the frontend widget."""
    return Response(create_challenge())
