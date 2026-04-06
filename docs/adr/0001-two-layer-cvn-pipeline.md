# ADR 0001 - Two-Layer CVN Pipeline

## Status

- Accepted

## Context

The official CVN package contains both structural XML definitions and metadata
required for a higher-level domain model. Generating a final usable domain model
directly from `CVN.xsd` would conflate interoperability concerns with semantic
modeling.

## Decision

Use a two-layer pipeline:

1. structural Pydantic bindings generated from official XSDs
2. semantic and domain generation built from normalized metadata and explicit
   mapping rules

## Consequences

- `src/generated/` remains a fidelity layer
- ergonomic cleanup is deferred to later issues
- limitations in the structural layer are documented, not hidden
