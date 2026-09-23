# Action — Module Change

Add or change a variable, resource, or output.

## Step 1 — Find the owning layer

Change the module only if the module is what is wrong:

| Concern | Change |
|---------|--------|
| Which component gets what | the module **call** and the environment's variable file |
| What the resource looks like for everyone | the module |
| A deployment-tool value | not Terraform — hand back to the orchestrator |

## Step 2 — Type the variable

Shape and defaults in the type, per `standards/hcl-style.md`:

```hcl
variable "integration" {
  type = object({
    project = optional(string, "default")
    stage   = optional(string, "")
  })
  default = {}
}
```

The resource body then reads flat — no `try()`, no defaulting ternary.

## Step 3 — Keep parallel variants in sync

Where a module defines the same resource in two shapes — a single-item and a
multi-item variant, for instance — they drift silently, and the drift only
surfaces for whichever consumers use the neglected one. **Every change lands
in both.** Diff them against each other before committing.

## Step 4 — Submodule mechanics

```bash
git submodule update --init modules/<name>
cd modules/<name>
git fetch origin && git checkout <base> && git pull
git checkout -b <user>/<type>/<ticket>-<slug>
```

Both sides are edited in the **same worktree**. The parent reads the
submodule from the working tree, so local testing works before anything is
pushed. On delivery the submodule gets its own branch and PR; the parent
commit **excludes** the pointer.

## Step 5 — Validate both sides

```bash
terraform init                  # NOT -upgrade
terraform validate
terraform fmt -recursive        # revert unrelated pre-existing drift
```

`-upgrade` re-resolves providers and modules and rewrites the lock file — a
version bump, which `standards/safety-protocol.md` classes as ask-first. It
does not belong in a routine module change.

Then a **targeted plan against a real consumer**, so the variable shape is
exercised rather than merely parsed.

## Step 6 — Document where it belongs

Module README: what the variable is for, its shape, an example. Commit body
or PR: why. The `.tf` file: at most a 1–2 line block-purpose comment.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Editing the module when the call was wrong | Change the call and the variable file |
| Updating one of two parallel variants | Both, always |
| Writing against an uninitialised submodule | Initialise first |
| Committing the pointer with the parent | Separate branch and PR |
| `validate` as the only check | Targeted plan against a real consumer |
| Explaining the change in a code comment | Commit body, PR, or README |
