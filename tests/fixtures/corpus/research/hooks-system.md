# Claude Code Hooks System -- Deep Reference

*Compiled: 2026-04-09*

---

## 1. Overview

Hooks are user-defined handlers that execute at specific lifecycle points in Claude Code.
They provide **deterministic** control -- certain actions always happen, rather than
relying on the LLM to choose to run them. Four hook types exist: shell commands, HTTP
endpoints, single-turn LLM prompts, and multi-turn agent subagents.

Configuration lives in JSON settings files at three scopes:

| Location | Scope | Shareable |
|----------|-------|-----------|
| `~/.claude/settings.json` | All projects (user-level) | No |
| `.claude/settings.json` | Single project | Yes (commit to repo) |
| `.claude/settings.local.json` | Single project | No (gitignored) |
| Managed policy settings | Organization-wide | Admin-controlled |
| Plugin `hooks/hooks.json` | When plugin is enabled | Bundled with plugin |
| Skill/agent frontmatter | While component is active | In component file |

---

## 2. All Hook Events

### 2.1 Event Table

| Event | Fires When | Matcher Field | Can Block? |
|-------|-----------|---------------|------------|
| **SessionStart** | New session, resume, `/clear`, or after compaction | session source (`startup\|resume\|clear\|compact`) | No |
| **SessionEnd** | Session terminates | end reason (`clear\|resume\|logout\|prompt_input_exit\|other`) | No |
| **InstructionsLoaded** | CLAUDE.md or `.claude/rules/*.md` loaded | load reason (`session_start\|nested_traversal\|path_glob_match\|include\|compact`) | No |
| **UserPromptSubmit** | User submits prompt, before processing | No matcher support | Yes (exit 2) |
| **PreToolUse** | Before tool executes | tool name | Yes (deny) |
| **PermissionRequest** | Permission dialog about to show | tool name | Yes (deny) |
| **PostToolUse** | After tool succeeds | tool name | No (tool already ran) |
| **PostToolUseFailure** | Tool execution fails | tool name | No |
| **PermissionDenied** | Auto mode classifier denies call | tool name | No |
| **Notification** | Claude Code sends notification | notification type | No |
| **SubagentStart** | Subagent spawned | agent type | No |
| **SubagentStop** | Subagent finishes | agent type | Yes (exit 2) |
| **Stop** | Claude finishes responding | No matcher support | Yes (exit 2) |
| **StopFailure** | Turn ends due to API error | error type | No (output ignored) |
| **TeammateIdle** | Agent team teammate going idle | No matcher support | Yes (exit 2) |
| **TaskCreated** | Task created via TaskCreate | No matcher support | Yes (rolls back) |
| **TaskCompleted** | Task marked complete | No matcher support | Yes |
| **ConfigChange** | Config file changes during session | config source | Yes (exit 2) |
| **CwdChanged** | Working directory changes | No matcher support | No |
| **FileChanged** | Watched file changes on disk | literal filenames | No |
| **WorktreeCreate** | Worktree being created | No matcher support | Yes (non-zero fails) |
| **WorktreeRemove** | Worktree being removed | No matcher support | No |
| **PreCompact** | Before context compaction | trigger (`manual\|auto`) | No |
| **PostCompact** | After compaction completes | trigger (`manual\|auto`) | No |
| **Elicitation** | MCP server requests user input | MCP server name | Yes |
| **ElicitationResult** | User responds to MCP elicitation | MCP server name | Yes |

### 2.2 Common Input Fields (All Events)

