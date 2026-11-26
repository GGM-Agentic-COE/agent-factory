# Evaluation Rubric — L0-testing-case-writer

Quality-gate rubric, scoring model, severity rules, Mechanical Fix Policy, and final-decision specification for evaluating `L0-testing-case-writer` outputs (`test-case.json` and per-Feature `<FeatureID>-test-cases.feature` files).

This rubric works alongside `kb-test-case-authoring-standards` (Best Practices KB §§12.3–12.6). It is loaded and applied at runtime by `L0-testing-case-writer-evaluator` (`content.type = "test_case_evaluation"`).

---

## Quality Gates (`QG-01` – `QG-10`)

Evaluate every gate independently using freshly retrieved Jira Scenarios, Jira Features, Test Strategy, and Best Practices KB. Never trust generator self-assessments or coverage claims without re-derivation.

### `QG-01` — Input Verification & Source Grounding

| Criterion | Pass | Fail |
|---|---|---|
| Contract & workflow IDs valid | `generator_output` valid, `workflow_execution_id` (`wf-...`) and `execution_id` (`exec-...`) valid, all expected source types (`jira_scenario`, `jira_feature`, `test_strategy`, `best_practices_kb`) verified, zero PRD dependency | Invalid IDs, missing/unusable `test-case.json`, source mismatch, or PRD used |
| Scenario `source-<KEY>` and `level-*` labels | Every processed Scenario has a valid `source-<KEY>` matching a supplied Feature and a valid `level-*` (`level-feature`, `level-task`, `level-api`); missing/invalid label stopped as `INSUFFICIENT_CONTEXT` | Scenario without `source-<KEY>` or valid `level-*` generated cases instead of reporting `INSUFFICIENT_CONTEXT` |
| Legitimate `INSUFFICIENT_CONTEXT` check | If generator returned `INSUFFICIENT_CONTEXT`, independent retrieval confirms the stated missing source/label/`Integration Point` is genuinely absent | False `INSUFFICIENT_CONTEXT` claim when all required sources and labels exist |

### `QG-02` — AC, Compliance & NFR Coverage

| Criterion | Pass | Fail |
|---|---|---|
| Positive coverage | Every in-scope Scenario AC and Feature AC with a documented successful outcome has at least one grounded positive case, or is recorded with a valid gap | Testable AC silently omitted |
| Negative coverage | Negative cases are written where Jira sources explicitly support adversarial, rejection, boundary, security, invariant, NFR, or compliance failure conditions (capped at 25 in priority order) | Supported negative obligation omitted without gap/cap record, or negative cap ignored |
| Compliance clauses | Every explicitly compliance-tagged Jira clause is covered (or flagged with `coverage_complete = false` and listed in `uncovered_clauses`) | Tagged compliance clause uncovered while claiming `coverage_complete = true` |
| NFR grounding | NFR cases copy ID, category, threshold, unit, measurement condition, measurement window, and source from Jira (or record missing elements in `untestable_nfrs`) | Invented NFR threshold/unit or untestable NFR converted into an arbitrary pass/fail test |

### `QG-03` — Traceability & Citation Gate

| Criterion | Pass | Fail |
|---|---|---|
| Verbatim citations | Every case has `>= 1` entry in `source_references`; every `source_phrase` appears verbatim in a verified Jira source and directly supports the case | Missing `source_references`, fabricated quote, or resolved source does not support the case |
| Identifier traceability | `rule_reference`, `IssueIds`, and `source_test_scenario_ids` accurately match the cited ACs and Scenarios | Wrong issue key, fabricated AC/requirement ID, or Scenario key attached to unrelated Feature AC |
| Dropped-citation threshold | `dropped_case_percentage <= 20` (accurately computed from `removed_for_no_valid_reference / generated_before_validation * 100`) | `dropped_case_percentage > 20` or miscalculated |

### `QG-04` — Grounding, Fidelity & Negative/Boundary Rigor

