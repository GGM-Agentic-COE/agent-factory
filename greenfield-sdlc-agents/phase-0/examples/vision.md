<!--
EXAMPLE OUTPUT — illustrative content generated to demonstrate Phase 0's document
chain end-to-end. Not a real product commitment. See idea-brief.md,
market-analysis.md, and regulatory-feasibility.md for the inputs this document
reconciles.
-->

# Vision: HarvestLink

| Field | Value |
|---|---|
| Vision ID | vision-2026-08-02-002 |
| Status | Approved (see Approval below) |
| Generated | 2026-08-02 |
| Viability Score | 7.4/10 — PASS (`qg-L1-viability-score`) |
| Inputs | `idea-brief.md`, `market-analysis.md`, `regulatory-feasibility.md` |

## ✅ Executive Summary
HarvestLink is a compliance-and-discovery platform connecting independent UK
food producers and distributors directly to foodservice buyers, who are
currently underserved by large wholesalers that offer scale but no
direct-producer access, and squeezed by compliance burdens they can't afford
alone. No competitor reviewed combines producer-friendly market access with
built-in HACCP/traceability/allergen compliance tooling, and the regulatory
path is feasible by design as long as HarvestLink remains a facilitation-only
platform rather than taking on Food Business Operator status. The single
biggest open risk is that the entire roadmap depends on structuring the
platform's legal and product model as facilitation-only from day one;
retrofitting this later would be far harder than designing for it up front.

## ✅ Problem
Independent and regional UK food producers and distributors are being
squeezed by consolidation pressure from large foodservice wholesalers, and
lack the compliance infrastructure — HACCP documentation, allergen
declarations, cold-chain traceability records — that foodservice buyers
increasingly require before awarding a contract. This locks smaller
producers out of contracts they could otherwise win on product quality
alone.

## ✅ Target Users
Independent and regional UK food producers/distributors without an in-house
compliance team, and foodservice (HORECA) buyers who want traceable,
locally-sourced ingredients but need documented compliance evidence before
onboarding a new supplier.

## ✅ Value Proposition
HarvestLink gives independent food producers and distributors an
out-of-the-box compliance and traceability layer — HACCP records, allergen
declarations, cold-chain temperature logging — plus direct discovery by
foodservice buyers, so they can win contracts that currently require
wholesaler-grade compliance evidence, without needing an in-house compliance
team.

## Market Context
No reviewed competitor — Bidfood, Brakes, Booker, or the independent/
regional distributor long tail — combines producer-friendly market access
with built-in compliance tooling. That combination is the open gap
HarvestLink targets. The clearest threat is that Bidfood or Brakes bundles a
producer-marketplace feature into their existing compliance infrastructure
before HarvestLink reaches scale, which makes time-to-market a genuine
priority, not just a nice-to-have.

## Regulatory Posture
**Overall status:** Amber — feasible, no unmitigated blocker.
- Food Business Operator status (Red) → operate strictly as a data/matching
  and documentation layer; producers and distributors remain the FBOs,
  HarvestLink never takes physical possession of food.
- Traceability record integrity (Amber) → require producer and distributor
  dual sign-off with an immutable audit log; not solved by default.
- Allergen declaration liability (Amber) → require producer attestation and
  sign-off before any declaration is finalised on-platform.
- Data protection (Green) → carried forward as an ongoing design/monitoring
  requirement, not a launch blocker.

## ✅ North-Star Metric(s)
- Time from producer onboarding to first fully-documented, compliance-complete
  trade — target under 14 days
- Compliance-documentation completeness score at first trade — target at
  least 95%

## ✅ Roadmap Outline (phase-level, not sprint-level)
1. **Structure the platform as facilitation-only** (legal/product design) and
   validate this structure with a design-partner local authority or legal
   counsel — resolves the Food-Business-Operator-status gap; nothing in
   Phase 2 onward can proceed without this being right from the start.
2. **Design and validate the dual-sign-off traceability and allergen-
   declaration workflows** — the Amber mitigations must be built and tested
   with real producer/distributor data before onboarding opens beyond a
   pilot cohort.
3. **Pilot launch with a capped cohort of producers and transaction limits
   scaled to compliance-documentation completeness**, then widen limits as
   completeness data accumulates.

## ✅ Open Risks Carried Forward
- **Facilitation-only structuring risk** (from Red regulatory item): the
  entire roadmap depends on getting this legal/product structure right
  first; no fallback path is defined yet if a facilitation-only model can't
  fully avoid FBO status in practice.
- **Compliance-documentation-completeness methodology** (from Amber
  regulatory items): the dual-sign-off and completeness-scoring approach is
  a design commitment, not yet a selected methodology or validated accuracy
  rate.
- **Competitive response speed** (from market analysis Threats): Bidfood or
  Brakes could bundle a producer-marketplace feature into their existing
  compliance infrastructure before HarvestLink reaches pilot launch.

## Approval
- [x] Product Lead sign-off — **required before Phase 1 (Requirements) may start**
- **Approved by:** Priya Ahluwalia, Product Lead
- **Date:** 2026-08-04
- **Comment:** "Approved. The facilitation-only structuring is the right
  first roadmap milestone — please make sure Requirements calls it out as a
  hard blocker for everything else, not just a risk."
- This comment is consumed directly by `L1-requirements-elicitor` as a
  required input — see `requirements.md`.

---
*Generated by `L1-vision-statement-generator` · execution_id: `exec-2e91c7d8` · workflow_execution_id: `wf-a17c5e92`*
*Published by `L1-confluence-publisher` to: confluence://PRODUCT/HarvestLink-Vision (published 2026-08-04, after Product Lead approval recorded above)*
