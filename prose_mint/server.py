"""Thin MCP server over the engine.

Two tools, both read-only and credential-free:

  scan_text(text, label?)   the composition primitive. Claude fetches a
                            Notion page or Google Doc with the MCP you
                            already have connected, then pipes the text
                            here. No Notion/Drive auth lives in this server.
  scan_files(paths)         scan a list of local files (e.g. a PR's changed
                            paths), each with its discovered .prose-mint.toml.

The tool bodies are plain functions so the test suite exercises them with
zero third-party dependencies. FastMCP is imported lazily in main(), so the
core package stays import-clean without it; it is an optional extra
(`pip install prose-mint[mcp]`, or `uv run --with fastmcp`).
"""

from __future__ import annotations

from pathlib import Path

from .config import default_config, load_config
from .engine import analyze
from .formatters import to_payload

INSTRUCTIONS = (
    "Scan markdown/prose for structural AI-flavored tells (em dashes, "
    "arrows, 'not X but Y', bold-colon openers, AI-attribution boilerplate, "
    "hard-wrapped paragraphs). Use scan_text after fetching content from "
    "another source (Notion, Google Docs, a PR body); use scan_files for "
    "local paths. Findings are advisory; this server changes nothing."
)


def scan_text_impl(text: str, label: str = "stdin", config_path: str | None = None) -> dict:
    cfg = (
        load_config(explicit=Path(config_path))
        if config_path
        else default_config()
    )
    return to_payload(analyze(text, label=label, config=cfg))


def scan_files_impl(paths: list[str], config_path: str | None = None) -> dict:
    files = []
    total = 0
    with_hits = 0
    for p in paths:
        path = Path(p)
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as e:
            files.append({"label": p, "error": str(e)})
            continue
        cfg = (
            load_config(explicit=Path(config_path))
            if config_path
            else load_config(start_path=path)
        )
        payload = to_payload(analyze(content, label=p, config=cfg))
        files.append(payload)
        total += payload["total_hits"]
        if payload["total_hits"] > 0:
            with_hits += 1
    return {
        "tool": "prose-mint",
        "files": files,
        "summary": {
            "scanned": len(paths),
            "with_hits": with_hits,
            "total_hits": total,
        },
    }


def build_server():
    """Build and return the configured FastMCP instance. Separated from
    main() so an in-memory client can introspect and call the tools without
    starting the stdio loop."""
    from fastmcp import FastMCP  # lazy: optional extra, not a core dep

    mcp = FastMCP(name="prose-mint", instructions=INSTRUCTIONS)

    @mcp.tool(annotations={"readOnlyHint": True})
    def scan_text(text: str, label: str = "stdin", config_path: str | None = None) -> dict:
        """Scan a block of prose/markdown text for structural AI tells.

        Pass content fetched from elsewhere (a Notion page, a Google Doc, a
        PR body). Returns structured findings; reports nothing if clean.
        """
        return scan_text_impl(text, label=label, config_path=config_path)

    @mcp.tool(annotations={"readOnlyHint": True})
    def scan_files(paths: list[str], config_path: str | None = None) -> dict:
        """Scan local markdown files (e.g. a PR's changed paths). Each file
        uses its own discovered .prose-mint.toml unless config_path is set.
        """
        return scan_files_impl(paths, config_path=config_path)

    return mcp


def main() -> None:
    build_server().run()  # stdio transport (FastMCP default), plugin-launched


if __name__ == "__main__":
    main()
