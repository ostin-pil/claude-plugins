#!/usr/bin/env python3
"""Scaffold a benchmark fixture + golden from one adoption probe.

A probe (one JSON record from ~/adoption-probes.jsonl) captures a real adoption:
the manifests the inference saw, its first guess, the final approved values, and
which fields were corrected. This does the mechanical half of turning that into a
regression-net fixture: it writes golden/<eco>.json from the FINAL (ground-truth)
values and stubs fixtures/<eco>/ with empty files named after the probe's
manifests. You still fill those stubs with minimized, realistic content and run
the inference to produce results/<eco>.json. Stdlib only.

Usage:
  probe-to-fixture.py <probe.json>             # a file holding one probe object
  probe-to-fixture.py --name node-pnpm -       # read one probe from stdin
  probe-to-fixture.py --out /tmp/scratch ...   # scaffold into a scratch dir first
"""
import argparse
import json
import re
import sys
from pathlib import Path


def norm(cmds):
    out = []
    for c in cmds or []:
        c = re.sub(r"\s+", " ", str(c).strip())
        if c.lower() not in ("", "none"):
            out.append(c)
    return out


def exts(globs):
    found = []
    for g in globs or []:
        for m in re.findall(r"\.([A-Za-z0-9]+)\b", str(g)):
            if m.lower() not in found:
                found.append(m.lower())
    return found


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("probe", help="probe JSON file, or - for stdin")
    ap.add_argument("--name", help="ecosystem/fixture name (default: probe.ecosystem)")
    ap.add_argument("--out", help="output base dir (default: the adoption benchmark dir)")
    ap.add_argument("--force", action="store_true", help="overwrite an existing golden")
    a = ap.parse_args(argv)

    raw = sys.stdin.read() if a.probe == "-" else Path(a.probe).read_text()
    p = json.loads(raw)
    final = p.get("final") or {}

    eco = a.name or p.get("ecosystem")
    if not eco:
        sys.exit("no ecosystem name: pass --name or set probe.ecosystem")
    eco = re.sub(r"[^a-z0-9-]+", "-", eco.lower()).strip("-")

    base = Path(a.out).resolve() if a.out else Path(__file__).resolve().parent.parent
    gfile = base / "golden" / f"{eco}.json"
    fdir = base / "fixtures" / eco
    if gfile.exists() and not a.force:
        sys.exit(f"{gfile} exists (use --force to overwrite)")

    build, test = norm(final.get("build_commands")), norm(final.get("test_commands"))
    golden = {
        "ecosystem": p.get("ecosystem", eco),
        "product_name": final.get("product_name", ""),
        "fields": {
            "build_commands": {"accept": [build] if build else [[]]},
            "test_commands": {"accept": [test] if test else [[]]},
            "code_globs": {"accept_ext": exts(final.get("code_globs"))},
        },
        "notes": p.get("notes", ""),
    }
    gfile.parent.mkdir(parents=True, exist_ok=True)
    gfile.write_text(json.dumps(golden, indent=2) + "\n")

    fdir.mkdir(parents=True, exist_ok=True)
    stubbed = []
    for m in p.get("manifests") or []:
        mf = fdir / m
        mf.parent.mkdir(parents=True, exist_ok=True)
        if not mf.exists():
            mf.write_text("")
            stubbed.append(str(mf.relative_to(base)))

    print(f"wrote {gfile.relative_to(base)}")
    print(f"stubbed fixture {fdir.relative_to(base)}/ ({len(stubbed)} file(s))")
    for s in stubbed:
        print(f"  - {s}")
    print("\nnext:")
    print(f"  1. fill the stub files under fixtures/{eco}/ with minimized, realistic content")
    print(f"  2. widen golden/{eco}.json accept lists if other answers are also correct")
    print(f"  3. run the inference on fixtures/{eco}/ to produce results/{eco}.json")
    print("  4. python3 grade.py")


if __name__ == "__main__":
    main()
