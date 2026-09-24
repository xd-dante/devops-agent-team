# Action — Open Pull Request

Commit, push, and open or update the PR. Submodules first.

## Step 1 — Submodules first, if any

```bash
git config --file .gitmodules --get-regexp path 2>/dev/null | awk '{print $2}'
git -C <sub> rev-parse --abbrev-ref HEAD      # on a feature branch?
git -C <sub> status --porcelain               # uncommitted?
git -C <sub> log --oneline @{u}..HEAD         # unpushed?
```

Any of those → run `actions/submodule-delivery.md` for that submodule before
touching the parent, and record its PR URL.

## Step 2 — Verify the branch is fit to use

```bash
git branch --show-current
git log --oneline "origin/$BASE"..HEAD
```

If this branch's PR has already merged, **do not reuse it**. Start fresh from
the pulled base and redo the change — cherry-picking or force-pushing to
reconcile makes it worse.

## Step 3 — Review and stage

```bash
git status --porcelain
git diff
git add <explicit paths>          # never -A in a repo with submodules
git diff --staged --stat          # verify: no submodule path in the staged set
```

Verifying the staged set is the step people skip. `git add -A` sweeps in the
submodule pointer, and the parent then references a commit that does not
exist on the submodule's base yet.

Revert unrelated formatter churn before staging.

Then **audit what the change removes**, against the merge base:

```bash
git fetch origin "$BASE"
git diff "origin/$BASE...HEAD" --numstat | awk '$2>0'   # files with removals
git diff "origin/$BASE...HEAD"                          # read every '-' line
```

Three dots, against the merge base. A two-dot diff mixes in the base's newer
commits, which hides real losses among unrelated noise.

This catches the failure where a file was rewritten wholesale from a copy read
somewhere else and silently dropped keys nobody meant to remove. Edit in
place, and if a deletion is not part of the intended change, find out why
before pushing.

## Step 4 — Commit

```bash
git commit -m "<type>: <TICKET> <description>"
```

Scopeless unless `vcs.commit_style: scoped`. No `-s`. No AI attribution. If
the repo's hooks generate files, `--no-verify` is legitimate — say so in the
report and keep generated files out of the commit.

## Step 5 — Push and open or update

```bash
git push -u origin "$(git branch --show-current)"
gh pr view --json number,url,headRefName 2>/dev/null   # existing PR?
gh pr create --base "$BASE" --title "<type>: [<TICKET>] <2–5 words>" --body-file <file>
```

Existing PR → update the body rather than opening a second one, and address
any open review comments (`actions/review-comments.md`) before reporting.

Pass `--base` explicitly. Relying on the remote's default is how PRs end up
on the wrong branch.

## Step 6 — Check CI

Run `actions/check-ci.md`. Pushing is not delivering.

## Report

```
Parent PR:    <url>      (base: <BASE>)
Submodule PR: <url>      (base: <sub base>)   — if any
Commit:       <sha> — <subject>
Gitlink:      excluded from the parent commit
CI:           <status>
Merge order:  <submodule first, then parent pin bump>   — if applicable
Ticket:       <ticket url>
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Opening the PR without `--base` | Pass the probed base explicitly |
| Reusing a merged branch | Fresh branch from pulled base; redo the change |
| `git add -A` with submodules | Stage explicit paths; verify with `--staged --stat` |
| Committing the submodule pointer | Submodule ships its own branch and PR |
| A second PR for the same branch | Update the existing one |
| Reporting the push as done | Check CI first |
| Not reading the `-` lines | A wholesale rewrite drops keys silently |
| Two-dot diff to audit removals | Three dots, against the merge base |
| A PR mentioned without its URL | Link inline, every time |
