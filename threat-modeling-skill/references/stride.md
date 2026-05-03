# STRIDE Reference

Complete question, check, and mitigation for each threat.
Apply at every trust boundary crossing in the DFD.

---

## S — Spoofing

**Question:** Can an attacker pretend to be a legitimate principal?

**What to check:**
- Is there authentication on every trust boundary crossing?
- Are tokens/credentials verified — not just present?
- Can a service impersonate another service?
- Can one tenant impersonate another tenant?
- Are long-lived static credentials in use?

**Mitigations:**
```
Service-to-service:
  SPIFFE/SPIRE — each service gets a SVID (cryptographic identity)
  Mutual TLS — both sides present certificates
  Validation service only accepts requests with valid SVID
  from the ingestion service namespace

External data sources:
  Checksum verification against known manifests
  SFTP host key verification + certificate pinning
  S3 bucket policy restricting source principals

Credential hygiene:
  Replace static access keys with EC2 instance profile
  Replace static keys with Workload Identity Federation (GCP)
  Replace static keys with Pod Identity (EKS)
  Credentials rotate automatically — no manual rotation needed

Multi-tenant systems:
  External ID in IAM trust policy prevents confused deputy
  Per-tenant realm isolation in catalog (Polaris model)
  Cross-account IAM with external ID — prevents confused deputy
```

---

## T — Tampering

**Question:** Can data be modified in transit or at rest without detection?

**What to check:**
- Is there a checksum or hash on data crossing each boundary?
- Can database records be modified after they are written?
- Can files be substituted between stages of a pipeline?
- Can configuration or validation rules be modified?
- Can training data or model inputs be poisoned?

**Mitigations:**
```
Data in transit:
  TLS for all service-to-service communication
  Message signing — HMAC or asymmetric signature
  Verify signature before processing

Data at rest — checksum chain:
  Ingestion:   SHA-256 on input → stored in audit log
  Processing:  verify input checksum → store output checksum
  Consumption: verify checksum before processing
  Any mismatch → reject + alert + human review

Database records:
  Append-only tables — no UPDATE or DELETE granted
  Immutable records — new version creates new row
  Hash chain — each record contains hash of previous record

Object storage:
  S3 Object Lock COMPLIANCE mode — immutable for retention period
  Even AWS cannot delete before retention period
  Use for audit records, training data, model artifacts

Validation results:
  Results written once, never modified
  Each result record includes SHA-256 of validated content
  Downstream consumer verifies checksum before consuming result
```

---

## R — Repudiation

**Question:** Can an actor deny they took an action?

**What to check:**
- Is every sensitive action logged?
- Does the audit record include who, what, when, result?
- Is the audit trail stored separately from operational data?
- Can the audit trail itself be tampered with or deleted?
- Are service identities captured — not just user identities?

**What a complete audit record contains:**
```
requestId          → correlation across services
sourceIdentity     → SPIRE SVID or IAM role ARN of caller
targetResource     → what was accessed or modified
action             → what was done (read, write, delete, validate)
contentChecksum    → SHA-256 of the content if applicable
result             → success / failure / partial
failureReason      → if applicable
timestamp          → ISO 8601, UTC
processingTime     → latency in ms
serviceVersion     → which binary version ran this action
```

**Mitigations:**
```
Storage:
  WORM append-only store — separate from operational database
  S3 Object Lock COMPLIANCE mode for long-term audit records
  7 year retention minimum for legal defensibility

Integrity:
  Hash chain — each audit record contains hash of previous record
  Nightly verification job checks chain integrity
  Any break in chain = tampering detected + immediate alert

Access:
  Audit store is write-only for services
  No service can read its own audit records
  Only a separate audit reader role can query
  Audit reader role requires MFA + approval
```

---

## I — Information Disclosure

**Question:** Can unauthorized parties read sensitive data?

**What to check:**
- Are credentials stored in environment variables, config files, or public repos?
- Are IAM roles scoped to minimum required access?
- Can a compromised component reach data it shouldn't reach?
- Is data encrypted at rest and in transit?
- Are there missing egress controls that allow data exfiltration?
- Is S3 access logging enabled?
- Are validation rules, schemas, or configs exposed publicly?

