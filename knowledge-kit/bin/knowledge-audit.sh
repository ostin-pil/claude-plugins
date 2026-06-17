#!/bin/sh
# Entrypoint for the knowledge-audit skill: scan the knowledge base for reuse
# health (orphaned docs, stale docs, unpromoted session learnings) and print a
# Markdown report to stdout. Read-only; resolves its own location and execs the
# Python implementation. See .claude/skills/knowledge-audit/SKILL.md.
DIR=$(cd "$(dirname "$0")" && pwd)
exec python3 "$DIR/knowledge-audit-impl.py" "$@"
