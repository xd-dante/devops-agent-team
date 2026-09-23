# Safety Protocol

## The targeting rule

**Always `-target`. Never an untargeted plan or apply** without explicit
approval for that specific run.

```bash
terraform plan  -target=module.example -out=tfplan
terraform apply tfplan
```

Why this is absolute: shared state covers many components and environments,
drift exists in resources nobody asked you to touch, and a provider or secret
refresh can rewrite unrelated resources. An untargeted apply can ship
somebody else's half-finished work.

If the change cannot be expressed as a clean target set, **stop and say so**.
Report the addresses you would need and let the user decide. Never widen
silently.

Always report whether targeting was clean: did the plan show *only* the
intended resources?

Set `policy.terraform_targeted_only: false` in `.devops-agents.yml` to opt
out of this — a deliberate local choice, not a default.

## Plan review before apply

Read every line. Flag explicitly:

- resources destroyed or replaced that the task never mentioned
- secrets or passwords appearing in the diff
- `known after apply` on something that should be stable
- provider version changes riding along with a resource change

Known recurring plan noise in a given repo gets stated, not hidden.

## Prove the environment

```bash
aws sts get-caller-identity --query Account --output text   # or the cloud equivalent
terraform workspace select <env>
terraform workspace show                                     # verify — select can no-op
```

`terraform workspace select` on a missing workspace silently no-ops in some
versions, leaving the next command pointed at the wrong state. Verify.

Some repos fail `terraform validate` in the default workspace because
top-level expressions index a map by workspace name. Retry with
`TF_WORKSPACE=<env>` before concluding the code is broken.

Version matters: a state file can require a specific Terraform version, and
a mismatch surfaces as a state-lock or schema error rather than a clear
message. Check what the project pins.

## Ask first

- Any apply in a protected environment
- Any untargeted plan or apply
- `state rm` / `state mv` / `import`
- `-replace=` / taint
- Provider or Terraform version bumps
- Anything that destroys data

## Never

- `terraform destroy` — no environment, not even targeted
- `-auto-approve` on a plan the user has not seen
- Editing or pushing a state file by hand
- Committing state files, variable files carrying secrets, or `.terraform/`
