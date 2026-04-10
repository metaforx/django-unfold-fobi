from cms.plugin_pool import plugin_pool
from django.apps import apps as django_apps
from django.utils.translation import gettext_lazy as _
from fobi.integration.processors import IntegrationProcessor
from fobi.models import FormEntry
from unfold_extra.contrib.cms.plugins import UnfoldCMSPluginBase

from .models import FobiFormPluginModel

try:
    from .serializers import FobiFormPluginSerializer
except ImportError:
    FobiFormPluginSerializer = None


def _get_form_queryset(request):
    """Return the FormEntry queryset filtered by site scope when available."""
    qs = FormEntry.objects.all()

    if not django_apps.is_installed("unfold_fobi.contrib.sites"):
        return qs

    from django.contrib.sites.models import Site
    from unfold_fobi.contrib.sites.conf import get_sites_for_user_func

    current_site = Site.objects.get_current(request)
    qs = qs.filter(site_binding__sites=current_site)

    if not request.user.is_superuser:
        user_sites = get_sites_for_user_func()(request.user)
        qs = qs.filter(site_binding__sites__in=user_sites)

    return qs.distinct()


@plugin_pool.register_plugin
class FobiFormPlugin(UnfoldCMSPluginBase, IntegrationProcessor):
    """django CMS plugin for embedding a Fobi form.

    Uses fobi's ``IntegrationProcessor`` to render the actual form
    (handles GET display and POST submission).
    """

    model = FobiFormPluginModel
    module = _("Forms")
    name = _("Form")
    render_template = "unfold_fobi/cms/form_plugin.html"
    can_redirect = False

    if FobiFormPluginSerializer is not None:
        serializer_class = FobiFormPluginSerializer

    def get_form(self, request, obj=None, change=False, **kwargs):
        """Restrict form_entry dropdown to forms allowed by site scope."""
        form_class = super().get_form(request, obj, change, **kwargs)
        qs = _get_form_queryset(request)

        class FilteredForm(form_class):
            def __init__(self, *args, **form_kwargs):
                super().__init__(*args, **form_kwargs)
                if "form_entry" in self.fields:
                    self.fields["form_entry"].queryset = qs

        return FilteredForm

    def render(self, context, instance, placeholder):
        """Render the fobi form via IntegrationProcessor into template context."""
        context = super().render(context, instance, placeholder)
        if instance.form_entry_id:
            self._process(context["request"], instance)
            context["rendered_form"] = getattr(self, "rendered_output", "")
        return context

