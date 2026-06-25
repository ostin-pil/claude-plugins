#!/bin/sh
# Knowledge-kit `issues` A/B (scenario-generic). One trial.
#   run-ab.sh <add|verify|search> <skill|control> <model> [trial]
#
# Both arms run a fresh `claude -p --safe-mode` agent (no host CLAUDE.md, plugin,
# skills, or hooks; auth/model/tools intact). The skill arm gets only the relevant
# command's slice of the `issues` SKILL.md (the shared head and tail plus that one
# `### /issues <cmd>` block, not the whole file); the control gets the bare task
# with the goal but not the procedure. Ground truth depends on the scenario: add
# and verify score the tracker file (assert-add.py / assert-verify.py); search
# scores the agent's report (assert-search.py), since search is a read-only command.
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

# Emit only the command-relevant slice of SKILL.md: the head (everything before the
# first `### ` command block), the one `### /issues <cmd>` block, and the tail
# (`## Entry Format` onward). The three sibling command blocks and the no-arg list
# block are dropped so the skill arm is not weighed down by irrelevant prose.
skill_slice() {
  awk -v cmd="$1" '
    BEGIN { phase="head"; keep=0 }
    phase=="head" {
      if ($0 ~ /^### /) { phase="cmds" } else { print; next }
    }
    phase=="cmds" {
      if ($0 ~ /^## /) { phase="tail" }
      else {
        if ($0 ~ /^### /) keep = ($0 ~ ("/issues " cmd))
        if (keep) print
        next
      }
    }
    phase=="tail" { print }
  ' "$SKILL_MD"
}

[ $# -ge 3 ] || { echo "usage: run-ab.sh <add|verify|search> <skill|control> <model> [trial]" >&2; exit 2; }
SCEN="$1"; ARM="$2"; MODEL="$3"; TRIAL="${4:-1}"
[ -f "$HERE/setup-$SCEN.sh" ] || { echo "no such scenario: $SCEN" >&2; exit 2; }
[ "$ARM" = skill ] || [ "$ARM" = control ] || { echo "arm must be skill|control" >&2; exit 2; }

REPO=$(sh "$HERE/setup-$SCEN.sh" 2>/dev/null | tail -1)
[ -d "$REPO" ] || { echo "setup failed" >&2; exit 2; }

TAG="$SCEN.$ARM.$(printf '%s' "$MODEL" | tr '/:' '__').t$TRIAL"
LOG="$OUTDIR/$TAG.log"
PROMPT=$(mktemp)
sub() { sed -e "s#{{REPO}}#$REPO#g"; }

if [ "$ARM" = skill ]; then
  sub < "$HERE/prompt-templates/$SCEN-skill.md" > "$PROMPT"
  printf '\n----- BEGIN SKILL: issues (%s) -----\n' "$SCEN" >> "$PROMPT"
  skill_slice "$SCEN" >> "$PROMPT"
  printf '\n----- END SKILL -----\n' >> "$PROMPT"
else
  awk 'f;/^---[[:space:]]*$/{f=1}' "$HERE/control-$SCEN.md" | sub > "$PROMPT"
fi

cd "$CLEAN" || { rm -f "$PROMPT"; exit 2; }
set -- --print --safe-mode --model "$MODEL" --permission-mode bypassPermissions \
       --allowedTools Bash,Read,Write,Edit,Glob,Grep --add-dir "$REPO" \
       --max-turns "$MAXT" --output-format text
run_to "$TMO" claude "$@" < "$PROMPT" > "$LOG" 2>&1
RC=$?
rm -f "$PROMPT"

case "$SCEN" in
  add)    SCAN=$(python3 "$HERE/assert-add.py" "$REPO" 2>&1) ;;
  verify) SCAN=$(python3 "$HERE/assert-verify.py" "$REPO" 2>&1) ;;
  search) SCAN=$(python3 "$HERE/assert-search.py" "$LOG" 2>&1) ;;
esac
{ echo "===== ASSERT ====="; echo "$SCAN"; } >> "$LOG"
CHECKS=$(printf '%s\n' "$SCAN" | sed -n 's/^CHECKS //p' | tail -1)
V=$(printf '%s\n' "$SCAN" | sed -n 's/^VERDICT: //p' | tail -1)
[ -n "$V" ] || V=FAIL

echo "RESULT $SCEN $ARM $MODEL t$TRIAL -> $V [$CHECKS] agent_rc=$RC"
echo "$SCEN|$ARM|$MODEL|$TRIAL|$V|$CHECKS|$RC|$REPO" >> "$OUTDIR/tally.psv"
[ "$V" = PASS ]
