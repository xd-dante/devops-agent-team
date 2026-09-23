# Action — Access Denied

An authorisation failure from a pod, a CI job, or a role.

## Step 1 — Read the message literally

The error names the principal, the action, and the resource. All three come
free. **Quote it; do not paraphrase it into a guess.**

## Step 2 — Simulate, do not read and infer

```bash
aws iam simulate-principal-policy \
  --policy-source-arn <role-arn> \
  --action-names <service>:<Action> \
  --resource-arns <resource-arn> \
  --query 'EvaluationResults[].{Action:EvalActionName,Decision:EvalDecision,Statements:MatchedStatements[].SourcePolicyId}'
```

The simulator evaluates identity policies and reports **which statement
matched**. Reading policy JSON and concluding "this should work" is how these
investigations go wrong.

What the simulator does **not** fully cover: resource policies, permission
boundaries, organisation-level policies, and session policies. If it says
allow and reality says deny, one of those is the cause.

## Step 3 — For a pod: is the identity binding actually wired

Four things must line up, and any one breaks it silently:

```bash
# 1. the service account carries the role annotation
kubectl get sa <sa> -n <ns> -o jsonpath='{.metadata.annotations}{"\n"}'
# 2. the pod actually uses that service account
kubectl get pod <pod> -n <ns> -o jsonpath='{.spec.serviceAccountName}{"\n"}'
# 3. the role's trust policy accepts this cluster's identity provider and this SA
aws iam get-role --role-name <role> --query 'Role.AssumeRolePolicyDocument'
# 4. the provider is registered
aws iam list-open-id-connect-providers
aws eks describe-cluster --name <cluster> --query 'cluster.identity.oidc.issuer'
```

The trust policy's subject condition must match the namespace and service
account **exactly**. A namespace or SA rename breaks it with a confusing
authorisation error rather than an assume-role error.

## Step 4 — Resource policies and encryption keys

```bash
aws s3api get-bucket-policy --bucket <bucket> --query Policy --output text
aws kms get-key-policy --key-id <id> --policy-name default --query Policy --output text
```

Encryption keys are a frequent culprit: a principal allowed to **read** a
secret still needs decrypt permission on the key that encrypts it. Encrypted
notification topics similarly need a dual grant — the publishing service and
the key.

## Report

```
Account:   <id>
Principal: <role arn>
Action:    <service:Action>    Resource: <arn>
Simulator: <Allow | ExplicitDeny | ImplicitDeny> — matched: <policy ids>
Binding:   sa annotation <ok?> | pod uses sa <ok?> | trust subject <ok?> | provider <registered?>
Resource policy / key: <findings>
Root cause: <the specific missing permission or mismatch>
Owner:     terraform-engineer → <repo>
Nothing was mutated.
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Reading policy JSON and concluding it works | Use the simulator |
| Checking the policy but not the trust policy | The subject must match exactly |
| Forgetting the encryption key | Reading a secret needs decrypt on its key |
| Attaching a policy to test the theory | Read-only; route the change |
| Paraphrasing the denial message | It names principal, action, resource |
