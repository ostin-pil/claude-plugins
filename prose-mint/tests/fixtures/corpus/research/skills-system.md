# Claude Code Skills System -- Deep Reference

*Compiled: 2026-04-09*

---

## 1. Overview

Skills extend what Claude Code can do. A skill is a directory containing a `SKILL.md` file with YAML frontmatter and markdown instructions. Skills load on demand (unlike CLAUDE.md which loads every session), so long reference material costs almost nothing until invoked.

Claude Code skills follow the [Agent Skills](https://agentskills.io) open standard (originally created by Anthropic, December 2025). The standard is cross-platform -- skills work in Claude Code, OpenAI Codex, Gemini CLI, GitHub Copilot, Cursor, VS Code, and 20+ other platforms. Claude Code extends the standard with invocation control, subagent execution, dynamic context injection, and hooks.

**Custom commands (`.claude/commands/`) have been merged into skills.** Both `.claude/commands/deploy.md` and `.claude/skills/deploy/SKILL.md` create `/deploy`. Existing commands files keep working. Skills add supporting files, frontmatter controls, and auto-invocation.

---

## 2. File Structure

### Skill directory layout

```
my-skill/
  SKILL.md           # Required: frontmatter + instructions
  template.md        # Optional: template for Claude to fill in
  examples/
    sample.md        # Optional: example output showing expected format
  scripts/
    validate.sh      # Optional: script Claude can execute
  references/
    REFERENCE.md     # Optional: detailed docs loaded on demand
  assets/
    schema.json      # Optional: static resources
```

### Where skills live (resolution order)

| Scope      | Path                                         | Applies to                     |
|:-----------|:---------------------------------------------|:-------------------------------|
| Enterprise | Managed settings (see docs)                  | All users in your organization |
| Personal   | `~/.claude/skills/<name>/SKILL.md`           | All your projects              |
| Project    | `.claude/skills/<name>/SKILL.md`             | This project only              |
| Plugin     | `<plugin>/skills/<name>/SKILL.md`            | Where plugin is enabled        |

**Priority:** enterprise > personal > project. Plugin skills use `plugin-name:skill-name` namespace (no conflicts).

### Automatic discovery

- **Nested directories**: editing files in `packages/frontend/` also discovers skills from `packages/frontend/.claude/skills/`. Supports monorepos.
- **Additional directories**: `--add-dir` loads `.claude/skills/` from added directories (exception to the general rule that `--add-dir` only grants file access). Live change detection works.
- **Commands directory**: `.claude/commands/*.md` still works. If a skill and command share the same name, the skill takes precedence.

---

## 3. SKILL.md Frontmatter -- Complete Reference

All fields are optional. Only `description` is recommended.

```yaml
---
name: my-skill
description: What this skill does and when to use it
argument-hint: "[issue-number]"
disable-model-invocation: true
user-invocable: true
allowed-tools: Read Grep Bash(git *)
model: claude-sonnet-4-20250514
effort: high
context: fork
agent: Explore
paths: "**/*.swift, **/*.ts"
shell: bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh"
---
```

### Field-by-field reference

#### `name`
- **Type:** string
- **Default:** directory name
- **Constraints:** lowercase letters, numbers, hyphens only. Max 64 chars. Must match parent directory name (per the open standard). No leading/trailing/consecutive hyphens.
- **Effect:** becomes the `/slash-command` name.

#### `description`
- **Type:** string
- **Default:** first paragraph of markdown content
- **Constraints:** max 1024 chars (open standard). Claude Code truncates at 250 chars in skill listings.
- **Effect:** Claude uses this to decide when to auto-load the skill. Front-load the key use case. If omitted, Claude may not discover the skill automatically.
- **Context budget:** skill descriptions share a budget of 1% of the context window (fallback: 8,000 chars). Tune with `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var.

#### `argument-hint`
- **Type:** string
- **Default:** none
- **Effect:** shown during autocomplete in the `/` menu. Examples: `[issue-number]`, `[filename] [format]`, `[component] [from] [to]`.

#### `disable-model-invocation`
- **Type:** boolean
- **Default:** `false`
- **Effect:** when `true`, only the user can invoke via `/name`. Claude cannot trigger it automatically. The skill description is NOT loaded into context at all.
- **Use for:** workflows with side effects (`/deploy`, `/commit`, `/send-slack-message`).

#### `user-invocable`
- **Type:** boolean
- **Default:** `true`
- **Effect:** when `false`, hides from the `/` menu. Only Claude can invoke it. Description IS loaded into context.
- **Use for:** background knowledge that is not a meaningful user action (`legacy-system-context`).
- **Note:** `user-invocable` only controls menu visibility, not Skill tool access. Use `disable-model-invocation: true` to block programmatic invocation.

#### Invocation matrix

| Frontmatter                      | User can invoke | Claude can invoke | Context loading                                              |
|:---------------------------------|:----------------|:------------------|:-------------------------------------------------------------|
| (default)                        | Yes             | Yes               | Description always in context; full skill loads when invoked |
| `disable-model-invocation: true` | Yes             | No                | Description NOT in context; loads only when user invokes     |
| `user-invocable: false`          | No              | Yes               | Description always in context; loads when Claude invokes     |

#### `allowed-tools`
- **Type:** space-separated string or YAML list
- **Default:** none (normal permission rules apply)
- **Effect:** grants permission for listed tools without prompting while the skill is active. Does NOT restrict available tools -- every tool remains callable.
- **Pattern syntax:** tool name with optional argument pattern.
  - `Read` -- pre-approve all Read calls
  - `Grep` -- pre-approve all Grep calls
  - `Bash(git add *)` -- pre-approve bash commands matching `git add *`
  - `Bash(gh *)` -- pre-approve GitHub CLI commands
  - `Bash(python *)` -- pre-approve python commands
- **With `context: fork`:** creates a "policy island" where the forked agent inherits only these permissions and executes matching commands without prompting.
- **Blocking tools:** add deny rules in your permission settings instead (not in the skill).

#### `model`
- **Type:** string
- **Default:** inherits from session
- **Effect:** overrides which Claude model is used when this skill is active.
- **Use for:** cost optimization (use Haiku for simple tasks) or capability (use Opus for reasoning-heavy skills).

#### `effort`
- **Type:** `low` | `medium` | `high` | `max`
- **Default:** inherits from session
- **Effect:** overrides the session effort level for this skill. `max` is Opus 4.6 only.
- **Use for:** heavy research tasks that benefit from more reasoning (`effort: max`) or quick lookups that do not (`effort: low`).

#### `context`
- **Type:** `fork` | (omit for inline)
- **Default:** inline (runs in your conversation context)
- **Effect:** when `fork`, runs in an isolated subagent. See Section 6 for details.

#### `agent`
- **Type:** string
- **Default:** `general-purpose`
- **Options:** `Explore`, `Plan`, `general-purpose`, or any custom subagent from `.claude/agents/`
- **Effect:** only meaningful when `context: fork`. Determines the execution environment (model, tools, permissions) for the forked subagent.
- **`Explore`:** read-only tools optimized for codebase exploration (Glob, Grep, Read).
- **`Plan`:** planning-focused toolset.
- **`general-purpose`:** full tool access.

#### `paths`
- **Type:** comma-separated string or YAML list of glob patterns
- **Default:** none (skill is always eligible for auto-activation)
- **Effect:** Claude loads the skill automatically only when working with files matching the patterns. Same glob format as path-specific CLAUDE.md rules.
- **Example:** `paths: "**/*.swift, Sources/**"` -- only activate when working on Swift files.

#### `shell`
- **Type:** `bash` | `powershell`
- **Default:** `bash`
- **Effect:** which shell to use for `!`command`` and ` ```! ` blocks. `powershell` requires `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`.

#### `hooks`
- **Type:** YAML mapping (same schema as settings.json hooks)
- **Default:** none
- **Effect:** hooks scoped to this skill's lifecycle. Run only while the skill is active. Cleaned up when the skill finishes.
- **Supported events:** `PreToolUse`, `PostToolUse`, `Stop` (all hook events work)
- **Hook types:** `command`, `http`, `prompt`, `agent`
- **Special fields:** `once: true` runs the hook only once per session then removes it (skills only)

```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-input.sh"
          timeout: 10
          statusMessage: "Validating..."
  PostToolUse:
    - matcher: "Write"
      hooks:
        - type: command
          command: "npm run lint --fix"
```

### Open standard fields (agentskills.io)

These additional fields are part of the open standard but not Claude Code-specific:

| Field           | Required (standard) | Claude Code behavior                            |
|:----------------|:--------------------|:------------------------------------------------|
| `name`          | Yes                 | Optional in Claude Code (defaults to dir name)  |
| `description`   | Yes                 | Recommended in Claude Code (not strictly required) |
| `license`       | No                  | Informational only                              |
| `compatibility` | No                  | Max 500 chars. Indicates environment requirements |
| `metadata`      | No                  | Arbitrary key-value pairs for custom properties  |

---

## 4. String Substitutions

Skills support these dynamic placeholders in the markdown content:

| Variable               | Description                                                                                   |
|:-----------------------|:----------------------------------------------------------------------------------------------|
| `$ARGUMENTS`           | Full argument string as typed after `/skill-name`. If not present in content, appended as `ARGUMENTS: <value>`. |
| `$ARGUMENTS[N]`        | Access specific argument by 0-based index. `$ARGUMENTS[0]` = first arg.                       |
| `$N`                   | Shorthand for `$ARGUMENTS[N]`. `$0` = first, `$1` = second, etc.                             |
| `${CLAUDE_SESSION_ID}` | Current session ID. Useful for logging, session-specific files, correlation.                   |
| `${CLAUDE_SKILL_DIR}`  | Directory containing this skill's `SKILL.md`. For plugin skills, the skill subdirectory (not plugin root). |

### Quoting behavior

Indexed arguments use **shell-style quoting**. Multi-word values must be wrapped in quotes:

```
/migrate-component "hello world" second
```

- `$0` / `$ARGUMENTS[0]` = `hello world`
- `$1` / `$ARGUMENTS[1]` = `second`
- `$ARGUMENTS` = `"hello world" second` (full string as typed)

### Fallback behavior

If you invoke a skill with arguments but the skill content does not contain `$ARGUMENTS`, Claude Code appends `ARGUMENTS: <your input>` to the end of the rendered content.

### Example

```yaml
---
name: fix-issue
description: Fix a GitHub issue by number
disable-model-invocation: true
argument-hint: "[issue-number]"
---

Fix GitHub issue #$ARGUMENTS following our coding standards.

Session: ${CLAUDE_SESSION_ID}
Scripts at: ${CLAUDE_SKILL_DIR}/scripts/
```

Running `/fix-issue 42` renders: "Fix GitHub issue #42 following our coding standards..."

---

## 5. Dynamic Command Injection

### Inline syntax: `` !`command` ``

Shell commands inside `` !`command` `` are executed as **preprocessing** before the skill content is sent to Claude. The command output replaces the placeholder. Claude never sees the command -- only the result.

```yaml
---
name: pr-summary
description: Summarize the current pull request
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

Summarize this pull request.
```

**Execution flow:**
1. Each `` !`command` `` executes immediately (before Claude sees anything)
2. Command stdout replaces the placeholder in the skill content
3. Claude receives the fully-rendered prompt with actual data

### Multi-line syntax: fenced code blocks

For multiple commands, use a fenced code block opened with ` ```! `:

````markdown
## Environment
```!
node --version
npm --version
git status --short
```
````

All commands in the block run, and combined output replaces the block.

### What you can run

Any shell command available in your environment. Common patterns:
- `git log --oneline -5` -- recent commits
- `gh pr diff` -- pull request data
- `cat package.json | jq .version` -- extract project data
- `ls src/` -- directory listing
- `python scripts/analyze.py` -- custom scripts
- `curl -s https://api.example.com/status` -- API calls

### Security considerations

**Known issue:** `$ARGUMENTS` passed into `` !`command` `` is not escaped. User input flows directly to bash without sanitization. Be cautious about skills that pass user arguments into shell commands.

### Disabling shell execution

Set `"disableSkillShellExecution": true` in settings to disable `` !`command` `` for user/project/plugin skills. Each command is replaced with `[shell command execution disabled by policy]`. Bundled and managed skills are NOT affected. Most useful in managed settings where users cannot override.

### Size limits

No documented hard limit on command output size. However, the rendered skill content enters the conversation as a single message and stays for the session. Practical limit is context window size. Keep output reasonable -- pipe through `head` or `tail` if needed.

---

## 6. Context Isolation (`context: fork`)

### What happens when you fork

When a skill has `context: fork`:

1. A **new isolated context** is created (fresh subagent)
2. The rendered SKILL.md content becomes the **task prompt** for the subagent
3. The subagent has **no access to your conversation history**
4. The `agent` field determines the execution environment (model, tools, permissions)
5. CLAUDE.md files **are loaded** in the forked context
6. Results are **summarized and returned** to your main conversation

### What is shared vs isolated

| Aspect                | Shared                          | Isolated                        |
|:----------------------|:--------------------------------|:--------------------------------|
| Conversation history  |                                 | Not available to subagent       |
| CLAUDE.md rules       | Loaded in fork                  |                                 |
| File system           | Same filesystem                 |                                 |
| Permission settings   | Base permissions apply          | `allowed-tools` can override    |
| Tool availability     | Determined by `agent` type      | Not same as parent session      |
| Session ID            | Same `${CLAUDE_SESSION_ID}`     |                                 |
| Skill descriptions    |                                 | Not inherited from parent       |

### Skills vs subagents (two directions)

| Approach                     | System prompt                             | Task                        | Also loads          |
|:-----------------------------|:------------------------------------------|:----------------------------|:--------------------|
| Skill with `context: fork`   | From agent type (`Explore`, `Plan`, etc.) | SKILL.md content            | CLAUDE.md           |
| Subagent with `skills` field | Subagent's markdown body                  | Claude's delegation message | Preloaded skills + CLAUDE.md |

### When to use fork

- **Research tasks** -- read-only exploration that should not pollute conversation context
- **Expensive operations** -- keep main context clean for follow-up work
- **Parallel work** -- forked skills can run independently
- **Security boundaries** -- `allowed-tools` in a fork creates a "policy island"

### When NOT to use fork

- **Reference content** -- guidelines like "use these API conventions" without a task produce no meaningful output in a fork
- **Interactive workflows** -- when you need back-and-forth conversation
- **Small tasks** -- overhead of fork is not worth it for quick lookups

---

## 7. Skill Content Lifecycle

### Loading

- **At session start:** all non-disabled skill descriptions are loaded into context (names + truncated descriptions)
- **On invocation:** full SKILL.md content enters conversation as a single message
- **No re-reading:** Claude Code does not re-read the file on later turns

### Compaction behavior

When auto-compaction fires:
- Most recent invocation of each skill is re-attached after the summary
- Each skill keeps first **5,000 tokens** max
- Combined budget for all re-attached skills: **25,000 tokens**
- Budget fills starting from most recently invoked skill
- Older skills can be **dropped entirely** if many skills were invoked

### Implications for authoring

- Write guidance as **standing instructions**, not one-time steps
- If behavior fades after compaction, re-invoke the skill
- Keep SKILL.md under 500 lines; move detail to supporting files
- Strengthen description + instructions if model stops following the skill

---

## 8. Skill Composition and Interaction with CLAUDE.md

### Can skills call other skills?

Yes. Claude can invoke the `Skill` tool during execution. A skill's instructions can tell Claude to invoke another skill. However:
- Built-in commands (`/compact`, `/init`) are NOT available through the Skill tool
- Skills with `disable-model-invocation: true` cannot be invoked by Claude (even from another skill)
- Permission rules can allow/deny specific skill invocations: `Skill(commit)`, `Skill(deploy *)`

### Skill + CLAUDE.md interaction

- **CLAUDE.md rules are always active.** They load at session start and persist.
- **Skills load on demand.** They only enter context when invoked.
- **CLAUDE.md applies inside forked skills.** Forked subagents load CLAUDE.md.
- **No override mechanism.** If CLAUDE.md says "never do X" and a skill says "do X", there is a conflict. Claude generally follows the more specific instruction, but behavior is non-deterministic.

### When to use which

| Content type                                  | Put in CLAUDE.md | Put in a Skill |
|:----------------------------------------------|:-----------------|:---------------|
| Rules that apply to every task                | Yes              |                |
| Commit message format                         | Yes              |                |
| Coding conventions                            | Yes              |                |
| Deployment workflow                           |                  | Yes            |
| PR review checklist                           |                  | Yes            |
| Domain-specific reference docs                |                  | Yes            |
| Background knowledge for specific subsystems  |                  | Yes            |

### Orchestration patterns

For skills with sequencing requirements (brainstorm -> plan -> execute), make the order explicit in a **top-level orchestration skill** rather than burying dependencies in individual skills:

```yaml
---
name: ship-feature
description: End-to-end feature shipping workflow
disable-model-invocation: true
---

Execute these phases in order:

1. /research $ARGUMENTS
2. Review research output with user
3. /plan based on research findings
4. /implement based on approved plan
5. /verify implementation
6. /commit with descriptive message
```

---

## 9. Project vs Personal Skills -- Scope Strategy

### Personal skills (`~/.claude/skills/`)

- Available across ALL projects
- Not committed to version control
- Good for: personal workflow preferences, general-purpose utilities, cross-project tools
- Examples: `/explain-code`, `/session-logger`, `/codebase-visualizer`

### Project skills (`.claude/skills/`)

- Scoped to one project
- Committed to version control (shared with team)
- Good for: project-specific workflows, team conventions, CI/CD integration
- Examples: `/build`, `/deploy`, `/verify`, `/phase`

### Team sharing patterns

1. **Project repo**: commit `.claude/skills/` to version control. Every team member gets the skills.
2. **Plugin distribution**: create a plugin with a `skills/` directory. Enable per-project.
3. **Managed settings**: deploy organization-wide through enterprise managed settings. Users cannot override.
4. **Shared skill repos**: maintain a repo of skills, add via `--add-dir` or symlinks.

---

## 10. Practical Skill Examples

### Code review skill

```yaml
---
name: review
description: Review code changes for quality, security, and correctness
context: fork
agent: Explore
allowed-tools: Bash(git diff *) Bash(git log *) Read Grep Glob
---

Review the current changes:

## Context
- Diff: !`git diff --cached`
- Recent commits: !`git log --oneline -5`

## Review checklist
1. **Correctness**: Does the code do what it claims?
2. **Security**: Any injection, auth, or data exposure issues?
3. **Performance**: N+1 queries, unnecessary allocations, blocking calls?
4. **Style**: Consistent with codebase conventions?
5. **Tests**: Are changes covered by tests?

Provide findings as a structured list with severity (critical/warning/info).
```

### Deployment skill with hooks

```yaml
---
name: deploy
description: Deploy application to production
disable-model-invocation: true
allowed-tools: Bash(git *) Bash(npm *) Bash(aws *)
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "echo 'Deploy action: running...'"
---

Deploy $ARGUMENTS to production:

1. Verify all tests pass: `npm test`
2. Build production bundle: `npm run build`
3. Tag release: `git tag -a v$0 -m "Release $0"`
4. Push tag: `git push origin v$0`
5. Deploy: `aws s3 sync dist/ s3://prod-bucket/`
6. Invalidate CDN: `aws cloudfront create-invalidation --distribution-id $DIST_ID --paths "/*"`
7. Verify health check passes
```

### Documentation generator with scripts

```yaml
---
name: gen-api-docs
description: Generate API documentation from source code
allowed-tools: Bash(python *) Read Write
argument-hint: "[output-dir]"
---

Generate API documentation:

1. Run the doc extraction script:
   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/extract-api.py --output $0
   ```
2. Review generated docs for completeness
3. Add any missing descriptions
4. Format with consistent headers and examples
```

### Testing skill

```yaml
---
name: test-focused
description: Run and analyze tests for specific files or components
allowed-tools: Bash(swift test *) Bash(npm test *) Read Grep
argument-hint: "[file-or-component]"
---

Test $ARGUMENTS:

1. Identify related test files using naming conventions
2. Run only the relevant tests
3. If tests fail:
   - Show the failure output
   - Identify the root cause
   - Suggest a fix (but do NOT implement it)
4. If all pass, report coverage if available
```

### Session logging skill (from this project)

```yaml
---
name: session
description: Update or create today's session log
allowed-tools: Read Write Glob Bash(git log *) Bash(git diff *)
---

Update the session log in sessions/:

1. Check for existing log: !`ls sessions/ | tail -5`
2. Recent activity: !`git log --oneline -10`

Create or update today's log with:
- What was done this session
- Key decisions made
- Files changed
- What to do next
```

---

## 11. Advanced Patterns

### Skills that bundle scripts

The most powerful pattern is skills with bundled scripts. The skill orchestrates; the script does heavy lifting.

```
codebase-visualizer/
  SKILL.md                    # Instructions to run the script
  scripts/
    visualize.py              # Generates interactive HTML
```

The `${CLAUDE_SKILL_DIR}` substitution lets scripts reference their own directory regardless of working directory:

```yaml
---
name: codebase-visualizer
description: Generate interactive codebase tree visualization
allowed-tools: Bash(python *)
---

Run from project root:
```bash
python ${CLAUDE_SKILL_DIR}/scripts/visualize.py .
```
```

### Skills with templates

Bundle templates that Claude fills in:

```
changelog-generator/
  SKILL.md
  templates/
    changelog-entry.md        # Template for each entry
    release-notes.md          # Template for release notes
```

```yaml
---
name: changelog
description: Generate changelog from recent commits
---

Read the template at ${CLAUDE_SKILL_DIR}/templates/changelog-entry.md
and fill it in using: !`git log --oneline --since="1 week ago"`
```

### Extended thinking in skills

Include the word `ultrathink` anywhere in skill content to enable extended thinking:

```yaml
---
name: architect
description: Deep architectural analysis
effort: max
---

ultrathink

Analyze the architecture of $ARGUMENTS:
1. Map all dependencies
2. Identify coupling patterns
3. Suggest improvements
```

### Skills that invoke external tools

```yaml
---
name: security-audit
description: Run security analysis on the codebase
context: fork
allowed-tools: Bash(semgrep *) Bash(codeql *) Read Grep
---

Run a security audit:

1. Semgrep scan: `semgrep --config auto .`
2. Check for secrets: `grep -r "API_KEY\|SECRET\|PASSWORD" --include="*.{ts,js,py}" .`
3. Review dependency vulnerabilities: `npm audit` or `pip audit`
4. Summarize findings by severity
```

### Permission control patterns

**Disable all skill invocation by Claude:**
```
# In deny rules:
Skill
```

**Allow only specific skills:**
```
Skill(commit)
Skill(review-pr *)
```

**Deny specific skills:**
```
Skill(deploy *)
```

---

## 12. Community Ecosystem

The skills ecosystem has grown substantially. Key resources:

### Curated collections

- **[awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)** -- skills, hooks, slash-commands, agent orchestrators, plugins
- **[awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills)** -- curated skills and resources for Claude AI workflows
- **[awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)** -- 1000+ skills compatible with Claude Code, Codex, Cursor, Gemini CLI
- **[awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit)** -- 135 agents, 35+ skills, 42 commands, 176+ plugins
- **[antigravity-awesome-skills](https://github.com/sickn33/antigravity-awesome-skills)** -- 1,370+ installable skills with CLI

### Notable skill packages

| Package                          | Author              | Focus                                              |
|:---------------------------------|:--------------------|:---------------------------------------------------|
| Trail of Bits Security Skills    | Trail of Bits       | CodeQL, Semgrep, variant analysis, security auditing |
| Fullstack Dev Skills             | jeffallan           | 65 specialized skills + 9 workflow commands          |
| Claude Scientific Skills         | K-Dense             | Research, science, engineering, academic writing     |
| Superpowers                      | Jesse Vincent       | Planning, reviewing, testing, debugging (SDLC)       |
| cc-devops-skills                 | akin-ozer           | IaC code generation across platforms                 |
| Context Engineering Kit          | Vlad Goncharov      | Advanced context patterns, minimal token footprint   |
| read-only-postgres               | jawwadfirdousi      | PostgreSQL queries with validation and row limits    |
| Web Assets Generator             | Alon Wolenitz       | Favicons, app icons, social media meta images        |

---

## 13. Troubleshooting

### Skill not triggering

1. Ensure description contains keywords matching natural requests
2. Verify skill appears: ask "What skills are available?"
3. Rephrase to match description keywords
4. Invoke directly with `/skill-name`
5. Check if `paths` filter is excluding your current files

### Skill triggers too often

1. Make description more specific
2. Add `disable-model-invocation: true`

### Skill descriptions cut short

Descriptions share a budget of 1% of context window (fallback: 8,000 chars). Names are always included but descriptions get truncated.
- Front-load the key use case (each entry capped at 250 chars)
- Set `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var to increase limit

### Skill stops working after long conversation

Auto-compaction may have dropped it. Re-invoke the skill. Each skill keeps only 5,000 tokens after compaction; combined budget is 25,000 tokens for all skills.

### Shell injection commands not running

Check `disableSkillShellExecution` in settings. If `true`, all `` !`command` `` calls are replaced with `[shell command execution disabled by policy]`.

---

## 14. Sources

- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
- [Claude Code Slash Commands](https://code.claude.com/docs/en/slash-commands)
- [Agent Skills Open Standard Specification](https://agentskills.io/specification)
- [Agent Skills SDK (Claude)](https://code.claude.com/docs/en/agent-sdk/skills)
- [Claude Code Hooks Reference](https://code.claude.com/docs/en/hooks)
- [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)
- [awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills)
- [awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)
- [Claude Code Advanced Patterns: Skills, Fork, and Subagents](https://www.trensee.com/en/blog/explainer-claude-code-skills-fork-subagents-2026-03-31)
- [A Mental Model for Claude Code: Skills, Subagents, and Plugins](https://levelup.gitconnected.com/a-mental-model-for-claude-code-skills-subagents-and-plugins-3dea9924bf05)
- [How Agent Skills Fork Governed Sub-Agents in Claude Code 2.1](https://medium.com/@richardhightower/from-approval-hell-to-just-do-it-how-agent-skills-fork-governed-sub-agents-in-claude-code-2-1-c0438416433a)
- [Skills Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
