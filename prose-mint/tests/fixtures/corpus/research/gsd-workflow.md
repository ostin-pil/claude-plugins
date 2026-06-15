# GSD (Get Shit Done) Workflow -- Deep Dive

*Research compiled: 2026-04-09*

---

## Overview

GSD is a meta-prompting, context engineering, and spec-driven development system for
Claude Code created by Lex Christopherson (GitHub: glittercowboy), a house music
producer in Costa Rica operating under the TACHES organization. First committed in
December 2025, it has grown to 50K+ GitHub stars and 1,700+ commits across 47+ releases
as of April 2026. It supports 12 runtimes (Claude Code, Gemini, Codex, Cursor, Windsurf,
Copilot, Cline, Kilo, Augment, Trae, Antigravity, OpenCode).

The core thesis: context rot is the defining bottleneck of agentic coding, and the
solution is to externalize all state to files and execute every task in a fresh context
window via sub-agents.

---

## 1. The Context Rot Problem

### What Is Context Rot?

Context rot is the measurable performance degradation LLMs experience as input length
increases. It is NOT context window overflow -- rot happens well before the window fills.
A model with a 200K token window can exhibit significant degradation at 50K tokens.

As an agent accumulates conversation history, partial decisions, debugging traces, and
file contents, the signal-to-noise ratio degrades. The model can no longer reliably
distinguish current intent from stale context. The result: hallucinated variable names,
forgotten constraints, and code that drifts from the spec.

### Research Evidence

**Chroma Context Rot Study (2025)**

Chroma Research tested 18 frontier models (GPT-4.1, Claude Opus 4, Gemini 2.5, Qwen3)
and found that **every single model** gets worse as input length increases. Key findings:

- The study isolated input length as the primary variable while keeping task complexity
  constant -- addressing a limitation in prior benchmarks where longer inputs correlated
  with increased difficulty
- As needle-question similarity decreases, performance degrades more significantly with
  increasing input length
- Context rot is universal across all architectures tested

**"Lost in the Middle" (Liu et al., Stanford, 2023)**

The foundational paper showing models recall information best at the beginning and end of
context, but struggle with information in the middle:

- Accuracy dropped from 70-75% for information at positions 1 or 20 (of 20 docs) down to
  55-60% for middle positions -- a 15-20 percentage point drop based entirely on position
- In multi-document QA with 20 documents, accuracy dropped by more than 30% when the
  relevant document was in positions 5-15 vs. position 1 or 20

**Veseli et al. (2025) -- The Fill Threshold Discovery**

This study found the U-shaped pattern (favoring beginning + end tokens) only persists when
context is **less than 50% full**. Above 50%:

- A different pattern emerges: the LLM favors more recent tokens, then middle tokens, over
  early tokens
- Early project requirements placed at the start of context get progressively buried

### Degradation Thresholds in Practice

The community has empirically identified three threshold zones for Claude Code:

| Context Fill | Observed Behavior |
|---|---|
| **0-30%** | Peak quality. Thorough, comprehensive, follows all instructions. |
| **30-50%** | Still good. Subtle degradation begins -- occasionally misses edge cases. |
| **50-70%** | Noticeable quality drop. Responses get shorter, starts cutting corners, misses instructions. |
| **70%+** | Severe degradation. Hallucinations spike, requirements forgotten, code quality collapses. |

These thresholds are empirical (derived from community testing and practitioner reports),
not from a controlled academic study. However, they align with the Chroma and Veseli
findings: degradation is continuous, not a cliff, but accelerates past 50%.

### The Attention Budget Model

LLMs have an "attention budget" analogous to human working memory. Every new token depletes
this budget. Context must be treated as a finite resource with diminishing marginal returns.
This is why GSD's approach -- fresh 200K windows per task -- is structurally superior to
trying to manage a single accumulating conversation.

---

## 2. GSD v1 Internals

### Sub-Agent Spawning Mechanism

GSD v1 is a collection of markdown prompts installed into `~/.claude/commands/` that
leverage Claude Code's built-in `Task` tool for sub-agent dispatch. Each `Task` call
starts a new sub-agent as an independent process with:

