"""Output formatters.

format_text reproduces check-prose.sh stdout byte-for-byte: each emitted
string here corresponds to one print() call in the source scanner, and
"\\n".join(...) reconstructs the stream (print adds the trailing newline that
the CLI re-adds). This exactness is the P0 regression contract.

format_json is a NEW contract (not a preserved behavior); it carries the full
hit list rather than the human report's first-5 truncation because machines
want complete data. It has its own tests, separate from the regression gate.
"""

from __future__ import annotations

import json

from . import __version__
from .engine import Analysis

_HITS_SHOWN = 5


def format_text(analysis: Analysis) -> str:
    """Byte-for-byte equivalent of the source scanner's stdout (sans the
    single trailing newline that print() appends)."""
    out: list[str] = [f"prose-check: {analysis.label}"]
    if analysis.skip_emdash:
        out.append("  (Cyrillic > 30%, skipping em-dash check)")
    if analysis.disabled:
        out.append(f"  (pragma disables: {', '.join(sorted(analysis.disabled))})")

    for cat in analysis.reported_categories:
        # Only non-error categories carry a severity tag, so error-class
        # (structural / hard-wrap / ai-attribution) output stays byte-for-byte
        # identical to the source scanner; the P0 gate depends on that.
        sev = "" if cat.severity == "error" else f" (severity: {cat.severity})"
        if cat.name == "hard-wrap":
            out.append(
                f"\n[hard-wrap] {len(cat.hits)} hit(s) — paragraphs broken "
                "across short lines; let the renderer wrap:"
            )
        else:
            out.append(f"\n[{cat.name}] {len(cat.hits)} hit(s){sev}:")
        for line_no, line in cat.hits[:_HITS_SHOWN]:
            out.append(f"{line_no}:{line.rstrip()[:160]}")

    out.append(f"\ntotal flagged lines: {analysis.total_hits}")
    return "\n".join(out)


def to_payload(analysis: Analysis) -> dict:
    """Structured findings as a dict. Shared by the CLI --json output and the
    MCP server so both speak the identical contract."""
    return {
        "tool": "prose-lint",
        "version": __version__,
        "label": analysis.label,
        "skip_emdash": analysis.skip_emdash,
        "pragma_disabled": sorted(analysis.disabled),
        "total_hits": analysis.total_hits,
        "categories": [
            {
                "name": c.name,
                "count": len(c.hits),
                "threshold": c.threshold,
                "severity": c.severity,
                "suppressed_by": c.suppressed_by,
                "reported": c.reported,
                "hits": [{"line": ln, "text": txt} for ln, txt in c.hits],
            }
            for c in analysis.categories
        ],
    }


def format_json(analysis: Analysis) -> str:
    """Structured findings for machine consumers (CLI --json, MCP server)."""
    return json.dumps(to_payload(analysis), ensure_ascii=False, indent=2)
