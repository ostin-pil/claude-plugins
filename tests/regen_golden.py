"""Regenerate the golden corpus from the LIVE Untype scanners.

Golden = source-of-truth behavior. We capture the exact stdout of the
original bin/check-prose.sh and bin/check-prose-bulk.sh so the regression
test can assert the ported engine reproduces it byte-for-byte.

Run from the prose-lint repo root:
    python3 tests/regen_golden.py

This is intentionally a manual, checked-in step (not a fixture factory the
test calls), so the golden files are a frozen artifact reviewed in git.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import os

REPO = Path(__file__).resolve().parent.parent
CORPUS = REPO / "tests" / "fixtures" / "corpus"
GOLDEN = REPO / "tests" / "fixtures" / "golden"
# Upstream source repo (Untype; was the "Untype" folder, renamed 2026-05).
LIVE = Path(os.environ.get("UNTYPE_REPO", "/Users/costa/Projects/Untype")) / "bin"
SCANNER = LIVE / "check-prose.sh"
BULK = LIVE / "check-prose-bulk.sh"

# Bulk invocations exercised. Keys become golden/_bulk/<key>.txt. Paths are
# relative to REPO so the recorded labels are stable across machines.
BULK_VARIANTS = {
    "default": ["tests/fixtures/corpus"],
    "summary_only": ["--summary-only", "tests/fixtures/corpus"],
    "quiet": ["--quiet", "tests/fixtures/corpus"],
    "exclude_archive": ["--exclude", "*/archive/*", "tests/fixtures/corpus"],
}


def corpus_files() -> list[Path]:
    return sorted(CORPUS.rglob("*.md"))


def regen_per_file() -> int:
    n = 0
    for f in corpus_files():
        rel = f.relative_to(CORPUS).as_posix()
        content = f.read_text(encoding="utf-8")
        res = subprocess.run(
            [str(SCANNER), "--stdin", "--label", rel],
            input=content,
            capture_output=True,
            text=True,
        )
        if res.returncode not in (0, 1):
            print(f"!! scanner failed on {rel}: {res.stderr}", file=sys.stderr)
            return 1
        dst = GOLDEN / "per_file" / (rel + ".txt")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(res.stdout, encoding="utf-8")
        n += 1
    print(f"wrote {n} per-file golden files")
    return 0


def regen_bulk() -> int:
    for key, args in BULK_VARIANTS.items():
        res = subprocess.run(
            [str(BULK), *args],
            cwd=str(REPO),
            capture_output=True,
            text=True,
        )
        dst = GOLDEN / "_bulk" / (key + ".txt")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(res.stdout, encoding="utf-8")
    print(f"wrote {len(BULK_VARIANTS)} bulk golden files")
    return 0


def main() -> int:
    if not SCANNER.exists():
        print(f"live scanner not found at {SCANNER}", file=sys.stderr)
        return 2
    GOLDEN.mkdir(parents=True, exist_ok=True)
    return regen_per_file() or regen_bulk()


if __name__ == "__main__":
    sys.exit(main())
