# Control prompt: issues add (no-skill arm)

The bare task a user would give, with no pointer to the `issues` skill. The runner
substitutes `{{REPO}}`. Everything below the `---` is the prompt. The control must
read the existing tracker to discover the format and the next id, and append
without losing the entries already there.

---

You are helping maintain a project. We just found a bug; please log it in the
project's issue tracker so it is tracked.

Repo: {{REPO}}

The tracker is at `knowledge/decisions/issues.md`; the project's conventions are
in `.claude/lifecycle-manifest.md` if you need them.

The bug:
  Title: Overlay panel steals keyboard focus on first show
  Symptom: When the overlay appears, the target app loses keyboard focus, so the
    user's keystrokes go nowhere until they click back into it.
  Root cause: The panel is created as an activating NSPanel, so showing it makes
    the overlay key and resigns the target app.
  Fix: Create the panel as non-activating (.nonactivatingPanel) so it never
    becomes key.
  Files: Window/OverlayPanel.swift
  Session: 38

cd into the repo and actually add the issue to the tracker (this is not a dry
description). Follow the project's conventions. Report what you added.
