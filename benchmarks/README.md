# Benchmarks

Two suites that guard the plugins against regressions.

- `adoption/` — can the adoption flow (`ADOPTING.md`) infer the build, test, and
  code-glob manifest values for an arbitrary repo? Fixtures graded against hidden
  goldens. See `adoption/README.md`.
- `lifecycle/` — do the lifecycle skills produce the right git state when an agent
  actually runs them? Offline scenarios with a file-based remote and a `gh` mock.
  See `lifecycle/README.md`.

## Authoring fan-out harnesses

Some benchmarks fan out across many subagents (the adoption runs, the multi-doc
prose comparison). When that fan-out is driven by the Workflow tool, one failure
mode has actually bitten and is worth a guard before every launch.

The Workflow `args` value arrives verbatim and untyped. Passing a JSON-encoded
string where the script expects an array delivers a string, and iterating a
string with `for...of` walks it one character at a time without throwing. A
malformed input then silently spawns one agent per character, up to the
1000-agent cap. A real run hit exactly this and burned about 7.9 million tokens
over 21 minutes before it failed (the mcscale `ISS-001` incident). The trap is
that iterating the wrong type does not error, so the bug stays invisible until it
is expensive.

Two guards, either of which prevents it:

- Do not pass fan-out data through `args`. Embed a fixed work-list as a constant
  in the script, or validate the arg's shape (`Array.isArray`, the keys you
  expect) and throw immediately when it is wrong.
- Bound the job count before the fan-out call (`if (jobs.length > N) throw ...`),
  so a bad input fails in milliseconds instead of running to the cap.

The shape of a safe harness is a validated or embedded work-list, a hard cap, then
`parallel` or `pipeline` over it. Treat any externally supplied work-list as
possibly-unparsed until you have checked it.
