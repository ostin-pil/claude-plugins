#!/usr/bin/env python3
"""Grade adoption-inference results against the per-fixture golden manifests.

For each fixture under fixtures/<eco>/ with a golden.json, read the inferred
values from results/<eco>.json (produced by running the adoption inference on
that fixture) and score the three portability-critical manifest fields:
product_name, build_commands, test_commands, code_globs.

Grading is deliberately lenient: a field passes if it matches any accepted
variant (commands compared as normalized sets; code_globs by the extension they
target). Stdlib only. Prints a Markdown report to stdout; exits non-zero if any
field mismatched, so it can gate CI.
"""
import argparse
import json
import re
import sys
from pathlib import Path


def norm_cmd(s):
    return re.sub(r"\s+", " ", str(s).strip().lower())


def norm_set(lst):
    return frozenset(norm_cmd(x) for x in (lst or []) if norm_cmd(x) not in ("", "none"))


def grade_commands(inferred, accept):
    got = norm_set(inferred)
    for opt in accept:
        if got == norm_set(opt):
            return "ok", got
    return "MISS", got


def grade_globs(inferred, accept_ext):
    exts = set()
    for g in inferred or []:
        for m in re.findall(r"\.([a-z0-9]+)\b", str(g).lower()):
            exts.add(m)
    missing = [e for e in accept_ext if e not in exts]
    return ("ok" if not missing else "MISS"), sorted(exts)


def grade_fixture(golden, inferred):
    rows, ok_count, total = [], 0, 0
    # product_name
    total += 1
    pn_got = (inferred.get("product_name") or "").strip()
    pn_ok = pn_got.lower() == golden["product_name"].lower()
    ok_count += pn_ok
    rows.append(("product_name", "ok" if pn_ok else "MISS", pn_got, golden["product_name"]))
    # command + glob fields
    for field, spec in golden["fields"].items():
        total += 1
        if "accept" in spec:
            verdict, got = grade_commands(inferred.get(field), spec["accept"])
            want = " | ".join(" ".join(o) if o else "(none)" for o in spec["accept"])
        else:
            verdict, got = grade_globs(inferred.get(field), spec["accept_ext"])
            want = "ext: " + ",".join(spec["accept_ext"])
        ok_count += verdict == "ok"
        rows.append((field, verdict, ", ".join(sorted(got)) or "(empty)", want))
    return rows, ok_count, total


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixtures", default=str(Path(__file__).parent / "fixtures"))
    ap.add_argument("--results", default=str(Path(__file__).parent / "results"))
    args = ap.parse_args(argv)

    fixtures_dir, results_dir = Path(args.fixtures), Path(args.results)
    print("# Adoption inference benchmark\n")
    grand_ok = grand_total = fixtures_graded = any_miss = 0
    for fx in sorted(p for p in fixtures_dir.iterdir() if (p / "golden.json").exists()):
        eco = fx.name
        golden = json.loads((fx / "golden.json").read_text())
        rfile = results_dir / f"{eco}.json"
        if not rfile.exists():
            print(f"## {eco} — NO RESULT ({rfile} missing)\n")
            any_miss = 1
            continue
        inferred = json.loads(rfile.read_text())
        rows, ok, total = grade_fixture(golden, inferred)
        fixtures_graded += 1
        grand_ok += ok
        grand_total += total
        any_miss |= ok < total
        print(f"## {eco} ({golden['ecosystem']}) — {ok}/{total}\n")
        print("| field | verdict | inferred | accepted |")
        print("|---|---|---|---|")
        for name, verdict, got, want in rows:
            mark = "PASS" if verdict == "ok" else "**MISS**"
            print(f"| {name} | {mark} | `{got}` | {want} |")
        print()
    print(f"---\n\n**Total: {grand_ok}/{grand_total} fields across {fixtures_graded} fixtures.**")
    return 1 if any_miss else 0


if __name__ == "__main__":
    sys.exit(main())
