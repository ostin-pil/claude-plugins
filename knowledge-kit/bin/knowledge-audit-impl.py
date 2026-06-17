#!/usr/bin/env python3
"""Audit the knowledge base for reuse health.

Three checks over the tracked Markdown in the repo:
  1. Orphaned docs   — knowledge/ and research/ docs no other file references.
  2. Stale docs      — docs with no commit in the last N days (git, not mtime).
  3. Unpromoted      — recent session logs whose "Decisions worth remembering"
                       section is not yet reflected under the decisions dir.

Prints a one-page Markdown health report to stdout. Read-only: it never edits,
promotes, or deletes anything. Stdlib + git only.
"""
from __future__ import annotations

import argparse
import datetime
import os
import re
import subprocess
import sys
from pathlib import Path

ENTRY_POINTS = {"README.md", "INDEX.md"}
DECISION_HEADER = re.compile(r"^##\s+.*decision", re.IGNORECASE)
SECTION_HEADER = re.compile(r"^##\s+")
SESSION_N = re.compile(r"_session_(\d+)")
DATED = re.compile(r"\d{4}-\d{2}(-\d{2})?")


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args],
                          capture_output=True, text=True, check=False).stdout


def tracked_md(root):
    out = git(root, "ls-files", "*.md")
    return [line for line in out.splitlines() if line]


def read(root, rel):
    try:
        return (root / rel).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def last_commit_dates(root):
    """rel-path -> most-recent commit date (YYYY-MM-DD), from one git log pass."""
    out = git(root, "log", "--format=C%cd", "--date=short", "--name-only", "--no-renames")
    dates, cur = {}, None
    for line in out.splitlines():
        if line.startswith("C") and len(line) == 11 and line[5] == "-":
            cur = line[1:]
        elif line and cur and line not in dates:
            dates[line] = cur  # first occurrence is the most recent commit
    return dates


