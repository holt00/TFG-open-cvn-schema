# Hotfix 2 - Human Project Entrypoint And Update Protocol Alignment

## Summary

Hotfix `#2` introduced `PROJECT_GUIDE.md` as the human-facing entry point for
the repository, stopped routing human readers through `AGENTS.md`, and updated
the documentation maintenance protocol so future issue work also updates the
human guide when repository orientation changes.

## Original Goal

- create a human-oriented entry point equivalent in practical information to
  `AGENTS.md`
- update `README.md` and `CONTRIBUTING.md` to stop presenting `AGENTS.md` as
  the human starting point
- align the documentation update protocol so `PROJECT_GUIDE.md` is updated when
  needed after issue work
- preserve `AGENTS.md` as the agent-specific operational entry point

## Original Plan

1. understand the existing documentation structure and reading order
2. create `PROJECT_GUIDE.md` as the human project entry point
3. update top-level onboarding documents to reference the new guide
4. update the context index and documentation conventions to distinguish human
   and agent entry points
5. extend post-issue update rules so `PROJECT_GUIDE.md` is maintained when the
   human-facing documentation map or repository orientation changes
6. record the documentation maintenance change in a dedicated hotfix file

## Adjustments Made During Implementation

The change remained documentation-only, but the scope was expanded slightly to
keep the repository cross-links internally consistent. In addition to the
top-level files requested, the context index, documentation conventions, and
agent guide were updated so the new human entry point became part of the
documented repository workflow rather than only a README-level redirect.

## Implementation Performed

### New Human Entry Point

File added:

- `PROJECT_GUIDE.md`

Content added:

- project purpose and current technical scope
- recommended reading order for humans
- repository rules and conventions relevant to contributors
- documentation map
- canonical source artifact overview
- resume-work guidance

### Documentation Links Updated

Files updated:

- `README.md`
- `CONTRIBUTING.md`
- `AGENTS.md`
- `docs/context/project_context_index.md`
- `docs/documentation/documentation_conventions.md`
- `docs/documentation/agents_content_migration_map.md`

Linking changes applied:

- `README.md` now directs human readers to `PROJECT_GUIDE.md`
- `CONTRIBUTING.md` now starts contributor reading order from
  `PROJECT_GUIDE.md`
- `docs/context/project_context_index.md` now distinguishes human and agent
  reading orders
- `AGENTS.md` now references `PROJECT_GUIDE.md` as the human counterpart to the
  agent entry point

### Documentation Update Protocol Aligned

The post-issue documentation rules now explicitly state that
`PROJECT_GUIDE.md` should be updated when any of the following change:

- the human-facing project entry guidance
- the documentation map
- the contributor reading order
- the repository orientation presented to human readers

## Verification

The change was verified by reviewing the updated documentation chain and
confirming that:

- humans are no longer directed to `AGENTS.md` from `README.md` or
  `CONTRIBUTING.md`
- the context index contains separate reading orders for humans and agents
- the documentation conventions and post-issue update rules mention
  `PROJECT_GUIDE.md`
- the new human entry point is linked from the main repository guidance

## Findings

- The original issue-oriented documentation model already contained most of the
  underlying information needed by human readers; the main problem was the lack
  of a dedicated root-level human entry point
- The maintenance rule mattered as much as the new document itself, because
  without it the new guide would quickly drift away from the rest of the
  persistent documentation

## Known Limitations

- This hotfix does not rewrite all historical references to `AGENTS.md` in
  archival or migration documents when those references are still accurate in
  context
- `AGENTS.md` remains part of the repository documentation surface for agents,
  so future maintenance must continue to keep both entry points aligned when the
  document map changes

## Impact On Future Issues

- Future documentation work can assume a clear split between the human entry
  point (`PROJECT_GUIDE.md`) and the agent entry point (`AGENTS.md`)
- Issue completion work should now evaluate whether changes affect the human
  project orientation and therefore require updating `PROJECT_GUIDE.md`
- Issue `#17` can build on this split when documenting the final workflow and
  repository guidance

## Status

- Status: completed and verified
