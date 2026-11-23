# Field Rules

A project's create and edit screens reject or relocate fields in ways the
API only reveals by failing. `field_rules` records those quirks so the
create call is right the first time.

## Actions

| `action` | Effect on the create call |
|----------|---------------------------|
| `omit` | Drop the field entirely. Surface `user_note` to the caller |
| `top_level` | Place the field at the top level of the call, not under `additional_fields` |
| `require` / `rename` | Reserved. Apply literally if present |

Apply each rule **mechanically**. Do not interpret it, extend it, or "fix" a
field the rule did not name.

## Typical quirks

| Quirk | Rule | Failure without it |
|-------|------|--------------------|
| Reporter hidden on the screen scheme | `omit` on create and edit | The API rejects the call: the field cannot be set |
| Parent must be top-level | `top_level` | The parent is silently ignored, or the call is rejected |
| Legacy epic-link field superseded by parent | `omit` | Both set, or the deprecated one wins |

## Shape

```yaml
field_rules:
  - field: reporter
    action: omit
    on: [create, edit]
    reason: "<why the screen rejects it>"
    user_note: "<what the user should do instead>"
  - field: parent
    action: top_level
```

A new quirk found by a failing create belongs here, in the local profile —
offered to the user, never written silently.
