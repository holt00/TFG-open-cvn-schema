# Code Style And Project Conventions

## Python Style

### Imports

Use this order:

1. standard library
2. third-party dependencies
3. local project imports

### Naming

- variables and functions: `snake_case`
- classes: `PascalCase`
- constants: `UPPER_SNAKE_CASE`
- modules and file names: `snake_case.py`

### Typing

- Use type hints whenever reasonably possible
- Prefer explicit return types for public functions
- Use concrete types where the contract is stable

### Documentation

- Use concise docstrings for public functions and classes
- Keep comments rare and only when the code is not self-explanatory
- Document references to external standards when relevant

### Error Handling

- Use specific exceptions where possible
- Wrap external tool failures with project-specific exceptions when needed

### Logging And Console Output

- Use `logging` for operational messages, progress reporting, and error
  reporting inside repository code
- Reserve `print` for direct console interactions, short shell examples, or
  explicit user-facing terminal snippets
- Define module loggers with `logging.getLogger(__name__)`
- Use the logging level that matches the situation: `info` for normal progress,
  `error` for controlled failures, and `exception` when a traceback should be
  recorded

### String Formatting

- Use f-strings for interpolated strings, for example
  `f"target '{target_name}' no reconocido"`
- Do not use old `%`-style string formatting in repository code

## Generated Code Boundaries

- `src/generated/` is generated code and must not be edited manually
- semantic cleanup, overrides, normalization, and domain generation belong
  outside `src/generated/`
- the structural layer favors fidelity over ergonomics

## Domain-Specific Conventions

- Preserve CVN code traceability throughout the pipeline
- Prefer Spanish academic terminology when mirroring source semantics
- Use ORCID, CERIF, and JSON-oriented naming consistently when introducing
  domain-facing models later in the roadmap

## Academic Project Conventions

- Keep architecture decisions documented
- Record limitations explicitly rather than hiding them
- Prioritize reproducibility over convenience for generation workflows
- Ensure future contributors can reconstruct the pipeline from repository docs
