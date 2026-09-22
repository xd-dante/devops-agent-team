# Action — Check Networking

A service is unreachable, or a pod cannot reach a dependency.

## Step 1 — Endpoints first

```bash
kubectl get svc <name> -n <ns> -o yaml
kubectl get endpoints <name> -n <ns>
kubectl get svc <name> -n <ns> -o jsonpath='{.spec.selector}{"\n"}'
kubectl get pods -n <ns> --show-labels
```

**Empty endpoints is the most common cause.** It means the selector matches
no *ready* pod — either the labels do not match, or readiness is failing.

## Step 2 — Port alignment

```bash
kubectl get svc <name> -n <ns> -o jsonpath='{.spec.ports[*]}{"\n"}'
kubectl get pod <pod> -n <ns> -o jsonpath='{.spec.containers[*].ports[*]}{"\n"}'
```

Service port → target port → container port → **what the app actually
listens on**. The last is only visible in the app's startup logs, and a
mismatch is silent.

## Step 3 — Service mesh, if present

```bash
kubectl get pod <pod> -n <ns> -o jsonpath='{.spec.containers[*].name}{"\n"}'   # sidecar?
kubectl get virtualservice,destinationrule,peerauthentication -n <ns> 2>/dev/null
kubectl logs <pod> -n <ns> -c <sidecar> --tail=50
```

With a sidecar, traffic routes through a proxy: mutual-TLS mode mismatches
and routing rules matching no pod both present as connection failures between
healthy-looking pods.

## Step 4 — Egress to external dependencies

```bash
kubectl get pod <pod> -n <ns> -o jsonpath='{.metadata.annotations}{"\n"}'
```

Where pods get their **own** network identity — a dedicated interface with
its own security group — node-level egress rules do not apply to them. A
symptom of "only this one service times out to the database" is usually
exactly that. The rules are owned by the infrastructure repo, so
`HANDOFF → terraform-agent` with the finding.

DNS:

```bash
kubectl logs -n kube-system -l k8s-app=kube-dns --tail=50
```

## Report

```
Cluster:    <cluster>
Path:       <ingress> → <svc>:<port> → <pod>:<targetPort>
Endpoints:  <n> ready  (empty = selector or readiness problem)
Mesh:       <sidecar yes/no> <mTLS mode> <routing findings>
Egress:     <dedicated identity? which> <blocked destination>
Root cause: <explanation or ranked hypotheses>
Owner:      <agent> → <repo/file>
Nothing was mutated.
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `port-forward` to test connectivity | Forbidden — surface the command |
| `exec` + curl from inside a pod | Forbidden — reason from endpoints, ports, logs |
| Ignoring empty endpoints | It is the answer more often than not |
| Checking node rules for a pod with its own identity | Its own rules govern it |
| Assuming the container port is what the app listens on | Confirm in startup logs |
