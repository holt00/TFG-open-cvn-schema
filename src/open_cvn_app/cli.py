from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from open_cvn_app import __version__
from open_cvn_app.config import OpenCvnAppConfig
from open_cvn_app.results import AppResult
from open_cvn_app.storage import SCHEMA_VERSION, CurriculumRepository, StorageError, initialize_store


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
    return _planned_result("Open CVN JSON import", "#64", args)


def _handle_json_export(args: argparse.Namespace) -> AppResult:
    return _planned_result("Open CVN JSON export", "#64", args)


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
    except StorageError as exc:
        return AppResult.failed("Version include failed.", error=str(exc))
    return AppResult.ok(f"Included {args.pointer} in derived curriculum version '{version.name}'.")


def _handle_versions_exclude(args: argparse.Namespace) -> AppResult:
    repository = _repository_from_args(args)
    try:
        version = repository.exclude_from_version(args.name, args.pointer)
    except StorageError as exc:
        return AppResult.failed("Version exclude failed.", error=str(exc))
    return AppResult.ok(f"Excluded {args.pointer} from derived curriculum version '{version.name}'.")


def _handle_latex_export(args: argparse.Namespace) -> AppResult:
    return _planned_result("LaTeX export", "#66", args)


def _handle_pdf_generate(args: argparse.Namespace) -> AppResult:
    return _planned_result("PDF generation", "#67", args)


def _repository_from_args(args: argparse.Namespace) -> CurriculumRepository:
    config = _config_from_args(args)
    return CurriculumRepository(config.store_path)
