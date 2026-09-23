# Action — Impact Radius

Before changing shared code: what else does this touch? Run it **before** the
edit, not after the review finds something.

## Step 1 — Radius

```
get_impact_radius_tool(target: "<symbol or file>")
```

Without a graph server:

```bash
grep -rn '<symbol>' . -l | sort -u                     # files referencing it
git log --oneline -20 -- <file>                        # how often it changes
git log --format='%an' -30 -- <file> | sort | uniq -c   # how many people touch it
```

Change frequency and author spread are decent proxies for risk when there is
no graph: a file many people edit often is one where a breaking change gets
noticed late.

## Step 2 — Tests

```
query_graph_tool(pattern: "tests_for", target: "<symbol>")
```

```bash
grep -rln '<symbol>' --include='*test*' --include='*spec*' .
```

**No tests covering a shared symbol is itself the finding.** Say it plainly
before the change goes in, not after.

## Step 3 — Does it cross a repo boundary

A graph sees one repo. If the symbol is part of a published interface — a
library chart helper, a Terraform module variable, an API response shape —
the real radius is larger than the graph shows.

Check the config's `dependency_chain` and `repos[].submodules`, and hand the
cross-repo ordering question to the orchestrator rather than guessing at it.

This is the most common way an impact assessment is confidently wrong: the
in-repo answer is complete and the change still breaks a consumer.

## Step 4 — Report before editing

```
Changing:     <symbol> in <file>
Referenced:   <n> call sites across <n> files
  <file:line>
Tests:        <n> cover it | NONE — flagged
Churn:        <n> commits, <n> distinct authors (last 30)
Cross-repo:   <published interface? which consumers> | in-repo only
Risk:         low | medium | high — <why>
Route:        <orchestrator, if the change crosses repos>
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Running it after the edit | The point is to run it before |
| Treating the in-repo radius as the whole radius | Check submodules and the dependency chain |
| Not mentioning absent tests | That is a finding, not a detail |
| Reading grep hit count as impact | It counts strings, including comments |
| Guessing the cross-repo order | Route it to the orchestrator |
