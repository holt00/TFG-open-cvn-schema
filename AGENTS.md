# AGENTS.md - Development Guidelines for TFG Open CVN Schema

## Project Overview

This is an academic TFG (Trabajo de Fin de Grado) project focused on creating an open schema and tools for processing academic CVs in Spanish universities. The project aims to develop a JSON-based format that's compatible with existing CVN standards while providing modern tooling for validation, export, and intelligent migration.

**Tech Stack:**
- Python 3.14 (required)
- uv (package manager)
- Pydantic (data validation)
- MongoDB (planned for data storage)
- LaTeX (documentation and export)
- AI API (TBD) para herramientas de migración inteligente

**Current Status:** Research and planning phase - implementation not yet started.

## Development Setup

### Prerequisites
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify Python 3.14 availability
uv python list
```

### Environment Setup
```bash
# Create project with Python 3.14
uv python pin 3.14

# Create virtual environment
uv venv

# Activate environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies (when available)
uv sync
```

### Managing Dependencies
```bash
# Add new dependency
uv add <package-name>

# Add development dependency
uv add --dev <package-name>

# Install from requirements.txt
uv pip install -r requirements.txt
```

## Build/Test/Lint Commands

### Running Code
```bash
# Run Python scripts
uv run python src/main.py

# Run module
uv run -m your_module

# Run with specific Python version
uv run --python 3.14 python script.py
```

### Testing (To be configured)
```bash
# Testing framework TBD - placeholder commands:
# uv run pytest                    # Run all tests
# uv run pytest tests/test_*.py    # Run specific tests
# uv run pytest -v                 # Verbose output
# uv run pytest --cov             # Coverage report

# Note: Testing framework selection pending - will update when decided
```

### Code Quality (Ruff - Not Yet Implemented)
```bash
# Ruff formatting and linting (requires setup)
# uv run ruff check .              # Lint all files
# uv run ruff check --fix .        # Auto-fix issues
# uv run ruff format .             # Format code

# Note: Ruff configuration needed in pyproject.toml
```

### Future Build Commands
```bash
# Package building (when ready)
# uv build

# Installation from source
# uv pip install -e .
```

## Code Style Guidelines

### Import Organization
```python
# Standard library imports
import json
import pathlib
from typing import Dict, List, Optional

# Third-party imports
import pydantic
from pydantic import BaseModel, Field

# Local application imports
from .models import ResearcherCV
from .validators import validate_orcid
```

### Naming Conventions
- **Variables/Functions**: `snake_case` (e.g., `researcher_name`, `validate_cv_data()`)
- **Classes**: `PascalCase` (e.g., `ResearcherCV`, `AcademicPublication`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_CV_VERSION`, `MAX_PUBLICATIONS`)
- **Private members**: Prefix with underscore `_private_method()`
- **Files/Modules**: `snake_case.py`

### Type Hints (Siempre que sea posible)
```python
from typing import Dict, List, Optional, Union
from datetime import datetime

def process_cv_data(cv_data: Dict[str, Any]) -> ResearcherCV:
    """Process raw CV data into validated model."""
    pass

class AcademicPublication(BaseModel):
    title: str
    authors: List[str]
    publication_date: datetime
    doi: Optional[str] = None
```

### Documentation Standards
```python
def validate_orcid_id(orcid: str) -> bool:
    """
    Validate ORCID identifier format.
    
    Args:
        orcid: ORCID identifier string (e.g., "0000-0000-0000-0000")
        
    Returns:
        bool: True if valid ORCID format, False otherwise
        
    References:
        ORCID identifier specification: https://orcid.org/
        
    Examples:
        >>> validate_orcid_id("0000-0002-1825-0097")
        True
    """
    pass
```

### Error Handling
```python
# Use specific exception types
from pydantic import ValidationError

try:
    cv = ResearcherCV.parse_obj(data)
except ValidationError as e:
    logger.error(f"CV validation failed: {e}")
    raise CVValidationError(f"Invalid CV data: {e}") from e

# Custom exceptions for domain-specific errors
class CVValidationError(Exception):
    """Raised when CV data fails validation."""
    pass
```

### File Organization
```
src/
├── __init__.py
├── models/          # Pydantic models for CV schema
├── validators/      # Custom validation logic
├── exporters/       # LaTeX and other format exporters
├── importers/       # CVN and legacy format parsers
└── utils/          # Common utilities
```

## Domain-Specific Guidelines

