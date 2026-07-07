# Issue 66 - Implement LaTeX Export From Open CVN

## Summary

Issue `#66` implements the MVP LaTeX export path from stored Open CVN curriculum
versions.

This issue is part of epic `#60`.

## Goal

- generate a structured LaTeX document from Open CVN JSON
- support master and derived curriculum versions
- prove the TFG export workflow without requiring a polished final template
- keep output deterministic for tests

## Template Direction

The MVP should use Jinja templates or a similarly simple rendering approach. The
first template should prioritize correctness and stable output over visual polish.

## Planned Scope

- create a LaTeX template directory
- render basic identity, education, research, professional experience,
  achievements, and other sections when present
- escape LaTeX-sensitive text values
- include trace metadata only when useful or behind an option
- output `.tex` files for master or derived versions
- provide deterministic rendering for tests

## Planned Steps

1. choose template dependency and add it if needed
2. define template file location
3. implement Open CVN-to-template context conversion
4. implement LaTeX escaping helpers
5. implement `.tex` export command
6. add deterministic rendering tests using example Open CVN JSON
7. document template limitations and customization points

## Expected Output

- LaTeX template file or files
- LaTeX rendering module
- CLI export command
- tests for deterministic `.tex` output
- documentation for LaTeX export

## Verification

- a valid stored curriculum renders to `.tex`
- derived version selection affects rendered output
- LaTeX escaping prevents obvious broken output for special characters
- full repository verification passes or a reason is documented

## Impact On Later Issues

- issue `#67` compiles `.tex` output into PDF when a local TeX engine exists

## Status

- Status: planned