| Criterion | Pass | Fail |
|---|---|---|
| Zero fabrication | No invented behaviour, rules, actors, roles, screens, limits, error messages, status codes, notifications, or fallback outcomes | Any behavioural element absent from Jira Scenario/Feature introduced |
| Negative-case structure | Every negative case populates `forbidden_state_or_constraint`, `adverse_input`, `expected_safe_behavior`, and `failure_signal`; every positive case sets all four to `null` | Missing negative field, positive case with populated negative fields, or invented failure signal |
| Boundary & conflict handling | Only documented edges tested; source conflicts preserve both references and mark `needs_clarification` rather than choosing silently | Inferred min/max boundaries or silently resolved source conflict |
| No unsupported expansion or duplication | No near-duplicate cases; cases merged only when obligation, behaviour, conditions, input class, and expected result are identical | Near-duplicates or merged cases with differing expected outcomes/categories |

### `QG-05` — Abstraction, Steps & Data Safety

| Criterion | Pass | Fail |
|---|---|---|
| Atomic steps & preconditions | Each manual step has `step_number`, `action`, `test_data`, `expected_result` with one primary action per step; preconditions state required starting state rather than actions | Multi-workflow steps, action inside precondition, or invented UI controls |
| Data & environment safety | `test_data` never empty (`"N/A – no input required"` when none needed); no real PII, secrets, credentials, or tokens; `test_environment` matches Test Strategy or is `null` | Empty `test_data`, real secrets/PII, or unsupported environment |
| Automation status | `automation_status` follows rules (`"needs_clarification"` when confidence `< 0.70`, timing/propagation caveats present, or required test detail missing) | `"ready"` assigned despite timing caveats, missing values, or low confidence |

### `QG-06` — Test Representation Compliance

| Criterion | Pass | Fail |
|---|---|---|
| KB §12.3 compliance | Each case's `test_representation` (`manual` \| `cucumber` \| `review`) matches `kb-test-case-authoring-standards` §12.3 (or §12.6 for `level-api`) with a one-line `representation_reason` | Representation contradicts §12.3/§12.6 or derived solely from `automation_status` or `test_category` |
| Review isolation | `review` cases remain in `test-case.json` with gaps recorded and never appear in any `.feature` file | `review` case rendered in Gherkin |

### `QG-07` — Gherkin & Artifact Synchronization

| Criterion | Pass | Fail |
|---|---|---|
| Per-Feature files stored | One `<FeatureID>-test-cases.feature` exists in S3 with non-null `storage` for every Feature in `feature_issue_keys` (ascending key order) alongside `test-case.json` | Missing S3 file or `storage: null` for `test-case.json` or any `<FeatureID>-test-cases.feature` |
| Feature-file fidelity | Each `<FeatureID>-test-cases.feature` contains only `cucumber` cases for that Feature in canonical order matching `test-case.json` (or only the `Feature:` line when that Feature has 0 `cucumber` cases); follows §12.4 (`Given`/`When`/`Then`, single `When`, no invented `Examples` markers) | Manual/review case in `.feature`, cross-Feature mixing, JSON-to-Gherkin drift, or invalid `Examples` placeholder |
| Metadata & status parity | Counts (`generated_test_case_count`, `positive_case_count`, `negative_case_count`, representation counts), `acceptance_criteria_coverage`, and writer `status` (`failed > partial > success`) match the canonical collection | Count mismatch, stale coverage list, or misleading `success` status when `failed`/`partial` condition holds |

### `QG-08` — Level Tags

| Criterion | Pass | Fail |
|---|---|---|
| Single valid level tag | Every test case carries **exactly one** level tag (`@feature`, `@task`, or `@api`), placed in the tag line right after `@<positive|negative>` (`@TC-nnn @<positive|negative> @<feature|task|api> ...`) | Missing, duplicated, invalid, or misplaced level tag |
| Matches source Scenario | Level tag matches the source Scenario's `level-*` label (`level-feature` → `@feature`, `level-task` → `@task`, `level-api` → `@api`) | Level tag conflicts with source Scenario's `level-*` label |

### `QG-09` — `level-api` Compliance

Applies to every case derived from a Scenario carrying the `level-api` label (mark `not_applicable` when no `level-api` Scenario is in scope).

