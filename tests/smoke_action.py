"""Verify the reusable CI action: structure + a real run of its scan pipeline.

Kept out of the dep-free pytest suite (YAML parse needs a lib). Run via uv:

    uv run --with pyyaml python tests/smoke_action.py

Part 1 parses action.yml and the example/own workflows and asserts the
composite shape, inputs, and that the steps drive the prose-lint CLI.

Part 2 reproduces the action's "scan changed markdown" step against a throw
away git repo: a changed README with a tell and a sessions/ file the repo's
.prose-lint.toml excludes. It asserts the consumer-config scoping flows
through the pipeline and that --strict flips the exit code. This is the
behavior a GitHub run would exercise, checked locally.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROSE_LINT = str(REPO / "bin" / "prose-lint")


def check_structure() -> None:
    import yaml

    action = yaml.safe_load((REPO / "action.yml").read_text())
    assert action["runs"]["using"] == "composite"
    assert set(action["inputs"]) == {"strict", "scan-pr-body", "python-version", "config"}
    steps_text = yaml.dump(action["runs"]["steps"])
    assert "prose-lint bulk" in steps_text and "prose-lint scan --stdin" in steps_text
    assert "actions/setup-python" in steps_text
    assert 'pip install "${{ github.action_path }}"' in steps_text

    # PyYAML (YAML 1.1) parses the `on:` key as boolean True; GitHub's own
    # parser does not. Read it back under either key.
    def trigger(doc):
        return doc.get("on", doc.get(True))

    example = yaml.safe_load((REPO / "examples" / "prose.yml").read_text())
    assert "pull_request" in trigger(example)
    own = yaml.safe_load((REPO / ".github" / "workflows" / "prose.yml").read_text())
    uses = [s.get("uses") for s in own["jobs"]["prose"]["steps"]]
    assert "./" in uses, uses
    print("action structure OK")


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True,
                    capture_output=True, text=True)


def check_pipeline() -> None:
    with tempfile.TemporaryDirectory() as d:
        repo = Path(d)
        _git(repo, "init", "-q")
        _git(repo, "config", "user.email", "t@t")
        _git(repo, "config", "user.name", "t")
        (repo / "README.md").write_text("# ok\n\nClean base line.\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-qm", "base")
        base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo,
                              capture_output=True, text=True).stdout.strip()

        # A change a consumer cares about, and one its config excludes.
        (repo / "README.md").write_text("# ok\n\nAn em dash — here is a tell.\n")
        (repo / "sessions").mkdir()
        (repo / "sessions" / "log.md").write_text("Another em dash — here.\n")
        (repo / ".prose-lint.toml").write_text('[scope]\nexclude = ["sessions/*"]\n')
        _git(repo, "add", "-A")
        _git(repo, "commit", "-qm", "change")

        diff = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=d", f"{base}...HEAD"],
            cwd=repo, capture_output=True, text=True).stdout.split()
        changed = [f for f in diff if f.endswith(".md")]
        assert "README.md" in changed and "sessions/log.md" in changed

        warn = subprocess.run([sys.executable, PROSE_LINT, "bulk", *changed],
                              cwd=repo, capture_output=True, text=True)
        assert warn.returncode == 0, "warn-only must not fail the build"
        assert "README.md" in warn.stdout
        assert "sessions/log.md" not in warn.stdout, "config exclude must apply"
        assert "scanned 1 file(s)" in warn.stdout

        strict = subprocess.run(
            [sys.executable, PROSE_LINT, "bulk", "--strict", *changed],
            cwd=repo, capture_output=True, text=True)
        assert strict.returncode == 1, "strict must fail on a hit"
    print("action scan pipeline OK (consumer-config scoping + strict exit)")


if __name__ == "__main__":
    check_structure()
    check_pipeline()
    print("SMOKE OK")
