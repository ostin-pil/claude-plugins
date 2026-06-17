#!/usr/bin/env python3
"""Render Claude Code session transcripts to a scrubbed, browsable Markdown archive.

Reads JSONL transcripts from ~/.claude/projects/<slug>/*.jsonl and emits one
Markdown file per session plus an index, after a mandatory secret-scrub pass.
The scrub runs on the rendered text before a single byte is written, so nothing
that leaves this script (and therefore nothing a destination sync ships) carries
a live credential. After rendering, the output tree is re-scanned for any
high-confidence secret that slipped through; if one is found the script exits
non-zero so the caller can refuse to sync. Stdlib only; no third-party deps.

This script never syncs anywhere. The session-archive skill owns the rsync/git/
Drive step and runs it only when this script exits 0 and the report is reviewed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

# Bump when SCRUB_RULES change so the incremental state invalidates and every
# session is re-scrubbed with the new rules (otherwise an unchanged transcript
# keeps its old, possibly-leaky rendering). See main().
SCRUB_VERSION = 2

# --- Secret scrub --------------------------------------------------------------
# Ordered list of (name, compiled-pattern, replacement). Applied to the fully
# rendered Markdown of each session. Over-redaction is acceptable; a missed
# secret is not. More specific patterns precede the generic ones they overlap.
SCRUB_RULES = [
    ("anthropic_key", re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}"), "[REDACTED:ANTHROPIC_KEY]"),
    ("openai_key", re.compile(r"sk-(?:proj-|svcacct-|admin-)?[A-Za-z0-9_\-]{20,}"), "[REDACTED:OPENAI_KEY]"),
    ("aws_access_key_id", re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[REDACTED:AWS_ACCESS_KEY_ID]"),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"), "[REDACTED:GITHUB_TOKEN]"),
    ("slack_token", re.compile(r"\bxox[baprse]-[A-Za-z0-9-]{10,}|\bxapp-[A-Za-z0-9-]{10,}"), "[REDACTED:SLACK_TOKEN]"),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b"), "[REDACTED:GOOGLE_API_KEY]"),
    ("stripe_key", re.compile(r"\bsk_live_[A-Za-z0-9]{20,}\b"), "[REDACTED:STRIPE_KEY]"),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+"), "[REDACTED:JWT]"),
    ("bearer", re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._\-+/]{20,}=*"), r"\1[REDACTED:TOKEN]"),
    # Credentials embedded in a URL: scheme://user:pass@host -> scheme://[REDACTED]@host
    ("url_credentials", re.compile(r"\b([a-z][a-z0-9+.\-]*://)[^\s:@/]+:[^\s:@/]+@"), r"\1[REDACTED:URL_CREDS]@"),
    ("private_key_block",
     re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"),
     "[REDACTED:PRIVATE_KEY]"),
    # KEY=VALUE / KEY: VALUE where the name looks secret-bearing or is a known
    # vendor env family. Tolerates a leading `export `/`set `/list-item prefix
    # so the common transcript form `export OPENAI_API_KEY=...` is caught.
    ("env_secret",
     re.compile(
         r"(?im)^([ \t]*(?:export[ \t]+|set[ \t]+|[-*][ \t]+)?"
         r"(?:[A-Za-z_][A-Za-z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|PRIVATE|ACCESS[_-]?KEY)[A-Za-z0-9_]*"
         r"|(?:ANTHROPIC|AWS|OPENAI|GOOGLE|GCP|AZURE|SLACK|STRIPE|GITHUB|GH|NPM|PYPI|HF|HUGGINGFACE)_[A-Z0-9_]*)"
         r"\s*[=:]\s*)(\S[^\n]*)$"),
     r"\1[REDACTED:ENV]"),
]

# High-confidence shapes that must NEVER appear in the written output. The
# post-render gate re-scans the archive for these; a hit means the scrub was
# bypassed somewhere (an unscrubbed write path or a novel format) and the
# script exits non-zero. Kept to unambiguous credential shapes plus the home
# forms, so a gate failure is a real leak, not noise.
GATE_PATTERNS = [
    ("anthropic_key", re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("openai_key", re.compile(r"sk-(?:proj-|svcacct-|admin-)?[A-Za-z0-9_\-]{20,}")),
    ("aws_access_key_id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("stripe_key", re.compile(r"\bsk_live_[A-Za-z0-9]{20,}\b")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+")),
    ("slack_token", re.compile(r"\bxox[baprse]-[A-Za-z0-9-]{10,}|\bxapp-[A-Za-z0-9-]{10,}")),
]


def home_forms(home):
    """Both encodings of the home prefix that leak the username: the slash form
    (`/Users/x`) and the slug/dash form (`-Users-x`)."""
    if not home:
        return []
    return [home, home.replace("/", "-")]


def scrub(text, home, extra_rules, counts):
    """Redact secrets and rewrite the home path (both slash and dash forms).
    Mutates `counts`; returns the cleaned text."""
    for name, pat, repl in SCRUB_RULES + extra_rules:
        text, n = pat.subn(repl, text)
        if n:
            counts[name] += n
    for form in home_forms(home):
        n = text.count(form)
        if n:
            text = text.replace(form, "~")
            counts["home_path"] += n
    return text


def safe_name(name, home):
    """Sanitize a project slug for use as an output path component, so the
    archive's directory names don't ship the username. Mirrors the dash-form
    home rewrite the content scrub does, but to a shell-safe token."""
    if home:
        name = name.replace(home.replace("/", "-"), "home")
    return name


def load_extra_rules(path):
    """Load extra regex patterns, one per line: `name<TAB>regex`. Lines without
    a tab use the whole line as the regex with an auto name."""
    rules = []
    if not path or path == "none":
        return rules
    for i, raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines()):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        name, _, rx = line.partition("\t")
        if not rx:
            name, rx = f"extra_{i}", name
        rules.append((name.strip(), re.compile(rx.strip()), "[REDACTED:EXTRA]"))
    return rules


def rules_signature(extra_rules):
    """A stable fingerprint of the active ruleset. Changes when SCRUB_VERSION or
    the extra-rules file changes, which forces a full re-render."""
    blob = "|".join(name + pat.pattern for name, pat, _ in SCRUB_RULES + extra_rules)
    return f"v{SCRUB_VERSION}:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


# --- Render --------------------------------------------------------------------
def short_ts(ts):
    return (ts or "").replace("T", " ").replace("Z", "")[:19]


def truncate(s, limit):
    if limit and len(s) > limit:
        return s[:limit] + f"\n... [truncated {len(s) - limit} chars]"
    return s


def block_text(content, limit):
    """Flatten a tool_result `content` (string or array of blocks) to text."""
    if isinstance(content, str):
        s = content
    elif isinstance(content, list):
        parts = []
        for b in content:
            if not isinstance(b, dict):
                parts.append(str(b))
            elif b.get("type") == "text":
                parts.append(b.get("text", ""))
            elif b.get("type") == "image":
                parts.append("[image]")
            else:
                parts.append(f"[{b.get('type') or 'block'}]")
        s = "\n".join(parts)
    else:
        s = json.dumps(content, ensure_ascii=False)
    return truncate(s, limit)


def render_message(obj, no_thinking, limit, out):
    """Append one user/assistant message's Markdown to `out` (list of lines)."""
    msg = obj.get("message") or {}
    role = msg.get("role", obj.get("type", "?"))
    content = msg.get("content")
    sidechain = " · subagent" if obj.get("isSidechain") else ""
    out.append(f"\n### {role}{sidechain} · {short_ts(obj.get('timestamp'))}\n")

    if isinstance(content, str):
        out.append(content + "\n")
        return
    if not isinstance(content, list):
        return
    for b in content:
        if not isinstance(b, dict):
            continue
        t = b.get("type")
        if t == "text":
            out.append(b.get("text", "") + "\n")
        elif t == "thinking":
            if no_thinking:
                out.append("_[thinking omitted]_\n")
            else:
                think = b.get("thinking", "")
                out.append("> **thinking**\n>\n")
                out.append("\n".join("> " + ln for ln in think.splitlines()) + "\n")
        elif t == "tool_use":
            name = b.get("name", "tool")
            inp = b.get("input") or {}
            out.append(f"**→ {name}**\n")
            if name == "Bash" and "command" in inp:
                if inp.get("description"):
                    out.append(f"_{inp['description']}_\n")
                out.append("```bash\n" + truncate(str(inp["command"]), limit) + "\n```\n")
            else:
                out.append("```json\n" + truncate(json.dumps(inp, ensure_ascii=False, indent=2), limit) + "\n```\n")
        elif t == "tool_result":
            err = " · error" if b.get("is_error") else ""
            out.append(f"**← result{err}**\n")
            out.append("```\n" + block_text(b.get("content", ""), limit) + "\n```\n")


