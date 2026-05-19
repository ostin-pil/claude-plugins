"""The canonical default ruleset, as data.

This is the single source of truth for v1 defaults. Applying it must
reproduce the original Untype scanner exactly, so the values here
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
        # honored by the engine regardless of this list. "banlist" is also
        # accepted when the banlist is enabled.
        "categories": list(ALL_CATEGORIES) + ["banlist"],
    },
    # v2 mechanized banlist. The default content is shipped so opting in is
    # one line (`[banlist] enabled = true`), but it is OFF by default: the
    # word sense ("navigate" the verb vs the figurative tell) cannot be
    # disambiguated mechanically, so it is advisory and false-positive-prone.
    # Default severity is "warn" (reported, never fails --strict); a project
    # can set "error" to enforce. Matching skips inline code spans and
    # blockquote lines, and honors the skip-banlist pragma.
    "banlist": {
        "enabled": False,
        "severity": "warn",
        "context_suppress": ["code-span", "blockquote", "pragma"],
        # Single tokens, matched whole-word and case-insensitively. The
        # parenthetical sense from prose-style.md ("robust (as praise)") is
        # not enforceable mechanically; that is the reason for warn + opt-in.
        "words": [
            "delve", "navigate", "underscore", "bolster", "foster",
            "harness", "leverage", "unpack", "pivotal", "groundbreaking",
            "cutting-edge", "transformative", "game-changing", "innovative",
            "robust", "comprehensive", "seamless", "intricate", "nuanced",
            "vibrant", "multifaceted", "holistic", "testament", "landscape",
            "realm",
        ],
        "words_remove": [],
        # Regex fragments, case-insensitive, matched per line after inline
        # code is blanked. <...> placeholders are written as \S+ here.
        "phrases": [
            r"\bdive into\b",
            r"\bshed light on\b",
            r"\bpave the way\b",
            r"In today's \S+ world",
            r"\bIt's important to note\b",
            r"\bWhen it comes to\b",
            r"\bAt its core\b",
            r"\bAt the end of the day\b",
            r"\bLet's break it down\b",
            r"\bThis is where \S+(?: \S+)? comes in\b",
            r"\bplays a crucial role in\b",
            r"\bcannot be overstated\b",
        ],
    },
}
