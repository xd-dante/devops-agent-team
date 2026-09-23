# Action — State Operations

`import`, `state rm`, `state mv`, `-replace`. Every one is **ask-first**, and
every one can lose infrastructure if the address is wrong.

## Gate — all required

- [ ] The user asked for this operation, or approved it after you proposed it
- [ ] Workspace confirmed with `terraform workspace show`
- [ ] Cloud identity confirmed
- [ ] The exact address checked against `terraform state list` **in the
      direction the operation needs**:

| Operation | The address must be |
|-----------|---------------------|
| `import` | **absent** from state, and present in the configuration |
| `state rm` / `state mv` / `-replace` | **present** in state |

An `import` whose address is already in state is a different problem — stop
and report it rather than forcing it.

## Inspect first

```bash
terraform state list | grep -i <thing>
terraform state show <address>
```

## Import

```bash
terraform import <address> <cloud-id>
terraform plan -target=<address>      # expect: no changes
```

A non-empty plan right after an import means the configuration does not match
reality. **Fix the configuration to match the resource** — never apply your
way out of a bad import.

## state rm

Removes Terraform's knowledge; the resource survives. Legitimate when a
resource's API deletion is blocked, or when moving ownership to another
stack.

Say explicitly in the report that the resource **still exists and is now
unmanaged**. An unmanaged resource nobody records is how orphans happen.

## state mv

```bash
terraform state mv <old> <new>
terraform plan -target=<new>          # expect: no changes
```

## -replace

```bash
terraform plan -replace=<address> -out=tfplan
```

Read the plan for what recreation destroys — attached volumes, DNS records,
addresses. Confirm before applying.

## Never

- Edit a state file by hand, or `state push` a modified one
- `terraform destroy`, targeted or not
- Run an operation whose address you have not verified

## Report

```
Operation:   import | state rm | state mv | -replace
Address:     <address>       Cloud id: <id>
Workspace:   <env>           Identity: <account or profile>
Post-check:  terraform plan -target=<address> → clean | <diff>
Consequence: <e.g. resource now unmanaged but still live>
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Applying to "fix" a post-import diff | Correct the configuration |
| `state rm` without flagging the orphan | State it in the report |
| Assuming `workspace select` succeeded | `terraform workspace show` |
| Guessing the address | `terraform state list` and match exactly |
| Running any of these unprompted | Ask first, every time |
