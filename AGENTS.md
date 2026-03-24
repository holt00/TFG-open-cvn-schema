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

### Canonical CVN Package Anatomy

The canonical source package contains the following relevant artifacts:

```text
docs/CvnXML_v1.4.3_2.1_17012025/
|- XML/
|  |- SpecificationManual.xml
|  `- CVNTreeModel.xml
`- XSD/
   |- CVN.xsd
   |- Common.xsd
   |- AuxTable.xsd
   |- ISOUtilities.xsd
   |- SpecificationManual.xsd
   `- CVNTreeModel_v1.0.xsd
```

Agents should understand these files as three different layers rather than one single schema:

1. **Final CVN XML structure**
   - `XSD/CVN.xsd` defines the XML exchanged by CVN systems
   - It declares the root element `CVN` and the main blocks `Version`, `Agent`, and repeated `CvnItem`

2. **Reusable technical types and controlled values**
   - `XSD/Common.xsd` defines common wrappers such as `CVN_string`, `CVN_date`, `CVN_ISO_639`, `CVN_ISO_3166`, and flexible date patterns
   - `XSD/AuxTable.xsd` defines auxiliary controlled value sets used by CVN
   - `XSD/ISOUtilities.xsd` provides ISO code tables reused by the rest of the schemas

3. **Functional and technical metadata used to derive a domain model**
   - `XML/SpecificationManual.xml` is the functional manual in XML form
   - `XML/CVNTreeModel.xml` maps functional CVN codes to the technical XML structure
   - `XSD/SpecificationManual.xsd` validates the manual XML
   - `XSD/CVNTreeModel_v1.0.xsd` validates the tree-model XML

### Observed Relationships Between Files

Agents should rely on the following concrete relationships observed in the package:

- `XSD/CVN.xsd` includes `Common.xsd` and `AuxTable.xsd`
- `XSD/Common.xsd` includes `ISOUtilities.xsd`
- `XSD/SpecificationManual.xsd` imports the CVN namespace from `ISOUtilities.xsd` to type language codes
- `XSD/CVNTreeModel_v1.0.xsd` is independent from the CVN XSD namespace and defines its own namespace `http://cv.normalizado.org/CVNTreeModel`
- `XML/SpecificationManual.xml` is validated by `XSD/SpecificationManual.xsd`
- `XML/CVNTreeModel.xml` is validated by `XSD/CVNTreeModel_v1.0.xsd`
- `XML/CVNTreeModel.xml` is the bridge between the functional `code` values from the manual and the XML elements from `CVN.xsd`

The conceptual relationship is:

```text
SpecificationManual.xml
  -> functional meaning of CVN codes

CVNTreeModel.xml
  -> technical mapping of those codes into XML nodes/properties/indicators

CVN.xsd + Common.xsd + AuxTable.xsd + ISOUtilities.xsd
  -> valid XML shape and controlled value types
```

### Observed Structural Characteristics

The analysis of the package shows a few facts that should drive implementation decisions:

- `CVN.xsd` is the largest technical schema and contains 74 `complexType`, 232 `element`, 125 `attribute`, and 3 `choice`
- `Common.xsd` contains 11 `complexType` and 1 `choice`
- `AuxTable.xsd` is almost entirely enumerations, with 33 `simpleType`
- `ISOUtilities.xsd` contributes very large enums, including `ISO_639` with 428 values and `ISO_3166` with 312 values
- No `xs:any`, `xs:union`, `xs:list`, or mixed content were detected in the analyzed XSD files
- The main structural complications are repeated wrappers, `choice` constructs, recursion, and very large enumerations

Important examples agents should remember:

- `XSD/CVN.xsd` contains recursive structure through `Link -> CvnItemType`
- Several CVN wrappers follow the pattern `Item` + metadata attributes (`code`, `obligatory`, `multiplicity`, `attribute`)
- `OfficialIdType`, `EntityTypeType`, `EntityNameType`, and `FlexibleDatesType` use `choice`
- `XML/SpecificationManual.xml` uses a namespace on the root and empties it for descendants with `xmlns=""`, which is a parsing detail agents must not ignore

### Observed Metadata Coverage

Agents should take the following numbers as the working baseline for planning:

- `XML/SpecificationManual.xml` contains 1456 `Item` elements and 1456 unique `code` attributes
- `XML/CVNTreeModel.xml` contains 101 `CVNItem` nodes, 939 `Property` nodes, and 4635 `Indicator` nodes
- `XML/CVNTreeModel.xml` exposes 1430 unique code attributes
- Overlap between manual codes and tree-model codes is 1429
- There are 27 codes present in the manual but not found in the tree model
- There is 1 code present in the tree model but not found in the manual: `030.010.000.250`

This means the metadata layers are highly aligned and suitable for automated cross-referencing, but not perfectly complete.

### Observed Reference-Table Situation

The functional manual references many controlled tables, but not all of them are fully present in the package:

