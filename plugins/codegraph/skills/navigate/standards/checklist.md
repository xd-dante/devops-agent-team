# Navigation Checklist

## Before querying
- [ ] Graph server availability checked — tool present, or fallback chosen
- [ ] Working root is the worktree being changed, not the main checkout
- [ ] Index freshness considered after a checkout or pull
- [ ] Repo type sanity-checked — a call graph adds little on config-only repos

## Querying
- [ ] Structural question asked structurally; literal strings left to grep
- [ ] Impact radius run **before** editing shared code, not after
- [ ] Results spot-checked against the real file before being relied on

## Reporting
- [ ] The method is stated — graph (with the indexed commit) or grep
- [ ] Resolved call sites distinguished from string matches
- [ ] Staleness flagged where the index predates the working tree
- [ ] Findings that belong to another domain routed, not investigated here
