# Review: feat/t04-playwright-ui — T04 Playwright smoke baseline

## Round 1

Found one P2 issue:

- [P2] `wait_for_url("**/admin/")` glob also matched the login URL
  (`/admin/login/?next=/admin/`), making the login fixture potentially
  return before the authenticated redirect completed. Fixed by waiting
  for the exact `live_server.url + "/admin/"` URL instead.

## Round 2

No actionable bugs identified. Changes are internally consistent.

**Status: DONE**