def render_session(path, no_thinking, limit):
    """Parse one transcript file. Returns (markdown, meta) or (None, None) if empty."""
    title, date, branch, msgs = None, None, None, 0
    body = []
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = obj.get("type")
            if date is None and obj.get("timestamp"):
                date = short_ts(obj["timestamp"])
            if obj.get("gitBranch"):
                branch = obj["gitBranch"]
            if t == "ai-title" and obj.get("aiTitle"):
                title = obj["aiTitle"]
            elif t == "summary" and obj.get("summary") and not title:
                title = obj["summary"]
            elif t in ("user", "assistant"):
                msgs += 1
                render_message(obj, no_thinking, limit, body)
    if msgs == 0:
        return None, None
    sid = path.stem
    header = [
        f"# {title or sid}\n",
        f"- Session: `{sid}`",
        f"- Date: {date or 'unknown'}",
        f"- Branch: `{branch or 'unknown'}`",
        f"- Messages: {msgs}",
        f"- Source: `{path.name}`\n",
    ]
    md = "\n".join(header) + "".join(body)
    meta = {"title": title or sid, "date": date or "", "branch": branch or "",
            "messages": msgs, "mdfile": sid + ".md"}
    return md, meta


# --- Scope / state -------------------------------------------------------------
def resolve_slugs(scope, projects_dir):
    """Map a scope token to a list of project-slug directory names."""
    all_slugs = sorted(p.name for p in projects_dir.iterdir() if p.is_dir())
    if scope == "all":
        return all_slugs
    if scope in ("cwd", "here"):
        cwd_slug = os.getcwd().replace("/", "-")
        matches = [s for s in all_slugs if s == cwd_slug or s.startswith(cwd_slug + "-")]
        if not matches:
            print(f"warning: no project slug matched cwd ({cwd_slug}); "
                  f"pass an explicit slug or 'all'", file=sys.stderr)
        return matches
    # explicit: an exact slug dir name, or a project-name fragment. Accepting a
    # fragment avoids typing the leading-dash slug, which argparse would treat
    # as a flag.
    if (projects_dir / scope).is_dir():
        return [scope]
    return [s for s in all_slugs if s == "-" + scope or s.endswith("-" + scope)]


