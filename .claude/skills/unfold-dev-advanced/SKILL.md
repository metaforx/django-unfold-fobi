---
name: unfold-dev-advanced
description: Advanced implementation for complex changes in django-unfold-modal or unfold_extra.contrib.modal. Use Opus.
model: opus
---

# Unfold Dev (Advanced, Opus)

Use this skill for complex tasks: cross-module refactors, nested modal behavior, iframe messaging, or resizing logic.

## Model
- Default: Opus

## Workflow
1) Read `CLAUDE.md` and `plans/IMMUTABLE_BASE_PLAN.md` before changes.
2) Create or update a task in `tasks/` with clear acceptance criteria.
3) Make changes incrementally; re-check critical flows (modal open/close, popup response).
4) Add a review note in `reviews/` if requested.
5) Suggest tests or run them if the change is risky.

## Guardrails
- No new JS libraries (use only Django/Unfold provided).
- Keep template overrides minimal and within the allowed surface.
