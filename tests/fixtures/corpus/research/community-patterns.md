# Claude Code Community Workflow Patterns

Research compiled April 2026. Covers workflow patterns, tooling, cost strategies,
and team adoption approaches drawn from community experience and official guidance.

---

## 1. Boris Cherny's Workflow

Boris Cherny is a Staff Engineer at Anthropic and the creator of Claude Code. He
published his full workflow publicly in early 2026, and it has become a reference
point for the community.

### Parallel Session Architecture

Boris runs **10-15 concurrent Claude Code sessions** at any given time:

- **5 terminal sessions** -- tabbed, numbered, with macOS notifications so he
  knows when each finishes. Each runs against a separate git checkout (he
  personally prefers full checkouts; most of the Claude Code team prefers
  worktrees).
- **5-10 browser sessions** via claude.ai/code, running in Anthropic-managed
  cloud VMs.
- **Mobile sessions** started from the iOS app in the morning and checked on
  throughout the day.

This approach lets him ship **20-30 PRs per day**.

### Plan-Then-Execute Pattern

Boris starts every task in **Plan Mode**. He iterates on the plan until it is
right, then switches to **auto-accept mode** so Claude can execute the entire
implementation without back-and-forth. The key insight: steering time on the plan
is much cheaper than steering time during implementation.

### CLAUDE.md as Team Knowledge Base

The Claude Code team shares a single `CLAUDE.md` checked into git. The entire
team contributes to it multiple times per week. The rule is simple:

> "Anytime we see Claude do something incorrectly, we add it to the CLAUDE.md
> so Claude knows not to do it next time."

During code review, Boris tags `@.claude` on coworkers' PRs to add learnings
back to `CLAUDE.md` via the Claude Code GitHub action.

### Model Choice

Boris uses **Opus with thinking mode** for every task. His reasoning: despite
Opus being bigger and slower, you steer it less and it handles tool use better,
making it almost always faster end-to-end than using a smaller model.

### Key Shortcuts

- **Shift+Tab** cycles through modes: Edit -> Auto-Accept -> Plan.
- **Ctrl+G** opens a plan file in your IDE for direct manual editing.

