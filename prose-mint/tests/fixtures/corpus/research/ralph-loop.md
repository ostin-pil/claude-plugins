# The Ralph Wiggum Loop: Deep Dive

*Compiled: 2026-04-09*
*See also: research/claude-code-workflows.md (section 1) for summary*

---

## Origin and Philosophy

The Ralph Wiggum Loop (or simply "Ralph") was created by Geoffrey Huntley, an Australian developer. Named after the Simpsons character who is "dumb but persistent," the technique embodies an insight: **persistent iteration beats clever prompting**. The loop doesn't need to be smart on any single pass -- it just needs to keep going, correcting itself each time.

Huntley proved the concept by running a Ralph loop for three consecutive months with a single prompt: "Make me a programming language like Golang but with Gen Z slang keywords." The result was CURSED -- a functional compiler with LLVM compilation to native binaries, a standard library, two execution modes, and partial editor support.

The technique went viral in late 2025/early 2026 and spawned an ecosystem of implementations, a Claude Code plugin, and multiple community forks.

---

## 1. The Repo Structure (snarktank/ralph)

Ryan Carson's snarktank/ralph (15.1k stars) is the most popular structured implementation. Repository layout:

```
ralph/
├── .claude-plugin/              # Claude Code marketplace manifest
├── .github/workflows/           # CI
├── flowchart/                   # Interactive React visualization
├── skills/
│   ├── prd/                     # Skill: generate PRD from conversation
│   └── ralph/                   # Skill: convert PRD markdown to JSON
├── AGENTS.md                    # Operational reference (project patterns)
├── CLAUDE.md                    # System prompt for Claude Code
├── prompt.md                    # System prompt for Amp
├── ralph.sh                     # The bash loop script
├── prd.json.example             # Reference schema
└── ralph.webp                   # Logo
```

### prd.json Schema

The PRD is a flat JSON file with a branch name and an ordered array of user stories:

```json
{
  "branchName": "feature-auth-flow",
  "userStories": [
    {
      "id": "story-001",
      "title": "Add login endpoint",
      "description": "Create POST /api/auth/login accepting email+password",
      "acceptanceCriteria": [
        "Returns JWT on valid credentials",
        "Returns 401 on invalid credentials",
        "Rate-limited to 5 attempts per minute"
      ],
      "priority": 1,
      "passes": false
    },
    {
      "id": "story-002",
      "title": "Add session middleware",
      "description": "Verify JWT on protected routes",
      "acceptanceCriteria": [
        "Rejects expired tokens",
        "Attaches user object to request"
      ],
      "priority": 2,
      "passes": false
    }
  ]
}
```

Key fields:
- **`branchName`** -- Git branch created automatically for the feature
- **`priority`** -- Integer; lower = higher priority. Agent always picks the lowest-priority-number incomplete story
- **`passes`** -- Boolean flipped to `true` when the story's acceptance criteria are verified
- **`acceptanceCriteria`** -- Array of strings; each must be testable/verifiable

Sizing guidance: stories should be atomic units completable in a single context window. Good: "Add a database column and migration." Bad: "Build the entire dashboard."

### progress.txt

Append-only learnings file. Each iteration the agent writes discoveries:

```
## Iteration 3 (2026-04-08)
- Discovered that `prisma generate` must run before tests
- Auth middleware uses req.user, not req.session
- Rate limiter config is in src/config/limits.ts
```

This is the agent's long-term memory across context resets. Future iterations read it to avoid repeating mistakes.

### AGENTS.md

Operational reference loaded every iteration. Contains:
- Build/test/lint commands for the project
- Environment setup instructions
- Known gotchas and workarounds
- Codebase conventions

**Critical rule**: Keep it brief and operational. Status updates belong in progress.txt or IMPLEMENTATION_PLAN.md. A bloated AGENTS.md pollutes every future iteration's context budget.

### The Loop Lifecycle

Each ralph.sh iteration:
1. Create/checkout feature branch from `branchName`
2. Select highest-priority incomplete story (`passes: false`)
3. Implement the story via the AI coding tool
4. Run quality checks (typecheck, tests, lint)
5. If checks pass: commit, mark story `passes: true`
6. Append learnings to `progress.txt`
7. Exit -- loop restarts with fresh context
8. Repeat until all stories pass or max iterations reached