- `SpecificationManual.xml` contains 557 `ReferenceTable` uses across 75 unique table names
- Many references are internal and can be tied to local XSD tables, such as `ISO_3166`, `ISO_639`, and CVN auxiliary tables
- Some important references are external or unresolved from the package alone, such as `ENTITY@Entity.xsd`, `THESAURUS@thesaurus.xsd`, and `UNESCO_CODES`

Agents must therefore separate:

- **internal controlled values** that can become local enums or typed aliases,
- **external or unresolved references** that should remain strings or externally documented placeholders until a later phase.

### Issue #8 - Epic: Automate CVN XML/XSD to Pydantic translation

**Goal**
- Establish the full roadmap for automatically translating CVN XML/XSD artifacts into Pydantic models with minimal manual intervention

**Agent expectations**
- Use this issue as the umbrella for planning and integration, not as the place for large undifferentiated implementation work
- Keep progress traceable through issues `#11` to `#17`
- Ensure each sub-issue closes with artifacts that are reusable by subsequent issues

**Specific context agents should carry through the epic**
- The package does not describe a single schema; it describes a structural XML layer plus two metadata layers
- Generating only from `XSD/CVN.xsd` is insufficient for the final domain model
- The intended end state is a two-step pipeline: structural bindings first, semantic/domain generation second
- External reference tables are a known limitation and should be made explicit early

**Integration checkpoints**
1. Generated structural models can be reproduced from the XSD package
2. Manual and tree-model metadata can be parsed and cross-indexed by `code`
3. Mapping rules exist for typing, naming, enums, multiplicity, and overrides
4. Domain models can be regenerated from normalized metadata
5. The full workflow is tested and documented

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
6. Ensure the initial layout can host both structural bindings and semantic model generation

**Recommended repository layout**

```text
src/
├── generated/
│   ├── cvn/
│   ├── specification_manual/
│   └── tree_model/
├── cvn_codegen/
│   ├── load_spec.py
│   ├── load_tree.py
│   ├── normalize.py
│   ├── mapping.py
│   └── emit_models.py
└── models/
    └── cvn/
```

**Dependency expectations**
- Include tooling for XSD/XML processing and generation, expected baseline being `xsdata` and `xsdata-pydantic`
- Use pinned versions to keep academic reproducibility
- If testing or linting is introduced here because it becomes necessary for the pipeline, document that explicitly

**Implementation notes**
- Keep generated output in a package isolated from hand-maintained modules because some generators format entire directories
- Prefer one obvious configuration file for generation rather than ad hoc CLI-only invocations
- Decide early whether generation scripts live under `src/cvn_codegen/` or a `scripts/` directory and keep it consistent

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
7. Keep the output separated by source concern: final CVN XML, specification manual, and tree model

**Observed schema facts to respect during generation**
- `CVN.xsd` depends on `Common.xsd` and `AuxTable.xsd`
- `Common.xsd` depends on `ISOUtilities.xsd`
- `SpecificationManual.xsd` imports the CVN namespace for `lang` typing
- The package contains very large enums and repeated wrapper patterns that may inflate generated code
- There are only a few `choice` constructs, so they should be handled explicitly rather than treated as a reason to avoid generation

**Operational steps agents should follow**
1. Generate bindings for the structural CVN schema rooted at `XSD/CVN.xsd`
2. Generate bindings for `SpecificationManual.xsd` so the manual XML can be parsed into typed objects
3. Generate bindings for `CVNTreeModel_v1.0.xsd` so the tree model can be traversed without raw XML parsing logic everywhere
4. Verify imports and package structure are stable after generation
5. Test at least one parsing flow for `SpecificationManual.xml` and one for `CVNTreeModel.xml`
6. Record exactly how the generator handled recursion, wrappers, anonymous types, and enums

**Known expected friction**
- Recursive `Link -> CvnItemType` references in `CVN.xsd`
- Wrapper-heavy types such as `CVN_string`, `CVN_date`, `CVN_ISO_639`, and similar constructs
- Potentially awkward names from anonymous inner types or `choice` branches
- Huge enum output for ISO and CVN auxiliary tables

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
7. Preserve enough source traceability to recover where each normalized field came from

**Observed source-specific details agents must encode**
- `SpecificationManual.xml` contains 1456 unique functional items and should be treated as the source of meaning, labels, multiplicity, obligatory flags, and reference tables
- `CVNTreeModel.xml` contains the structural bridge from those functional codes into XML paths through `CVNItem`, `Property`, `Indicator`, `Child`, and optional `Value`
- The tree model includes repeated code references, not only one code per item, so normalization must keep both a per-code view and a per-path view
- There is one observed code mismatch in the tree model (`030.010.000.250`) and there are manual codes absent from the tree model; these are not reasons to abort normalization but must be reported

**Normalization guidance**
- Build a manual index keyed by `code`
- Build a tree-model index keyed by `code`
- Build a path-oriented view that captures at least `cvn_item_code`, `property_name`, `indicator_name`, `value`, and the technical XML path
- Normalize multilingual names in a predictable way without discarding the original language entries
- Preserve raw codes and source references in the normalized layer for later traceability

