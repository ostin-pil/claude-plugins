"""Join hard-wrapped paragraphs in markdown. Verbatim port of Untype
bin/unwrap-prose.py; only the file/stdin plumbing moved to cli.py.

Markdown renderers handle word-wrap. Hard line breaks inside a paragraph
produce unnaturally narrow text on wide screens (GitHub PR bodies, READMEs,
issue comments). unwrap() joins consecutive prose lines into one
soft-wrapped paragraph per blank-line-terminated block, and joins
continuation lines under list items.

Skips: fenced code, indented code (4+ leading spaces or tab), headers,
blockquotes, table rows, HTML blocks, and any paragraph that already
contains a very long line (>200 chars), which signals a deliberate break.
"""

from __future__ import annotations

import re

LIST_RE = re.compile(r"^(\s*)([-*+]|\d+\.)\s+(.*)$")
HEADER_RE = re.compile(r"^#{1,6}\s")
FENCE_RE = re.compile(r"^\s*```")
TABLE_RE = re.compile(r"^\s*\|")
QUOTE_RE = re.compile(r"^>")
HTML_RE = re.compile(r"^<[a-zA-Z!/]")
SETEXT_UNDERLINE_RE = re.compile(r"^(=+|-+)\s*$")


def classify(line: str) -> str:
    if not line.strip():
        return "blank"
    if FENCE_RE.match(line):
        return "fence"
    if HEADER_RE.match(line):
        return "header"
    if LIST_RE.match(line):
        return "list"
    if QUOTE_RE.match(line):
        return "quote"
    if TABLE_RE.match(line):
        return "table"
    if HTML_RE.match(line):
        return "html"
    if SETEXT_UNDERLINE_RE.match(line):
        return "setext"
    # 4+ leading spaces or tab is indented code.
    if line.startswith("    ") or line.startswith("\t"):
        return "code_indent"
    # 1-3 leading spaces with content = continuation of whatever came before.
    if line[:1] == " ":
        return "continuation"
    return "prose"


def unwrap(content: str) -> str:
    lines = content.split("\n")
    out: list[str] = []
    in_fence = False
    buf: list[str] = []
    buf_kind = None  # "prose" or "list" or None

    def flush():
        nonlocal buf, buf_kind
        if not buf:
            return
        if any(len(s) > 200 for s in buf):
            out.extend(buf)
        else:
            # Preserve the leading whitespace of the first line (matters for
            # nested list items). Strip continuations to collapse them.
            first = buf[0].rstrip()
            rest = [s.strip() for s in buf[1:]]
            joined = " ".join([first] + rest) if rest else first
            out.append(joined)
        buf = []
        buf_kind = None

    for line in lines:
        if FENCE_RE.match(line):
            flush()
            out.append(line)
            in_fence = not in_fence
            continue
        if in_fence:
            flush()
            out.append(line)
            continue
        kind = classify(line)
        if kind == "blank":
            flush()
            out.append(line)
        elif kind == "prose":
            if buf_kind == "list":
                flush()
            buf.append(line)
            buf_kind = "prose"
        elif kind == "list":
            flush()
            buf.append(line)
            buf_kind = "list"
        elif kind == "continuation":
            if buf_kind in ("list", "prose", "indented"):
                buf.append(line)
            else:
                buf.append(line)
                buf_kind = "indented"
        else:
            flush()
            out.append(line)
    flush()
    return "\n".join(out)