Completion signal: when all stories have `passes: true`, the agent outputs `<promise>COMPLETE</promise>` and the loop exits.

---

## 2. Huntley's Original Method (how-to-ralph-wiggum)

Huntley's own repo (ghuntley/how-to-ralph-wiggum) differs from snarktank/ralph in several important ways. It uses a two-mode loop with separate planning and building prompts:

### Repository Structure

```
project-root/
├── loop.sh                    # Orchestration script (plan or build mode)
├── PROMPT_plan.md             # Planning-only prompt
├── PROMPT_build.md            # Implementation prompt
├── AGENTS.md                  # Operational reference
├── IMPLEMENTATION_PLAN.md     # Prioritized task list (markdown bullets)
└── specs/                     # One spec file per "topic of concern"
    ├── auth-flow.md
    └── api-design.md
```

### The Loop Script

```bash
#!/bin/bash
# Usage: ./loop.sh [plan] [max_iterations]

if [ "$1" = "plan" ]; then
  MODE="plan"
  PROMPT_FILE="PROMPT_plan.md"
  MAX_ITERATIONS=${2:-0}
elif [[ "$1" =~ ^[0-9]+$ ]]; then
  MODE="build"
  PROMPT_FILE="PROMPT_build.md"
  MAX_ITERATIONS=$1
else
  MODE="build"
  PROMPT_FILE="PROMPT_build.md"
  MAX_ITERATIONS=0
fi

ITERATION=0
CURRENT_BRANCH=$(git branch --show-current)

while true; do
  if [ $MAX_ITERATIONS -gt 0 ] && [ $ITERATION -ge $MAX_ITERATIONS ]; then
    echo "Reached max iterations: $MAX_ITERATIONS"
    break
  fi

  cat "$PROMPT_FILE" | claude -p \
    --dangerously-skip-permissions \
    --output-format=stream-json \
    --model opus \
    --verbose

  git push origin "$CURRENT_BRANCH" || {
    echo "Failed to push. Creating remote branch..."
    git push -u origin "$CURRENT_BRANCH"
  }

  ITERATION=$((ITERATION + 1))
done
```

**CLI flags explained:**
- `-p` -- headless/pipe mode (reads prompt from stdin)
- `--dangerously-skip-permissions` -- auto-approves all tool calls (use sandboxing!)
- `--output-format=stream-json` -- structured output for parsing
- `--model opus` -- use Opus for the orchestrator

### Two-Mode Operation

| Mode | Command | Purpose |
|------|---------|---------|
| **PLANNING** | `./loop.sh plan` | Gap analysis only; generates IMPLEMENTATION_PLAN.md |
| **BUILDING** | `./loop.sh 20` | Implements from plan, commits, updates plan |

Plan first, build second. The plan is disposable -- regenerate it when stale.

### Concepts: JTBDs, Topics, Specs

Huntley structures requirements using Jobs To Be Done:
- **JTBD** -- High-level user need ("users need to authenticate")
- **Topic of concern** -- Distinct aspect within a JTBD ("session management," "password reset")
- **Spec** -- Requirements doc for one topic, stored in `specs/`
- **Task** -- Unit of work derived from comparing specs to current code

**Topic scope test**: Can you describe it in one sentence without "and"? If not, split it.

### IMPLEMENTATION_PLAN.md

Unlike snarktank's JSON-based prd.json, Huntley uses a markdown bullet list:

```markdown
- [ ] Add JWT validation middleware (priority: high)
- [ ] Wire up rate limiter to auth endpoints
- [x] ~~Create user model and migration~~ (completed iteration 4)
- [ ] BUG: Token refresh fails silently when Redis is down
```

Updated by the agent each iteration. Cleaned out periodically to prevent bloat.

---

## 3. The Stop Hook Variant

Instead of a bash `while` loop, the stop hook approach uses Claude Code's native hook system to prevent the agent from exiting.

### How It Works

Claude Code hooks are defined in `.claude/settings.json` (project) or `~/.claude/settings.json` (global). A **Stop hook** fires when the agent tries to end its session. If the hook script exits with **code 2**, Claude Code:
1. Ignores any stdout
2. Reads stderr as a message
3. Injects that message back as a prompt
4. The agent continues working

