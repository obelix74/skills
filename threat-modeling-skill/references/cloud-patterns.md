# Cloud Infrastructure Security Patterns

Common findings and mitigations for AWS, GCP, and Azure cloud architectures.
Reference when reviewing cloud-native designs.

---

## Credential Patterns

### Static Credentials — Always a Critical Finding

```
Found as:
  AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY in environment variables
  Service account JSON key files on disk
  Database username/password in config files
  Any credential with no expiry date

Why critical:
  Static credentials never expire automatically
  If exposed (public repo, logs, metadata service), attacker has
  permanent access until manually rotated
  Manual rotation is operationally difficult → often not done

Replacement patterns:
  EC2 → IAM instance profile (credentials rotate every hour)
  EKS → Pod Identity or IRSA (IAM Roles for Service Accounts)
  GCE → Service account via metadata server (no key files)
  GKE → Workload Identity Federation
  Azure → Managed Identity
  Cross-cloud → AWS STS with Web Identity Federation

If credentials found in public GitHub:
  Treat as already compromised — do not assume zero exposure window
  Rotate all secrets in the repository immediately
  Check CloudTrail / audit logs for unauthorized use
  Revoke and reissue — do not just update the secret
```

---

## IAM Patterns

### Shared IAM Roles — Always a High or Critical Finding

```
Found as:
  All services in a pipeline using one role
  All workers in a fleet using one role
  One role for dev AND prod

Why dangerous:
  Compromise of any service = compromise of all services
  Blast radius = everything that role can access
  No ability to distinguish which service took which action

Mitigation:
  One IAM role per service — named after the service
  Job-scoped vended credentials for batch workloads:
    Credential vending service issues short-lived STS per job
    Role ARN encodes job_id in session name
    Expires when job completes
    CloudTrail captures which job assumed which role

  Session tags for audit:
    aws:RequestedRegion, job:id, service:name, tenant:id
    Appear in CloudTrail — correlate storage access to job
```

### Overly Broad S3 Access

```
Found as:
  s3:* on * (wildcard resource)
  s3:GetObject on arn:aws:s3:::bucket/* (entire bucket)
  No prefix condition on ListBucket

Mitigation:
  Scope to minimum prefix:
    "Resource": [
      "arn:aws:s3:::training-bucket/jobs/${aws:PrincipalTag/job-id}/*"
    ]

  Explicit deny on destructive operations:
    "Effect": "Deny",
    "Action": ["s3:DeleteObject", "s3:DeleteBucket", "s3:PutBucketPolicy"],
    "Resource": "*"

  S3 Object Lock for immutable data:
    GOVERNANCE mode — privileged users can still delete
    COMPLIANCE mode — nobody can delete before retention period
    Use COMPLIANCE for audit records and training data
```

---

## Database Patterns

### Username/Password on PostgreSQL/RDS — Always a Critical Finding

```
Found as:
  Hardcoded credentials in config files
  Credentials in environment variables
  Credentials in source code or GitHub

Mitigation — RDS Proxy + IAM database authentication:
  1. Enable IAM authentication on RDS cluster
  2. Create RDS Proxy in front of the cluster
  3. Each service gets an IAM role with rds-db:connect permission
  4. No username/password anywhere — IAM token used instead
  5. Token expires after 15 minutes — automatic rotation

  IAM policy for service:
    "Action": "rds-db:connect",
    "Resource": "arn:aws:rds-db:region:account:dbuser:proxy-id/service-user"

Schema-level least privilege:
  Validation service role → read/write validation schema only
  Tokenizer role → read-only on validation schema
  Training role → read-only on job manifest table only (if needed)
  Audit role → write-only on audit schema
  No role has UPDATE or DELETE on audit tables
  No role has access to another service's schema
```

### RDS Encryption at Rest

```
Important constraint:
  Encryption at rest CANNOT be enabled on an existing RDS cluster
  Must be enabled at creation time

If a cluster was created without encryption:
  Create new encrypted cluster
  Migrate data
  Decommission old cluster
  This is not optional — it is a hard AWS limitation

Enable with:
  aws rds create-db-cluster --storage-encrypted --kms-key-id <key-arn>
```