- A prompt assignment containing everything needed
- Subagent type definition (researcher, planner, executor, debugger, verifier)
- Model specification
- Description of expected output

Communication between agents happens **exclusively via files**. There is no shared memory
or message passing.

### Orchestration Architecture

Every orchestration stage follows this pattern:

```
1. Thin orchestrator routes work to specialized agents
2. Parallel agents execute domain-specific tasks
3. Result aggregation synthesizes outputs into structured context
4. Next-step routing feeds results to downstream stages
```

Example -- research phase:

```
4x Researcher agents start in parallel
  -> Each writes results to its own file
  -> When all finish, Synthesizer starts
  -> Reads result files, distills into SUMMARY.md
  -> Roadmapper receives synthesis to create roadmap
```

### Task Boundary Decisions

GSD enforces the **Iron Rule**: a task must fit in one context window. If it cannot, it
becomes two tasks. Task plans are structured in XML for unambiguous parsing:

```xml
<task type="auto">
  <name>Create login endpoint</name>
  <files>src/app/api/auth/login/route.ts</files>
  <action>
    Use jose for JWT. Validate credentials against users table.
    Return httpOnly cookie on success.
  </action>
  <verify>curl -X POST localhost:3000/api/auth/login returns 200 + Set-Cookie</verify>
  <done>Valid credentials return cookie, invalid return 401</done>
</task>
```

Each plan contains a maximum of 3 tasks. Plans are grouped into **waves** based on
dependency analysis:

```
WAVE 1 (parallel): Plan 01 (User Model) + Plan 02 (Product Model)
WAVE 2 (parallel): Plan 03 (Orders API) + Plan 04 (Cart API)
WAVE 3 (sequential): Plan 05 (Checkout UI -- depends on waves 1+2)
```

### Context Size Calibration

Each plan is designed to consume approximately 50% of a fresh context window. This ensures
no single task is large enough to trigger the quality degradation observed past 50% fill.
The orchestrator conversation stays at 30-40% -- it only dispatches, never accumulates
execution detail.

---

## 3. State Files in Detail

GSD externalizes all project state to `.planning/` (v1) or `.gsd/` (v2). These files are
the cross-session memory that makes fresh-context execution possible.

### PROJECT.md

The vision document. Always loaded into every agent's context. Concise -- the project in
one page.

```markdown
# MyApp

## Vision
A real-time collaborative whiteboard for distributed teams.

## Tech Stack
- Frontend: Next.js 15, React 19, TailwindCSS
- Backend: Node.js, PostgreSQL, Drizzle ORM
- Real-time: WebSockets via Socket.io
- Auth: NextAuth.js with Google/GitHub providers

## Constraints
- Must work offline with sync-on-reconnect
- Target <100ms latency for drawing operations
- No paid third-party services beyond hosting

## Non-Goals
- Mobile native apps (web PWA only for v1)
- Video/audio conferencing
```

### REQUIREMENTS.md

Scoped requirements with unique IDs and phase traceability. Distinguishes v1, v2, and
out-of-scope:

```markdown
# Requirements

## v1 (MVP)
- [R001] User authentication via Google OAuth
- [R002] Create/join whiteboard rooms via shareable link
- [R003] Freehand drawing with pressure sensitivity
- [R004] Real-time cursor presence for all participants
- [R005] Undo/redo stack (local, 50 levels)

## v2
- [R010] Shape tools (rectangle, ellipse, arrow)
- [R011] Text annotations with formatting
- [R012] Export board as PNG/SVG

## Out of Scope
- Video conferencing
- User permissions / role-based access
```

### ROADMAP.md

Progress tracking -- maps requirements to phases with completion status:

```markdown
# Roadmap

## Phase 1: Auth & Room Infrastructure [COMPLETE]
- [x] R001 - Google OAuth
- [x] R002 - Room creation/joining

## Phase 2: Drawing Engine [IN PROGRESS]
- [x] R003 - Freehand drawing
- [ ] R004 - Cursor presence
- [ ] R005 - Undo/redo

## Phase 3: Polish & Ship
- [ ] Performance optimization
- [ ] Error handling
- [ ] Deployment pipeline
```

