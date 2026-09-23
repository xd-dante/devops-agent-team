# Action — Profile Repo

Produce a short orientation document for a repo you have not worked in
before: what it is, how it is organised, and the conventions that are not
obvious from the file tree.

Run once per repo, then reuse. This is the step that stops every new ticket
starting with the same twenty minutes of exploration.

## Step 1 — Is there one already

Check the memory directory (`memory` plugin) for an existing profile entry
before generating a new one. If it exists, **load it instead** — and only
regenerate if the repo has changed shape.

## Step 2 — Gather structure

With a graph server:

```
get_architecture_overview_tool(repo_path: "<WORKTREE>")
list_communities_tool(repo_path: "<WORKTREE>")
list_flows_tool(repo_path: "<WORKTREE>")
```

Without one, derive the same picture cheaply:

```bash
# what kind of repo is this
ls; cat README* 2>/dev/null | head -40
ls *.tf Chart.yaml package.json go.mod pyproject.toml pom.xml 2>/dev/null

# shape
git ls-files | awk -F/ '{print $1}' | sort | uniq -c | sort -rn | head -15
git ls-files | sed -n 's/.*\.\([a-z0-9]*\)$/\1/p' | sort | uniq -c | sort -rn | head -8

# conventions worth knowing
ls .github/workflows/ 2>/dev/null
cat .gitmodules 2>/dev/null
git log --oneline -15
```

## Step 3 — Capture what is not obvious

The value is in the parts a file listing does not tell you:

- **Base branch**, probed — not assumed
- **Submodule edges**, and which repo each points at
- **What CI enforces** — commit format, lint, generated files
- **Hooks that regenerate files**, which change how you commit here
- **Where the real entry points are**, versus scaffolding
- **Conventions the code follows** that a reviewer will hold you to

## Step 4 — Write it as a memory entry

Hand to the `memory` plugin's remember flow, `type: environment`,
`scope: project`, so it is found on the next ticket without regenerating:

```markdown
# <repo> — orientation

Purpose:      <one line>
Base branch:  <probed>
Tech:         <languages, frameworks>
Layout:       <the 4–6 directories that matter and what lives in each>
Submodules:   <path → repo → base>
CI enforces:  <commit format, lint, generated files>
Gotchas:      <the things that cost time the first time>
Entry points: <where to start reading>
```

Keep it short. A profile nobody reads is worth nothing, and a long one gets
skipped.

## Report

```
Profile: <repo> — <generated | loaded from memory>
Source:  <graph overview | file-tree derivation>
Saved:   <memory scope and entry name>
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Regenerating a profile that already exists | Check memory first |
| A profile that restates the file tree | Capture what the tree does not show |
| Assuming the base branch | Probe it |
| Writing pages | Short enough to read on every ticket |
| Leaving it in the session | Save it, or the next ticket pays again |
