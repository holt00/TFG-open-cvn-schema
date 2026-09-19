import json
import random
from pathlib import Path

import pytest

from tfm_lakehouse.synthetic_cvn import SyntheticCvnConfig, generate_synthetic_cvn
from tfm_lakehouse.synthetic_cvn import seed as seed_module
from tfm_lakehouse.synthetic_cvn.exceptions import SyntheticCvnSeedError
from tfm_lakehouse.synthetic_cvn.seed import OrcidSeedPool, parse_orcid_summary
from tfm_lakehouse.synthetic_cvn.validation import validate_synthetic_document

_NAMESPACES = " ".join(
    f'xmlns:{prefix}="http://www.orcid.org/ns/{name}"'
    for prefix, name in (
        ("record", "record"),
        ("common", "common"),
        ("personal", "personal-details"),
        ("person", "person"),
        ("employment", "employment"),
        ("education", "education"),
        ("work", "work"),
        ("keyword", "keyword"),
        ("activities", "activities"),
    )
)
_BIOGRAPHY = "PRIVATE-BIOGRAPHY-TEXT"


def _orcid_id(number: int) -> str:
    digits = f"{number:015d}"
    total = 0
    for digit in digits:
        total = (total + int(digit)) * 2
    check_value = (12 - total % 11) % 11
    full = digits + ("X" if check_value == 10 else str(check_value))
    return "-".join(full[i : i + 4] for i in range(0, 16, 4))


def _affiliation(tag: str, org: str, role: str | None, start: str, end: str | None, country: str = "ES") -> str:
    end_xml = f"<common:end-date><common:year>{end}</common:year><common:month>06</common:month></common:end-date>" if end else ""
    role_xml = f"<common:role-title>{role}</common:role-title>" if role else ""
    return (
        f"<{tag}:{tag}-summary>{role_xml}"
        f"<common:start-date><common:year>{start}</common:year><common:month>09</common:month></common:start-date>"
        f"{end_xml}<common:organization><common:name>{org}</common:name>"
        f"<common:address><common:city>Madrid</common:city><common:country>{country}</common:country></common:address>"
        f"</common:organization></{tag}:{tag}-summary>"
    )


def _work(title: str, work_type: str, year: str, doi: str | None) -> str:
    doi_xml = (
        "<common:external-ids><common:external-id><common:external-id-type>doi</common:external-id-type>"
        f"<common:external-id-value>{doi}</common:external-id-value></common:external-id></common:external-ids>"
        if doi
        else ""
    )
    return (
        f"<work:work-summary><work:title><common:title>{title}</common:title></work:title>{doi_xml}"
        f"<work:type>{work_type}</work:type>"
        f"<common:publication-date><common:year>{year}</common:year><common:month>03</common:month></common:publication-date>"
        "</work:work-summary>"
    )


def _summary_xml(
    orcid_id: str,
    given: str | None = "Ana",
    family: str | None = "García López",
    *,
    rich: bool = True,
) -> str:
    given_xml = f"<personal:given-names>{given}</personal:given-names>" if given else ""
    family_xml = f"<personal:family-name>{family}</personal:family-name>" if family else ""
    activities = ""
    keywords = ""
    if rich:
        activities = (
            "<activities:activities-summary>"
            + _affiliation("employment", "Universidad de Ejemplo", "Profesora Titular", "2018", None)
            + _affiliation("employment", "Centro de Pruebas", "Investigadora", "2012", "2018")
            + _affiliation("education", "Universidad de Ejemplo", "Doctora en Informática", "2008", "2012")
            + _affiliation("education", "Universidad de Ejemplo", "Licenciada en Informática", "2003", "2008")
            + _work("Un artículo de ejemplo", "journal-article", "2020", "https://doi.org/10.1000/abc")
            + _work("Un capítulo de ejemplo", "book-chapter", "2019", None)
            + _work("Una ponencia de ejemplo", "conference-paper", "2018", None)
            + "</activities:activities-summary>"
        )
        keywords = "<keyword:keywords><keyword:keyword><keyword:content>datos abiertos</keyword:content></keyword:keyword></keyword:keywords>"
    return (
        f'<?xml version="1.0" encoding="UTF-8"?><record:record {_NAMESPACES}>'
        f"<common:orcid-identifier><common:path>{orcid_id}</common:path></common:orcid-identifier>"
        f"<person:person><person:name>{given_xml}{family_xml}</person:name>"
        f"<person:biography><personal:content>{_BIOGRAPHY}</personal:content></person:biography>{keywords}"
        f"</person:person>{activities}</record:record>"
    )


