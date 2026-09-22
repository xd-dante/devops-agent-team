# Action — Finish Branch

Clean up after a PR merges. **Ask first** — the user decides when work is
finished.

## Gate

- [ ] The PR is actually merged (verify; do not take it on trust)
- [ ] The user confirmed cleanup for this branch
- [ ] Any dependent PR (a submodule's) has merged too, or is accounted for

Any box unticked → 🛑 STOP.

```bash
gh pr view <n> --json state,mergedAt --jq '{state, mergedAt}'
```

## Step 1 — Pin bump, if a submodule shipped

Merging the submodule PR does not move the parent's pin. If the parent should
now track the merged submodule commit, that is a **new branch and a new PR**:

```bash
git checkout "$BASE" && git pull --ff-only
git checkout -b <user>/chore/<ticket>-submodule-pin
git submodule update --remote <sub>
git add <sub> && git commit -m "chore: <TICKET> bump <sub> pin"
```

Never push a pin bump straight to a protected branch.

## Step 2 — Remove the worktree and branches

```bash
MAIN_ROOT=$(git worktree list --porcelain | awk '/^worktree /{print $2; exit}')
git -C "$MAIN_ROOT" worktree remove "$WORKTREE_PATH"
git -C "$MAIN_ROOT" branch -d "$BRANCH"
git -C "$MAIN_ROOT" push origin --delete "$BRANCH"    # if not auto-deleted on merge
git -C "$MAIN_ROOT" fetch --prune
```

`worktree remove` refuses if the worktree is dirty — that refusal is
information. Report it rather than forcing past it; something uncommitted is
in there.

The submodule's branch lives inside the worktree's submodule clone and goes
with it. If it was pushed, its PR is independent — clean that up after it
merges.

## Report

```
PR:        <url> — merged <timestamp>
Worktree:  removed <path>   | kept, because <reason>
Branches:  local <deleted|kept>   remote <deleted|kept>
Pin bump:  <PR url> | not needed
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Cleaning up unprompted | Ask; the user decides when it is done |
| Assuming the PR merged | Verify with `gh pr view` |
| Forcing past a dirty-worktree refusal | Report it — something is uncommitted |
| Pushing the pin bump to a protected branch | New branch, new PR |
| Deleting a branch whose submodule PR is still open | Account for it first |
