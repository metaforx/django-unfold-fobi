---
name: unfold-debug-refactor
description: Deep debugging or refactoring for django-unfold-modal/unfold_extra. Use Opus.
model: opus
---

# Unfold Debug (Refactor, Opus)

Use this skill when the fix requires structural changes or multi-step investigation.

## Model
- Default: Opus

## Workflow
1) Reproduce or reason about the failure and document assumptions.
2) Propose a minimal refactor plan before editing.
3) Apply changes in small commits if possible.
4) Update tests if behavior changes.

## Guardrails
- No new JS libraries.
- Preserve existing external interfaces unless explicitly asked to change them.
