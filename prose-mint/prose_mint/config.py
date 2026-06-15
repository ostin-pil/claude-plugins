"""Per-project configuration.

A project drops a `.prose-mint.toml` anywhere above the file/dir being
scanned; discovery walks up from the target like git/eslint. The file
extends or relaxes the canonical default in rules_default.py; the absence
of a file (the common case, and every P0 regression case) yields the
default, which reproduces the original scanner exactly.

Merge semantics, kept deliberately simple and predictable:
  - scalars and bools: replace
  - scope lists (include/exclude/extensions): replace if the project states
    them (a project declares its own scope, it doesn't append to ours)
  - structural.enabled: replace if stated (omitting a category disables it)
  - structural.thresholds: shallow-merge onto the default thresholds
  - banlist.words: default + words - words_remove (v2; inert in v1)
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from .rules_default import DEFAULT_RULESET

CONFIG_FILENAME = ".prose-mint.toml"

# Engine builtin per-category threshold when neither the default ruleset nor a
# project overrides it.
_BUILTIN_THRESHOLD = 1


@dataclass
class Config:
    enabled: list[str]
    thresholds: dict[str, int]
    cyrillic_em_dash_exempt: bool
    pragma_categories: list[str]
    include: list[str]
    exclude: list[str]
    extensions: list[str]
    banlist: dict = field(default_factory=dict)
    source: str = "default"  # path of the .prose-mint.toml, or "default"

    def threshold_for(self, name: str, builtin: int = _BUILTIN_THRESHOLD) -> int:
        return self.thresholds.get(name, builtin)

    @property
    def banlist_enabled(self) -> bool:
        return bool((self.banlist or {}).get("enabled"))

    @property
    def banlist_severity(self) -> str:
        return (self.banlist or {}).get("severity", "warn")

    @property
    def banlist_words(self) -> list[str]:
        return list((self.banlist or {}).get("words", []))

    @property
    def banlist_phrases(self) -> list[str]:
        return list((self.banlist or {}).get("phrases", []))

    @property
    def banlist_context_suppress(self) -> list[str]:
        return list((self.banlist or {}).get("context_suppress", []))


def _deep_merge(base: dict, over: dict) -> dict:
    """Merge `over` onto a copy of `base`. Lists replace; dicts recurse."""
    out = {k: (v.copy() if isinstance(v, dict) else v) for k, v in base.items()}
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _to_config(ruleset: dict, source: str) -> Config:
    structural = ruleset.get("structural", {})
    scope = ruleset.get("scope", {})
    language = ruleset.get("language", {})
    pragma = ruleset.get("pragma", {})
    banlist = dict(ruleset.get("banlist", {}))

    # banlist.words / .phrases are additive over the default, minus
    # words_remove. enabled/severity/context_suppress fall back to default.
    bl_default = DEFAULT_RULESET["banlist"]
    words = list(dict.fromkeys(bl_default["words"] + banlist.get("words", [])))
    for w in banlist.get("words_remove", []):
        if w in words:
            words.remove(w)
    banlist["words"] = words
    banlist["phrases"] = list(
        dict.fromkeys(bl_default["phrases"] + banlist.get("phrases", []))
    )
    banlist.setdefault("enabled", bl_default["enabled"])
    banlist.setdefault("severity", bl_default["severity"])
    banlist.setdefault("context_suppress", list(bl_default["context_suppress"]))

    return Config(
        enabled=list(structural.get("enabled", DEFAULT_RULESET["structural"]["enabled"])),
        thresholds=dict(structural.get("thresholds", {})),
        cyrillic_em_dash_exempt=bool(
            language.get("cyrillic_em_dash_exempt", True)
        ),
        pragma_categories=list(pragma.get("categories", [])),
        include=list(scope.get("include", [])),
        exclude=list(scope.get("exclude", [])),
        extensions=list(scope.get("extensions", ["md"])),
        banlist=banlist,
        source=source,
    )


def default_config() -> Config:
    return _to_config(DEFAULT_RULESET, "default")


def find_config_file(start: Path) -> Path | None:
    """Walk up from `start` (a file or dir) looking for .prose-mint.toml."""
    start = start.resolve()
    base = start if start.is_dir() else start.parent
    for d in [base, *base.parents]:
        candidate = d / CONFIG_FILENAME
        if candidate.is_file():
            return candidate
    return None


def load_config(
    *,
    start_path: Path | None = None,
    explicit: Path | None = None,
) -> Config:
    """Resolve effective config. Explicit path wins; else discover by walking
    up from start_path; else the canonical default."""
    path = explicit
    if path is None and start_path is not None:
        path = find_config_file(start_path)
    if path is None:
        return default_config()

    with open(path, "rb") as f:
        project = tomllib.load(f)
    merged = _deep_merge(DEFAULT_RULESET, project)
    return _to_config(merged, str(path))