This creates the loop without an external bash script.

### Plugin Implementation (anthropics/claude-code)

The official `ralph-wiggum` plugin ships with Claude Code and registers a stop hook in `hooks/hooks.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "command": "${CLAUDE_PLUGIN_ROOT}/hooks/stop-hook.sh"
      }
    ]
  }
}
```

The `stop-hook.sh` script:
1. Checks a state file to verify this session started a Ralph loop
2. Compares session IDs (prevents firing in unrelated sessions)
3. Checks if the agent output the completion promise
4. If not complete: exits with code 2, injecting the original prompt via stderr
5. If complete or max iterations reached: exits with code 0, allowing normal exit

Usage: `/ralph-loop "your prompt here" --max-iterations 10 --completion-promise "DONE"`

### Bash Loop vs. Stop Hook: Tradeoffs

| Dimension | Bash Loop | Stop Hook |
|-----------|-----------|-----------|
| **Context** | Guaranteed fresh each iteration | Same session may accumulate context |
| **Setup** | Just a shell script | Requires hooks config or plugin install |
| **Portability** | Works anywhere with bash | Requires Claude Code hooks support |
| **Control** | Full control over iteration logic | Limited to hook exit codes |
| **Debugging** | Easy to inspect loop state | Harder to debug hook interactions |
| **Windows** | Works in WSL/Git Bash | Known issues with plugin hooks on Windows |
| **Session isolation** | Complete isolation | Must check session IDs manually |
| **Known bugs** | Stable | Exit code 2 behaves differently for direct hooks vs plugin hooks |

**Recommendation**: The bash loop is simpler and more reliable. The stop hook is convenient for one-off loops without creating files, but the bash approach gives better context isolation and debuggability.

### frankbria/ralph-claude-code: Intelligent Exit Detection

Frank Bria's fork adds a dual-condition exit gate:

```
Exit requires BOTH:
  1. completion_indicators >= 2 (heuristic: phrases like "all tasks complete")
  2. Claude's explicit EXIT_SIGNAL: true in RALPH_STATUS block
```

Even when heuristics detect 3+ completion indicators, if Claude sets `EXIT_SIGNAL: false`, the loop continues. This prevents premature termination when the agent says "phase complete" but means to continue to the next phase.

---

## 4. Subagent Parallelization

This is Huntley's most advanced technique, described in PROMPT_build.md and PROMPT_plan.md.

### The Model

The main Claude instance (Opus) acts as an **orchestrator**. It spawns subagents for parallel work:

```
Main Agent (Opus) -- orchestrator
  ├── Sonnet subagent 1 -- read src/auth/
  ├── Sonnet subagent 2 -- read src/api/
  ├── ...
  ├── Sonnet subagent 500 -- read specs/
  └── Opus subagent -- complex reasoning for architecture decisions
```

### Allocation Rules

| Task Type | Model | Max Parallel |
|-----------|-------|-------------|
| Code search / file reads | Sonnet | Up to 500 |
| Build / test execution | Sonnet | **Exactly 1** |
| Complex reasoning / debugging | Opus | As needed |
| Spec inconsistency analysis | Opus 4.5 + ultrathink | As needed |

**The critical constraint**: Only 1 subagent for build/tests. This serializes validation and creates **backpressure** -- the agent cannot outrun its ability to verify correctness.

### How It Appears in Prompts

