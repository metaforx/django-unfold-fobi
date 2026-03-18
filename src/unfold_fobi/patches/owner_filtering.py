"""Remove owner filtering from fobi edit/delete views for staff users.

Fobi hardcodes two layers of owner checks:
1. ``_get_queryset`` filters by ``form_entry__user__pk == request.user.pk``
2. Permission classes check ``obj.form_entry.user == request.user``

Both cause 404 / PermissionDenied when an admin who is not the form's
original creator tries to edit or delete elements/handlers.  This patch
relaxes both checks for ``is_staff`` users.
"""


def apply():
    """Patch fobi views and permissions — idempotent."""
    _patch_querysets()
    _patch_permissions()


def _patch_querysets():
    try:
        from fobi.views.class_based import (
            AbstractDeletePluginEntryView,
            EditFormElementEntryView,
            EditFormHandlerEntryView,
        )
    except ImportError:
        return

    def _make_staff_queryset(original):
        def _get_queryset(self, request):
            qs = original(self, request)
            if request.user.is_staff:
                return qs.model._default_manager.select_related(
                    "form_entry", "form_entry__user"
                )
            return qs

        return _get_queryset

    for view_cls in (
        EditFormElementEntryView,
        EditFormHandlerEntryView,
        AbstractDeletePluginEntryView,
    ):
        if not getattr(view_cls._get_queryset, "_unfold_patched", False):
            view_cls._get_queryset = _make_staff_queryset(view_cls._get_queryset)
            view_cls._get_queryset._unfold_patched = True


def _patch_permissions():
    try:
        from fobi.permissions.default import (
            DeleteFormElementEntryPermission,
            DeleteFormHandlerEntryPermission,
            EditFormElementEntryPermission,
            EditFormHandlerEntryPermission,
        )
    except ImportError:
        return

    def _make_staff_object_perm(original):
        def has_object_permission(self, request, view, obj):
            if request.user.is_staff:
                return True
            return original(self, request, view, obj)

        return has_object_permission

    for perm_cls in (
        EditFormElementEntryPermission,
        DeleteFormElementEntryPermission,
        EditFormHandlerEntryPermission,
        DeleteFormHandlerEntryPermission,
    ):
        method = perm_cls.has_object_permission
        if not getattr(method, "_unfold_patched", False):
            patched = _make_staff_object_perm(method)
            patched._unfold_patched = True
            perm_cls.has_object_permission = patched
