#!/bin/sh
# Isolated-control lifecycle A/B runner. Runs ONE trial and prints a verdict.
#
#   run-ab.sh <scenario> <skill|control> <model> [trial]
#
# Both arms launch a fresh `claude -p --safe-mode` agent: safe-mode disables the
# host CLAUDE.md, the lifecycle plugin, its skills, and its hooks, so the no-skill
# control is genuinely naive of the disciplines under test (this is the isolation
# the first A/B lacked). Auth, model, and the built-in tools still work. The skill
# arm gets the same pristine agent plus the scenario's SKILL.md inlined into the
# prompt; the control arm gets only the bare task. The single variable between arms
# is the skill procedure. The verdict is the scenario's ground-truth assert.sh,
# never the agent's self-report.
#
# Env knobs: LCK_MODEL_* not used; pass the model id as $3. GH_MOCK_MERGE_MODE
# selects clean|partial for finalize-clean (default clean). LCK_MAX_TURNS,
# LCK_TIMEOUT, LCK_AB_OUT override the defaults below.
set -u

HERE=$(cd "$(dirname "$0")" && pwd)            # .../benchmarks/lifecycle/ab
LCROOT=$(cd "$HERE/.." && pwd)                 # .../benchmarks/lifecycle
SKILLS_ROOT="${LCK_SKILLS_ROOT:-$(cd "$LCROOT/../.." && pwd)/lifecycle-kit/skills}"
CLEANROOM="${LCK_CLEANROOM:-${TMPDIR:-/tmp}/lck-cleanroom}"
OUT="${LCK_AB_OUT:-$HERE/runs}"
MAX_TURNS="${LCK_MAX_TURNS:-60}"
TIMEOUT="${LCK_TIMEOUT:-900}"
mkdir -p "$CLEANROOM" "$OUT"

# portable timeout: GNU timeout, then gtimeout, then a perl alarm (alarm survives
# exec, so claude inherits the timer); if none, run uncapped (--max-turns bounds it).
run_to() {
  _s=$1; shift
  if command -v timeout >/dev/null 2>&1; then timeout "$_s" "$@"
  elif command -v gtimeout >/dev/null 2>&1; then gtimeout "$_s" "$@"
  elif command -v perl >/dev/null 2>&1; then perl -e 'alarm shift; exec @ARGV' "$_s" "$@"
  else "$@"; fi
}

[ $# -ge 3 ] || { echo "usage: run-ab.sh <scenario> <skill|control> <model> [trial]" >&2; exit 2; }
SCEN="$1"; ARM="$2"; MODEL="$3"; TRIAL="${4:-1}"
SCEN_DIR="$LCROOT/scenarios/$SCEN"
[ -d "$SCEN_DIR" ] || { echo "no such scenario: $SCEN" >&2; exit 2; }
[ "$ARM" = skill ] || [ "$ARM" = control ] || { echo "arm must be skill|control" >&2; exit 2; }

# scenario -> skill, and whether it drives the gh mock
case "$SCEN" in
  branch-birth)            SKILL=session-start;     USES_GH=0;;
  ambiguous-finalize)      SKILL=finalize-worktree; USES_GH=0;;
  cleanup-containment)     SKILL=cleanup-worktrees; USES_GH=0;;
  finalize-clean)          SKILL=finalize-worktree; USES_GH=1;;
  finalize-already-merged) SKILL=finalize-worktree; USES_GH=1;;
  *) echo "unmapped scenario: $SCEN" >&2; exit 2;;
esac

# 1. setup: REPO from stdout (last line); mock env from stderr.
ERR=$(mktemp)
REPO=$("$SCEN_DIR/setup.sh" 2>"$ERR" | tail -1)
MOCKDIR=$(sed -n 's/^GH_MOCK_DIR:[[:space:]]*//p' "$ERR" | tail -1)
REMOTE=$(sed -n 's/^GH_MOCK_REMOTE:[[:space:]]*//p' "$ERR" | tail -1)
rm -f "$ERR"
[ -d "$REPO" ] || { echo "setup produced no repo for $SCEN" >&2; exit 2; }

