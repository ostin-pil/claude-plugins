# Configuration schema

A project tunes prose-lint by dropping a `.prose-lint.toml` anywhere above the file or directory being scanned. Discovery walks up from the target, like git or eslint, and stops at the first file found. With no file, the canonical default applies, and the default reproduces the original Untype scanner exactly.

You only state what you change. Everything you omit falls back to the default in `prose_lint/rules_default.py`.

## Sections

### `[scope]`

Controls which files the `bulk` surface walks. It does not affect a single-file `scan`.

| Key | Type | Default | Meaning |
|---|---|---|---|
| `include` | list of globs | `[]` | If non-empty, keep only files matching one of these. Empty means keep all. |
| `exclude` | list of globs | `[]` | Drop files matching any of these. Globs are matched against the path string with `fnmatch`, where `*` also crosses `/`. |
| `extensions` | list | `["md"]` | File extensions walked inside directories. |

### `[structural]`

The v1 detectors.

| Key | Type | Default | Meaning |
|---|---|---|---|
| `enabled` | list | all nine categories | Categories that run. Omitting a category from this list disables it (it reports as suppressed by config). |
| `thresholds` | table | `bold-colon-opener = 5`, `hard-wrap = 2` | Minimum hits before a category is reported. Any category not listed uses the engine builtin of 1. |

Category slugs: `em-dash`, `ascii-arrow`, `not-X-but-Y`, `no-X-no-Y-just-Z`, `this-isnt-about-X`, `not-only-but`, `bold-colon-opener`, `ai-attribution`, `hard-wrap`.

### `[language]`

| Key | Type | Default | Meaning |
|---|---|---|---|
| `cyrillic_em_dash_exempt` | bool | `true` | When Cyrillic exceeds 30% of alphabetic characters, skip the em-dash check for that file. The em dash is ordinary Russian punctuation. Every other check still applies. |

### `[pragma]`

| Key | Type | Default | Meaning |
|---|---|---|---|
| `categories` | list | all nine categories | The vocabulary accepted in a `<!-- prose-check: skip ... -->` comment. `all` is always honored regardless of this list. |

### `[banlist]` (v2, reserved)

Present so a project can stage overrides early. It is parsed and merged in v1 but enforces nothing; if you populate `words` or `phrases`, the CLI prints a one-line notice to stderr and the findings are unchanged. v2 turns this on with severity levels and context suppression.

| Key | Type | Default | Meaning (v2) |
|---|---|---|---|
| `words` | list | `[]` | Added to the default banned-word list. |
| `words_remove` | list | `[]` | Removed from the effective banned-word list. |
| `phrases` | list | `[]` | Added to the default banned-phrase list. |
| `severity` | string | `"warn"` | `warn` or `error`. |
| `context_suppress` | list | `["code-span","blockquote","pragma"]` | Contexts where a banned word is not flagged. |

## Merge rules

Scalars and bools replace. Scope lists replace when the project states them, since a project declares its own scope rather than appending to the default. `structural.enabled` replaces when stated. `structural.thresholds` shallow-merges onto the default thresholds. `banlist.words` is the default plus `words` minus `words_remove`.

## Example

```toml
# A docs-heavy repo that keeps session logs out of scope and runs strict
# bold-colon detection.

[scope]
exclude = ["sessions/*", ".claude/*"]

[structural.thresholds]
bold-colon-opener = 1

[language]
cyrillic_em_dash_exempt = true
```
