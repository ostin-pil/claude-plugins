#!/usr/bin/env python3
"""Score an `issues verify` run against the planted fixture.

Usage: assert-verify.py <repo>

Each "Resolved (verify)" issue should transition based on whether its Fix marker
is still in the referenced file: ISS-101 and ISS-103 held (-> Resolved), ISS-102
and ISS-104 were reverted (-> Regressed). The two non-target issues (ISS-105 Open,
ISS-106 Resolved) must not change. Prints a per-issue report, a CHECKS line, and
VERDICT. Stdlib only.
"""
import re, sys
from pathlib import Path

EXPECT = {101: "Resolved", 102: "Regressed", 103: "Resolved",
          104: "Regressed", 105: "Open", 106: "Resolved"}
TARGETS = (101, 102, 103, 104)
REGRESSED = (102, 104)

def status_of(text, n):
    m = re.search(rf"(?ms)^##\s+ISS-0*{n}\s*:.*?(?=^##\s|\Z)", text)
    if not m:
        return None
    s = re.search(r"\*\*Status\*\*:\s*(.+)", m.group(0))
    return s.group(1).strip() if s else None

def main():
    if len(sys.argv) < 2:
        sys.exit("usage: assert-verify.py <repo>")
    text = (Path(sys.argv[1]) / "knowledge/decisions/issues.md").read_text(errors="replace")

    correct = {}
    for n, want in EXPECT.items():
        got = status_of(text, n)
        ok = (got or "").lower() == want.lower()
        correct[n] = ok
        tag = "target" if n in TARGETS else "keep  "
        print(f"  {'ok' if ok else 'FAIL'}  ISS-{n} [{tag}]  want={want!r:14} got={got!r}")

    # "detected" is the softer capability signal: for a reverted fix, did the agent
    # move it off Resolved/Resolved (verify) to anything signalling not-fixed,
    # regardless of whether it used the canonical word "Regressed"? That separates
    # the verification capability (notice the fix is gone) from schema conformance
    # (use the project's status vocabulary).
    detected = 0
    for n in REGRESSED:
        got = (status_of(text, n) or "").strip().lower()
        if got and got not in ("resolved", "resolved (verify)"):
            detected += 1

    targets_ok = sum(correct[n] for n in TARGETS)
    regressed_ok = sum(correct[n] for n in REGRESSED)
    nontargets_ok = sum(correct[n] for n in (105, 106))
    all_ok = all(correct.values())

    print(f"CHECKS targets={targets_ok}/4 regressed={regressed_ok}/2 detected={detected}/2 nontargets={nontargets_ok}/2")
    print(f"VERDICT: {'PASS' if all_ok else 'FAIL'}")
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
