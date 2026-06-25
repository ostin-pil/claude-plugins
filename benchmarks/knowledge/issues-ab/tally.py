#!/usr/bin/env python3
"""Summarize the issues add/verify/search A/B: per scenario, model, and arm, the
pass rate and the average of each CHECKS sub-metric.

Reads runs/tally.psv (SCEN|ARM|MODEL|TRIAL|VERDICT|CHECKS|RC|REPO), where CHECKS is
scenario-specific in `name=num/den` form ("preserved=1/1 seq=1/1 schema=0/1",
"targets=3/4 regressed=1/2 nontargets=2/2", or "found=1/1"). Stdlib only.
"""
import sys, collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
psv = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "runs" / "tally.psv"
if not psv.exists():
    sys.exit(f"no tally at {psv}")

rows = collections.defaultdict(list)
for line in psv.read_text().splitlines():
    if not line.strip():
        continue
    f = line.split("|")
    scen, arm, model, verdict, checks = f[0], f[1], f[2], f[4], f[5]
    rows[(scen, model, arm)].append((verdict, checks))

for scen in sorted({k[0] for k in rows}):
    print(f"\n== {scen} ==")
    print(f"{'model':28} {'arm':8} {'trials':>6} {'pass':>6}   checks (avg)")
    print("-" * 74)
    for key in sorted(k for k in rows if k[0] == scen):
        _, model, arm = key
        recs = rows[key]
        t = len(recs)
        p = sum(1 for v, _ in recs if v == "PASS")
        sums = collections.OrderedDict()
        for _, checks in recs:
            for kv in checks.split():
                name, _, frac = kv.partition("=")
                num, _, den = frac.partition("/")
                try:
                    sums.setdefault(name, [0.0, den])
                    sums[name][0] += float(num)
                except ValueError:
                    pass
        detail = "  ".join(f"{n}={s/t:.1f}/{d}" for n, (s, d) in sums.items())
        print(f"{model:28} {arm:8} {t:>6} {p:>3}/{t:<2}   {detail}")
