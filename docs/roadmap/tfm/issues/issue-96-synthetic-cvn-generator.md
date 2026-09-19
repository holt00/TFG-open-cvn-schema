# Issue 96 - Synthetic CVN Generator

## Summary

Generate schema-valid Open CVN JSON curricula, seeded with real ORCID
fields. Third data-source issue of TFM epic phase 2.

## Original Goal

Produce a configurable volume of realistic, schema-valid synthetic CVN
documents, without sourcing real personal CVN data (rejected in the epic on
privacy/consent grounds).

## Original Plan

- reuse `schemas/open_cvn.schema.json` as the validation target and the
  small set of `examples/open_cvn/` documents as structural seed templates
  (both TFG artifacts, not rebuilt)
- take real public fields (names, works, affiliations, dates) from issue
  `#94` and/or `#95`'s ORCID data as seed data for each generated curriculum
- generate synthetic Open CVN JSON documents at a configurable volume
- validate every generated document against the schema, reusing
  `src/open_cvn/parser_contract.py`'s `validate_open_cvn_json(...)` rather
  than reimplementing validation

## Adjustments Made During Implementation

Plan accepted on 2026-09-19. Design decisions locked before any code, each
with its reason, so a later session does not re-litigate them.

**Finding that shaped the plan: the schema validates weakly.**
`validate_open_cvn_json(...)` runs JSON Schema and then Pydantic
(`OpenCvnDocument`), but `curriculum.identity` and every entry's `data` are
`additionalProperties: true` in both. A document with invented field names
would pass. "Schema-valid" alone therefore does not prove realism or
conformity to the CVN model. Decision: keep `validate_open_cvn_json(...)` as
the required first gate (per the original plan, no reimplementation) and add
a stricter, generator-owned layer on top (see Task 5).

**Decision 1 - data shape: the schema's own Spanish snake_case field names,
same as the XML semantic importer emits, not the English names of
`examples/open_cvn/*.json`.** The examples are hand-authored
(`given_name`, `family_name`); real CVNs imported through
`parse_cvn_xml(...)` produce `nombre`, `apellidos`,
`fecha_de_titulacion`, and entry `type` values of the form
`<section>.<entity>_<cvn_code>`. Issue `#98` must handle real and synthetic
CVNs identically, so the synthetic documents follow the importer's shape.
The examples remain structural seed templates for the envelope
(`schema_version`, `metadata`, `curriculum`) only.

**Decision 2 - seed source: local `data/orcid_bulk/filtered/` files from
issue `#95` only; the `#94` API client is not used.** 301,763 local records
are enough seed volume, offline and reproducible. The anonymous API tier is
capped at 25k reads/day per IP, and API enrichment here would be scope the
epic does not assign to `#96`.

**Decision 3 - scaling: `count` and `seed` are parameters; beyond the seed
pool size, seeds are reused with variation**, never exact duplicates. Issue
`#101` needs a scalable synthetic volume, and the verification requirement
says generated documents must vary realistically rather than be
near-duplicates. (As first written this listed shifted dates and swapped
organizations as variation; that was dropped during implementation because
it falsifies real data. See "Refines Decision 3" below for what varies.)

**Decision 4 - ORCID linkage: configurable `orcid_link_ratio`, with a ground
truth manifest.** Linked documents carry the seed's ORCID iD in
`identificador_digital_de_autor` (CVN code `000.010.000.260`, type code `140`
= ORCID in `CVN_SOURCE_C`, `000.010.000.270`). Unlinked documents carry no
iD but keep the seed's name and affiliation with realistic variation
(accents, name order, initials). A sidecar manifest records, per document,
the seed iD and the linkage kind. Reason: issue `#98`'s own verification
needs known shared-iD pairs, name/affiliation-fallback pairs, and unrelated
records, and a generator that forgets its own ground truth makes that
verification impossible. This is the only addition close to the scope edge;
it is kept because `#98` depends on it and adds no new technology.

