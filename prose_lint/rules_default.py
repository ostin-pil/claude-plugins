"""The canonical default ruleset, as data.

This is the single source of truth for v1 defaults. Applying it must
reproduce the original Untype/Bounce scanner exactly, so the values here
mirror engine.PATTERNS thresholds and the source's Cyrillic exemption. A
project's .prose-lint.toml extends or relaxes this; it never has to restate
the whole thing.

The regex patterns themselves stay in engine.py (they are code, not config).
This module owns the *policy* knobs: which categories are enabled, their
thresholds, the Cyrillic toggle, the pragma vocabulary, bulk scope, and the
v2-reserved banlist block (parsed but inert in v1).
"""

from __future__ import annotations

# Category slugs the engine implements. Kept here so the drift test can assert
# the ruleset and the engine never diverge without a checked-in change.
STRUCTURAL_CATEGORIES = [
    "em-dash",
    "ascii-arrow",
    "not-X-but-Y",
    "no-X-no-Y-just-Z",
    "this-isnt-about-X",
    "not-only-but",
    "bold-colon-opener",
    "ai-attribution",
]
HARD_WRAP = "hard-wrap"
ALL_CATEGORIES = STRUCTURAL_CATEGORIES + [HARD_WRAP]

DEFAULT_RULESET = {
    "scope": {
        # Empty include/exclude == "scan whatever paths are given", which is
        # exactly today's bulk behavior. A project narrows this in its own file.
        "include": [],
        "exclude": [],
        "extensions": ["md"],
    },
    "structural": {
        "enabled": list(ALL_CATEGORIES),
        # Only non-1 thresholds need stating; engine defaults fill the rest.
        "thresholds": {
            "bold-colon-opener": 5,
            "hard-wrap": 2,
        },
    },
    "language": {
        "cyrillic_em_dash_exempt": True,
    },
    "pragma": {
        # Names accepted in <!-- prose-check: skip ... -->. "all" is always
        # honored by the engine regardless of this list.
        "categories": list(ALL_CATEGORIES),
    },
    # v2. Present so projects can stage overrides early; inert in v1 (the CLI
    # prints a one-line notice if a project populates it).
    "banlist": {
        "words": [],
        "words_remove": [],
        "phrases": [],
        "severity": "warn",
        "context_suppress": ["code-span", "blockquote", "pragma"],
    },
}