Every event receives this base JSON on stdin:

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/current/working/directory",
  "permission_mode": "default|plan|acceptEdits|auto|dontAsk|bypassPermissions",
  "hook_event_name": "EventName",
  "agent_id": "agent-xyz",
  "agent_type": "agent-name"
}
```

### 2.3 Event-Specific Input Fields

**SessionStart**: `source` (startup|resume|clear|compact), `model`, optional `agent_type`

**UserPromptSubmit**: `prompt` (the user's text)

**PreToolUse**: `tool_name`, `tool_input`, `tool_use_id`

**PermissionRequest**: `tool_name`, `tool_input`, optional `permission_suggestions[]`

**PostToolUse**: `tool_name`, `tool_input`, `tool_response`, `tool_use_id`

**PostToolUseFailure**: `tool_name`, `tool_input`, `tool_use_id`, `error`, optional `is_interrupt`

**PermissionDenied**: `tool_name`, `tool_input`, `tool_use_id`, `reason`

**Notification**: `message`, optional `title`, `notification_type`

**SubagentStart**: `agent_id`, `agent_type`

**SubagentStop**: `stop_hook_active`, `agent_id`, `agent_type`, `agent_transcript_path`, `last_assistant_message`

**Stop**: `stop_hook_active` (boolean)

**StopFailure**: `error_type` (rate_limit|authentication_failed|billing_error|invalid_request|server_error|max_output_tokens|unknown)

**TaskCreated**: `task_id`, `task_subject`, optional `task_description`, `teammate_name`, `team_name`

**TaskCompleted**: `task_id`, optional `task_subject`

**ConfigChange**: `source`, `file_path`

**InstructionsLoaded**: `file_path`, `memory_type`, `load_reason`, optional `globs`, `trigger_file_path`, `parent_file_path`

---

## 3. All Four Hook Types in Detail

### 3.1 Command Hooks (`type: "command"`)

Shell commands that receive JSON on stdin and communicate via exit codes + stdout/stderr.

```json
{
  "type": "command",
  "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/my-script.sh",
  "async": false,
  "shell": "bash",
  "if": "Bash(git *)",
  "timeout": 600,
  "statusMessage": "Running validation..."
}
```

**Fields:**
- `command` (required): shell command to execute
- `async`: `true` runs in background without blocking (fire-and-forget)
- `shell`: `"bash"` (default) or `"powershell"` (Windows)
- `if`: permission rule syntax filter for tool events -- `"Bash(git *)"`, `"Edit(*.ts)"`
- `timeout`: seconds before canceling (default 600 = 10 minutes)
- `statusMessage`: custom spinner text while running

**Working directory:** the project root (`$CLAUDE_PROJECT_DIR`).

**Environment variables available:**

| Variable | Description |
|----------|-------------|
| `$CLAUDE_PROJECT_DIR` | Project root directory |
| `${CLAUDE_PLUGIN_ROOT}` | Plugin installation directory |
| `${CLAUDE_PLUGIN_DATA}` | Plugin persistent data directory |
| `$CLAUDE_CODE_REMOTE` | `"true"` in remote web environments, unset in CLI |
| `$CLAUDE_ENV_FILE` | File path for persisting env vars (SessionStart, CwdChanged, FileChanged) |

**Stdin/stdout contract:**
- **stdin**: JSON with common fields + event-specific fields
- **stdout**: plain text (added to context) or JSON for structured control
- **stderr**: on exit 2, becomes feedback to Claude; on other non-zero, goes to debug log
- **Exit 0**: action proceeds; stdout parsed for JSON or added as context
- **Exit 2**: action blocked; stderr fed to Claude as feedback
- **Any other exit**: non-blocking error; action proceeds; stderr in debug log

**Shell profile sourcing:** Claude Code spawns a shell that sources your profile
(`~/.zshrc` or `~/.bashrc`). If your profile has unconditional `echo` statements,
they pollute stdout and break JSON parsing. Guard them:

```bash
if [[ $- == *i* ]]; then
  echo "Shell ready"  # only in interactive shells
