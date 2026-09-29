# L1 Testing Strategy — Evaluation Criteria

> **Knowledge Base:** kb-L1-testing-strategy-eval
> **Consumed by:** L1-testing-strategy-evaluator
> **Purpose:** Rubric for independently evaluating a Test Strategy document produced
> by L1-testing-strategy-architect. Every gate is binary pass/fail. The evaluator
> must re-derive results from freshly-fetched source data — never trust the
> generator's self-assessment.

---

## Evaluation Gates

### Gate 1 — Input Coverage Verification

| Criterion | Pass | Fail |
|-----------|------|------|
| Input coverage count matches re-fetched data | Generator's `input_coverage` matches actual artifact presence | Any mismatch between claimed and actual input availability |
| [TO BE CONFIRMED] markers are genuine | Every TBC marker corresponds to a truly absent input | TBC marker applied to a section whose input was present but ignored |
| False confidence detection | No section claims confirmed status when its input was absent | Section marked confirmed but required/recommended input is missing |

**Evaluation method:** Compare generator's `metadata.input_coverage` and `sections_to_be_confirmed` against the set of artifacts successfully returned by the blob storage reader.

---

### Gate 2 — Requirements Grounding (§2)

| Criterion | Pass | Fail |
|-----------|------|------|
| Epic completeness | Every epic in source Jira data appears in §2 | Any source epic missing from §2 |
| Story completeness | Every story with ACs appears in §2 mapping | Any source story with ACs missing from §2 |
| AC completeness | Every AC from every story has a testability classification | Any AC unclassified or missing |
| Testability accuracy | Classification is reasonable given AC text | Clearly wrong classification (e.g., pure API AC marked UI-testable) |
| No hallucination | Every epic/story/AC in §2 exists in source data | Any ID in §2 not found in source Jira data |
| Business criticality grounding | Ranking cites specific epic/story keys from source | Ranking uses generic language without citing real IDs |

**Evaluation method:** Parse freshly-fetched `jira_epics_stories.json`. Build a set of all epic keys, story keys, and ACs. Compare 1:1 against §2 content.

---

### Gate 3 — Architecture Grounding (§3)

| Criterion | Pass | Fail |
|-----------|------|------|
| HLD fidelity | Every component/service in §3 exists in source HLD | Any component in §3 not in HLD |
| LLD fidelity | Every technical detail in §3 exists in source LLD | Any technical detail in §3 not in LLD |
| Testing impact validity | Architecture→testing logic is sound | Testing approach contradicts architecture (e.g., contract testing for monolith) |
| Impact assessment alignment | Blast radii/dependency references match source | Unsupported blast-radius or dependency claim (when impact_assessment provided) |
| No hallucination | No fabricated component names, APIs, or tech stack items | Any tech/component in §3 not in source HLD/LLD |

**Evaluation method:** Parse freshly-fetched `hld.md` and `lld.md`. Extract component lists, tech stack, integration points. Cross-reference §3 claims.

---

### Gate 4 — Scope Consistency (§4)

| Criterion | Pass | Fail |
|-----------|------|------|
| Component coverage | Every component in §3 appears in §4 In-Scope or Out-of-Scope | Any component in §3 not accounted for in §4 |
| In-scope traceability | Every in-scope item traces to a real epic/story or HLD section | In-scope item with no source reference |
| Out-of-scope justification | Every out-of-scope area has explicit, grounded justification | Unjustified exclusion or generic "not in scope" without reason |
| No scope creep | No in-scope item references requirements not in source data | Scope item citing non-existent requirement |

**Evaluation method:** Build component set from §3, verify every member appears in §4. Check source references for each scope item.

---

### Gate 5 — Tier Policy Completeness (§5)

| Criterion | Pass | Fail |
|-----------|------|------|
| Tier field completeness | Every tier (1–4) has Owner, Scope, Coverage Target, Automation | Any tier missing any of the 4 fields |
| Coverage target quantification | Targets are numeric/quantitative (e.g., "≥ 80% line coverage") | Vague targets (e.g., "high coverage", "adequate testing") |
| Testing type rationale | Every testing type has applicability rationale + source reference | Any type listed without rationale or source |
| NFR validation approach | Entries present when nfr.md was provided; marked TBC when absent | Present without NFR input (false confidence) or absent with NFR input (missed) |
| Shift-left definition | Shift-left section is populated with project-specific approach | Generic "we will shift left" without specifics |