def _write_pool(root: Path, records: int, *, rich_every: int = 1) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for index in range(records):
        orcid_id = _orcid_id(1000 + index)
        bucket = root / f"{index % 3:03d}"
        bucket.mkdir(parents=True, exist_ok=True)
        path = bucket / f"{orcid_id}.xml"
        path.write_text(_summary_xml(orcid_id, rich=index % rich_every == 0), encoding="utf-8")
        paths[orcid_id] = path
    return paths


def _read_documents(output_dir: Path) -> list[dict]:
    return [
        json.loads(line)
        for shard in sorted(output_dir.glob("cvn_shard_*.jsonl"))
        for line in shard.read_text(encoding="utf-8").splitlines()
    ]


def _read_manifest(output_dir: Path) -> list[dict]:
    return [json.loads(line) for line in (output_dir / "manifest.jsonl").read_text(encoding="utf-8").splitlines()]


def _config(tmp_path: Path, **overrides) -> SyntheticCvnConfig:
    values = {
        "count": 20,
        "seed": 7,
        "orcid_seed_dir": tmp_path / "pool",
        "output_dir": tmp_path / "out",
        **overrides,
    }
    return SyntheticCvnConfig(**values)


def test_parse_orcid_summary_extracts_seed_fields_and_ignores_biography(tmp_path):
    orcid_id = _orcid_id(1)
    path = tmp_path / "seed.xml"
    path.write_text(_summary_xml(orcid_id), encoding="utf-8")

    seed = parse_orcid_summary(path)

    assert seed is not None
    assert (seed.orcid_id, seed.given_names, seed.family_name) == (orcid_id, "Ana", "García López")
    assert [a.kind for a in seed.affiliations] == ["employment", "employment", "education", "education"]
    assert seed.affiliations[0].end_year is None and seed.affiliations[1].end_year == "2018"
    assert [w.work_type for w in seed.works] == ["journal-article", "book-chapter", "conference-paper"]
    assert seed.works[0].doi == "https://doi.org/10.1000/abc"
    assert seed.keywords == ("datos abiertos",)
    assert _BIOGRAPHY not in repr(seed)


@pytest.mark.parametrize(
    "xml",
    [
        _summary_xml(_orcid_id(2), family=None),
        _summary_xml(_orcid_id(3), given=None),
        _summary_xml("0000-0000-0000-0000"),
        "<not-closed",
    ],
    ids=["no-family-name", "no-given-name", "bad-checksum", "malformed-xml"],
)
def test_parse_orcid_summary_returns_none_for_unusable_records(xml):
    assert parse_orcid_summary(xml.encode("utf-8")) is None


def test_seed_pool_rejects_missing_or_empty_directory(tmp_path):
    with pytest.raises(SyntheticCvnSeedError):
        OrcidSeedPool(tmp_path / "missing")
    (tmp_path / "empty").mkdir()
    with pytest.raises(SyntheticCvnSeedError):
        OrcidSeedPool(tmp_path / "empty")


def test_seed_pool_draws_distinct_files_then_reuses_with_a_higher_round(tmp_path, monkeypatch):
    monkeypatch.setattr(seed_module, "_EXHAUSTION_MISSES", 50)
    paths = _write_pool(tmp_path / "pool", 6)
    draws = OrcidSeedPool(tmp_path / "pool").iter_draws(random.Random(1))

    first_round = [next(draws) for _ in range(6)]
    assert {draw.path for draw in first_round} == set(paths.values())
    assert {draw.reuse_round for draw in first_round} == {0}
    assert next(draws).reuse_round == 1


def test_generated_documents_are_all_valid_and_counts_are_consistent(tmp_path):
    _write_pool(tmp_path / "pool", 12)

    result = generate_synthetic_cvn(_config(tmp_path, count=30))

    assert (result.generated, result.invalid_discarded) == (30, 0)
    assert result.linked + result.unlinked == 30
    documents = _read_documents(tmp_path / "out")
    assert len(documents) == 30
    assert all(validate_synthetic_document(document) == () for document in documents)
    assert len({d["curriculum"]["identity"]["identificador_unico_de_cv"] for d in documents}) == 30
    assert all(d["metadata"]["source"]["synthetic"] is True for d in documents)