### Pydantic Models for CV Schema
```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date

class ResearcherCV(BaseModel):
    """Main CV model following CVN standards."""
    
    # Personal identification (aligned with ORCID)
    orcid_id: Optional[str] = Field(None, description="ORCID identifier")
    full_name: str = Field(..., description="Full researcher name")
    
    # Academic positions
    positions: List[AcademicPosition] = Field(default_factory=list)
    publications: List[Publication] = Field(default_factory=list)
    
    @validator('orcid_id')
    def validate_orcid_format(cls, v):
        """Ensure ORCID follows standard format."""
        if v and not validate_orcid_id(v):
            raise ValueError('Invalid ORCID format')
        return v
```

### CVN/Spanish Academic Standards
- Follow FECYT CVN field mappings for compatibility
- Use Spanish academic terminology where applicable
- Support hierarchical academic positions (Catedrático, Profesor Titular, etc.)
- Include Spanish research evaluation system fields (sexenios, quinquenios)

### Integration Standards
- **ORCID**: Use standard ORCID field names and validation
- **CERIF**: Align with European research information format when possible
- **JSON Schema**: Maintain valid JSON Schema for all models
- **Internationalization**: Support both Spanish and English field descriptions

### Data Validation Patterns
```python
# Academic year validation
def validate_academic_year(year: int) -> int:
    current_year = datetime.now().year
    if year < 1900 or year > current_year + 5:
        raise ValueError(f"Academic year must be between 1900 and {current_year + 5}")
    return year

# Spanish university validation
SPANISH_UNIVERSITIES = ["UCM", "UAM", "UPM", "UC3M", ...]  # Load from data
```

## Academic Project Conventions

### Research Documentation
- Include citations in docstrings for academic standards referenced
- Document decision rationale for schema design choices
- Maintain research notes in `/docs/research/` directory

### Version Control for Academic Work
- Use descriptive commit messages referencing research phases
- Tag important milestones (schema versions, validation implementations)
- Maintain clear branch naming for different research areas

### Reproducibility
- Pin exact dependency versions for research reproducibility
- Document Python version and uv version in README
- Include environment export commands for sharing setups

## Implementation Roadmap by Issue

This section defines the expected delivery order and execution criteria for the current implementation roadmap. Agents should use it as the default guide when working on issue-driven tasks related to CVN ingestion, code generation, and Pydantic modeling.

### General Execution Rules
- Follow the issue order strictly unless the user explicitly requests otherwise
- Keep generated code and manually maintained code clearly separated
- Prefer incremental deliveries that leave the repository in a reproducible state
- Document decisions that affect later issues, especially around naming, typing, enums, and external reference tables
- When an issue depends on another, do not shortcut the dependency by embedding unfinished work from future issues unless strictly necessary and documented
- Treat `docs/CvnXML_v1.4.3_2.1_17012025` as the canonical source package for this roadmap

### Issue #8 - Epic: Automate CVN XML/XSD to Pydantic translation

**Goal**
- Establish the full roadmap for automatically translating CVN XML/XSD artifacts into Pydantic models with minimal manual intervention

**Agent expectations**
- Use this issue as the umbrella for planning and integration, not as the place for large undifferentiated implementation work
- Keep progress traceable through issues `#11` to `#17`
- Ensure each sub-issue closes with artifacts that are reusable by subsequent issues

**Done when**
- The sub-issues are completed and their outputs integrate into a coherent, documented pipeline

### Issue #11 - Prepare project infrastructure for code generation

**Goal**
- Create the project foundation required for reproducible code generation and schema processing

**Required steps**
1. Add and pin the required dependencies in `pyproject.toml`
2. Create the initial `src/` layout separating generated artifacts from hand-written code
3. Add base configuration for `xsdata` and any required generation settings
4. Define where code generation scripts or modules should live
5. Document the rule that generated files are not edited manually

**Expected outputs**
- dependency setup
- initial package structure
- generator configuration
- documentation of repository conventions for generated code

**Notes for agents**
- Keep the structure conservative and easy to evolve
- Optimize for maintainability over premature abstraction

### Issue #12 - Generate structural Pydantic bindings from CVN XSDs

**Goal**
- Produce Pydantic bindings that mirror the official CVN XML schemas

**Required steps**
1. Generate models from `XSD/CVN.xsd`
2. Generate models from `XSD/SpecificationManual.xsd`
3. Generate models from `XSD/CVNTreeModel_v1.0.xsd`
4. Verify local `include` and `import` resolution works correctly
5. Confirm the generated modules can be imported and used for parsing
6. Record any structural limitations detected during generation

**Expected outputs**
- generated structural models under a dedicated package
- importable modules
- notes on problematic constructs such as `choice`, recursion, or very large enums

