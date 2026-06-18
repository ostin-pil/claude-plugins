#!/usr/bin/env python3
"""Grade adoption-inference results against the per-ecosystem golden manifests.

For each golden under golden/<eco>.json, read the inferred values from
results/<eco>.json (produced by running the adoption inference on fixtures/<eco>)
and score the four portability-critical fields: product_name, build_commands,
test_commands, code_globs.

Goldens live outside the fixture repos on purpose, so an inference agent
inspecting a fixture cannot see the expected answer.

Grading is deliberately lenient: a field passes if it matches any accepted
variant (commands compared as normalized sets; code_globs by the extension they
target; product_name by case-insensitive membership). Stdlib only. Prints a
Markdown report; exits non-zero if any field mismatched, so it can gate CI.
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


def grade_product(inferred, golden_pn):
    accept = golden_pn if isinstance(golden_pn, list) else [golden_pn]
    got = (inferred or "").strip()
    ok = got.lower() in {a.lower() for a in accept}
    return ("ok" if ok else "MISS"), got, " | ".join(accept)


def grade_fixture(golden, inferred):
    rows, ok_count, total = [], 0, 0
    total += 1
    v, got, want = grade_product(inferred.get("product_name"), golden["product_name"])
    ok_count += v == "ok"
    rows.append(("product_name", v, got, want))
    for field, spec in golden["fields"].items():
        total += 1
        if "accept" in spec:
            v, got = grade_commands(inferred.get(field), spec["accept"])
            want = " | ".join(" ".join(o) if o else "(none)" for o in spec["accept"])
        else:
            v, got = grade_globs(inferred.get(field), spec["accept_ext"])
            want = "ext: " + ",".join(spec["accept_ext"])
        ok_count += v == "ok"
        rows.append((field, v, ", ".join(sorted(got)) if isinstance(got, frozenset) else ", ".join(got) or "(empty)", want))
    return rows, ok_count, total


def main(argv=None):
    here = Path(__file__).parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--golden", default=str(here / "golden"))
    ap.add_argument("--results", default=str(here / "results"))
    args = ap.parse_args(argv)

    golden_dir, results_dir = Path(args.golden), Path(args.results)
    print("# Adoption inference benchmark\n")
    grand_ok = grand_total = graded = any_miss = 0
    for gf in sorted(golden_dir.glob("*.json")):
        eco = gf.stem
        golden = json.loads(gf.read_text())
        rfile = results_dir / f"{eco}.json"
        if not rfile.exists():
            print(f"## {eco} — NO RESULT ({rfile.name} missing)\n")
            any_miss = 1
            continue
        rows, ok, total = grade_fixture(golden, json.loads(rfile.read_text()))
        graded += 1
        grand_ok += ok
        grand_total += total
        any_miss |= ok < total
        flag = "" if ok == total else "  <- gap"
        print(f"## {eco} ({golden.get('ecosystem','?')}) — {ok}/{total}{flag}\n")
        print("| field | verdict | inferred | accepted |")
        print("|---|---|---|---|")
        for name, verdict, got, want in rows:
            mark = "PASS" if verdict == "ok" else "**MISS**"
            print(f"| {name} | {mark} | `{got}` | {want} |")
        print()
    print(f"---\n\n**Total: {grand_ok}/{grand_total} fields across {graded} fixtures.**")
    return 1 if any_miss else 0


if __name__ == "__main__":
    sys.exit(main())
