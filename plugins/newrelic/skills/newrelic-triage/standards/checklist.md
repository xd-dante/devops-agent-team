# Triage Checklist

## Before querying
- [ ] Region resolved explicitly (`US`/`EU`) — never guessed
- [ ] User key present in the environment
- [ ] Account list returned at least one account
- [ ] Window stated, and comparison window chosen (same hour, week over week)

## Querying
- [ ] Read-only — no mutation ran
- [ ] Every response checked for a GraphQL `errors` array
- [ ] Paginated to empty `nextCursor` where the query supports it
- [ ] Queries scoped with `SINCE` rather than scanning wide

## Reasoning
- [ ] Absolute thresholds paired with a baseline comparison
- [ ] Known noise suppressed, and the suppression **counted** in the report
- [ ] Recurrence noted where an issue has appeared before
- [ ] Symptom separated from cause — and the cause routed, not guessed at

## Reporting
- [ ] Verdict first, exceptions only
- [ ] Every finding carries a number, not an adjective
- [ ] "Could not verify" used where a check failed — **never** "all clear"
- [ ] Failed checks listed explicitly
- [ ] Each 🔴/🟠 has an owning agent named
- [ ] No raw log payloads, no key material