| Criterion | Pass | Fail |
|---|---|---|
| Always Cucumber | Every case from a `level-api` Scenario has `test_representation = "cucumber"` (never `"manual"` or `"review"` due to representation ambiguity) | Any `level-api` case marked `manual` (or omitted from `.feature` as `manual`) |
| `Integration Point` verbatim | Scenario's `Integration Point` description key exists; all component names in the case match the `Integration Point` verbatim | `Integration Point` missing/guessed, or any component invented, abbreviated, or renamed |
| Sending / receiving GWT | `Given` states the sending component's starting state; `When` states the sending component sending, creating, updating, or exposing the business data or event; `Then` states what the receiving component holds or does afterwards per the AC | Inverted or vague component roles or outcome absent from the AC |
| Business-level abstraction | Every step stays strictly at business level: zero endpoints, URLs, HTTP methods, status codes, JSON field names, payloads, queues, or database tables | Technical protocol, endpoint, payload schema, status code, queue, or table detail present |
| Grounded negative hand-off | Negative `level-api` cases exist only when the AC explicitly states what happens when the hand-off is rejected or fails | Negative `level-api` case created with invented rejection/error behaviour |

### `QG-10` — Output Schema & Ordering Determinism

| Criterion | Pass | Fail |
|---|---|---|
| Canonical ordering & IDs | `TC-001, TC-002, ...` sequential across positive and negative after ordering (Scenario ACs → Feature ACs → other requirement IDs; positive before negative per `rule_reference`) | Duplicate, gapped, or non-canonical TC IDs |
| Output isolation | `generator_output` returns metadata, inventories, coverage summaries, and `artifacts` only; never embeds full test cases, steps, or Gherkin | Complete test cases or artifact bodies embedded inside `AgentOutput` |

---

## Severity Classification

| Severity | Criteria |
|---|---|
| `blocker` | Invented behaviour or values; fabricated citations or non-matching `source_phrase`; uncovered tagged compliance obligation; processed Scenario missing `source-<KEY>` or valid `level-*` instead of `INSUFFICIENT_CONTEXT`; guessed missing `Integration Point`; `dropped_case_percentage > 20`; missing/corrupt `test-case.json`; materially false generator `status` (`success` when `failed` condition applies) |
| `major` | Missing testable AC coverage; any `level-api` failure (`manual` representation, renamed/invented component, technical details in steps, unsupported negative hand-off); meaning-altering `test_representation` violation; unsupported environment; missing `<FeatureID>-test-cases.feature` (`storage: null`); JSON-to-Gherkin semantic drift |
| `minor` | Arithmetic discrepancy in counts, percentages, or coverage summary lists; non-canonical TC-ID numbering/order; missing, incorrect, or misplaced level tag derivable from source Scenario `level-*`; non-null negative fields on a positive case; missing `automation_status = "needs_clarification"` on timing/ambiguity note; formatting defects |

---

## Scoring Model

Compute all 6 component scores independently on a `0.00`–`10.00` scale (rounded to 2 decimal places), where `10.00` represents full compliance (including `hallucination = 10.00` when zero fabrication/hallucination is found):

- **`faithfulness`** (`0.00–10.00`, weight `0.25`): Grounding of positive/negative cases, preconditions, expected results, and `level-api` component behaviour against verified Jira ACs (`QG-01`, `QG-04`, `QG-09`).
- **`hallucination`** (`0.00–10.00`, weight `0.20`): Absence of invented rules, UI elements, thresholds, error messages, endpoints/payloads in `level-api`, or ungrounded data (`QG-04`, `QG-05`, `QG-09`).
- **`consistency`** (`0.00–10.00`, weight `0.15`): Alignment across canonical JSON, `.feature` files, counts, coverage lists, canonical TC order, representation rules, and level tags (`QG-06`, `QG-07`, `QG-08`, `QG-10`).
- **`relevance`** (`0.00–10.00`, weight `0.15`): Coverage of in-scope Scenario/Feature ACs, compliance clauses, NFRs, and absence of out-of-scope regression/near-duplicate cases (`QG-02`).
- **`reasoning_quality`** (`0.00–10.00`, weight `0.10`): Accuracy of `representation_reason`, confidence scoring, gap/conflict reporting, and `automation_status` classification (`QG-05`, `QG-06`).
- **`citation_completeness`** (`0.00–10.00`, weight `0.15`): Verbatim `source_phrase` validity, ID traceability, and `dropped_case_percentage` (`QG-03`).

