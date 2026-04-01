# Task T22 - Prevent duplicate form names with friendly validation

Goal
- Show a user-friendly validation error instead of crashing with an
  `IntegrityError` when creating a form with a name that already exists
  for the same user.

Problem statement
- Fobi's `FormEntry` model has a `unique_together = ("user", "name")` constraint.
- When a user tries to create a form with a name that already exists, Django's
  admin add view crashes with an unhandled `IntegrityError`:
  `duplicate key value violates unique constraint "fobi_formentry_user_id_name_1ed0a04a_uniq"`
- This surfaces as a 500 error page instead of a validation message.

Root cause
- Fobi's `FormEntryForm` does not validate uniqueness of `(user, name)` at the
  form level. It relies on the database constraint, which raises an exception
  after `save()` instead of during `clean()`.
- Django's `ModelForm.validate_unique()` normally catches this, but fobi's form
  does not call it or the `user` field is excluded from the form.

Suggested Skills
- Primary: `$unfold-dev-structured`.

Dependencies
- None.

Scope
- `src/unfold_fobi/admin/form_entry_proxy.py` — add validation in `get_form`
  or `save_model` to check for duplicate names before saving.
- `tests/admin/` — add test for duplicate name rejection.

Non-goals
- No changes to fobi's model or form classes.
- No changes to the unique constraint itself.

Implementation requirements
- In `FormEntryProxyAdmin`, validate that no other `FormEntry` with the same
  `(user, name)` combination exists before saving.
- Prefer form-level validation (override `clean` or `validate_unique` on the
  form class returned by `get_form`) so the error appears as a field error
  next to the name field.
- The error message should be translatable and user-friendly, e.g.
  _("A form with this name already exists.")
- Must handle both add (new form) and change (rename) scenarios:
  - Add: reject if any existing form has the same user+name.
  - Change: reject only if a *different* form has the same user+name.

Deliverables
- Validation logic preventing duplicate form names.
- Test: creating a form with a duplicate name returns a form error, not a 500.
- Test: renaming a form to a conflicting name returns a form error.
- Test: saving a form with its own existing name succeeds (no false positive).
- `poetry run pytest -q` passes.

Acceptance Criteria
- Creating a form with a duplicate name shows a validation error on the name
  field, not a 500 `IntegrityError`.
- Renaming a form to a conflicting name shows a validation error.
- Saving a form without changing its name succeeds.
- `poetry run pytest -q` passes.

Tests to run
- `poetry run pytest -q`
