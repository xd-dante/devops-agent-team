# newrelic

Daily observability triage: is anything actually wrong, and what needs a human.

## The MCP server is bundled

This plugin ships an `.mcp.json` pointing at the hosted MCP server. Set
`NEWRELIC_MCP_URL` if your organisation is not in the default region (see
[Region](#region)), then authenticate once:

```bash
claude mcp login plugin:newrelic:newrelic
```

Tools appear in the **next** session, not the current one — the client binds
its servers at startup.

## "Rejected them on reconnect" is a permission error, not an auth error

Claude Code reports a **403** from the MCP server as *"Got new credentials, but
&lt;server&gt; rejected them on reconnect"*. That wording points at a stale or
broken credential and will send you re-registering the server at other scopes.
It is neither of those.

Tell the two apart **before changing any configuration** — present the stored
token yourself and read the status code:

- **403** `Missing required capabilities to access MCP server` → OAuth
  succeeded; the user lacks permission. Nothing in this plugin, and nothing in
  Claude Code, can fix it.
- **401** → a real authentication problem.

The MCP server permission (`New Relic MCP Server`, READ) is
**organisation-scoped**. Account-level administrator access — however broad —
never grants it. An administrator must give a group the user belongs to an
**organisation-scoped** role containing that permission: the built-in
read-only organisation role carries it, or they can create a custom
organisation-scoped role holding only that one permission, which grants no
administrative capability.

Enabling the feature org-wide in the provider's feature-control screen is a
**separate layer** and does not authorise an individual user. Both are needed,
so a screenshot showing the feature enabled does not rule the permission out.

NerdGraph does not check this permission, so the agent's queries keep working
over the API while a grant is pending.

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
