# Six Security Lenses

Use as a final checklist after STRIDE. Each lens catches a class of findings
that STRIDE may miss when applied only at explicit trust boundaries.

---

## Lens 1 — Threat Model Gaps

**Question:** What attacks aren't covered by the design?

```
Ask:
  What is the worst-case scenario if this component is compromised?
  What is the blast radius?
  How long would an attacker have access before detection?
  Is there a recovery path that doesn't bypass security controls?

Common gaps:
  No mention of supply chain attacks (dependencies, build pipeline)
  No mention of insider threat
  No mention of credential theft vs credential misuse
  Multi-week jobs with permanent credentials → long blast radius window
  Single shared role → compromise of one worker = compromise of all
```

---

## Lens 2 — Trust Boundary Violations

**Question:** Does every trust boundary crossing have authentication?

```
Ask:
  Is there any implicit trust not documented in the design?
  Can a compromised component reach components in other trust zones?
  Is there a path from a low-trust zone to a high-trust zone?

Common violations:
  Service accepts requests from any source (no authentication)
  Public IP on internal service
  No network policy — any pod can reach any other pod
  Database accessible from public internet
  Shared role allows lateral movement between services
```

---

## Lens 3 — Authentication and Credential Hygiene

**Question:** Are credentials handled correctly throughout the system?

```
Ask:
  Are any credentials long-lived (static keys, annual rotation)?
  Where are secrets stored? Code? Config files? Environment variables?
  Is there mutual authentication or only one-way?
  Can credentials be rotated without downtime?
  Are credentials scoped to minimum required access?

Red flags — immediate Critical findings:
  AWS access keys in environment variables
  Database credentials in config files checked into source control
  Credentials in public GitHub repository
  Annual rotation on any credential (should be 90 days or less)
  Shared username/password for database access
  Same IAM role used by multiple services or multiple jobs
```

---

## Lens 4 — Audit Trail Completeness

**Question:** Can you reconstruct exactly what happened after an incident?

```
Ask:
  What actions are logged?
  What actions are NOT logged? (this is the more important question)
  Is the audit trail immutable — can it be deleted or modified?
  Does the audit record capture service identity, not just user identity?
  Is there correlation across services (requestId, traceId)?
  How long are audit records retained?

Common gaps:
  S3 access logging not enabled
  Database query logging not enabled
  Ingestion service logs what was processed but not what was rejected
  No correlation between catalog requests and storage access logs
  Audit records stored in the same database as operational data
  Audit records deletable by the services that write them

What legally defensible audit requires:
  Immutable store (WORM / Object Lock COMPLIANCE mode)
  Hash chain — each record contains hash of previous record
  7 year retention minimum
  Service identity captured (SPIRE SVID or IAM role ARN)
  Covers both allows AND denies
  Nightly verification job checks chain integrity
```

---

## Lens 5 — Least Privilege Violations

**Question:** Does any component have more access than it needs to function?

```
Ask:
  Can this service access data from other services?
  Can this role access resources from other tenants?
  Can this role perform destructive operations (delete, terminate)?
  Can this role escalate its own privileges (iam:PassRole)?
  Is access scoped to the minimum required prefix/resource?

Common violations:
  Shared IAM role across all GPU workers in all jobs
  Tokenizer uses same role as training cluster
  Training cluster can write to training bucket (should be read-only)
  Application role can call ec2:RunInstances (cost escalation)
  Application role has iam:PassRole (privilege escalation path)
  Database role can access all schemas (should be schema-scoped)
  S3 role can list all buckets (should be prefix-scoped)

The explicit deny list every application role needs:
  iam:CreateRole, iam:AttachRolePolicy, iam:PassRole
  ec2:RunInstances, ecs:RunTask, lambda:CreateFunction
  s3:DeleteObject, s3:PutBucketPolicy
  kms:DeleteKey, kms:ScheduleKeyDeletion
```

---

## Lens 6 — Failure Mode Safety

**Question:** Does the system fail closed (safe) or fail open (dangerous)?

```
Ask:
  What happens when the auth service is unavailable?
  What happens when OPA / the policy engine is down?
  What happens when the validation service is unavailable?
  Does a partial failure expose data that should be protected?
  Is there a recovery path that doesn't bypass controls?

Fail open examples (dangerous):
  Auth service down → requests pass through unauthenticated
  Policy engine down → all requests allowed
  Validation service down → data passes to training without validation
  Circuit breaker disabled → requests pile up and timeout = data loss

Fail closed examples (safe):
  Auth service down → deny all requests, page on-call
  OPA down → deny sensitive access, allow non-sensitive, alert
  Validation service down → queue to Kafka, do not drop, do not pass
  Checksum mismatch → reject file, alert, do not train on it

The rule: when in doubt, deny and alert.
Never allow access when the authorization system is unavailable.
```
