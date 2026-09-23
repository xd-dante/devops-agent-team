# Branch and Commit

## Base branch — probe, never trust the advertised default

```bash
git fetch origin
BASE=$(git rev-parse --verify --quiet origin/develop >/dev/null && echo develop || echo main)
```

Deliberately **not** `origin/HEAD` or `git remote show origin`. Both report a
cached value that can be stale or plain wrong where the integration branch is
not the advertised default — and the failure is silent: the PR opens against
the wrong branch and nobody notices until merge.

Where the probe is still wrong, list the repo under
`vcs.base_branch_overrides` in `.devops-agents.yml`.

**Always fetch the base before branching.** Branching from a stale local ref
produces a diff against history that moved on.

## Branches

Default template: `{user}/{type}/{ticket}-{slug}` — configurable via
`vcs.branch_template`.

```
✅  alex/feat/PROJ-412-runner-image-pin
✅  alex/fix/PROJ-418-probe-timeout
🚫  my-branch
🚫  Feature_Auth
🚫  fix-stuff
```

- Names describe the **actual change**, not the ticket title verbatim
- **Never reuse a branch whose PR has merged** — start fresh from the pulled
  base. A reused branch diffs against stale history
- Base branches are protected: always a PR, never a direct push
- Never force-push a base branch

## When the base has moved

Do not cherry-pick and do not force-push to reconcile:

```bash
git checkout "$BASE" && git pull --ff-only
git checkout -b <user>/<type>/<ticket>-<slug>
# redo the change directly on the fresh branch
```

Cherry-picking is for salvaging work you cannot easily reproduce — not for
routine divergence.

## Identity — check it before the first commit

```bash
git config user.name && git config user.email
```

An address that is not an address (a name in the `user.email` field) produces
commits the forge cannot attribute, and they have to be rewritten. Where
`vcs.commit_author` is configured, or the ambient identity is unusable, pass it
per commit rather than editing someone's global config:

```bash
git -c user.name="<name>" -c user.email="<email>" commit ...
```

Then verify: `git log --format='%an <%ae>' -1`.

Check the **effective** value from the directory you are committing in — a repo
can carry a local override that the global config does not show.

## Commits

`<type>: <subject>` — imperative, ≤72 chars. Types: `feat`, `fix`, `docs`,
`refactor`, `chore`, `test`, `ci`.

**Scopeless by default.** `vcs.commit_style: scoped` opts into
`<type>(<scope>): <subject>` where a project wants it. Some commit-lint
configurations reject particular scope casing, so scopeless is the safe
default.

```
✅  feat: PROJ-412 pin runner image to a released tag
✅  fix: correct null check in the user lookup
🚫  Added the pin
🚫  fixed it.
```

- Never `-s` / `--signoff` — it writes a personal email into the trailer
- Review the staged diff before committing
- Revert unrelated formatting churn; a repo-wide formatter run buries the
  actual change
- **No AI or assistant attribution** anywhere — not in commit messages, not
  in trailers, not in PR bodies

## Hooks

If a commit fails a hook, fix the cause and make a **new** commit. Never
amend something already pushed, and never skip the hook silently.

Where a repo's hooks generate files (docs regeneration, version bumping,
lockfiles), those generated changes pollute the diff. Committing with
`--no-verify` is legitimate there — say so in the report, and keep the
generated files out of the commit.

## Never commit

Secrets, tokens, keys, `.env`, kubeconfigs, Terraform state, or a submodule
pointer alongside a parent change.
