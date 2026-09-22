---
name: github-delivery
description: 'Deliver a change through git and GitHub — create the branch and an isolated worktree, commit, open or update a pull request against the correctly probed base branch, address review comments, check CI, ship submodule changes as their own PR, and clean up after merge. Use when work needs a worktree or branch, when changes need committing and pushing, when a PR needs opening or updating, or when review feedback or CI needs handling.'
allowed-tools: Bash
---

# Delivery

Branch, worktree, commit, PR, review, CI, cleanup.

Three facts drive most failures here: the remote's **advertised default
branch can be wrong**, a **reused merged branch** diffs against stale
history, and a **submodule pointer** committed with the parent pins it to a
commit that does not exist upstream yet.

## Capabilities

| Capability | Action | Description |
|------------|--------|-------------|
| Setup Worktree | `actions/setup-worktree.md` | Anchor to the main worktree, probe the base, branch, isolate, install deps |
| Open Pull Request | `actions/open-pull-request.md` | Submodules first, stage explicitly, commit, push, open or update |
| Review Comments | `actions/review-comments.md` | Change, reply with what changed, then resolve |
| Check CI | `actions/check-ci.md` | Read the rollup, quote failures verbatim, classify |
| Submodule Delivery | `actions/submodule-delivery.md` | Own branch and PR; parent excludes the pointer; merge order stated |
| Finish Branch | `actions/finish-branch.md` | **Ask first.** Pin bump, worktree and branch cleanup |

## Standards

| Standard | File | Description |
|----------|------|-------------|
| Branch and Commit | `standards/branch-and-commit.md` | Base probing, branch naming, commit format, hooks |
| PR Conventions | `standards/pr-conventions.md` | Titles, bodies, target, merge strategy, links |
| Review Etiquette | `standards/review-etiquette.md` | Reply before resolve, disagreeing, scoping |
| Checklist | `standards/checklist.md` | Pre-commit, submodule, PR, review, reporting |

## Principles

1. **Probe the base branch** — the advertised default can be stale or wrong,
   and the failure is silent.
2. **Fetch before branching** — a stale ref diffs against moved history.
3. **Never reuse a merged branch** — fresh branch, redo the change. No
   cherry-pick, no force-push to reconcile.
4. **Reply before resolve** — "Done ✅" is not a reply.
5. **Disagree out loud** — post the evidence, leave the thread open.
6. **Submodules ship separately** — own branch, own PR, parent excludes the
   pointer.
7. **Pushing is not delivering** — check CI, fix forward with a new commit.
8. **Every PR gets a link** — inline, plus an end-of-reply recap.

## Usage

1. Load this manifest and `standards/branch-and-commit.md`.
2. Probe the base branch before anything else.
3. Execute the capability's action file.
4. Validate against `standards/checklist.md`.
