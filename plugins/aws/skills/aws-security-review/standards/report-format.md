# Report Format — Security Review

One file per run, `security-findings-<date>.md`, readable top-down by someone
who was not in the session. Tables over prose. Every number carries its
account and its pull time.

```
# Security findings review — <date>
Accounts: <id (role)>…   Regions: <in scope>   Blocked: <…>   Pulled: <time>
Mode: read-only — nothing mutated

## 1. Headline
3–5 lines: open items, % stale, the generator, the real signal (crit / high),
the single highest-value change.

## 2. Topology
Administrator / members / aggregator. Standards: live vs code (drift).

## 3. Operations backlog
| Account | Open | Stale | Live-backed | Sev 1 | 2 | 3 | 4 | none |
Generator: <setting / rule, value, since, in code?>
Inflow: <per day, recent month>
| Bucket (title) | Items | Distinct resources | Stale % |

## 4. Findings
| Account | Crit | High | Med | Low | Info |
| Product | Count |
| Control | Title | Severity | Findings | Distinct resources |

## 5. Quick wins — ranked
| # | Fix | Clears | Resources | Owner (repo:file / manual) | Effort | Risk | Prerequisite |

## 6. Suppress instead
| Item | Reason |

## 7. Needs triage
| Finding | Evidence | Hypothesis | Confirming check |

## 8. Prepared lists
| File | Rows | Built from | Pulled at | Use |

## 9. Not checked
Every skipped check, every denial verbatim, every region blocked.
```

## Rules

- **Evidence or nothing.** A row with no resource id or command behind it
  does not go in.
- **Hypotheses are labelled**, with the check that would confirm them.
- **Section 9 is never empty by omission.** If everything ran, say so.
- **No secret values, and no real identifiers in shared copies.** If the
  report leaves the team, keep account ids and resource ids only where the
  audience is entitled to them.
