"""Bulk scan over files/directories. Port of check-prose-bulk.sh.

Runs the scanner in-process (not as a subprocess) but the emitted stream is
byte-for-byte identical: per-file blocks use format_text (== scanner stdout
rstripped) and the summary table reproduces the source wrapper exactly.
"""

from __future__ import annotations

import fnmatch
import sys
from pathlib import Path

from .config import Config, default_config
from .engine import analyze
from .formatters import format_text


def collect_files(
    paths: list[str],
    extensions: list[str],
    excludes: list[str],
    includes: list[str] | None = None,
) -> list[Path]:
    """Expand paths to a deduplicated, ordered list of files.

    Empty `excludes`/`includes` mean no filtering, which is the original
    bulk behavior the P0 gate pins.
    """
    files: list[Path] = []
    for p in paths:
        path = Path(p)
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            for ext in extensions:
                files.extend(sorted(path.rglob(f"*.{ext}")))
        else:
            print(f"warning: {p} not found", file=sys.stderr)
    if includes:
        files = [f for f in files if any(fnmatch.fnmatch(str(f), pat) for pat in includes)]
    if excludes:
        files = [f for f in files if not any(fnmatch.fnmatch(str(f), pat) for pat in excludes)]
    seen: set[str] = set()
    out: list[Path] = []
    for f in files:
        key = str(f.resolve())
        if key not in seen:
            seen.add(key)
            out.append(f)
    return out


def run_bulk(
    paths: list[str],
    *,
    extensions: list[str],
    excludes: list[str],
    quiet: bool,
    summary_only: bool,
    strict: bool,
    includes: list[str] | None = None,
    config: Config | None = None,
) -> int:
    if config is None:
        config = default_config()
    files = collect_files(paths, extensions, excludes, includes)
    if not files:
        print("no files matched", file=sys.stderr)
        return 0

    results: list[tuple[Path, int]] = []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
        except OSError:
            results.append((f, 0))
            continue
        analysis = analyze(content, label=str(f), config=config)
        total = analysis.total_hits
        results.append((f, total))
        if summary_only:
            continue
        if quiet and total == 0:
            continue
        print(format_text(analysis).rstrip())
        print()

    total_hits = sum(t for _, t in results)
    files_with_hits = sum(1 for _, t in results if t > 0)
    worst = sorted(results, key=lambda r: -r[1])

    print("=" * 64)
    print(
        f"scanned {len(files)} file(s); {files_with_hits} with hits; "
        f"{total_hits} total flagged lines"
    )
    if files_with_hits > 0:
        print("\ntop offenders:")
        for f, t in worst:
            if t == 0:
                break
            print(f"  {t:6d}  {f}")

    if strict and total_hits > 0:
        return 1
    return 0