**Evaluation method:** Parse §5 structure, verify 4 tiers × 4 fields. Check coverage targets for numeric values. Cross-reference NFR approach against nfr.md presence.

---

### Gate 6 — Environment & Automation Consistency (§6, §7)

| Criterion | Pass | Fail |
|-----------|------|------|
| Environment source alignment | §6 reflects environment_inventory if present; TBC if absent | §6 populated without inventory (false confidence) or TBC with inventory (missed) |
| Tooling-tech stack consistency | §7 tooling matches tech stack in §3/LLD | Recommending wrong-ecosystem tools (e.g., JUnit for Python) |
| CI/CD source alignment | §7 CI/CD reflects cicd_pipeline_config if present; TBC if absent | §7 CI/CD populated without config (false confidence) or TBC with config (missed) |
| Automation inventory accounting | If existing_automation_inventory provided, §7 accounts for reuse | Existing inventory ignored |

**Evaluation method:** Cross-reference §6 against environment_inventory.json, §7 against lld.md tech stack and cicd_pipeline_config.yaml.

---

### Gate 7 — Risk Grounding (§9)

| Criterion | Pass | Fail |
|-----------|------|------|
| Risk traceability | Every risk traces to a specific input (requirement, HLD, LLD, impact assessment, or risk register) | Any risk without source attribution |
| Risk register incorporation | If risk_register provided, pre-identified risks appear in §9 | Risk register provided but risks not incorporated |
| Mitigation actionability | Mitigation plans contain actionable steps | Vague mitigations ("monitor closely", "address as needed") |
| Impact assessment integration | If impact_assessment provided, blast-radius risks incorporated | Impact assessment provided but not reflected in risks |
| No hallucination | No fabricated risks citing non-existent components or systems | Risk referencing component not in HLD/LLD |

**Evaluation method:** For each risk in §9, trace to source document. Verify mitigation specificity. Cross-reference impact_assessment and risk_register if present.

---

### Gate 8 — Quality Gates Consistency (§10)

| Criterion | Pass | Fail |
|-----------|------|------|
| Tier count match | Tier count in §10 matches tier count in §5 | Mismatched tier counts |
| Coverage target reference | Per-tier exit criteria reference §5 coverage targets | Exit criteria generic or disconnected from §5 targets |
| Cascade integrity | Each tier's entry requires prior tier's exit | Tier entry skips prior tier's exit criteria |
| Global gate aggregation | Global Release Gate aggregates all tiers | Global gate omits any tier |

**Evaluation method:** Count tiers in §10 vs §5. Verify exit criteria contain coverage target references. Check cascade chain.

---

### Gate 9 — Pack Governance Validation (§11)

| Criterion | Pass | Fail |
|-----------|------|------|
| Flake threshold per tier | Thresholds set for every tier in §5 | Any tier missing a flake threshold |
| Staleness ceiling defined | Maximum age + audit cadence specified | Missing staleness definition or audit cadence |
| Runtime budgets per tier | Budget set for every automated tier (Tiers 1–3) | Any automated tier missing a runtime budget |
| Budget consistency | Runtime budgets plausible given §7 CI/CD context | Budget exceeds total pipeline window or is unrealistically small |
| Breach policies defined | Every threshold type has a breach/remediation policy | Thresholds without breach policies |
| Quarantine policy defined | Flaky test quarantine policy specified | Flake threshold without quarantine process |

**Evaluation method:** Parse §11 structure. Verify thresholds exist for all tiers in §5. Cross-reference runtime budgets against §7 CI/CD pipeline.

---

### Gate 10 — Traceability Matrix Verification (§12)

| Criterion | Pass | Fail |
|-----------|------|------|
| Row completeness | Every requirement/AC from §2 (sourced from Jira data) has a row | Any requirement/AC without a traceability row |
| Coverage status accuracy | "Covered" rows have all columns populated; "Partial" rows cite what's missing | "Covered" status but references TBC sections |
| Coverage summary accuracy | Summary counts match actual row statuses | Count mismatch |
| No hallucination | Every row references a real requirement from source data | Row citing non-existent requirement |
| Section reference validity | Strategy Section(s) column references real sections (§1–§12) | References to non-existent sections |
| Risk linkage accuracy | Risk IDs in matrix exist in §9 | Matrix cites risk ID not in §9 |

