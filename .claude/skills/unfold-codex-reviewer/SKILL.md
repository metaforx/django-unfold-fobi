---
name: unfold-codex-reviewer
description: Run Codex CLI for concise code reviews after Claude completes coding, iterate until review is marked done.
model: sonnet
---

# Codex CLI Reviewer (Concise)

Use this skill **after** Claude finishes coding to run a concise Codex CLI review.

## When to use
- After a feature branch is ready and needs review.
- Repeat until review findings are resolved and the review note is marked done.

## Workflow (non-verbose)
1) Identify branch + scope.
2) Run Codex CLI and request a concise review:

Option A (interactive, uses base):
```
codex review --base <base-branch>
```
Then paste:
```
Thinking: high.
Review branch <branch-name>. Scope: <files/areas>. Findings only, ordered by severity with file:line. If none, say "No issues found."
```

Option B (non-interactive, no base):
```
git diff development...HEAD | codex review "Thinking: high. Review the diff. Findings only, ordered by severity with file:line. If none, say 'No issues found.'"
```

Notes:
- `codex` does **not** support `-q/--quiet`. Keep the prompt concise instead.
- Prefer piping the diff directly to `codex review` to avoid printing large diffs to stdout.

3) Capture findings in `reviews/<branch>__<task>.md` or update existing review note.
4) If findings exist, have Claude fix them, then re-run Codex review.
5) Stop when Codex returns "No issues found" and mark review as done.

## Guardrails
- Keep the review output short and actionable.
- Do not merge until review is clean.
