# AGENTS Content Migration Map

## Purpose

This document records where the former long-form content of `AGENTS.md` was
moved during the documentation migration. It exists so future sessions can
trace the new canonical location of every major topic without reconstructing
that mapping manually.

## Migration Map

| Former AGENTS section | New canonical location |
| --- | --- |
| Project Overview | `README.md` |
| Development Setup | `docs/development/setup.md` |
| Build/Test/Lint Commands | `docs/development/setup.md` |
| Code Style Guidelines | `docs/development/code_style.md` |
| Domain-Specific Guidelines | `docs/development/code_style.md` and `docs/pipeline/cvn_pydantic_generation_pipeline.md` |
| Academic Project Conventions | `docs/development/code_style.md` and `docs/documentation/documentation_conventions.md` |
| Canonical CVN Package Anatomy | `docs/pipeline/cvn_pydantic_generation_pipeline.md` |
| Observed Relationships Between Files | `docs/pipeline/cvn_pydantic_generation_pipeline.md` |
| Observed Structural Characteristics | `docs/pipeline/cvn_pydantic_generation_pipeline.md` |
| Observed Metadata Coverage | `docs/pipeline/cvn_pydantic_generation_pipeline.md` |
| Observed Reference-Table Situation | `docs/pipeline/cvn_pydantic_generation_pipeline.md` |
| Issue #8 epic description | `docs/roadmap/cvn_generation_roadmap.md` and `docs/roadmap/issues/issue-08-epic-cvn-automation.md` |
| Issue #11 detail | `docs/roadmap/issues/issue-11-project-infrastructure.md` |
| Issue #12 detail | `docs/roadmap/issues/issue-12-structural-bindings.md` |
| Issues #13-#17 detail | `docs/roadmap/issues/issue-13-normalization.md` through `issue-17-workflow-documentation.md` |
| Agent-specific operational rules | `AGENTS.md` |

## Resulting Rule

`AGENTS.md` is no longer the repository knowledge base. It is now the agent
entry point that points to the canonical documents above.