fi
```

### 3.2 HTTP Hooks (`type: "http"`)

POST event JSON to a URL endpoint. The endpoint returns results through the HTTP response body.

```json
{
  "type": "http",
  "url": "http://localhost:8080/hooks/pre-tool-use",
  "headers": {
    "Authorization": "Bearer $MY_TOKEN",
    "X-Project": "${PROJECT_NAME}"
  },
  "allowedEnvVars": ["MY_TOKEN", "PROJECT_NAME"],
  "timeout": 30
}
```

**Fields:**
- `url` (required): POST endpoint URL
- `headers`: key-value pairs with `$VAR_NAME` or `${VAR_NAME}` interpolation
- `allowedEnvVars`: whitelist of env vars that may be interpolated (required for interpolation to work; unlisted variables resolve to empty strings)
- `timeout`: seconds (default 30)

**Request format:** the same JSON that a command hook receives on stdin is sent as the POST body.

**Response handling:**

| HTTP Status | Body | Behavior |
|-------------|------|----------|
| 2xx | Empty | Success, no output (like exit 0 with no stdout) |
| 2xx | Plain text | Success, text added as context |
| 2xx | JSON | Success, parsed like command hook JSON output |
| Non-2xx | Any | Non-blocking error, execution continues |
| Connection failure/timeout | N/A | Non-blocking error, execution continues |

**Key difference from commands:** HTTP status codes alone cannot block actions. To block a
tool call, return a 2xx response with the appropriate `hookSpecificOutput` fields containing
a deny/block decision.

### 3.3 Prompt Hooks (`type: "prompt"`)

Single-turn LLM evaluation. Claude Code sends your prompt + the hook input to a fast model.

```json
{
  "type": "prompt",
  "prompt": "Is this Bash command safe to execute? Review carefully: $ARGUMENTS",
  "model": "claude-haiku",
  "timeout": 30
}
```

**Fields:**
- `prompt` (required): text sent to the model; use `$ARGUMENTS` to inject the hook's JSON input
- `model`: model alias (default: fast model, typically Haiku)
- `timeout`: seconds (default 30)

**How LLM judgment works:**
1. Claude Code takes your `prompt` text and replaces `$ARGUMENTS` with the JSON input for this event
2. The combined prompt is sent to the specified model in a single turn (no tool access)
3. The model returns a JSON decision

**Response format the model must return:**
```json
{"ok": true}
```
or
```json
{"ok": false, "reason": "Explanation of why this was blocked"}
```

- `"ok": true` -- action proceeds
- `"ok": false` -- action is blocked; `reason` is fed back to Claude as feedback

**When to use:** decisions that require judgment but no file access or multi-step reasoning.

### 3.4 Agent Hooks (`type: "agent"`)

Multi-turn subagent that can use tools (Read, Grep, Glob, Bash) to verify conditions.

```json
{
  "type": "agent",
  "prompt": "Verify all unit tests pass. Run the test suite and check results. $ARGUMENTS",
  "model": "claude-opus",
  "timeout": 120
}
```

**Fields:**
- `prompt` (required): task description; use `$ARGUMENTS` for hook input JSON
- `model`: model alias (default: fast model)
- `timeout`: seconds (default 60)

**How it differs from prompt type:**
- Spawns a full subagent with tool access (Read, Grep, Glob, Bash, etc.)
- Can perform multi-turn reasoning -- up to 50 tool-use turns
- Longer default timeout (60s vs 30s)
- Can inspect actual codebase state, run commands, read files
- Same response format: `{"ok": true}` or `{"ok": false, "reason": "..."}`

**When to use:** verification that requires inspecting files, running commands, or
multi-step reasoning against the actual state of the codebase.

### 3.5 Common Fields (All Hook Types)

- `type` (required): `"command"`, `"http"`, `"prompt"`, or `"agent"`
- `if`: permission rule syntax filter (tool events only)
- `timeout`: seconds (defaults vary by type)
- `statusMessage`: custom spinner text
- `once`: `true` runs only once per session (skills/plugins only)

---

## 4. Exit Codes and Control Flow

### 4.1 Exit Code Reference

| Code | Meaning | Stdout | Stderr |
|------|---------|--------|--------|
| **0** | Success | Parsed for JSON fields or added as context | Ignored |
| **2** | Blocking error | Ignored | Fed to Claude as feedback |
| **1, 3+** | Non-blocking error | Ignored | Shown in debug log / transcript |

**Exit code 1** and all other non-zero codes (except 2) are non-blocking errors.
The action proceeds, stderr appears in the debug transcript, and a one-line
`<hook name> hook error` notice appears in the transcript view.

### 4.2 Exit Code 2 Behavior Per Event

**Blocking events** (exit 2 prevents the action):
- `PreToolUse` -- blocks tool call
- `PermissionRequest` -- denies permission
- `UserPromptSubmit` -- blocks prompt, erases from context
- `Stop` -- prevents Claude from stopping (continues working)
- `SubagentStop` -- prevents subagent from stopping
- `TeammateIdle` -- prevents teammate going idle
- `TaskCreated` -- rolls back task creation
- `TaskCompleted` -- prevents completion mark
- `ConfigChange` -- blocks config change (not policy-level)
- `Elicitation` -- denies elicitation
- `ElicitationResult` -- blocks response
- `WorktreeCreate` -- any non-zero exit fails creation

**Non-blocking events** (exit 2 has no blocking effect):
- `PostToolUse`, `PostToolUseFailure`, `PermissionDenied`, `StopFailure`
- `Notification`, `SubagentStart`, `SessionStart`, `SessionEnd`
- `CwdChanged`, `FileChanged`, `PreCompact`, `PostCompact`

### 4.3 Hooks and Permission Modes

PreToolUse hooks fire **before** any permission-mode check. A hook returning
`permissionDecision: "deny"` blocks the tool even in `bypassPermissions` mode or with
`--dangerously-skip-permissions`. Hooks can tighten restrictions but not loosen them
past what permission rules allow. A hook returning `"allow"` does NOT override deny
rules from settings.

---

## 5. Matcher Patterns

### 5.1 Evaluation Rules

| Pattern | Evaluated As | Example |
|---------|-------------|---------|
| `"*"`, `""`, or omitted | Match all | Fires on every occurrence |
| Only letters, digits, `_`, `\|` | Exact string or `\|`-separated list | `Bash` or `Edit\|Write` |
| Contains other characters | JavaScript regex | `^Notebook`, `mcp__memory__.*` |

**Matchers are case-sensitive.** `"bash"` will NOT match the `Bash` tool.

### 5.2 The `if` Field (Argument-Level Filtering)

Beyond matcher (which filters by tool name at the group level), the `if` field uses
permission rule syntax to filter by tool name AND arguments together:

```json
{
  "if": "Bash(git *)",
  "command": "check-git-policy.sh"
}
```

- `"Bash(rm *)"` -- matches Bash commands starting with `rm`
- `"Edit(*.ts)"` -- matches Edit operations on TypeScript files
- Only works on tool events: PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest, PermissionDenied
- Adding `if` to any other event prevents the hook from running

### 5.3 MCP Tool Naming

MCP tools follow the pattern `mcp__<server>__<tool>`:

```
mcp__memory__create_entities
mcp__github__search_repositories
mcp__filesystem__read_file
```

Matcher examples:
- `mcp__memory__.*` -- all tools from the memory server
- `mcp__.*__write.*` -- any write tool from any server
- `mcp__memory__create_entities` -- exact tool match

---

## 6. Stdin/Stdout JSON Schema

### 6.1 JSON Output (Structured Control via Exit 0)

Universal fields available on any event:

```json
{
  "continue": true,
  "stopReason": "message when continue=false",
  "suppressOutput": false,
  "systemMessage": "warning to user",
  "decision": "block",
  "reason": "why blocked",
  "additionalContext": "injected into Claude's context",
  "sessionTitle": "new session name"
}
```

- `continue: false` stops Claude entirely; `stopReason` is shown
- `suppressOutput: true` omits stdout from debug log
- `additionalContext` -- text from ALL hooks is concatenated and passed to Claude
- Output capped at **10,000 characters**; excess saved to file with preview + path

### 6.2 Event-Specific Output Schemas

**PreToolUse:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow|deny|ask|defer",
    "permissionDecisionReason": "explanation fed to Claude",
    "updatedInput": { "command": "modified command" },
    "additionalContext": "context for Claude"
  }
}
```