def load_state(path):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"version": 1, "files": {}}


def sha256_of(path):
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_output(out_dir, home):
    """Re-scan the written archive for secrets that must never appear. Returns a
    list of (path, label, sample); empty means the gate passes."""
    hits = []
    forms = [("home_slug" if "-" in f and "/" not in f else "home_path", f) for f in home_forms(home)]
    for md in sorted(out_dir.rglob("*.md")):
        text = md.read_text(encoding="utf-8", errors="replace")
        for label, pat in GATE_PATTERNS:
            m = pat.search(text)
            if m:
                hits.append((str(md), label, m.group(0)[:40]))
        for label, form in forms:
            if form in text:
                hits.append((str(md), label, form))
    # no output PATH may leak the home slug either (rsync ships dir names)
    if home:
        hd = home.replace("/", "-")
        for p in out_dir.rglob("*"):
            if hd in p.name:
                hits.append((str(p), "home_slug_path", hd))
    return hits


# --- Main ----------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description="Render Claude Code sessions to a scrubbed Markdown archive.")
    ap.add_argument("scope", nargs="?", default="cwd",
                    help="cwd (default, slugs derived from the current directory) | all | an explicit slug dir name")
    ap.add_argument("--out", default=".archive/sessions", help="export directory (default: .archive/sessions)")
    ap.add_argument("--projects-dir", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--home", default=os.path.expanduser("~"), help="home prefix rewritten to ~ (none to disable)")
    ap.add_argument("--scrub-extra", default="none", help="file of extra `name<TAB>regex` redaction rules")
    ap.add_argument("--max-block-chars", type=int, default=4000, help="per-block truncation limit")
    ap.add_argument("--no-thinking", action="store_true", help="omit thinking blocks")
    ap.add_argument("--full", action="store_true", help="re-render every session, ignore incremental state")
    ap.add_argument("--dry-run", action="store_true",
                    help="render+scrub+report but do not update incremental state")
    args = ap.parse_args(argv)

    projects_dir = Path(args.projects_dir)
    if not projects_dir.is_dir():
        print(f"error: projects dir not found: {projects_dir}", file=sys.stderr)
        return 2
    out_dir = Path(args.out)
    home = None if args.home == "none" else args.home
    extra_rules = load_extra_rules(args.scrub_extra)
    sig = rules_signature(extra_rules)

    slugs = resolve_slugs(args.scope, projects_dir)
    if not slugs:
        print(f"error: scope '{args.scope}' matched no project slugs", file=sys.stderr)
        return 2

    state_path = out_dir / "_archive-state.json"
    state = load_state(state_path)
    files_state = state["files"]
    # A ruleset change forces a full re-render so unchanged sessions get re-scrubbed.
    rules_changed = state.get("rules_sig") != sig
    force_all = args.full or rules_changed
    total_counts = Counter()
    rendered, skipped = 0, 0
    report_lines = []

    for slug in slugs:
        slug_dir = projects_dir / slug
        safe = safe_name(slug, home)
        out_slug = out_dir / safe
        index_meta = []
        for jsonl in sorted(slug_dir.glob("*.jsonl")):
            key = f"{safe}/{jsonl.stem}"
            st = jsonl.stat()
            prev = files_state.get(key)
            unchanged = (prev and not force_all and not args.dry_run
                         and prev.get("size") == st.st_size and prev.get("mtime") == int(st.st_mtime))
            if unchanged:
                skipped += 1
                index_meta.append(prev)
                continue

            md, meta = render_session(jsonl, args.no_thinking, args.max_block_chars)
            if md is None:
                continue
            counts = Counter()
            md = scrub(md, home, extra_rules, counts)
            out_slug.mkdir(parents=True, exist_ok=True)
            (out_slug / meta["mdfile"]).write_text(md, encoding="utf-8")
            rendered += 1
            total_counts.update(counts)
            if counts:
                report_lines.append(f"{key}: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
            entry = {**meta, "size": st.st_size, "mtime": int(st.st_mtime),
                     "sha256": sha256_of(jsonl), "slug": safe}
            index_meta.append(entry)
            if not args.dry_run:
                files_state[key] = entry

        # per-slug index — scrubbed like any other output (titles/branches are transcript-derived)
        if index_meta:
            out_slug.mkdir(parents=True, exist_ok=True)
            rows = ["# Session archive: " + safe, "",
                    "| Date | Title | Branch | Msgs | File |", "|---|---|---|---|---|"]
            for m in sorted(index_meta, key=lambda x: x.get("date", ""), reverse=True):
                title = (m.get("title", "") or "").replace("|", "\\|")[:70]
                rows.append(f"| {m.get('date', '')} | {title} | `{m.get('branch', '')}` | "
                            f"{m.get('messages', '')} | [{m.get('mdfile', '')}]({m.get('mdfile', '')}) |")
            index_md = scrub("\n".join(rows) + "\n", home, extra_rules, total_counts)
            (out_slug / "index.md").write_text(index_md, encoding="utf-8")

    # post-render gate: re-scan the written archive for any secret that bypassed the scrub
    leaks = verify_output(out_dir, home)

    out_dir.mkdir(parents=True, exist_ok=True)
    report = ["Redaction report", "================",
              f"scope={args.scope} slugs={len(slugs)} rendered={rendered} skipped={skipped} "
              f"dry_run={args.dry_run} rules={sig}",
              f"GATE={'FAIL' if leaks else 'PASS'}", "",
              "Totals by rule:"]
    report += [f"  {k}: {v}" for k, v in sorted(total_counts.items())] or ["  (no redactions)"]
    report += ["", "Per-session (only sessions with redactions):"] + (report_lines or ["  (none)"])
    if leaks:
        report += ["", "GATE FAILURES (secrets that survived into the output):"]
        report += [f"  {lbl}  {sample}  in {p}" for p, lbl, sample in leaks[:50]]
    report_text = "\n".join(report) + "\n"
    (out_dir / "_redaction-report.txt").write_text(report_text, encoding="utf-8")

    if not args.dry_run and not leaks:
        state["rules_sig"] = sig
        state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    print(report_text, end="")
    if args.dry_run:
        print("[dry-run] incremental state NOT updated", file=sys.stderr)
    if leaks:
        print(f"GATE FAILED: {len(leaks)} secret(s) survived into the output; do NOT sync. "
              f"Add a pattern to --scrub-extra and re-run.", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