def test_same_seed_gives_identical_output_and_a_different_seed_differs(tmp_path):
    _write_pool(tmp_path / "pool", 12)

    generate_synthetic_cvn(_config(tmp_path, output_dir=tmp_path / "a"))
    generate_synthetic_cvn(_config(tmp_path, output_dir=tmp_path / "b"))
    generate_synthetic_cvn(_config(tmp_path, output_dir=tmp_path / "c", seed=8))

    read = lambda name: (tmp_path / name / "cvn_shard_00000.jsonl").read_bytes()  # noqa: E731
    assert read("a") == read("b")
    assert read("a") != read("c")


def test_link_ratio_controls_the_orcid_id_and_the_manifest_records_ground_truth(tmp_path):
    paths = _write_pool(tmp_path / "pool", 12)

    generate_synthetic_cvn(_config(tmp_path, output_dir=tmp_path / "linked", orcid_link_ratio=1.0))
    generate_synthetic_cvn(_config(tmp_path, output_dir=tmp_path / "unlinked", orcid_link_ratio=0.0))

    for document, entry in zip(_read_documents(tmp_path / "linked"), _read_manifest(tmp_path / "linked"), strict=True):
        identity = document["curriculum"]["identity"]
        assert entry["linkage"] == "orcid_id"
        assert identity["identificador_digital_de_autor"] == [entry["seed_orcid_id"]]
        assert identity["tipo_de_identificador_digital_de_autor"][0]["code"] == "140"
        assert entry["name_variant"] == "exact"

    unlinked_documents = _read_documents(tmp_path / "unlinked")
    for document, entry in zip(unlinked_documents, _read_manifest(tmp_path / "unlinked"), strict=True):
        assert entry["linkage"] == "name_affiliation"
        assert entry["seed_orcid_id"] in paths
        assert "identificador_digital_de_autor" not in document["curriculum"]["identity"]
        # Neither the iD nor the seed's private text may leak into an unlinked document.
        assert entry["seed_orcid_id"] not in json.dumps(document)
        assert _BIOGRAPHY not in json.dumps(document)


def test_unlinked_documents_keep_the_seed_affiliations_with_a_varied_name(tmp_path):
    _write_pool(tmp_path / "pool", 12)

    generate_synthetic_cvn(_config(tmp_path, count=40, orcid_link_ratio=0.0))

    documents = _read_documents(tmp_path / "out")
    manifest = _read_manifest(tmp_path / "out")
    assert {entry["name_variant"] for entry in manifest} <= {
        "exact",
        "accents_stripped",
        "given_initial",
        "family_upper",
        "first_surname_only",
    }
    assert {entry["name_variant"] for entry in manifest} - {"exact"}
    for document in documents:
        organizations = {
            entry["data"].get("entidad_empleadora", {}).get("name")
            for entry in document["curriculum"]["professional_experience"]
        }
        assert "Universidad de Ejemplo" in organizations


def test_manifest_points_at_the_document_it_describes_and_shards_respect_shard_size(tmp_path):
    _write_pool(tmp_path / "pool", 12)

    result = generate_synthetic_cvn(_config(tmp_path, count=25, shard_size=10))

    assert result.shards_written == 3
    shard_lengths = [
        len((tmp_path / "out" / f"cvn_shard_{i:05d}.jsonl").read_text(encoding="utf-8").splitlines()) for i in range(3)
    ]
    assert shard_lengths == [10, 10, 5]
    for entry in _read_manifest(tmp_path / "out"):
        shard_lines = (tmp_path / "out" / entry["shard_file"]).read_text(encoding="utf-8").splitlines()
        document = json.loads(shard_lines[entry["line_number"]])
        assert document["curriculum"]["identity"]["identificador_unico_de_cv"] == entry["document_id"]


def test_existing_run_is_not_overwritten_unless_requested(tmp_path):
    _write_pool(tmp_path / "pool", 12)
    generate_synthetic_cvn(_config(tmp_path, count=5))

    with pytest.raises(FileExistsError):
        generate_synthetic_cvn(_config(tmp_path, count=5))
    result = generate_synthetic_cvn(_config(tmp_path, count=5, overwrite=True))
    assert result.generated == 5


