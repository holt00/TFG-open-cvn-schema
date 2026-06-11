# Project Documentation, Typing, Logging, And Generation Contracts

## Purpose

This project uses persistent repository documentation as the source of truth. Chat
history, issue comments, and temporary agent context must not be required to
understand the current state of the project.

All implementation work must keep code, generated artifacts, roadmap state,
limitations, and documentation synchronized in the same session.

## Mandatory Reading Contract

Before making changes, read the project entry documents in this order:

1. `AGENTS.md`
2. `PROJECT_GUIDE.md`
3. `docs/context/project_context_index.md`
4. `docs/context/current_status.md`
5. The relevant issue document under `docs/roadmap/issues/`

Human contributors may start from `README.md` and `PROJECT_GUIDE.md`, but
implementation work must still use the persistent context files.

## Documentation Source Of Truth Contract

Repository documentation is versioned and authoritative.

Required entry files:

- `README.md`: high-level repository overview
- `PROJECT_GUIDE.md`: human-oriented project entry point and documentation map
- `AGENTS.md`: operational rules and document map for agents
- `CONTRIBUTING.md`: contributor onboarding and update obligations

Required persistent context files:

- `docs/context/project_context_index.md`: documentation index and reading map
- `docs/context/current_status.md`: current implementation state and next steps

Required architecture files:

- `docs/pipeline/cvn_pydantic_generation_pipeline.md`: generation pipeline
  architecture
- `docs/pipeline/known_limitations.md`: structural, source, and process
  limitations
- `docs/adr/`: architecture decision records

Required roadmap files:

- `docs/roadmap/cvn_generation_roadmap.md`: roadmap overview
- `docs/roadmap/issues/*.md`: per-issue execution records
- `docs/roadmap/hotfixes/*.md`: maintenance and corrective records

## Documentation Update Contract

Every issue or implementation change must update documentation in the same
session.

At minimum, update:

1. The relevant issue document under `docs/roadmap/issues/`
2. `docs/context/current_status.md`
3. `docs/pipeline/known_limitations.md` if a new limitation was discovered
4. `docs/roadmap/cvn_generation_roadmap.md` if roadmap state changed
5. `PROJECT_GUIDE.md` if the human-facing entry guidance, document map,
   contributor reading order, or repository orientation changed

Update `AGENTS.md` only when:

- the document map changes
- the mandatory reading order changes
- operational rules for agents change

## Issue Documentation Contract

Every issue document must include these sections:

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

Issue documents must record the original plan and the final implemented path. Any
deviation from the original plan must be documented with the reason.

## Documentation Writing Contract

Documentation must be stable, concrete, and reconstructable.

Rules:

- Prefer repository documents over chat history as the source of truth
- Record both decisions and implementation outcomes
- Explain why deviations happened
- Reference concrete files, commands, and outputs
- Document limitations explicitly instead of hiding them
- Keep setup and tooling docs aligned with dependency-group decisions
- Keep runtime dependencies separate from non-runtime tooling
- Cross-link issue files to supporting architecture and limitation documents
- Keep limitation entries tied to the future issues expected to address them

## Python Typing Contract

Python code should use type hints whenever reasonably possible.

Rules:

- Use explicit return types for public functions
- Use concrete types when the contract is stable
- Keep generated structural types separate from hand-maintained semantic/domain
  types
- Preserve source traceability in generated and normalized structures
- Prefer typed data structures for public pipeline outputs
- Do not weaken stable contracts with overly broad types unless required by
  generated code or source ambiguity

## Python Documentation Contract

Repository Python code must use concise English docstrings.

Rules:

- Use Google-style docstrings for public functions and classes
- Use sections such as `Args:`, `Returns:`, and `Raises:` when applicable
- Keep comments rare
- Add comments only for non-obvious logic
- Document references to external standards when relevant

## Logging Contract

Repository code must use `logging` for operational output.

Rules:

- Use `logging` for progress reporting, operational messages, and controlled
  errors
- Reserve `print` for direct console interactions, shell snippets, or explicit
  user-facing terminal examples
- Define module loggers with `logging.getLogger(__name__)`
- Use `logger.info(...)` for normal progress
- Use `logger.error(...)` for controlled failures
- Use `logger.exception(...)` when a traceback should be recorded
- CLI entry points may configure a local baseline such as
  `logging.basicConfig(level=logging.INFO)`
- Do not use old `%`-style string formatting in repository code
- Use f-strings for interpolated strings

## Generated Code Contract

Generated code is an interoperability layer, not the place for manual cleanup.

Rules:

- Do not edit `src/generated/` manually
- Regenerate generated artifacts from canonical source inputs instead
- Keep hand-maintained generation and pipeline logic in `src/cvn_codegen/`
- Keep semantic or domain-facing models outside `src/generated/`
- Structural generated code should favor fidelity to the source artifacts over
  ergonomics
- Semantic cleanup, overrides, normalization, and domain generation must live
  outside generated output
- Generated output must be reproducible from documented commands and
  configuration

## Generation Pipeline Contract

The generation workflow must be explicit, reproducible, and documented.

Rules:

- Treat the documented source package as canonical input
- Keep generation configuration versioned, for example under `config/`
- Run generation through a standard runner instead of ad hoc commands
- The runner should validate prerequisites, clean target output directories,
  execute generation, and verify generated output
- Target-specific generation overrides must be documented with their reason
- Generation commands must be listed in setup or workflow documentation
- Parse/import smoke checks should be documented when generated bindings are
  expected to load real source files

## Dependency And Tooling Contract

Use dependency groups to separate concerns.

Rules:

- Keep true runtime dependencies in `[project.dependencies]`
- Keep code-generation tooling in a dedicated dependency group
- Keep test-only tooling in a dedicated dependency group
- Create new dependency groups only when the tooling has a separate workflow or
  reproducibility need
- Document environment setup commands in `docs/development/setup.md` or
  equivalent
- Keep CI commands aligned with local commands

## Testing And Verification Contract

Implementation work must be verifiable.

Rules:

- Automated tests must live under `tests/`
- The standard test entry point must remain documented
- CI should run the same documented test entry point used locally
- Issue documents must record the verification performed
- Generated artifacts should have import checks, runner tests, and smoke checks
  when applicable
- Known failures caused by source-package inconsistencies must be documented as
  limitations, not hidden as broken tests

## Known Limitations Contract

Limitations are first-class project knowledge.

Rules:

- Record limitations in `docs/pipeline/known_limitations.md`
- Include the affected area, impact, and expected follow-up
- Distinguish source-package inconsistencies from implementation bugs
- Do not silently patch generated or canonical-source inconsistencies without
  documenting the policy
- Future issues must read the limitation register before changing related code

## Naming And Style Contract

Python naming rules:

- variables and functions: `snake_case`
- classes: `PascalCase`
- constants: `UPPER_SNAKE_CASE`
- modules and file names: `snake_case.py`

Import order:

1. standard library
2. third-party dependencies
3. local project imports

String formatting:

- Use f-strings
- Do not use old `%`-style formatting

## Architecture Boundary Contract

Keep project layers separate.

Rules:

- Canonical source artifacts are inputs
- Generated structural bindings are reproducible outputs
- Hand-maintained pipeline logic lives outside generated code
- Normalization and semantic mapping live outside generated code
- Domain-facing models live outside structural bindings
- Architecture decisions and known tradeoffs must be documented persistently
