"""Native change-view popup contracts and modal response behavior."""

import re

import pytest
from django.urls import reverse


class TestPopupModeLinks:
    """Popup links must include `_popup=1` on inline and dropdown actions."""

    def test_element_edit_link_has_popup_param(self, change_html, form_entry):
        element = form_entry.formelemententry_set.first()
        edit_url = reverse(
            "fobi.edit_form_element_entry",
            kwargs={"form_element_entry_id": element.pk},
        )
        assert f"{edit_url}?_popup=1" in change_html

    def test_element_delete_link_has_popup_param(self, change_html, form_entry):
        element = form_entry.formelemententry_set.first()
        delete_url = reverse(
            "fobi.delete_form_element_entry",
            kwargs={"form_element_entry_id": element.pk},
        )
        assert f"{delete_url}?_popup=1" in change_html

    def test_add_element_link_has_popup_param(self, change_html, form_entry):
        add_url = reverse(
            "fobi.add_form_element_entry",
            kwargs={
                "form_entry_id": form_entry.pk,
                "form_element_plugin_uid": "text",
            },
        )
        assert f"{add_url}?_popup=1" in change_html

    def test_handler_delete_link_has_popup_param(self, change_html, form_entry):
        from fobi.models import FormHandlerEntry

        handler = FormHandlerEntry.objects.filter(
            form_entry=form_entry, plugin_uid="db_store"
        ).first()
        delete_url = reverse(
            "fobi.delete_form_handler_entry",
            kwargs={"form_handler_entry_id": handler.pk},
        )
        assert f"{delete_url}?_popup=1" in change_html


class TestUnfoldModalTriggerContract:
    """Popup links must follow Django admin popup contract for unfold-modal."""

    def test_element_edit_has_data_popup(self, change_html, form_entry):
        element = form_entry.formelemententry_set.first()
        assert f'id="change_fobi_element_{element.pk}" data-popup="yes"' in change_html

    def test_element_delete_has_data_popup(self, change_html, form_entry):
        element = form_entry.formelemententry_set.first()
        assert f'id="delete_fobi_element_{element.pk}" data-popup="yes"' in change_html

    def test_element_edit_has_wrapper_link_class(self, change_html):
        assert "related-widget-wrapper-link" in change_html

    def test_add_element_has_data_popup(self, change_html):
        assert 'id="add_fobi_element_text"' in change_html
        assert 'data-popup="yes"' in change_html

    def test_handler_delete_has_data_popup(self, change_html, form_entry):
        from fobi.models import FormHandlerEntry

        handler = FormHandlerEntry.objects.filter(
            form_entry=form_entry, plugin_uid="db_store"
        ).first()
        assert f'id="delete_fobi_handler_{handler.pk}" data-popup="yes"' in change_html

    def test_no_inline_window_open(self, change_html):
        assert "window.open(this.href" not in change_html

    def test_popup_bridge_js_loaded_for_add_dropdowns(self, change_html):
        assert "unfold_fobi/js/admin_popup_actions.js" in change_html


class TestPopupResponse:
    """Fobi popup views must return popup HTML instead of redirects."""

    @staticmethod
    def _text_plugin_post_data(element):
        import json as _json

        data = _json.loads(element.plugin_data)
        return {
            "name": data.get("name", "full_name"),
            "label": data.get("label", "Full Name"),
            "max_length": data.get("max_length", "255"),
            "required": "1" if data.get("required") else "",
            "placeholder": data.get("placeholder", ""),
            "help_text": data.get("help_text", ""),
            "initial": data.get("initial", ""),
        }

    def test_element_edit_popup_returns_html_not_redirect(
        self, admin_client, form_entry
    ):
        element = form_entry.formelemententry_set.first()
        edit_url = reverse(
            "fobi.edit_form_element_entry",
            kwargs={"form_element_entry_id": element.pk},
        )
        get_resp = admin_client.get(edit_url + "?_popup=1")
        assert get_resp.status_code == 200

        post_data = {**self._text_plugin_post_data(element), "_popup": "1"}
        resp = admin_client.post(edit_url + "?_popup=1", data=post_data)
        assert resp.status_code == 200
        content = resp.content.decode()
        assert "postMessage" in content or "window.opener" in content

    def test_element_edit_without_popup_still_redirects(self, admin_client, form_entry):
        element = form_entry.formelemententry_set.first()
        edit_url = reverse(
            "fobi.edit_form_element_entry",
            kwargs={"form_element_entry_id": element.pk},
        )
        post_data = self._text_plugin_post_data(element)
        resp = admin_client.post(edit_url, data=post_data)
        assert resp.status_code == 302


