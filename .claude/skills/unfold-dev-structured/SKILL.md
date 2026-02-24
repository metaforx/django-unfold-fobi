---
name: unfold-dev-structured
description: Structured implementation for small/medium changes in django-unfold-modal or unfold_extra.contrib.modal. Use Sonnet by default.
model: sonnet
---

# Unfold Dev (Structured, Sonnet)

Use this skill for well-scoped tasks (docs, small features, tests, minor JS/CSS changes).

## Model
- Default: Sonnet
- Escalate to Opus if cross-module changes, complex UI flows, or >300 LOC core logic.

## Workflow
1) Read `CLAUDE.md` and `plans/IMMUTABLE_BASE_PLAN.md` before changes.
2) Follow the task file in `tasks/` and keep scope tight.
3) Prefer minimal diffs; no new JS libraries (only Django/Unfold provided).
4) Add/update review notes in `reviews/` if required.
5) Run tests only if requested or if changes are risky.

## Guardrails
- No edits outside task scope.
- No new dependencies unless explicitly requested.
