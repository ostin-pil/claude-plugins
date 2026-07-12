"""Plugin + marketplace manifests are valid and internally consistent.

These are the contracts Claude Code reads to install and launch the plugin;
a typo here is a silent install failure, so the suite guards them.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# prose-mint lives inside the claude-plugins monorepo; the marketplace is the
# repo-root manifest listing all plugins (the nested one was dropped on
# absorption, commit 32d7499).
MONOREPO = REPO.parent
MARKETPLACE = MONOREPO / ".claude-plugin" / "marketplace.json"
PLUGIN_DIR = REPO / "plugin"
PLUGIN_JSON = PLUGIN_DIR / ".claude-plugin" / "plugin.json"


def test_marketplace_manifest_lists_prose_mint_plugin():
    m = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    assert m["name"] == "ostin-pil-plugins"
    assert isinstance(m["plugins"], list)
    entry = next(p for p in m["plugins"] if p["name"] == "prose-mint")
    assert entry["source"] == "./prose-mint/plugin"
    # The source path (repo-root relative) must resolve to a real plugin.
    assert (MONOREPO / entry["source"][2:] / ".claude-plugin" / "plugin.json").is_file()


def test_plugin_manifest_valid():
    p = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    assert p["name"] == "prose-mint"
    assert "version" in p and "description" in p
    mcp = p["mcpServers"]["prose-mint"]
    assert mcp["type"] == "stdio"
    assert mcp["command"] == "uvx"
    assert "prose-mint[mcp]" in mcp["args"]
    assert "prose-mint-mcp" in mcp["args"]


def test_bundled_skill_and_command_present():
    skill = PLUGIN_DIR / "skills" / "prose-check" / "SKILL.md"
    cmd = PLUGIN_DIR / "commands" / "prose-check.md"
    assert skill.is_file() and cmd.is_file()
    head = skill.read_text(encoding="utf-8").splitlines()
    assert head[0] == "---"
    fm = "\n".join(head[1 : head.index("---", 1)])
    assert "name: prose-check" in fm
    assert "description:" in fm
    assert "allowed-tools:" in fm