class TestIframeXFrameOptions:
    """Popup responses must allow same-origin iframe embedding."""

    def test_settings_has_sameorigin(self):
        from django.conf import settings

        assert getattr(settings, "X_FRAME_OPTIONS", None) == "SAMEORIGIN"

    def test_element_edit_popup_has_sameorigin_header(self, admin_client, form_entry):
        element = form_entry.formelemententry_set.first()
        edit_url = reverse(
            "fobi.edit_form_element_entry",
            kwargs={"form_element_entry_id": element.pk},
        )
        resp = admin_client.get(edit_url + "?_popup=1")
        assert resp.status_code == 200
        assert resp["X-Frame-Options"] == "SAMEORIGIN"

    def test_element_edit_non_popup_inherits_global(self, admin_client, form_entry):
        element = form_entry.formelemententry_set.first()
        edit_url = reverse(
            "fobi.edit_form_element_entry",
            kwargs={"form_element_entry_id": element.pk},
        )
        resp = admin_client.get(edit_url)
        assert resp["X-Frame-Options"] == "SAMEORIGIN"

    def test_add_element_popup_has_sameorigin_header(self, admin_client, form_entry):
        add_url = reverse(
            "fobi.add_form_element_entry",
            kwargs={"form_entry_id": form_entry.pk, "form_element_plugin_uid": "text"},
        )
        resp = admin_client.get(add_url + "?_popup=1")
        if resp.status_code == 200:
            assert resp["X-Frame-Options"] == "SAMEORIGIN"
        else:
            assert resp.status_code == 200 or resp["X-Frame-Options"] == "SAMEORIGIN"

    def test_popup_response_after_save_has_sameorigin_header(
        self, admin_client, form_entry
    ):
        import json as _json

        element = form_entry.formelemententry_set.first()
        edit_url = reverse(
            "fobi.edit_form_element_entry",
            kwargs={"form_element_entry_id": element.pk},
        )
        admin_client.get(edit_url + "?_popup=1")
        data = _json.loads(element.plugin_data)
        post_data = {
            "name": data.get("name", "full_name"),
            "label": data.get("label", "Full Name"),
            "max_length": data.get("max_length", "255"),
            "required": "1" if data.get("required") else "",
            "placeholder": data.get("placeholder", ""),
            "help_text": data.get("help_text", ""),
            "initial": data.get("initial", ""),
            "_popup": "1",
        }
        resp = admin_client.post(edit_url + "?_popup=1", data=post_data)
        assert resp.status_code == 200
        assert resp["X-Frame-Options"] == "SAMEORIGIN"


class TestPopupLayout:
    """Popup add/edit screens must not render the admin nav sidebar."""

    def test_add_element_popup_hides_nav_sidebar(self, admin_client, form_entry):
        add_url = reverse(
            "fobi.add_form_element_entry",
            kwargs={"form_entry_id": form_entry.pk, "form_element_plugin_uid": "text"},
        )
        resp = admin_client.get(add_url + "?_popup=1")
        assert resp.status_code == 200
        assert 'id="nav-sidebar"' not in resp.content.decode()

    def test_add_handler_popup_hides_nav_sidebar(self, admin_client, form_entry):
        add_url = reverse(
            "fobi.add_form_handler_entry",
            kwargs={"form_entry_id": form_entry.pk, "form_handler_plugin_uid": "mail"},
        )
        resp = admin_client.get(add_url + "?_popup=1")
        assert resp.status_code == 200
        assert 'id="nav-sidebar"' not in resp.content.decode()


class TestPopupSubmitRow:
    """Popup add/edit screens must render the shared Unfold submit row."""

    @staticmethod
    def assert_submit_row(response, button_text):
        assert response.status_code == 200
        html = response.content.decode()
        assert 'backdrop-blur-xs bg-white/80' in html
        assert 'bg-primary-600 text-white' in html
        match = re.search(
            r'<button type="submit"[^>]*>\s*(.*?)\s*</button>',
            html,
            re.S,
        )
        assert match is not None
        assert match.group(1).strip() == button_text
        return html

    def test_add_element_popup_renders_submit_row(self, admin_client, form_entry):
        add_url = reverse(
            "fobi.add_form_element_entry",
            kwargs={"form_entry_id": form_entry.pk, "form_element_plugin_uid": "text"},
        )
        html = self.assert_submit_row(admin_client.get(add_url + "?_popup=1"), "Save")
        assert 'id="form_element_entry_form"' in html

    def test_edit_element_popup_renders_submit_row(self, admin_client, form_entry):
        element = form_entry.formelemententry_set.first()
        edit_url = reverse(
            "fobi.edit_form_element_entry",
            kwargs={"form_element_entry_id": element.pk},
        )
        html = self.assert_submit_row(admin_client.get(edit_url + "?_popup=1"), "Save")
        assert 'id="form_element_entry_form"' in html

    def test_add_handler_popup_renders_submit_row(self, admin_client, form_entry):
        add_url = reverse(
            "fobi.add_form_handler_entry",
            kwargs={"form_entry_id": form_entry.pk, "form_handler_plugin_uid": "mail"},
        )
        html = self.assert_submit_row(admin_client.get(add_url + "?_popup=1"), "Save")
        assert 'id="fobi-form"' in html

    def test_edit_handler_popup_renders_submit_row(self, admin_client, form_entry):
        from fobi.models import FormHandlerEntry

        handler, _ = FormHandlerEntry.objects.get_or_create(
            form_entry=form_entry,
            plugin_uid="mail",
        )
        edit_url = reverse(
            "fobi.edit_form_handler_entry",
            kwargs={"form_handler_entry_id": handler.pk},
        )
        html = self.assert_submit_row(admin_client.get(edit_url + "?_popup=1"), "Save")
        assert 'id="fobi-form"' in html
