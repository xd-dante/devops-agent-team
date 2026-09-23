# Terraform Checklist

## Before writing
- [ ] Correct repo and module identified
- [ ] Base branch probed, not assumed
- [ ] Submodules initialised if the change touches a module call
- [ ] Value classified: does it belong in Terraform at all, or in a chart?

## Writing
- [ ] Shape and defaults in the variable type, not the resource
- [ ] No `try()`, `flatten()`, or defaulting ternaries in resource bodies
- [ ] Comments 1–2 lines, block purpose only
- [ ] `terraform fmt` clean; unrelated pre-existing drift reverted

## Validating
- [ ] `terraform init` in the right directory
- [ ] `terraform validate` passes (with `TF_WORKSPACE=<env>` if needed)
- [ ] Workspace confirmed with `terraform workspace show` after select
- [ ] Cloud identity proved for the target environment

## Planning
- [ ] Plan is **targeted**
- [ ] Targeting is clean — only intended resources appear
- [ ] Plan read line by line; unexpected destroys and replaces flagged
- [ ] Plan saved to a file

## Applying
- [ ] User approved this run explicitly
- [ ] Protected environments confirmed separately
- [ ] Applied from the saved plan file
- [ ] Post-apply re-plan clean, and the downstream effect verified

## Committing
- [ ] Conventional commit, scopeless unless configured otherwise
- [ ] No state files, secret-bearing variable files, or `.terraform/`
- [ ] Rationale in the commit body or PR, not in the `.tf` files
