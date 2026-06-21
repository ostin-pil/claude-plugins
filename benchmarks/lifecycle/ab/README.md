# Lifecycle value A/B (skill vs no-skill)

The lifecycle execution scenarios test that an agent *running the skill* produces
the correct git state. This A/B asks the next question: does the skill make a
difference? It reuses each scenario's `setup.sh` and `assert.sh`, and adds a
control arm, a fresh agent given the bare task with no `SKILL.md`, run against the
same setup. Correct-completion rate is compared arm to arm with the ground-truth
assert, never the agent's self-report.

## How to run one scenario

For arm in {skill, no-skill}, for N trials:

1. The agent runs the scenario's `setup.sh` (its own throwaway repo) and reports
   the repo path.
2. Skill arm: the agent follows the scenario's skill (`run-agent-prompt.md`
   pattern). No-skill arm: the agent gets `control-prompts/<scenario>.md`, the
   same goal phrased as a user would, with no pointer to the skill.
3. Run `scenarios/<scenario>/assert.sh <repo>` on each repo; tally PASS rate.

## The result so far, and the catch

First run: two scenarios (`branch-birth`, `ambiguous-finalize`), N=3 per arm, the
session model (Opus 4.8), ground-truth asserts. Every trial passed, both arms,
both scenarios (12/12). The skill did not change the outcome here, for two
reasons worth stating plainly:

- `branch-birth` is carried by the manifest. The control agents read
  `integration_ref: origin/main` from `.claude/lifecycle-manifest.md`, fetched,
  and branched off it. The skill's "do not substitute local main" warning is
  belt-and-suspenders a competent agent did not need.
- `ambiguous-finalize` is confounded. The control was not skill-free: a subagent
  runs inside the host project, so it inherits that project's `CLAUDE.md` and
  `.claude/rules/workflow.md`, which already say "more than one finalize candidate
  with no explicit target is an abort-or-ask, never an auto-pick." Both arms knew
  the rule; several control agents cited it by name, others reasoned it from first
  principles.

So at the top model tier, in a rules-aware environment, these skills add
determinism and consistency, not capability uplift on these two scenarios. That is
an honest and useful thing to know: the value is "you do not have to hope the
agent re-derives the rule each time," not "the agent fails without it."

## To measure capability uplift (what this harness needs next)

- **Isolate the control** from the host project's lifecycle rules, so the no-skill
  arm is genuinely naive. A subagent inheriting `workflow.md` is not a fair
  control. Run it from a directory with no ambient `.claude/rules`.
- **Add a weaker-model arm.** The uplift, if any, shows where the agent would
  otherwise slip; Sonnet or Haiku is the likelier place to see auto-pick or a
  branch off stray-ahead `main`.
- **Use the complex incident scenarios.** The single-step git invariants are easy
  to reason out. The value, if it is anywhere, is in the multi-step gh-mock cases
  (`finalize-already-merged` re-entry, the `partial` assert-then-reconcile) where
  the correct sequence is non-obvious even to a strong agent.
