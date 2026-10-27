# L1 Testing Strategy — Evaluation Criteria

> **Knowledge Base:** kb-L1-testing-strategy-eval
> **Consumed by:** L1-testing-strategy-evaluator
> **Purpose:** Rubric for independently evaluating a Test Strategy document produced
> by L1-testing-strategy-architect. Every gate is binary pass/fail. The evaluator
> must re-derive results from freshly-fetched source data — never trust the
> generator's self-assessment.

> **Source artifacts:** PRD and the four Cycle 0 architecture declaration viewpoints
> (APP, PLT, INT, DAT). There is no HLD or LLD at this point — the declaration
> precedes all component work.

> **Strategy document structure:** The architect produces an 8-section document:
> §1 Scope and standing, §2 The four tiers, §3 Environment topology,
> §4 Fixture policy, §5 NFR approach, §6 Pack governance,
> §7 What this strategy does NOT settle and why, §8 Declaration sections read
> and sections absent.

---

## Evaluation Gates

### Gate 1 — Input Coverage Verification

| Criterion | Pass | Fail |
|-----------|------|------|
| Declaration section coverage matches re-fetched data | Architect's `declaration_sections_present` and `declaration_sections_absent` match actual presence of declaration viewpoint sections (APP-*, PLT-*, INT-*, DAT-*) in the re-fetched data | Any mismatch between claimed and actual section availability |
| Minimum required sections present | APP-2 (component map) and DAT-3 (classification, retention) are present in re-fetched data — architect should have returned INSUFFICIENT_CONTEXT if either was absent | Strategy produced without APP-2 or DAT-3 |
| [TO BE CONFIRMED] markers are genuine | Every TBC marker corresponds to a truly absent or sparse declaration section | TBC marker applied to a section whose declaration input was present and detailed |
| False confidence detection | No section claims confirmed status when its source declaration section lacked detail | Section marked confirmed but required details are absent in source declaration |

**Evaluation method:** Re-fetch all declaration viewpoint documents independently. Compare architect's `input_summary.parameters.declaration_sections_present` and `declaration_sections_absent` against actual re-fetched sections. Verify APP-2 and DAT-3 presence. Cross-reference every [TO BE CONFIRMED] marker against re-fetched section content.

---

### Gate 2 — Requirements Grounding (§1, §2)

| Criterion | Pass | Fail |
|-----------|------|------|
| §1 scope accuracy | §1 correctly names product, PI identifier, declaration sections read/absent, and roadmap status | Incorrect product name, PI, or declaration section listing |
| Tier derivation source accuracy | Feature tier traces to PRD epics/ACs + APP-2; Contract tier traces to INT service-to-service + APP-2 boundaries; Integration tier traces to INT dependency graph + blast-radius; Regression+NFR tier traces to nfr_classifications + REQ-* budgets | Tier derived from wrong source or ungrounded source reference |
| Entry/exit criteria grounding | Every entry criterion is a condition grounded in PRD or declaration data; every exit criterion is a number or boolean, never qualitative | Entry criterion is prose not a condition; exit criterion is qualitative ("high coverage", "adequate") |
| No hallucination | Every epic, feature, AC, or requirement ID in the strategy exists in source PRD or declaration | Any ID in the strategy not found in source data |

**Evaluation method:** Parse freshly-fetched prd.md independently. Extract all epics, features, ACs, requirement IDs, and nfr_classifications. Verify §1 scope fields. For each tier in §2, verify the derivation sources are correct and entry/exit criteria are grounded. Cross-reference all cited IDs against source data.

---

### Gate 3 — Tier Policy Completeness (§2)

| Criterion | Pass | Fail |
|-----------|------|------|
| Tier count | §2 covers all 4 governed tiers: Feature, Contract, Integration, Regression+NFR | Any tier missing |
| Field completeness | Every tier has all 4 required fields: entry, exit, cadence, load_bearing_in | Any tier missing any field |
| Exit criteria quantification | Every exit criterion is a number or boolean | Qualitative exit criteria ("high", "adequate", "fast") |
| Cadence validity | Cadence values are one of {every cycle, band boundary, every N cycles, release} and justified against PI cadence | Invalid cadence value or unjustified cadence |
| Load-bearing validity | load_bearing_in values are valid subsets of {greenfield, brownfield, bugfix} | Invalid load-bearing classification |
| Coverage target quantification | Per-tier coverage targets are numbers | Vague coverage targets |
| Project specificity | Per-tier ownership and scope descriptions are project-specific | Boilerplate descriptions applicable to any project |
| Stub entry criteria | Declared-but-never-built components have stub entry criteria in Contract and Integration tiers | Declared-but-never-built component missing from Contract/Integration tiers |

**Evaluation method:** Parse §2 tier table and per-tier detail. Verify 4 tiers × 4 fields. Check every exit criterion and coverage target for numeric values. Verify cadence justification against PI cadence. Check load_bearing_in against valid enum. Verify project-specific language.

---

### Gate 4 — Environment Topology Grounding (§3)

