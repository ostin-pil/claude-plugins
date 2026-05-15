"""--json is a NEW contract, not a preserved behavior. It gets its own tests,
deliberately separate from the byte-for-byte regression gate.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CORPUS = REPO / "tests" / "fixtures" / "corpus"
sys.path.insert(0, str(REPO))

from prose_lint.engine import analyze  # noqa: E402
from prose_lint.formatters import format_json  # noqa: E402


def test_json_is_valid_and_consistent():
    content = (CORPUS / "_edge" / "structural_all.md").read_text(encoding="utf-8")
    a = analyze(content, label="_edge/structural_all.md")
    payload = json.loads(format_json(a))

    assert payload["tool"] == "prose-lint"
    assert payload["label"] == "_edge/structural_all.md"
    assert payload["total_hits"] == a.total_hits

    reported = [c for c in payload["categories"] if c["reported"]]
    assert sum(c["count"] for c in reported) == payload["total_hits"]
    # Every category appears (including suppressed/below-threshold ones).
    names = {c["name"] for c in payload["categories"]}
    assert "hard-wrap" in names and "em-dash" in names


def test_json_carries_full_hits_not_truncated():
    content = (CORPUS / "_edge" / "structural_all.md").read_text(encoding="utf-8")
    a = analyze(content)
    payload = json.loads(format_json(a))
    bold = next(c for c in payload["categories"] if c["name"] == "bold-colon-opener")
    # Human report truncates to 5; JSON keeps the full list.
    assert bold["count"] == len(bold["hits"]) == 5


def test_json_records_cyrillic_suppression():
    content = (CORPUS / "_edge" / "russian_emdash.md").read_text(encoding="utf-8")
    a = analyze(content)
    payload = json.loads(format_json(a))
    assert payload["skip_emdash"] is True
    em = next(c for c in payload["categories"] if c["name"] == "em-dash")
    assert em["suppressed_by"] == "cyrillic"
    assert em["reported"] is False
