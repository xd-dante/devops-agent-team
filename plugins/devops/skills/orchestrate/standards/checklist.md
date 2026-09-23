# Orchestration Checklist

## Routing
- [ ] Domain resolved via `routing-table.md`, not intuition
- [ ] Disambiguation rules applied where two domains overlap
- [ ] Required plugin confirmed available, or the gap reported
- [ ] Environment established explicitly

## Briefing
- [ ] Each brief self-contained — no "see above"
- [ ] Absolute paths, environment, cloud profile, ticket id included
- [ ] Required output shape named
- [ ] Scope boundary stated

## Execution
- [ ] Parallel only where work is genuinely independent
- [ ] No two mutating agents at the same target at once
- [ ] Cross-repo work followed dependency order, not convenience order
- [ ] No mutation in a protected environment without explicit confirmation

## Verification
- [ ] Every finding has evidence
- [ ] One claim per specialist spot-checked against the real source
- [ ] No specialist exceeded its own boundaries
- [ ] Conflicts surfaced, not averaged

## Reporting
- [ ] Single report in `report-format.md` shape
- [ ] "Not done" filled in where anything was blocked or skipped
- [ ] Every PR referenced with its URL, plus an end-of-reply recap
- [ ] Clear statement of whether anything was mutated
