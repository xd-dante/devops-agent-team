---
name: pr-list
description: 'List the open pull requests authored by the current GitHub user, across every repository, in one table. Use when asked for my open PRs, what is awaiting review, or a PR status roundup. Read-only; one query, no per-PR calls.'
allowed-tools: Bash(gh search prs:*), Bash(gh auth status:*)
context: fork
---

# PR List

Open PRs authored by the authenticated user — one query, read-only.

## Run

```bash
gh search prs --author @me --state open --sort updated --limit 100 \
  --json repository,number,title,isDraft,updatedAt,url \
  --template '{{range .}}{{.repository.nameWithOwner}}#{{.number}}{{"\t"}}{{if .isDraft}}draft{{else}}ready{{end}}{{"\t"}}{{timeago .updatedAt}}{{"\t"}}{{.title}}{{"\t"}}{{.url}}{{"\n"}}{{end}}'
```

Scope to one org or repo only when asked: add `--owner <org>` or `--repo <org>/<repo>`.

## Report

One table, newest update first, URL on every row:

```
| PR | State | Updated | Title | Link |
```

End with the count. Empty result → say `No open PRs`.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `gh pr list` | Lists one repo only — use `gh search prs` for all repos |
| Fetching CI or review state per PR | Slow, N calls — offer it as a follow-up, do not default to it |
| Truncating at the default 30 | Pass `--limit 100` |
| Auth error | Report `gh auth status` output; do not attempt login |