**Decision 5 - output: sharded JSON Lines plus a manifest, in the git-ignored
`data/synthetic_cvn/`.** Issue `#95` showed that hundreds of thousands of
small files on the Windows-mounted `/mnt/e` drive are I/O-bound, and issue
`#97` will land the output into MinIO, where few large objects beat many
tiny ones. `shard_size` documents per file.

**Decision 6 - module path `src/tfm_lakehouse/synthetic_cvn/`, not the
epic's `src/tfm_lakehouse/ingestion/synthetic_cvn_generator.py`.** Same
reasoning and same precedent as issues `#94` (`orcid_client/`) and `#95`
(`orcid_bulk/`): one dedicated package per data-source concern. Test files
follow the same precedent (`test_synthetic_cvn_*.py`) rather than the epic's
`test_tfm_*.py`.

**Decision 7 - bounded set of entry types.** `identity.person`;
`education` (university degree and doctorate);
`professional_experience` (`professionalsituation`, fed by ORCID
employments); `research` (scientific publications, fed by ORCID works and
DOIs). Remaining sections stay empty. Reason: the schema has ~100 entity
types; generating all of them would be unbounded work for a 6 ECTS project
and the epic asks for realistic, not exhaustive, curricula.

**Decision 8 - no new dependency: `random.Random(seed)` from the standard
library with small hand-curated pools, not Faker.** Faker offers `es_ES`
and seeded generation, but its Python 3.14 support could not be confirmed
and this repository requires `>=3.14`. ORCID already supplies the realistic
names, titles, and organizations, so synthetic pools are only needed for
identity filler.

**Decision 9 - privacy handling.** The ORCID Public Data File is CC0, but
ORCID states that the rights of privacy and publicity of the individuals in
it remain, and asks users not to present modified data as genuine.
Consequently: only names, work titles/years/DOIs, affiliations, and
keywords are taken from ORCID; biography, emails, and researcher URLs are
never copied; identity filler (DNI, phone, email, birth date) is fully
invented, with phones in a non-existent range and emails on the
`example.invalid` domain; every document is marked synthetic. (As first
written this planned DNIs in a fictitious range and put the marker in
`metadata.generator`; both changed during implementation, see the two
"Refines Decision 9" adjustments below.)

**Task 1 findings (verified against the schema, the importer, and the
reference tables, not assumed):**

- **Each entity `$def` in `schemas/open_cvn.schema.json` is itself strict**:
  `additionalProperties: false` plus its own `required` list. The document
  schema does not enforce it (entry `data` is free-form there), but
  validating `data` against `#/$defs/<entity>` (with the root `$defs`
  available for `$ref` resolution) rejects invented fields and missing
  required ones. Verified: the English `examples/open_cvn/education_entry.json`
  `data` fails against its entity `$def` (`degree_name`, `start_date`, ... are
  "unexpected"), which confirms Decision 1. **Decision 10 (refines Task 5):**
  the generator-owned strict layer is exactly this per-entity `$def`
  validation, not a hand-written field-name list; it is derived from the
  schema so it cannot drift from it.
- Consequence: synthetic documents must be **fully compliant**, stricter than
  what the XML importer emits (which maps only the fields present in the
  source and would fail required-field checks). Required fields per chosen
  type: `identity.person` needs `nombre`, `apellidos`, `sexo`,
  `fecha_de_nacimiento`, `fecha_del_documento`, `telefono_fijo`;
  `research.publicacionesdocumentoscientificosytecnicos_060_010_010_000`
  needs only `tipo_de_produccion`;
  `professional_experience.cargosyactividadesdesempenadosconanterioridad_010_020_000_000`
  needs `ambito_actividad_de_direccion_y_o_gestion`,
  `categoria_profesional_puesto_o_cargo`, `duracion`, `entidad_empleadora`,
  `fecha_de_finalizacion`, `fecha_de_inicio`;
  `education.estudiosde1oy2ocicloy...020_010_010_000` needs
  `entidad_de_titulacion` and `fecha_de_titulacion`.
