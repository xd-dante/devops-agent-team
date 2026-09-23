# Action — Database Diagnostics

Connection errors, slowness, or storage pressure on a managed database.

## Step 1 — Instance facts

```bash
aws rds describe-db-instances --db-instance-identifier <id> \
  --query 'DBInstances[0].{Class:DBInstanceClass,Engine:Engine,Version:EngineVersion,Status:DBInstanceStatus,Storage:AllocatedStorage,MaxStorage:MaxAllocatedStorage,MultiAZ:MultiAZ,Params:DBParameterGroups[0].DBParameterGroupName}'
```

Instance class drives the connection ceiling, and that is the most common
root cause.

## Step 2 — "too many clients" / connection exhaustion

The engine's maximum connections usually scales with instance memory unless
overridden. **Read the real value rather than assuming:**

```bash
aws rds describe-db-parameters --db-parameter-group-name <group> \
  --query "Parameters[?ParameterName=='max_connections'].[ParameterValue,Source]" --output table

aws cloudwatch get-metric-statistics --namespace AWS/RDS \
  --metric-name DatabaseConnections --dimensions Name=DBInstanceIdentifier,Value=<id> \
  --start-time "$(date -u -v-3H +%Y-%m-%dT%H:%M:%S)" --end-time "$(date -u +%Y-%m-%dT%H:%M:%S)" \
  --period 300 --statistics Maximum --query 'Datapoints[].[Timestamp,Maximum]' --output table
```

Typical cause: several logical databases on one small instance, each with an
idle-heavy connection pool.

**On connection proxies.** A proxy multiplexes; it does **not** raise the
engine's maximum connections. Pinning behaviour (session-level statements,
advisory locks, temp tables, prepared statements) degrades the multiplexing,
and a proxy's minimum cost can exceed the small instance it would front. For
plain connection exhaustion, moving up one instance class is usually both
cheaper and more effective. Propose a proxy only for a genuine
connection-churn problem, with the churn evidenced.

The instance class is owned by the infrastructure repo — route the fix there.

## Step 3 — Performance

```bash
for m in CPUUtilization FreeableMemory ReadLatency WriteLatency FreeStorageSpace; do
  echo "== $m"
  aws cloudwatch get-metric-statistics --namespace AWS/RDS --metric-name $m \
    --dimensions Name=DBInstanceIdentifier,Value=<id> \
    --start-time "$(date -u -v-6H +%Y-%m-%dT%H:%M:%S)" --end-time "$(date -u +%Y-%m-%dT%H:%M:%S)" \
    --period 300 --statistics Average Maximum --query 'Datapoints[-5:]' --output table
done
```

On **burstable** instance classes also check the CPU credit balance — an
exhausted balance looks exactly like a slow database, and no amount of query
tuning fixes it.

## Step 4 — Logs

```bash
aws rds describe-db-log-files --db-instance-identifier <id> \
  --query 'DescribeDBLogFiles[-3:].[LogFileName,Size]' --output table
aws rds download-db-log-file-portion --db-instance-identifier <id> \
  --log-file-name <name> --starting-token 0 --output text | tail -100
```

## Step 5 — If the app cannot reach a healthy instance

That is a network finding, not a database one. Route to
`actions/network-path.md` — and remember that a pod with its own network
identity is not covered by node-level rules.

## Report

```
Account:   <id>   Region: <region>
Instance:  <id>   <class> <engine> <version>   Status: <status>
Ceiling:   max connections <n> (source: <default|user>)   Peak used: <n>
Metrics:   cpu <x>%  mem <y>  credits <z>  storage <free>
Logs:      <key error lines, verbatim>
Root cause: <explanation or ranked hypotheses>
Owner:     terraform-engineer → <repo>/<file>
Nothing was mutated.
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Proposing a connection proxy for exhaustion | It does not raise the ceiling; size up instead |
| Ignoring credit balance on a burstable class | Exhausted credits mimic a slow database |
| Assuming the connection ceiling from a class table | Read the parameter and its source |
| Diagnosing the database when the pod cannot reach it | It is a network finding |
| Modifying the instance to test a theory | Read-only; route the change |