### STATE.md

The cross-session memory file. Tracks decisions, blockers, current position, and lessons
learned. Updated after every phase:

```markdown
# State

## Current Position
Phase 2, Task 3 of 5 (Drawing Engine)

## Active Decisions
- Using Canvas 2D API over WebGL (simpler, sufficient for v1 scope)
- Socket.io chosen over native WebSocket for reconnection handling
- Storing strokes as polyline arrays, not SVG paths

## Blockers
- None currently

## Lessons Learned
- Phase 1: NextAuth session handling requires explicit cookie config for WebSocket auth
- Phase 2: Canvas redraw on resize needs debouncing (was causing frame drops)

## Open Questions
- Compression strategy for stroke data over WebSocket (evaluate after R004)
```

### Additional Planning Artifacts

| File / Directory | Purpose |
|---|---|
| `research/` | Ecosystem knowledge (stack, architecture, prior art) |
| `{N}-CONTEXT.md` | Discussion decisions for phase N |
| `{N}-RESEARCH.md` | Research findings for phase N |
| `{N}-{M}-PLAN.md` | Task plan M for phase N |
| `{N}-{M}-SUMMARY.md` | Execution summary for plan M |
| `{N}-VERIFICATION.md` | Post-execution verification results |
| `{N}-UAT.md` | User acceptance testing results |
| `todos/` | Captured ideas for later work |
| `threads/` | Persistent context threads for cross-session work |
| `seeds/` | Forward-looking ideas surfaced at appropriate milestones |

---

## 4. GSD v2 (TypeScript Controller)

### The Fundamental Shift

GSD v1 was a prompt framework that *requested* cooperation from the LLM. v2 is a
**TypeScript application built on the Pi SDK** that *controls* the agent session. This is
the critical architectural difference.

v1 installed markdown prompts into `~/.claude/commands/` and hoped Claude followed them.
v2 is a standalone CLI with direct TypeScript access to the agent harness, enabling it to:

- **Programmatically clear context** between tasks (not just asking nicely)
- **Inject exactly the right files** at dispatch time (pre-inlined, no tool calls needed)
- **Manage git branches** (milestone branches, squash-merge on completion)
- **Track cost and tokens** per phase/slice/model
- **Detect stuck loops** via sliding-window pattern detection
- **Recover from crashes** via lock files and state persistence
- **Auto-advance** through entire milestones without human intervention

### Installation and Usage

```bash
# Install
npm install -g gsd-pi@latest

# Start interactive session
gsd
/login          # OAuth or API key for 20+ providers

# Step mode (one unit at a time, pause for review)
/gsd
/gsd next

# Autonomous mode (walk away)
/gsd auto
```

### The Five-Wave State Machine

GSD v2 implements a state machine driven by filesystem state, reading `.gsd/STATE.md` to
determine the next work unit:

```
Plan (with integrated research)
  -> Execute (per task, fresh context each)
  -> Complete
  -> Reassess Roadmap
  -> Next Slice
  |--- (all slices done) --->
  Validate Milestone
  -> Complete Milestone
```

Hierarchy:

```
Milestone -> shippable version (4-10 slices)
  Slice -> demoable vertical capability (1-7 tasks)
    Task -> context-window-sized unit of work
```

### Tiered Context Injection (v2.67+, M005)

One of v2's most significant optimizations: relevance-scoped context injection that
achieves **65%+ token reduction** compared to v1. Instead of loading all state files into
every agent, v2 uses a decision scope cascade -- only injecting what is relevant to the
specific task being dispatched.

### Crash Recovery and Supervision

**Lock file tracking**: A lock file tracks the current unit. If the session dies, the next
`/gsd auto` reads the surviving session file and synthesizes a recovery briefing.

**Parallel orchestrator state**: Multi-worker sessions persist state to disk with PID
liveness detection. In headless mode, crashes trigger automatic restart with exponential
backoff (default 3 attempts).

**Stuck detection**: A sliding-window detector identifies repeated dispatch patterns. On
detection: retry once with deep diagnostics. If it fails again, auto mode stops.