---

## Network Patterns

### Missing VPC Endpoints — High Finding

```
Found as:
  Services communicating with S3 or KMS via public internet
  No mention of VPC endpoints in the design
  Traffic to AWS services routing through NAT gateway

Why it matters:
  S3 and KMS traffic on public internet is visible to network observers
  NAT gateway adds latency and cost
  No VPC endpoint = data leaving the AWS network

Mitigation:
  Create VPC endpoints for:
    S3 (Gateway endpoint — free)
    KMS (Interface endpoint)
    RDS Proxy (Interface endpoint)
    CloudWatch Logs (Interface endpoint)
    STS (Interface endpoint for workload identity)

  Traffic stays on AWS network — never touches public internet
  VPC endpoint policies restrict which buckets are accessible
```

### Missing Kubernetes NetworkPolicy — Critical Finding

```
Found as:
  No NetworkPolicy resources mentioned in design
  Services with public IP (LoadBalancer or NodePort service type)
  Pods that accept ingress from 0.0.0.0/0

Mitigation:
  Default deny all ingress and egress:
    apiVersion: networking.k8s.io/v1
    kind: NetworkPolicy
    metadata:
      name: default-deny-all
    spec:
      podSelector: {}
      policyTypes: [Ingress, Egress]

  Allowlist specific paths:
    Validation pod: ingress from ingestion pod only
    Tokenizer pod: egress to RDS Proxy + S3 endpoint only
    Training pod: no ingress, egress to S3 endpoint only

  Use pod selector labels not IP addresses:
    ipBlock is brittle (IPs change)
    podSelector is stable (labels don't change)
```

---

## Audit Patterns

### S3 Access Logging — Always Check This

```
Found as:
  No mention of S3 access logging in the design
  "We will add monitoring in the future"

Why it matters:
  Without S3 access logging, you cannot answer:
    Who accessed this object?
    When was it accessed?
    Was it accessed from an unexpected source?
  Data exfiltration through S3 is invisible

Mitigation:
  Enable server access logging on every bucket:
    Source bucket: training-data-bucket
    Target bucket: audit-logs-bucket (separate account ideally)
    Log prefix: s3-access/training-data/

  Enable S3 Object-level CloudTrail:
    Captures GetObject, PutObject, DeleteObject with principal
    More granular than server access logging
    Costs more — use for sensitive buckets

  Enable on:
    All staging buckets
    Training data bucket
    Model artifact bucket
    Audit log bucket itself (detect tampering)
```

### CloudWatch Is Not an Audit Trail

```
Important distinction:
  CloudWatch = operational logs (errors, metrics, training progress)
  Audit trail = immutable record of every security-relevant action

CloudWatch logs can be deleted
CloudWatch logs are not append-only
CloudWatch logs do not have hash chain integrity

A design that says "everything goes to CloudWatch" has no audit trail.

Real audit trail requirements:
  S3 with Object Lock COMPLIANCE mode
  WORM — cannot be deleted before retention period
  Hash chain — each record contains hash of previous
  7 year retention minimum
  Separate from operational logging infrastructure
```

---

## Encryption Patterns

### Key Rotation — Always Ask

```
Ask:
  What encryption keys are in use?
  What is the rotation schedule?
  Who manages the keys?
  What happens during key rotation — is there downtime?

NIST SP 800-57 guidance:
  Data encryption keys (DEK): rotate per file or per snapshot
  Key encryption keys (KEK): rotate annually or more frequently
  Master keys: rotate annually

AWS KMS automatic rotation:
  Customer managed keys — enable automatic annual rotation
  Rotation does not affect existing encrypted data
  AWS re-encrypts the key material, not the data

Forward-only rotation (Iceberg model):
  New snapshots use new key
  Existing snapshots remain readable with original key
  Old keys retained in encryption-keys array
  O(1) rotation — metadata update only
```
