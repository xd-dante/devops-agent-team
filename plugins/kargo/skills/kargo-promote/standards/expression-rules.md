# Expression Rules

Promotion steps use a small expression language inside `${{ }}`. These rules
are where real outages come from, not style preferences.

## Sibling step outputs inside a shared task

Scope is the thing that catches everyone:

| Context | Correct reference |
|---------|-------------------|
| A Stage's own promotion steps | `outputs['<alias>']` |
| Inside an embedded **promotion task** | **`task.outputs['<alias>']`** |

`outputs` alone is scoped to a Stage's own steps and is **undefined inside a
task**. It does not error — it evaluates to nil.

The failure mode is silent and total: a step gated on `outputs.commit != nil`
inside a task is always false, so the step is **always skipped**. This has
hidden a broken deployment step for months while every other theory was
investigated.

✅ Task-scoped:

```yaml
if: ${{ task.outputs['commit'] != nil }}
desiredRevision: ${{ task.outputs['commit'].commit }}
```

🚫 Always nil inside a task:

```yaml
if: ${{ outputs.commit != nil }}
```

> A double `.commit` can be correct rather than a typo: a step's alias and
> its single output field may share a name. Check both.

## No string formatting function

There is no `printf`/`sprintf`. Build strings by concatenating literal text
with `${{ }}` blocks:

```yaml
✅  message: chore(${{ vars.appName }}): bump to ${{ vars.tag }}
🚫  message: ${{ printf("bump %s", vars.tag) }}
```

## Quoting helpers belong in structured fields only

A quoting helper JSON-quotes its value. That is **required** in a values-update
`value:` field to force string typing (so `1.2.0` is not read as a number),
and **wrong** in plain text, where it leaves literal quote marks visible.

```yaml
✅  value:   ${{ quote(vars.tag) }}                       # structured field
✅  message: chore: bump to ${{ vars.tag }}               # plain text
🚫  message: chore: bump to ${{ quote(vars.tag) }}        # renders: bump to "1.2.0"
```

## Verify against the docs for your version

Scoping and the available function set are version-specific, and the failure
mode is a silently skipped step rather than an error. Confirm any unfamiliar
function or output reference in the docs for the installed version before
using it.