- **Entity type corrections to Decision 7**, found while reading the
  schema: (a) the received-degree entity is
  `education.estudiosde1oy2ocicloyantiguoscicloslicenciadosdiplomadosingenierossuperioresingenierostecnicosarquitectos_020_010_010_000`
  (the fixture-tested one); `education.titulacionuniversitaria_030_010_000_020`
  belongs to the *teaching delivered* block (`030`), not to degrees received,
  so it is not used. (b) ORCID employments are past and present positions, so
  they map to `professional_experience.cargosyactividadesdesempenadosconanterioridad_010_020_000_000`
  when they have an end date, and to
  `professional_experience.professionalsituation_010_010_000_000` (the
  current-situation entity) for at most one open-ended employment per
  document. (c) doctorate: `education.doctorados_020_010_020_000`.
- **Value shapes.** Controlled references are objects
  `{code, label, raw_value, source}`; `EntityNameValue` is
  `{name, others}`; `FlexibleDateValue` is `{raw_value, year, month, day}`.
  The schema declares `year`/`month`/`day` as **strings**, but the XML
  importer's `_flexible_date` emits **integers**. Neither is rejected today
  for the importer's output because `data` is free-form there. **Decision 11:
  the generator follows the schema's declared type (strings)**, because the
  per-entity `$def` check in Decision 10 enforces it and the schema is the
  contract; the importer/schema mismatch is a pre-existing TFG inconsistency,
  recorded as a limitation, not fixed here (TFG code is out of scope).
- **Code values (from `ReferenceTables.xml`)**: `CVN_SEX_A` `000` Hombre /
  `010` Mujer (the only strict enum); `CVN_SOURCE_C` `140` ORCID;
  `CVN_SOURCE_B` `040` DOI; `CVN_SITUATION_A` (contract type) 8 values, e.g.
  `160` indefinido, `170` temporal, `350` Funcionario/a, `040` Becario/a;
  `CVN_DEDICATION_A` `020` completo / `030` parcial;
  `CVN_MANAGEMENT_TYPE_A` `000` Universitaria, `010` OPIs; `CVN_ENTITY_TYPE`
  `000` Universidad, `060` OPI; `ISO_3166` `724` = Espana;
  `CVN_PUBLICATION_A` (18 values) `020` Articulo cientifico, `004` Capitulo
  de libro, `032` Libro o monografia cientifica, `018` Informe
  cientifico-tecnico, `210` Software de investigacion, `211` Set de datos,
  `OTHERS` Otros; `CVN_TITLE_B` (2,765 degree names, codes like `2500013`
  Graduado o Graduada en Derecho) and `CVN_TITLE_C` (3,102 doctorate
  programme names) are large open tables. Every `vocabularies.*` schema type
  other than `CVN_SEX_A` is an open `string`, so a code outside the table is
  not rejected by the schema; the generator still restricts itself to codes
  actually present in the reference tables and takes them from a small
  hand-picked constant set, verified now, rather than loading the 2 MB
  `ReferenceTables.xml` at runtime.
- Mapping ORCID work type to `CVN_PUBLICATION_A` (`journal-article` -> `020`,
  `book-chapter` -> `004`, `book` -> `032`, `report` -> `018`, software ->
  `210`, dataset -> `211`, anything else -> `OTHERS`) is a generator
  decision, not a source fact; the ORCID type vocabulary observed in real
  data is checked in Task 2 before the table is frozen.

**Adjustments found while implementing (each one a refinement of a decision
above, recorded because it changes what the decision said):**

- **Refines Decision 9 - no DNI, no nationality, random sex.** Both DNI and
  nationality are optional in the schema, `#98` does not need them, and no DNI
  range can be guaranteed to belong to no real person, so they are omitted.
  `sexo` (required) is drawn at random and is deliberately *not* inferred from
  the ORCID name. Phones use a `000`-prefixed number (not a valid Spanish
  range) and emails use `@example.invalid` (RFC 2606).
