from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from open_cvn_app import __version__
from open_cvn_app.config import OpenCvnAppConfig
from open_cvn_app.results import AppResult


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
    return _planned_result("Store initialization", "#62", args)


def _handle_json_import(args: argparse.Namespace) -> AppResult:
    return _planned_result("Open CVN JSON import", "#64", args)


def _handle_json_export(args: argparse.Namespace) -> AppResult:
    return _planned_result("Open CVN JSON export", "#64", args)


def _handle_versions_list(args: argparse.Namespace) -> AppResult:
    return _planned_result("Version listing", "#63", args)


def _handle_versions_derive(args: argparse.Namespace) -> AppResult:
    return _planned_result("Derived version creation", "#63", args)


def _handle_latex_export(args: argparse.Namespace) -> AppResult:
    return _planned_result("LaTeX export", "#66", args)


def _handle_pdf_generate(args: argparse.Namespace) -> AppResult:
    return _planned_result("PDF generation", "#67", args)
