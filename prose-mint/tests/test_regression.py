"""P0 regression gate: the ported engine must reproduce the LIVE scanner's
text output byte-for-byte across the frozen corpus.

Golden files in tests/fixtures/golden/ were captured from Untype's
bin/check-prose.sh and bin/check-prose-bulk.sh (see regen_golden.py). If a
change here makes a test fail, the engine has drifted from source behavior.
"""

from __future__ import annotations

import io
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
CORPUS = REPO / "tests" / "fixtures" / "corpus"
GOLDEN = REPO / "tests" / "fixtures" / "golden"

sys.path.insert(0, str(REPO))
from prose_mint.cli import main as cli_main  # noqa: E402


def _per_file_cases() -> list[tuple[str, Path, Path]]:
    cases = []
    for golden in sorted((GOLDEN / "per_file").rglob("*.txt")):
        rel = golden.relative_to(GOLDEN / "per_file")
        src_rel = rel.with_suffix("")  # strip the .txt we appended
        src = CORPUS / src_rel
        cases.append((src_rel.as_posix(), src, golden))
    return cases


PER_FILE = _per_file_cases()


def test_corpus_is_present():
    assert len(PER_FILE) > 90, "frozen corpus shrank unexpectedly"


@pytest.mark.parametrize("label,src,golden", PER_FILE, ids=[c[0] for c in PER_FILE])
def test_scan_matches_live_scanner(label, src, golden):
    content = src.read_text(encoding="utf-8")
    expected = golden.read_text(encoding="utf-8")

    buf = io.StringIO()
    real_stdin = sys.stdin
    sys.stdin = io.StringIO(content)
    try:
        with redirect_stdout(buf):
            # --no-config pins the built-in default ruleset: the golden was
            # captured from the config-less source scanner, so an ambient
            # .prose-mint.toml above cwd (e.g. the monorepo's) must not apply.
            rc = cli_main(["scan", "--stdin", "--no-config", "--label", label])
    finally:
        sys.stdin = real_stdin

    assert rc == 0
    assert buf.getvalue() == expected, f"engine drifted from source on {label}"


@pytest.mark.parametrize(
    "key,args",
    [
        ("default", ["tests/fixtures/corpus"]),
        ("summary_only", ["--summary-only", "tests/fixtures/corpus"]),
        ("quiet", ["--quiet", "tests/fixtures/corpus"]),
        ("exclude_archive", ["--exclude", "*/archive/*", "tests/fixtures/corpus"]),
    ],
)
def test_bulk_matches_live_wrapper(key, args):
    expected = (GOLDEN / "_bulk" / f"{key}.txt").read_text(encoding="utf-8")
    res = subprocess.run(
        [sys.executable, str(REPO / "bin" / "prose-mint"), "bulk", "--no-config", *args],
        cwd=str(REPO),
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, res.stderr
    assert res.stdout == expected, f"bulk drifted from source for variant {key}"


def test_strict_exit_code_on_hits():
    res = subprocess.run(
        [sys.executable, str(REPO / "bin" / "prose-mint"),
         "scan", "--file", str(CORPUS / "_edge" / "structural_all.md"),
         "--no-config", "--strict"],
        capture_output=True, text=True,
    )
    assert res.returncode == 1


def test_strict_exit_code_clean():
    res = subprocess.run(
        [sys.executable, str(REPO / "bin" / "prose-mint"),
         "scan", "--file", str(CORPUS / "_edge" / "clean.md"),
         "--no-config", "--strict"],
        capture_output=True, text=True,
    )
    assert res.returncode == 0
