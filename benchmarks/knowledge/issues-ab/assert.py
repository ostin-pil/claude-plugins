#!/usr/bin/env python3
"""Score an `issues add` run against the planted tracker.

Usage: assert.py <repo>

Reads <repo>/knowledge/decisions/issues.md after the agent added one issue and
checks three things, each a discipline the skill encodes:
  preserved - all five planted entries (ISS-001..005) survive (no data loss; the
              skill's "read the current file before writing" guideline).
  seq       - exactly one new entry, at the next sequential id ISS-006, with no
              duplicate or out-of-sequence headers.
  schema    - the new entry carries the canonical fields (Status, Symptom, Root
              Cause, Fix).
Prints a per-check report, a machine-readable CHECKS line, and VERDICT. Exits
non-zero unless all three pass. Stdlib only.
"""
import re, sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        sys.exit("usage: assert.py <repo>")
    f = Path(sys.argv[1]) / "knowledge" / "decisions" / "issues.md"
    text = f.read_text(encoding="utf-8", errors="replace") if f.is_file() else ""

    headers = re.findall(r"(?m)^##\s+ISS-0*(\d+)\s*:", text)
    ids = [int(n) for n in headers]
    idset = set(ids)

    preserved = set(range(1, 6)).issubset(idset)
    # exactly one new entry, sequential, no dups
    seq = (sorted(ids) == [1, 2, 3, 4, 5, 6])

    # schema of the ISS-006 block: from its header to the next "## " or EOF
    schema = False
    m = re.search(r"(?m)^##\s+ISS-0*6\s*:.*?(?=^##\s|\Z)", text, re.S)
    if m:
        block = m.group(0).lower()
        schema = all(k in block for k in ("status", "symptom", "root cause", "fix"))

    print(f"  {'ok' if preserved else 'FAIL'}  preserved   (ISS-001..005 all present; found {sorted(idset)})")
    print(f"  {'ok' if seq else 'FAIL'}  seq         (exactly ISS-001..006, no dup/skip)")
    print(f"  {'ok' if schema else 'FAIL'}  schema      (ISS-006 has Status/Symptom/Root Cause/Fix)")

    ok = preserved and seq and schema
    print(f"CHECKS preserved={int(preserved)} seq={int(seq)} schema={int(schema)}")
    print(f"VERDICT: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
