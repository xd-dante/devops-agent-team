# newrelic

Daily observability triage: is anything actually wrong, and what needs a human.

## The MCP server is not bundled — register it yourself

This plugin deliberately ships **no `.mcp.json`**. New Relic's documented
Claude Code setup registers the server in `~/.claude.json`, at user scope, and
their docs do not use `.mcp.json` at all.

A plugin-bundled server is also injected at a dynamic scope with no persisted
config entry, and OAuth credentials do not survive a reconnect there: login
succeeds, then the next connection is rejected. Registering it yourself avoids
that entirely.

Follow New Relic's own instructions:

```bash
# pick the endpoint for YOUR region (see below)
claude mcp add --scope user --transport http newrelic https://mcp.newrelic.com/mcp/
claude mcp login newrelic
```

`--scope user` matters: without it the server is written to project-local
config and is invisible from any other directory, so `claude mcp login` will
report that no such server exists.

If a login ever starts failing on reconnect, clear the stored credential
before retrying — a credential written by an older storage format lacks the
issuer field and is rejected on every subsequent connection:

```bash
claude mcp logout newrelic && claude mcp login newrelic
```

## Region

| Region | MCP server | NerdGraph API |
|--------|-----------|---------------|
| US | `https://mcp.newrelic.com/mcp/` | `https://api.newrelic.com/graphql` |
| EU | `https://mcp.eu.newrelic.com/mcp/` | `https://api.eu.newrelic.com/graphql` |
| JP | `https://mcp.jp.newrelic.com/mcp/` | — |

Set `observability.region` in `.devops-agents.yml` to match whichever you
registered, since that is what the NerdGraph path uses.

**Getting the region wrong returns an empty account rather than an error** —
which looks exactly like "nothing is wrong". Confirm with
`actor { accounts { id name } }` before trusting a clean result; a connected
server proves nothing about the region.

## Credentials

A **user key** (`NRAK-…`), from the environment. Never in a config file,
never in the repo:

```bash
export NEW_RELIC_API_KEY="<your user key>"
```

## The MCP server is optional

Every action also works over NerdGraph with `curl`, which is the documented
baseline. That is deliberate: the agent stays useful when the server is
unregistered, unauthenticated, or unreachable.

Note that some New Relic tools are **OAuth-only** and unavailable via API key
— the natural-language-to-NRQL and generated-report tools among them. The
agent's own actions do not depend on those.

## Configuration

Account id, region, critical services, dashboards and thresholds go in
`.devops-agents.yml` under `observability:` — see
[`.devops-agents.example.yml`](../../.devops-agents.example.yml). Without it,
the agent discovers what it can and asks for the rest.