Sources:
- [How Boris Uses Claude Code](https://howborisusesclaudecode.com)
- [Building Claude Code with Boris Cherny (Pragmatic Engineer)](https://newsletter.pragmaticengineer.com/p/building-claude-code-with-boris-cherny)
- [Boris Cherny on parallel worktrees (X)](https://x.com/bcherny/status/2017742743125299476)
- [Boris team tips (GitHub Gist)](https://gist.github.com/joyrexus/e20ead11b3df4de46ab32b4a7269abe0)

---

## 2. Planning-First Approach

The community has converged on a "plan first, build second" pattern that mirrors
how senior engineers naturally work.

### The Two-Claude Review Pattern

1. **Claude A** drafts a plan in Plan Mode, reading files and asking clarifying
   questions but never editing code.
2. **Claude B** (or the developer) reviews the plan "as a staff engineer,"
   checking for missed edge cases, architectural concerns, and scope creep.
3. Only after approval does Claude A switch to Edit Mode and execute.

This mirrors pair programming but with the AI on both sides of the review.

### Plan Mode Mechanics

Plan Mode is a **read-only state** where Claude can:
- Read files and search the codebase
- Ask clarifying questions
- Produce a structured plan with file-level changes

It **cannot** edit files, write new files, or run shell commands.

### Version-Controlled Plans

For long-running refactors, teams write plans to files like `tasks/todo.md` and
check them into git. This enables:
- Reviewing plan diffs in pull requests before any code changes
- Multiple developers (or Claude sessions) working from the same plan
- Audit trails for architectural decisions

### Ctrl+G for Plan Editing

When Claude shows a plan, pressing **Ctrl+G** opens it in your IDE. This lets
you manually edit the plan -- adding steps, removing scope, reordering -- before
handing it back for execution.

Sources:
- [Claude Code Plan Mode (DataCamp)](https://www.datacamp.com/tutorial/claude-code-plan-mode)
- [Claude Code Planning Workflow](https://juliangoldie.com/claude-code-planning-workflow/)
- [Plan Mode (Medium)](https://medium.com/@kuntal-c/claude-code-plan-mode-revolutionizing-the-senior-engineers-workflow-21d054ee3420)
- [Interactive mode docs](https://code.claude.com/docs/en/interactive-mode)

---

## 3. The Three-Tier Approach

The community organizes Claude Code usage into three tiers based on supervision
level and parallelism.

### Tier 1: Interactive

Direct, hands-on work in a single terminal session. You prompt, review, steer.

- Best for: exploratory work, debugging, learning a new codebase
- Typical session: 1 Claude instance, full attention
- Mode: Edit mode with manual approval of each change

### Tier 2: Parallel Worktrees (3-5 sessions)

Multiple Claude instances running simultaneously, each in an isolated git
worktree working on an independent task.

- Best for: feature sprints, knocking out a backlog of small tasks
- Setup: `claude --worktree` or `claude --worktree my-feature-name`
- Coordination: shared task list (agent teams) or independent branches
- Typical cadence: check in every 5-10 minutes, review diffs, steer

Shell aliases help navigation:

```bash
alias za="cd ~/project-worktrees/feature-a && claude --resume"
alias zb="cd ~/project-worktrees/feature-b && claude --resume"
alias zc="cd ~/project-worktrees/feature-c && claude --resume"
```

The `--tmux` flag launches Claude in its own tmux session for even more
isolation.

### Tier 3: Agent Teams / Overnight Runs

Fully autonomous multi-agent sessions that run without supervision.

- **Agent Teams** (experimental): one lead session coordinates 3-5 teammate
  sessions, each in its own worktree. The lead assigns tasks and synthesizes
  results; teammates communicate directly with each other.
- **Cloud sessions** via `claude --remote` or claude.ai/code: run in
  Anthropic-managed VMs, accessible from browser and mobile.
- Best for: draining the backlog overnight, large refactors, test generation

Most developers in 2026 use all three tiers: Tier 1 for interactive work,
Tier 2 for parallel sprints, Tier 3 to drain the backlog overnight.

Sources:
- [Orchestrate teams of Claude Code sessions](https://code.claude.com/docs/en/agent-teams)
- [One-Person Engineering Team: Parallel Workflow Guide](https://www.shareuhack.com/en/posts/claude-code-parallel-workflow-guide-2026)
- [Claude Code Worktrees Guide](https://claudefa.st/blog/guide/development/worktree-guide)
- [Building a C compiler with parallel Claudes (Anthropic)](https://www.anthropic.com/engineering/building-c-compiler)

---

## 4. CLAUDE.md as Living Documentation

`CLAUDE.md` is the single most important file for Claude Code effectiveness. The
community treats it as a living document that evolves with every mistake.

### The Feedback Loop

```
Claude makes mistake -> Developer corrects -> Update CLAUDE.md -> Claude reads
updated file -> Mistake does not recur
```

This is the core maintenance pattern. When code reviews reveal conventions that
were not documented or reviewers catch pattern violations, that signals a
`CLAUDE.md` update.

### What to Include

Based on community consensus, effective `CLAUDE.md` files contain:

1. **Build and test commands** -- exact commands, not descriptions
2. **Architecture rules** -- "never use Combine," "all UI is programmatic"
3. **File layout conventions** -- where things go and why
4. **Dependency policy** -- what is allowed, what is not
5. **Error patterns** -- specific mistakes Claude keeps making
6. **Style rules** -- only those that differ from standard conventions

### What to Avoid

- **Exceeding 200 lines** -- bloated files cause Claude to ignore instructions.
  Some teams target 60 lines.
- **Obvious rules** -- do not state things Claude would do by default
- **Aspirational rules** -- only include rules that reflect current practice

For each line, ask: would removing it cause Claude to make mistakes? If not,
delete it.

### Team Maintenance

- Check `CLAUDE.md` into git so the whole team can contribute
- Review it when things go wrong; prune it regularly
- Use hierarchical files: `~/.claude/CLAUDE.md` for personal preferences,
  repo-level for project rules, directory-level for subsystem rules
- Run periodic reviews: "Claude, review this CLAUDE.md and suggest improvements"

### Hierarchy

Claude Code reads `CLAUDE.md` files at multiple levels:

| Level | Path | Scope |
|-------|------|-------|
| Enterprise | Admin-managed | Company-wide standards |
| User | `~/.claude/CLAUDE.md` | Personal preferences |
| Project | `./CLAUDE.md` | Repository rules |
| Directory | `./src/CLAUDE.md` | Subsystem rules |

Lower-level files override higher-level ones for conflicting rules.

Sources:
- [Best Practices - Claude Code Docs](https://code.claude.com/docs/en/best-practices)
- [How to Write a Good CLAUDE.md (Builder.io)](https://www.builder.io/blog/claude-md-guide)
- [Writing a good CLAUDE.md (HumanLayer)](https://www.humanlayer.dev/blog/writing-a-good-claude-md)
- [CLAUDE.md Best Practices (UX Planet)](https://uxplanet.org/claude-md-best-practices-1ef4f861ce7c)
- [7 Mistakes Boris Cherny Never Makes (Medium)](https://alirezarezvani.medium.com/your-claude-md-is-probably-wrong-7-mistakes-boris-cherny-never-makes-6d3e5e41f4b7)

---

## 5. Third-Party Orchestration Tools

A growing ecosystem of tools wraps Claude Code to add multi-agent orchestration,
visual management, and cross-provider support.

### oh-my-claudecode

**What it does:** Teams-first multi-agent orchestration for Claude Code. Adds 5
execution modes and 32 specialized agents.

**Key modes:**
- **Team Mode** -- staged pipeline for enterprise stability
- **Ultrawork / Ultrapilot** -- burst-parallel execution (up to 5 instances in
  isolated worktrees with a shared task list)
- **Ralph** -- persistence mode with self-healing loops that auto-verify and fix
  code

**Claims:** 3-5x speedup on large projects, 30-50% reduction in token costs.

**Source:** [oh-my-claudecode (GitHub)](https://github.com/yeachan-heo/oh-my-claudecode)

### Claude Code Agentrooms

**What it does:** Desktop app and API for multi-agent orchestration. Route tasks
to specialized agents (local or remote) and coordinate via @mentions.

**Architecture:** Frontend connects to a backend orchestrator that manages both
local agents and remote agents across different machines and cloud instances.

**Source:** [Claude Code Agentrooms](https://claudecode.run/) |
[GitHub](https://github.com/baryhuang/claude-code-by-agents)

### parallel-code

**What it does:** Run Claude Code, OpenAI Codex, and Gemini side by side, each
in its own git worktree. Free, open source, no extra subscription.

**Use case:** Compare outputs from different providers on the same task, or run
the best provider for each task type.

**Source:** [parallel-code (GitHub)](https://github.com/johannesjo/parallel-code)

### Nimbalyst

**What it does:** Visual workspace and session manager for Claude Code and Codex.
Adds a GUI layer with WYSIWYG editors, multi-session kanban board, inline diff
review, and a mobile app.

**Key features:**
- 7+ visual editors (markdown, code, CSV, UI mockups, Excalidraw, ERDs, Mermaid)
- Automatic git worktree creation per session
- Session kanban board for at-a-glance agent status
- Free for individual users

**Source:** [Nimbalyst](https://nimbalyst.com/)

### Other Notable Tools

| Tool | Purpose |
|------|---------|
| [Plural](https://github.com/zhubert/plural) | Run parallel sessions across branches, fork competing approaches, broadcast prompts |
| [parallel-cc](https://github.com/frankbria/parallel-cc) | Coordinate parallel sessions using worktrees + E2B cloud sandboxes |
| [AgentHub](https://github.com/jamesrochabrun/AgentHub) | Native macOS app for managing Claude Code and Codex sessions |
| [ruflo](https://github.com/ruvnet/ruflo) | Agent orchestration platform with swarm intelligence and RAG |

---

## 6. Common Workflow Patterns

### Code Review

Claude Code's built-in code review dispatches **5 parallel reviewers**, each
analyzing changes from a different angle:

1. CLAUDE.md compliance checking
2. Bug detection
3. Git history context analysis
4. Previous PR comment review
5. Code comment verification

Each finding is scored on a 0-100 confidence scale. Only high-confidence issues
(default threshold: 80) are posted as PR comments.

**Usage:** Integrated into GitHub Actions or triggered manually with
`claude review`.

### PR Creation

```
"Create a PR for my changes"
```

Claude examines staged changes, drafts a title and description, and runs
`gh pr create`. The session is automatically linked to the PR, so you can resume
later with `claude --from-pr <number>`.

### Debugging

The community recommends a **structured debugging skill** that enforces:

1. Reproduce the issue
2. Form a hypothesis
3. Verify the hypothesis with evidence (logs, tests, print statements)
4. Apply the fix
5. Verify the fix resolves the original issue

Without this structure, Claude (like most developers) jumps to a plausible fix
without confirming the root cause, leading to "fixed it but it came back" cycles.

### Refactoring

Large refactors benefit from the Plan Mode workflow:

1. Start in Plan Mode to map all files that need changes
2. Write the plan to a version-controlled file
3. Review the plan (ideally with a second Claude or human reviewer)
4. Execute in parallel worktrees if changes are independent
5. Merge worktree branches sequentially

### Test-Driven Development

The TDD pattern with Claude Code follows red-green-refactor:

1. **Red:** Tell Claude to write tests for functionality that does not exist yet.
   Be explicit that you are doing TDD so Claude does not create mock
   implementations.
2. **Green:** Run the tests, confirm they fail, then ask Claude to write the
   minimal implementation to make them pass.
3. **Refactor:** Ask Claude to improve the implementation while keeping tests
   green.

A TDD skill can enforce this at the prompt level: Claude will not write
implementation code until it has written a failing test.

### Session Management

- Use `claude --resume` to continue a previous session
- Use `claude --from-pr 123` to resume from a PR context
- Cloud sessions persist and are accessible from browser and mobile
- Named worktrees (`claude --worktree auth-refactor`) make it easy to return

Sources:
- [Common Workflows (Claude Code Docs)](https://code.claude.com/docs/en/common-workflows)
- [Code Review for Claude Code](https://claude.com/blog/code-review)
- [TDD with Claude (Steve Kinney)](https://stevekinney.com/courses/ai-development/test-driven-development-with-claude)
- [Claude Code Skill Packs (DEV Community)](https://dev.to/whoffagents/claude-code-skill-packs-10-skills-that-cut-my-development-time-in-half-m97)

---

## 7. Cost Management Strategies

### Subscription vs API

| Approach | Cost | Best for |
|----------|------|----------|
| API pay-as-you-go | $3-25/MTok | Under 50M tokens/month |
| Max 5x plan | $100/month | 50-200M tokens/month |
| Max 20x plan | $200/month | 200M-1B+ tokens/month |
| Pro plan | $20/month | Light usage (~44K tokens per 5-hour window) |

The subscription runs roughly **15-30x cheaper** than API billing for the same
work, because over 90% of tokens in heavy sessions are cache reads, which are
included in the flat rate.

### Model Selection Strategy

| Model | Input/Output per MTok | When to use |
|-------|----------------------|-------------|
| Sonnet 4.6 | $3 / $15 | 80% of coding tasks -- implementation, tests, refactoring |
| Opus 4.6 | $5 / $25 | Complex multi-file architecture, difficult debugging, planning |
| Haiku | $0.25 / $1.25 | Simple completions, formatting, boilerplate |

Boris Cherny's counterpoint: Opus with thinking is almost always faster
end-to-end because you steer less. The per-token cost is higher but the total
cost (tokens + developer time) is lower.

### Budget Controls

- Set spending limits in the Anthropic console
- Use `claude --model sonnet` for routine tasks to conserve budget
- Monitor token usage with `claude usage` or the dashboard
- For teams: set per-seat limits and alert thresholds

### Optimization Tactics

1. **Keep CLAUDE.md concise** -- every line is read on every prompt, costing
   input tokens
2. **Use worktrees** -- isolated contexts mean smaller context windows
3. **Resume sessions** instead of starting fresh to leverage cached context
4. **Use Plan Mode** before Edit Mode -- planning tokens are cheaper than
   undoing bad implementations
5. **Batch related changes** into single sessions to amortize context loading

Sources:
- [Manage costs effectively (Claude Code Docs)](https://code.claude.com/docs/en/costs)
- [Claude Code Pricing 2026 (NxCode)](https://www.nxcode.io/resources/news/claude-code-pricing-2026-free-api-costs-max-plan)
- [Claude Code Pricing (Product Compass)](https://www.productcompass.pm/p/claude-code-pricing)
- [API Pricing (Anthropic)](https://platform.claude.com/docs/en/about-claude/pricing)

---

## 8. Team Adoption Patterns

### Phased Rollout

The community consensus is that introducing Claude Code is **20% technology,
80% people**.

**Phase 1: Pilot (1-2 developers, 1 sprint)**
- Pick curious developers, not skeptics
- Have them document their experience as an internal case study
- Measure: time saved, PR velocity, test coverage delta

**Phase 2: Team Expansion (5-8 developers)**
- Create a shared `CLAUDE.md` with the pilot team's learnings
- Run a workshop on effective prompting
- Establish review standards for AI-generated code
- Measure: before/after PR velocity and defect rates

**Phase 3: Organization**
- Deploy enterprise `CLAUDE.md` for company-wide standards
- Integrate Claude Code Review into CI/CD
- Set up per-seat budget limits and usage monitoring

### Shared Configuration

Teams share context through a layered configuration:

```
~/.claude/CLAUDE.md          # Personal preferences
./CLAUDE.md                  # Project rules (checked into git)
./src/subsystem/CLAUDE.md    # Subsystem-specific rules
.claude/commands/            # Custom slash commands
.claude/settings.json        # Permissions and tool access
```

Custom commands (`.claude/commands/*.md`) standardize workflows across the team.
For example, a `/review` command might enforce a specific checklist, while
`/deploy` might run a standard deployment sequence.

### Reviewing AI-Generated Code

The community standard: **AI-generated code passes the same checks as human
code**. If a PR is good, it does not matter how it was written.

Reviewers should pay special attention to:

1. **Business logic correctness** -- Claude optimizes for "looks right" over
   "is right" for domain-specific logic
2. **Edge cases** -- Claude tends to handle the happy path well but may miss
   boundary conditions
3. **Security** -- input validation, auth checks, data exposure
4. **Performance** -- Claude may choose readable but suboptimal approaches
5. **Consistency** -- does it match patterns established in CLAUDE.md?

### Multi-Agent Code Review

Anthropic's official Code Review tool (launched March 2026) operates in layers:

1. **Parallel analysis** -- multiple reviewers examine changes simultaneously
2. **Verification** -- a second group filters false positives
3. **Ranking** -- findings sorted by severity and confidence score

This integrates directly into GitHub and CI/CD, posting only high-confidence
findings as PR comments.

### Anti-Patterns to Avoid

- **Skipping review** because "Claude wrote it" -- AI code needs the same
  scrutiny as human code
- **Over-specified CLAUDE.md** -- bloated files degrade output quality
- **No shared configuration** -- every developer reinventing prompts wastes
  time and produces inconsistent code
- **Jumping to Tier 3** (overnight autonomous runs) without mastering Tier 1
  (interactive) -- you need to understand Claude's failure modes before
  removing supervision

Sources:
- [How to Introduce Claude Code to Your Team (Code Velocity Academy)](https://www.codevelocity.academy/en/blog/claude-code-team-adoption)
- [Setting Up Claude Code for a Team (CallSphere)](https://callsphere.tech/blog/claude-code-team-setup-best-practices)
- [Claude Code for Enterprise (Anthropic)](https://claude.com/product/claude-code/enterprise)
- [Claude Code best practices for enterprise teams (Portkey)](https://portkey.ai/blog/claude-code-best-practices-for-enterprise-teams/)
- [Code Review for Claude Code (Anthropic blog)](https://claude.com/blog/code-review)

---

## Summary

The Claude Code community has settled on a few core principles:

1. **Plan before you build.** Plan Mode is not optional -- it is the primary
   quality lever.
2. **Parallelize aggressively.** Git worktrees make it safe. The productivity
   gain is multiplicative, not additive.
3. **Treat CLAUDE.md as code.** Review it, prune it, version it. Every mistake
   is a documentation opportunity.
4. **Match supervision to risk.** Interactive for novel work, parallel for
   known patterns, autonomous for well-defined tasks.
5. **Review AI code like human code.** The bar does not change because the
   author is an AI.
