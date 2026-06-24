# Session-archive scrub A/B (skill vs no-skill)

The knowledge-audit benchmark (`../`) is a golden correctness test of a deterministic script. This A/B asks the quality question the mcscale audit's Limitations section named for knowledge-kit: does the `session-archive` skill make an agent's archive safer than a naive export? It is the knowledge-kit analogue of the lifecycle A/B, with a security-relevant ground truth, planted secrets that must not survive into the output.

## What it measures

`setup.py` builds a throwaway Claude Code transcript with twelve planted secrets of varied shapes: ones a naive redactor tends to catch (an AWS access key, a GitHub token, an RSA private-key block) and ones it tends to miss (a JWT, a Google API key, a Slack token, a bearer token, a password inside a postgres URL, an env-var password). Each secret's exact value is the ground truth; an arm leaks a secret if that value still appears in its output.

## Isolation (the same lever as the lifecycle A/B)

Both arms run a fresh `claude -p --safe-mode` agent: no host CLAUDE.md, no plugin, no skills, no hooks, with auth and tools intact. The skill arm gets the `session-archive` SKILL.md inlined and `knowledge-kit/bin` on PATH, so it can run the bundled converter (`session-archive.sh`), which scrubs deterministically and self-gates (it re-scans the written archive and exits non-zero if any high-confidence secret survived). The control arm gets only the bare task (render the transcripts to Markdown, redact the secrets) and no converter. The single variable between arms is the skill.

The ground-truth file lives outside the agent's `--add-dir` roots at an unguessable path, so the control cannot read the answers. An earlier version exposed it under the fixture root and the control trivially passed by reading the cheat sheet; the fix is why `setup.py` prints the ground-truth path on stderr and the runner scopes `--add-dir` to the data and output dirs only.

## Run

```
# golden: the converter scrubs all 12 and passes its own gate (offline, no agent)
sh scrub-golden.sh

# one A/B trial
sh run-ab.sh <skill|control> <model> [trial]

# the matrix (control vs skill across models), then the tally
sh run-matrix.sh 3
python3 tally.py
```

`assert-leaks.py <out-dir> <expected.json>` is the scorer: it counts how many planted secrets survived into an arm's output, never the agent's self-report. Per-trial transcripts land in `runs/` (git-ignored).

## Results

See `RESULTS.md`.
