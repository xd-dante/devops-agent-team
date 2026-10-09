---
name: pr-list
description: 'List the open pull requests authored by the current GitHub user, across every repository, in one table. Use when asked for my open PRs, what is awaiting review, or a PR status roundup. Read-only; one query, no per-PR calls.'
allowed-tools: Bash
context: fork
---

# PR List

Open PRs authored by the authenticated user — one query, read-only.

## Scope

Argument: `$ARGUMENTS`

| Argument | Scope |
|----------|-------|
| `<org>` (one or more) | Only those orgs/users — config ignored |
| `all` | Every org, config ignored |
| none | `vcs.orgs` from `.devops-agents.yml`; absent → every org |

Resolve the default scope first. Walk up from the current directory — not
`git rev-parse --show-toplevel`, which misses a workspace-level config:

```bash
d=$(pwd); for _ in 1 2 3 4; do [ -f "$d/.devops-agents.yml" ] && cfg="$d/.devops-agents.yml" && break; d=$(dirname "$d"); done
[ -n "$cfg" ] && awk '/^vcs:/{v=1;next} /^[^ #]/{v=0} v&&/^  orgs:/{o=1;next} o&&/^    - /{print $2;next} o{o=0}' "$cfg"
```

Prints one org per line, or nothing. Say which scope was used in the report.

## Run

One `--owner` per org (repeatable). No orgs → omit the flag.

```bash
gh search prs --author @me --state open --sort updated --limit 100 \
  --owner <org1> --owner <org2> \
  --json repository,number,title,isDraft,updatedAt,url \
  --template '{{range .}}{{.repository.nameWithOwner}}#{{.number}}{{"\t"}}{{if .isDraft}}draft{{else}}ready{{end}}{{"\t"}}{{timeago .updatedAt}}{{"\t"}}{{.title}}{{"\t"}}{{.url}}{{"\n"}}{{end}}'
```

Narrow to one repo only when asked: `--repo <org>/<repo>`.

## Report

One table, newest update first, URL on every row:

```
| PR | State | Updated | Title | Link |
```

Open with `Scope: <orgs | all> (<config | argument | default>)`. End with the count. Empty result → say `No open PRs`.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `gh pr list` | Lists one repo only — use `gh search prs` for all repos |
| Fetching CI or review state per PR | Slow, N calls — offer it as a follow-up, do not default to it |
| Truncating at the default 30 | Pass `--limit 100` |
| Reading `git rev-parse --show-toplevel` for the config | Walk up — workspace config sits above the repo |
| Auth error | Report `gh auth status` output; do not attempt login |