**Suggested normalized fields**
- `code`
- `manual_name`
- `manual_short_name`
- `manual_type`
- `manual_obligatory`
- `manual_multiplicity`
- `manual_reference_table`
- `tree_cvn_item_code`
- `tree_property_name`
- `tree_indicator_name`
- `tree_value`
- `xml_path`
- `source_file`

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
7. Align the rules with the actual characteristics observed in the package, not with abstract assumptions

**Observed constraints that must shape the rules**
- Many structural XSD types are technical wrappers and should not automatically become first-class domain concepts
- Internal controlled tables are available locally in `AuxTable.xsd` and `ISOUtilities.xsd`, but some functional reference tables are external and cannot be strongly typed from the package alone
- `choice` appears in a few important places, including IDs, flexible dates, and entity-related wrappers
- Repeated wrapper attributes such as `code`, `obligatory`, `multiplicity`, and `attribute` belong to the XML interoperability layer and should not automatically pollute the domain model

**Minimum decisions this issue must finalize**
1. Which XSD wrappers collapse to primitives in the domain layer
2. Which controlled sets become Python enums and which remain string-like values
3. How multilingual manual names affect generated class and field naming
4. How to represent CVN multiplicity as optional values vs `list[T]`
5. How to handle external reference tables such as `ENTITY@Entity.xsd`, `THESAURUS@thesaurus.xsd`, and `UNESCO_CODES`
6. How to register code-specific exceptions without baking them directly into the generic algorithm

**Recommended rule style**
- Prefer a small number of broad mapping rules
- Keep overrides in a dedicated data file or module
- Preserve CVN code traceability in the generated artifacts even when names become more human-readable
- Favor stable naming over literal XML naming when the two conflict

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
6. Make regeneration deterministic and repeatable from committed inputs

**How the generator should be conceived**
- It should not emit classes directly from raw XSD alone
- It should consume the normalized metadata layer from issue `#13`
- It should apply mapping rules and overrides from issue `#14`
- It should emit readable domain models that are distinct from the structural XML bindings

**Concrete implementation guidance**
1. Traverse the tree-model hierarchy to identify logical groups anchored in `CVNItem`
2. Resolve each referenced `code` back to manual metadata
3. Infer target field names and target Python/Pydantic types from the mapping rules
4. Detect and factor repeated domain structures such as identification, contact, dates, entities, and locations
5. Emit source traceability, for example through metadata, docstrings, or constants bound to CVN codes
6. Keep output idempotent so repeated runs do not create noisy diffs

**Recommended first generation scope based on the observed package**
- the `Version` / `Agent` identification area
- personal identification and contact information
- simple date and wrapper conversions
- a small but representative subset of `CVNItem` blocks that exercise multiplicity, nested indicators, and controlled tables

**Things not to overfit in the first implementation**
- full support for every external reference table
- complete beautification of every generated class name before the mapping rules stabilize
- broad manual post-processing of emitted code

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
7. Cover the mismatches and special cases discovered during source analysis

**Tests should reflect observed package realities**
- the parser must handle the namespace behavior of `SpecificationManual.xml`
- the normalization layer must tolerate repeated code references in the tree model
- the overlap report should verify the expected presence of unmatched codes instead of assuming perfect parity
- the pipeline should include assertions for known external reference-table limitations

**Minimum recommended coverage**
1. Structural parsing smoke tests for generated bindings
2. Normalization tests using real XML inputs from the CVN package
3. Regression tests for `choice`-related mappings and recursive references where relevant
4. Tests for enum-vs-string decisions, especially around internal vs external reference tables
5. End-to-end generation test producing importable domain models from the canonical package

**Quality principles**
- Prefer deterministic assertions over snapshots of huge generated files
- Add focused regression tests when a code-specific edge case is discovered
- Keep fixtures as close as possible to the official package rather than hand-crafted approximations

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
6. Capture the actual relationships between the analyzed CVN files so future contributors do not need to rediscover them

**Documentation must include**
- the role of each XML and XSD file in `docs/CvnXML_v1.4.3_2.1_17012025`
- how `CVN.xsd`, `Common.xsd`, `AuxTable.xsd`, and `ISOUtilities.xsd` connect technically
- how `SpecificationManual.xml` and `CVNTreeModel.xml` complement the XSDs semantically
- which parts of the package are complete and which depend on external reference tables
- what is generated automatically, what is normalized, and what remains manually curated

**Automation expectations**
- One obvious command or small set of commands should regenerate the structural bindings, normalized metadata, and domain models
- The workflow should be safe to rerun on a clean checkout
- The workflow should explain where outputs land and which files are authoritative inputs

**Recommended final workflow narrative**
1. Install or sync dependencies
2. Generate structural bindings from XSD
3. Parse and normalize manual + tree-model XML
4. Apply semantic mapping rules and overrides
5. Emit domain models
6. Run tests validating the pipeline

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
