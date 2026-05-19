"""MCP server tool bodies. Tested as plain functions (no fastmcp needed) so
this stays part of the zero-dep suite. The FastMCP wiring in main() is a
thin decoration over these and is exercised manually via the inspector.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CORPUS = REPO / "tests" / "fixtures" / "corpus"
sys.path.insert(0, str(REPO))

from prose_lint.engine import analyze  # noqa: E402
from prose_lint.formatters import to_payload  # noqa: E402
from prose_lint.server import scan_files_impl, scan_text_impl  # noqa: E402

STRUCTURAL = (CORPUS / "_edge" / "structural_all.md").read_text(encoding="utf-8")


def test_scan_text_matches_engine_payload():
    out = scan_text_impl(STRUCTURAL, label="x")
    assert out == to_payload(analyze(STRUCTURAL, label="x"))
    assert out["tool"] == "prose-lint"
    assert out["total_hits"] > 0


def test_scan_text_clean():
    out = scan_text_impl((CORPUS / "_edge" / "clean.md").read_text(encoding="utf-8"))
    assert out["total_hits"] == 0


def test_scan_text_honors_explicit_config(tmp_path):
    cfg = tmp_path / ".prose-lint.toml"
    cfg.write_text('[structural]\nenabled = []\n', encoding="utf-8")
    out = scan_text_impl(STRUCTURAL, config_path=str(cfg))
    assert out["total_hits"] == 0  # everything disabled


def test_scan_files_aggregates_and_reports_errors(tmp_path):
    good = tmp_path / "g.md"
    good.write_text("An em dash — here.\n", encoding="utf-8")
    out = scan_files_impl([str(good), str(tmp_path / "missing.md")])
    assert out["summary"]["scanned"] == 2
    assert out["summary"]["with_hits"] == 1
    assert out["summary"]["total_hits"] >= 1
    err = next(f for f in out["files"] if f.get("label") == str(tmp_path / "missing.md"))
    assert "error" in err


def test_scan_files_discovers_per_file_config(tmp_path):
    (tmp_path / ".prose-lint.toml").write_text(
        '[structural]\nenabled = []\n', encoding="utf-8"
    )
    doc = tmp_path / "d.md"
    doc.write_text("An em dash — here.\n", encoding="utf-8")
    out = scan_files_impl([str(doc)])
    assert out["summary"]["total_hits"] == 0  # discovered config disables all
