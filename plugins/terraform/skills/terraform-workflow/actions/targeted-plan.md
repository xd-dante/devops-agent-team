# Action — Targeted Plan

Produce a plan showing **only** the resources the change should touch.

## Step 1 — Prove the environment

```bash
export AWS_PROFILE=<profile for this environment>     # or the cloud equivalent
aws sts get-caller-identity --query Account --output text

terraform workspace select <env>
terraform workspace show        # verify — select can silently no-op
```

**🛑 STOP** if the target is a protected environment and the user has not
said so.

## Step 2 — Init and validate

```bash
terraform init
terraform validate
```

`validate` failing in the default workspace usually means top-level
expressions index a map by workspace name — retry with
`TF_WORKSPACE=<env> terraform validate` before concluding the code is broken.

## Step 3 — Resolve real addresses

```bash
terraform state list | grep -i <component>
```

Write them down. One `-target` per address:

```bash
terraform plan -target=module.example -target=example_resource.this -out=tfplan
```

**Never** run an untargeted plan as a shortcut to "see everything". If the
change needs a target set you cannot express cleanly, stop and report the
addresses — the user decides whether to widen.

## Step 4 — Read the plan

Line by line. Flag out loud: unexpected destroys or replaces, secrets in the
diff, `known after apply` on values that should be stable, provider version
churn riding along.

## Report

```
Repo / workspace: <repo> / <env>     Identity: <account or profile>
Targets:          <addresses>
Targeting clean:  yes | no — <what else appeared and why>
Plan summary:     <n> to add, <n> to change, <n> to destroy
Flagged:          <unexpected replaces, secret noise, version churn>
Plan file:        tfplan
```

Whether targeting was clean is the point of this action. Say it.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Untargeted plan "just to look" | Targeted only; widen on approval |
| Assuming `workspace select` worked | `terraform workspace show` after |
| Wrong cloud identity | Prove it before planning |
| Guessing resource addresses | `terraform state list` and match |
| Skimming the plan | The destroy you miss is the one that matters |
