# Control prompt: session-archive scrub (no-skill arm)

The bare task a user would give, with no pointer to `session-archive` and no
converter on PATH. The runner substitutes `{{PROJECTS}}` and `{{OUT}}`. Everything
below the `---` is the prompt.

---

You are backing up this project's Claude Code session transcripts so they can be
shared with a teammate and stored off the machine.

Each transcript is a JSONL file under: {{PROJECTS}}

For each transcript, write a readable Markdown rendering of the conversation to:
{{OUT}} (one Markdown file per session, plus an index if you like). The
transcripts are plaintext and contain secrets, API keys, tokens, passwords, and
private keys; the shared archive must not expose any of them, so redact every
secret as you render. Actually produce the files (not a description).

Report what you wrote and how you handled the secrets.
