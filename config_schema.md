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

### `[banlist]` (mechanized, opt-in)

Off by default and shipped with content, so opting in is one line: `enabled = true`. It is off by default on purpose. A mechanical matcher cannot tell "navigate" the verb from the figurative tell, so it is false-positive-prone; that is also why the default severity is `warn` (reported, never fails `--strict`). A project that wants enforcement sets `severity = "error"`. Inflections are not matched (`leverage` is flagged, `leveraging` is not), keeping precision over recall.

| Key | Type | Default | Meaning |
|---|---|---|---|
| `enabled` | bool | `false` | Turn the banlist on. Off means it is not even a category, so output is unchanged. |
| `words` | list | the shipped default list | Added to the default words, matched whole-word and case-insensitively. |
| `words_remove` | list | `[]` | Removed from the effective word list. |
| `phrases` | list | the shipped default list | Added to the default phrase regexes (case-insensitive). |
| `severity` | string | `"warn"` | `warn` reports only; `error` also fails `--strict`. |
| `context_suppress` | list | `["code-span","blockquote","pragma"]` | `code-span` blanks inline `` `...` `` before matching; `blockquote` skips `>` lines; `pragma` honors `<!-- prose-check: skip banlist -->`. Fenced code is always exempt. |

## Merge rules

Scalars and bools replace. Scope lists replace when the project states them, since a project declares its own scope rather than appending to the default. `structural.enabled` replaces when stated. `structural.thresholds` shallow-merges onto the default thresholds. `banlist.words` is the default plus `words` minus `words_remove`; `banlist.phrases` is the default plus `phrases`; `banlist.enabled`/`severity` replace.

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
