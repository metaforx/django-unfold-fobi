# Review: feat/unfold-admin-integration — T01 test infrastructure

## Round 1

**[P1] URL ordering in testapp makes `/admin/fobi/*` unreachable**
`tests/server/testapp/urls.py:10`

`path("admin/", admin.site.urls)` is registered before the Fobi admin includes,
so Django admin's `catch_all_view` matches all `/admin/fobi/...` paths first and
returns 404. Routes like `/admin/fobi/forms/create/` and element/handler edit
endpoints never reach `fobi.urls.class_based.edit` or the redirect views.

**Fix:** register `admin.site.urls` *after* the Fobi edit URLs.

---

## Round 2

No issues found. URL ordering fix confirmed clean.

**Status: DONE**