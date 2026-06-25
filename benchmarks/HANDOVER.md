# Plugin benchmark program: handover

Status: complete. The three adopted plugins (lifecycle-kit, prose-mint, knowledge-kit) are benchmarked across context cost, automation latency, prose-mint accuracy, and a task-completion A/B for every non-trivial skill command. All three repos (claude-plugins, mcscale, untype) are clean on `main` with no open PRs. This doc is the single place to resume from: what the suite covers, the one durable conclusion, the reusable harness mechanics, and the open items with how to pick each up.

## What the suite covers

| Dimension | What it measures | Where | Landed |
|---|---|---|---|
| Context cost + hook latency | Always-on vs on-invoke token cost (real Claude tokens), hook wall-clock | `mcscale knowledge/audits/2026-06-19_plugin-benchmark/ctx_cost.py` | mcscale #2 |
| prose-mint accuracy | Deterministic detector vs a model pass, across docs/trials/models | mcscale audit Metric 3/3b/3c | mcscale #1 |
| lifecycle-kit quality A/B | Skill vs no-skill on `branch-birth`, `ambiguous-finalize`, 3 tiers | `benchmarks/lifecycle/ab/` | claude-plugins #10, #11 |
| knowledge-audit correctness | Golden precision/recall on a planted corpus | `benchmarks/knowledge/` | claude-plugins #9 |
| session-archive scrub A/B | Does a naive export leak secrets the skill's gated scrubber catches? | `benchmarks/knowledge/ab/` | claude-plugins #12 |
| issues add A/B | Correct id, no data loss, schema conformance | `benchmarks/knowledge/issues-ab/` | claude-plugins #13 |
| issues verify/search A/B | Status transitions against the files; search across logs | `benchmarks/knowledge/issues-ops-ab/` | claude-plugins #14 |

## The one conclusion

Skill value splits cleanly into two kinds, and which kind a given command falls into is the whole story.

**Capability uplift** (the skill makes the agent succeed where it otherwise fails) shows up in two places:
- Judgment calls the model rationalizes around. `ambiguous-finalize`: the isolated control fails at every tier (haiku 1/3, sonnet 0/3, opus 1/3); even Opus sees the two equal candidates and invents a tiebreak rather than refusing. The skill refuses 3/3.
- High-recall scans the agent cannot match by eye. `session-archive` scrub: the gated converter leaks zero planted secrets by construction; a weak-tier control leaked four of twelve on one trial, including an obvious Anthropic key, and reported success in the same output.

**Determinism and conformance insurance** (the agent usually succeeds; the skill removes the variance) covers everything self-documenting or reconstructable:
- `branch-birth`: Opus re-derives the discipline from the manifest's `integration_ref` (control 3/3) and ties; Sonnet needs the skill (0/3 vs 3/3); Haiku cannot execute the multi-step skill at all.
- `issues add`: 18/18 tie, every tier; the tracker is its own spec.
- `issues verify`: skill 9/9, control 0/9, but the control detected both reverted fixes at every tier (`detected` 2/2) and only missed the canonical status word (`Reverted`/`Open`, never `Regressed`). The value is the status vocabulary, not the verification.
- `issues search`: no effect (control 7/9, skill 6/9; the skill's losses were agent errors, not search logic).

Both kinds are real value. Only the first is capability; the second is consistency you would otherwise have to hope for.

## Reusable harness mechanics

These are the parts worth carrying to any future skill A/B.

- **Isolation lever: `claude -p --safe-mode` for both arms.** Safe-mode disables the host CLAUDE.md, the plugin, its skills, and its hooks while auth, model, and tools keep working. The skill arm inlines the `SKILL.md`; the control gets the bare task. A subagent spawned from the host session cannot be isolated (it inherits the project rules), and `--bare` will not authenticate here (no keychain read, no API key), so safe-mode is the lever. It also gives the weaker-model arm for free via `--model`.
- **The classifier gates autonomous headless agents.** Spawning `claude -p --permission-mode bypassPermissions` is blocked until the user explicitly authorizes it. This is a real permission decision, not something to work around; once authorized the same pattern runs without re-prompting.
- **Keep the ground truth out of the agent's reach.** The scrub A/B first put `expected-secrets.json` under the fixture root inside the agent's `--add-dir`, and the control trivially passed by reading the answers. Write the ground truth to an unguessable path outside any `--add-dir`, and scope `--add-dir` to the data and output dirs only.
- **Separate capability from conformance in the assert.** When the assert scores conformance to a defined form (a status vocabulary, an entry schema), measure "did the agent do the task" apart from "did it use the canonical form," or a vocabulary drift reads as a capability gap. The `issues verify` A/B looked like a 9/0 rout until a `detected` metric showed the control caught every reverted fix and only missed the word `Regressed`.
- **Score ground truth, never the self-report.** Every assert checks the produced artifact (git state, the scrubbed archive, the tracker file) because the agent's own summary is unreliable; the scrub control asserted "no secrets are exposed" over four live secrets.

## Open items

None blocking. Ordered by value.

| # | Item | Priority | How to resume |
|---|---|---|---|
| 1 | A/B harness inlines the whole `SKILL.md`, which handicaps the skill arm on light tasks | Medium | Inline only the relevant command's section, not the full file. The `issues search` skill-arm losses were agent errors from prompt weight; this understates the skill on null/tie results (immaterial to the wide decisive cells). While there, the two issues A/B dirs (`issues-ab`, `issues-ops-ab`) could fold into one scenario-based harness. |
| 2 | prose-mint MCP server fails on cold start (uvx first-run download exceeds the connect timeout) | Medium | `ostin-pil/claude-plugins#8`, still OPEN. Fix options in the issue: pre-warm the uvx cache on install, document a warm-up step, or allow a longer connect timeout. The CLI path is unaffected; only the MCP server. |
| 3 | `issues update` command has no A/B | Low | Trivial status-set; would tie like `add`. A scenario could plant an issue and assert the status moved with a commit ref, but the expected result is a tie. |
| 4 | Token counting has no `count_tokens` endpoint mode | Low | Blocked on an `ANTHROPIC_API_KEY` the sandbox lacks. `ctx_cost.py --real-tokens` already gives exact counts via the CLI usage-delta, so this is a third path, not a gap. |
| 5 | Probabilistic cells are N=3 | Low | The scrub leak rate (haiku 1.3/12) and the search noise would sharpen with a larger control-arm N; the skill arms are deterministic and need no more. The decisive cells are already wide. |
| 6 | More probe-driven fixtures as real adoptions happen | Ongoing | The adoption-probe to fixture loop (`probes/`, `probe-to-fixture.py`) turns a real adoption into a regression fixture; convert instructive ones as they accrue. |

## PR map

- **claude-plugins** (the suite): #4, #5, #7, #9 (earlier coverage), #10, #11 (lifecycle A/B), #12 (scrub), #13 (issues add), #14 (issues verify/search).
- **mcscale** (the audit): #1 (adoption + cost/latency), #2 (real tokens), #3, #4, #5 (quality-gap closures).
- **untype** (session logs): sessions 134 through 140 under `sessions/`, each a log-only PR. Session 140 is the closing review; this handover promotes its conclusions to a durable doc.