**Timeout supervision**:
- Soft timeout warns the LLM to wrap up
- Idle watchdog detects stalls
- Hard timeout pauses auto mode
- Recovery steering nudges completion before giving up

### Budget Controls

Cost management is observable through logs and a web interface. Budget ceilings can pause
auto mode before overspending. Token/cost tracking is broken down by phase, slice, and
model.

### Git Isolation

When configured, each milestone runs on an isolated `milestone/<MID>` branch. All slice
work commits sequentially. On completion, squash-merged to main as one clean commit.

### Two-Terminal Workflow

```
Terminal 1 (let it build):     Terminal 2 (steer while working):
  gsd                            gsd
  /gsd auto                      /gsd discuss   # architecture decisions
                                  /gsd status    # progress dashboard
                                  /gsd steer     # hard-steer plan docs
```

Both terminals read/write the same `.gsd/` files. Decisions in terminal 2 are picked up
at phase boundaries automatically.

### Headless Mode (CI/Scripts)

```bash
gsd headless --timeout 600000
gsd headless new-milestone --context spec.md --auto
gsd headless query    # JSON snapshot (~50ms, no LLM call)
```

---

## 5. The 5-Phase Cycle in Practice

### Phase 1: Project Initialization (`/gsd-new-project`)

The system asks questions until it fully comprehends goals, constraints, tech preferences,
and edge cases. Then spawns parallel research agents to investigate the domain.

**Creates**: `PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`, `.planning/research/`

### Phase 2: Phase Discussion (`/gsd-discuss-phase N`)

Captures implementation preferences before planning. The system identifies gray areas
based on what is being built:

- Visual features: layout, density, interactions, empty states
- APIs/CLIs: response format, flags, error handling
- Content systems: structure, tone, depth, flow
- Organization tasks: grouping criteria, naming conventions

**Creates**: `{N}-CONTEXT.md`

Alternative mode: set `workflow.discuss_mode` to `"assumptions"` to have the system
analyze the codebase and surface what it would do, asking only for corrections.

### Phase 3: Phase Planning (`/gsd-plan-phase N`)

Spawns parallel researchers, creates 2-3 atomic task plans in XML structure, then runs a
**checker loop** that validates plans against requirements:

**Creates**: `{N}-RESEARCH.md`, `{N}-{M}-PLAN.md`

### Phase 4: Phase Execution (`/gsd-execute-phase N`)

Implements through wave-based parallel execution. Each task receives a fresh 200K token
context with pre-inlined content (task plans, prior summaries, dependency summaries,
roadmap excerpts, decisions register).

Every completed task produces an atomic git commit. Each task is independently revertable.

**Creates**: `{N}-{M}-SUMMARY.md`, `{N}-VERIFICATION.md`

### Phase 5: Work Verification (`/gsd-verify-work N`)

Human-in-the-loop validation:

1. Extracts testable deliverables from the completed phase
2. Walks through each interactively
3. Auto-diagnoses failures with debug agents
4. Creates fix plans ready for re-execution

**Creates**: `{N}-UAT.md`, fix plans if issues found

### Verification Gates (v1.34.0+)

Four canonical gate types integrated into planning and execution:

- **Pre-flight gates**: validate inputs before starting
- **Revision gates**: check intermediate milestones
- **Escalation gates**: flag complexity or scope concerns
- **Abort gates**: detect when to stop and reassess

### Quick Mode (`/gsd-quick`)

For ad-hoc tasks without full planning structure:

```bash
/gsd-quick
> "Add dark mode toggle to settings"

# Optional flags (composable):
--discuss    # lightweight discussion
--research   # focused research
--full       # complete pipeline
--validate   # plan-checking + verification only
```

### Sequential Chaining

```bash
/gsd-discuss-phase 1 --chain
# Auto-chains: discuss -> plan -> execute
```

---

## 6. The 48K+ Stars Phenomenon

### Why It Went Viral

GSD hit a nerve because context rot is the universal pain point of agentic coding in 2026.
Every developer using Claude Code, Cursor, or Copilot has experienced the agent getting
progressively dumber during long sessions. GSD provided a structured, name-brand solution
at exactly the right time.

