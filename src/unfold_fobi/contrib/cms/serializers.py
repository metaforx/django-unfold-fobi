from rest_framework import serializers

from .models import FobiFormPluginModel


class FormEntrySerializer(serializers.Serializer):
    """Inline representation of the referenced Fobi form entry."""

    name = serializers.CharField(read_only=True)
    slug = serializers.SlugField(read_only=True)


class FobiFormPluginSerializer(serializers.ModelSerializer):
    form_entry = FormEntrySerializer(read_only=True)

    class Meta:
        model = FobiFormPluginModel
        exclude = (
            "id",
            "placeholder",
            "language",
            "position",
            "creation_date",
            "changed_date",
            "parent",
        )
