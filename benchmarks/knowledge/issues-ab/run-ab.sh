#!/bin/sh
# Knowledge-kit `issues` add A/B. One trial: fixture -> isolated agent -> assert.
#   run-ab.sh <skill|control> <model> [trial]
#
# Both arms run a fresh `claude -p --safe-mode` agent (no host CLAUDE.md, plugin,
# skills, or hooks; auth/model/tools intact). The skill arm gets the `issues`
# SKILL.md inlined; the control gets only the bare "log this bug" task. Both are
# given the same structured bug details, so the variable is the skill's procedure
# (sequential id, read-before-write, the entry schema). Ground truth is assert.py
# on the tracker file, never the agent's self-report.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
KROOT=$(cd "$HERE/../../.." && pwd)                 # claude-plugins repo root
SKILL_MD="$KROOT/knowledge-kit/skills/issues/SKILL.md"
CLEAN="${KAB_CLEANROOM:-${TMPDIR:-/tmp}/iab-cleanroom}"
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

REPO=$(sh "$HERE/setup.sh" 2>/dev/null | tail -1)
[ -d "$REPO" ] || { echo "setup failed" >&2; exit 2; }

TAG="$ARM.$(printf '%s' "$MODEL" | tr '/:' '__').t$TRIAL"
LOG="$OUTDIR/$TAG.log"
PROMPT=$(mktemp)
sub() { sed -e "s#{{REPO}}#$REPO#g"; }

if [ "$ARM" = skill ]; then
  sub < "$HERE/prompt-templates/skill-arm.md" > "$PROMPT"
  printf '\n----- BEGIN SKILL: issues -----\n' >> "$PROMPT"
  cat "$SKILL_MD" >> "$PROMPT"
  printf '\n----- END SKILL -----\n' >> "$PROMPT"
else
  awk 'f;/^---[[:space:]]*$/{f=1}' "$HERE/control-prompt.md" | sub > "$PROMPT"
fi

cd "$CLEAN" || { rm -f "$PROMPT"; exit 2; }
set -- --print --safe-mode --model "$MODEL" --permission-mode bypassPermissions \
       --allowedTools Bash,Read,Write,Edit,Glob,Grep --add-dir "$REPO" \
       --max-turns "$MAXT" --output-format text
run_to "$TMO" claude "$@" < "$PROMPT" > "$LOG" 2>&1
RC=$?
rm -f "$PROMPT"

SCAN=$(python3 "$HERE/assert.py" "$REPO" 2>&1)
{ echo "===== ASSERT ($REPO) ====="; echo "$SCAN"; } >> "$LOG"
CHECKS=$(printf '%s\n' "$SCAN" | sed -n 's/^CHECKS //p' | tail -1)
V=$(printf '%s\n' "$SCAN" | sed -n 's/^VERDICT: //p' | tail -1)
[ -n "$V" ] || V=FAIL

echo "RESULT $ARM $MODEL t$TRIAL -> $V [$CHECKS] agent_rc=$RC"
echo "$ARM|$MODEL|$TRIAL|$V|$CHECKS|$RC|$REPO" >> "$OUTDIR/tally.psv"
[ "$V" = PASS ]