| Criterion | Pass | Fail |
|-----------|------|------|
| Isolation rule traced | §3 isolation rule is derived from a named PLT section with traced_to | Isolation rule without traced_to or traced to wrong section |
| Data-residency constraint traced | §3 data-residency constraint is derived from a named PLT section with traced_to | Data-residency constraint without traced_to or fabricated |
| Topology summary sourced | §3 topology summary reflects environments and purposes from PLT-1..5 and APP-2 | Topology includes environments not in PLT or APP-2 |
| No per-component enumeration | §3 does NOT enumerate environments per component | Per-component environment list present (this is a register, not a policy) |
| No hallucination | Every environment and constraint in §3 exists in source PLT and APP-2 data | Any fabricated environment, constraint, or infrastructure detail |

**Evaluation method:** Parse freshly-fetched PLT-1..5 and APP-2 independently. Extract environment definitions, isolation rules, and data-residency policies. Verify every claim in §3 traces to a specific declaration section.

---

### Gate 5 — Fixture Policy Grounding (§4)

| Criterion | Pass | Fail |
|-----------|------|------|
| Data ownership traced | §4 data ownership model is derived from DAT-1 with traced_to | Ownership model without traced_to or not from DAT-1 |
| Classification traced | §4 classification and retention is derived from DAT-3 with traced_to | Classification without traced_to or not from DAT-3 |
| PII rule is prohibition | PII rule is stated as a PROHIBITION ("No PII in any non-production environment") | PII rule stated as a preference ("PII should be minimised") |
| Provisioning strategy sourced | Test data provisioning strategy derives from DAT-1 and DAT-3 | Provisioning strategy ungrounded or fabricated |
| No untraced policy | Every data policy carries traced_to naming DAT-1 or DAT-3 | Any data policy without traceability to DAT sections |

**Evaluation method:** Parse freshly-fetched DAT-1 and DAT-3 independently. Extract ownership rules, classification schemes, retention policies, and masking requirements. Verify every claim in §4 traces to DAT-1 or DAT-3.

---

### Gate 6 — NFR Approach Grounding (§5)

| Criterion | Pass | Fail |
|-----------|------|------|
| Budgeted NFRs have numbers | Every budgeted NFR has a numeric budget and a testable assertion derived from that number | Any budgeted NFR with qualitative assertion ("fast", "reliable", "low latency") |
| Unbudgeted NFRs explicitly listed | Every classified-but-unbudgeted NFR is listed under nfr_unbudgeted with reason "no budget provided" | Unbudgeted NFR missing from the list |
| No classification mismatch | No NFR with a budget listed as unbudgeted; no NFR without a budget listed as budgeted | Misclassified NFR |
| Source alignment | NFR categories and budgets match nfr_classifications and REQ-* budgets from PRD | NFR category or budget not in source PRD |

**Evaluation method:** Parse freshly-fetched nfr_classifications and REQ-* budgets from prd.md independently. Build a set of all NFRs with their budget status. Compare 1:1 against §5 budgeted and unbudgeted lists.

---

### Gate 7 — Pack Governance Validation (§6)

| Criterion | Pass | Fail |
|-----------|------|------|
| Flake threshold numeric | flake_threshold is a number with a unit (e.g., ≤ 2.0%) | Prose threshold or missing |
| Staleness ceiling numeric | staleness_ceiling is a number with a unit (e.g., 3 cycles) | Prose threshold or missing |
| Runtime budgets per tier | runtime_budget_per_tier_minutes has one entry per tier (feature, contract, integration, regression_nfr), each a number | Any tier missing a budget or budget is prose |
| Coverage targets numeric | coverage_target_ac and coverage_target_adversarial are numbers | Prose targets |
| Cadence justification | Every threshold is justified against the PI cadence | Threshold without cadence justification |
| Budget within cadence | No runtime budget exceeds the cadence window | Budget exceeds total pipeline/cadence window |
| Quarantine policy defined | Policy for what happens when flake threshold is breached | Missing quarantine policy |
| Staleness audit cadence | Staleness audit frequency and mechanism specified | Missing staleness audit |
| Breach policy defined | Policy for what happens when runtime budget is exceeded | Missing breach policy |

**Evaluation method:** Parse §6 governance table. Verify every threshold is a number with a unit. Cross-reference runtime budgets against PI cadence to ensure they fit within the window. Verify quarantine, staleness audit, and breach policies are defined.

---

### Gate 8 — Not-Settled-Here Validation (§7)

| Criterion | Pass | Fail |
|-----------|------|------|
| Section present and non-empty | §7 exists and contains at least three exclusion statements | §7 missing or empty |
| No test cases stated | §7 states that no test cases are authored here, with justification | Missing the no-test-cases exclusion |
| No per-component register stated | §7 states that no per-component environment register is included, with justification | Missing the no-register exclusion |
| No per-component fixtures stated | §7 states that no per-component fixture inventory is included, with justification | Missing the no-fixtures exclusion |
| Justifications grounded | Every exclusion has a justification traceable to the architect's domain context | Unjustified exclusion or generic "not in scope" |

