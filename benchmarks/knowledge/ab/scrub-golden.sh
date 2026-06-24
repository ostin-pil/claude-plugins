#!/bin/sh
# Golden test for the session-archive scrubber: the deterministic converter must
# scrub every planted secret and pass its own gate. No agents; this validates the
# tool the skill arm relies on, the way score.py validates knowledge-audit.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
IMPL="$HERE/../../../knowledge-kit/bin/session-archive-impl.py"

ERR=$(mktemp)
ROOT=$(python3 "$HERE/setup.py" 2>"$ERR")
EXP=$(sed -n 's/^EXPECTED: //p' "$ERR" | tail -1)
rm -f "$ERR"
OUT="$ROOT/out"
echo "fixture: $ROOT  (ground truth: $EXP)"

# Run the converter over the fixture projects-dir. It scrubs, writes the archive,
# then re-scans and exits 3 if any high-confidence secret survived (its gate).
python3 "$IMPL" all --projects-dir "$ROOT/projects" --out "$OUT" --home /nonexistent --full >/dev/null 2>"$ROOT/conv.err"
RC=$?
echo "converter exit: $RC ($([ "$RC" = 0 ] && echo 'GATE=PASS' || echo 'GATE=FAIL or error'))"
[ "$RC" = 0 ] || { echo "--- converter stderr ---"; cat "$ROOT/conv.err"; }

echo "--- leak scan of the scrubbed output ---"
python3 "$HERE/assert-leaks.py" "$OUT" "$EXP"
AL=$?

echo ""
[ "$RC" = 0 ] && [ "$AL" = 0 ] && echo "GOLDEN: PASS (gate passed, zero secrets survived)" || { echo "GOLDEN: FAIL"; exit 1; }
