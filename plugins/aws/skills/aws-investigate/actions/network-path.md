# Action — Network Path

"A can't reach B." Trace the path in order and stop at the first break.

## Step 1 — Name both ends precisely

Source (pod, instance, function, egress address) and destination (endpoint,
external host), with ports. A vague pair produces a vague answer.

## Step 2 — Name resolution

A private endpoint must resolve to a **private** address. A public answer
means traffic will try to leave the network and be dropped.

```bash
aws ec2 describe-vpc-endpoints \
  --query 'VpcEndpoints[].{Service:ServiceName,Type:VpcEndpointType,State:State}' --output table
```

Note which services already have endpoints — traffic to those does **not**
traverse the NAT path, so do not attribute a NAT problem to them.

## Step 3 — Security groups, both directions

```bash
aws ec2 describe-security-groups --group-ids <dest-sg> \
  --query 'SecurityGroups[].IpPermissions[].{Proto:IpProtocol,From:FromPort,To:ToPort,SrcSGs:UserIdGroupPairs[].GroupId,Cidrs:IpRanges[].CidrIp}'
aws ec2 describe-security-groups --group-ids <src-sg> \
  --query 'SecurityGroups[].IpPermissionsEgress[].{Proto:IpProtocol,From:FromPort,To:ToPort,DstSGs:UserIdGroupPairs[].GroupId,Cidrs:IpRanges[].CidrIp}'
```

Destination inbound **and** source egress must both allow the flow.

**The pod-identity trap.** Where pods get their own network interface with
its own security group, rules on the **node's** group do not apply to that
pod's traffic. A symptom of "only this one service times out to the database"
is almost always exactly that: the pod's own group is missing from the
destination's inbound rules.

```bash
aws ec2 describe-network-interfaces --filters "Name=group-id,Values=<pod-sg>" \
  --query 'NetworkInterfaces[].{Id:NetworkInterfaceId,Desc:Description,Ip:PrivateIpAddress}' --output table
```

## Step 4 — Routes and zones

```bash
aws ec2 describe-route-tables --filters "Name=association.subnet-id,Values=<subnet>" \
  --query 'RouteTables[].Routes[].{Dest:DestinationCidrBlock,Gw:GatewayId,Nat:NatGatewayId,Vpce:VpcEndpointId}' --output table
aws ec2 describe-network-acls --filters "Name=association.subnet-id,Values=<subnet>" \
  --query 'NetworkAcls[].Entries[].{Rule:RuleNumber,Action:RuleAction,Cidr:CidrBlock,Ports:PortRange}' --output table
```

A private subnet reaching the internet needs an egress route. Check zones
too — cross-zone assumptions break where a gateway exists in only some.

## Step 5 — Egress identity for allow-listed destinations

External partners allow-list the **egress address**, not the pod:

```bash
aws ec2 describe-nat-gateways \
  --query 'NatGateways[].{Id:NatGatewayId,Subnet:SubnetId,Ip:NatGatewayAddresses[0].PublicIp,State:State}' --output table
```

If the partner reports "connection refused" rather than a timeout, the path
works and the problem is authentication or allow-listing — a different
investigation.

## Step 6 — Flow logs for the verdict

```bash
aws logs filter-log-events --log-group-name <flow-log-group> \
  --start-time $(( ($(date +%s) - 900) * 1000 )) \
  --filter-pattern '"REJECT"' --max-items 50
```

Rejections name the exact interface, port, and direction. Keep the window
tight — these queries are billed per GB scanned.

## Report

```
Account:   <id>   Region: <region>
Path:      <source (interface/sg)> → <destination (endpoint/sg)> : <port>
Resolution: <private | public | fails>
Groups:    dest inbound <allows?>   source egress <allows?>   pod identity: <yes/no>
Routes:    <egress route present?>   Zone: <zone>
Flow logs: <accept | reject on <interface> <port>>
Break at:  <the first failing hop>
Owner:     terraform-agent → <repo>/<file>
Nothing was mutated.
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Checking the node's group for a pod with its own identity | Its own group governs it |
| Checking only one direction | Destination inbound **and** source egress |
| Blaming the NAT path for a service that has an endpoint | Endpoints bypass it |
| Treating "connection refused" as a network block | The path works; it is auth or allow-listing |
| Unbounded flow-log scans | Tight window; billed per GB |
