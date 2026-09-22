# Action — Ephemeral Debug Container

**The only mutating action in this skill.** It attaches a short-lived
diagnostic container to a running pod so an external dependency can be
reached from that pod's exact network identity.

## Gate — all required

- [ ] The user asked for this, or approved it after you proposed it
- [ ] The environment is **not** protected
- [ ] Cleanup is agreed up front (see the caveat below)

Any box unticked → **🛑 STOP**. Everything else here is read-only; this does
not become available because an investigation stalled.

## Why the obvious approaches fail

| Attempt | Result |
|---------|--------|
| `kubectl debug --target=<c>` with a root-default image | Config error — it inherits the pod's `runAsNonRoot`, and the image defaults to root |
| Add a ptrace capability to read `/proc/1/root` | The capability lands in the bounding set but never the effective set for a non-root ephemeral container — access stays denied |
| Run the debug container as root | Privilege escalation. Do not |

## The working approach

Patch the `ephemeralcontainers` subresource directly, run as a **non-root uid
that exists in the image's `/etc/passwd`**, and mount the pod's **existing**
secret volume — no cross-container `/proc` access needed.

```bash
POD=$(kubectl get pod -n <ns> -l <selector> -o jsonpath='{.items[0].metadata.name}')
DBG="dbg-<purpose>-$(date +%s)"

kubectl patch pod "$POD" -n <ns> --subresource=ephemeralcontainers --type=strategic -p "{
  \"spec\": {\"ephemeralContainers\": [{
    \"name\": \"$DBG\", \"image\": \"<diagnostic-image>\", \"stdin\": true, \"tty\": true,
    \"securityContext\": {\"runAsUser\": 65534, \"runAsGroup\": 65534, \"runAsNonRoot\": true, \"allowPrivilegeEscalation\": false},
    \"volumeMounts\": [{\"name\": \"<existing-secret-volume>\", \"mountPath\": \"/var/run/secrets/app\", \"readOnly\": true}],
    \"env\": [{\"name\": \"HOME\", \"value\": \"/tmp\"}],
    \"command\": [\"sh\", \"-c\", \"sleep 3600\"]
  }]}
}"
```

Non-negotiable details:

- **A uid that exists in the image.** `65534` (`nobody`) is present in most
  diagnostic images. An arbitrary uid like `1000` makes `ssh`/`sftp` fail
  with "No user exists for uid 1000".
- **`HOME=/tmp`** — that uid has no writable home otherwise.
- **Mount the pod's existing volume** rather than reaching into another
  container.
- **Fresh name every time.** Ephemeral containers do not survive a pod
  restart and names cannot be reused.
- **Re-resolve the pod name** every session; it changes on every restart.

## Before you start

```bash
kubectl config current-context     # drifts between sessions
```

## Do not trust the pod's own endpoint variables

In lower environments these often point at **mock** services rather than the
real dependency. Use the real endpoint explicitly, and say in the report
which one was used.

## Credentials

Prefer the mounted secret volume:

```bash
kubectl exec "$POD" -n <ns> -c "$DBG" -- sh -c \
  'base64 -d /var/run/secrets/app/<KEY> > /tmp/k && chmod 600 /tmp/k'
```

If the mount no longer carries the key — real drift happens when
infrastructure wiring is merged but never applied — report that as a finding.

Never leave a decoded secret on the local machine, and never print one.

## Interactive authentication is the user's step

Retrieving a credential and then authenticating to an external host with it
is not something this agent completes. Prepare the container, place the key,
then hand over the exact command:

```bash
kubectl exec -it "$POD" -n <ns> -c "$DBG" -- <client> -i /tmp/k <user>@<host>
```

Retrieving a file afterwards: `kubectl cp -n <ns> -c "$DBG" "$POD:/tmp/<file>" <dest>`

## Cleanup — state it up front

Ephemeral containers **cannot be deleted individually**. Only a pod restart
clears them:

```bash
kubectl rollout restart deployment/<name> -n <ns>    # the user runs this
```

An idle sleeping container is harmless meanwhile, but say clearly that a
restart is needed and that it is the user's call.

## Report

```
Cluster:     <cluster>   Namespace: <ns>
Pod:         <pod>       Container: <DBG>
Endpoint:    <the real endpoint used — not the pod's env var>
Credential:  <source>    (never print the value)
Result:      <what was reached / what failed>
Left behind: ephemeral container <DBG> — clears on a pod restart (user's call)
Next (user runs): <exact interactive command>
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `kubectl debug --target=...` | Patch `ephemeralcontainers` directly |
| Running as root to get access | Never; use a non-root uid plus the volume mount |
| Adding a ptrace capability | It does not take effect; mount the volume |
| An arbitrary uid like 1000 | Use one that exists in the image |
| Reusing a pod or container name | Re-resolve the pod; timestamp the name |
| Using the pod's endpoint variable | It may point at a mock |
| Leaving a decoded secret on disk | Delete it immediately |
| Claiming cleanup is done | Only a pod restart clears it — say so |
