# Read-Only Rules — Security Review

## The rule

**This skill reads. It does not change findings, items, controls or
settings.** The output is evidence and prepared lists. The change is routed
through the orchestrator and approved by a human.

## Allowed

```
sts            get-caller-identity
securityhub    describe-hub / get-administrator-account / list-members / list-finding-aggregators
               get-enabled-standards / describe-standards-controls / list-enabled-products-for-import
               get-findings / get-insights / list-automation-rules
ssm            get-ops-summary / describe-ops-items / get-ops-item / get-service-setting
               list-associations / describe-association-executions / describe-instance-information
events         list-rules / describe-rule / list-targets-by-rule
guardduty      list-detectors / get-detector / list-findings / get-findings
inspector2     batch-get-account-status / list-findings / list-coverage
config         describe-configuration-recorders / describe-delivery-channel-status
ec2|kms|iam    describe-* / get-* / list-*   (to verify resources a finding names)
```

## Forbidden: these look harmless but mutate

| Verb | Why it is a mutation |
|------|----------------------|
| `ssm update-ops-item` | closes or changes someone's ticket |
| `ssm update-service-setting` / `reset-service-setting` | changes what the integration creates |
| `securityhub batch-update-findings` | changes workflow status or suppresses a finding |
| `securityhub update-standards-control` / `batch-update-standards-control-associations` | disables a control for everyone |
| `securityhub enable-*` / `disable-*` / `create-insight` / `create-automation-rule` | changes the hub |
| `guardduty archive-findings` / `create-filter` | hides a threat finding |
| `inspector2 enable` / `disable` | changes scanning and cost |
| anything security-group, key or policy related that is not describe/get/list | changes access |

"I'll just resolve one to see what happens" is a mutation.

## Read-only is not free

- A full finding pull is large and slow. Pull once and project.
- Batch id filters (about 20 values per field), rather than one call per
  finding.
- Some describe calls need permissions a power-user role lacks, such as
  reading role details. Quote the denial verbatim and carry on.

## Red flags: STOP

- About to run any verb in the forbidden table → prepare the list instead
- About to call a runtime-threat finding benign → give the confirming check
- About to report one total across administrator and members → split it
- Identity not proved for this account → prove it first
