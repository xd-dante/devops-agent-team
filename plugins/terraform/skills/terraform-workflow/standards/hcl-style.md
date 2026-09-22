# HCL Style

## Push shape into the variable, not the resource

Resource bodies stay flat. Defaults, optionality and shape belong in the
variable type.

✅ The type carries the contract:

```hcl
variable "services" {
  type = map(object({
    enabled  = optional(bool, true)
    replicas = optional(number, 2)
    revision = optional(string, "HEAD")
  }))
}

resource "example_service" "this" {
  for_each = { for k, v in var.services : k => v if v.enabled }
  revision = each.value.revision
}
```

🚫 Defaulting logic smeared through the resource:

```hcl
revision = try(each.value.revision, "HEAD") != "" ? try(each.value.revision, "HEAD") : "HEAD"
```

## Banned inside resource bodies

- `try()` — if a value can be absent, type it `optional(..., default)`
- `flatten()` and nested `merge()` chains — restructure the input instead
- ternaries used for defaulting
- `lookup(var.x, k, "fallback")` for a default the type could express

Conditionals for genuine behaviour branching (`count`, `for_each` filters)
are fine. Conditionals papering over an untyped variable are not.

## Comments

**One to two lines maximum**, describing the *purpose of the block*.

✅ `# Per-service network policy; attached to the service's own interface.`

🚫 Narrating a change, recapping a discussion, or citing a ticket:

```hcl
# TICKET-123: moved here from the module because it was creating one per
# service and we decided ownership belongs in the root stack. See the PR
# discussion for why the previous approach broke.
```

Rationale, ticket references and trade-offs go in the commit body, the PR, or
the module README. Never in the `.tf` file — comments there rot fast and
duplicate the PR.

## Formatting

`terraform fmt` before every commit. Note that `fmt -recursive` picks up
**pre-existing drift** in unrelated files — revert those to keep the change
reviewable.

## Naming

Resources named for what they are, not what they are for:
`example_service.api`, not `example_service.api_service_for_frontend`.
Variables `snake_case`; object attributes match the upstream API's naming
where one exists.
