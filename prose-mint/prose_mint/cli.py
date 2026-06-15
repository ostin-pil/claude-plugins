"""Command-line entrypoint.

Subcommands:
  scan    Scan one file or stdin (port of check-prose.sh)
  bulk    Scan files/directories with a summary (port of check-prose-bulk.sh)
  unwrap  Join hard-wrapped paragraphs (port of unwrap-prose.py)

The `scan` text output and `bulk` output are byte-for-byte compatible with the
source scanners so a migrating project sees identical findings. `--json` is a
new, additive contract.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import REQUIRES_PYTHON, __version__
from .bulk import run_bulk
from .config import load_config
from .engine import analyze
from .formatters import format_json, format_text
from .unwrap import unwrap


def _check_python() -> None:
    if sys.version_info < REQUIRES_PYTHON:
        need = ".".join(str(n) for n in REQUIRES_PYTHON)
        have = ".".join(str(n) for n in sys.version_info[:3])
        print(
            f"prose-mint requires Python {need}+ (found {have}). "
            "The config layer uses stdlib tomllib (3.11+). "
            "Use a newer python3 or pin python3.11 in CI.",
            file=sys.stderr,
        )
        raise SystemExit(3)


def _cmd_scan(args: argparse.Namespace) -> int:
    if args.file:
        try:
            with open(args.file, encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            print(f"no such file: {args.file}: {e}", file=sys.stderr)
            return 2
        label = args.label or args.file
    elif args.stdin:
        content = sys.stdin.read()
        label = args.label or "stdin"
    else:
        print("specify --file <path> or --stdin", file=sys.stderr)
        return 2

    start = Path(args.file) if args.file else Path.cwd()
    config = load_config(
        start_path=start,
        explicit=Path(args.config) if args.config else None,
    )
    analysis = analyze(content, label=label, config=config)
    if args.json:
        print(format_json(analysis))
    else:
        print(format_text(analysis))
    if args.strict and analysis.strict_failed:
        return 1
    return 0


def _cmd_bulk(args: argparse.Namespace) -> int:
    start = Path(args.paths[0]) if args.paths else Path.cwd()
    config = load_config(
        start_path=start,
        explicit=Path(args.config) if args.config else None,
    )
    # CLI --ext overrides config when given; otherwise config's extensions.
    if args.ext is not None:
        extensions = [e.strip().lstrip(".") for e in args.ext.split(",") if e.strip()]
    else:
        extensions = config.extensions
    # Excludes are the union of config scope and CLI flags.
    excludes = list(config.exclude) + list(args.exclude)
    return run_bulk(
        args.paths,
        extensions=extensions,
        excludes=excludes,
        includes=config.include,
        quiet=args.quiet,
        summary_only=args.summary_only,
        strict=args.strict,
        config=config,
    )


def _cmd_unwrap(args: argparse.Namespace) -> int:
    if args.stdin:
        sys.stdout.write(unwrap(sys.stdin.read()))
        return 0
    if not args.file:
        print("specify --file <path> or --stdin", file=sys.stderr)
        return 2
    with open(args.file, encoding="utf-8") as f:
        content = f.read()
    result = unwrap(content)
    if args.dry_run:
        sys.stdout.write(result)
    else:
        with open(args.file, "w", encoding="utf-8") as f:
            f.write(result)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="prose-mint",
        description="Structural-tells linter for AI-flavored prose (v1).",
    )
    p.add_argument("--version", action="version", version=f"prose-mint {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("scan", help="Scan one file or stdin")
    s.add_argument("--file", help="Path to a markdown file")
    s.add_argument("--stdin", action="store_true", help="Read content from stdin")
    s.add_argument("--label", default="", help="Label for the report header")
    s.add_argument("--strict", action="store_true", help="Exit non-zero on any hit")
    s.add_argument("--json", action="store_true", help="Emit structured JSON")
    s.add_argument("--config", help="Path to a .prose-mint.toml (else auto-discovered)")
    s.set_defaults(func=_cmd_scan)

    b = sub.add_parser("bulk", help="Scan files/directories with a summary")
    b.add_argument("paths", nargs="+", help="Files or directories")
    b.add_argument("--strict", action="store_true", help="Exit 1 if any file has hits")
    b.add_argument("--quiet", action="store_true", help="Skip clean files in output")
    b.add_argument("--summary-only", action="store_true", help="Summary table only")
    b.add_argument("--ext", default=None, help="Comma-separated extensions (default: md or config)")
    b.add_argument("--exclude", action="append", default=[], help="Glob to exclude (repeatable)")
    b.add_argument("--config", help="Path to a .prose-mint.toml (else auto-discovered)")
    b.set_defaults(func=_cmd_bulk)

    u = sub.add_parser("unwrap", help="Join hard-wrapped paragraphs")
    u.add_argument("--file", help="Path to a markdown file (rewritten in place)")
    u.add_argument("--stdin", action="store_true", help="Read stdin, write stdout")
    u.add_argument("--dry-run", action="store_true", help="Print result instead of writing")
    u.set_defaults(func=_cmd_unwrap)

    return p


def main(argv: list[str] | None = None) -> int:
    _check_python()
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
