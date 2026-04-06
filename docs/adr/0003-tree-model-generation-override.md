# ADR 0003 - Tree Model Generation Override

## Status

- Accepted

## Context

`CVNTreeModel_v1.0.xsd` triggered circular dependency failures under the default
xsdata generation strategy used for the other structural packages.

## Decision

Apply a target-specific xsdata override for `tree_model` generation through the
runner instead of changing the global xsdata config for every target.

Current override:

- `--unnest-classes`

## Consequences

- `tree_model` can be generated without breaking the successful configuration
  used for `cvn` and `specification_manual`
- the override must remain documented because it is target-specific and not a
  general generation policy
- the resulting names may be less ergonomic, but the structural layer remains
  importable and usable