Four decisions: `allow` (skip permission prompt), `deny` (cancel + feedback),
`ask` (show prompt), `defer` (non-interactive mode only, exits process with tool preserved).

**PermissionRequest:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow|deny",
      "updatedInput": { "command": "npm run lint" },
      "updatedPermissions": [
        {
          "type": "addRules|replaceRules|removeRules|setMode|addDirectories|removeDirectories",
          "rules": [{"toolName": "Bash", "ruleContent": "git *"}],
          "behavior": "allow|deny|ask",
          "mode": "acceptEdits",
          "destination": "session|localSettings|projectSettings|userSettings"
        }
      ],
      "message": "deny reason"
    }
  }
}
```

**PostToolUse:**
```json
{
  "decision": "block",
  "reason": "why",
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "context",
    "updatedMCPToolOutput": "replacement output"
  }
}
```

**Stop / SubagentStop / UserPromptSubmit / ConfigChange:**
```json
{
  "decision": "block",
  "reason": "explanation"
}
```

**PermissionDenied:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionDenied",
    "retry": true
  }
}
```

**WorktreeCreate (command):** print path to stdout.
**WorktreeCreate (http):**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "WorktreeCreate",
    "worktreePath": "/path/to/worktree"
  }
}
```

---

## 7. Practical Examples

### 7.1 Auto-Format Code After Edits

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
          }
        ]
      }
    ]
  }
}
```

