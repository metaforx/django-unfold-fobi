"""Return a close-and-reload popup response when ``_popup=1`` is set.

Fobi add/edit/delete views always redirect after a successful
operation.  When the view is opened in popup mode (``?_popup=1``),
we intercept the redirect and return a tiny HTML page that tells
the opening window to reload, compatible with both ``window.open``
popups and ``django-unfold-modal`` iframe modals.
"""


def apply():
    """Patch fobi add/edit/delete views for popup mode — idempotent."""
    from django.http import HttpResponse
    from django.template.loader import render_to_string

    try:
        from fobi.views.class_based import (
            AddFormElementEntryView,
            AddFormHandlerEntryView,
            DeleteFormElementEntryView,
            DeleteFormHandlerEntryView,
            EditFormElementEntryView,
            EditFormHandlerEntryView,
        )
    except ImportError:
        return

    POPUP_TEMPLATE = "admin/unfold_fobi/popup_response.html"
    SESSION_KEY = "_fobi_popup_count"

    def _is_popup(request):
        return (
            request.GET.get("_popup")
            or request.POST.get("_popup")
            or request.session.get(SESSION_KEY, 0) > 0
        )

    def _popup_http_response(request):
        count = request.session.get(SESSION_KEY, 0)
        if count > 1:
            request.session[SESSION_KEY] = count - 1
        else:
            request.session.pop(SESSION_KEY, None)
        html = render_to_string(POPUP_TEMPLATE)
        response = HttpResponse(html)
        response["X-Frame-Options"] = "SAMEORIGIN"
        return response

    def _is_success_redirect(response):
        if response.status_code not in (301, 302):
            return False
        location = response.get("Location", "")
        from django.conf import settings

        login_path = getattr(settings, "LOGIN_URL", "/accounts/login/")
        if login_path and login_path in location:
            return False
        return True

    def _wrap_method(original, method_name, intercept_get_redirect=False):
        def wrapped(self, request, *args, **kwargs):
            if method_name == "get":
                if request.GET.get("_popup"):
                    count = request.session.get(SESSION_KEY, 0)
                    request.session[SESSION_KEY] = count + 1
                else:
                    request.session.pop(SESSION_KEY, None)
            response = original(self, request, *args, **kwargs)
            intercept = (
                _is_popup(request)
                and _is_success_redirect(response)
                and (request.method == "POST" or intercept_get_redirect)
            )
            if intercept:
                return _popup_http_response(request)
            if _is_popup(request):
                response["X-Frame-Options"] = "SAMEORIGIN"
            return response

        return wrapped

    add_views = (AddFormElementEntryView, AddFormHandlerEntryView)
    edit_views = (EditFormElementEntryView, EditFormHandlerEntryView)
    delete_views = (DeleteFormElementEntryView, DeleteFormHandlerEntryView)

    for view_cls in edit_views:
        for method_name in ("get", "post"):
            method = getattr(view_cls, method_name, None)
            if method and not getattr(method, "_unfold_popup_patched", False):
                wrapped = _wrap_method(method, method_name)
                wrapped._unfold_popup_patched = True
                setattr(view_cls, method_name, wrapped)

    for view_cls in (*add_views, *delete_views):
        for method_name in ("get", "post"):
            method = getattr(view_cls, method_name, None)
            if method and not getattr(method, "_unfold_popup_patched", False):
                wrapped = _wrap_method(method, method_name, intercept_get_redirect=True)
                wrapped._unfold_popup_patched = True
                setattr(view_cls, method_name, wrapped)
