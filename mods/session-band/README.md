# session-band

A Claude Code mod for repos where several sessions run at once, each in its own git worktree on a branch named `feature/session-<n>-<thread>-<what>`, as `lifecycle-kit` sets up with threads. It shows one row above the prompt:

```
my-game · session 12 art · also live: 9 tool, 11 harness
```

It warns, in yellow or red, when:

- another live session is on the same thread;
- `main` has moved under this session's branch, so it should be merged in before the state file is written;
- the main checkout has uncommitted changes, or has been switched off `main`.

It rescans every 90 seconds and after each turn. `/sessions` rescans now and lists the live sessions. Outside a git repository, or with nothing live and a clean main checkout, the row stays hidden.

## Install

```
/plugin install session-band --marketplace ostin-pil/claude-plugins
```