**Notes for agents**
- Do not manually beautify generated models beyond generation settings unless absolutely necessary
- Treat this layer as an interoperability layer, not the final domain model

### Issue #13 - Parse and normalize `SpecificationManual.xml` and `CVNTreeModel.xml`

**Goal**
- Build a normalized metadata layer that can be consumed by the domain-model generator

**Required steps**
1. Parse `XML/SpecificationManual.xml`
2. Parse `XML/CVNTreeModel.xml`
3. Build indexes keyed by CVN `code`
4. Extract technical XML paths from the tree model
5. Compare overlap and detect unresolved or mismatched codes
6. Expose the normalized result through reusable Python structures

**Expected outputs**
- normalized metadata objects or dictionaries
- code-based indexes
- overlap report between manual and tree model
- list of exceptions or unresolved references

**Notes for agents**
- Favor explicit normalized structures over loosely shaped dictionaries when possible
- Preserve traceability to source XML files and CVN codes

### Issue #14 - Define semantic mapping rules and override policy

**Goal**
- Establish deterministic rules for turning normalized CVN metadata into domain-oriented Pydantic models

**Required steps**
1. Define type-mapping rules from CVN metadata to Python/Pydantic types
2. Decide which auxiliary tables become enums and which remain strings
3. Define naming rules for generated classes, fields, and modules
4. Define how `choice`, wrapper patterns, and recursion are represented in domain models
5. Create a controlled override mechanism for exceptional cases
6. Document all decisions in a repo-tracked artifact

**Expected outputs**
- mapping specification
- override mechanism or override file format
- documented policy for external reference tables not included in the package

**Notes for agents**
- Keep overrides small and intentional
- Prefer general rules first, overrides second

### Issue #15 - Implement the domain Pydantic model generator

**Goal**
- Generate cleaner domain models from the normalized metadata and the semantic mapping rules

**Required steps**
1. Implement traversal of `CVNItem`, `Property`, and `Indicator` structures
2. Generate domain models for the first representative CVN blocks
3. Factor reusable structures such as identification, contact, entities, and dates when appropriate
4. Preserve traceability to CVN codes in emitted artifacts
5. Keep generated domain code separated from structural bindings

**Expected outputs**
- executable generator
- first set of generated domain Pydantic models
- reusable shared domain components

**Recommended first scope**
- identification
- contact
- basic personal data
- a small but representative subset of `CVNItem` blocks

**Notes for agents**
- Prioritize correctness and traceability before completeness
- Make regeneration idempotent whenever possible

### Issue #16 - Add automated tests for the generation pipeline

**Goal**
- Validate that the structural and semantic generation pipeline is reproducible and resistant to regressions

**Required steps**
1. Add test fixtures based on the CVN package XML files
2. Test parsing of manual and tree-model inputs
3. Test indexing and metadata normalization
4. Test semantic mapping and overrides
5. Test generated modules can be imported
6. Add at least one end-to-end pipeline test

**Expected outputs**
- test suite for critical pipeline stages
- smoke coverage for generation commands
- regression coverage for known special cases

**Notes for agents**
- Prefer small deterministic tests over brittle snapshot-heavy tests
- Add regression tests whenever a special mapping case is fixed

### Issue #17 - Document and automate the complete workflow

**Goal**
- Leave the repository with a clear and reproducible workflow for regenerating all CVN-related models

**Required steps**
1. Document the architecture: structural bindings vs semantic domain models
2. Document the generation workflow step by step
3. Document known limitations, especially external tables and unresolved references
4. Add a command, script, or documented entrypoint for regeneration
5. Update `README.md` and any technical documentation impacted by the work

**Expected outputs**
- updated developer documentation
- a single clear regeneration workflow
- explicit notes on assumptions and limitations

**Notes for agents**
- Documentation should be sufficient for another contributor to rerun the full pipeline without prior context
- Prefer one obvious workflow over several partially overlapping instructions

---

## Notes for Agents

- **Current Phase**: Transition from research/planning to early implementation of the CVN generation pipeline
- **Primary Roadmap**: Follow issue `#8` and sub-issues `#11` to `#17`
- **Missing Configurations**: Ruff, testing framework, and build tools may still require setup as part of the roadmap
- **Academic Context**: Prioritize documentation and standards compliance
- **Spanish Focus**: Consider Spanish academic system requirements
- **Future Implementation**: Structure assumes `/src` directory for main code and a clear separation between generated and hand-written modules

**Last Updated**: March 2026 - Phase: Early implementation roadmap defined
