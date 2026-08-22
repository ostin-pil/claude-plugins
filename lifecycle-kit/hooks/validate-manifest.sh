#!/bin/sh
# lifecycle-kit SessionStart validation.
#
# Validates the manifest of a project that has ADOPTED the kit, so a malformed
# manifest surfaces as one clear message instead of a cryptic failure mid-
# /session-end.
#
# A repo with no .claude/lifecycle-manifest.md has not adopted the kit. The kit is
# user-scoped, so that is the resting state of most repos on the machine, not a
# misconfiguration: this stays silent there. The skills own the "no manifest"
# message and raise it at the point of use, where the intent to use the kit is
# unambiguous.
#
# Dependency-free on purpose: sh + git + grep only. No YAML parser, so the
# structural check is "required keys are present", not a full parse.
#
# Non-blocking: SessionStart hooks never abort the session. On a problem this
# emits a SessionStart JSON payload (systemMessage for the user, additionalContext
# for the model) and exits 0. When all is well it prints nothing.

emit() {
  # $1: single-line message. JSON-escape it: the text carries a manifest-supplied
  # remote name and a filesystem path, neither of which is trusted to be quote-free.
  esc=$(printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g')
  printf '{"systemMessage":"%s","hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$esc" "$esc"
}

TOPLEVEL=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0   # not a git repo: nothing to validate
MANIFEST="$TOPLEVEL/.claude/lifecycle-manifest.md"

# No manifest: the project has not adopted the kit. Nothing to validate, nothing to say.
[ -f "$MANIFEST" ] || exit 0

# Resolve the template from this script's own location, so the message names a path
# the user can actually copy rather than one relative to nothing.
PLUGIN_ROOT=$(unset CDPATH; cd -- "$(dirname -- "$0")/.." 2>/dev/null && pwd)
TEMPLATE="${PLUGIN_ROOT:-$CLAUDE_PLUGIN_ROOT}/lifecycle-manifest.template.md"

msg=""

# Required keys the skills cannot run without.
missing=
for key in product_name remote integration_ref local_main pr_base branch_pattern branch_glob \
           log_dir log_pattern log_presence_regex build_commands test_commands merge_strategy; do
  grep -qE "^${key}:" "$MANIFEST" || missing="$missing $key"
done
[ -n "$missing" ] && msg="lifecycle-kit: $MANIFEST is missing required key(s):$missing. Fill them in; the full set with defaults is in $TEMPLATE."

add() { [ -n "$msg" ] && msg="$msg $1" || msg="$1"; }

# forge (default github when absent, so pre-forge manifests keep working).
forge=$(grep -E "^forge:" "$MANIFEST" | head -1 | sed -E 's/^forge:[[:space:]]*//; s/[[:space:]]*#.*$//')
[ -n "$forge" ] || forge=github
case "$forge" in
  github|forgejo|none) ;;
  *) add "lifecycle-kit: forge: '$forge' is not a known provider (github, forgejo, none). Presets live in $PLUGIN_ROOT/forges/." ;;
esac

# Per-provider preconditions. Each is a real mid-finalize failure otherwise.
case "$forge" in
  github)
    command -v gh >/dev/null 2>&1 || add "lifecycle-kit: forge is github but 'gh' is not on PATH; phase 3 cannot create or merge the PR."
    ;;
  forgejo)
    command -v jq >/dev/null 2>&1 || add "lifecycle-kit: forge is forgejo but 'jq' is not on PATH; the forgejo preset parses every API response with it."
    for k in forge_url forge_repo; do
      v=$(grep -E "^${k}:" "$MANIFEST" | head -1 | sed -E "s/^${k}:[[:space:]]*//; s/[[:space:]]*#.*$//")
      { [ -n "$v" ] && [ "$v" != none ]; } || add "lifecycle-kit: forge is forgejo but $k is unset; the API base URL and owner/name are both required."
    done
    [ -n "$FORGEJO_TOKEN" ] || add "lifecycle-kit: forge is forgejo but FORGEJO_TOKEN is unset in the environment; every API call will 401."
    ;;
  none)
    strat=$(grep -E "^merge_strategy:" "$MANIFEST" | head -1 | sed -E 's/^merge_strategy:[[:space:]]*//; s/[[:space:]]*#.*$//')
    [ -z "$strat" ] || [ "$strat" = merge ] || add "lifecycle-kit: forge is none, which requires merge_strategy: merge; '$strat' leaves the branch tip unreachable from the integration branch, breaking the ancestry that stands in for a PR record."
    ;;
esac

# requires_remote (default true) needs a real remote configured. forge: none
# has its own supported no-remote lifecycle, so it never warrants this warning.
if [ "$forge" != none ] && ! grep -qE "^requires_remote:[[:space:]]*false" "$MANIFEST"; then
  remote=$(grep -E "^remote:" "$MANIFEST" | head -1 | sed -E 's/^remote:[[:space:]]*//; s/[[:space:]]*#.*$//')
  [ -n "$remote" ] || remote=origin
  if ! git remote | grep -qx "$remote"; then
    add "lifecycle-kit: requires_remote is set but git remote '$remote' is not configured; the finalize/cleanup lifecycle needs a fetchable remote (report and read-only briefing still work). Set requires_remote: false, or forge: none for a repo that has no remote by design."
  fi
fi

[ -n "$msg" ] && emit "$msg"
exit 0
