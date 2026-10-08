# Security Review Checklist

## Before reading
- [ ] Identity proved for every account in scope
- [ ] Regions listed; blocked and unsubscribed ones recorded
- [ ] Administrator / member topology established

## Reading
- [ ] Read-only verbs only (see the forbidden table)
- [ ] Findings pulled once, with pull time recorded
- [ ] Counts split by account
- [ ] Generator of operations items identified, with its value and history
- [ ] Items joined to findings within the same account
- [ ] Staleness proved on a sample spread across the list

## Reasoning
- [ ] Findings grouped by fix, not listed one by one
- [ ] Owner found by checking every infrastructure repo on its base branch
- [ ] Drift called out where code and live disagree
- [ ] Dependencies checked before any port or rule removal is recommended
- [ ] Runtime-threat findings carry a confirming check, not a verdict

## Reporting
- [ ] Report file written in the standard shape
- [ ] Prepared lists named, with row counts and pull time
- [ ] Every fix notes the resolve step that follows it
- [ ] "Not checked" section filled in
- [ ] Explicit statement that nothing was mutated
