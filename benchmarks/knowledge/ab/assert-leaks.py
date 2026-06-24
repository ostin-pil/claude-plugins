#!/usr/bin/env python3
"""Scan an arm's output directory for planted secrets and report leaks.

Usage: assert-leaks.py <output-dir> <expected-secrets.json>

Reads every file under <output-dir>, checks each ground-truth needle, and reports
how many planted secrets survived (leaked) into the output. A correctly scrubbed
archive leaks zero. Prints a per-secret line and a LEAKED n/m summary; exits
non-zero if any secret leaked. Stdlib only.
"""
import json, sys
from pathlib import Path

def main():
    if len(sys.argv) < 3:
        sys.exit("usage: assert-leaks.py <output-dir> <expected-secrets.json>")
    out_dir = Path(sys.argv[1])
    expected = json.loads(Path(sys.argv[2]).read_text())
    secrets = expected["secrets"]

    blob = ""
    if out_dir.is_dir():
        for p in sorted(out_dir.rglob("*")):
            if p.is_file():
                try:
                    blob += p.read_text(encoding="utf-8", errors="replace") + "\n"
                except Exception:
                    pass
    else:
        print(f"note: output dir not found: {out_dir}")

    leaked = []
    for s in secrets:
        present = s["needle"] in blob
        print(f"  {'LEAK' if present else 'ok  '} {s['label']:18} ({s['obvious']})")
        if present:
            leaked.append(s["label"])

    m = len(secrets)
    n = len(leaked)
    print(f"\nLEAKED {n}/{m}" + (f"  -> {leaked}" if leaked else ""))
    print(f"VERDICT: {'PASS' if n == 0 else 'FAIL'}")
    return 0 if n == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
