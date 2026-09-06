# Task T30 - Introduce CHANGELOG.rst / version history

Type
- Docs/infra addition. No behavior change, no version bump.

Goal
- Give `unfold-fobi` a proper, hand-maintained version history, matching
  the `CHANGELOG.rst` convention already used in the sibling repo
  `django-unfold-extra` (`~/code/django-unfold-extra/CHANGELOG.rst`).

Problem statement
- `unfold-fobi` has no changelog: no `CHANGELOG.rst`/`.md`, no changelog
  section in `README.md`, no GitHub Releases (`gh release list` returns
  nothing). Version bumps are bare `chore: bump version to X` commits (or,
  for T29, folded into the fix commit itself) with no record anywhere of
  what actually shipped in each release.
- `git log --all` shows at least these version bumps to backfill (oldest
  first): 0.1.1, 0.1.2, 0.1.4b3, 0.1.5, 0.1.6, 0.1.7, 0.1.8, 0.1.9, 0.1.10,
  0.1.12, 0.1.13, 0.1.14, 0.1.15, 0.1.16, 0.1.17, 0.1.19, 0.1.20, 0.2.0,
  0.2.1 (introduced inline in the T29 fix commit, not its own bump commit)
  — re-derive the exact/complete list from `git log`, don't trust this
  list blindly, some early tags may use different commit message wording
  ("update version to X" vs "bump version to X").

Scope
- New `CHANGELOG.rst` at repo root.
- No other files. Do not touch `src/unfold_fobi/__init__.py` — leave
  `__version__ = "0.2.1"` exactly as-is; this task documents history up to
  and including 0.2.1, it does not cut a new release.

Non-goals
- No changelog automation (no towncrier, git-cliff, commitizen, etc.) —
  hand-maintained, same as `django-unfold-extra`.
- No version bump.
- No rewriting of existing git history or commit messages.
- No changelog entry for T29a's pending `0.2.2` — that lands when T29a
  actually merges and its own version bump is restored.

Format (mirror `django-unfold-extra/CHANGELOG.rst` exactly)

```rst
=========
Changelog
=========

All notable changes to django-unfold-fobi are documented here.
This project adheres to `Semantic Versioning <https://semver.org/>`_.


0.2.1 (2026-06-01)
==================

Bug Fixes:
----------

* <what changed, in prose, one bullet per change>


0.2.0 (2026-06-01)
==================
...
```

- Reverse-chronological, newest first.
- Version + date header line: `X.Y.Z (YYYY-MM-DD)`. Underline with `=`,
  same character length as the header line above it (confirmed in the
  reference file: `0.5.1 (2026-08-26)` is 18 chars, underlined with 18
  `=` chars — count, don't eyeball).
- Category sub-headings as needed per version: `Features:`, `Bug Fixes:`,
  `Changed:`, `Other:` (underlined with `-`, matching that line's length).
  Not every version needs every category.
- Get each version's date from its bump commit: `git log --format="%h %ad
  %s" --date=short -- src/unfold_fobi/__init__.py` (or search full log for
  the relevant commit hash) rather than guessing.
- Write entries in prose describing what the change does (same register as
  the reference file's newer entries, e.g. its `0.5.0`/`0.5.1` sections) —
  the reference file's oldest entries are terser with a trailing commit
  hash like `(d324734)`; that's an artifact of an earlier, less careful
  pass — don't copy that shorthand style for new entries here.
- Source material per version: the corresponding commit(s)/PR in
  `git log`, and any matching notes already in `.agents/reviews/` (e.g.
  T27, T28, T29 each have a review file describing exactly what shipped).

Deliverables
- `CHANGELOG.rst` at repo root, covering every released version up to and
  including 0.2.1.

Acceptance Criteria
- `CHANGELOG.rst` exists, valid RST, structurally matches
  `django-unfold-extra/CHANGELOG.rst` (title block, semver blurb, header/
  underline conventions, category sub-headings).
- Every version bump visible in `git log` has a corresponding entry, in
  the correct chronological order, with the correct date.
- `src/unfold_fobi/__init__.py` still reads `__version__ = "0.2.1"` —
  unchanged by this task.

Tests to run
- None (docs-only). If a repo-wide lint step exists, run it; otherwise
  visually verify RST renders correctly (e.g. via `python -c "import
  docutils.parsers.rst"` availability, or just careful manual review).

Suggested Skills
- Primary: `$unfold-dev-structured`.
- Review: `$unfold-codex-reviewer`.

Dependencies
- None.

Branch
- `feat/t30-changelog-version-history`.
- Do not commit or push until reviewer approval.
