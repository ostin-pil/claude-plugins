# Lifecycle A/B results

Run 2026-06-21. Model: Opus 4.8 (both arms, to isolate the skill's effect from the
model's). N=3 per arm per scenario. Verdicts are the scenario `assert.sh`
ground-truth check, not agent self-report.

| scenario | skill arm | no-skill arm |
|---|---|---|
| branch-birth | 3/3 PASS | 3/3 PASS |
| ambiguous-finalize | 3/3 PASS | 3/3 PASS |

No differentiation at this tier. The headline is in `README.md`: branch-birth is
carried by the manifest's `integration_ref`, and the ambiguous-finalize control is
confounded because the subagent inherits the host project's `workflow.md` rules.
Both arms knew the disciplines, so both refused or based correctly.

What this establishes:

- The skills do not make a strong, rules-aware agent succeed where it would
  otherwise fail on these single-step scenarios. Their value here is determinism:
  the behavior does not depend on the agent re-deriving the rule.
- The A/B harness works (setup, control prompts, ground-truth tally), but the
  control is not yet isolated from the ambient project rules, so it cannot measure
  capability uplift as run.

Next, to actually measure uplift: isolate the control from `.claude/rules`, add a
weaker-model arm, and target the multi-step gh-mock incident scenarios where the
correct sequence is non-obvious. See `README.md`.
