## What

<!-- One or two lines. -->

## Why

<!-- The failure this rule or agent prevents. A rule without a consequence
     attached tends not to get followed. -->

## Checklist

- [ ] `python3 scripts/validate.py` passes
- [ ] New agent registered in **both** `.claude-plugin/marketplace.json` and
      the orchestrator's `routing-table.md`
- [ ] No org-specific values — no hostnames, account ids, cluster names,
      internal repo names, ticket ids, or figures from a real bill
- [ ] No secrets, keys, tokens, kubeconfigs, state files or `.env`
- [ ] Mutating actions have a gate
- [ ] Hub `SKILL.md` still reads as a router (~80 lines or fewer)
