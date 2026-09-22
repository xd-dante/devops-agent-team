# Account Discovery

## Prove the identity before reading anything

```bash
aws sts get-caller-identity --query 'Account' --output text
aws configure get region
```

An investigation against the wrong account produces **confident, wrong
answers**. This is the most common failure mode in cloud investigation, and
it is entirely preventable.

State the account and region in every report.

## Resolve the environment's profile

From `.devops-agents.yml` `environments.<env>.cloud_profile` where present.
Otherwise ask which profile corresponds to the environment — do not infer it
from a naming pattern.

Note that several environments commonly share one account. "dev" and
"staging" being in the same account is normal, so the account alone does not
tell you which environment you are looking at — resource tags and names do.

## Find the owning code

A resource that looks unmanaged usually is not:

```bash
grep -rln "<resource-identifier>" <infra-repo>/ 2>/dev/null
```

Check **every** infrastructure repo listed in config before concluding a
resource is unmanaged. Missing a second estate is an easy and embarrassing
mistake.

## Search by tag before name

```bash
aws resourcegroupstaggingapi get-resources \
  --tag-filters "Key=Environment,Values=<env>" \
  --query 'ResourceTagMappingList[].ResourceARN' --output table
```

Tags are more reliable than guessed names.

## Live state over code

Infrastructure code can be merged and never applied. When the question is
"what is true now", read the cloud, not the repo. When the question is "what
should be true", read the repo.

Drift between the two is itself a finding worth reporting.

## Pods and cloud identity

Where pods are given their **own** network identity (a dedicated interface
with its own security group) or their own IAM identity (a token-based role
binding), node-level rules and node roles do **not** apply to them. Diagnose
the pod's own identity, not the node's.
