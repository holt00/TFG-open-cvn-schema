# Documentation Conventions

## Purpose

This document defines how repository documentation is organized and how future
sessions must update it.

## Documentation Taxonomy

### Repository Entry Files

- `README.md`: human overview
- `AGENTS.md`: operational rules and document map for agents
- `CONTRIBUTING.md`: developer onboarding and update obligations

### Persistent Context

- `docs/context/project_context_index.md`: single documentation entry point
- `docs/context/current_status.md`: current implementation state

### Architecture

- `docs/pipeline/cvn_pydantic_generation_pipeline.md`: architecture of the
  generation workflow
- `docs/pipeline/known_limitations.md`: known structural and process limits
- `docs/adr/*.md`: architecture decisions with consequences

### Roadmap And Execution History

- `docs/roadmap/cvn_generation_roadmap.md`: roadmap across issues
- `docs/roadmap/issues/*.md`: per-issue history and implementation record

### Development Reference

- `docs/development/setup.md`: environment and commands
- `docs/development/code_style.md`: style and conventions

## Code Documentation Conventions

- Python docstrings in repository code should use Google-style sections such as
  `Args:`, `Returns:`, and `Raises:` when applicable
- Python docstrings should be written in English to keep the codebase
  internally consistent
- Comments in code should remain rare and should only explain non-obvious logic

## Mandatory Sections For Issue Documents

Every issue file under `docs/roadmap/issues/` must include these sections:

1. `Summary`
2. `Original Goal`
3. `Original Plan`
4. `Adjustments Made During Implementation`
5. `Implementation Performed`
6. `Verification`
7. `Findings`
8. `Known Limitations`
9. `Impact On Future Issues`
10. `Status`

## Mandatory Update Protocol After Each Issue

At the end of every issue session, update at minimum:

1. the issue file itself
2. `docs/context/current_status.md`
3. `docs/pipeline/known_limitations.md` when a new limitation appears
4. `docs/roadmap/cvn_generation_roadmap.md` when issue state changes

Update `AGENTS.md` only if:

- the document map changes,
- the mandatory reading order changes,
- or the operational rules for agents change.

## Writing Principles

- Prefer stable documents over chat history as the source of truth
- Record both the original plan and the final implemented path
- Explain why deviations happened
- Keep references to concrete files, commands, and outputs
- Document limitations explicitly, including their impact on later issues
- When documenting setup or tooling, reflect dependency-group decisions and keep
  runtime vs non-runtime dependencies clearly separated

## Naming Conventions

- roadmap overview: `docs/roadmap/cvn_generation_roadmap.md`
- issue files: `docs/roadmap/issues/issue-<number>-<slug>.md`
- ADRs: `docs/adr/000N-<slug>.md`
- context files: `docs/context/<name>.md`

## Cross-Linking Rules

- `AGENTS.md` must point to the context index
- the context index must point to current status, roadmap, issues, pipeline,
  and ADRs
- issue files must link to supporting architecture and limitation documents
- limitation entries should mention the future issues expected to address them
