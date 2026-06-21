# Control prompt: branch-birth (no-skill arm)

The bare task a user would give, with no pointer to `session-start`. Substitute the
scenario `setup.sh` path. The agent should report `REPO=<path>` as its last line.

---

You are helping in a git repository. I'm starting a new work session and want my
work on a dedicated feature branch, per the project's convention.

1. Run this setup script first; it prepares the repo and prints its path on stdout
   (the last line). cd into that repo:
   <repo>/benchmarks/lifecycle/scenarios/branch-birth/setup.sh
2. Create the new session's feature branch (session number 200, topic `bench`) so I
   can start working on it. Follow the repo's conventions; there is a
   `.claude/lifecycle-manifest.md` if you need them. Actually create the branch
   (not a dry run). No GitHub access; the remote is local, so do not run gh.
3. Report, as the LAST line of your message, exactly: REPO=<the repo path from step 1>
