# context-effort

A Claude Code mod that adds one row above the prompt:

```
context 38% (76k of 200k) · effort high
```

- **context** is the status line's figure: the input tokens the last response was answered over, against the model's context window. It turns yellow from 70% and red from 85%. After a fresh start or a compaction it reads `new window` until the next response.
- **effort** is the reasoning effort the main loop's last model request was sent at, after any downgrade for the model. A sub-agent's requests are left out, since they run at their own effort. It reads `model default` when the request carried no level, and `not sent yet` before the first request.

## Install

```
/plugin install context-effort --marketplace ostin-pil/claude-plugins
```

It is a hooks module with no options and no commands. `tests/` holds two tests that run with `claude plugin test`.
