# Finding Sources

How findings and operations items are produced, and the behaviours that make
backlogs grow without anyone noticing.

## Lifecycles

| Thing | Created by | Closes when | Does not close when |
|-------|------------|-------------|---------------------|
| Control finding | control evaluation per resource | resource passes, or is deleted (archived, then purged after about 90 days) | — |
| Product finding (threat, vulnerability, patch) | the product's own scan | the product resolves it, or a rescan clears it | the artefact is never rebuilt or rescanned |
| Operations item mirrored from a finding | the hub-to-OpsCenter integration | **only when someone resolves it** | its finding passes, is archived, or is purged |

The last row is the single biggest backlog source. Every fix therefore needs
a resolve step afterwards, and where both the administrator and the member
mirror findings, that means both copies.

## Generators of volume

| Generator | Signature | Consequence |
|-----------|-----------|-------------|
| Integration includes medium and low severities | most items are severity 3–4 | volume grows with every new resource |
| Ephemeral compute (autoscaled nodes, runners) | one item per distinct short-lived instance | grows with node churn and never shrinks |
| Patch compliance per scan run | same title, same instance, new id per run | thousands of findings from a few instances |
| Fleet-wide association targeting `*` | association compliance failing on images the association does not support | every new node fails the control |
| Tagging standard | platform-created resources untagged | hundreds of low findings that cannot be fixed at the source |
| Overlapping standards (two versions of the same benchmark) | similar titles twice | noise, not new risk |

## Drift that keeps a finding alive

- Manual rules added to a group whose module manages rules as separate
  resources: apply never removes them.
- A setting or standard enabled in the console and absent from code.
- A code change merged but never applied, or applied from a stale module
  cache.
- Committed build artefacts that dependency bots do not rebuild.

## Severity mapping

Operations-item severity `1` critical, `2` high, `3` medium, `4` low. Some
items carry no severity. Report them as their own bucket; never fold them
into a severity.
