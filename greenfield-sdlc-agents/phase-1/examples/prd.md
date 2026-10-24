<!--
EXAMPLE OUTPUT — illustrative content, continuing the HarvestLink scenario from
Phase 0/1. Not a real product commitment.
-->

# PRD: HarvestLink

| Field | Value |
|---|---|
| Source requirements | `requirements.md` (requirements-2026-08-05-002) |
| Source NFR spec | `nfr-spec.md` (nfr-spec-2026-08-05-002) |
| Source vision | `vision.md` (vision-2026-08-02-002) — Assumptions/Constraints/Risks only |
| Source enterprise security | `kb-L1-enterprise-security` — retention/SLA citations only, carried forward from nfr-spec.md |
| Approval consumed | Priya Ahluwalia, Product Lead, 2026-08-04: "Approved. The facilitation-only structuring is the right first roadmap milestone — please make sure Requirements calls it out as a hard blocker for everything else, not just a risk." |
| Generated | 2026-08-05 |

## ✅ Executive Summary
This PRD composes HarvestLink's 9 functional requirements (FR-001–FR-009)
with their cross-functional constraints into one document, following the
vision Priya Ahluwalia approved as Product Lead on 2026-08-04. The single
biggest constraint shaping the requirement set is that HarvestLink must
never acquire Food Business Operator status — FR-001 and FR-006 exist
specifically to enforce this, and the corresponding facilitation-only
structuring risk (not yet validated with a design-partner local authority
or legal counsel) remains the roadmap's biggest open dependency. Six NFR
boundary conditions are still marked TBD pending stakeholder input — three
others (FR-001's retention period, FR-003's and FR-008's availability SLAs)
are resolved via `kb-L1-enterprise-security`'s existing group policies
rather than invented — and composing this document surfaced two
requirement-coverage gaps — offboarding/suspension and dispute handling —
that need scoping before Phase 2 planning begins.

## Compound Requirements Split
Vision's Roadmap Outline Phase 3 bundles two independently testable
capabilities into one clause: "pilot launch with a capped cohort **and**
transaction limits scaled to compliance-documentation completeness." Split
into **FR-007** (cohort cap) and **FR-005** (completeness-scaled transaction
limits) below, since a system could satisfy one without the other and each
needs its own acceptance test.

## ✅ Assumptions
- **Facilitation-only structure will hold up to validation** (underlies
  FR-001, FR-006): vision.md's Roadmap Outline calls for validating the
  facilitation-only legal/product structure with a design-partner local
  authority or legal counsel, but that validation hasn't happened yet — FR-001
  and FR-006 are written as if the structure will hold.
- **Producers and distributors have sufficient digital access** (underlies
  FR-001, FR-003, FR-004): attestation, dual sign-off, and allergen
  declaration all assume onboarded producers/distributors can reliably
  complete an on-platform digital workflow — not yet confirmed for the
  target user segment (independent/regional producers without an in-house
  compliance team).
- **Buyers will trust the displayed completeness score without independent
  audit** (underlies FR-002): buyer discovery surfaces a compliance-
  documentation completeness score, assuming foodservice buyers will act on
  it directly rather than requiring their own verification before
  onboarding a new supplier.
- **Pilot cohort will be selected and onboarded manually** (underlies
  FR-007): the cohort-eligibility gate assumes product/operations will
  designate eligible producers/distributors by hand, not via a self-service
  application flow.

## ✅ Constraints
- **Must never acquire Food Business Operator status** (constrains FR-001,
  FR-006): vision.md § Regulatory Posture (Red item) — HarvestLink must
  operate strictly as a data/matching and documentation layer; producers
  and distributors remain the FBOs.
- **Traceability records require dual sign-off and immutability**
  (constrains FR-003): vision.md § Regulatory Posture (Amber item) —
  producer and distributor dual sign-off with an immutable audit log is not
  solved by default and must be explicitly designed for.
- **Allergen declarations require producer attestation before finalisation**
  (constrains FR-004): vision.md § Regulatory Posture (Amber item).
- **Pilot phase is scoped to a designated cohort, not general availability**
  (constrains FR-005, FR-007): vision.md § Roadmap Outline, Phase 3 — limits
  scale with completeness data only after pilot, general availability is
  out of scope for this PRD.
- **Data protection remains an ongoing design/monitoring requirement**
  (constrains FR-002, FR-008, FR-009): vision.md § Regulatory Posture (Green
  item) — not a launch blocker, but every component that surfaces or reports
  on user/producer data must keep this in view.

## ✅ Risks
- **Facilitation-only structuring risk** (affects FR-001, FR-006): carried
  forward from vision.md § Open Risks Carried Forward — the entire roadmap
  depends on getting this legal/product structure right first; no fallback
  path is defined yet if a facilitation-only model can't fully avoid FBO
  status in practice.
- **Compliance-documentation-completeness methodology** (affects FR-004,
  FR-005, FR-009): carried forward from vision.md § Open Risks Carried
  Forward — the dual-sign-off and completeness-scoring approach is a design
  commitment, not yet a selected methodology or validated accuracy rate.
- **Competitive response speed** (program-level, not tied to a specific
  requirement): carried forward from vision.md § Open Risks Carried Forward
  — Bidfood or Brakes could bundle a producer-marketplace feature into
  their existing compliance infrastructure before HarvestLink reaches pilot
  launch.

## ✅ Requirements

### FR-001: Facilitation-only role attestation at onboarding
**Statement:** The system shall require every onboarding producer or
distributor to explicitly attest that they, not HarvestLink, hold Food
Business Operator status for any trade facilitated on the platform.
**Traces to:** vision.md § Regulatory Posture (FBO-status mitigation)

**Non-Functional Requirements:**
| Category | Boundary Condition | Source |
|---|---|---|
| Usability | Attestation must be a clear, explicit step, not a buried checkbox | requirements.md § FR-001 |
| Security | Attestation must be tied to an authenticated producer/distributor identity | requirements.md § FR-001 |
| Compliance | Retain 6 years from creation, per Group Records Retention Policy | kb-L1-enterprise-security § ES3 |

### FR-002: Foodservice buyer discovery and matching
**Statement:** The system shall allow foodservice buyers to discover
onboarded producers and distributors by product category, location, and
compliance-documentation completeness score.
**Traces to:** vision.md § Value Proposition

**Non-Functional Requirements:**
| Category | Boundary Condition | Source |
|---|---|---|
| Usability | Search results must show compliance-documentation completeness score alongside each producer | requirements.md § FR-002 |
| Performance | Buyer search/discovery response time — TBD — needs stakeholder input | — |

### FR-003: Dual sign-off traceability record entry
**Statement:** The system shall require both producer and distributor
sign-off before a traceability record is finalised, and shall retain every
finalised record in an immutable, append-only audit log.
**Traces to:** vision.md § Regulatory Posture (traceability mitigation:
"producer and distributor dual sign-off... immutable audit log")

**Non-Functional Requirements:**
| Category | Boundary Condition | Source |
|---|---|---|
| Security | Traceability record must be immutable (append-only) once dual-signed | requirements.md § FR-003 |
| Compliance | Must satisfy Reg. (EC) 178/2002 Art. 18 "one step back, one step forward" | vision.md § Regulatory Posture (Traceability record integrity) |
| Availability | 99.9% uptime — traceability records may be required for active regulatory defence | kb-L1-enterprise-security § ES4 |

### FR-004: Producer-attested allergen declaration workflow
**Statement:** The system shall require producer attestation and sign-off
before an allergen declaration is finalised on-platform.
**Traces to:** vision.md § Regulatory Posture (allergen mitigation:
"producer attestation and sign-off before any declaration is finalised")

**Non-Functional Requirements:**
| Category | Boundary Condition | Source |
|---|---|---|
| Compliance | Must satisfy Natasha's Law / EU FIC Reg. 1169/2011 baseline labelling | vision.md § Regulatory Posture (Allergen declaration liability) |
| Usability | Producer must see a clear pending/finalised state distinction for each declaration | requirements.md § FR-004 |
| Scalability | Expected declaration volume — TBD — needs stakeholder input | — |

### FR-005: Compliance-completeness-scaled transaction limits
**Statement:** The system shall set a producer's maximum transaction value
according to their compliance-documentation completeness score, and
re-evaluate that limit as the score changes.
**Traces to:** vision.md § Roadmap Outline, Phase 3 (split — see Compound
Requirements Split above)

**Non-Functional Requirements:**
| Category | Boundary Condition | Source |
|---|---|---|
| Security | Transaction-value limit must be enforced server-side; not client-configurable | requirements.md § FR-005 |
| Performance | Limit recalculation frequency on completeness-score change — TBD — needs stakeholder input | — |

### FR-006: Facilitation-only transaction routing
**Statement:** The system shall never record HarvestLink as taking
possession, title, or physical custody of food in any transaction; every
trade shall be routed and documented as a direct producer/distributor-to-
buyer arrangement.
**Traces to:** vision.md § Regulatory Posture (FBO-status mitigation:
"HarvestLink never takes physical possession of food")

**Non-Functional Requirements:**
| Category | Boundary Condition | Source |
|---|---|---|
| Compliance | Must never record HarvestLink as taking title/possession of goods in any transaction record | requirements.md § FR-006 |
| Availability | Behaviour if a trade cannot be routed facilitation-only — TBD — needs stakeholder input | — |

### FR-007: Pilot-phase cohort restriction
**Statement:** The system shall restrict onboarding and trading, during the
pilot phase, to a cohort of producers/distributors explicitly designated
eligible by the product/operations team.
**Traces to:** vision.md § Roadmap Outline, Phase 3 (split — see Compound
Requirements Split above)

**Non-Functional Requirements:**
| Category | Boundary Condition | Source |
|---|---|---|
| Usability | Non-cohort users must receive an explicit "not yet available" response, not a silent failure | requirements.md § FR-007 |
| Scalability | Target cohort size for pilot — TBD — needs stakeholder input | — |

### FR-008: Time-to-first-compliant-trade measurement
**Statement:** The system shall record, per producer, the elapsed time from
onboarding start to first fully-documented, compliance-complete trade, and
expose this for reporting against a target of under 14 days.
**Traces to:** vision.md § North-Star Metric(s), metric 1

**Non-Functional Requirements:**
| Category | Boundary Condition | Source |
|---|---|---|
| Performance | P95 time-to-first-compliant-trade < 14 days (onboarding start → first compliance-complete trade) | vision.md § North-Star Metric(s), metric 1 |
| Availability | Best-effort (outbound-only reporting feed, not a compliance record) | kb-L1-enterprise-security § ES4 |

### FR-009: Compliance-documentation-completeness measurement
**Statement:** The system shall record, per producer, a compliance-
documentation completeness score at first trade, and expose this for
reporting against a target of at least 95%.
**Traces to:** vision.md § North-Star Metric(s), metric 2

**Non-Functional Requirements:**
| Category | Boundary Condition | Source |
|---|---|---|
| Performance | Reported compliance-documentation completeness score ≥ 95% at first trade | vision.md § North-Star Metric(s), metric 2 |
| Compliance | Whether specific buyer names may appear in completeness reporting — TBD — needs stakeholder input | — |

## ✅ Open Questions
- FR-002 (Performance): Buyer search/discovery response time
- FR-004 (Scalability): Expected declaration volume
- FR-005 (Performance): Limit recalculation frequency on completeness-score change
- FR-006 (Availability): Behaviour if a trade cannot be routed facilitation-only
- FR-007 (Scalability): Target cohort size for pilot
- FR-009 (Compliance): Whether specific buyer names may appear in completeness reporting

Resolved since the previous revision — no longer open: FR-001's attestation
retention period, FR-003's and FR-008's availability SLAs, all three via
`kb-L1-enterprise-security` (see their NFR tables above). Not invented
values — an existing group policy already answered these once an enterprise
security KB existed to check.
- **Coverage gap:** no FR covers producer/distributor offboarding or
  suspension (e.g. on repeated compliance failures) — only onboarding
  (FR-001) and ongoing trading are specified. Surfaced by reading FR-001
  through FR-009 together; not visible from requirements.md or nfr-spec.md
  in isolation, since neither document prompts a reviewer to check for a
  missing lifecycle state.
- **Coverage gap:** no FR covers dispute handling when a buyer contests a
  delivered trade's compliance documentation after FR-003's dual sign-off —
  the traceability record is immutable once signed, but what happens when a
  buyer disputes it isn't specified anywhere in the requirement set.

---
*Generated by `L1-requirements-prd-composer` · execution_id: `exec-2d7c94ab` · workflow_execution_id: `wf-6d3f8b04`*