### 7.2 Block Edits to Protected Files

```bash
#!/bin/bash
# .claude/hooks/protect-files.sh
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

PROTECTED_PATTERNS=(".env" "package-lock.json" ".git/")

for pattern in "${PROTECTED_PATTERNS[@]}"; do
  if [[ "$FILE_PATH" == *"$pattern"* ]]; then
    echo "Blocked: $FILE_PATH matches protected pattern '$pattern'" >&2
    exit 2
  fi
done
exit 0
```

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/protect-files.sh"
          }
        ]
      }
    ]
  }
}
```

### 7.3 Desktop Notifications (macOS)

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

### 7.4 Re-Inject Context After Compaction

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "compact",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Reminder: use Bun, not npm. Run bun test before committing. Current sprint: auth refactor.'"
          }
        ]
      }
    ]
  }
}
```

### 7.5 Block Dangerous Bash Commands

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(rm *)",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-rm.sh"
          }
        ]
      }
    ]
  }
}
```

### 7.6 HTTP Audit Logging

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "http",
            "url": "http://localhost:8080/hooks/tool-use",
            "headers": {
              "Authorization": "Bearer $AUDIT_TOKEN"
            },
            "allowedEnvVars": ["AUDIT_TOKEN"]
          }
        ]
      }
    ]
  }
}
```

### 7.7 Prompt-Based Safety Check

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Is this Bash command safe to execute? Could it delete files, expose secrets, or modify system configuration? Review: $ARGUMENTS",
            "model": "claude-haiku"
          }
        ]
      }
    ]
  }
}
```

### 7.8 Agent-Based Test Verification

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "agent",
            "prompt": "Verify that all unit tests pass. Run the test suite and check the results. $ARGUMENTS",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

### 7.9 Auto-Approve Plan Mode Exit

```json
{
  "hooks": {
    "PermissionRequest": [
      {
        "matcher": "ExitPlanMode",
        "hooks": [
          {
            "type": "command",
            "command": "echo '{\"hookSpecificOutput\": {\"hookEventName\": \"PermissionRequest\", \"decision\": {\"behavior\": \"allow\"}}}'"
          }
        ]
      }
    ]
  }
}
```

### 7.10 Environment Reload with direnv

```json
{
  "hooks": {
    "CwdChanged": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "direnv export bash >> \"$CLAUDE_ENV_FILE\""
          }
        ]
      }
    ]
  }
}
```

---

## 8. Hook Chaining and Execution Order

### 8.1 Parallel Execution

All matching hooks for an event run **in parallel**. There is no guaranteed execution
order between hooks in the same event.

### 8.2 Deduplication

Identical handlers are automatically deduplicated:
- Command hooks: deduplicated by command string
- HTTP hooks: deduplicated by URL

### 8.3 Decision Precedence (Multiple Hooks)

When multiple PreToolUse hooks return different decisions, the most restrictive wins:

```
deny > defer > ask > allow
```

A single `deny` cancels the tool call regardless of what other hooks return.
A single `ask` forces the permission prompt even if others return `allow`.

### 8.4 Context Aggregation

Text from `additionalContext` is kept from **every** hook and passed to Claude together
(concatenated).

### 8.5 Input Modification Conflicts

When multiple PreToolUse hooks return `updatedInput`, the last one to finish wins.
Since hooks run in parallel, the order is **non-deterministic**. Avoid having more
than one hook modify the same tool's input.

### 8.6 Scoping in Skills/Agents

Hooks defined in skill/agent frontmatter are scoped to that component's lifetime
and cleaned up when the skill/agent finishes.

---

## 9. The Stop Hook for Autonomous Loops (Ralph Loop Replacement)

### 9.1 How it Works

The Ralph Loop (`while true; do cat PROMPT.md | claude; done`) restarts Claude after
each completion to get fresh context. The **Stop hook** achieves the same effect natively:
when Claude finishes, the hook fires and can force continuation by returning exit 2
or `{"decision": "block"}`.

### 9.2 Basic Stop Hook

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/check-completion.sh"
          }
        ]
      }
    ]
  }
}
```

