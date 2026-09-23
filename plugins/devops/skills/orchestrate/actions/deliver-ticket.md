# Action — Deliver Ticket

End-to-end delivery: ticket → worktree → implementation → PR. This is the
full lifecycle, and it replaces running the individual steps by hand.

## Step 1 — Ticket (`ticket-analyst`)

Look for a ticket id matching the configured pattern (default
`[A-Z]+-[0-9]+`).

| Found? | Do |
|--------|----|
| Yes | `HANDOFF → ticket-analyst` with `actions/read-ticket.md` |
| No | `HANDOFF → ticket-analyst` with `actions/create-ticket.md`, then read it back |

Require back: summary, description, acceptance criteria, environment, linked
issues, **and the content of every attachment**.

> Attachments are not optional. A title is a 2–5 word label; the actual
> requirement is regularly in the acceptance-criteria field, an attachment, or
> the last comment. Implementing from a title produces the wrong change.

**🛑 STOP** — present the restated scope and the repos you believe are
affected. Confirm before touching anything. Restating in different words is
the cheapest way to catch a misread ticket.

## Step 2 — Plan the repos

If the change spans repos, run `actions/cross-repo-change.md` **now** and fix
the merge order before any edit. Note submodule edges — they change how the
work is branched.

## Step 3 — Worktree (`delivery-engineer`)

`HANDOFF → delivery-engineer` with `actions/setup-worktree.md`. It anchors to the
main worktree, resolves the base branch by probing, fetches it, creates the
branch, creates the worktree, and installs dependencies.

Require back: the absolute worktree path and the branch name. Every later
handoff carries that path — the main checkout stays untouched.

## Step 4 — Implement (domain specialists)

Route each piece of work via `standards/routing-table.md`. Every brief
carries the worktree path as the working root.

| Work | Agent |
|------|-------|
| Terraform resources, variables, environment values | `terraform-engineer` |
| Chart templates and values | `helm-engineer` |
| GitOps Application wiring | `argocd-analyst` |
| Promotion pipeline config | `kargo-promoter` |
| Verifying live state before or after | `kubernetes-investigator`, `aws-investigator` |

Sequence anything with a dependency. Never two mutating agents in the same
files at once.

## Step 5 — Commit and PR (`delivery-engineer`)

`HANDOFF → delivery-engineer` with `actions/open-pull-request.md`. It handles
submodule PRs first, commits the parent without the submodule pointer, pushes,
opens or updates the PR, and checks CI.

Require back: every PR URL and the CI status.

## Step 6 — Record and report

`HANDOFF → ticket-analyst` with `actions/update-ticket.md` to link the PR onto
the ticket.

Then one report per `standards/report-format.md`, including every PR URL and
the merge order if one exists.

**Leave the worktree in place.** The branch is live until the PR merges, and
cleanup is the user's call.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Asking for a ticket id instead of creating one | No id → create the ticket, then proceed |
| Implementing before reading attachments | Step 1 requires them |
| Skipping the scope-confirmation stop | It is the cheapest check in the flow |
| Trusting the remote's advertised default branch | `delivery-engineer` probes it |
| A second worktree for a submodule | Same worktree; branch inside the submodule |
| Committing the submodule pointer with the parent | Submodule ships its own branch and PR |
| Removing the worktree at the end | Leave it; ask after merge |
| Doing a specialist's work yourself | Hand off; they carry the standards you would skip |
