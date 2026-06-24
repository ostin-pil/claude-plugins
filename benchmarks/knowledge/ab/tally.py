#!/usr/bin/env python3
"""Summarize the scrub A/B tally: per model and arm, how many trials leaked zero
secrets and the average number of planted secrets that survived.

Reads runs/tally.psv (ARM|MODEL|TRIAL|N|M|VERDICT|RC|ROOT). Stdlib only.
"""
import sys, collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
psv = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "runs" / "tally.psv"
if not psv.exists():
    sys.exit(f"no tally at {psv}")

agg = collections.defaultdict(list)
M = 12
for line in psv.read_text().splitlines():
    if not line.strip():
        continue
    f = line.split("|")
    arm, model, n, m = f[0], f[1], f[3], f[4]
    try:
        n = int(n); M = int(m)
    except ValueError:
        continue
    agg[(model, arm)].append(n)

print(f"{'model':28} {'arm':8} {'trials':>6} {'clean':>6} {'avg leaked':>12} {'range':>7}")
print("-" * 74)
for key in sorted(agg):
    model, arm = key
    ns = agg[key]
    t = len(ns)
    clean = sum(1 for x in ns if x == 0)
    avg = sum(ns) / t if t else 0
    rng = f"{min(ns)}-{max(ns)}" if ns else "-"
    print(f"{model:28} {arm:8} {t:>6} {clean:>3}/{t:<2} {avg:>8.1f}/{M:<3} {rng:>7}")