Key factors:

1. **Real pain, clear solution**: Context rot is not theoretical. Every practitioner
   experiences it. GSD names the problem and provides a concrete fix.

2. **Zero cost, MIT license**: No paid tier, no premium version. Pure open source. This
   removed all adoption friction.

3. **One-line install**: `npx get-shit-done-cc@latest` -- from zero to working in under
   a minute.

4. **Creator authenticity**: Lex Christopherson is not a framework author by trade. He is
   a music producer who built what he needed. The project feels practitioner-built, not
   enterprise-marketed.

5. **Timing**: Launched December 2025, right as Claude Code adoption was exploding and
   before Anthropic shipped official solutions for context management.

6. **Multi-runtime support**: Not locked to Claude Code. Supporting 12 runtimes widened
   the addressable community significantly.

### Growth Trajectory

- December 2025: Initial commit
- March 2026: 35K stars, ~4,500 stars/week growth rate
- April 2026: 50K+ stars, 1,700+ commits, 47+ releases
- Trusted by engineers at Amazon, Google, Shopify, and Webflow

### Community Ecosystem

- Active Discord with a GSD Wizard bot (RAG over the actual codebase)
- Multiple forks (e.g., `get-shit-done-multi` for multi-CLI support)
- Third-party courses (CC for Everyone, DeepWiki)
- Integration with gstack and Superpowers frameworks

---

## 7. Token Overhead Analysis

### The 4:1 Ratio Claim

Community reports consistently cite a roughly **4:1 overhead ratio**: for every 1 token
writing actual code, approximately 4 tokens go to orchestration (planning, research,
verification, state management, sub-agent dispatch prompts).

### Where the Overhead Goes

| Category | Token Cost | Purpose |
|---|---|---|
| State file injection | High | PROJECT.md, REQUIREMENTS.md, STATE.md loaded into every agent |
| Research agents | Medium-High | 2-4 parallel researchers per phase, each with full context |
| Planning + checker loop | Medium | Plan generation + validation against requirements |
| Execution dispatch | Medium | Pre-inlined task plans, summaries, dependencies per task |
| Verification | Low-Medium | Post-execution checks, UAT generation |

### Real-World Cost Data

From community reports (Reddit r/ClaudeCode, Hacker News):

- **Daily feature work**: $5-15 on Claude Max plan
- **Large refactors / multi-agent workflows**: $30-50/day
- **Full project from scratch**: Varies widely, $50-200+
- **Max plan ($100-200/mo) strongly recommended** for regular GSD usage

### Is the Overhead Worth It?

Arguments for:

- **Quality preservation**: Each task gets peak-quality output (0-50% context fill)
- **Reduced rework**: Tasks that would fail at 70% context fill and require debugging now
  succeed on first attempt
- **Atomic commits**: Every task is independently revertable -- bad output is isolated
- **Verification built in**: Catches errors before they compound

Arguments against:

- **Simple projects do not benefit**: For a one-file script or quick fix, GSD is massive
  overkill. `/gsd-quick` exists for this but still has overhead.
- **Speed**: The multi-phase pipeline is slower than just asking Claude to do the thing.
  Community reports it as "so slow, too detailed" for simple tasks.
- **Cost ceiling**: Token-heavy users on API billing can run up significant costs.

### v2 Improvements

GSD v2's tiered context injection (M005) achieves **65%+ token reduction** compared to v1
by only injecting relevant state into each agent rather than loading everything. This
significantly improves the overhead ratio.

---

## 8. Comparison with Ralph Loop

### Philosophical Difference

The Ralph Loop and GSD solve the same problem (context rot) but from opposite ends of the
complexity spectrum.

