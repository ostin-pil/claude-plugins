"""Prove the fallback-chain shim before it is applied to Bounce.

Builds a throwaway sandbox: the *current* Bounce bin scripts copied in as
the vendored *-impl fallbacks, plus the staged shims. Then asserts, on the
same sample, that all three are byte-identical:

  - shim with prose-lint reachable (local checkout) -> the shared tool
  - shim with prose-lint NOT reachable               -> the vendored impl
  - the original Bounce script run directly          -> the baseline

If those three agree, flipping Bounce to the shim changes nothing the CI
gate or the prose-check skill can observe. Nothing here touches Bounce.

    python3 staging/bounce/verify_shims.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

STAGE = Path(__file__).resolve().parent
BOUNCE_BIN = Path(os.environ.get("UNTYPE_REPO", "/Users/costa/Projects/Untype")) / "bin"

SAMPLE = (
    "# Sample\n\nAn em dash — here is a structural tell.\n\n"
    "It's not X, it's Y as a clause.\n\nArrow flow input → output.\n\n"
    "Co-Authored-By: someone <x@y>\n"
)


def build_sandbox(tmp: Path) -> Path:
    bind = tmp / "bin"
    bind.mkdir(parents=True)
    # Current Bounce scripts become the vendored fallbacks.
    shutil.copy(BOUNCE_BIN / "check-prose.sh", bind / "check-prose-impl.py")
    shutil.copy(BOUNCE_BIN / "check-prose-bulk.sh", bind / "check-prose-bulk-impl.py")
    shutil.copy(BOUNCE_BIN / "unwrap-prose.py", bind / "unwrap-prose-impl.py")
    # The staged shims under the original names.
    for n in ("check-prose.sh", "check-prose-bulk.sh", "unwrap-prose.py"):
        shutil.copy(STAGE / "bin" / n, bind / n)
    for f in bind.iterdir():
        f.chmod(0o755)
    return bind


def run(cmd, *, env=None, stdin=None, cwd=None):
    return subprocess.run(cmd, capture_output=True, text=True,
                          input=stdin, env=env, cwd=cwd)


def main() -> int:
    if not (BOUNCE_BIN / "check-prose.sh").exists():
        print(f"no Bounce bin at {BOUNCE_BIN}", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        bind = build_sandbox(tmp)
        doc = tmp / "sample.md"
        doc.write_text(SAMPLE, encoding="utf-8")

        base_env = dict(os.environ)
        # python3 must stay reachable for the impl fallback.
        py_dir = str(Path(sys.executable).parent)
        minimal_path = f"{py_dir}:/usr/bin:/bin"

        # 1. Baseline: the original Bounce scanner, run directly.
        baseline = run(["python3", str(BOUNCE_BIN / "check-prose.sh"),
                        "--file", str(doc)])

        # 2. Shim, prose-lint NOT reachable (HOME with no checkout, no PATH
        #    entry) -> must fall back to the vendored impl.
        fb_env = dict(base_env)
        fb_env["HOME"] = str(tmp / "nohome")
        fb_env["PATH"] = minimal_path
        fallback = run([str(bind / "check-prose.sh"), "--file", str(doc)],
                       env=fb_env)

        # 3. Shim, prose-lint reachable via the real local checkout.
        sh_env = dict(base_env)
        sh_env["HOME"] = os.path.expanduser("~")
        sh_env["PATH"] = minimal_path  # not on PATH -> uses ~/Projects checkout
        shared = run([str(bind / "check-prose.sh"), "--file", str(doc)],
                     env=sh_env)

        ok = (baseline.stdout == fallback.stdout == shared.stdout)
        print("check-prose.sh:")
        print(f"  baseline rc={baseline.returncode} fallback rc={fallback.returncode} "
              f"shared rc={shared.returncode}")
        print(f"  identical: {ok}")
        if not ok:
            import difflib
            for tag, other in (("fallback", fallback), ("shared", shared)):
                if other.stdout != baseline.stdout:
                    print(f"  --- baseline vs {tag} ---", file=sys.stderr)
                    for ln in difflib.unified_diff(
                        baseline.stdout.splitlines(), other.stdout.splitlines(),
                        "baseline", tag, lineterm=""):
                        print("  " + ln, file=sys.stderr)
            return 1

        # bulk + unwrap: just confirm the shims run and agree fallback vs shared.
        b_fb = run([str(bind / "check-prose-bulk.sh"), str(doc)], env=fb_env)
        b_sh = run([str(bind / "check-prose-bulk.sh"), str(doc)], env=sh_env)
        u_fb = run([str(bind / "unwrap-prose.py"), "--stdin"], env=fb_env, stdin=SAMPLE)
        u_sh = run([str(bind / "unwrap-prose.py"), "--stdin"], env=sh_env, stdin=SAMPLE)
        bulk_ok = b_fb.stdout == b_sh.stdout
        unwrap_ok = u_fb.stdout == u_sh.stdout == subprocess.run(
            ["python3", str(BOUNCE_BIN / "unwrap-prose.py"), "--stdin"],
            capture_output=True, text=True, input=SAMPLE).stdout
        print(f"check-prose-bulk.sh: fallback==shared: {bulk_ok}")
        print(f"unwrap-prose.py: fallback==shared==original: {unwrap_ok}")
        if not (bulk_ok and unwrap_ok):
            return 1

    print("\nSHIM VERIFY OK: shim (shared) == shim (fallback) == original, "
          "for scan, bulk, and unwrap.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
