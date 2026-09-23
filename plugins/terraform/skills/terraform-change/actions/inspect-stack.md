# Action — Inspect Stack

Orient before changing anything. Cheap, read-only, prevents most of the
expensive mistakes.

## Steps

```bash
basename "$(git rev-parse --show-toplevel)"
git rev-parse --verify --quiet origin/develop >/dev/null && echo develop || echo main
ls *.tf modules/ 2>/dev/null
ls *.tfvars tfvars/ environments/ 2>/dev/null
terraform workspace list
terraform workspace show
git submodule status
```

## Read the module call, not the module

To answer "where is this value set for X in environment Y", read in order:

1. the root module call for that component
2. the environment's variable file
3. the module's `variables.tf` — defaults and `optional()` shape
4. only then the module's resources

Most "where does this come from" questions are answered at step 2 or 3.
Starting at the resources wastes the most tokens for the least information.

## Submodules

An empty submodule directory means the variable schema is missing. Everything
written against it looks valid locally and fails later with unknown-attribute
errors.

```bash
git submodule update --init <path>
```

## Is it even Terraform

If the value might be a chart value rather than an infrastructure one,
classify it before going further — static chart values are read directly by
the deployment tool and bypass Terraform entirely.

## Report

```
Repo:        <name>  (base: <branch>)
Workspaces:  <list>  (current: <name>)
Target:      <module / resource addresses in scope>
Value path:  <static chart value | computed in Terraform>
Submodules:  <initialised? which>
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Reading module internals first | Module call → variables file → variables.tf → resources |
| Assuming the base branch | Probe it |
| Writing against an uninitialised submodule | `submodule update --init` first |
| Assuming a value lives in Terraform | Classify static vs computed first |
