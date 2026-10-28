# gr-L1-impact-assessment-quality-gate

**Layer:** L1
**Triggers on:** post_execution (output rail) — fires when `L1-planning-impact-assessor-evaluator` concludes
**On fail:** Retry once, then escalate to HITL
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid mode
**Applies to:** `L1-planning-impact-assessor-evaluator` only (`configured_agents`)

## What does it do?

`L1-planning-impact-assessor-evaluator` independently re-runs
`L1-planning-impact-assessor`'s capability check and technical-touch check
against the same `service_catalog`/`cmdb_export` exports and
`kb-L1-enterprise-architecture`, and fixes what it can. This guardrail
fires at that point but validates a different thing: the **resultant**
`L1-planning-impact-assessor` output — its own `items`, with the
evaluator's `fixes_applied` resolved in — is what actually flows to
`L1-planning-dependency-mapper` and `L1-planning-backlog-prioritizer`.
This gate checks THAT content:

1. **Output schema validation** — does the resultant content conform to
   `L1-planning-impact-assessor/output_schema.json` (not the evaluator's
   own output shape)?
2. **Rubric adherence** — does the resultant content actually satisfy
   `L1-planning-impact-assessor/evaluation.md`'s five Quality Gates:
   capability check genuinely run (not vacuous), every relevant CMDB CI
   checked and cross-referenced (not skipped, not silently reconciled),
   every FR mapped to a component with a blast-radius rationale, every
   newly-surfaced dependency captured, and a genuinely empty
   catalog/CMDB stated explicitly as such?

This is NOT a check on the evaluator's own scores/findings/final_decision
— it's an independent re-derivation of both checks, run against what
actually ships downstream.

**Why it matters:** an evaluator reporting `fixed_and_approved` is a
claim, not a guarantee. If a "fix" left `capability_check.matched_service_id`
null despite a real service catalog, closed a coverage gap by pointing an
FR at the wrong component, or left `existing_system_impact` referencing a
CI that doesn't exist in the CMDB, that's exactly the defect this gate
exists to catch — independent of what the evaluator's own bookkeeping
says. Unlike its Phase 0/Phase 1 sibling gates, several of this gate's
rules need the ORIGINAL input (`prd_output`, `service_catalog`,
`cmdb_export`) rather than just the generator's own `items`, because
coverage and anti-hallucination checks here are inherently checks against
source data the generator's output does not itself carry.

### Rules

| # | Rule | Category | Action | Severity |
|---|------|----------|--------|----------|
| 1 | schema-compliance | Output schema validation | block | critical |
| 2 | blast-radius-enum-validity | Output schema validation | block | high |
| 3 | capability-check-not-vacuous | Rubric adherence | block | critical |
| 4 | no-vacuous-empty-check | Rubric adherence | block | high |
| 5 | ci-id-validity | Rubric adherence | block | high |
| 6 | full-fr-coverage | Rubric adherence | block | critical |
| 7 | cmdb-kb-mismatch-flagged | Rubric adherence | flag | high |
| 8 | rationale-explanation-check | Rubric adherence | flag | medium |
| 9 | newly-surfaced-dependency-completeness | Rubric adherence | flag | medium |
| 10 | empty-source-explicit-statement | Rubric adherence | flag | medium |

## How It Works

```
L1-planning-impact-assessor-evaluator concludes
        ↓
┌────────────────────────────────────────────────────────────────────┐
│  IMPACT-ASSESSMENT QUALITY GATE (post_execution, fires on eval)    │
│                                                                      │
│  Reconstruct RESULTANT content: capability_check/                  │
│  existing_system_impact/components/external_dependencies with      │
│  fixes_applied[].before→after resolved in                           │
│                                                                      │
│  DETERMINISTIC (actions.py, needs original_input too):             │
│  1. Schema: required fields, id patterns, length minimums?          │
│  2. Every components[].blast_radius in {Low, Medium, High}?         │
│  3. matched_service_id null only if service_catalog genuinely       │
│     empty; else must name a real SVC- id present in the catalog?    │
│  4. existing_system_impact[] non-empty when catalog/CMDB non-empty? │
│  5. Every ci_id actually exists in cmdb_export (unless empty)?      │
│  6. components[].requirement_id set == prd.md's full FR id set?     │
│                                                                      │
│  Any ✗ → BLOCK, retry once, then escalate_to_hitl                   │
│                                                                      │
│  SEMANTIC (self_check_output, LLM):                                  │
│  7. Any CMDB/KB mismatch silently reconciled instead of flagged?    │
│  8. Does every rationale/how_or_why_not genuinely explain, not      │
│     just restate, the decision?                                     │
│  9. Is anything newly surfaced by checks 3-5 captured in            │
│     external_dependencies with newly_surfaced=true?                 │
│  10. Is a genuinely empty catalog/CMDB stated explicitly as such?   │
│                                                                      │
│  Any ✗ → BLOCK, retry once, then escalate_to_hitl                   │
│                                                                      │
│  All ✓ → gate passes                                                 │
└────────────────────────────────────────────────────────────────────┘
        ↓
Resultant impact-assessment content flows to dependency-mapper / backlog-prioritizer
```