**Evaluation method:** Build requirement set from freshly-fetched Jira data. Verify 1:1 row coverage in §12. Count rows by status, compare to summary.

---

### Gate 11 — Boundary & Hallucination Check

| Criterion | Pass | Fail |
|-----------|------|------|
| No test cases | No test cases, test scripts, or test data records anywhere | Any test case, script, or data record found |
| Executive Summary grounding | §1 introduces no claim not traceable to §2–§12 | New analysis or untraceable claim in §1 |
| ID authenticity | Every epic key, story key, component name exists in source | Any fabricated ID |
| No boilerplate | Every section contains project-specific content | Section with generic content applicable to any project |
| No PII / credentials | No PII, real credentials, or sensitive data | PII or credentials found |

**Evaluation method:** Scan full document for test case patterns ("test case:", "TC-", "steps: 1. navigate to"). Verify §1 claims trace to later sections. Cross-reference all IDs against source data.

---

### Gate 12 — Defect Management Validation (§8)

| Criterion | Pass | Fail |
|-----------|------|------|
| Policy source alignment | §8 adopts org_defect_policy if provided; uses defaults if absent | §8 ignores available policy or fabricates one |
| Severity definitions present | All severity levels (Blocker, Critical, Major, Minor) defined | Any severity level undefined or empty |
| Lifecycle defined | Defect lifecycle workflow is stated | Missing lifecycle definition |
| Tool specified | Defect tracking tool is named | No tool specified |

**Evaluation method:** Check org_defect_policy presence. Verify §8 content alignment. Confirm all severity levels present.

---

## Scoring Model

### Per-Gate Scoring

Each gate produces a score from 0.0 to 1.0:
- **1.0** — All criteria pass
- **0.5–0.9** — Most criteria pass; minor issues found (mechanically fixable)
- **0.1–0.4** — Significant failures; multiple criteria fail
- **0.0** — Complete gate failure; fundamental issues

### Overall Score Computation

```
overall_score = (
    requirements_grounding × 1.5 +
    architecture_grounding × 1.5 +
    scope_consistency × 1.0 +
    tier_policy_completeness × 1.5 +
    pack_governance_validity × 1.0 +
    traceability_completeness × 1.5 +
    hallucination × 2.0 +
    consistency × 1.0 +
    boundary_compliance × 1.0
) / 12.0 × 10.0
```

Weights reflect downstream impact:
- **2.0x** — Hallucination (fabricated data propagates as false truth)
- **1.5x** — Requirements grounding, architecture grounding, tier policy,
  traceability (directly consumed by downstream agents)
- **1.0x** — Scope, pack governance, consistency, boundary (important but
  less likely to propagate errors)

### Pass/Fail Threshold

- **Pass:** overall_score ≥ 7.0 AND no hallucination findings AND no
  unresolved boundary violations
- **Fail:** overall_score < 7.0 OR any hallucination finding OR any
  unresolved boundary violation

### Final Decision Rules

| Condition | Decision |
|-----------|----------|
| All gates pass, no fixes needed | `approved` |
| All gates pass after mechanical fixes | `fixed_and_approved` |
| Any gate has ambiguous failure requiring human judgment | `escalate_to_hitl` |
| Hallucination found but mechanically removable (no downstream impact) | `fixed_and_approved` |
| Hallucination found with downstream impact (affects scope, risks, traceability) | `escalate_to_hitl` |

---

## Mechanical Fix Policy

The evaluator MAY fix the following WITHOUT escalation:
- Missing traceability row for a requirement that clearly maps to existing sections
- Wrong testability classification clearly contradicted by AC text
- Missing [TO BE CONFIRMED] marker for genuinely absent input
- Inconsistent coverage summary count (arithmetic error)
- Missing tier field derivable from source data with no ambiguity

The evaluator MUST escalate the following:
- Hallucinated content with downstream impact
- Architecture-to-testing-approach misalignment that requires domain judgment
- Missing requirements (epics/stories in source but not in strategy) that may
  indicate intentional scoping decisions vs. omissions
- Conflicting source data (e.g., HLD says microservices, LLD says monolith)
- Coverage targets that may be intentionally aggressive or conservative
