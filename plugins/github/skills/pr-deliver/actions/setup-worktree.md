# Action — Setup Worktree

Create the branch and an isolated worktree so implementation never touches
the main checkout. The first step of ticket delivery.

## Step 1 — Anchor to the main worktree

This may be invoked from inside another worktree, so resolve the main one
rather than trusting the current directory:

```bash
git fetch origin
MAIN_ROOT=$(git worktree list --porcelain | awk '/^worktree /{print $2; exit}')
REPO_NAME=$(basename "$MAIN_ROOT")
```

Not inside a git repo → use the path the user gives. Do not guess.

## Step 2 — Resolve the base branch

```bash
BASE=$(git -C "$MAIN_ROOT" rev-parse --verify --quiet origin/develop >/dev/null && echo develop || echo main)
git -C "$MAIN_ROOT" fetch origin "$BASE"
```

Check `vcs.base_branch_overrides` in `.devops-agents.yml` first — an override
wins over the probe. Never use `origin/HEAD` or `git remote show origin`:
both cache a value that is silently wrong in repos where the integration
branch is not the advertised default.

Fetching the base before branching is not optional. A stale local ref
produces a diff against history that has moved on.

## Step 3 — Compute the names

```bash
# vcs.user_slug from config wins — a derived slug is frequently wrong
USER_SLUG="<vcs.user_slug from config>"
if [ -z "$USER_SLUG" ]; then
  USER_SLUG=$(git config user.name | tr '[:upper:] ' '[:lower:]-' | tr -cd 'a-z0-9-')
  [ -z "$USER_SLUG" ] && USER_SLUG="${USER:-dev}"
fi
BRANCH="$USER_SLUG/feat/$TICKET-$SLUG"     # per vcs.branch_template
```

Sanity-check the derived value against the branches that already exist —
`git for-each-ref --format='%(refname:short)' refs/remotes/origin | head`. A
name derived from `user.name` looks plausible while disagreeing with every
branch in the repo.

`SLUG` is kebab-case, 3–5 words, from the ticket summary.

## Step 4 — Create the worktree

Default layout is **nested** under the repo (`vcs.worktree_layout`):

```bash
WORKTREE_PATH="$MAIN_ROOT/.worktree/$TICKET"

# keep the nested worktree out of the parent's status — local, uncommitted
EXCLUDE="$MAIN_ROOT/.git/info/exclude"
grep -qxF '.worktree/' "$EXCLUDE" 2>/dev/null || echo '.worktree/' >> "$EXCLUDE"

git -C "$MAIN_ROOT" worktree add "$WORKTREE_PATH" -b "$BRANCH" "origin/$BASE"
# branch already exists:
# git -C "$MAIN_ROOT" worktree add "$WORKTREE_PATH" "$BRANCH"
```

The `.git/info/exclude` line matters: without it the nested worktree shows up
as untracked in every subsequent `git status`, and eventually someone commits
it.

## Step 5 — Submodules, if the change needs one

Submodules are **not** populated in a new worktree, and a second worktree is
never the answer:

```bash
cd "$WORKTREE_PATH"
SUB=<submodule path>
git submodule update --init "$SUB"

SUB_BASE=<submodule base, per config or probe>
git -C "$SUB" fetch origin
git -C "$SUB" checkout "$SUB_BASE"
git -C "$SUB" pull origin "$SUB_BASE"      # pull, not just checkout
git -C "$SUB" checkout -b "$BRANCH"
```

Pulling matters: the pinned commit is often behind the submodule's base, and
branching from the pin means working against stale code.

An uninitialised submodule is an empty directory — everything written against
it looks valid locally and fails later with missing-schema errors.

Both sides are edited in **this** worktree. Local builds read the submodule
from the working tree, so both are testable together.

## Step 6 — Install dependencies

Inside the worktree, detect and run:

```bash
cd "$WORKTREE_PATH"
[ -f package.json ]     && npm install
[ -f go.mod ]           && go mod download
[ -f requirements.txt ] && pip install -r requirements.txt
[ -f pyproject.toml ]   && poetry install
[ -f Cargo.toml ]       && cargo build
[ -f Gemfile ]          && bundle install
```

## Report

```
Repo:      <REPO_NAME>   (main worktree: <MAIN_ROOT>)
Base:      <BASE>        (probed | override from config)
Branch:    <BRANCH>
Worktree:  <WORKTREE_PATH>      ← every later step runs from here
Submodule: <path> on <BRANCH> from <SUB_BASE>   (if any)
Deps:      <what was installed, or none detected>
```

The worktree path is the handoff payload. Every later agent works from it.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Creating the worktree from inside another worktree | Anchor to `MAIN_ROOT` first |
| Trusting the advertised default branch | Probe `origin/develop`; honour config overrides |
| Branching without fetching the base | Always fetch first |
| Forgetting the `.git/info/exclude` line | The nested worktree pollutes every `git status` |
| A second worktree for a submodule | Same worktree; branch inside the submodule |
| `checkout` without `pull` in the submodule | The pin is usually behind its base |
| Writing against an uninitialised submodule | `git submodule update --init` first |
| Installing dependencies in the main checkout | `cd` into the worktree first |
