# Action — Locate Resource

"Where is X", "does X exist", "what is X attached to". The cheap first step
that prevents most wrong-account and wrong-resource investigations.

## Step 1 — Prove the identity

```bash
export AWS_PROFILE=<profile for this environment>
aws sts get-caller-identity --query 'Account' --output text
aws configure get region
```

State the account and region in the report. Never skip this.

## Step 2 — Search by tag, then by type

```bash
aws resourcegroupstaggingapi get-resources \
  --tag-filters "Key=Environment,Values=<env>" \
  --query 'ResourceTagMappingList[].ResourceARN' --output table

aws rds describe-db-instances --query 'DBInstances[].{Id:DBInstanceIdentifier,Class:DBInstanceClass,Status:DBInstanceStatus,AZ:AvailabilityZone}' --output table
aws ec2 describe-instances --query 'Reservations[].Instances[].{Id:InstanceId,Type:InstanceType,State:State.Name,Name:Tags[?Key==`Name`]|[0].Value}' --output table
aws secretsmanager list-secrets --query 'SecretList[].Name' --output table
aws eks list-clusters
```

Tags beat guessed names.

## Step 3 — Establish who owns it

```bash
grep -rln "<resource-identifier>" <infra-repo>/ 2>/dev/null
```

Check every infrastructure repo in config before calling something unmanaged.

## Step 4 — Relationships

```bash
aws ec2 describe-security-groups --group-ids <sg-id> \
  --query 'SecurityGroups[].{Id:GroupId,Ingress:IpPermissions,Egress:IpPermissionsEgress}'
aws ec2 describe-network-interfaces --filters "Name=group-id,Values=<sg-id>" \
  --query 'NetworkInterfaces[].{Id:NetworkInterfaceId,Desc:Description,Ip:PrivateIpAddress}' --output table
aws ec2 describe-subnets --query 'Subnets[].{Id:SubnetId,AZ:AvailabilityZone,Cidr:CidrBlock}' --output table
```

## Report

```
Account:  <id>   Profile: <profile>   Region: <region>
Resource: <type> <identifier>
State:    <status / class / size>
Attached: <interfaces, security groups, subnets, zones>
Owned by: <repo>  (confirmed at <file>)
Nothing was mutated.
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Reading before proving the identity | `sts get-caller-identity` first |
| Searching by guessed name | Search by tag, or list the type |
| Declaring a resource unmanaged | Check every infrastructure repo |
| Assuming the region | State it |
