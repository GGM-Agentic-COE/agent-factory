<!--
TEMPLATE: impact-assessment.md
Produced by: L1-planning-impact-assessor (Core)
Evaluated by: L1-planning-impact-assessor-evaluator
Consumes: prd.md (composes requirements.md + nfr-spec.md — see
          prd.template.md) + THREE existing-estate sources, each a
          different grain, all checked, none skipped:
          1. enterprise-data/{org}-service-catalog.json (SERVICE grain —
             "does a capability like this already exist, who owns it" —
             avoid proposing a duplicate build)
          2. enterprise-data/{org}-cmdb-export.json (CONFIGURATION-ITEM
             grain — "what specific technical asset/integration touchpoint
             exists, and what does it currently connect to")
          3. kb-L1-enterprise-architecture (NARRATIVE grain — "why does
             this component touch or not touch that system, what's the
             governance rule" — the KB's EA3 table should already agree
             with what the CMDB/catalog show; if it doesn't, the KB is
             stale and that mismatch is itself a finding, not something to
             silently reconcile by picking one source over the other)
          Service catalog/CMDB may be genuinely empty for a product built
          with no parent enterprise at all — degrade gracefully in that
          case, don't error — but "greenfield product" is NOT the same
          claim as "no parent enterprise"; check for real export files
          before asserting either.
Consumed by: L1-planning-dependency-mapper, L1-planning-backlog-prioritizer (Phase 2)

Required sections marked ✅. A genuinely empty CMDB/catalog (no parent
enterprise at all) still gets an explicit "No existing internal systems
affected" — but do NOT default to that when a parent enterprise exists:
check every service in the catalog (capability duplication) AND every CI in
the CMDB relevant to a proposed component (technical touch) and state
EXPLICITLY, per system, whether it's touched and how — a system correctly
NOT touched by architecture decision (e.g. "no ERP integration — HarvestLink
must never take title/possession of goods") is a finding worth stating, not
the same as never having checked. Note the distinction throughout: "no
existing INTERNAL systems affected" is not the same claim as "no external
dependencies" — a regulated third-party partner, platform provider, or data
vendor is a real dependency even though it isn't one of the org's own
existing systems.
-->

# Impact Assessment: {{product_name}}

| Field | Value |
|---|---|
| Source PRD | `prd.md` ({{prd_artifact_id}}) |
| Service catalog | {{"empty — no parent enterprise" \| "enterprise-data/{org}-service-catalog.json, N services checked"}} |
| CMDB export | {{"empty — no parent enterprise" \| "enterprise-data/{org}-cmdb-export.json, N of M CIs relevant, checked"}} |
| Generated | {{yyyy-mm-dd}} |

## ✅ Existing-System Impact

**Capability check (service catalog, service grain):** {{state explicitly
whether any existing service already provides a similar capability to what
this product proposes — a real duplicate-build risk if missed, not a
formality. Name the closest existing service even when it's NOT a match,
and say specifically why it doesn't cover the same ground (different
operating model, different user population, etc.) — "no similar service
found" with nothing checked against is not the same claim as "checked X and
Y, neither is a match."}}

**Technical touch check (CMDB, configuration-item grain):** {{one row per
CI in the CMDB relevant to a proposed component — "not touched" is a real,
stated finding, not an omission. If CMDB is genuinely empty (no parent
enterprise), write "No existing internal systems affected — net-new build,
no parent enterprise" instead of this table.}}
| Existing System (CI) | Touched? | How / Why Not | Component(s) |
|---|---|---|---|
| {{CI name}} | {{Yes \| No — by architecture decision}} | {{the specific integration, or the specific reason it's excluded — cross-check against kb-L1-enterprise-architecture's EA3 table; a mismatch between what the CMDB shows and what the KB claims is itself a finding}} | {{FR-NNN component(s), or "—"}} |

## ✅ Components Identified
| Requirement | Component (new/existing) | Blast Radius | Rationale |
|---|---|---|---|
| {{FR-NNN}} | {{component name}} ({{new \| existing}}) | {{Low \| Medium \| High}} | {{why this radius, e.g. "on critical path" or "isolated, independently deployable"}} |

{{repeat one row per requirement — every FR in prd.md must appear
here at least once; a requirement with no identifiable component is itself a
finding, not an omission}}

## ✅ External Dependencies
{{list any third-party system, partner, or vendor a component depends on that
is NOT one of the org's existing internal systems but is still a real
dependency — e.g. a regulated partner institution, platform provider, or
data vendor. Include a NEWLY discovered need surfaced by checking the
Existing-System Impact table above (e.g. an existing identity provider that
turns out not to cover this product's user population, per
kb-L1-enterprise-security's identity boundary) — that is exactly this
section's job to catch, not something to leave implicit.}}

---
*Generated by `L1-planning-impact-assessor` · execution_id: `{{execution_id}}` · workflow_execution_id: `{{workflow_execution_id}}`*
