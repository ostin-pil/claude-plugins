#!/usr/bin/env python3
"""Score knowledge-audit against the planted ground truth in expected.json.

Runs the bundled knowledge-audit-impl.py over the repo built by setup.sh, parses
its report, and checks the orphaned / stale / unpromoted sets exactly. Prints
precision and recall per check; exits non-zero on any false positive or false
negative. Stdlib only.

Usage: REPO=$(./setup.sh); python3 score.py "$REPO"
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMPL = HERE.parent.parent / "knowledge-kit" / "bin" / "knowledge-audit-impl.py"


def run_audit(repo):
    r = subprocess.run([sys.executable, str(IMPL), "--root", repo],
                       capture_output=True, text=True, check=True)
    return r.stdout


def sections(report):
    secs, cur = {}, None
    for ln in report.splitlines():
        if ln.startswith("## "):
            cur = ln[3:].strip()
            secs[cur] = []
        elif cur is not None:
            secs[cur].append(ln)
    return secs


def body(secs, needle):
    for k, v in secs.items():
        if needle.lower() in k.lower():
            return v
    return []


def backticked(lines):
    out = []
    for ln in lines:
        if ln.lstrip().startswith("- "):
            m = re.search(r"`([^`]+)`", ln)
            if m:
                out.append(m.group(1))
    return out


def score_set(name, expected, got):
    exp, g = set(expected), set(got)
    fp, fn = g - exp, exp - g
    recall = len(exp & g) / len(exp) if exp else 1.0
    precision = len(exp & g) / len(g) if g else 1.0
    ok = not fp and not fn
    print(f"## {name}: {'PASS' if ok else 'FAIL'}  recall={recall:.2f} precision={precision:.2f}")
    if fn:
        print(f"   MISSED (false negatives): {sorted(fn)}")
    if fp:
        print(f"   EXTRA  (false positives): {sorted(fp)}")
    return ok


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: score.py <repo-path>  (the path printed by setup.sh)")
    repo = sys.argv[1]
    expected = json.loads((HERE / "expected.json").read_text())
    secs = sections(run_audit(repo))

    orphans = backticked(body(secs, "Orphaned"))
    stale = backticked(body(secs, "Stale"))
    unpromoted = re.findall(r"###\s+session\s+(\d+)", "\n".join(body(secs, "Unpromoted")))

    print("# knowledge-audit benchmark\n")
    ok = True
    ok &= score_set("orphaned", expected["orphans"], orphans)
    ok &= score_set("stale", expected["stale"], stale)
    ok &= score_set("unpromoted", expected["unpromoted_sessions"], unpromoted)
    print(f"\nVERDICT: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