# 2. prompt. GH note differs: with the mock the agent should use gh; without it,
#    there is no GitHub and gh must not run.
if [ "$USES_GH" = 1 ]; then
  GH_NOTE="A 'gh' mock is on PATH and the GH_MOCK_* env is exported; use gh exactly as the procedure prescribes (pr view/merge, api). The remote behind it is a local bare repo."
else
  GH_NOTE="There is no GitHub here; the remote is a local bare repo. Do NOT run any gh command; read and act on the underlying git state instead."
fi

TAG="${SCEN}.${ARM}.$(printf '%s' "$MODEL" | tr '/:' '__').t${TRIAL}"
LOG="$OUT/$TAG.log"
PROMPT=$(mktemp)

sub() { sed -e "s#{{REPO}}#$REPO#g" -e "s#{{GH_NOTE}}#$GH_NOTE#g" -e "s#{{SKILL_NAME}}#$SKILL#g"; }

if [ "$ARM" = skill ]; then
  SKILL_MD="$SKILLS_ROOT/$SKILL/SKILL.md"
  [ -f "$SKILL_MD" ] || { echo "missing SKILL.md: $SKILL_MD" >&2; rm -f "$PROMPT"; exit 2; }
  sub < "$HERE/prompt-templates/skill-arm.md" > "$PROMPT"
  printf '\n----- BEGIN SKILL: %s -----\n' "$SKILL" >> "$PROMPT"
  cat "$SKILL_MD" >> "$PROMPT"
  printf '\n----- END SKILL -----\n' >> "$PROMPT"
else
  # control body is everything below the first `---` line in the prompt file
  awk 'f;/^---[[:space:]]*$/{f=1}' "$HERE/control-prompts/$SCEN.md" | sub > "$PROMPT"
fi

# 3. isolated agent, launched from a clean cwd (belt-and-suspenders with safe-mode)
cd "$CLEANROOM" || { rm -f "$PROMPT"; exit 2; }
set -- --print --safe-mode --model "$MODEL" \
       --permission-mode bypassPermissions \
       --allowedTools Bash,Read,Edit,Write,Glob,Grep \
       --add-dir "$REPO" --max-turns "$MAX_TURNS" --output-format text
if [ "$USES_GH" = 1 ]; then
  PATH="$LCROOT/gh-mock:$PATH"; export PATH
  GH_MOCK_DIR="$MOCKDIR"; GH_MOCK_REMOTE="$REMOTE"; export GH_MOCK_DIR GH_MOCK_REMOTE
  set -- "$@" --add-dir "$LCROOT/gh-mock" --add-dir "$MOCKDIR"
fi

run_to "$TIMEOUT" claude "$@" < "$PROMPT" > "$LOG" 2>&1
RC=$?
rm -f "$PROMPT"

# 4. ground-truth assert
if [ "$USES_GH" = 1 ]; then
  AOUT=$("$SCEN_DIR/assert.sh" "$REPO" "$MOCKDIR" 2>&1)
else
  AOUT=$("$SCEN_DIR/assert.sh" "$REPO" 2>&1)
fi
VERDICT=$(printf '%s\n' "$AOUT" | sed -n 's/^VERDICT: //p' | tail -1)
[ -n "$VERDICT" ] || VERDICT=FAIL
{ echo "===== ASSERT ====="; echo "$AOUT"; } >> "$LOG"

echo "RESULT $SCEN $ARM $MODEL t$TRIAL -> $VERDICT (agent_rc=$RC)"
echo "$SCEN|$ARM|$MODEL|$TRIAL|$VERDICT|$RC|$REPO" >> "$OUT/tally.psv"
[ "$VERDICT" = PASS ]
