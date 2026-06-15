"""P5: the opt-in mechanized banlist.

Default-off is covered in test_config.py. Here the banlist is enabled and
the focus is matching correctness, the false-positive suppressions that
make warn-by-default defensible, and the severity/strict contract.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from prose_mint.config import load_config  # noqa: E402
from prose_mint.engine import analyze  # noqa: E402


def cfg(tmp_path, body: str = "[banlist]\nenabled = true\n"):
    p = tmp_path / ".prose-mint.toml"
    p.write_text(body, encoding="utf-8")
    return load_config(explicit=p)


def _banlist(a):
    return next((c for c in a.categories if c.name == "banlist"), None)


def test_flags_default_words_and_phrases(tmp_path):
    c = cfg(tmp_path)
    text = (
        "We leverage a seamless pipeline.\n"
        "It's important to note the comprehensive design.\n"
        "This is where the engine comes in.\n"
    )
    bl = _banlist(analyze(text, config=c))
    assert bl is not None and bl.reported
    flagged = " ".join(t for _, t in bl.hits)
    assert "leverage" in flagged and "important to note" in flagged


def test_whole_word_only_no_substring_false_positives(tmp_path):
    c = cfg(tmp_path)
    # "delve" is banned; "delved"/"delver" must not trip a \b...\b match,
    # and "realm" must not match inside "overwhelmed".
    a = analyze("The overwhelmed team delved deeper.\n", config=c)
    assert _banlist(a).hits == []


def test_code_span_suppression(tmp_path):
    c = cfg(tmp_path)
    a = analyze("Call `leverage()` then `robust_parse`.\n", config=c)
    assert _banlist(a).hits == [], "inline code spans must be exempt"
    # Same word outside a code span is flagged.
    a2 = analyze("We leverage the API.\n", config=c)
    assert len(_banlist(a2).hits) == 1


def test_blockquote_suppression(tmp_path):
    c = cfg(tmp_path)
    a = analyze("> They called it a robust, seamless platform.\n", config=c)
    assert _banlist(a).hits == [], "quoted external text must be exempt"


def test_fenced_code_is_exempt(tmp_path):
    c = cfg(tmp_path)
    text = "```\nleverage seamless robust\n```\nA clean sentence.\n"
    assert _banlist(analyze(text, config=c)).hits == []


def test_pragma_skips_banlist(tmp_path):
    c = cfg(tmp_path)
    text = "<!-- prose-check: skip banlist -->\n# Doc\n\nWe leverage things.\n"
    bl = _banlist(analyze(text, config=c))
    assert bl.suppressed_by == "pragma" and not bl.reported


def test_severity_warn_does_not_fail_strict(tmp_path):
    doc = tmp_path / "d.md"
    doc.write_text("We leverage a seamless thing.\n", encoding="utf-8")
    (tmp_path / ".prose-mint.toml").write_text(
        "[banlist]\nenabled = true\n", encoding="utf-8"
    )
    r = subprocess.run(
        [sys.executable, str(REPO / "bin" / "prose-mint"),
         "scan", "--file", str(doc), "--strict"],
        capture_output=True, text=True,
    )
    assert "[banlist]" in r.stdout and "severity: warn" in r.stdout
    assert r.returncode == 0, "warn severity must not fail --strict"


def test_severity_error_fails_strict(tmp_path):
    doc = tmp_path / "d.md"
    doc.write_text("We leverage a seamless thing.\n", encoding="utf-8")
    (tmp_path / ".prose-mint.toml").write_text(
        '[banlist]\nenabled = true\nseverity = "error"\n', encoding="utf-8"
    )
    r = subprocess.run(
        [sys.executable, str(REPO / "bin" / "prose-mint"),
         "scan", "--file", str(doc), "--strict"],
        capture_output=True, text=True,
    )
    assert r.returncode == 1


def test_structural_strict_unchanged_with_banlist_off(tmp_path):
    # The structural --strict contract must be exactly as before P5.
    doc = tmp_path / "d.md"
    doc.write_text("An em dash — here.\n", encoding="utf-8")
    r = subprocess.run(
        [sys.executable, str(REPO / "bin" / "prose-mint"),
         "scan", "--file", str(doc), "--strict"],
        capture_output=True, text=True,
    )
    assert r.returncode == 1  # em-dash is error-class, still fails strict


def test_words_remove_and_add(tmp_path):
    c = cfg(tmp_path, '[banlist]\nenabled = true\n'
                       'words = ["zorp"]\nwords_remove = ["leverage"]\n')
    a = analyze("We leverage zorp here.\n", config=c)
    flagged = " ".join(t for _, t in _banlist(a).hits)
    assert "zorp" in flagged
    assert c.banlist_words.count("leverage") == 0
