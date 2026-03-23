# Review: feat/t03-pytest-cases — T03 pytest baseline

## Round 1

Found one P3 issue:

- [P3] `assert_no_save_ordering_button` used a disjunctive condition
  (`not in lowered OR not in lowered`) that could pass even when a submit
  control existed with implicit type or single-quote attributes.
  Fixed by simplifying to `"save ordering" not in content.lower()`.

## Round 2

No issues found. The diff introduces test utilities and baseline tests that are
internally consistent and cover the T03 scope.

**Status: DONE**