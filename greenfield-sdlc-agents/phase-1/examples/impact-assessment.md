<!--
EXAMPLE OUTPUT — illustrative content, continuing the HarvestLink scenario.
Not a real product commitment.
-->

# Impact Assessment: HarvestLink

| Field | Value |
|---|---|
| Source PRD | `prd.md` (prd-2026-08-05-002) |
| Service catalog | `enterprise-data/thornbury-service-catalog.json`, 7 services checked |
| CMDB export | `enterprise-data/thornbury-cmdb-export.json`, 6 of 9 CIs relevant, checked |
| Generated | 2026-08-05 |

## ✅ Existing-System Impact

**Capability check (service catalog, service grain):** the closest existing
service to HarvestLink's producer marketplace is `SVC-CUST-001` (Customer &
Sales — the legacy wholesale CRM). It is NOT a match: SVC-CUST-001 is
account-managed direct sales by Thornbury's own sales team, not a
self-service marketplace where producers/distributors and foodservice
buyers discover and transact with each other directly. No existing service
in the catalog provides compliance-documentation tooling (HACCP/allergen/
traceability) either — `SVC-COMP-001` is a manual document store for the
wholesale side's own supplier certs, not a producer-facing attestation
workflow. Confirmed via `enterprise-data/thornbury-service-catalog.json`,
not assumed: no duplicate-build risk found.

**Technical touch check (CMDB, configuration-item grain):** HarvestLink is
a new product built WITHIN an already-established enterprise (Thornbury
Foods Group), not a standalone greenfield company — every CI in
`enterprise-data/thornbury-cmdb-export.json` relevant to a proposed
component was checked explicitly against `kb-L1-enterprise-architecture`'s
EA3 table, not assumed clear; both sources agree, no mismatch found:

| Existing System (CI) | Touched? | How / Why Not | Component(s) |
|---|---|---|---|
| Supplier Master Data System (SMDS) | Yes — read-only check | Check for an existing wholesale supplier/distributor record to avoid duplicate producer identity; HarvestLink's own records are not written back to SMDS | FR-001 (onboarding-attestation-service) |
| Group ERP (SAP) | No — by architecture decision | HarvestLink must never take title/possession of goods (vision.md § Regulatory Posture); an ERP posting would imply HarvestLink is a transacting party | FR-006 (facilitation-routing-engine) — explicitly excluded |
| Compliance Document Store | No — by architecture decision | No API exists; traceability/allergen services are built standalone, not as an extension of this legacy store | FR-003, FR-004 — explicitly excluded |
| Employee Identity (Azure AD) | No — out of scope by design | Employee-only; has no external-party tier (kb-L1-enterprise-security ES1) — see External Dependencies below for the resulting new need | — |
| Data Warehouse (Snowflake) | Yes — outbound feed only | Aggregate, non-PII metrics feed the group DW per group reporting policy; no read dependency back | FR-008, FR-009 (metrics-reporting-pipeline) |
| API Gateway (Kong) | Yes — required integration pattern | Any HarvestLink service exposed beyond its own boundary must publish through the Gateway, not point-to-point | FR-002 (buyer-discovery-matching-service), FR-001 (onboarding-attestation-service) |

This is a materially different finding from "no existing internal systems
affected" — three systems are genuinely touched (one read-only, one
outbound-only, one as a mandatory integration pattern), and two are
explicitly, deliberately NOT touched by architecture decision rather than
by oversight. Neither claim is the same as "no external dependencies" — see
External Dependencies below.

## ✅ Components Identified
| Requirement | Component (new/existing) | Blast Radius | Rationale |
|---|---|---|---|
| FR-001 | onboarding-attestation-service (new) | Low | Isolated onboarding step; no other component depends on its internal implementation, only its attestation record |
| FR-002 | buyer-discovery-matching-service (new) | Medium | Not on the critical trade-routing path, but core to the value proposition's visibility promise |
| FR-003 | traceability-record-service (new) | High | Legal/compliance-critical — a trade cannot be routed if this component is unavailable |
| FR-004 | allergen-declaration-service (new) | High | Compliance-critical for the same reason as traceability; also feeds completeness scoring |
| FR-005 | compliance-completeness-limit-engine (new) | Medium | Not independently deployable — depends on allergen-declaration-service's completeness contribution |
| FR-006 | facilitation-routing-engine (new) | High | Core critical-path service — every trade-related component either feeds it or is fed by it; the entire legal structure depends on this working correctly |
| FR-007 | cohort-eligibility-gating-service (new) | Low | Isolated gating layer; can be disabled post-pilot without affecting other components |
| FR-008 | metrics-reporting-pipeline (new) | Medium | Not on the critical path of a trade itself, but required to evidence the north-star metric |
| FR-009 | metrics-reporting-pipeline (new — same component as FR-008) | Medium | Same component as FR-008; completeness-score and time-to-first-trade reporting share one pipeline |

## ✅ External Dependencies
- **Legal/regulatory design partner** (local authority or legal counsel) —
  required to validate the facilitation-only structure underpinning
  `facilitation-routing-engine` (FR-006) and the overall FBO-status
  mitigation named in `vision.md` § Regulatory Posture. Not an internal
  system, but a real prerequisite — no validated structure means this
  component cannot be built with confidence it actually avoids FBO status.
- **Compliance-documentation-completeness methodology** — required for
  `allergen-declaration-service` (FR-004) and
  `compliance-completeness-limit-engine` (FR-005). Not yet selected (see
  `vision.md` § Open Risks Carried Forward, "Compliance-documentation-
  completeness methodology").
- **External identity provider** — a NEW need surfaced by this assessment,
  not visible at vision/requirements stage: Thornbury Foods Group's
  existing Azure AD covers employees only (kb-L1-enterprise-security ES1);
  producers, distributors, and buyers have no group-provided identity tier.
  Required for `onboarding-attestation-service` (FR-001) and every other
  component that authenticates an external party. Not yet selected — this
  is a genuine gap the Existing-System Impact check above exists to catch,
  and one the vision/requirements stages had no way to know about before an
  enterprise architecture landscape was checked.

---
*Generated by `L1-planning-impact-assessor` · execution_id: `exec-71e0a9c4` · workflow_execution_id: `wf-6d3f8b04`*
