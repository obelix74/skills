---
name: threat-modeling
description: >
  Security threat modeling coach and reviewer using STRIDE methodology and data flow diagrams.
  Use this skill whenever the user wants to:
  - Review a system design document for security issues
  - Perform a threat model on any architecture, pipeline, or service
  - Prepare for a security design review interview
  - Apply STRIDE to identify threats at trust boundaries
  - Find security gaps in authentication, authorization, audit trails, or data flows
  - Practice identifying Spoofing, Tampering, Repudiation, Information Disclosure, DoS, or Elevation of Privilege
  - Review cloud infrastructure (AWS, GCP, Azure) for credential hygiene, IAM scope, and network isolation
  - Analyze a design document and prioritize findings as Critical, High, Medium, or Low
  Trigger this skill even when the user casually mentions "security review", "threat model",
  "find the security issues", "review this design", or "what could go wrong with this architecture".
---

# Threat Modeling Skill

A structured security threat modeling framework using STRIDE, data flow diagrams, and
the six security lenses. Guides the user through a complete security review of any
system design document or architecture.

---

## Overview

Security threat modeling has five steps:

```
1. Identify actors and data flows
2. Draw the DFD with trust boundaries
3. Apply STRIDE at each trust boundary
4. Prioritize findings by impact and likelihood
5. Suggest concrete mitigations
```

Read `references/stride.md` for the complete STRIDE reference.
Read `references/lenses.md` for the six security lenses checklist.
Read `references/cloud-patterns.md` for common cloud infrastructure findings.

---

## Step 1 — Clarifying Questions

Before reviewing any design, ask targeted questions. Do not skip this step.

**Always ask:**
```
1. Is there a VPC / network boundary between services?
2. How do services authenticate to each other?
3. Where are credentials stored?
4. Is there an audit log for data access?
5. Are IAM roles scoped per service or shared?
6. Is data encrypted at rest and in transit?
7. What happens when a component fails — fail open or fail closed?
8. Who are the principals and what trust level does each carry?
```

**For cloud infrastructure specifically:**
```
9.  Are credentials long-lived (static keys) or short-lived (STS)?
10. Are S3 buckets access-logged?
11. Is there a VPC endpoint for S3 and KMS — or do they route via public internet?
12. Can IAM roles be scoped per job or are they permanent shared roles?
13. Is database access via IAM auth (RDS Proxy) or username/password?
14. Are encryption keys rotated and on what schedule?
```

---

## Step 2 — Draw the DFD

Identify and label these four elements before applying STRIDE:

```
External entities  → actors outside your control (users, external APIs, vendors)
Processes          → services that transform or route data
Data stores        → databases, caches, queues, object storage
Trust boundaries   → dashed lines where privilege level changes
```

**Trust boundary examples:**
```
Public internet → internal network
Unauthenticated zone → authenticated zone
Low-privilege service → high-privilege service
External vendor → internal pipeline
One tenant → another tenant (multi-tenancy boundary)
```

Every arrow that crosses a trust boundary is a potential attack surface.
Apply STRIDE at each crossing.

---

## Step 3 — Apply STRIDE

Apply all six threats at every trust boundary. Read `references/stride.md` for
the complete question, check, and mitigation for each threat.

**Quick reference — one question per threat:**
```
S — Spoofing:              Can an attacker impersonate a legitimate principal?
T — Tampering:             Can data be modified without detection?
R — Repudiation:           Can an actor deny their actions?
I — Information Disclosure: Can unauthorized parties read sensitive data?
D — Denial of Service:     Can an attacker prevent legitimate use?
E — Elevation of Privilege: Can an attacker gain more access than allowed?
```

**The two most commonly missed threats:**

Tampering — always ask:
*"Can data be modified in transit or at rest between these two components
without detection? Is there a checksum or signature chain?"*

Information Disclosure — always ask:
*"What credentials exist at this boundary and where are they stored?
What can this component reach that it shouldn't be able to reach?"*

---

## Step 4 — Prioritize Findings

