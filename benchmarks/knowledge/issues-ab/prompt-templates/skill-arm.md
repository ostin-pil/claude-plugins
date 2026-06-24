You are managing a project's issue tracker, as a benchmark of the `issues` skill.
Follow the skill instructions appended below, verbatim. Resolve the manifest keys
from the repo's `.claude/lifecycle-manifest.md`.

Repo: {{REPO}}

Task: perform `/issues add` for this bug.
  Title: Overlay panel steals keyboard focus on first show
  Symptom: When the overlay appears, the target app loses keyboard focus, so the
    user's keystrokes go nowhere until they click back into it.
  Root cause: The panel is created as an activating NSPanel, so showing it makes
    the overlay key and resigns the target app.
  Fix: Create the panel as non-activating (.nonactivatingPanel) so it never
    becomes key.
  Files: Window/OverlayPanel.swift
  Session: 38

cd into the repo and actually update the tracker file (this is not a dry
description). Report what you added.