```text
overall_score = round(
    faithfulness * 0.25 +
    hallucination * 0.20 +
    consistency * 0.15 +
    relevance * 0.15 +
    reasoning_quality * 0.10 +
    citation_completeness * 0.15,
    1
)
```

### Thresholds & Null Rules

- `thresholds_met = true` only when `overall_score >= 7.0`, every applicable component score `>= 6.00`, and zero unresolved `blocker` findings remain.
- When `INSUFFICIENT_CONTEXT` applies or the canonical collection is empty, set every component score and `overall_score` to `null` and `thresholds_met = false`.
- Compute `scores.initial` from the as-received artifacts before fixes, and `scores.final` after permitted mechanical fixes (or equal to `scores.initial` when no fixes are applied).

---

## Mechanical Fix Policy

Apply deterministic fixes **only** when no unresolved `blocker` remains and **only** from this permitted list:

### Permitted Mechanical Fixes

1. Recompute counts (`generated_test_case_count`, `positive_case_count`, `negative_case_count`, `manual_case_count`, `cucumber_case_count`, `review_representation_count`, `compliance_clause_count`, `source_conflicts`), `acceptance_criteria_coverage` lists, and `dropped_case_percentage`.
2. Renumber `TC-nnn` IDs into canonical order and propagate updated TC IDs across dependent coverage lists.
3. Set `forbidden_state_or_constraint`, `adverse_input`, `expected_safe_behavior`, and `failure_signal` to `null` on positive cases.
4. Set `automation_status = "needs_clarification"` where writer rules require (low confidence, timing caveats, missing values).
5. Set `test_environment` when exactly one unambiguous environment is explicitly stated in the Test Strategy.
6. **Level tags:** Add or correct a level tag (`@feature`, `@task`, or `@api`) **only** when it can be taken directly from the source Scenario's `level-*` label, and move a misplaced level tag to immediately follow `@<positive|negative>`.
7. Recompute generator `status` (`failed > partial > success`), re-serialize `test-case.json`, and re-render affected stored `<FeatureID>-test-cases.feature` files from the same corrected canonical collection (never creating a `.feature` file whose writer `storage` was `null`).

### Forbidden / Escalate to Human (`requires_stakeholder_input = true`)

- **Any other `level-api` failure** (non-`cucumber` representation on a `level-api` case, missing or renamed `Integration Point` component, technical endpoints/methods/payloads/status codes/tables in steps, or unsupported negative hand-off cases): **must NOT be fixed**; record finding with `requires_stakeholder_input = true`.
- Never add or delete cases, rewrite intent/steps/expected results/citations, add missing ACs, resolve source conflicts silently, or set/change/reclassify `test_representation` or `representation_reason`.

---

## Final Decision Rules (`final_decision`)

| Decision | Condition |
|---|---|
| `approved` *(legitimate `INSUFFICIENT_CONTEXT`)* | Generator `status = "failed"` reporting `INSUFFICIENT_CONTEXT`, independent retrieval confirms the missing required source/label/`Integration Point`, and `QG-01` confirms no fabricated cases (`scores.* = null`) |
| `rejected` | Unresolved `blocker` finding; false `INSUFFICIENT_CONTEXT` claim; missing/unusable `test-case.json`; `thresholds_met = false`; `overall_score < 7.0`; or unrecoverable synchronization failure |
| `needs_clarification` | No unresolved `blocker`, but one or more unresolved findings require human/stakeholder input (`requires_stakeholder_input = true`, including any non-tag `level-api` failure or missing `<FeatureID>-test-cases.feature` with `storage: null`), or a required S3 overwrite failed |
| `approved` | Zero fixes required, every applicable gate (`QG-01`–`QG-10`) passes, remaining gates legitimately `not_applicable`, `thresholds_met = true`, `overall_score >= 7.0`, and zero unresolved findings block approval |
| `fixed_and_approved` | Permitted mechanical fixes applied, every applicable gate passes after fixes, `thresholds_met = true`, `overall_score >= 7.0`, zero unresolved findings block approval, and every required S3 overwrite confirmed (`never fixed_and_approved while S3 holds pre-fix content`) |
