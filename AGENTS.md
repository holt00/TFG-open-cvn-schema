# AGENTS.md - Development Guidelines for TFG Open CVN Schema

## Project Overview

This is an academic TFG (Trabajo de Fin de Grado) project focused on creating an open schema and tools for processing academic CVs in Spanish universities. The project aims to develop a JSON-based format that's compatible with existing CVN standards while providing modern tooling for validation, export, and intelligent migration.

**Tech Stack:**
- Python 3.14 (required)
- uv (package manager)
- Pydantic (data validation)
- MongoDB (planned for data storage)
- LaTeX (documentation and export)
- OpenAI/Groq (AI-powered migration tools)

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

### Type Hints (Mandatory for Public APIs)
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

---

## Notes for Agents

- **Current Phase**: This is a research project in planning stage
- **Missing Configurations**: Ruff, testing framework, and build tools need setup
- **Academic Context**: Prioritize documentation and standards compliance
- **Spanish Focus**: Consider Spanish academic system requirements
- **Future Implementation**: Structure assumes `/src` directory for main code

**Last Updated**: February 2026 - Phase: Planning and Research