#!/usr/bin/env python3
"""Score an `issues search` run: did the agent's report surface ISS-207?

Usage: assert-search.py <agent-log>

The query "thermal throttling" matches no tracker entry; the only link to ISS-207
is in a session log. So an agent that searches the session logs (as the skill
prescribes) cites ISS-207 in its report, while one that searches only the tracker
reports nothing. The log captures the agent's final text (--output-format text),
so the tracker entry headers are not echoed there unless the agent chose to report
them. Stdlib only.
"""
import re, sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        sys.exit("usage: assert-search.py <agent-log>")
    text = Path(sys.argv[1]).read_text(errors="replace") if Path(sys.argv[1]).is_file() else ""
    # strip the appended assert section if a prior run wrote it
    text = text.split("===== ASSERT =====")[0]
    found = bool(re.search(r"ISS-0*207", text))
    print(f"  {'ok' if found else 'FAIL'}  report cites ISS-207 (the log-only match): {'yes' if found else 'no'}")
    print(f"CHECKS found={int(found)}/1")
    print(f"VERDICT: {'PASS' if found else 'FAIL'}")
    return 0 if found else 1

if __name__ == "__main__":
    sys.exit(main())
