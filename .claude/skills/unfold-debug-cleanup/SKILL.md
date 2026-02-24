---
name: unfold-debug-cleanup
description: Triage and small fixes (tests, lint, small regressions) for django-unfold-modal. Use Sonnet.
model: sonnet
---

# Unfold Debug (Cleanup, Sonnet)

Use this skill for small bug fixes, test failures, or cleanup-only changes.

## Model
- Default: Sonnet
- Escalate to Opus for multi-file refactors or unclear root cause.

## Workflow
1) Identify the smallest fix that addresses the failure.
2) Avoid refactors unless necessary.
3) Update or add a test only if it directly prevents regression.
4) Provide a short review note if requested.

## Guardrails
- No new dependencies.
- Keep changes local to failing area.
