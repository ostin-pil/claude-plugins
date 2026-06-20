# Adoption probes

A probe is one captured real-world adoption: the manifests the inference saw, the
values it first guessed, the values you finally approved, and which fields you had
to correct. Probes are how the synthetic fixtures grow. The six fixtures here are
hand-built and ecosystem-clean; real repos are where the inference actually meets
workspaces, odd build scripts, and ecosystems we have not covered. A field you
correct during the adoption review is a labeled miss, and that is the signal worth
collecting.

## Where probes live

Probes stay local while you collect them, one JSON line per adopted repo in
`~/adoption-probes.jsonl`. They are not committed: real repos can be private, and
a raw probe carries repo labels and notes. Only the minimized, anonymized
fixtures derived from instructive probes get committed (under `fixtures/` and
`golden/`). The `*.jsonl` in this directory is git-ignored for the same reason.

## The probe record

```json
{
  "date": "2026-06-19",
  "repo": "acme-web",
  "ecosystem": "node-pnpm-workspace",
  "manifests": ["package.json", "pnpm-workspace.yaml"],
  "inferred": {"product_name": "acme-web", "build_commands": ["npm run build"], "test_commands": ["npm test"], "code_globs": ["*.ts"]},
  "final":    {"product_name": "acme-web", "build_commands": ["pnpm -r build"], "test_commands": ["pnpm -r test"], "code_globs": ["*.ts", "*.tsx"]},
  "corrected": ["build_commands", "test_commands", "code_globs"],
  "notes": "pnpm workspace; npm is wrong, build/test must recurse with pnpm -r"
}
```

`inferred` versus `final`, plus `corrected`, is the miss signal. `manifests` is
what the inference saw, so a probe can be rebuilt as a fixture. `corrected: []`
means a clean inference, which is still worth recording as a coverage
confirmation. See `example-probe.json` for the same record on disk.

## Capturing a probe (zero extra work)

The adoption flow already shows you the proposed manifest for review before
committing (ADOPTING.md step 6). Append one step to the step-2 prompt you paste
into each repo, and Claude writes the probe as the last thing it does:

```
7. After I approve the manifest, append one JSON line to ~/adoption-probes.jsonl
   recording this adoption as a benchmark probe: the date, a short repo label, an
   ecosystem tag, the dependency-manifest files you found, your FIRST inference of
   {product_name, build_commands, test_commands, code_globs}, the FINAL approved
   values, and the list of fields I corrected (empty if your first guess stood).
   Notes field for any gotcha. Nothing secret; the label and notes are enough.
```

## The feedback loop

Hand over a batch of probes (or just say go) every several adoptions, or whenever
a correction happened. Each probe routes one of two ways.

A miss (a corrected field) is triaged for whether it is a one-off or a pattern. A
repeating pattern earns a sharper ADOPTING.md step-2 instruction, then a benchmark
re-run to confirm the fix and guard it, the same loop that closed the Python
build-step miss. A clean repro of the miss usually becomes a fixture too, so the
gap cannot reopen silently.

A new ecosystem not covered by the six fixtures (workspaces and monorepos,
gradle or maven, cmake, bazel, swift package, elixir mix, and so on) becomes a
minimized synthetic fixture plus a golden, added to the regression net.

## Turning a probe into a fixture

`probe-to-fixture.py` does the mechanical half. Given a probe it writes
`golden/<eco>.json` from the final (ground-truth) values and stubs
`fixtures/<eco>/` with empty files named after the probe's manifests:

```
python3 probe-to-fixture.py <probe.json>
# or read one probe from a batch:
sed -n '3p' ~/adoption-probes.jsonl | python3 probe-to-fixture.py --name node-pnpm-workspace -
```

Then fill the stub files with minimized, realistic content (no secrets, no real
identifiers), widen the golden `accept` lists if other answers are also correct,
run the inference on the new fixture to produce `results/<eco>.json`, and
`python3 grade.py`. Use `--out <dir>` to scaffold into a scratch directory first
if you want to inspect before writing into the benchmark.

For a no-manifest repo (a `manifests: []` probe, such as an ops or shell repo)
the helper has no filenames to stub, so author the representative files by hand.
The first such case, `shell-ops-no-build`, is a worked example: it grades clean
and still surfaced a finding (the inference declines a `shellcheck` test gate that
the real adoption accepted). A future probe schema could carry a small sample of
key files to close that gap.