- **Refines Decision 9 - the synthetic marker lives in `metadata.source`.**
  Task 1 assumed `metadata.generator` could carry it, but that object only
  allows `name` and `version` (`additionalProperties: false`). `metadata.source`
  allows extra keys, so it carries `format: "synthetic_open_cvn_json"`,
  `synthetic: true`, `generator_seed`, and `orcid_snapshot`. The seed record's
  ORCID iD is never written into an unlinked document (a unit test asserts
  it); it exists only in the manifest.
- **Refines Decision 3 - variation is subsetting and filler, not altered
  facts.** Documents differ by a random subset of 3-40 of the seed's works,
  the invented identity filler, contract/dedication/duties, and (for unlinked
  documents) a name variant. Publication years, organizations, and dates are
  never shifted or swapped: ORCID asks that data not be modified to become
  false, and the epic wants realism, not fabricated careers. Consequence:
  when a seed is reused (pool exhausted), its employments and education are
  identical across the documents built from it (see limitations).
- **Discarding versus raising on an invalid document.** Invalid documents are
  discarded and counted, with the first five error lists kept in
  `SyntheticCvnResult.invalid_samples`; the run aborts with
  `SyntheticCvnGenerationError` if attempts exceed `3 * count + 1000`. The first
  real run showed why this layer exists: 179 of 200 documents were discarded
  because of two builder bugs that the document schema alone would never have
  caught (the degree entity names its city/country fields
  `ciudad_entidad_titulacion`/`pais_entidad_titulacion`, unlike the doctorate
  entity; and `titulo_homologado_fecha_de_homologacion` is required and not
  nullable, so an empty date object is emitted). Both were fixed; later runs had
  zero discards.
- **`duracion` format** is the CVN manual's `YY.MM.DD` (e.g. `05.09.00`),
  verified in `SpecificationManual.xml` for item `010.020.000.190`, computed
  from the ORCID start/end year and month; it is not ISO 8601.
- **ORCID work-type mapping frozen against real data.** Counts in a random
  400-record sample of the subset: `journal-article` 7,504,
  `conference-paper` 688, `book-chapter` 489, `book` 246, `other` 174,
  `preprint` 95, `working-paper` 51, `dissertation-thesis` 42,
  `conference-poster` 21, `conference-abstract` 21, `data-set` 20,
  `magazine-article` 19, `report` 13, `edited-book` 12. Mapping: journal
  article `020`, book chapter `004`, book `032`, edited book `208`, report
  `018`, data set `211`, software/research tool `210`, magazine article `203`,
  everything else `OTHERS` plus the ORCID type in `tipo_de_produccion_otros`.
- **Education classification is keyword-based.** ORCID education entries carry
  only a free-text role. Text with a doctorate marker becomes a doctorate
  entry; text with a degree marker (licenciad, grado, ingenier, bachelor,
  ...) becomes a first/second-cycle degree entry; master's and anything
  unrecognized are skipped rather than misfiled (there is a distinct CVN
  postgraduate entity that was deliberately not added). Result: 54% of
  generated documents have no education entries.
- **Only Spanish organizations get a country reference** (`ISO_3166` code
  `724`): ORCID uses alpha-2, the CVN table numeric codes, and that mapping
  was not verified.
- **Performance changed the design (measured, not assumed).** The first
  10,000-document run on real data ran at ~16 documents/s with the process in
  disk-wait (`D` state, 27% CPU): reading ~300k small seed files from the
  Windows-mounted drive dominates, the same wall issue `#95` hit. Validation
  costs ~10 ms/document and document building is negligible. Fix: seed files are
  read ahead by a 16-thread pool with a 128-file window, and the pool draws use
  a random stream separate from the document-building stream so prefetching
  cannot change the output. After the change the same run took 169 s
  (~59 documents/s).
- Test file names follow the `#94`/`#95` precedent
  (`tests/test_synthetic_cvn_generator_unit.py`,
  `tests/test_synthetic_cvn_local_smoke.py`), not the epic's `test_tfm_*.py`.

Revised task breakdown (status in brackets):