| Dimension | Ralph Loop | GSD |
|---|---|---|
| **Core mechanism** | Bash loop: `while true; do cat PROMPT.md \| claude; done` | Multi-phase pipeline with orchestrator + sub-agents |
| **State management** | `prd.json`, `progress.txt`, `AGENTS.md` | PROJECT.md, REQUIREMENTS.md, ROADMAP.md, STATE.md + per-phase artifacts |
| **Planning** | Assumes you already have a blueprint (PRD) | Builds the blueprint for you (phases 1-3) |
| **Context strategy** | Fresh process per iteration (clean window) | Fresh sub-agent per task (clean window) |
| **Task selection** | Agent reads PRD, picks highest-priority incomplete task | Orchestrator assigns tasks based on wave dependencies |
| **Verification** | Automated (tests, lint, build must pass to advance) | Automated + human-in-the-loop UAT |
| **Parallelism** | Optional (Huntley's 500-subagent variant) | Built-in wave-based parallel execution |
| **Overhead** | Minimal (~1.1:1 ratio) | Heavy (~4:1 ratio, improving in v2) |
| **Best for** | Known scope, good tests, overnight batch runs | Greenfield projects, complex features, unclear requirements |

### Context Management: The Key Difference

**Ralph Loop**: Each iteration spawns a new agent process with a completely clean context
window. The agent reads specs from disk, takes a task, implements it, verifies via
automated checks, commits, and exits. The loop restarts with a fresh process. Context rot
is solved by brute force -- kill the process, start over.

**GSD**: The orchestrator maintains a persistent (but thin) context that only handles
dispatch. Heavy work is delegated to sub-agents, each with a fresh context. The
orchestrator's context stays at 30-40% fill because it never accumulates execution detail.
Context rot is solved by architectural isolation -- the orchestrator is a router, not a
worker.

### When to Use Which

**Use Ralph Loop when**:
- You have a well-defined PRD with clear task boundaries
- Your project has strong automated verification (tests, type-checking, linting)
- You want minimal overhead and maximum speed
- You are running overnight batch jobs

**Use GSD when**:
- Requirements are unclear and need exploration
- The project is complex enough to benefit from structured planning
- You want human-in-the-loop verification between phases
- You need the system to help you break down the problem, not just execute it

### Can They Combine?

Yes. Some practitioners use GSD phases 1-3 (initialization, discussion, planning) to
generate a structured PRD, then execute with a Ralph Loop for the implementation phase.
This gets GSD's planning rigor with Ralph's execution simplicity.

---

## Sources

- [GSD v1 GitHub Repository](https://github.com/gsd-build/get-shit-done)
- [GSD v2 GitHub Repository](https://github.com/gsd-build/gsd-2)
- [Beating Context Rot in Claude Code with GSD -- The New Stack](https://thenewstack.io/beating-the-rot-and-getting-stuff-done/)
- [Chroma Context Rot Research](https://research.trychroma.com/context-rot)
- [Lost in the Middle: How Language Models Use Long Contexts (Liu et al., 2023)](https://cs.stanford.edu/~nfliu/papers/lost-in-the-middle.arxiv2023.pdf)
- [GSD Hits 35K Stars -- TopAIProduct](https://topaiproduct.com/2026/03/19/get-shit-done-gsd-hits-35k-github-stars-a-music-producers-fix-for-ais-context-rot-problem/)
- [Complete Beginner's Guide to GSD -- DEV Community](https://dev.to/alikazmidev/the-complete-beginners-guide-to-gsd-get-shit-done-framework-for-claude-code-24h0)
- [GSD Deep Dive -- Codecentric](https://www.codecentric.de/en/knowledge-hub/blog/the-anatomy-of-claude-code-workflows-turning-slash-commands-into-an-ai-development-system)
- [GSD vs Ralph Loops -- Chase AI](https://www.chaseai.io/blog/gsd-vs-ralph-loops-claude-code)
- [Superpowers, GSD, and gstack Comparison -- Medium](https://medium.com/@tentenco/superpowers-gsd-and-gstack-what-each-claude-code-framework-actually-constrains-12a1560960ad)
- [Ralph Loop Fresh Context Pattern -- DeepWiki](https://deepwiki.com/FlorianBruniaux/claude-code-ultimate-guide/7.6-fresh-context-pattern-(ralph-loop))
- [Lex Christopherson on X](https://x.com/official_taches)
- [Context Rot Explained -- Redis](https://redis.io/blog/context-rot/)
- [Hacker News Discussion](https://news.ycombinator.com/item?id=46849977)
