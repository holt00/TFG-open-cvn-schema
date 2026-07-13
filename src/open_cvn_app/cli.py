from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from open_cvn import CvnParseIssue, CvnValidationStatus, parse_open_cvn_json
from open_cvn_app import __version__
from open_cvn_app.config import OpenCvnAppConfig
from open_cvn_app.editing import list_curriculum_entries, list_curriculum_sections
from open_cvn_app.latex import export_latex_document
from open_cvn_app.pdf import (
    PdfCompilationError,
    PdfGenerationUnavailable,
    PdfPreviewError,
    format_compilation_diagnostics,
    generate_pdf_document,
)
from open_cvn_app.results import AppResult
from open_cvn_app.storage import (
    SCHEMA_VERSION,
    CurriculumCreate,
    CurriculumRepository,
    MasterCurriculumNotFound,
    StorageError,
    initialize_store,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="open-cvn",
        description="Local CLI shell for managing Open CVN curriculum data.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"open-cvn {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    version_parser = subparsers.add_parser("version", help="Show application version.")
    version_parser.set_defaults(handler=_handle_version)

    store_parser = subparsers.add_parser("store", help="Manage local curriculum store.")
    store_subparsers = store_parser.add_subparsers(dest="store_command")
    store_init_parser = store_subparsers.add_parser("init", help="Initialize local store.")
    _add_store_path_option(store_init_parser, option_name="--path")
    store_init_parser.set_defaults(handler=_handle_store_init)

    json_parser = subparsers.add_parser("json", help="Import or export Open CVN JSON.")
    json_subparsers = json_parser.add_subparsers(dest="json_command")
    json_import_parser = json_subparsers.add_parser("import", help="Import Open CVN JSON.")
    json_import_parser.add_argument("input", help="Input Open CVN JSON file.")
    json_import_parser.add_argument("--name", help="Stored curriculum display name.")
    json_import_parser.add_argument(
        "--as-master",
        action="store_true",
        help="Assign imported curriculum as the master version.",
    )
    _add_store_path_option(json_import_parser)
    json_import_parser.set_defaults(handler=_handle_json_import)
    json_export_parser = json_subparsers.add_parser("export", help="Export Open CVN JSON.")
    json_export_parser.add_argument("output", help="Output Open CVN JSON file.")
    _add_store_path_option(json_export_parser)
    _add_version_option(json_export_parser)
    json_export_parser.set_defaults(handler=_handle_json_export)

    versions_parser = subparsers.add_parser("versions", help="Manage curriculum versions.")
    versions_subparsers = versions_parser.add_subparsers(dest="versions_command")
    versions_list_parser = versions_subparsers.add_parser("list", help="List curriculum versions.")
    _add_store_path_option(versions_list_parser)
    versions_list_parser.set_defaults(handler=_handle_versions_list)
    versions_master_parser = versions_subparsers.add_parser("master", help="Assign master curriculum version.")
    versions_master_parser.add_argument("curriculum_id", help="Stored curriculum ID to assign as master.")
    _add_store_path_option(versions_master_parser)
    versions_master_parser.set_defaults(handler=_handle_versions_master)
    versions_show_parser = versions_subparsers.add_parser("show", help="Show curriculum version metadata.")
    versions_show_parser.add_argument("name", help="Version name or ID.")
    _add_store_path_option(versions_show_parser)
    versions_show_parser.set_defaults(handler=_handle_versions_show)
    versions_sections_parser = versions_subparsers.add_parser(
        "sections",
        help="List curriculum sections in a version.",
    )
    versions_sections_parser.add_argument("name", help="Version name or ID.")
    _add_store_path_option(versions_sections_parser)
    versions_sections_parser.set_defaults(handler=_handle_versions_sections)
    versions_entries_parser = versions_subparsers.add_parser(
        "entries",
        help="List entries in a curriculum section.",
    )
    versions_entries_parser.add_argument("name", help="Version name or ID.")
    versions_entries_parser.add_argument("section", help="Curriculum section name or /curriculum section pointer.")
    _add_store_path_option(versions_entries_parser)
    versions_entries_parser.set_defaults(handler=_handle_versions_entries)
    versions_metadata_parser = versions_subparsers.add_parser(
        "metadata",
        help="Show or update derived version metadata.",
    )
    versions_metadata_parser.add_argument("name", help="Derived version name or ID.")
    versions_metadata_parser.add_argument("--display-name", help="Human display name for the derived version.")
    versions_metadata_parser.add_argument("--purpose", help="Human purpose for the derived version.")
    _add_store_path_option(versions_metadata_parser)
    versions_metadata_parser.set_defaults(handler=_handle_versions_metadata)
    versions_derive_parser = versions_subparsers.add_parser(
        "derive",
        help="Create derived curriculum version.",
    )
    versions_derive_parser.add_argument("name", help="Derived version name.")
    versions_derive_parser.add_argument(
        "--from",
        dest="source",
        default="master",
        help="Source version name.",
    )
    _add_store_path_option(versions_derive_parser)
    versions_derive_parser.set_defaults(handler=_handle_versions_derive)
    versions_include_parser = versions_subparsers.add_parser("include", help="Include selection pointer in derived version.")
    versions_include_parser.add_argument("name", help="Derived version name or ID.")
    versions_include_parser.add_argument("pointer", help="JSON Pointer under /curriculum.")
    _add_store_path_option(versions_include_parser)
    versions_include_parser.set_defaults(handler=_handle_versions_include)
    versions_exclude_parser = versions_subparsers.add_parser("exclude", help="Exclude selection pointer from derived version.")
    versions_exclude_parser.add_argument("name", help="Derived version name or ID.")
    versions_exclude_parser.add_argument("pointer", help="JSON Pointer under /curriculum.")
    _add_store_path_option(versions_exclude_parser)
    versions_exclude_parser.set_defaults(handler=_handle_versions_exclude)
    versions_field_edit_parser = versions_subparsers.add_parser(
        "field-edit",
        help="Report unsupported field-level edit behavior for the MVP.",
    )
    versions_field_edit_parser.add_argument("name", help="Version name or ID.")
    versions_field_edit_parser.add_argument("pointer", help="Field JSON Pointer.")
    versions_field_edit_parser.add_argument("value", help="Replacement value.")
    _add_store_path_option(versions_field_edit_parser)
    versions_field_edit_parser.set_defaults(handler=_handle_versions_field_edit)

    latex_parser = subparsers.add_parser("latex", help="Export curriculum to LaTeX.")
    latex_subparsers = latex_parser.add_subparsers(dest="latex_command")
    latex_export_parser = latex_subparsers.add_parser("export", help="Export LaTeX file.")
    latex_export_parser.add_argument("output", help="Output LaTeX file.")
    _add_store_path_option(latex_export_parser)
    _add_version_option(latex_export_parser)
    latex_export_parser.set_defaults(handler=_handle_latex_export)

    pdf_parser = subparsers.add_parser("pdf", help="Generate optional PDF artifact.")
    pdf_subparsers = pdf_parser.add_subparsers(dest="pdf_command")
    pdf_generate_parser = pdf_subparsers.add_parser("generate", help="Generate PDF file.")
    pdf_generate_parser.add_argument("output", help="Output PDF file.")
    pdf_generate_parser.add_argument(
        "--open",
        action="store_true",
        help="Open the generated PDF with the platform default viewer.",
    )
    _add_store_path_option(pdf_generate_parser)
    _add_version_option(pdf_generate_parser)
    pdf_generate_parser.set_defaults(handler=_handle_pdf_generate)

    return parser


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 0

    result = handler(args)
    stream = sys.stderr if result.error else sys.stdout
    if result.message:
        print(result.message, file=stream)
    if result.error:
        print(result.error, file=sys.stderr)
    return result.exit_code


def main() -> int:
    return run()


def _add_store_path_option(parser: argparse.ArgumentParser, *, option_name: str = "--store") -> None:
    parser.add_argument(option_name, dest="store_path", help="Local Open CVN store path.")


def _add_version_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--version", dest="version_name", default="master", help="Curriculum version name.")


def _config_from_args(args: argparse.Namespace) -> OpenCvnAppConfig:
    return OpenCvnAppConfig.from_store_path(getattr(args, "store_path", None))


def _planned_result(action: str, issue: str, args: argparse.Namespace) -> AppResult:
    config = _config_from_args(args)
    return AppResult.ok(
        f"{action} is planned for issue {issue}. "
        f"Resolved store path: {config.store_path}"
    )


def _handle_version(args: argparse.Namespace) -> AppResult:
    return AppResult.ok(f"open-cvn {__version__}")


def _handle_store_init(args: argparse.Namespace) -> AppResult:
    config = _config_from_args(args)
    try:
        store_info = initialize_store(config.store_path)
    except StorageError as exc:
        return AppResult.failed("Store initialization failed.", error=str(exc))
    return AppResult.ok(
        f"Initialized Open CVN store at {store_info.path}. "
        f"Schema version: {SCHEMA_VERSION}"
    )


def _handle_json_import(args: argparse.Namespace) -> AppResult:
    input_path = Path(args.input)
    repository = _repository_from_args(args)
    parse_result = parse_open_cvn_json(input_path, source_identifier=str(input_path))
    if parse_result.validation_status in {CvnValidationStatus.INVALID, CvnValidationStatus.FAILED}:
        return AppResult.failed(
            "Open CVN JSON import failed.",
            error="\n".join(
                (
                    f"Validation status: {parse_result.validation_status.value}",
                    "Errors:",
                    _format_parse_issues(parse_result.errors),
                )
            ),
        )
    if parse_result.data is None:
        return AppResult.failed(
            "Open CVN JSON import failed.",
            error="Parser accepted input but did not return Open CVN JSON data.",
        )

    display_name = args.name or input_path.stem
    try:
        if args.as_master:
            try:
                repository.get_master_version()
            except MasterCurriculumNotFound:
                pass
            else:
                return AppResult.failed(
                    "Open CVN JSON import failed.",
                    error="A master curriculum version already exists.",
                )
        record = repository.create_curriculum(
            CurriculumCreate(
                display_name=display_name,
                document=parse_result.data,
                source_identifier=str(input_path),
                diagnostics=parse_result.warnings,
            )
        )
        master_line = None
        if args.as_master:
            master = repository.assign_master_curriculum(record.id)
            master_line = f"Assigned master curriculum version '{master.name}' with id {master.id}."
    except StorageError as exc:
        return AppResult.failed("Open CVN JSON import failed.", error=str(exc))

    lines = [
        f"Imported Open CVN JSON as curriculum '{record.display_name}'.",
        f"Curriculum ID: {record.id}",
        f"Validation status: {record.validation_status}",
        f"Source: {input_path}",
    ]
    if master_line is not None:
        lines.append(master_line)
    return AppResult.ok("\n".join(lines))


def _handle_json_export(args: argparse.Namespace) -> AppResult:
    repository = _repository_from_args(args)
    output_path = Path(args.output)
    try:
        materialized = repository.materialize_version(args.version_name)
        _write_canonical_json(output_path, materialized.document)
    except StorageError as exc:
        return AppResult.failed("Open CVN JSON export failed.", error=str(exc))
    except OSError as exc:
        return AppResult.failed("Open CVN JSON export failed.", error=str(exc))
    return AppResult.ok(
        "\n".join(
            (
                f"Exported Open CVN JSON version '{materialized.version.name}' to {output_path}.",
                f"Validation status: {materialized.validation_status}",
            )
        )
    )


def _handle_versions_list(args: argparse.Namespace) -> AppResult:
    repository = _repository_from_args(args)
    try:
        versions = repository.list_versions()
    except StorageError as exc:
        return AppResult.failed("Version listing failed.", error=str(exc))
    if not versions:
        return AppResult.ok("No curriculum versions found.")
    lines = ["Curriculum versions:"]
    lines.extend(
        f"- {version.name} ({version.kind}) id={version.id} "
        f"master={version.master_curriculum_id} source={version.source_version_id or '-'} "
        f"updated={version.updated_at}"
        for version in versions
    )
    return AppResult.ok("\n".join(lines))


def _handle_versions_master(args: argparse.Namespace) -> AppResult:
    repository = _repository_from_args(args)
    try:
        version = repository.assign_master_curriculum(args.curriculum_id)
    except StorageError as exc:
        return AppResult.failed("Master version assignment failed.", error=str(exc))
    return AppResult.ok(f"Assigned master curriculum version '{version.name}' with id {version.id}.")


def _handle_versions_show(args: argparse.Namespace) -> AppResult:
    repository = _repository_from_args(args)
    try:
        version = repository.get_version(args.name)
    except StorageError as exc:
        return AppResult.failed("Version lookup failed.", error=str(exc))
    return AppResult.ok(
        "\n".join(
            (
                f"Name: {version.name}",
                f"ID: {version.id}",
                f"Kind: {version.kind}",
                f"Master curriculum ID: {version.master_curriculum_id}",
                f"Source version ID: {version.source_version_id or '-'}",
                f"Selection mode: {version.selection.mode}",
                f"Included pointers: {', '.join(version.selection.included_pointers) or '-'}",
                f"Excluded pointers: {', '.join(version.selection.excluded_pointers) or '-'}",
                f"Created at: {version.created_at}",
                f"Updated at: {version.updated_at}",
            )
        )
    )


def _handle_versions_sections(args: argparse.Namespace) -> AppResult:
    repository = _repository_from_args(args)
    try:
        sections = list_curriculum_sections(repository, args.name)
    except StorageError as exc:
        return AppResult.failed("Section listing failed.", error=str(exc))
    if not sections:
        return AppResult.ok("No curriculum sections found.")
    lines = [f"Curriculum sections for version '{args.name}':"]
    for section in sections:
        entries = section.entry_count if section.entry_count is not None else section.value_kind
        lines.append(f"- {section.name} pointer={section.pointer} entries={entries}")
    return AppResult.ok("\n".join(lines))


def _handle_versions_entries(args: argparse.Namespace) -> AppResult:
    repository = _repository_from_args(args)
    try:
        entries = list_curriculum_entries(repository, args.name, args.section)
    except StorageError as exc:
        return AppResult.failed("Entry listing failed.", error=str(exc))
    section_name = _display_section_name(args.section)
    if not entries:
        return AppResult.ok(f"No entries found in section '{section_name}'.")
    lines = [f"Entries for version '{args.name}' section '{section_name}':"]
    for entry in entries:
        lines.append(
            f"- [{entry.index}] pointer={entry.pointer} "
            f"id={entry.entry_id or '-'} type={entry.entry_type or '-'} "
            f"summary={entry.summary or '-'} cvn_codes={', '.join(entry.cvn_codes) or '-'}"
        )
    return AppResult.ok("\n".join(lines))


def _handle_versions_metadata(args: argparse.Namespace) -> AppResult:
    repository = _repository_from_args(args)
    try:
        if args.display_name is not None or args.purpose is not None:
            version = repository.update_version_metadata(
                args.name,
                display_name=args.display_name,
                purpose=args.purpose,
            )
            prefix = f"Updated metadata for derived curriculum version '{version.name}'."
        else:
            version = repository.get_version(args.name)
            prefix = f"Metadata for curriculum version '{version.name}':"
    except StorageError as exc:
        return AppResult.failed("Version metadata update failed.", error=str(exc))
    metadata = version.selection.metadata or {}
    return AppResult.ok(
        "\n".join(
            (
                prefix,
                f"Display name: {metadata.get('display_name', '-')}",
                f"Purpose: {metadata.get('purpose', '-')}",
            )
        )
    )


def _handle_versions_derive(args: argparse.Namespace) -> AppResult:
    repository = _repository_from_args(args)
    try:
        version = repository.create_derived_version(args.name, source=args.source)
    except StorageError as exc:
        return AppResult.failed("Derived version creation failed.", error=str(exc))
    return AppResult.ok(f"Created derived curriculum version '{version.name}' with id {version.id}.")


def _handle_versions_include(args: argparse.Namespace) -> AppResult:
    repository = _repository_from_args(args)
    try:
        version = repository.include_in_version(args.name, args.pointer)
        repository.materialize_version(version.id)
    except StorageError as exc:
        return AppResult.failed("Version include failed.", error=str(exc))
    return AppResult.ok(f"Included {args.pointer} in derived curriculum version '{version.name}'.")


def _handle_versions_exclude(args: argparse.Namespace) -> AppResult:
    repository = _repository_from_args(args)
    try:
        version = repository.exclude_from_version(args.name, args.pointer)
        repository.materialize_version(version.id)
    except StorageError as exc:
        return AppResult.failed("Version exclude failed.", error=str(exc))
    return AppResult.ok(f"Excluded {args.pointer} from derived curriculum version '{version.name}'.")


def _handle_versions_field_edit(args: argparse.Namespace) -> AppResult:
    return AppResult.failed(
        "Field-level edits are not supported in issue #65 MVP.",
        error="Use include/exclude section or entry selection instead.",
    )


def _handle_latex_export(args: argparse.Namespace) -> AppResult:
    repository = _repository_from_args(args)
    try:
        result = export_latex_document(
            repository,
            version=args.version_name,
            output_path=args.output,
        )
    except StorageError as exc:
        return AppResult.failed("LaTeX export failed.", error=str(exc))
    except OSError as exc:
        return AppResult.failed("LaTeX export failed.", error=str(exc))
    return AppResult.ok(
        "\n".join(
            (
                f"Exported LaTeX version '{result.version_name}' to {result.output_path}.",
                f"Validation status: {result.validation_status}",
            )
        )
    )


def _handle_pdf_generate(args: argparse.Namespace) -> AppResult:
    repository = _repository_from_args(args)
    try:
        result = generate_pdf_document(
            repository,
            version=args.version_name,
            output_path=args.output,
            open_pdf=args.open,
        )
    except StorageError as exc:
        return AppResult.failed("PDF generation failed.", error=str(exc))
    except PdfGenerationUnavailable as exc:
        return AppResult.failed("PDF generation unavailable.", error=str(exc))
    except PdfCompilationError as exc:
        return AppResult.failed(
            "PDF generation failed.",
            error="\n".join((str(exc), format_compilation_diagnostics(exc.diagnostics))),
        )
    except PdfPreviewError as exc:
        return AppResult.failed("PDF preview failed.", error=str(exc))
    except OSError as exc:
        return AppResult.failed("PDF generation failed.", error=str(exc))
    lines = [
        f"Generated PDF version '{result.version_name}' to {result.output_path}.",
        f"Validation status: {result.validation_status}",
        f"Compiler: {result.compiler_name}",
    ]
    if result.preview_opened:
        lines.append("Preview handoff: opened")
    return AppResult.ok("\n".join(lines))


def _repository_from_args(args: argparse.Namespace) -> CurriculumRepository:
    config = _config_from_args(args)
    return CurriculumRepository(config.store_path)


def _format_parse_issues(issues: tuple[CvnParseIssue, ...]) -> str:
    if not issues:
        return "-"
    return "\n".join(_format_parse_issue(issue) for issue in issues)


def _format_parse_issue(issue: CvnParseIssue) -> str:
    location = issue.source_location or "-"
    return (
        f"- code={issue.code.value} severity={issue.severity.value} "
        f"path={_format_issue_path(issue.path)} location={location} message={issue.message}"
    )


def _format_issue_path(path: tuple[str, ...]) -> str:
    if not path:
        return "-"
    return "/".join(path)


def _display_section_name(section: str) -> str:
    if section.startswith("/curriculum/"):
        parts = section.split("/")
        if len(parts) == 3:
            return parts[2].replace("~1", "/").replace("~0", "~")
    return section


def _write_canonical_json(path: Path, document: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2)
    path.write_text(f"{payload}\n", encoding="utf-8")
