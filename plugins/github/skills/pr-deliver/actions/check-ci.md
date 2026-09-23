# Action — Check CI

A push is not a delivery. Establish whether the pipeline passed, and if not,
why.

## Step 1 — Status

```bash
gh pr checks
gh pr view --json statusCheckRollup \
  --jq '.statusCheckRollup[] | {name, status, conclusion, detailsUrl}'
```

`pending` is not `passing`. Wait for the rollup to settle, or say explicitly
that checks were still running.

## Step 2 — Read the failing log

```bash
RUN=$(gh run list --branch "$(git branch --show-current)" --limit 1 --json databaseId --jq '.[0].databaseId')
gh run view "$RUN" --log-failed
```

Quote the failure verbatim. A paraphrased CI error sends the fix in the wrong
direction.

## Step 3 — Classify

| Failure | Usual cause |
|---------|-------------|
| Commit-lint rejects the message | Format or scope casing — check `vcs.commit_style` |
| Formatter check fails | Formatter not run, or unrelated churn got committed |
| Validation fails only in CI | An environment variable or workspace the local run had set |
| Toolchain version mismatch | The project pins a version the local shell does not use |
| Chart or manifest lint fails | Render problem — hand to `helm-engineer` |
| Policy admission check fails | Policy config, often in a different repo than expected |
| Missing schema / unknown attribute | An uninitialised submodule was committed against |

## Step 4 — Fix forward

New commit. **Never** amend something already pushed, and never skip a hook
to get green — fix the cause.

## Report

```
PR:      <url>
Checks:  <n> passed, <n> failed, <n> pending
Failing: <job> — <error, verbatim>
Cause:   <diagnosis>
Fix:     <new commit | HANDOFF → <agent>>
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Reporting a push as delivered | Check CI first |
| Treating `pending` as passing | Wait, or say they were still running |
| Paraphrasing the error | Quote it verbatim |
| Amending a pushed commit | New commit, always |
| Skipping a hook to get green | Fix the cause |
