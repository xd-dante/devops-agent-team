# Account Discovery

## Resolve, never hardcode

| Value | Source | Fallback |
|-------|--------|----------|
| Account id | `observability.account_id` | `actor { accounts { id name } }` — ask if more than one |
| Region | `observability.region` (`US`/`EU`) | Ask. **Do not guess** |
| User key | `$NEW_RELIC_API_KEY` (name from `observability.api_key_env`) | Stop and ask the user to export it |
| Critical services | `observability.critical_services` | Entity search, then ask which matter |
| Dashboards | `observability.dashboards` | `entitySearch(query: "type = 'DASHBOARD'")` |
| Thresholds | `observability.thresholds` | The defaults in `signal-triage.md` |

## Endpoints

| Region | NerdGraph | MCP server |
|--------|-----------|------------|
| US | `https://api.newrelic.com/graphql` | `https://mcp.newrelic.com/mcp/` |
| EU | `https://api.eu.newrelic.com/graphql` | `https://mcp.eu.newrelic.com/mcp/` |

**A wrong region returns an empty account, not an error** — which is
indistinguishable from "nothing is wrong".

This applies to the MCP server too: OAuth against the wrong regional endpoint
can complete successfully while authorising an account that holds none of your
data. **A connected server is not evidence the region is right** — confirm the
account before trusting any result.

This plugin ships no MCP server. It is registered by the user at user scope
per New Relic's own setup instructions, so the endpoint is their choice, not
this plugin's. The first-party hosts are `mcp.newrelic.com`,
`mcp.eu.newrelic.com` and `mcp.jp.newrelic.com`; if the connected server is
anywhere else, **stop and report it** rather than querying — that endpoint
holds an OAuth token, and a token already sent cannot be unsent. Enforcement
belongs in `allowedMcpServers` in managed settings, not in this skill.

Confirm the region resolves to a real account before reporting anything:

```bash
: "${NEW_RELIC_API_KEY:?export your user key first}"
NR_API="https://api.newrelic.com/graphql"        # or api.eu. for EU

nr() {  # nr '<graphql query>'
  curl -s -X POST "$NR_API" \
    -H 'Content-Type: application/json' -H "API-Key: $NEW_RELIC_API_KEY" \
    -d "$(jq -nc --arg q "$1" '{query:$q}')"
}

nr '{ actor { accounts { id name } } }' | jq -r '.data.actor.accounts[] | "\(.id) \(.name)"'
```

Empty list → wrong region or a key without account access. Stop and report;
do not proceed with an empty result set.

## The MCP server is optional

Where the plugin's MCP server is connected, prefer its tools — they are
cheaper than raw GraphQL. Where it is not, every action works over NerdGraph
with the `nr` helper above. **Never invent an MCP tool name**: if the
expected tool is not in the available list, fall back to NerdGraph rather
than guessing.

## Query shapes

Verified against the NerdGraph docs:

```graphql
# open issues (states: CREATED, ACTIVATED, DEACTIVATED, CLOSED)
{ actor { account(id: ACCOUNT) { aiIssues {
  issues(filter: {states: [ACTIVATED]}) {
    issues { issueId title priority state entityNames entityGuids createdAt }
    nextCursor } } } } }

# entity health
{ actor { entitySearch(query: "alertSeverity IS NOT NULL") {
  count results { entities { name entityType guid alertSeverity reporting } } } } }

# NRQL
{ actor { account(id: ACCOUNT) { nrql(query: "SELECT ...") { results } } } }

# alert conditions and policies
{ actor { account(id: ACCOUNT) { alerts {
  policiesSearch { policies { id name } }
  nrqlConditionsSearch { nrqlConditions { id name type enabled } } } } } }
```

Paginate with `nextCursor` until it comes back empty. An unpaginated first
page silently truncates, which under-reports problems.

## Errors are not emptiness

GraphQL returns HTTP 200 with an `errors` array. Always check it:

```bash
nr '<query>' | jq -e '.errors == null' >/dev/null || echo "QUERY FAILED"
```

A failed query that is read as "no results" is the single easiest way for
this agent to report all-clear on a broken system.
