#!/bin/sh
# Entrypoint for the session-archive skill: render Claude Code session
# transcripts to a scrubbed, browsable Markdown archive. Resolves its own
# location and execs the Python implementation (stdlib only, no install step).
# The skill owns the destination sync; this script only renders and scrubs.
# See .claude/skills/session-archive/SKILL.md.
DIR=$(cd "$(dirname "$0")" && pwd)
exec python3 "$DIR/session-archive-impl.py" "$@"