```
Critical:  High impact + likely exploit
           → Must fix before shipping
           Examples: unauthenticated endpoints, credentials in public repos,
                     shared IAM roles, missing encryption on sensitive data

High:      High impact + requires sophistication
           → Fix in next iteration
           Examples: missing audit trail, overly broad IAM scope,
                     no egress policy, annual credential rotation

Medium:    Lower impact or low likelihood
           → Document and mitigate
           Examples: defense in depth gaps, monitoring gaps

Low:       Theoretical, minimal real-world impact
           → Accept with documentation
```

---

## Step 5 — Concrete Mitigations

Every finding must have a specific fix. Never say "this is bad" without proposing
the exact mitigation.

**Common mitigation patterns — read `references/cloud-patterns.md` for full details:**

```
Spoofing:
  Service-to-service  → SPIFFE/SPIRE SVIDs + mutual TLS
  External sources    → checksum verification against known manifests
  Static credentials  → EC2 instance profile / Workload Identity / Pod Identity

Tampering:
  Data in transit     → TLS + message signing
  Data at rest        → SHA-256 checksum chain stored separately from data
  Database records    → append-only tables, no UPDATE or DELETE

Repudiation:
  All actions         → structured audit record: who, what resource,
                        what action, timestamp, result
  Storage             → WORM append-only store, separate from operational data
  Retention           → 7 years minimum for legal defensibility

Information Disclosure:
  Static credentials  → replace with short-lived STS / instance profile
  Credentials in repo → treat repo as compromised, rotate all secrets immediately
  Overly broad IAM    → scope to minimum prefix, explicit deny on delete
  Network egress      → allowlist-only NetworkPolicy + VPC endpoints

Denial of Service:
  Network level       → AWS Shield / Cloud Armor
  Pipeline disruption → rate limiting, circuit breakers, DLQ
  Single chokepoint   → horizontal pod autoscaling, queue buffering

Elevation of Privilege:
  Shared roles        → per-service roles, job-scoped vended credentials
  iam:PassRole        → explicit deny on privilege escalation APIs
  Overpermissioned    → explicit deny list: ec2:*, iam:CreateRole, etc.
  Database access     → RDS Proxy + IAM auth, schema-level grants only
```

---

## Interview Mode

When the user is preparing for a security design review interview, follow this structure:

**Opening statement template:**
*"Before I walk through my findings, let me confirm I understood the system
correctly — [summarize actors, data flows, trust boundaries]. Does that match
your intent?"*

**Walk findings in priority order:**
1. Name the most critical finding first and its blast radius
2. State the STRIDE category
3. Propose a concrete mitigation
4. Move to next finding

**The treat-as-already-compromised framing:**
When credentials are exposed (public repo, environment variables, shared config):
*"I would treat this as already compromised — rotate immediately, then fix the
root cause. Do not assume the window of exposure was zero."*

**The checksum chain pattern:**
For any multi-stage data pipeline, establish end-to-end data provenance:
```
Ingestion:   SHA-256 on input files → stored in audit log
Processing:  verify input checksum → store output checksum
Consumption: verify checksum before processing
```
If this chain is intact, you can prove what the system processed. This is legally
defensible data provenance.

---

## Confused Deputy Pattern

When reviewing multi-tenant systems with credential vending:

```
The confused deputy problem:
  Attacker is Tenant A
  Attacker knows Tenant B's role ARN
  Attacker asks the vending service to assume Tenant B's role
  Vending service is trusted by AWS → AssumeRole succeeds
  Attacker gets Tenant B's credentials

Prevention — external ID:
  Tenant B's IAM trust policy requires sts:ExternalId = {secret}
  Attacker doesn't know the external ID
  AssumeRole call is rejected by STS

STRIDE mapping:
  Root cause:     Spoofing (attacker impersonates tenant)
  Consequence 1:  Elevation of Privilege (attacker gains tenant's permissions)
  Consequence 2:  Information Disclosure (attacker reads tenant's data)
  External ID cuts the chain at the root — stops spoofing,
  prevents both downstream consequences
```

---

## Six Security Lenses Checklist

Use as a final check after STRIDE. Read `references/lenses.md` for full details.

```
□ Threat model gaps        — what attacks aren't covered?
□ Trust boundary violations — does every crossing have authentication?
□ Credential hygiene        — are credentials short-lived and rotated?
□ Audit trail completeness  — can you reconstruct what happened?
□ Least privilege           — does any component have excess access?
□ Failure mode safety       — does the system fail closed not open?
```
