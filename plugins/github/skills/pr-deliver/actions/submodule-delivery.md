# Action — Submodule Delivery

Shipping a change that spans a parent repo and a git submodule. Getting this
wrong either pins the parent to an unmerged commit or loses the submodule
change entirely.

## The rule

**Both sides are edited in the same worktree. Each ships its own branch and
PR. The parent commit excludes the submodule pointer.**

The parent reads the submodule from its working tree, so both sides are
testable locally before anything is pushed. The pin stays on base until the
submodule PR merges — then it moves as a deliberate follow-up commit.

## Step 1 — Detect what changed

```bash
git config --file .gitmodules --get-regexp path | awk '{print $2}'
git -C <sub> rev-parse --abbrev-ref HEAD      # feature branch?
git -C <sub> status --porcelain               # uncommitted?
git -C <sub> log --oneline @{u}..HEAD         # unpushed?
```

## Step 2 — Ship the submodule

Run the full commit → push → PR cycle **inside** the submodule, against its
own remote and base:

```bash
cd <sub>
SUB_BASE=<from config, else probe>
git fetch origin
gh pr create --base "$SUB_BASE" --title "<type>: [<TICKET>] <2–5 words>" --body-file <file>
```

Same ticket link as the parent. Record the URL.

## Step 3 — Commit the parent without the pointer

```bash
cd <parent-root>
git status --porcelain            # the submodule path shows modified — leave it
git add <files excluding the submodule path>
git diff --staged --stat          # verify: no submodule path staged
git commit -m "<type>: <TICKET> <description>"
```

Never `git add -A` here. Never push a pointer bump directly to a protected
branch.

## Step 4 — Keep parallel variants in sync

Where a module defines the same resource in two shapes (a single-item and a
multi-item variant, for instance), they drift silently and the drift only
surfaces for whichever consumers use the neglected one. Every change lands in
both — diff them against each other before pushing.

## Step 5 — State the merge order

```
Merge order:
  1. <submodule repo>#<n>   <url>
  2. <parent repo>#<n>      <url>   — bump the pin after #1 merges
```

The pin bump is a separate commit after the submodule PR merges. Say so; do
not leave the user to work it out.

## Report

```
Submodule PR: <repo>#<n> — <url>   (base: <sub base>)
Parent PR:    <repo>#<n> — <url>   (base: <base>)
Gitlink:      excluded from the parent commit — pin still on base
Merge order:  submodule first, then the parent pin bump
Variants:     <both updated | n/a>
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| A second worktree for the submodule | Same worktree, branch inside it |
| Writing against an uninitialised submodule | `git submodule update --init` first |
| `checkout` without `pull` on its base | The pin is usually behind |
| `git add -A` in the parent | Stage explicitly; verify the gitlink is absent |
| Pushing a pointer bump to a protected branch | It goes through a PR too |
| Updating one of two parallel variants | Both, always |
| Leaving the merge order implicit | State it |
