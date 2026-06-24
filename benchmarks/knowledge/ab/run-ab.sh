#!/bin/sh
# Knowledge-kit session-archive scrub A/B. One trial: fixture -> isolated agent ->
# leak scan. Prints a verdict (PASS = zero planted secrets survived).
#
#   run-ab.sh <skill|control> <model> [trial]
#
# Both arms run a fresh `claude -p --safe-mode` agent (no host CLAUDE.md, no
# plugin, no skills, no hooks; auth/model/tools intact). The skill arm gets the
# session-archive SKILL.md inlined and knowledge-kit/bin on PATH, so it can run
# the deterministic, self-gating scrubber. The control arm gets only the bare
# "render and redact" task and no converter. The single variable is the skill.
# Ground truth is assert-leaks.py: how many planted secrets survived into the
# arm's output, never the agent's self-report.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
KROOT=$(cd "$HERE/../../.." && pwd)                 # claude-plugins repo root
SKILL_MD="$KROOT/knowledge-kit/skills/session-archive/SKILL.md"
BIN="$KROOT/knowledge-kit/bin"
CLEAN="${KAB_CLEANROOM:-${TMPDIR:-/tmp}/kab-cleanroom}"
OUTDIR="${KAB_OUT:-$HERE/runs}"
MAXT="${KAB_MAX_TURNS:-40}"; TMO="${KAB_TIMEOUT:-900}"
mkdir -p "$CLEAN" "$OUTDIR"

run_to() {
  _s=$1; shift
  if command -v timeout >/dev/null 2>&1; then timeout "$_s" "$@"
  elif command -v gtimeout >/dev/null 2>&1; then gtimeout "$_s" "$@"
  elif command -v perl >/dev/null 2>&1; then perl -e 'alarm shift; exec @ARGV' "$_s" "$@"
  else "$@"; fi
}

[ $# -ge 2 ] || { echo "usage: run-ab.sh <skill|control> <model> [trial]" >&2; exit 2; }
ARM="$1"; MODEL="$2"; TRIAL="${3:-1}"
[ "$ARM" = skill ] || [ "$ARM" = control ] || { echo "arm must be skill|control" >&2; exit 2; }

ERR=$(mktemp)
ROOT=$(python3 "$HERE/setup.py" 2>"$ERR" | tail -1)
EXP=$(sed -n 's/^EXPECTED: //p' "$ERR" | tail -1)
rm -f "$ERR"
[ -d "$ROOT" ] || { echo "setup failed" >&2; exit 2; }
[ -f "$EXP" ] || { echo "no ground truth file from setup" >&2; exit 2; }
PROJ="$ROOT/projects"; OUT="$ROOT/out-$ARM"
mkdir -p "$OUT"

TAG="$ARM.$(printf '%s' "$MODEL" | tr '/:' '__').t$TRIAL"
LOG="$OUTDIR/$TAG.log"
PROMPT=$(mktemp)
sub() { sed -e "s#{{PROJECTS}}#$PROJ#g" -e "s#{{OUT}}#$OUT#g"; }

if [ "$ARM" = skill ]; then
  sub < "$HERE/prompt-templates/skill-arm.md" > "$PROMPT"
  printf '\n----- BEGIN SKILL: session-archive -----\n' >> "$PROMPT"
  cat "$SKILL_MD" >> "$PROMPT"
  printf '\n----- END SKILL -----\n' >> "$PROMPT"
  PATH="$BIN:$PATH"; export PATH
else
  awk 'f;/^---[[:space:]]*$/{f=1}' "$HERE/control-prompt.md" | sub > "$PROMPT"
fi

cd "$CLEAN" || { rm -f "$PROMPT"; exit 2; }
set -- --print --safe-mode --model "$MODEL" --permission-mode bypassPermissions \
       --allowedTools Bash,Read,Write,Glob,Grep --add-dir "$PROJ" --add-dir "$OUT" \
       --max-turns "$MAXT" --output-format text
run_to "$TMO" claude "$@" < "$PROMPT" > "$LOG" 2>&1
RC=$?
rm -f "$PROMPT"

SCAN=$(python3 "$HERE/assert-leaks.py" "$OUT" "$EXP" 2>&1)
{ echo "===== LEAK SCAN ($OUT) ====="; echo "$SCAN"; } >> "$LOG"
LINE=$(printf '%s\n' "$SCAN" | sed -n 's#^LEAKED \([0-9][0-9]*\)/\([0-9][0-9]*\).*#\1 \2#p' | tail -1)
N=$(printf '%s' "$LINE" | awk '{print $1}'); M=$(printf '%s' "$LINE" | awk '{print $2}')
[ -n "$N" ] || N=NA; [ -n "$M" ] || M=12
V=$([ "$N" = 0 ] && echo PASS || echo FAIL)

echo "RESULT $ARM $MODEL t$TRIAL -> leaked $N/$M ($V) agent_rc=$RC"
echo "$ARM|$MODEL|$TRIAL|$N|$M|$V|$RC|$ROOT" >> "$OUTDIR/tally.psv"
[ "$V" = PASS ]
