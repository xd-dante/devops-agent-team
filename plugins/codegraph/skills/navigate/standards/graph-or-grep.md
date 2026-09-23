# Graph or Grep

## The graph is optional

This skill assumes **no** particular MCP server. Where a code-graph server is
connected it is preferred; where it is not, every action has a grep/read
fallback that produces a worse answer rather than no answer.

```
graph available    → structural lookup, impact radius, callers/callees
graph unavailable  → grep + read, and say so in the report
```

**Never invent a tool name.** If the expected tool is absent from the
available list, fall back. An invented call fails the whole action for no
reason.

A server such as `code-review-graph` typically exposes tools along these
lines — check the actual list rather than assuming these:

| Purpose | Tool |
|---------|------|
| Build or refresh the index | `build_or_update_graph_tool` |
| Find a symbol by name or meaning | `semantic_search_nodes_tool` |
| Callers, callees, imports, tests | `query_graph_tool` |
| Blast radius of a change | `get_impact_radius_tool` |
| Token-efficient source for review | `get_review_context_tool` |
| High-level structure | `get_architecture_overview_tool`, `list_communities_tool`, `list_flows_tool` |

## When the graph is worth it

| Situation | Why |
|-----------|-----|
| "Where is X used?" across a large repo | One structural query beats a dozen greps, and it resolves call sites rather than string matches |
| About to change a shared function or type | Impact radius before editing is the whole point |
| Reading unfamiliar code | Architecture overview orients faster than opening files at random |
| Checking test coverage of a symbol | `tests_for` is exact; a grep for the name is not |

## When grep is the right tool anyway

| Situation | Why |
|-----------|-----|
| Config, YAML, Markdown, Terraform | Graphs index code structure; these are mostly not that |
| A literal string — an error message, a flag, a URL | grep is exact and instant |
| A file you already know the path of | Just read it |
| The repo is small | Indexing costs more than it saves |

Reaching for the graph on a Terraform or chart repo is a common
mis-application: the useful relationships there are module calls and value
files, not a call graph.

## Staleness

An index reflects the commit it was built at. After checking out a branch or
pulling, **refresh it or say it may be stale** — a confident answer from a
stale graph is worse than a slow grep.

Verify anything the graph asserts about a specific file or symbol before
acting on it, the same as a memory entry.

## Honesty in the report

State which path produced the answer:

```
✅  Found via graph (indexed at <sha>): 14 callers across 6 files
✅  Graph unavailable — grep found 14 matches; call sites not resolved,
    so some may be comments or unrelated names
🚫  "14 callers" with no indication of how that was established
```

The difference matters: grep counts string occurrences, the graph counts
resolved call sites. Presenting one as the other overstates the confidence.