1. **Task 0 - lock decisions and plan in this document** [done].
2. **Task 1 - verify field shapes against the schema and importer** [done].
3. **Task 2 - seed reader** (`seed.py`) [done].
4. **Task 3 - document builders** (`builders.py`) [done].
5. **Task 4 - variation and linkage engine** (`config.py`, `generator.py`)
   [done].
6. **Task 5 - validation layer** (`validation.py`) [done].
7. **Task 6 - writer** (`writer.py`, `__init__.py`) [done].
8. **Task 7 - unit tests** on fabricated ORCID fixtures [done].
9. **Task 8 - real-data run**: throughput, variety, gated smoke test [done].
10. **Task 9 - documentation update** [done].

## Implementation Performed

New package `src/tfm_lakehouse/synthetic_cvn/`:

- `seed.py`: `parse_orcid_summary` (ORCID summary XML to typed `OrcidSeed`;
  reads name, employments, educations, works with DOI, keywords; never
  biography, emails, or URLs; returns `None` for malformed XML, an invalid
  ORCID iD checksum, or a missing given/family name) and `OrcidSeedPool`
  (lazy per-bucket listing, distinct random draws, then reuse with an
  incremented `reuse_round` once the pool is exhausted).
- `builders.py`: `build_document` and `vary_name`; entity types
  `identity.person`, degree and doctorate education, past and current
  professional positions, and scientific publications, each filled with all
  required fields per its entity `$def`.
- `validation.py`: `validate_synthetic_document` = `validate_open_cvn_json`
  (warnings count as errors) plus per-entity `$defs` validation of identity
  and every entry's `data`, plus ORCID iD checksum validation reusing
  `tfm_lakehouse.orcid_client`.
- `writer.py`: `ShardedJsonlWriter` (JSON Lines shards
  `cvn_shard_NNNNN.jsonl` plus `manifest.jsonl` with document id, seed ORCID
  iD, linkage, seed reuse round, name variant, shard file and line number).
- `config.py`/`generator.py`: `SyntheticCvnConfig` (`count`, `seed`,
  `orcid_seed_dir`, `output_dir`, `orcid_link_ratio`=0.7, `shard_size`=10,000,
  `overwrite`) and `generate_synthetic_cvn(config) -> SyntheticCvnResult`,
  the function issue `#97`'s Airflow task should call. No CLI and no new
  dependency.
- Tests: `tests/test_synthetic_cvn_generator_unit.py` (23 cases on fabricated
  ORCID XML, no network) and `tests/test_synthetic_cvn_local_smoke.py` (skipped
  when `data/orcid_bulk/filtered/` is absent).
- `pyproject.toml`: added `[tool.pytest.ini_options] testpaths = ["tests"]`
  (see Findings).
- Documentation: this document, `docs/context/tfm/current_status.md`,
  `docs/roadmap/tfm/tfm_roadmap.md`, `docs/pipeline/known_limitations.md`
  (three new sections), `PROJECT_GUIDE.md`. `.gitignore` already covered
  `data/`, so nothing was added there.

## Verification

- `uv run pytest tests/test_synthetic_cvn_generator_unit.py -q` -- 23 passed:
  every generated document passes both validation layers; same seed gives
  byte-identical output and a different seed does not; `orcid_link_ratio` 1.0
  and 0.0 behave as specified and the manifest matches the documents; no ORCID
  iD or biography text leaks into an unlinked document; manifest line numbers
  resolve to the documented document; shard sizes are respected; an existing
  run is not overwritten without `overwrite`; a count beyond the pool size
  reuses seeds without identical documents; seeds without works or
  affiliations still produce valid documents; the strict layer rejects an
  invented field, a missing required field, an unknown entity type, and a
  bad ORCID checksum.
- `uv run pytest tests/test_synthetic_cvn_local_smoke.py -q` -- 1 passed
  against the real subset (150 documents, 0 discarded).
- 10,000 documents from the real subset (seed 42, `orcid_link_ratio` 0.7),
  written to a scratch directory outside the repository: 10,000 generated,
  0 discarded as invalid, 7,000 linked / 3,000 unlinked, 279 unusable seed
  records skipped (2.7%), 169 s (~59 documents/s), 83.4 MB (8.3 KB per
  document), 10,000 distinct document ids, 9,994 distinct names.
