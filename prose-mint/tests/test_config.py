"""P1: per-project config layer.

Covers the override merge, discovery walk-up, the v2 banlist being parsed but
inert, and a self-contained drift test so the engine's categories and the
default ruleset can't diverge without a checked-in change.

The drift test is intentionally scoped to this repo's own artifacts. The
plan's Untype-rule parity check belongs to the (separate, not-yet-run) Untype
migration; this repo does not reach into the Untype tree.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CORPUS = REPO / "tests" / "fixtures" / "corpus"
sys.path.insert(0, str(REPO))

from prose_mint.config import default_config, load_config  # noqa: E402
from prose_mint.engine import PATTERNS, analyze  # noqa: E402
from prose_mint.rules_default import ALL_CATEGORIES, DEFAULT_RULESET  # noqa: E402

STRUCTURAL = (CORPUS / "_edge" / "structural_all.md").read_text(encoding="utf-8")
RUSSIAN = (CORPUS / "_edge" / "russian_emdash.md").read_text(encoding="utf-8")


# --- drift: engine and ruleset must agree -----------------------------------

def test_engine_categories_match_default_ruleset():
    engine_cats = {name for name, *_ in PATTERNS} | {"hard-wrap"}
    assert engine_cats == set(ALL_CATEGORIES)
    # Pragma vocabulary is the structural categories plus "banlist" (the
    # opt-in v2 category, not a PATTERNS entry).
    assert set(DEFAULT_RULESET["pragma"]["categories"]) == engine_cats | {"banlist"}


def test_default_ruleset_thresholds_match_engine_builtins():
    builtin = {name: thr for name, _, thr, _ in PATTERNS}
    builtin["hard-wrap"] = 2
    cfg = default_config()
    for name, thr in builtin.items():
        assert cfg.threshold_for(name, thr) == thr, name


# --- override: disable a category -------------------------------------------

def _toml(tmp_path: Path, body: str) -> Path:
    p = tmp_path / ".prose-mint.toml"
    p.write_text(body, encoding="utf-8")
    return p


def test_override_disables_a_category(tmp_path):
    cfg = load_config(explicit=_toml(tmp_path, """
[structural]
enabled = ["ascii-arrow"]
"""))
    a = analyze(STRUCTURAL, config=cfg)
    by = {c.name: c for c in a.categories}
    assert by["em-dash"].suppressed_by == "config"
    assert by["em-dash"].reported is False
    assert by["ascii-arrow"].reported is True
    # hard-wrap not in enabled -> also config-suppressed
    assert by["hard-wrap"].suppressed_by == "config"


def test_override_lowers_a_threshold(tmp_path):
    # Default bold-colon threshold is 5; structural_all has exactly 5.
    cfg = load_config(explicit=_toml(tmp_path, """
[structural.thresholds]
bold-colon-opener = 2
"""))
    a = analyze(STRUCTURAL, config=cfg)
    bold = next(c for c in a.categories if c.name == "bold-colon-opener")
    assert bold.threshold == 2
    assert bold.reported is True


def test_override_disables_cyrillic_exemption(tmp_path):
    base = analyze(RUSSIAN, config=default_config())
    assert base.skip_emdash is True  # default: Russian em-dash exempt

    cfg = load_config(explicit=_toml(tmp_path, """
[language]
cyrillic_em_dash_exempt = false
"""))
    a = analyze(RUSSIAN, config=cfg)
    assert a.skip_emdash is False
    em = next(c for c in a.categories if c.name == "em-dash")
    assert em.reported is True  # now flagged


# --- discovery --------------------------------------------------------------

def test_discovery_walks_up_from_target(tmp_path):
    (tmp_path / ".prose-mint.toml").write_text(
        '[structural]\nenabled = []\n', encoding="utf-8"
    )
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    doc = nested / "d.md"
    doc.write_text("An em dash — here.\n", encoding="utf-8")

    cfg = load_config(start_path=doc)
    assert cfg.source.endswith(".prose-mint.toml")
    a = analyze(doc.read_text(), config=cfg)
    assert a.total_hits == 0  # everything disabled by the discovered config


def test_no_config_file_yields_default(tmp_path):
    doc = tmp_path / "d.md"
    doc.write_text("plain text\n", encoding="utf-8")
    cfg = load_config(start_path=doc)
    assert cfg.source == "default"


# --- banlist is opt-in: inert unless enabled -------------------------------

def test_banlist_inert_unless_enabled(tmp_path, capsys):
    # A project adds words but does not enable the banlist: still inert,
    # no stderr noise, no banlist category emitted.
    cfg = load_config(explicit=_toml(tmp_path, """
[banlist]
words = ["frobnicate"]
"""))
    assert "frobnicate" in cfg.banlist_words      # merged additively
    assert "leverage" in cfg.banlist_words         # default content present
    assert cfg.banlist_enabled is False            # but off by default
    assert capsys.readouterr().err == ""           # no v1-style notice
    a = analyze("We leverage a seamless frobnicate.\n", config=cfg)
    assert a.total_hits == 0
    assert all(c.name != "banlist" for c in a.categories)


def test_banlist_default_config_is_off():
    assert default_config().banlist_enabled is False


# --- explicit overrides discovery -------------------------------------------

def test_explicit_config_wins_over_discovery(tmp_path):
    (tmp_path / ".prose-mint.toml").write_text(
        '[structural]\nenabled = []\n', encoding="utf-8"
    )
    explicit = tmp_path / "custom.toml"
    explicit.write_text('[structural]\nenabled = ["em-dash"]\n', encoding="utf-8")
    doc = tmp_path / "d.md"
    doc.write_text("An em dash — here.\n", encoding="utf-8")

    cfg = load_config(start_path=doc, explicit=explicit)
    assert cfg.source == str(explicit)
    em = next(c for c in analyze(doc.read_text(), config=cfg).categories
              if c.name == "em-dash")
    assert em.reported is True


def test_bulk_respects_config_scope_exclude(tmp_path):
    (tmp_path / "keep.md").write_text("An em dash — here.\n", encoding="utf-8")
    skipd = tmp_path / "sessions"
    skipd.mkdir()
    (skipd / "log.md").write_text("Another em dash — here.\n", encoding="utf-8")
    (tmp_path / ".prose-mint.toml").write_text(
        '[scope]\nexclude = ["sessions/*"]\n', encoding="utf-8"
    )
    res = subprocess.run(
        [sys.executable, str(REPO / "bin" / "prose-mint"), "bulk", "."],
        cwd=str(tmp_path), capture_output=True, text=True,
    )
    assert "keep.md" in res.stdout
    assert "sessions/log.md" not in res.stdout
    assert "scanned 1 file(s)" in res.stdout
