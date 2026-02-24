# Unfold Fobi Integration Plan (Build Readme)

Goal: Unfold Fobi integrates `django-fobi` natively into the Unfold admin.
Target package: `unfold_fobi` (symlinked in project).

This document is a step-by-step build plan for another AI agent. Each item is a checkbox to be ticked once implemented and verified.

References:
- Unfold custom pages: https://unfoldadmin.com/docs/configuration/custom-pages/
- Add view: `http://localhost:8080/admin/unfold_fobi/formentryproxy/add/`
- Edit view: `http://localhost:8080/admin/unfold_fobi/formentryproxy/edit/7/`

## 1) Add View (FormEntryProxy add)

**Goal:** align the add view with Unfold UX patterns, with clean field grouping and i18n-ready labels.

- [x] Confirm add view URL renders via Unfold admin and uses Unfold base layout.
- [x] Define logical fieldsets for the add form (group by purpose, not by model order).
  - Example grouping concept (adjust to real fields):
    - "Basic details" (name, slug, status)
    - "Form settings" (public/private, theme, handler)
    - "Scheduling" (publish/expiry date, start/end)
    - "Metadata" (created/updated if editable)
- [x] Group date/time fields into a dedicated fieldset.
  - All date/time inputs should live in the same fieldset with a clear label.
- [ ] Add i18n support for all frontend elements on the add view:
  - Fieldset titles
  - Section headers
  - Helper texts or UI labels
  - Button labels or custom UI strings
- [ ] Verify all translated strings appear in UI and are extractable for `django.po`.

Notes:
- Prefer Unfold’s fieldset styling and default form patterns where possible.
- Keep layout consistent with other Unfold admin forms.

## 2) Edit View (FormEntryProxy edit)

**Goal:** match Unfold custom page integration and native tab patterns while preserving Fobi functionality.

### Layout & Structure
- [ ] Ensure the edit view is implemented as an Unfold custom page (per docs).
- [ ] Remove the H1 title from the edit view.
- [ ] Add an H2 styled as a legend under the tabs/nav (see legend snippet below).

### Tabs
- [ ] Replace current jQuery UI tab markup/classes with Unfold native tabs.
  - Current classes:
    - `tab-links ui-tabs-nav ui-helper-reset ui-helper-clearfix ui-widget-header ui-corner-all`
  - Target structure/classes:
    ```
    <nav id="tabs-items" class="bg-base-100 flex flex-row font-medium gap-1 p-1 rounded-default text-important dark:border-base-700 md:w-auto dark:bg-white/[.04] *:flex *:flex-row *:font-medium *:whitespace-nowrap *:items-center *:px-2.5 *:py-[5px] *:rounded-default *:transition-colors *:hover:bg-base-700/[.04] *:dark:hover:bg-white/[.04] [&>.active]:bg-white [&>.active]:shadow-xs [&>.active]:hover:bg-white [&>.active]:dark:bg-base-900 [&>.active]:dark:hover:bg-base-900">
    ```
- [ ] Ensure active tab styling uses the Unfold pattern (`.active`).
- [ ] Verify tab structure is accessible and consistent with Unfold components.

### Actions (Add Form Element)
- [x] Use Unfold Select widget for the "Add form element" action.
- [x] Align the "Add form element" action on the same nav level as tabs, **right-aligned**.
- [x] Remove "Save ordering" from Elements tab; auto-save ordering on reorder.
- [x] Keep save actions in their current locations but use Unfold button styles.

### Header / Breadcrumbs
- [ ] Update document header breadcrumb structure:
  - Current: `<- Fobi - Form entries - Tesformular - Editform`
  - Desired: `<- Unfold_Fobi (link from changelist) - Forms (builder) - Tesformular`
- [ ] Ensure the active item is the form name (`Tesformular`).

### Legend Styling
### Table / Grid Styling
- [ ] Apply Unfold button styles to all user actions in `table-striped`.
- [ ] Replace `table-striped` with Unfold-style grid cards (use the grid example as baseline).
- [x] Apply legend styling for H2:
  ```
  <legend class="border-b border-base-200 font-semibold float-left mb-5 -mx-3 pb-3 px-3 text-[15px] text-font-important-light dark:text-font-important-dark dark:border-base-800">
      Custom form
  </legend>
  ```

## 3) Verification Checklist

- [ ] Add view renders with correct fieldsets and date grouping.
- [ ] All add-view UI strings are i18n-wrapped and extracted.
- [ ] Edit view uses Unfold custom page layout.
- [ ] Tabs render with Unfold classes and correct active state.
- [ ] "Add form element" uses Unfold Select and aligns right in nav row.
- [ ] H1 removed; H2/legend styled correctly.
- [ ] Breadcrumbs match desired structure with correct active item.
- [ ] Save actions use Unfold button styles and stay in current locations.
- [ ] Elements tab auto-saves ordering (no Save ordering button).
- [ ] Table actions use Unfold button styles.
- [ ] Table/grid layout matches Unfold grid components.

## Notes for Implementer

- Keep changes in `unfold_fobi` so the integration is reusable across projects.
- Prefer small, targeted template overrides rather than large forked templates.
- Verify behavior in both light and dark themes.
