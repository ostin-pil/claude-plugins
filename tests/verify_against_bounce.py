"""Real-repo dogfood: the P1b pre-flip gate.

Runs the live Untype/Bounce bin/check-prose-bulk.sh and the extracted
prose-lint over the same CI-relevant doc set in the *current* Bounce tree
(not the frozen 05-15 corpus) and asserts byte-identical output. This proves
the extraction is faithful on the real repo as it stands today, which is the
gate the plan requires before any project is flipped to consume prose-lint.

Manual check (needs the live Bounce checkout), like regen_golden.py:
    python3 tests/verify_against_bounce.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BOUNCE = Path(os.environ.get("UNTYPE_REPO", "/Users/costa/Projects/Bounce"))
OLD = BOUNCE / "bin" / "check-prose-bulk.sh"
NEW = REPO / "bin" / "prose-lint"

# The set Untype's CI gate cares about (prose.yml path filter), restricted to
# what exists at the Bounce root plus the three doc trees.
ROOT_DOCS = ["README.md", "PLAYBOOK.md", "GUIDE.md",
             "API_ARCHITECTURE_MVP.md", "IMPLEMENTATION_PLAN.md"]
TREES = ["knowledge/", "research/", "reports/"]


def main() -> int:
    if not OLD.exists():
        print(f"no live Bounce scanner at {OLD}", file=sys.stderr)
        return 2
    paths = [d for d in ROOT_DOCS if (BOUNCE / d).is_file()] + TREES

    old = subprocess.run([str(OLD), *paths], cwd=str(BOUNCE),
                          capture_output=True, text=True)
    new = subprocess.run([sys.executable, str(NEW), "bulk", *paths],
                          cwd=str(BOUNCE), capture_output=True, text=True)

    if old.stdout == new.stdout and old.returncode == new.returncode:
        lines = old.stdout.splitlines()
        summary = next((l for l in lines if l.startswith("scanned ")), "")
        print(f"IDENTICAL on live Bounce ({len(paths)} path args). {summary}")
        return 0

    print("DIVERGED. unified diff (old vs new):", file=sys.stderr)
    import difflib
    for line in difflib.unified_diff(
        old.stdout.splitlines(), new.stdout.splitlines(),
        "live check-prose-bulk.sh", "prose-lint bulk", lineterm="",
    ):
        print(line, file=sys.stderr)
    print(f"\nreturncodes: old={old.returncode} new={new.returncode}",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
