from pathlib import Path

import pytest

from cvn_codegen.auxiliary_sources.bundle import build_auxiliary_source_bundle
from cvn_codegen.normalization import build_normalization_result


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def canonical_package_dir(repo_root: Path) -> Path:
    return repo_root / "docs" / "CvnXML_v1.4.3_2.1_17012025"


@pytest.fixture(scope="session")
def canonical_xml_dir(canonical_package_dir: Path) -> Path:
    return canonical_package_dir / "XML"


@pytest.fixture(scope="session")
def canonical_xsd_dir(canonical_package_dir: Path) -> Path:
    return canonical_package_dir / "XSD"


@pytest.fixture(scope="session")
def canonical_paths(canonical_xml_dir: Path, canonical_xsd_dir: Path) -> dict[str, Path]:
    return {
        "specification_manual": canonical_xml_dir / "SpecificationManual.xml",
        "tree_model": canonical_xml_dir / "CVNTreeModel.xml",
        "reference_tables": canonical_xml_dir / "ReferenceTables.xml",
        "subtypes": canonical_xml_dir / "Subtype_Spa.xml",
        "entity": canonical_xml_dir / "Entity.xml",
        "thesaurus": canonical_xml_dir / "Thesaurus.xml",
        "cvn_xsd": canonical_xsd_dir / "CVN.xsd",
        "common_xsd": canonical_xsd_dir / "Common.xsd",
    }


@pytest.fixture(scope="session")
def canonical_auxiliary_bundle(canonical_paths: dict[str, Path]):
    return build_auxiliary_source_bundle(
        reference_tables_path=canonical_paths["reference_tables"],
        subtypes_path=canonical_paths["subtypes"],
        entity_path=canonical_paths["entity"],
        thesaurus_path=canonical_paths["thesaurus"],
    )


@pytest.fixture(scope="session")
def canonical_normalization_result(canonical_paths: dict[str, Path]):
    return build_normalization_result(
        specification_manual_path=canonical_paths["specification_manual"],
        tree_model_path=canonical_paths["tree_model"],
        reference_tables_path=canonical_paths["reference_tables"],
        subtypes_path=canonical_paths["subtypes"],
        entity_path=canonical_paths["entity"],
        thesaurus_path=canonical_paths["thesaurus"],
        cvn_xsd_path=canonical_paths["cvn_xsd"],
        common_xsd_path=canonical_paths["common_xsd"],
    )


@pytest.fixture
def domain_generation_output_dir(tmp_path: Path) -> Path:
    return tmp_path / "generated_domain"