**The two fastest Information Disclosure findings:**
```
1. Static credentials anywhere:
   Environment variables, config files, GitHub repos
   → Treat repo as already compromised
   → Rotate all secrets immediately
   → Replace with instance profile / workload identity

2. Overly broad IAM scope:
   Service can read data from other tenants
   Service can read data from other pipeline stages
   Role can be assumed by unexpected principals
   → Scope to minimum prefix, explicit deny on excess
```

**Mitigations:**
```
Credentials:
  EC2 instance profile — no static keys on EC2
  Workload Identity Federation — no static keys on GCP
  Pod Identity / IRSA — no static keys in Kubernetes
  AWS Secrets Manager / HashiCorp Vault for application secrets
  Automatic rotation — never manual

IAM scope:
  Per-service roles — one role per service, not shared
  Per-job vended credentials — STS with job-scoped prefix
  Explicit deny on delete operations
  Explicit deny on iam:*, ec2:* for application roles
  S3 prefix conditions — role can only read its own prefix

Network egress:
  Kubernetes NetworkPolicy — allowlist only
  VPC endpoints for S3, KMS, RDS — traffic never on public internet
  gVisor sandbox — system call filtering on sensitive pods
  DNS allowlist — only approved hostnames resolvable

Encryption:
  S3 SSE-KMS with customer-managed keys
  RDS encryption at rest — must enable at creation time
  Table-level encryption for sensitive data (Polaris/Iceberg model)
  Key rotation schedule — NIST SP 800-57 (annually or per snapshot)
```

---

## D — Denial of Service

**Question:** Can an attacker prevent legitimate use?

**What to check:**
- Is there a single point of failure in the pipeline?
- Are there rate limits on ingestion or processing?
- What happens if a downstream service is unavailable?
- Can a large volume of invalid requests overwhelm a service?
- Is there a maximum file size or volume limit per run?

**Mitigations:**
```
Network level:
  AWS Shield Standard — always on, no configuration needed
  AWS Shield Advanced — for production workloads
  Cloud Armor (GCP equivalent)

Pipeline resilience:
  Kafka or SQS as buffer — decouple producers from consumers
  Dead letter queue — failed processing doesn't block pipeline
  Circuit breaker — if downstream unavailable, queue don't drop
  Rate limiting on ingestion — max files per run, max size per file

Service resilience:
  Horizontal pod autoscaling — scale validation/tokenizer pods
  Pod disruption budgets — minimum pods always available
  Health checks + liveness probes — restart unhealthy pods
  Multiple availability zones — no single AZ dependency

Training pipeline specific:
  GPU workers are scarce — protect them from invalid workloads
  Validate all inputs before they reach GPU workers
  Checksum failures rejected before tokenization
  Malformed files go to DLQ — human review, not silent discard
```

---

## E — Elevation of Privilege

**Question:** Can an attacker gain more access than they were granted?

**What to check:**
- Do any services share IAM roles?
- Can a compromised service assume a more privileged role?
- Is iam:PassRole granted to any service?
- Can a low-privilege service reach high-privilege data?
- Can an application role launch new compute resources?
- Are database grants at the correct granularity?

**Mitigations:**
```
IAM role isolation:
  One IAM role per service — never shared
  Job-scoped vended credentials for batch workloads
  STS credentials expire when job completes
  CloudTrail alert fires on unexpected AssumeRole

Explicit deny list on all service roles:
  iam:CreateRole, iam:AttachRolePolicy, iam:PassRole
  ec2:RunInstances, ecs:RunTask, lambda:CreateFunction
  s3:DeleteObject, s3:DeleteBucket
  kms:DeleteKey, kms:ScheduleKeyDeletion

Database least privilege:
  RDS Proxy + IAM database authentication
  No username/password — IAM role grants access
  Schema-level grants — service A cannot read service B's schema
  Column-level grants — sensitive columns restricted to authorized roles
  Row-level security — service only sees rows it created
  No UPDATE or DELETE granted to application roles

Confused deputy prevention:
  External ID in IAM trust policy for all assumed roles
  Per-tenant external IDs — attacker cannot supply another tenant's ID
  External IDs stored in catalog metastore — never returned in API responses
```