### 9.3 The Infinite Loop Problem

A Stop hook that always returns exit 2 creates an infinite loop:
1. Claude finishes -> Stop hook fires -> exit 2 -> Claude continues
2. Claude finishes -> Stop hook fires -> exit 2 -> Claude continues
3. Forever...

### 9.4 Prevention with `stop_hook_active`

The `stop_hook_active` field in the Stop event's JSON input indicates whether a Stop hook
already triggered continuation. Always check it:

```bash
#!/bin/bash
INPUT=$(cat)

# Prevent infinite loop: if we already forced continuation, let Claude stop
if [ "$(echo "$INPUT" | jq -r '.stop_hook_active')" = "true" ]; then
  exit 0  # Let Claude stop
fi

# Your completion check logic here
# e.g., check if all tasks in prd.json are done
INCOMPLETE=$(jq '[.tasks[] | select(.status != "done")] | length' prd.json)

if [ "$INCOMPLETE" -gt 0 ]; then
  echo "There are $INCOMPLETE incomplete tasks. Continue working." >&2
  exit 2  # Force continuation
fi

exit 0  # All done, let Claude stop
```

### 9.5 Prompt-Based Stop Hook (Simpler)

Use a prompt hook to let an LLM decide if work is complete:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check if all tasks are complete. If not, respond with {\"ok\": false, \"reason\": \"what remains to be done\"}."
          }
        ]
      }
    ]
  }
}
```

### 9.6 Agent-Based Stop Hook (Most Powerful)

The agent can actually run tests and verify completion:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "agent",
            "prompt": "Run the test suite and verify all tests pass. Check prd.json for incomplete tasks. If anything remains, return {\"ok\": false, \"reason\": \"description of what's left\"}.",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

### 9.7 Advantages Over Bash Loop

| Aspect | Bash Loop | Stop Hook |
|--------|-----------|-----------|
| Context | Fresh each iteration (no rot) | Same session (possible rot) |
| State | Filesystem only | Filesystem + conversation context |
| Cost | Re-reads all context each time | Continues existing context |
| Safety | Iteration count limit | `stop_hook_active` + iteration tracking |
| Setup | External script | Native configuration |
| Verification | Must be in prompt | Can use agent hooks with tool access |

### 9.8 The Official Ralph Plugin

Anthropic absorbed the pattern into the native `/loop` command and the `ralph-loop` plugin.
The plugin uses `--max-iterations` and `--completion-promise` for safety:

```bash
/ralph-loop "implement all tasks in prd.json" --max-iterations 10 --completion-promise "DONE"
```

---

## 10. Debugging Hooks

### 10.1 The `/hooks` Menu

Type `/hooks` in Claude Code to browse all configured hooks grouped by event. Shows:
- Hook count per event
- Type prefix: `[command]`, `[prompt]`, `[agent]`, `[http]`
- Source labels: `[User]`, `[Project]`, `[Local]`, `[Plugin]`, `[Session]`, `[Built-in]`
- Read-only -- edit settings JSON directly to modify

### 10.2 Transcript View

Toggle with `Ctrl+O`. Shows one-line summaries:
- Success: silent
- Blocking error (exit 2): shows stderr
- Non-blocking error: `<hook name> hook error` + first line of stderr

### 10.3 Debug Log

Full execution details (matched hooks, exit codes, stdout, stderr):

```bash
claude --debug-file /tmp/claude.log
# In another terminal:
tail -f /tmp/claude.log
```

Or mid-session: run `/debug` to enable logging and find the log path.

### 10.4 Manual Testing

Test hook scripts by piping sample JSON:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' | ./my-hook.sh
echo $?  # Should be 2 for blocked
```

