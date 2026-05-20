"""In-memory functional smoke for the FastMCP wiring.

Kept out of the dep-free pytest suite (it needs fastmcp). Run it via uv so
the dependency is ephemeral:

    uv run --with fastmcp python tests/smoke_mcp.py

Uses FastMCP's in-memory Client (the documented testing path) to list the
tools and call each, asserting the same results the unit tests pin on the
impl functions, now through the real MCP tool layer.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from prose_mint.server import build_server  # noqa: E402

SAMPLE = "It's not X. An em dash — here. Arrow → there.\n"


async def run() -> int:
    from fastmcp import Client

    server = build_server()
    async with Client(server) as client:
        tools = {t.name for t in await client.list_tools()}
        assert tools == {"scan_text", "scan_files"}, tools

        r = await client.call_tool("scan_text", {"text": SAMPLE, "label": "smoke"})
        payload = r.data
        assert payload["tool"] == "prose-mint"
        assert payload["label"] == "smoke"
        assert payload["total_hits"] > 0
        names = {c["name"] for c in payload["categories"]}
        assert {"em-dash", "ascii-arrow", "hard-wrap"} <= names

        clean = await client.call_tool("scan_files", {"paths": [str(REPO / "pyproject.toml")]})
        # pyproject.toml isn't markdown but the scanner still runs; just
        # assert the envelope shape.
        assert clean.data["summary"]["scanned"] == 1

    print(f"MCP smoke OK: tools={sorted(tools)}, scan_text total_hits="
          f"{payload['total_hits']}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(run()))
