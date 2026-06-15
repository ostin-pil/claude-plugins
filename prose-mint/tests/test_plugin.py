"""Plugin + marketplace manifests are valid and internally consistent.

These are the contracts Claude Code reads to install and launch the plugin;
a typo here is a silent install failure, so the suite guards them.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MARKETPLACE = REPO / ".claude-plugin" / "marketplace.json"
PLUGIN_DIR = REPO / "plugin"
PLUGIN_JSON = PLUGIN_DIR / ".claude-plugin" / "plugin.json"


def test_marketplace_manifest_valid_and_points_at_plugin():
    m = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    assert m["name"] == "prose-mint"
    assert isinstance(m["plugins"], list) and len(m["plugins"]) == 1
    entry = m["plugins"][0]
    assert entry["name"] == "prose-mint"
    assert entry["source"] == "./plugin"
    # The local source path must resolve to a real plugin.
    assert (REPO / entry["source"][2:] / ".claude-plugin" / "plugin.json").is_file()


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
