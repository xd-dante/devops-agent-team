# Action — Find Code

"Where is X?" — answered structurally where possible, textually where not.

## Step 1 — Pick the right instrument

| The question | Use |
|--------------|-----|
| A symbol by name or by meaning | graph: `semantic_search_nodes_tool` |
| Who calls this / what does it call | graph: `query_graph_tool` with `callers_of` / `callees_of` |
| What imports this file | graph: `imports_of` / `importers_of` |
| Which tests cover this | graph: `tests_for` |
| A literal string — error text, a flag, a URL | **grep.** Exact and instant |
| A config key, a Terraform variable, a chart value | **grep.** Not code structure |
| A file whose path you know | Just read it |

Reaching for a graph to find a literal string is slower and less exact than
grep. Reaching for grep to find callers gives you string matches and calls
them callers.

## Step 2 — Structural lookup

```
semantic_search_nodes_tool(query: "<symbol or description>")
query_graph_tool(pattern: "callers_of", target: "<symbol>")
```

`callers_of` returns one row per **call site** with the file and line, plus a
split showing how many are bound to an indexed node versus matched by bare
name. Read that split: bare-name matches are the graph's own grep fallback
and carry the same false-positive risk.

## Step 3 — Textual fallback

```bash
grep -rn --include='*.<ext>' '<symbol>' . | head -30
grep -rn '<symbol>' . -l | sed 's#/[^/]*$##' | sort | uniq -c | sort -rn | head
```

The second command shows *where* the matches cluster, which is usually the
actual question.

## Step 4 — Verify before relying on it

Open one hit and confirm it is what the tool claimed. A graph can be stale; a
grep can match a comment, a similarly-named symbol, or a vendored copy.

## Report

```
Looking for: <symbol>
Method:      graph @ <sha> | grep
Found:       <n> <resolved call sites | string matches> in <n> files
  <file:line>  <context>
Clusters in: <directory> (<n>)
Verified:    <the one you actually opened>
```

Never report a grep count as "callers". Say "matches", and say the method.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Graph for a literal string | grep is exact and faster |
| grep for callers, reported as callers | Say "matches"; grep cannot resolve calls |
| Ignoring the resolved/unresolved split | Bare-name rows are grep-quality |
| Not opening a single hit | Verify one before building on it |
| Trusting a stale index | Note the commit; refresh after a pull |
