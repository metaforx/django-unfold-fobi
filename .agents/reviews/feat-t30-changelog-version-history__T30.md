# T30 — Introduce CHANGELOG.rst / version history

## What was added

`CHANGELOG.rst` at repo root, mirroring `django-unfold-extra/CHANGELOG.rst`'s
format exactly: title block, semver blurb, reverse-chronological
`X.Y.Z (YYYY-MM-DD)` headers underlined with `=` (length-matched), category
sub-headings (`Features:`, `Bug Fixes:`, `Other:`) underlined with `-`,
prose bullets per change.

24 versions covered, `0.1.1` through `0.2.1` (oldest to newest), re-derived
directly from `git log` rather than trusting the task file's seed list —
this surfaced four versions the seed list missed (`0.1.3`, `0.1.4`,
`0.1.4b1`, `0.1.4b2`), including `0.1.4b1`, which only exists on a
merged-in branch and needed a full-history walk (`git rev-list --all`) to
find. Confirmed `0.1.18` never existed (clean `0.1.17` → `0.1.19` jump).
Each version's date comes from the commit that actually introduced that
`__version__` string in `src/unfold_fobi/__init__.py` (verified via
`git show <hash>:src/unfold_fobi/__init__.py`), not commit-message guesses.

`0.2.2` is intentionally absent: it was a transient version string in
T29's fix commit, corrected to `0.2.1` before merge — `__init__.py` never
shipped at `0.2.2`, so there's nothing to document.

`0.1.4`/`0.1.4b1`/`0.1.4b2`/`0.1.4b3` are listed in semver order rather
than by raw commit date — their author dates are non-monotonic (parallel
branches reconciled by merge), so date-sorting them would scramble the
version numbering.

## Verification

- Independently re-checked several entries (including `0.1.4b1`) against
  `git show <hash>:src/unfold_fobi/__init__.py` — all correct.
- Programmatic check: every header/underline pair has an exactly matching
  character length (0 mismatches).
- `docutils.parsers.rst` parses the file with no warnings/errors.
- `src/unfold_fobi/__init__.py` confirmed untouched — still
  `__version__ = "0.2.1"`.

## Review

`codex review` (non-interactive, diff of `CHANGELOG.rst` and
`.agents/tasks/T30_changelog_version_history.md` against `main`) — ran its
own independent cross-check of every `__version__` ever committed
(`git rev-list --all`) against the changelog's version list: the only
delta is `0.2.2` (expected, see above). Verdict: "No issues found in the
staged docs-only changelog/task diff. The changelog is valid RST and
covers the visible released versions up to 0.2.1 per the task scope."

## Status

Implemented and reviewed. Not committed/pushed — awaiting human review.
