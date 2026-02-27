# Task T08 - Django Permission Alignment for Form Edit Access

Goal
- Replace owner-only edit access with Django-admin-style permission handling.
- Ensure list/detail behavior is consistent and predictable for admin users.

Suggested Skills
- Primary: `$unfold-dev-advanced` (permission/queryset changes across admin + custom views).
- Debug fallback: `$unfold-debug-refactor` for auth edge cases and permission regressions.
- Review: `$unfold-codex-reviewer`.

Dependencies
- Requires T03 baseline tests in place (reuse and extend).

Context from code back-check
- Proxy changelist shows all forms via admin model listing.
- Edit view currently inherits Fobi owner restriction (`obj.user == request.user` / user-filtered queryset).
- Result: some forms appear in list but return not found in edit for non-owner superusers/staff.

Scope
- Align edit access with Django permission model:
  - `is_superuser` can edit any form entry.
  - Staff users with `fobi.change_formentry` can edit any form entry.
  - Users without required Django permissions are denied.
- Remove owner-based filtering from edit queryset/object permission path in `unfold_fobi` custom view layer.
- Keep behavior explicit and documented for non-staff users.
- Ensure changelist/edit-link behavior matches actual access rules.
- Extend pytest coverage:
  - superuser can edit form created by a different user.
  - staff user with `change_formentry` can edit form created by a different user.
  - staff user without `change_formentry` is denied.
  - no false 404 for authorized users when object exists.

Non-goals
- No per-object permission backend integration (e.g., guardian).
- No UI redesign.

Deliverables
- Updated permission/queryset logic in edit flow.
- Tests covering cross-user edit access and denial cases.
- Notes in task/review docs about final permission semantics.

Acceptance Criteria
- A listed existing form is editable by any authorized Django admin user (not only owner).
- Unauthorized users are denied by permission checks (not by owner-filtered object lookup).
- `poetry run pytest -q` passes with added permission tests.

Tests to run
- `poetry run pytest -q`
