#!/usr/bin/env python3
"""Summarize the `issues` add A/B: per model and arm, the pass rate and how often
each discipline check held (preserved / seq / schema).

Reads runs/tally.psv (ARM|MODEL|TRIAL|VERDICT|CHECKS|RC|REPO), where CHECKS is
"preserved=1 seq=1 schema=0". Stdlib only.
"""
import sys, collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
psv = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "runs" / "tally.psv"
if not psv.exists():
    sys.exit(f"no tally at {psv}")

agg = collections.defaultdict(lambda: {"n": 0, "pass": 0, "preserved": 0, "seq": 0, "schema": 0})
for line in psv.read_text().splitlines():
    if not line.strip():
        continue
    f = line.split("|")
    arm, model, verdict, checks = f[0], f[1], f[3], f[4]
    a = agg[(model, arm)]
    a["n"] += 1
    if verdict == "PASS":
        a["pass"] += 1
    for kv in checks.split():
        k, _, v = kv.partition("=")
        if k in a and v == "1":
            a[k] += 1

print(f"{'model':28} {'arm':8} {'trials':>6} {'pass':>6} {'preserved':>10} {'seq':>5} {'schema':>7}")
print("-" * 78)
for key in sorted(agg):
    model, arm = key
    a = agg[key]; t = a["n"]
    print(f"{model:28} {arm:8} {t:>6} {a['pass']:>3}/{t:<2} {a['preserved']:>6}/{t:<3} {a['seq']:>2}/{t:<2} {a['schema']:>4}/{t:<2}")
