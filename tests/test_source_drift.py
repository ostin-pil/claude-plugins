"""Drift guard against the upstream source scanner.

While Untype/Bounce remains the canonical rule (until P1b makes prose-lint
the source), its bin/check-prose.sh can gain a category and prose-lint
silently falls behind. That already happened once: `ai-attribution` landed
in Untype on 2026-05-18 and went unnoticed here for days.

This test parses the upstream scanner's category slugs and asserts they
match prose-lint's. The scanner is the precise drift vector (the prose-style
prose is illustrative, not an exhaustive machine list), so guarding against
it is what would have caught d0a1cb7 the day it merged.

It is skipped, not failed, when the Untype checkout is absent, so prose-lint
CI on a machine without it stays green. On the dev machine it is a real gate.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from prose_lint.rules_default import ALL_CATEGORIES  # noqa: E402

UPSTREAM = Path(
    os.environ.get("UNTYPE_REPO", "/Users/costa/Projects/Untype")
) / "bin" / "check-prose.sh"

# First tuple element of each PATTERNS entry: ("slug", re.compile(...
# Slugs include uppercase (not-X-but-Y, no-X-no-Y-just-Z, this-isnt-about-X).
_PATTERN_SLUG = re.compile(r'^\s*\(\s*"([A-Za-z0-9-]+)"\s*,\s*re\.compile', re.M)


def _upstream_categories() -> set[str]:
    src = UPSTREAM.read_text(encoding="utf-8")
    slugs = set(_PATTERN_SLUG.findall(src))
    # hard-wrap is handled outside PATTERNS in the source (find_hard_wraps),
    # gated on the literal "hard-wrap" disable key. Mirror that here.
    assert 'find_hard_wraps' in src and '"hard-wrap"' in src, (
        "upstream scanner shape changed; revisit this guard"
    )
    slugs.add("hard-wrap")
    return slugs


@pytest.mark.skipif(not UPSTREAM.exists(), reason=f"no upstream scanner at {UPSTREAM}")
def test_categories_match_upstream_scanner():
    upstream = _upstream_categories()
    ours = set(ALL_CATEGORIES)
    missing = upstream - ours          # source added one; we must port it
    extra = ours - upstream            # we have one the source dropped
    assert not missing and not extra, (
        f"drifted from {UPSTREAM}\n"
        f"  add to prose-lint default: {sorted(missing) or 'none'}\n"
        f"  no longer in source:       {sorted(extra) or 'none'}"
    )