From PROMPT_plan.md:
```
Study `specs/*` with up to 250 parallel Sonnet subagents to learn
application specifications.

Use up to 500 Sonnet subagents to study existing source code in `src/*`
and compare it against `specs/*`. Use an Opus subagent to analyze
findings, prioritize tasks, and create/update @IMPLEMENTATION_PLAN.md.
```

From PROMPT_build.md:
```
You may use up to 500 parallel Sonnet subagents for searches/reads
and only 1 Sonnet subagent for build/tests. Use Opus subagents when
complex reasoning is needed.
```

### Why This Works

- **Reads are cheap and parallelizable** -- scanning 500 files simultaneously gives the orchestrator comprehensive codebase understanding
- **Writes must be serialized** -- you can't run two builds simultaneously
- **Model tiering saves cost** -- Sonnet for grunt work, Opus for decisions
- **The "don't assume not implemented" guardrail** -- with 500 subagents searching, the agent is less likely to reimplement existing code

---

## 5. Adam Tuttle's 3-Script Approach

Tuttle's approach (documented at adamtuttle.codes) focuses on portability and per-project customization.

### Setup

Add `~/.bin/` to your PATH, then create three scripts:

#### `~/.bin/ralph-install`
Bootstraps a project's `.ralph/` directory by copying templates from `~/.ralph/`:

```
~/.ralph/
├── ralph.sh            # Loop script template
├── prd.example.json    # PRD template
└── progress.md         # Progress log template
```

Running `ralph-install` in a project:
1. Creates `.ralph/` in the project root
2. Copies templates from `~/.ralph/`
3. Adds `.ralph/` to `.gitignore`
4. Prints usage instructions

The key design: templates are **copied**, not symlinked. Each project gets its own customizable versions.

#### `~/.bin/plan`
Starts a planning session with Claude Code. It:
1. Studies `.ralph/prd.example.json` for the expected format
2. Loads `.ralph/prd.json` if it exists (to extend/modify)
3. Lets you brain-dump your thoughts about what you want to build
4. Asks clarifying questions when prompted
5. Writes the result to `.ralph/prd.json`

#### `~/.bin/ralph`
Executes `.ralph/ralph.sh` -- a thin wrapper so you type `ralph` instead of `./.ralph/ralph.sh`.

### Permission Management

Tuttle explicitly avoids `--dangerously-skip-permissions`. Instead, he configures `.claude/settings.local.json` with specific allowed patterns:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run:*)",
      "Bash(npx prisma:*)",
      "Bash(git:*)"
    ]
  }
}
```

This gives the loop just enough access without full sandbox bypass.

### Progress Tracking

Uses `progress.md` (markdown) instead of `progress.txt`:

```markdown
## Session 1 - 2026-04-08
### Completed
- Initialized Next.js project with TypeScript
- Set up Prisma with PostgreSQL

### Learnings
- Dev server must be stopped before running migrations
- Tailwind config needs explicit content paths for app router
```

---

## 6. Cole Medin's Quickstart (ralph-loop-quickstart)

Medin's repo focuses on getting people running quickly with three innovations over the base approach.

### Repository Structure

```
ralph-loop-quickstart/
├── .claude/
│   ├── settings.json              # Sandbox and permissions
│   └── commands/
│       └── create-prd.md          # Interactive PRD generation
├── .claude/skills/
│   └── agent-browser-skill/
│       └── SKILL.md               # Visual verification instructions
├── screenshots/                    # Visual proof of completed work
├── PROMPT.md                       # Loop iteration instructions
├── activity.md                     # Per-iteration execution log
└── ralph.sh                        # Bash loop script
```

### Innovation 1: Interactive PRD Generation (`/create-prd`)

A Claude Code custom command that walks you through structured planning:
- Discovery questions: problem, audience, features, tech stack, architecture, auth, integrations
- Research assistance for uncertain decisions
- Auto-generates atomic, verifiable task lists
- Also generates tech-stack-specific `.claude/settings.json` permissions

### Innovation 2: Visual Verification with agent-browser

Integration with Vercel's agent-browser CLI:

```bash
npm install -g agent-browser && agent-browser install
```

Each iteration, the agent can:
1. Start the dev server
2. Launch a headless browser
3. Navigate to the page being worked on
4. Take a screenshot
5. Compare the screenshot against acceptance criteria
6. Store proof in `screenshots/`

This is especially valuable for frontend work where "it compiles" doesn't mean "it looks right."

### Innovation 3: Fresh Context Per Iteration (vs. Plugin)

Medin explicitly positions this as the **correct** way to run Ralph, contrasting it with the official Anthropic plugin. The bash loop creates genuinely isolated iterations, while the plugin operates within a single session that can accumulate context bloat.

### Activity Logging

`activity.md` captures structured per-iteration records:

```markdown
## Iteration 5 - 2026-04-08T03:42:00Z
**Task:** story-003 - Add user profile page
**Changes:** src/pages/profile.tsx, src/api/user.ts
**Commands:** npm run test, npm run build
**Screenshot:** screenshots/iteration-5-profile.png
**Issues:** None
**Commit:** a1b2c3d
```

### Comparison to Base Ralph

| Aspect | snarktank/ralph | ralph-loop-quickstart |
|--------|----------------|----------------------|
| Planning | Manual PRD creation | Interactive `/create-prd` command |
| Verification | Build/test only | Build/test + visual screenshots |
| Context | Fresh per iteration | Fresh per iteration |
| Permissions | Skip all or manual | Auto-generated per tech stack |
| Progress | progress.txt | activity.md with structured format |

---

## 7. Practical Tips and Prompt Engineering

### Writing Good PRD Tasks

**Do:**
- One logical unit per story ("Add the login API endpoint")
- Include explicit acceptance criteria with testable conditions
- Order by dependency (setup before features, backend before frontend)
- Include verification commands in criteria ("Verify `npm test` passes")
- For frontend: include "Verify in browser" criteria

**Don't:**
- Bundle multiple features ("Add auth AND the dashboard")
- Use vague criteria ("works correctly," "looks good")
- Assume the agent knows your stack -- specify commands
- Skip infrastructure stories (DB setup, env config)

### Prompt Structure That Works

Huntley's prompt structure uses distinctive patterns:

1. **"Study" not "read"** -- more directive, implies comprehension
2. **Numbered with absurd padding** (99999, 999999...) -- forces priority ordering that the agent can't misinterpret
3. **"Don't assume not implemented"** -- critical guardrail against reimplementation
4. **"Ultrathink"** -- triggers extended reasoning in Claude
5. **Explicit subagent allocation** -- "up to 500 Sonnet subagents for reads"
6. **Single responsibility per iteration** -- "choose the most important item"

### Verification Criteria

Every loop needs backpressure. Without automated verification, the agent declares victory on broken code.

**Programmatic backpressure:**
- Type checking (`tsc --noEmit`)
- Test suite (`npm test`, `pytest`, etc.)
- Linting (`eslint`, `ruff`)
- Build (`npm run build`)

**Non-deterministic backpressure** (for subjective criteria):
- LLM-as-judge tests with binary pass/fail
- Screenshot comparison against mockups
- Agent-browser visual verification

### Common Pitfalls

| Pitfall | Why It Happens | Prevention |
|---------|---------------|------------|
| Agent reimplements existing code | Doesn't search before writing | "Don't assume not implemented; search first" |
| AGENTS.md grows unbounded | Agent dumps status updates there | "Keep AGENTS.md operational only" |
| Plan goes stale | Codebase evolves, plan doesn't | Regenerate plan periodically with `./loop.sh plan` |
| Context pollution | Too many files loaded per iteration | Keep AGENTS.md brief, use subagents for reads |
| Placeholder/stub implementations | Agent satisfies tests minimally | "Implement completely. Placeholders waste time." |
| Inconsistent specs | Multiple spec files contradict | Use Opus subagent to reconcile specs |
| Loop runs all night on one stuck task | No iteration limit | Always set `max_iterations` |
| Compilation errors fill context | Cascading failures | Fresh context per iteration handles this |

### Security Considerations

Running with `--dangerously-skip-permissions` exposes everything on your machine: credentials, SSH keys, cookies, API tokens.

**Recommended sandboxing:**
- Docker containers for local development
- Fly Sprites or E2B for remote/production sandboxes
- Minimum viable access (only necessary API keys)
- Tuttle's approach: explicit permission allowlists in settings.json

---

## 8. Cost Analysis

### Real-World Reports

| Scenario | Cost | Output | Source |
|----------|------|--------|--------|
| $50K contract MVP | $297 | Full MVP, tested and reviewed | YC hackathon / ghuntley.com |
| 6 repos shipped overnight | $297 | Complete applications | YC hackathon teams |
| 50-iteration medium codebase | $50-100 | Feature implementation | Community reports |
| 50-iteration large codebase | $100+ | Partial feature work | Community reports |
| Huntley's CURSED compiler | Not disclosed | Full compiler + stdlib over 3 months | ghuntley.com |

### Cost Drivers

1. **Context size per iteration** -- larger codebases = more tokens per read
2. **Model choice** -- Opus orchestrator + Sonnet subagents is cheaper than all-Opus
3. **Iteration count** -- each iteration is a fresh API call
4. **Subagent count** -- 500 parallel Sonnet reads adds up
5. **Task complexity** -- simple CRUD vs. complex algorithms

### Cost Management Strategies

- **Set max_iterations** -- always cap overnight runs (25-50 typical)
- **Use model tiering** -- Sonnet for reads, Opus for decisions
- **Atomic tasks** -- smaller tasks = fewer iterations per story
- **Good PRDs** -- clear specs reduce wasted iterations
- **Plan mode first** -- catch gaps before burning build iterations
- **Monitor progress.txt** -- check if the loop is making progress or spinning

### Subscription vs. API

On a Claude Pro/Max subscription, Ralph loops chew through usage limits fast. The API with pay-per-token gives more predictable cost control and is generally recommended for serious Ralph usage. Huntley's approach assumes API access.

---

## 9. The Ecosystem

### Official Plugin

Anthropic ships a `ralph-wiggum` plugin in the claude-code repository:
- Install: `/plugin marketplace add snarktank/ralph`
- Usage: `/ralph-loop "prompt" --max-iterations 10`
- Uses stop hook approach (not bash loop)
- Known issues with Windows compatibility and plugin vs. direct hook behavior

### Community Forks

| Repository | Innovation |
|------------|-----------|
| [snarktank/ralph](https://github.com/snarktank/ralph) | PRD-driven, skills for Amp + Claude Code (15.1k stars) |
| [ghuntley/how-to-ralph-wiggum](https://github.com/ghuntley/how-to-ralph-wiggum) | Original methodology, two-mode prompts, subagent patterns |
| [coleam00/ralph-loop-quickstart](https://github.com/coleam00/ralph-loop-quickstart) | Interactive PRD, visual verification, fresh context |
| [frankbria/ralph-claude-code](https://github.com/frankbria/ralph-claude-code) | Intelligent dual-condition exit detection |
| [linrswa/ralph-in-claude](https://github.com/linrswa/ralph-in-claude) | Parallel worker agents spawned from main loop |
| [umputun/ralphex](https://github.com/umputun/ralphex) | Extended loop with additional orchestration |
| [ClaytonFarr/ralph-playbook](https://github.com/ClaytonFarr/ralph-playbook) | Comprehensive guide/playbook format |

### Key Blog Posts and Interviews

- [ghuntley.com/ralph](https://ghuntley.com/ralph/) -- Original concept + CURSED compiler story
- [ghuntley.com/loop](https://ghuntley.com/loop/) -- "Everything is a Ralph loop"
- [Dev Interrupted interview](https://devinterrupted.substack.com/p/inventing-the-ralph-wiggum-loop-creator) -- Origin story and philosophy
- [Adam Tuttle's workflow](https://adamtuttle.codes/blog/2026/my-ralph-workflow-for-claude-code/) -- 3-script approach
- [The Register coverage](https://www.theregister.com/2026/01/27/ralph_wiggum_claude_loops/) -- "'Ralph Wiggum' loop prompts Claude to vibe-clone software"

---

## 10. Applying Ralph to Untype

For our project, the relevant patterns are:

1. **Two-mode loop** -- we could use plan mode to generate IMPLEMENTATION_PLAN.md from our existing specs, then build mode to execute
2. **Subagent reads** -- our codebase is small enough that 500 subagents is overkill, but the pattern of "search before implementing" is valuable
3. **Backpressure via `swift build`** -- our existing build verification is exactly the kind of automated check Ralph needs
4. **AGENTS.md = our CLAUDE.md** -- we already maintain this; keep it operational
5. **Session logs as progress.txt** -- our `sessions/` directory serves a similar purpose
6. **Atomic stories** -- our phase-based implementation plan already breaks work into small units

The main thing we'd need to add: a `prd.json` or `IMPLEMENTATION_PLAN.md` with machine-readable task status, and a `loop.sh` wrapper.