def test_count_beyond_pool_size_reuses_seeds_without_identical_documents(tmp_path, monkeypatch):
    monkeypatch.setattr(seed_module, "_EXHAUSTION_MISSES", 50)
    _write_pool(tmp_path / "pool", 6)

    result = generate_synthetic_cvn(_config(tmp_path, count=15))

    assert result.generated == 15
    assert result.max_seed_reuse_round >= 1
    serialized = {json.dumps(document, sort_keys=True) for document in _read_documents(tmp_path / "out")}
    assert len(serialized) == 15


def test_seeds_without_works_or_affiliations_still_produce_valid_documents(tmp_path):
    _write_pool(tmp_path / "pool", 6, rich_every=10**6)  # only index 0 is rich; the rest are bare

    result = generate_synthetic_cvn(_config(tmp_path, count=12))

    documents = _read_documents(tmp_path / "out")
    assert result.invalid_discarded == 0
    assert any(not document["curriculum"]["research"] for document in documents)
    assert all(validate_synthetic_document(document) == () for document in documents)


def test_work_types_and_dois_are_mapped_and_normalized(tmp_path):
    _write_pool(tmp_path / "pool", 3)

    generate_synthetic_cvn(_config(tmp_path, count=6))

    publications = [
        entry["data"]
        for document in _read_documents(tmp_path / "out")
        for entry in document["curriculum"]["research"]
    ]
    by_title = {data["publicacion_titulo"]: data for data in publications}
    assert by_title["Un artículo de ejemplo"]["tipo_de_produccion"]["code"] == "020"
    assert by_title["Un artículo de ejemplo"]["identificador_de_publicacion_digital"] == ["10.1000/abc"]
    assert by_title["Un capítulo de ejemplo"]["tipo_de_produccion"]["code"] == "004"
    assert "identificador_de_publicacion_digital" not in by_title["Un capítulo de ejemplo"]
    conference = by_title["Una ponencia de ejemplo"]
    assert conference["tipo_de_produccion"]["code"] == "OTHERS"
    assert conference["tipo_de_produccion_otros"] == "conference-paper"


def test_at_most_one_current_position_and_durations_use_the_manual_format(tmp_path):
    _write_pool(tmp_path / "pool", 3)

    generate_synthetic_cvn(_config(tmp_path, count=6))

    for document in _read_documents(tmp_path / "out"):
        entries = document["curriculum"]["professional_experience"]
        assert sum(entry["type"].endswith("010_010_000_000") for entry in entries) <= 1
        for entry in entries:
            if "duracion" in entry["data"]:
                # Fixture employment runs 2012-09 to 2018-06: 5 years 9 months.
                assert entry["data"]["duracion"] == "05.09.00"


def _valid_generated_document(tmp_path: Path) -> dict:
    _write_pool(tmp_path / "pool", 3)
    generate_synthetic_cvn(_config(tmp_path, count=1, orcid_link_ratio=1.0))
    return _read_documents(tmp_path / "out")[0]


def test_validation_rejects_invented_fields_missing_required_fields_and_unknown_types(tmp_path):
    document = _valid_generated_document(tmp_path)
    assert validate_synthetic_document(document) == ()

    document["curriculum"]["identity"]["campo_inventado"] = 1
    del document["curriculum"]["identity"]["apellidos"]
    document["curriculum"]["research"].append({"type": "research.no_existe", "data": {}})

    errors = " | ".join(validate_synthetic_document(document))
    assert "campo_inventado" in errors
    assert "'apellidos' is a required property" in errors
    assert "research.no_existe" in errors


def test_validation_rejects_an_orcid_id_with_a_bad_checksum(tmp_path):
    document = _valid_generated_document(tmp_path)
    document["curriculum"]["identity"]["identificador_digital_de_autor"] = ["0000-0000-0000-0000"]

    assert any("checksum" in error for error in validate_synthetic_document(document))


@pytest.mark.parametrize(
    "overrides",
    [{"count": 0}, {"orcid_link_ratio": 1.5}, {"orcid_link_ratio": -0.1}, {"shard_size": 0}],
)
def test_config_rejects_out_of_range_values(tmp_path, overrides):
    with pytest.raises(ValueError):
        _config(tmp_path, **overrides)
