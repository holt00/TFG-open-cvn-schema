from __future__ import annotations

import json
from pathlib import Path

from open_cvn_app.latex import escape_latex, render_latex_document


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "open_cvn"
EXAMPLES_DIR = Path(__file__).parent.parent / "examples" / "open_cvn"


def test_escape_latex_escapes_special_characters():
    assert escape_latex("A&B_#%$ {x} ~ ^ \\") == (
        r"A\&B\_\#\%\$ \{x\} \textasciitilde{} "
        r"\textasciicircum{} \textbackslash{}"
    )


def test_render_latex_document_renders_minimal_document():
    document = json.loads((FIXTURES_DIR / "valid_minimal.json").read_text(encoding="utf-8"))

    rendered = render_latex_document(document, version_name="master")

    assert rendered.startswith("\\documentclass[11pt,a4paper]{article}\n")
    assert "\\section*{Version Metadata}" in rendered
    assert "\\item[Schema version] 0.1.0" in rendered
    assert "\\item[Version] master" in rendered
    assert "\\section*{Research}" not in rendered
    assert rendered.endswith("\n")
    assert not rendered.endswith("\n\n")


def test_render_latex_document_renders_research_entry():
    document = json.loads((EXAMPLES_DIR / "research_entry.json").read_text(encoding="utf-8"))

    rendered = render_latex_document(document, version_name="public")

    assert "\\section*{ Research }" in rendered
    assert "Open CVN data representation" in rendered
    assert "\\item[ID] research-001" in rendered
    assert "\\item[Type] research.publication" in rendered
    assert "\\item[Publication Year] 2026" in rendered
    assert r"UNESCO\_CODES" in rendered


def test_render_latex_document_escapes_identity_values():
    document = json.loads((EXAMPLES_DIR / "identity.json").read_text(encoding="utf-8"))
    document["curriculum"]["identity"]["given_name"] = "Ana & Co_"

    rendered = render_latex_document(document, version_name="master")

    assert "Ana \\& Co\\_" in rendered
