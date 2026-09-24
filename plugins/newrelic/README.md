# newrelic

Daily observability triage: is anything actually wrong, and what needs a human.

## Region

| Region | MCP server | NerdGraph API |
|--------|-----------|---------------|
| US | `https://mcp.newrelic.com/mcp/` | `https://api.newrelic.com/graphql` |
| EU | `https://mcp.eu.newrelic.com/mcp/` | `https://api.eu.newrelic.com/graphql` |

The MCP URL defaults to **US** and is overridable without editing this
plugin — set `NEWRELIC_MCP_URL` in your `settings.json` `env` block:

```json
{
  "env": {
    "NEWRELIC_MCP_URL": "https://mcp.eu.newrelic.com/mcp/"
  }
}
```

Set `observability.region` in `.devops-agents.yml` to match, since that is
what the NerdGraph fallback path uses.

**Getting the region wrong returns an empty account rather than an error** —
which looks exactly like "nothing is wrong". Worse, OAuth against the wrong
regional endpoint can succeed while the account it authorises holds none of
your data, so a connected server is not evidence the region is right. Confirm
with `actor { accounts { id name } }` before trusting a clean result.

## Credentials

A **user key**, from the environment. Never in a config file, never in the
repo:

```bash
export NEW_RELIC_API_KEY="<your user key>"
```

The MCP server is optional. Every action also works over NerdGraph with
`curl`, which is the documented baseline.

## Configuration

Account id, region, critical services, dashboards and thresholds go in
`.devops-agents.yml` under `observability:` — see
[`.devops-agents.example.yml`](../../.devops-agents.example.yml). Without it,
the agent discovers what it can and asks for the rest.