## File Structure

```
gr-L1-impact-assessment-quality-gate/
├── config.yml                                  # Rail configuration
├── prompts.yml                                 # LLM evaluation prompt (10 checks)
├── gr-L1-impact-assessment-quality-gate.co     # LLM-only Colang flow
├── impact_assessment_quality_gate.co           # Python-hybrid Colang flow (calls actions.py)
├── actions.py                                  # Deterministic Python (schema, blast-radius enum, capability-check vacuity, CI/FR coverage & anti-hallucination)
├── spec.yaml                                   # Guardrail specification
└── README.md                                   # This file
```

**Two modes:**
- **LLM-only** (`gr-L1-impact-assessment-quality-gate.co`): all 10 checks via `self_check_output`.
- **Python-hybrid** (`impact_assessment_quality_gate.co`): the 6 deterministic checks (1-6) reconstruct the resultant content, pull in `original_input` (prd_output/service_catalog/cmdb_export), and validate directly in `actions.py`; the LLM handles the 4 genuinely semantic checks (7-10) — whether a CMDB/KB mismatch plausibly exists and was silently reconciled, whether a rationale genuinely explains vs. restates, whether something newly surfaced was captured, and whether an empty source was stated explicitly are all judgment calls, not regex matches.

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

**Valid resultant output (expected: "yes")** — capability check names a real non-duplicate candidate, one CI genuinely checked, one FR mapped with a rationale:

```json
{
  "capability_check": {"summary": "Checked the proposed loyalty-points capability against SVC-CUST-001 (Customer & Sales) — the closest candidate in the catalog.", "matched_service_id": "SVC-CUST-001", "is_duplicate": false, "rationale": "SVC-CUST-001 handles customer profile and order history but has no points-accrual or redemption logic; this is a net-new capability, not a duplicate build."},
  "existing_system_impact": [
    {"ci_id": "CI-APP-001", "system_name": "SAP ERP", "touched": true, "how_or_why_not": "Order totals must be read from SAP ERP to compute points accrual per transaction.", "related_components": ["FR-001"]}
  ],
  "components": [
    {"requirement_id": "FR-001", "component_name": "Points Accrual Service", "is_new": true, "blast_radius": "Medium", "rationale": "Other components (redemption, notifications) depend on its output, but it is not on a compliance-critical path."}
  ],
  "external_dependencies": []
}
```

**Invalid resultant output (expected: "no")** — invalid blast_radius and a vacuous capability check:

```json
{
  "capability_check": {"summary": "Checked the catalog, no similar service found.", "matched_service_id": null, "is_duplicate": false, "rationale": "Nothing similar exists."},
  "existing_system_impact": [],
  "components": [
    {"requirement_id": "FR-001", "component_name": "Points Accrual Service", "is_new": true, "blast_radius": "Critical", "rationale": "important"}
  ],
  "external_dependencies": []
}
```

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Clean resultant content | None | "yes" |
| Invalid blast_radius | `"blast_radius": "Critical"` | "no" |
| FR coverage gap | An FR in prd.md with no matching component | "no" |
| Vacuous capability check | `matched_service_id: null` despite a non-empty service_catalog | "no" |
| Invented CI reference | `ci_id` not present in cmdb_export | "no" |
| Skipped technical-touch check | `existing_system_impact: []` despite non-empty catalog/CMDB | "no" |
| Invented FR reference | `requirement_id` not present in prd_output | "no" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L1-impact-assessment-quality-gate")
rails = LLMRails(config)

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<clean resultant impact-assessment JSON>"}]
)
assert "blocked" not in response["content"].lower()
print("✅ Clean resultant content passed")

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<invalid blast_radius JSON>"}]
)
assert "blocked" in response["content"].lower()
print("✅ Invalid blast_radius blocked")
```

### Option 3: Python Unit Testing (standalone actions.py)

```python
import json
from actions import check_impact_assessment_quality_gate

generator_output = json.dumps({"status": "success", "content": {"items": {
    "capability_check": {"summary": "s" * 25, "matched_service_id": "SVC-CUST-001", "is_duplicate": False, "rationale": "r" * 25},
    "existing_system_impact": [{"ci_id": "CI-APP-001", "system_name": "SAP ERP", "touched": True, "how_or_why_not": "h" * 15, "related_components": ["FR-001"]}],
    "components": [{"requirement_id": "FR-001", "component_name": "c", "is_new": True, "blast_radius": "Critical", "rationale": "r" * 15}],
    "external_dependencies": [],
}}})
original_input = json.dumps({
    "prd_output": {"content": {"items": {"requirements": [{"id": "FR-001"}]}}},
    "service_catalog": {"services": [{"service_id": "SVC-CUST-001"}]},
    "cmdb_export": {"configuration_items": [{"ci_id": "CI-APP-001"}]},
})

result = await check_impact_assessment_quality_gate(output="{}", generator_output=generator_output, original_input=original_input)
assert result == True  # invalid blast_radius "Critical" caught
```

See `test_actions.py` (standalone, no pytest dependency) alongside this
guardrail's development for the full functional test suite covering
clean-pass, invalid blast_radius, FR coverage gap, and vacuous
capability-check scenarios.
