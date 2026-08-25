"""Output encoding: the scanner must survive its own findings.

A finding quotes the offending line, so the output carries whatever the scanned
document carries. On Windows a redirected stdout falls back to the ANSI code
page, and cp1252 cannot encode an ASCII arrow, the robot emoji in an
AI-attribution footer, or any Cyrillic at all. Before the fix these killed the
process with UnicodeEncodeError on exactly the input the scanner exists to
report, and only when redirected, so an interactive run looked healthy while CI
died.

Every test here forces `PYTHONIOENCODING=cp1252` on the child, which reproduces
the Windows failure on any platform. Without that these would pass everywhere
UTF-8 is the default and guard nothing.

Note what is *not* in the list below: the em dash. cp1252 encodes it at 0x97,
so the tool's most common finding never crashed, which is part of why this
went unnoticed.
"""

from __future__ import annotations

import io
import os
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from prose_mint.cli import main as cli_main  # noqa: E402

ARROW = "→"
ROBOT = "\U0001f916"
CYRILLIC = "привет"


def _cp1252_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "cp1252"
    env.pop("PYTHONUTF8", None)
    return env


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(REPO / "bin" / "prose-mint"), *args],
        cwd=str(REPO),
        capture_output=True,
        env=_cp1252_env(),
    )


@pytest.mark.parametrize(
    "name,char",
    [("ascii-arrow", ARROW), ("ai-attribution", ROBOT), ("cyrillic", CYRILLIC)],
)
def test_scan_survives_characters_cp1252_cannot_encode(tmp_path, name, char):
    # The character has to sit on a line that actually trips a detector, since
    # only a reported line is quoted back into stdout. An arrow is the cheapest
    # tell to carry a payload, so the Cyrillic case rides one.
    doc = tmp_path / f"{name}.md"
    doc.write_text(f"A line {ARROW} containing {char}.\n", encoding="utf-8")

    res = _run("scan", "--file", str(doc), "--no-config")

    assert res.returncode == 0, res.stderr.decode("utf-8", "replace")
    assert char.encode("utf-8") in res.stdout, "the finding lost its own evidence"


def test_bulk_survives_them_too(tmp_path):
    (tmp_path / "a.md").write_text(f"Arrow {ARROW} here.\n", encoding="utf-8")
    (tmp_path / "b.md").write_text(f"Robot {ROBOT} here.\n", encoding="utf-8")

    res = _run("bulk", "--no-config", str(tmp_path))

    assert res.returncode == 0, res.stderr.decode("utf-8", "replace")
    assert ARROW.encode("utf-8") in res.stdout


def test_the_em_dash_was_never_the_problem(tmp_path):
    """Pinning the thing that made this hard to see.

    cp1252 encodes the em dash, so the most-reported category always worked.
    If a future change makes this crash, the diagnosis above is wrong and the
    comment in `_force_utf8_output` needs revisiting.
    """
    doc = tmp_path / "dash.md"
    doc.write_text("An em dash — right here.\n", encoding="utf-8")

    res = _run("scan", "--file", str(doc), "--no-config")

    assert res.returncode == 0
    assert "—".encode("cp1252") == b"\x97"


def test_a_replaced_stdout_is_left_alone():
    """`redirect_stdout` hands us a StringIO, which has no `reconfigure`.

    The regression suite captures in-process this way, and an embedder may do
    the same. Reconfiguring is not ours to do when the stream is not ours.
    """
    buf = io.StringIO()
    real_stdin = sys.stdin
    sys.stdin = io.StringIO("A line with an em dash — in it.\n")
    try:
        with redirect_stdout(buf):
            rc = cli_main(["scan", "--stdin", "--no-config", "--label", "x"])
    finally:
        sys.stdin = real_stdin
    assert rc == 0
    assert "em-dash" in buf.getvalue()