- variety on those 10,000: 86,944 publications of which 79,747 have distinct
  titles (91.7%; the rest are titles shared by different people); median 7
  entries per document, maximum 51; documents with no education 54%, with no
  research 30%, with no professional experience 28%.
- full suite, `uv run pytest -n auto tests` (the documented command):
  531 passed, 2 skipped (the two `*_live_smoke` tests that need
  `ORCID_LIVE_TEST=1`) in 8 min 25 s.

## Findings

- The Open CVN document schema does not constrain entry `data` or `identity`,
  so `validate_open_cvn_json` alone would have passed the two builder bugs that
  discarded 179 of the first 200 documents. Each entity's own `$defs` schema is
  strict and is the right validation target.
- `FlexibleDateValue` is declared with string parts in the schema but the XML
  importer emits integers; see `docs/pipeline/known_limitations.md`.
- Seed reading, not validation or document building, bounds throughput: ~10 ms
  per document to validate, negligible to build, but ~50 ms per document to
  read seed files cold from `/mnt/e`. Threaded prefetch gave ~3.7x. Generating
  the whole 301,763-record pool would take roughly 85 minutes at the measured
  rate; volumes above the pool size (issue `#101`) use seed reuse, which is
  covered by a unit test but was not run at real scale.
- 2.7% of ORCID summary records are unusable as seeds (mostly a missing family
  name).
- a bare `pytest` (no path) hung in collection: pytest recurses into the
  git-ignored `data/` directory, which holds the 301,763 XML files from issue
  `#95` (over 2.5 minutes stuck at "collecting" in disk wait, observed while
  verifying this issue). The documented `uv run pytest -n auto tests` was
  never affected, and CI has no `data/`. Fixed at the user's request with
  `[tool.pytest.ini_options] testpaths = ["tests"]` in `pyproject.toml`; a
  bare `pytest --collect-only` now collects 533 tests in ~12 s.
- unlinked documents (no ORCID iD) still contain the seed's real publication
  titles and DOIs, so they remain linkable to the seed record by content, not
  only by name and affiliation. That is acceptable for `#98`'s fallback checks
  but means the unlinked share is not a test of name/affiliation matching in
  isolation.

## Known Limitations

Per the epic, sourcing additional real CVN documents beyond the existing small
TFG example set remains explicitly out of scope. Recorded in
`docs/pipeline/known_limitations.md`: synthetic documents combine real public
ORCID data with invented personal data; coverage is deliberately narrow (four
entity types, `OTHERS` for unmapped work types, owner-only author lists, no
codes for `CVN_TITLE_B`/`CVN_TITLE_C` references, country only for Spain,
identical employments and education when a seed is reused); the schema does
not enforce entity shapes and disagrees with the XML importer on date types.

## Impact On Future Issues

Feeds issue `#97` (bronze landing): call
`tfm_lakehouse.synthetic_cvn.generate_synthetic_cvn` from the
`generate_synthetic_cvn` task; the output is JSON Lines shards plus
`manifest.jsonl`, which suits landing a few large objects into MinIO. Every
line of a shard is a complete Open CVN JSON document. The landing-time
structural check can reuse `validate_open_cvn_json`, and should also consider
`validate_synthetic_document` if it wants entity-level conformity.

Feeds issue `#98`: CVN documents carry the seed's ORCID iD in
`curriculum.identity.identificador_digital_de_autor` (with type code `140` in
`tipo_de_identificador_digital_de_autor`) for the linked share, and no iD but
a varied name plus unchanged affiliations for the rest. `manifest.jsonl` is the
ground truth for checking entity resolution. `#98` must accept both date
representations (string parts from this generator, integer parts from the XML
importer) and should not assume `sexo`, birth date, or contact data relate to
the real person.

Feeds issue `#101`: `count` and `seed` give a reproducible scalable volume;
beyond ~300k documents seeds are reused with only publication-subset and filler
variation.

## Status

`Completed`
