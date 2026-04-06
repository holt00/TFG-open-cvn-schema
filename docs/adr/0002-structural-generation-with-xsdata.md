# ADR 0002 - Structural Generation With xsdata

## Status

- Accepted

## Context

The project needs reproducible structural bindings from the official CVN XSD
package, including imported and included schemas and large enumerations.

## Decision

- use `xsdata[cli,lxml]` for structural generation
- use `xsdata-pydantic` as the Pydantic backend
- keep a shared generation config at `config/.xsdata.xml`
- execute generation through a repository runner in `src/cvn_codegen/`

## Consequences

- generated bindings are reproducible from source XSDs
- the project depends on the xsdata generation model and its known limitations
- generation behavior is centralized and testable