### 10.5 Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| Hook not firing | Matcher case mismatch | Matchers are case-sensitive: `Bash` not `bash` |
| Hook not firing | Wrong event type | `PreToolUse` fires before, `PostToolUse` after |
| Hook not firing | `PermissionRequest` in `-p` mode | Use `PreToolUse` for non-interactive |
| JSON parse error | Shell profile `echo` statements | Guard with `[[ $- == *i* ]]` check |
| "command not found" | Relative paths | Use absolute paths or `$CLAUDE_PROJECT_DIR` |
| Unexpected blocking | Script exits non-zero | `grep` returns 1 on no match; add `\|\| true` |
| Stop hook infinite loop | No `stop_hook_active` check | Always check and exit 0 when true |
| `/hooks` shows nothing | Invalid JSON in settings | Check for trailing commas, comments |
| Stale hooks | File watcher missed change | Restart session to force reload |

### 10.6 Disabling All Hooks

```json
{
  "disableAllHooks": true
}
```

Respects managed settings hierarchy: user/project/local settings cannot disable
managed hooks. Only managed-level `disableAllHooks` can disable managed hooks.

---

## 11. Tool Input Schemas (For Writing PreToolUse Hooks)

When writing hooks that inspect tool input, these are the key fields per tool:

| Tool | Key Input Fields |
|------|-----------------|
| **Bash** | `command`, `description`, `timeout`, `run_in_background` |
| **Write** | `file_path`, `content` |
| **Edit** | `file_path`, `old_string`, `new_string`, `replace_all` |
| **Read** | `file_path`, `offset`, `limit` |
| **Glob** | `pattern`, `path` |
| **Grep** | `pattern`, `path`, `glob`, `output_mode`, `-i`, `multiline` |
| **WebFetch** | `url`, `prompt` |
| **WebSearch** | `query`, `allowed_domains`, `blocked_domains` |
| **Agent** | `prompt`, `description`, `subagent_type`, `model` |

---

## Sources

- [Hooks Reference -- Claude Code Docs](https://code.claude.com/docs/en/hooks)
- [Automate Workflows with Hooks -- Claude Code Docs](https://code.claude.com/docs/en/hooks-guide)
- [Claude Code Hooks: Complete Guide to All 12 Lifecycle Events](https://claudefa.st/blog/tools/hooks/hooks-guide)
- [Claude Code Stop Hook: Force Task Completion](https://claudefa.st/blog/tools/hooks/stop-hook-task-enforcement)
- [Claude Code Hooks Complete Guide -- SmartScope](https://smartscope.blog/en/generative-ai/claude/claude-code-hooks-guide/)
- [Claude Code Hook Control Flow -- Steve Kinney](https://stevekinney.com/courses/ai-development/claude-code-hook-control-flow)
- [Ralph Wiggum: Autonomous Loops for Claude Code](https://paddo.dev/blog/ralph-wiggum-autonomous-loops/)
- [Claude Code Hooks Reference: All 12 Events -- Pixelmojo](https://www.pixelmojo.io/blogs/claude-code-hooks-production-quality-ci-cd-patterns)
