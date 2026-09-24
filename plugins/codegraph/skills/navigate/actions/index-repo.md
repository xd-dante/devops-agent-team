# Action — Index Repo

Build or refresh the structural index for a checkout, so later lookups are
structural rather than textual.

## Step 1 — Is it worth indexing

| Repo shape | Verdict |
|------------|---------|
| Application code, more than a few thousand lines | Index it |
| Config-only — Terraform, charts, manifests, docs | **Skip.** The useful relationships are module calls and value files, not a call graph |
| Small enough to read | Skip; grep and read are faster |

Say when you skip and why. Indexing a chart repo produces an index nobody
benefits from and takes the time anyway.

## Step 2 — Index the worktree, not the main checkout

```bash
WORKTREE=$(git rev-parse --show-toplevel)
echo "indexing: $WORKTREE"
```

Ticket work happens in `<repo>/.worktree/<TICKET>`. Indexing the main
checkout answers questions about the wrong code — subtly, since most of it
is identical.

## Step 3 — Build

Where a graph server is connected:

```
build_or_update_graph_tool(repo_path: "<WORKTREE>")
```

Incremental where the server supports it, so a refresh after a pull is cheap.
No server → skip, note it once, and let later actions fall back to grep.

## Step 4 — Record what it was built from

```bash
git -C "$WORKTREE" rev-parse --short HEAD
git -C "$WORKTREE" status --porcelain | wc -l      # uncommitted files not in the index
```

Both matter. The index reflects a commit; uncommitted edits are invisible to
it, which is exactly the state ticket work is usually in.

## Report

```
Indexed:     <repo> @ <sha>   (<worktree path>)
Uncommitted: <n> files — not reflected in the index
Server:      <available | absent, later lookups will use grep>
Skipped:     <reason, if skipped>
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Indexing the main checkout during worktree work | Index the worktree |
| Indexing a Terraform or chart repo | Skip it; grep serves better there |
| Silently skipping when no server is present | Say so once, so later answers are read correctly |
| Not recording the commit | A stale index gives confident wrong answers |
| Treating uncommitted work as indexed | It is not; flag the count |
