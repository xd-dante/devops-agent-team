# newrelic

Daily observability triage: is anything actually wrong, and what needs a human.

## Region

The MCP server URL in `.mcp.json` defaults to the **US** endpoint. On an EU
account, change it:

| Region | MCP server | NerdGraph API |
|--------|-----------|---------------|
| US | `https://mcp.newrelic.com/mcp/` | `https://api.newrelic.com/graphql` |
| EU | `https://mcp.eu.newrelic.com/mcp/` | `https://api.eu.newrelic.com/graphql` |

Getting this wrong returns an empty account rather than an error — which
looks exactly like "nothing is wrong".

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