def decision_bullets(text):
    """Extract bullet lines from the first decisions-style section."""
    lines = text.splitlines()
    out, inside = [], False
    for ln in lines:
        if SECTION_HEADER.match(ln):
            if inside:
                break
            inside = bool(DECISION_HEADER.match(ln))
            continue
        if inside and ln.strip():
            out.append(ln.rstrip())
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Audit the knowledge base for reuse health.")
    ap.add_argument("--root", default=None, help="repo root (default: git toplevel)")
    ap.add_argument("--knowledge-dir", default="knowledge")
    ap.add_argument("--research-dir", default="research")
    ap.add_argument("--log-dir", default="sessions")
    ap.add_argument("--stale-days", type=int, default=90)
    ap.add_argument("--recent-logs", type=int, default=8)
    args = ap.parse_args(argv)

    root = Path(args.root) if args.root else Path(git(Path.cwd(), "rev-parse", "--show-toplevel").strip() or ".")
    today = datetime.date.today()

    all_md = tracked_md(root)
    texts = {rel: read(root, rel) for rel in all_md}
    corpus = "\n".join(texts.values())
    dates = last_commit_dates(root)

    # Markdown links resolved against each citing file's directory. A README or
    # INDEX that links a doc by a path relative to its own folder (e.g.
    # `voices/swiss.md` from knowledge/design/README.md) is a real citation; the
    # full-path substring check below only catches the backticked full-repo-path
    # mentions that session logs use, so without this those links read as orphans.
    link_refs = set()
    link_re = re.compile(r"\]\(([^)\s#]+)")
    for citer, text in texts.items():
        base = os.path.dirname(citer)
        for m in link_re.finditer(text):
            tgt = m.group(1).split("#")[0].lstrip("./").rstrip("/")
            if not tgt or "://" in tgt:
                continue
            resolved = os.path.normpath(os.path.join(base, tgt)) if base else os.path.normpath(tgt)
            for form in (tgt, resolved):
                if form != citer:
                    link_refs.add(form)

    def candidates(top):
        pref = top.rstrip("/") + "/"
        return [r for r in all_md if r.startswith(pref)
                and Path(r).name not in ENTRY_POINTS and "/fixtures/" not in r]

    know = candidates(args.knowledge_dir)
    res = candidates(args.research_dir)

    def is_referenced(rel):
        # a resolved markdown link to it, or its full repo-relative path mentioned
        # literally in some other file (the backticked form session logs use)
        if rel in link_refs:
            return True
        return (corpus.count(rel) - texts.get(rel, "").count(rel)) > 0

    def age_note(rel):
        d = dates.get(rel)
        if not d:
            return None, ""
        age = (today - datetime.date.fromisoformat(d)).days
        tag = " [dated snapshot]" if DATED.search(Path(rel).name) else ""
        return age, f"last commit {d} ({age}d ago){tag}"

    orphans = {"knowledge": [], "research": []}
    stale = {"knowledge": [], "research": []}
    cited = {"knowledge": 0, "research": 0}
    for label, group in (("knowledge", know), ("research", res)):
        for rel in group:
            if is_referenced(rel):
                cited[label] += 1
            else:
                orphans[label].append(rel)
            age, note = age_note(rel)
            if age is not None and age > args.stale_days:
                stale[label].append((rel, note))

    # unpromoted learnings from recent session logs
    log_pref = args.log_dir.rstrip("/") + "/"
    logs = sorted(r for r in all_md
                  if r.startswith(log_pref) and "/archive/" not in r and SESSION_N.search(r))
    know_text = "\n".join(t for r, t in texts.items()
                          if r.startswith(args.knowledge_dir.rstrip("/") + "/"))
    unpromoted = []
    for rel in logs[-args.recent_logs:]:
        m = SESSION_N.search(rel)
        n = m.group(1)
        bullets = decision_bullets(texts[rel])
        if not bullets:
            continue
        # "promoted" proxy: the session number appears somewhere durable under knowledge/
        referenced = bool(re.search(rf"session[ \-]?{n}\b", know_text, re.IGNORECASE))
        if not referenced:
            unpromoted.append((n, rel, bullets))

    # --- report ---
    out = [f"# Knowledge audit — {today.isoformat()}", ""]
    out.append("## Citation coverage")
    out.append(f"- knowledge/: {cited['knowledge']}/{len(know)} docs referenced "
               f"({len(orphans['knowledge'])} orphaned)")
    out.append(f"- research/: {cited['research']}/{len(res)} docs referenced "
               f"({len(orphans['research'])} orphaned)")
    out.append("")

    out.append("## Orphaned docs (no other tracked file references the path)")
    any_orphan = False
    for label in ("knowledge", "research"):
        for rel in orphans[label]:
            any_orphan = True
            _, note = age_note(rel)
            out.append(f"- `{rel}`{(' — ' + note) if note else ''}")
    if not any_orphan:
        out.append("- none")
    out.append("")
    out.append("_Heuristic: matches the full repo-relative path. Brace-expanded or renamed "
               "references can read as orphaned; confirm before acting._")
    out.append("")

    out.append(f"## Stale docs (no commit in {args.stale_days}+ days)")
    any_stale = False
    for label in ("knowledge", "research"):
        for rel, note in sorted(stale[label], key=lambda x: x[1]):
            any_stale = True
            out.append(f"- `{rel}` — {note}")
    if not any_stale:
        out.append("- none")
    out.append("")
    out.append("_A dated snapshot going stale is often intentional (research convention: "
               "leave superseded docs in place). Staleness here is informational._")
    out.append("")

    out.append("## Unpromoted learnings (recent logs whose decisions aren't referenced anywhere "
               f"under `{args.knowledge_dir}`)")
    if not unpromoted:
        out.append("- none in the last "
                   f"{args.recent_logs} logs (each recent session is referenced under {args.knowledge_dir}/)")
    for n, rel, bullets in unpromoted:
        out.append(f"\n### session {n} — `{rel}`")
        for b in bullets[:12]:
            out.append(b if b.lstrip().startswith(("-", "*", "1", "2", "3", "4", "5", "6", "7", "8", "9")) else f"- {b}")
    out.append("")
    out.append("_A learning that is multi-session or cross-project belongs in a durable doc "
               "(an `OD-NNN` in open-decisions, an issue, or a knowledge doc), not only the log._")

    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
