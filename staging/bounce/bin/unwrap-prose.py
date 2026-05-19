#!/usr/bin/env python3
"""Fallback-chain shim (staged by prose-lint P1b; do not hand-edit).

Python (not sh) so both `bin/unwrap-prose.py ...` and
`python3 bin/unwrap-prose.py ...` work, since prose-style.md and callers
invoke it by that name. Resolution: prose-lint on PATH, then the local
checkout, then the vendored original unwrap-prose-impl.py.
"""
import os
import shutil
import sys

_args = sys.argv[1:]
_tool = shutil.which("prose-lint") or os.path.expanduser(
    "~/Projects/prose-lint/bin/prose-lint"
)
if os.path.exists(_tool):
    os.execv(_tool, [_tool, "unwrap", *_args])

_impl = os.path.join(os.path.dirname(os.path.abspath(__file__)), "unwrap-prose-impl.py")
os.execv(sys.executable, [sys.executable, _impl, *_args])
