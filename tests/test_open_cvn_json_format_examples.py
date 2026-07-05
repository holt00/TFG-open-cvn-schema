import json

from pathlib import Path


EXAMPLES_DIR = Path("examples/open_cvn")
REQUIRED_CURRICULUM_SECTIONS = {
    "identity",
    "education",
    "research",
    "professional_experience",
    "achievements",
    "other",
}


def load_examples() -> list[tuple[Path, dict]]:
    examples = []
    for path in sorted(EXAMPLES_DIR.glob("*.json")):
        examples.append((path, json.loads(path.read_text(encoding="utf-8"))))
    return examples


def test_open_cvn_examples_exist():
    assert {path.name for path, _example in load_examples()} == {
        "controlled_references.json",
        "education_entry.json",
        "identity.json",
        "minimal.json",
        "research_entry.json",
        "trace_and_extensions.json",
    }


def test_open_cvn_examples_use_canonical_root_shape():
    for path, example in load_examples():
        assert example["schema_version"] == "0.1.0", path
        assert set(example) <= {"schema_version", "metadata", "curriculum", "extensions"}, path
        assert "metadata" in example, path
        assert "curriculum" in example, path
        assert example["metadata"]["policy"]["name"] == "default_cvn_semantic_policy", path
        assert example["metadata"]["policy"]["version"] == "0.1.0", path


def test_open_cvn_examples_include_expected_curriculum_sections():
    for path, example in load_examples():
        curriculum = example["curriculum"]
        assert REQUIRED_CURRICULUM_SECTIONS <= set(curriculum), path
        assert isinstance(curriculum["identity"], dict), path
        for section in REQUIRED_CURRICULUM_SECTIONS - {"identity"}:
            assert isinstance(curriculum[section], list), (path, section)


def test_open_cvn_examples_use_canonical_repeated_entry_shape():
    for path, example in load_examples():
        for section_name, entries in example["curriculum"].items():
            if section_name == "identity":
                continue
            for entry in entries:
                assert "type" in entry, (path, section_name)
                assert "data" in entry, (path, section_name)
                assert set(entry) <= {"id", "type", "data", "trace", "extensions"}, (
                    path,
                    section_name,
                )


def test_controlled_reference_example_records_open_and_unresolved_references():
    example = json.loads(
        (EXAMPLES_DIR / "controlled_references.json").read_text(encoding="utf-8")
    )

    identity = example["curriculum"]["identity"]
    agency = example["curriculum"]["research"][0]["data"]["agency"]

    assert identity["sex"]["source"] == "CVN_SEX_A"
    assert identity["entity_type"]["source"] == "CVN_ENTITY_TYPE"
    assert agency["source"] == "CVN_AGENCY_C"
    assert agency["reference_status"] == "unresolved"
