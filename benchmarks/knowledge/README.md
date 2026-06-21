# knowledge-audit benchmark

Tests whether `knowledge-audit` flags exactly the right docs and logs, not just
that it runs. The audit is a deterministic scan (orphaned docs, stale docs,
unpromoted session learnings), so the benchmark is a golden correctness test: a
corpus with a known ground truth, scored for precision and recall against it.

## How it works

`setup.sh` builds a throwaway git repo with a controlled knowledge base:

- two orphaned docs (nothing references them),
- one stale doc, added in a backdated commit and never touched since, that is
  still cited by a session log (so it is stale but not an orphan),
- three session logs: one promoted (its number appears under `knowledge/`), one
  unpromoted (it does not), and one with no decisions section,
- plus referenced docs and a promoted session that must NOT be flagged.

`score.py <repo>` runs the bundled `knowledge-audit-impl.py` over that repo,
parses the report, and checks the orphaned / stale / unpromoted sets exactly. It
prints precision and recall per check and exits non-zero on any false positive or
false negative.

## Run

```
REPO=$(./setup.sh)
python3 score.py "$REPO"
```

## Baseline

PASS, 1.0 precision and 1.0 recall on all three checks: the audit flags exactly
`{orphan-a, orphan-b}`, the stale `old-stale.md` (kept out of orphans by its
citation), and session 51, while leaving the cited docs, the promoted session 50,
and the decision-less session 52 untouched. The corpus is small by design; the
value is a regression net that catches a logic change in any of the three checks.

## Why git dates, not mtime

The stale check reads the last commit date per file (`git log`, not filesystem
mtime), so `setup.sh` plants staleness with a backdated commit
(`GIT_*_DATE=2026-01-01`) rather than touching timestamps. With the default
`--stale-days 90`, that doc reads as stale; everything else is committed now.
