"""Core scanner. Detection logic is a verbatim port of Untype's
bin/check-prose.sh; only the structure changed (analyze() returns data,
formatting moved to formatters.py) so the same findings can drive text,
JSON, and the MCP/bulk surfaces without behavioral drift.

The v1 ruleset is hard-coded here to match the source scanner exactly. P1
introduces a config layer that injects enabled categories / thresholds; the
seams (DEFAULT_PATTERNS, threshold lookups) are kept obvious for that.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config import Config

# (name, compiled pattern, threshold, is_emdash)
PATTERNS = [
    ("em-dash", re.compile(r"—"), 1, True),
    ("ascii-arrow", re.compile(r"→"), 1, False),
    # Synced with Untype fix/prose-phrase-rule-patterns (2026-08-08): the comma
    # form is the canonical rendering; the "but" arm was dropped after its only
    # detection across 366 measured files was a false positive on natural
    # comparative speech (ketin evaluations/2026-08-07).
    ("not-X-but-Y", re.compile(r"\bIt'?s not\b[^.!?\n]{1,60}[,—]\s*(?:it'?s|rather)\b", re.I), 1, False),
    # Sentence-case, any position; fragment bounds keep it a slogan detector.
    ("no-X-no-Y-just-Z", re.compile(r"\bNo [^.!?\n]{1,40}[.!?] No [^.!?\n]{1,40}[.!?] Just \S"), 1, False),
    ("this-isnt-about-X", re.compile(r"\bThis isn'?t about\b", re.I), 1, False),
    ("not-only-but", re.compile(r"\bNot only\b.*\bbut\b", re.I), 1, False),
    ("bold-colon-opener", re.compile(r"^\*\*[^*]+\*\*\s*[—:]\s+\S", re.M), 5, False),
    # Ported from Untype d0a1cb7 (2026-05-18): the harness-default
    # "Generated with Claude Code" / robot-emoji footer and Co-Authored-By
    # trailers. A universal AI-tell, so it lives in the shared default.
    ("ai-attribution", re.compile(r"🤖|Generated with \[?Claude Code|Co-Authored-By", re.I), 1, False),
]

HARD_WRAP_THRESHOLD = 2

# Lines that aren't prose continuations: anything matching these starts a new
# block, so a following line isn't a hard-wrap continuation of it. Allow
# leading whitespace so nested list items still count as list, not prose.
_NON_PROSE_PREFIX = re.compile(r"^\s*(?:#{1,6}\s|[-*+]\s|\d+\.\s|>|\||```|<)")

PRAGMA_RE = re.compile(r"<!--\s*prose-check:\s*skip\s+([\w\-,\s]+)-->", re.I)


def find_hard_wraps(content: str, min_len: int = 50, max_len: int = 95) -> list[tuple[int, str]]:
    """Detect hard-wrapped paragraphs.

    Markdown renderers handle word-wrap; hard breaks inside a paragraph
    show up as unnaturally short consecutive prose lines. Flags the
    second line of any pair where both are in the [50, 95] char range
    and both look like prose (not headers, lists, tables, code, etc.).
    """
    lines = content.split("\n")
    hits = []
    prev_was_short_prose = False
    in_fence = False
    for i, line in enumerate(lines, start=1):
        if line.startswith("```"):
            in_fence = not in_fence
            prev_was_short_prose = False
            continue
        if in_fence:
            prev_was_short_prose = False
            continue
        stripped = line.strip()
        is_prose = (
            bool(stripped)
            and not _NON_PROSE_PREFIX.match(line)
            and min_len <= len(line) <= max_len
        )
        if is_prose and prev_was_short_prose:
            hits.append((i, line))
        prev_was_short_prose = is_prose
    return hits


def parse_pragma(content: str) -> set[str]:
    """Return set of category names disabled by a top-of-file pragma.

    Looks at the first 5 non-empty lines for:
      <!-- prose-check: skip <cat>[, <cat>]* -->
    Use category names from PATTERNS (e.g. "bold-colon-opener", "em-dash")
    or "all" to disable every check.
    """
    head = [line for line in content.splitlines()[:10] if line.strip()][:5]
    for line in head:
        m = PRAGMA_RE.search(line)
        if m:
            cats = {c.strip().lower() for c in m.group(1).replace(",", " ").split() if c.strip()}
            return cats
    return set()


def cyrillic_skip(content: str) -> bool:
    """Return True if Cyrillic chars exceed 30% of alpha chars."""
    alpha = sum(1 for c in content if c.isascii() and c.isalpha())
    cyr = sum(1 for c in content if "Ѐ" <= c <= "ӿ")
    total = alpha + cyr
    return total > 0 and (cyr * 100 // total) > 30


def strip_fenced_code(content: str) -> str:
    """Replace lines inside ``` fences with blank lines (preserves line numbers)."""
    out = []
    in_fence = False
    for line in content.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else line)
    return "\n".join(out)


def find_hits(content: str, pattern: re.Pattern) -> list[tuple[int, str]]:
    """Return list of (line_number, line_text) for pattern matches."""
    hits = []
    if pattern.flags & re.M:
        # Multiline-anchored patterns: search whole content, report matched line.
        for m in pattern.finditer(content):
            line_no = content.count("\n", 0, m.start()) + 1
            line_text = content.splitlines()[line_no - 1] if line_no <= content.count("\n") + 1 else ""
            hits.append((line_no, line_text))
    else:
        for i, line in enumerate(content.splitlines(), start=1):
            if pattern.search(line):
                hits.append((i, line))
    return hits


_INLINE_CODE = re.compile(r"`[^`]*`")
_BLOCKQUOTE = re.compile(r"^\s*>")


def _banlist_regexes(words: list[str], phrases: list[str]):
    """Compile the word and phrase matchers. Words are whole-word and
    case-insensitive; phrases are already regex fragments (placeholders
    written as \\S+ in the ruleset)."""
    word_re = None
    if words:
        word_re = re.compile(
            r"\b(?:" + "|".join(re.escape(w) for w in words) + r")\b", re.I
        )
    phrase_re = re.compile("(?:" + "|".join(phrases) + ")", re.I) if phrases else None
    return word_re, phrase_re


def find_banlist_hits(content, word_re, phrase_re, context_suppress) -> list[tuple[int, str]]:
    """Per-line banned word/phrase matches on the fenced-code-stripped
    content. Inline code spans and blockquote lines are skipped when
    context_suppress asks for it."""
    drop_blockquote = "blockquote" in context_suppress
    blank_code = "code-span" in context_suppress
    hits = []
    for i, line in enumerate(content.splitlines(), start=1):
        if drop_blockquote and _BLOCKQUOTE.match(line):
            continue
        probe = _INLINE_CODE.sub(lambda m: " " * len(m.group()), line) if blank_code else line
        if (word_re and word_re.search(probe)) or (phrase_re and phrase_re.search(probe)):
            hits.append((i, line))
    return hits


@dataclass
class CategoryResult:
    name: str
    hits: list[tuple[int, str]]
    threshold: int
    # None means reported; otherwise "cyrillic", "pragma", "config",
    # or "below-threshold"
    suppressed_by: str | None
    # "error" categories fail --strict; "warn" categories only report.
    severity: str = "error"

    @property
    def reported(self) -> bool:
        return self.suppressed_by is None


@dataclass
class Analysis:
    label: str
    skip_emdash: bool
    disabled: set[str]
    categories: list[CategoryResult] = field(default_factory=list)

    @property
    def reported_categories(self) -> list[CategoryResult]:
        return [c for c in self.categories if c.reported]

    @property
    def total_hits(self) -> int:
        return sum(len(c.hits) for c in self.reported_categories)

    @property
    def strict_failed(self) -> bool:
        """True if any reported error-severity category has hits. Warn
        categories (the banlist by default) report but never fail --strict."""
        return any(
            c.severity == "error" and c.hits for c in self.reported_categories
        )


def analyze(content: str, label: str = "stdin", config: "Config | None" = None) -> Analysis:
    """Run every category against content and return structured results.

    Mirrors check-prose.sh main() exactly: pragma + Cyrillic detection on the
    raw content, then code fences stripped before pattern and hard-wrap scans.
    Suppression precedence is config-disabled, then Cyrillic em-dash skip,
    then pragma, then threshold. With the default config (every category
    enabled, source thresholds, Cyrillic exemption on) this is byte-for-byte
    the original scanner; the P0 regression gate enforces that.
    """
    if config is None:
        from .config import default_config

        config = default_config()

    cyrillic = cyrillic_skip(content)
    skip_emdash = cyrillic and config.cyrillic_em_dash_exempt
    disabled = parse_pragma(content)
    scanned = strip_fenced_code(content)

    categories: list[CategoryResult] = []
    for name, pat, builtin_threshold, is_emdash in PATTERNS:
        threshold = config.threshold_for(name, builtin_threshold)
        hits = find_hits(scanned, pat)
        if name not in config.enabled:
            suppressed = "config"
        elif is_emdash and skip_emdash:
            suppressed = "cyrillic"
        elif "all" in disabled or name.lower() in disabled:
            suppressed = "pragma"
        elif len(hits) < threshold:
            suppressed = "below-threshold"
        else:
            suppressed = None
        categories.append(CategoryResult(name, hits, threshold, suppressed))

    wrap_threshold = config.threshold_for("hard-wrap", HARD_WRAP_THRESHOLD)
    wrap_hits = find_hard_wraps(scanned)
    if "hard-wrap" not in config.enabled:
        wrap_suppressed = "config"
    elif "all" in disabled or "hard-wrap" in disabled:
        wrap_suppressed = "pragma"
    elif len(wrap_hits) < wrap_threshold:
        wrap_suppressed = "below-threshold"
    else:
        wrap_suppressed = None
    categories.append(
        CategoryResult("hard-wrap", wrap_hits, wrap_threshold, wrap_suppressed)
    )

    # Banlist is opt-in (config.banlist.enabled). When off it is not even a
    # category, so default output stays byte-identical to the source scanner
    # and the P0 regression gate is unaffected.
    if config.banlist_enabled:
        word_re, phrase_re = _banlist_regexes(
            config.banlist_words, config.banlist_phrases
        )
        bl_hits = find_banlist_hits(
            scanned, word_re, phrase_re, config.banlist_context_suppress
        )
        if "all" in disabled or "banlist" in disabled:
            bl_suppressed = "pragma"
        elif len(bl_hits) < 1:
            bl_suppressed = "below-threshold"
        else:
            bl_suppressed = None
        categories.append(
            CategoryResult(
                "banlist", bl_hits, 1, bl_suppressed,
                severity=config.banlist_severity,
            )
        )

    return Analysis(
        label=label,
        skip_emdash=skip_emdash,
        disabled=disabled,
        categories=categories,
    )
