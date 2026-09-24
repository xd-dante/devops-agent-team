# Companion Tooling

None of this is required — every agent works without it. This is what the
agents integrate with, and what makes them noticeably better.

Listed because a working setup is more than the agents: the first three
change behaviour, the rest change quality.

## Integrated

### A code-graph MCP server

`codegraph-navigator` prefers structural lookup and **falls back to grep when
no server is connected**, saying which it used. With a server it resolves call
sites; without one it counts string matches — a real difference when you are
asking "what will this break".

[`code-review-graph`](https://github.com/sriniously/code-review-graph) is the
one the plugin's tool names are written against:
`build_or_update_graph_tool`, `semantic_search_nodes_tool`,
`query_graph_tool`, `get_impact_radius_tool`.

Its impact-radius output includes `unresolved_call_sites` — call sites that
name a changed symbol but were never bound to it. That is the number that
stops an empty radius being mistaken for proof, and it is why a graph is
worth having for shared-code changes.

Any MCP server exposing equivalent tools works; the agent checks the
available list and never calls a tool that is not there.

## Recommended

### rtk — command output compression

[`rtk-ai/rtk`](https://github.com/rtk-ai/rtk) (MIT, single Rust binary) sits
between the shell and the model and compresses command output.

This matters more here than for most toolkits, because these agents are
**command-heavy by design** — `git diff`, `terraform plan`, `kubectl
describe`, `helm template`, `gh run view --log-failed`. Those are exactly the
outputs that are mostly noise by volume.

```bash
brew install rtk        # or: cargo install --git https://github.com/rtk-ai/rtk
rtk init -g             # installs the Bash-rewrite hook, then restart
```

Two things worth knowing before you enable the hook:

- It rewrites Bash commands transparently (`git status` → `rtk git status`).
  **If the binary later goes missing, every rewritten command fails** with
  `command not found: rtk` — including `git fetch`, which fails *quietly
  enough to look like "no changes"*. Keep `rtk --version` in your
  troubleshooting reflexes.
- There is a **name collision**: `reachingforthejack/rtk` is a different
  project (Rust Type Kit). `rtk gain` working is the quick check that you have
  the right one.

### superpowers — process skills

Brainstorming, systematic debugging, test-driven development, plan writing.
Complements rather than overlaps: those shape *how* you approach a problem,
while these agents carry *domain* knowledge.

Available in the official Claude Code plugin marketplace.

## Optional, quality-of-life

| Plugin | What it adds |
|--------|--------------|
| `code-review` | A review pass over a diff, independent of the delivery flow |
| `code-simplifier` | Post-change cleanup for clarity and consistency |
| `security-guidance` | Automated security review of changes as you make them |
| `humanizer` | Strips the tells out of generated prose — useful for PR bodies and reports that people actually read |
| `session-report` | A summary of what a long session actually did |

## On memory — two different jobs

This repo ships a [`memory`](../plugins/memory) plugin. It is deliberately
**not** a code-indexing tool, and does not replace one:

| | Holds | Source |
|---|---|---|
| `memory` plugin (here) | Your preferences, conventions, environment facts, decisions and their reasoning | What you told it, or a correction it offered to save |
| A code-memory / indexing tool | Structure derived from the codebase — symbols, calls, architecture | Parsed from source |

They answer different questions. "Which branch do PRs target here?" is the
first. "Who calls this function?" is the second — and that is what
`codegraph-navigator` is for.

Running both is reasonable. Just do not expect either to cover the other, and
keep site-specific facts in the local, gitignored memory directory rather
than in an indexed artifact.

## Registering a marketplace

For a local checkout — which is also how you develop against this repo:

```json
{
  "extraKnownMarketplaces": {
    "devops-agent-team": {
      "source": { "source": "directory", "path": "/path/to/devops-agent-team" },
      "autoUpdate": true
    }
  }
}
```

A directory marketplace serves **whatever branch is checked out**. Switching
branches changes the plugin set under you, and a plugin enabled in
`settings.json` whose directory is absent on the current branch fails to
load. Worth knowing before you go hunting for a config problem.
