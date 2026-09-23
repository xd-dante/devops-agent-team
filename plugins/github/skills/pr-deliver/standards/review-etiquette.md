# Review Etiquette

## Reply before resolve — always

```
make the change → reply saying what changed → resolve the thread
```

A silently resolved thread tells the reviewer nothing and makes them re-check
the diff themselves. Never resolve a thread without a reply, and never reply
"done" without saying what was done.

✅ Carries information:

```
Dropped the quoting helper here. It JSON-quotes, which is correct in the
structured value field to force string typing, but in a plain-text commit
message it leaves literal quote marks. Moved the component name into the
commit type instead.
```

🚫 Carries none:

```
Done ✅
Fixed.
Good catch, updated.
```

## Disagreeing

Disagreement is legitimate; silence is not. If a suggestion is wrong, post
the evidence in the thread and leave it **unresolved** until settled.

Quietly complying with a change you believe is wrong is the worst of the
options: the reviewer learns nothing and the codebase gets the worse version.

## Bot reviewers

Treat automated reviewers like any other reviewer — reply, then fix or
explain why not. They catch real bugs. They also raise points that do not
apply to a given codebase; say which, rather than resolving in silence.

## Keep the PR scoped

- Revert unrelated formatter churn
- Do not fold an unrelated fix into a ticket's PR — separate branch, separate
  PR
- If a drive-by fix is genuinely necessary, say so in the body

## Re-request review

After changes that alter the approach rather than polish it, re-request
review explicitly rather than assuming the reviewer is watching.
