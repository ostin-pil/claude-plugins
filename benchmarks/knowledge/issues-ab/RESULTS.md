# Issues add A/B results

## Run 2026-06-24: does the skill help an agent log an issue correctly?

Both arms run a fresh `claude -p --safe-mode` agent against a repo whose tracker already holds ISS-001..005 in the canonical format. Each is asked to add the same new bug, with the same structured details. The skill arm gets the `issues` SKILL.md inlined; the control gets only the bare task. Verdict is `assert.py` on the tracker file: all five originals preserved, exactly one new entry at the next sequential id (ISS-006), and the new entry carries the canonical fields. N=3 per arm per model.

| model | arm | pass | preserved | seq | schema |
|---|---|---:|---:|---:|---:|
| haiku 4.5 | control | 3/3 | 3/3 | 3/3 | 3/3 |
| haiku 4.5 | skill | 3/3 | 3/3 | 3/3 | 3/3 |
| sonnet 4.6 | control | 3/3 | 3/3 | 3/3 | 3/3 |
| sonnet 4.6 | skill | 3/3 | 3/3 | 3/3 | 3/3 |
| opus 4.8 | control | 3/3 | 3/3 | 3/3 | 3/3 |
| opus 4.8 | skill | 3/3 | 3/3 | 3/3 | 3/3 |

## The finding: a complete tie, and why

Eighteen of eighteen pass, both arms, every tier, every check. There is no differentiation to report, and the reason is the point: `issues add` is self-documenting. The agent has to read the tracker to find the next id anyway, and once it has the file open, the entry format, the highest id, and the five existing entries are all in front of it. The control reconstructs the convention by copying what it sees, on every trial, even on Haiku. The "read the current file before writing" guideline that the skill states explicitly is what a competent agent does by default when the task is "append to this file," so no arm lost data.

This is the same shape as `branch-birth` at the top tier in the lifecycle A/B (the manifest carried the discipline, so the control re-derived it) and the prose-redaction control at the strong tiers in the scrub A/B (told to redact, it did). Where the discipline is reconstructable from the artifact in front of the agent, the skill adds determinism and consistency, not capability. For `issues add` that is the whole story: the tracker is its own spec.

## Scope, and where the skill would differentiate

This tested one command on its happy path, and that is the command most carried by the existing file. The `issues` skill has three others whose procedure is not visible in a single append:

- `search` greps the tracker and the session-log directory together; a naive agent told "find related issues" might search only the tracker and miss the log mentions.
- `verify` re-checks every "Resolved (verify)" issue against its referenced files and transitions it to Resolved or Regressed; a naive agent would not know that convention exists.
- `update` moves an issue through the defined status values with a commit reference.

Those are where a knowledge-kit `issues` A/B could plausibly show uplift, because the procedure is not reconstructable from reading one entry. The `add` happy path measured here is the self-documenting floor, and it ties. So the honest conclusion for `issues` is narrow: on the common add path the skill is consistency insurance rather than capability, and the commands that would test capability (verify, search) are left for a future run.

## Scope and caveats

- N=3 per cell, one fixture, one bug. The tie is clean (every check passes everywhere), so a larger N would not change the qualitative finding for `add`; it would only matter for catching a rare weak-tier data-loss slip, which did not occur here.
- The structured bug details were given to both arms identically, so the entry's content was not a variable; only the agent's handling of format, numbering, and preservation was.