**Evaluation method:** Parse §7 content. Verify presence of the three mandatory exclusion statements. Check justifications trace to domain context (e.g., just-in-time elaboration, register vs. policy distinction).

---

### Gate 9 — Declaration Coverage Verification (§8)

| Criterion | Pass | Fail |
|-----------|------|------|
| Sections read listed | §8 enumerates every section ID and title that was read | Any read section missing from the list |
| Sections absent listed | §8 enumerates every absent section with the policy constrained by its absence | Absent section missing or no constraint stated |
| Cross-reference accuracy | §8 listings match the re-fetched declaration data | Section listed as present but absent in re-fetched data, or vice versa |

**Evaluation method:** Cross-reference §8 sections_read and sections_absent against the independently re-fetched declaration viewpoints. Verify constraint statements for each absent section.

---

### Gate 10 — Traceability & Hallucination Check (Full Document)

| Criterion | Pass | Fail |
|-----------|------|------|
| No test cases | No test cases, test scripts, or test data records anywhere in the document | Any test case, script, or data record found |
| ID authenticity | Every requirement ID, epic key, component name, declaration section ID exists in source data | Any fabricated ID |
| Traceability completeness | Every derived policy carries traced_to naming a declaration section | Any policy without traced_to |
| No boilerplate | Every section contains project-specific content | Generic content applicable to any project |
| No PII / credentials | No PII, real credentials, or sensitive data | PII or credentials found |
| No leftover placeholders | No raw {placeholder} brackets remain in sections that had sufficient input | Unfilled placeholders in sections with available data |
| Summary field integrity | No *_summary field silently contains the full artifact text instead of a distillation | Summary field contains full artifact text verbatim |
| Threshold integrity | Every threshold in the tier table, governance table, and NFR approach is a number with a unit or a boolean | Any threshold expressed in prose |

**Evaluation method:** Scan full document for test case patterns ("test case:", "TC-", "steps: 1. navigate to"). Cross-reference all IDs against source data. Verify traced_to on every policy. Check for boilerplate, PII, placeholders, and threshold prose.

---

## Scoring Model

### Per-Gate Scoring

Each gate produces a score from 0.0 to 1.0:
- **1.0** — All criteria pass
- **0.5–0.9** — Most criteria pass; minor issues found (mechanically fixable)
- **0.1–0.4** — Significant failures; multiple criteria fail
- **0.0** — Complete gate failure; fundamental issues

### Score Dimensions

| Dimension | Maps to Gate(s) |
|-----------|----------------|
| `requirements_grounding` | G2 |
| `tier_policy_completeness` | G3 |
| `environment_topology_grounding` | G4 |
| `fixture_policy_grounding` | G5 |
| `nfr_approach_grounding` | G6 |
| `pack_governance_validity` | G7 |
| `declaration_coverage_accuracy` | G9 |
| `traceability_and_hallucination` | G10 |
| `boundary_compliance` | G8 |

### Overall Score Computation

```
overall_score = (
    requirements_grounding × 1.5 +
    tier_policy_completeness × 1.5 +
    environment_topology_grounding × 1.0 +
    fixture_policy_grounding × 1.0 +
    nfr_approach_grounding × 1.0 +
    pack_governance_validity × 1.0 +
    declaration_coverage_accuracy × 1.0 +
    traceability_and_hallucination × 2.0 +
    boundary_compliance × 1.0
) / 11.5 × 10.0
```

Weights reflect downstream impact:
- **2.0x** — Traceability & hallucination (fabricated data propagates as false truth)
- **1.5x** — Requirements grounding, tier policy completeness (directly consumed by
  downstream agents: `env-provisioner`, `regression-pack-curator`, `risk-selector`)
- **1.0x** — Environment topology, fixture policy, NFR approach, pack governance,
  declaration coverage, boundary compliance (important but less likely to propagate)

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
| Hallucination found with downstream impact (affects tiers, governance, topology) | `escalate_to_hitl` |

---

## Mechanical Fix Policy

The evaluator MAY fix the following WITHOUT escalation:
- Missing traced_to on a policy that is clearly derivable from a specific
  declaration section
- Wrong cadence or load_bearing_in value clearly contradicted by the declaration
  or PRD
- Missing [TO BE CONFIRMED] marker for genuinely absent or sparse declaration section
- Inconsistent declaration_coverage listing (section listed as present but absent
  in re-fetched data, or vice versa)
- A threshold expressed in prose when the source data provides a number
- Tier field missing but derivable from source data with no ambiguity
- Correcting invalid section cross-references

The evaluator MUST escalate the following:
- Hallucinated content with downstream impact (affects tier structure, governance
  thresholds, topology, or fixture policy that downstream agents consume)
- A tier's entry/exit criteria that may be intentionally structured but appear
  misaligned — requires domain judgment
- Missing declaration sections that constrain multiple policies — may indicate
  intentional scoping decisions vs. omissions
- Conflicting declaration data (e.g., PLT and APP disagree on environment topology)
- Coverage targets or governance thresholds that may be intentionally aggressive
  or conservative for the project's context
