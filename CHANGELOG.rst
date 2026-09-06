=========
Changelog
=========

All notable changes to django-unfold-fobi are documented here.
This project adheres to `Semantic Versioning <https://semver.org/>`_.


0.2.1 (2026-09-05)
==================

Bug Fixes:
----------

* Fix ``ImportError`` for ``UnfoldAdminCheckboxSelectMultiple`` on
  django-unfold >=0.94.0, which dropped that alias in favor of
  ``UnfoldAdminCheckboxSelectMultipleWidget``. The import now falls back to
  the Widget-suffixed class when the alias is unavailable.


0.2.0 (2026-06-01)
==================

Features:
---------

* Add WYSIWYG support for the ``content_text`` plugin, with a customizable
  toolbar.

Bug Fixes:
----------

* Remove unnecessary cursor styling on form rows.
* Correct "underlined" to "underline" in the README and templates, and add
  ``functools.wraps`` to the patch decorator.
* Remove a redundant attribute from the WYSIWYG toolbar template.


0.1.20 (2026-05-19)
===================

Bug Fixes:
----------

* Remove the ``id`` field from the serializer exclusion list for
  ``FobiFormPluginModel``.


0.1.19 (2026-05-08)
===================

Bug Fixes:
----------

* Update the ``cmsplugin_ptr`` field on ``FobiFormPluginModel`` to align
  with Django 5.2+ requirements.
* Add a guard to prevent bulk export across multiple forms in the admin
  interface.


0.1.17 (2026-05-05)
===================

Bug Fixes:
----------

* Enhance field serialization to include metadata for placeholders and
  initial values.
* Improve serialization of initial values in API responses to correctly
  handle datetime objects.
* Add a metadata form fixture and enhance field serialization for API
  responses.
* Update form entry references and enhance admin search fields.


0.1.16 (2026-05-04)
===================

Bug Fixes:
----------

* Add an inactive-page title and message to the form entry context.


0.1.15 (2026-05-04)
===================

Bug Fixes:
----------

* Update the "Export entries" button to use the project-specific admin
  endpoint, ensuring correct CSV export for all staff users.


0.1.14 (2026-04-23)
===================

Bug Fixes:
----------

* Add German translations for active form fields and inactive form
  messages.


0.1.13 (2026-04-23)
===================

Features:
---------

* Add save-first notices for form elements and handlers in the add view.


0.1.12 (2026-04-23)
===================

Bug Fixes:
----------

* Update German translations for various form-related messages and fix a
  typo in the CSV export.


0.1.11 (2026-04-11)
===================

Features:
---------

* Add optional ALTCHA integration for DRF public form submissions.

Other:
------

* Improve ALTCHA payload validation and error handling, and update altcha
  to v2.0.0.


0.1.10 (2026-04-10)
===================

Features:
---------

* Add a site-aware django CMS Fobi form plugin.

Bug Fixes:
----------

* Remove the duplicate delete action and update German translations.
* Mark ``rendered_form`` as safe in the form plugin template.


0.1.9 (2026-04-01)
==================

Features:
---------

* Implement site-scoped preview filtering for the form-fields API.


0.1.8 (2026-04-01)
==================

Features:
---------

* Add preview access for non-public forms in the form-fields API.


0.1.7 (2026-04-01)
==================

Features:
---------

* Implement a reusable ``SavedFormDataEntry`` admin with readonly,
  pretty-printed data rendering.
* Add validation to prevent duplicate form names.
* Implement safe deletion of ``FormEntryProxy`` while preserving submitted
  data.

Bug Fixes:
----------

* Sanitize JSON to prevent XSS injection.
* Update form deletion logic to use app-level permissions.


0.1.6 (2026-03-28)
==================

Other:
------

* Version bump only; no functional changes.


0.1.5 (2026-03-26)
==================

Other:
------

* Version bump only; no functional changes.


0.1.4 (2026-03-25)
==================

Features:
---------

* Enforce active dates on REST API submissions and expose form metadata.
* Use an HTTP status constant instead of a magic number.

Other:
------

* README overhaul.


0.1.4b3 (2026-03-26)
====================

Features:
---------

* Add caching prevention to the ``get_form_fields`` API endpoint.


0.1.4b2 (2026-03-25)
====================

Features:
---------

* Include the CSRF token in the form-fields API response for seamless
  frontend submissions.


0.1.4b1 (2026-03-25)
====================

Bug Fixes:
----------

* Update permissions for the form entry import action.


0.1.3 (2026-03-24)
==================

Features:
---------

* Support all fobi field types, with a fallback for widget API field-type
  lookups.


0.1.2 (2026-03-24)
==================

Features:
---------

* Add widget type to the form-fields API response for better frontend
  handling.


0.1.1 (2026-03-23)
==================

Other:
------

* First version tracked via ``unfold_fobi.__version__``; add compiled
  German locale translations and adjust localization file handling.
