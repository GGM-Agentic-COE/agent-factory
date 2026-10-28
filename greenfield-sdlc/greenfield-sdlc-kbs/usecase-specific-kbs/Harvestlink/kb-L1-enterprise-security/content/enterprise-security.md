<!--
kb-L1-enterprise-security · content · enterprise-security.md
Layer: L1 (enterprise-wide, cross-phase — NOT domain-specific). Illustrative
content for the reference scenario: Thornbury Foods Group's established
security standards, which HarvestLink (a new digital product built within
the group) must satisfy. Not a real company; not a real product
commitment. Cross-references kb-L1-enterprise-architecture for system
landscape rather than duplicating it. Grounds L1-requirements-nfr-classifier
(Security/Compliance/Availability categories) and L1-planning-impact-assessor.
-->

# Thornbury Foods Group — Enterprise Security Standards

## ES1: Identity & Access Management
- Employees: Azure AD group SSO — MUST NOT be extended to external parties (kb-L1-enterprise-architecture EA2)
- External parties (producers, distributors, foodservice buyers): MUST use a separate, group-approved external identity provider — internal AD has no external-party tier
- Every external-facing action MUST be tied to an authenticated, non-shared identity — no anonymous or shared-credential access to compliance-relevant workflows
- Server-side enforcement MUST NOT be bypassable by altering a client-side request (applies to any limit, gate, or attestation check)

## ES2: Data Classification
| Class | Definition | Example (HarvestLink context) |
|---|---|---|
| Public | No restriction | Marketing content, public product category listings |
| Internal | Group-internal, low sensitivity | Aggregate, non-PII platform metrics |
| Confidential | Sensitive to a specific party | Producer compliance documents, allergen declarations, individual completeness scores |
| Restricted | Legally or financially sensitive | Any data touching Group ERP/financial ledger (kb-L1-enterprise-architecture EA3 — HarvestLink does not integrate here by design) |

## ES3: Data Retention & Erasure (UK GDPR / Records Retention)
- Trade/compliance-relevant records (attestations, traceability sign-offs, allergen declarations): retain **6 years** from creation, per Group Records Retention Policy aligned to HMRC/Companies Act business-record guidance
- Right-to-erasure (UK GDPR Art. 17) requests: MUST be honoured for personal data NOT required for the 6-year compliance-retention obligation above — the two are not the same population of data and must be handled distinctly, never a blanket "delete everything" or "retain everything"
- Retention period MUST be stated per record TYPE, not assumed uniform across all HarvestLink data

## ES4: Audit Logging & Availability Tiering (for NEW systems, not the group's existing Tier table)
- Any new system storing a legally-relevant audit/compliance record (e.g. an immutable traceability sign-off) MUST target minimum **99.5% uptime** (group Tier 2 equivalent)
- If the record could be required for active regulatory defence (e.g. an FBO-status dispute), target **99.9%** (group Tier 1 equivalent)
- Reporting/analytics pipelines feeding the group Data Warehouse (kb-L1-enterprise-architecture EA3, outbound-only): **best-effort / group Tier 3 equivalent** is acceptable unless the specific metric is regulator-facing
- A new system's tier MUST be explicitly stated, not silently inherited from an unrelated existing system's SLA

## ES5: Secure SDLC — Pre-Launch Requirements (New External-Facing Digital Products)
- Secrets MUST be managed via the group secrets vault — never hardcoded or committed
- Dependency/vulnerability scanning MUST run in CI before any release to an external-facing environment
- A penetration test MUST be completed and remediated before first external-user onboarding — not before internal/staging use
- Any new external identity integration (ES1) MUST be reviewed by the security team before go-live

## ES6: Incident Response & Breach Notification
- A personal-data breach MUST be reported to the ICO within **72 hours** of the group becoming aware, per UK GDPR Art. 33
- Affected individuals MUST be notified without undue delay where the breach poses a high risk to their rights and freedoms (UK GDPR Art. 34)
- Any new external-facing system (HarvestLink included) MUST have a named incident-response owner before launch — not assigned retroactively after a first incident

## ES7: Third-Party & External-User Risk
- Onboarding an external party (producer, distributor, buyer) as a platform user requires a lightweight identity/eligibility check before granting write access to compliance-relevant workflows — this is a security requirement independently of any food-regulatory attestation requirement (kb-L2-domain-regulatory), the two obligations happen to point at the same onboarding step but come from different policy sources
- A vetting check MUST be logged (who, when, what was checked) even when the outcome is "approved" — an approval with no record is indistinguishable from no check having happened

## ES8: Glossary
- PII — Personally Identifiable Information
- DPIA — Data Protection Impact Assessment (required for high-risk processing under UK GDPR Art. 35)
- ICO — Information Commissioner's Office (UK data protection regulator)
- Server-side enforced — a rule the client cannot bypass by altering its own request

---
*Last reviewed: 2026-08-07 · Review cadence: quarterly (regulatory guidance
and incident-response practice evolve faster than core identity/data
classification structure).*
