# Body Format

## Description — exactly one paragraph

Open with one sentence of persona or situation: who is affected, and when.
Then what changes and why. Describe the problem and the outcome; leave the
"how" to the engineer who picks it up. No headings inside it.

> "Operators reconciling partner settlements each morning cross-check three
> exports by hand, which is slow and error-prone; the nightly job should
> produce one reconciled file so the manual check is no longer needed."

## Acceptance criteria

Only when the resolved type has `acceptance_criteria: true`. Never on an Epic
— its scope is tracked through its children.

| Rule | Why |
|------|-----|
| `The <subject> shall <observable behaviour> <concrete threshold>.` | Forces a pass/fail check |
| One assertion per line — an "and" means two lines | A half-met line cannot be ticked |
| Weight suffix `(P1–P10)`, 10 = must-have | Scope can be cut under pressure without renegotiating |
| 3–7 lines | More usually means the ticket should split |

```
🚫  Reconciliation should be fast and reliable.
✅  The nightly reconciliation job shall complete in under 5 minutes for a standard batch. (P8)
✅  The reconciliation output shall flag any mismatch above 0.01 for manual review. (P10)
```

## Assembled body

Sent with `contentFormat: markdown`:

```markdown
## Context
<one paragraph>

## Acceptance Criteria
- [ ] The <subject> shall <behaviour> <threshold>. (P10)
- [ ] The <subject> shall <behaviour> <threshold>. (P7)

## Open Questions
- <only if any remain>
```

Omit `## Acceptance Criteria` when the type does not take them, and
`## Open Questions` when there are none. Criteria live **in the body**, not
in the project's acceptance-criteria custom field — do not "fix" them into it.
