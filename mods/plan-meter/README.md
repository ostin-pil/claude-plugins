# plan-meter

A Claude Code mod for a subscription's usage windows. It shows one row above the prompt, the 5-hour and weekly windows with when each resets, and the session's model:

```
5h 42% until 18:00 · week 30% until Mon 09:00 · opus-5-5
```

A window turns yellow from 75% and red from 90%, and a toast appears at 80%, 90% and 95% with a hint on whether to wait for the reset.

It also keeps a ledger, shared by every session on the machine, of how many window points each model spent and how many turns and tokens it used.

- `/meter` prints the ledger.
- `/meter run <label>` opens a labelled run, so a batch can be measured on its own; `/meter run off` closes it.
- `/meter clear` empties the ledger.

A headless run (`claude -p`) cannot type a command, so it names its run in the `PLAN_METER_RUN` environment variable instead, and only that session counts toward it.

The percentages are account-wide, so another session working at the same time is counted too. Off a subscription there are no windows and the row stays hidden.

## Install

```
/plugin install plan-meter --marketplace ostin-pil/claude-plugins
```
