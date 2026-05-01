# Changelog

## [Unreleased]

### Initial scaffolding (2026-04-30)
- Repo created as part of the 3-repo plan (safe-mini · justai · local-resident).
- Reference implementation seeded under `reference/` from the pre-public lab study (`~/projects/mini-swe-agent-study-2026-04-29/lab/`): 54 trials, 6 task families, 9 configs.
- Production module skeleton at `safe_mini/` — runner, types, protocol, policies, observation policies, classifier — TODO-stubbed pending the careful port from reference.
- Test fixtures: `tests/fixtures/practice_repo/` is the original lab practice_repo, ready for regression suites.
