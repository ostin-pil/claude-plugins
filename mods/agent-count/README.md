# agent-count

A Claude Code mod that counts every sub-agent that actually ran in a session, nested ones included. The count a session launched is not the count that ran, because sub-agents start their own.

- The status line shows `agents 7 (3 nested)` once one has run.
- `/agent-count` prints a line ready for a session log: how many the session started, how many ran in total, by type and by model, with output tokens, then one row per agent with its description, turns and tokens.

It counts from when the mod loaded, and it cannot see whether an agent wrote files; a log should say that itself. It pairs with `lifecycle-kit`'s session logs.

## Install

```
/plugin install agent-count --marketplace ostin-pil/claude-plugins
```
