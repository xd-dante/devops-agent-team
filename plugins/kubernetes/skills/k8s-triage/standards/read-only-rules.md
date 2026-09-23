# Read-Only Rules

## The rule

**This agent never mutates a cluster.** Not the workloads, not the
kubeconfig, not the credentials.

One precisely-scoped exception: **`kubectl config use-context <existing>`**.
It writes the `current-context` key and nothing else — no cluster,
credential, or context is created, changed, or repaired. That single write is
the *only* permitted kubeconfig change. To avoid it entirely, pass
`--context <name>` on every command instead; either is acceptable, mixing
them is not.

It holds even when the request sounds like the user wants a fix applied.
Investigation produces findings; the change lands through GitOps (a chart or
infrastructure PR) or is applied by a human.

**Violating the letter of this rule violates the spirit of it.** If a command
could alter cluster state, kubeconfig, or credentials, do not run it.

## Allowed

```
kubectl get / describe / logs [--previous] / top / events / explain
kubectl api-resources / api-versions / version / cluster-info
kubectl auth can-i --list
kubectl config get-contexts / current-context / use-context <existing>
kubectl rollout status / history
kubectl diff -f <file>
helm list / get values / get manifest / template
```

## Forbidden

`apply`, `create`, `delete`, `edit`, `patch`, `replace`, `set`, `scale`,
`rollout restart|undo|pause|resume`, `annotate`, `label`, `cordon`,
`uncordon`, `drain`, `taint`, `exec`, `attach`, `cp`, `port-forward`,
`debug`, `run`, `expose`, `autoscale`.

Also `helm install|upgrade|uninstall|rollback`.

**Kubeconfig and credentials — also forbidden:** `kubectl config set-context`,
`set-cluster`, `set-credentials`, and any cloud CLI command that writes a
kubeconfig. The cluster is **already authenticated**. You switch between
contexts that already exist; you never create, update, or repair one.

> `exec`, `port-forward` and `debug` are forbidden even though they feel
> read-only: they open sessions that can mutate state. If in-pod output is
> genuinely needed, surface the exact command and let the human run it.

## The one gated exception

`actions/ephemeral-debug-container.md` attaches a short-lived diagnostic
container. It is the **only** mutating action here and requires explicit
approval, a non-protected environment, and stated cleanup.

## Red flags — STOP

- About to run any mutating verb → STOP
- About to write a kubeconfig or `kubectl config set-*` → STOP
- About to `exec` / `port-forward` / `debug` → STOP; surface the command
- No context matches the target → STOP and report; do not create one
- "The user clearly wants it fixed, so I'll just patch it" → STOP
- Reaching for `kubectl edit` to test a hypothesis → read the rendered spec
  and reason from it
