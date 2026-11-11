## L1 Test Scenario — Evaluation Criteria

**Knowledge Base:** kb-L1-test-scenario-eval
**Consumed by:** L1-test-scenario-evaluator
**Purpose:** Rubric for independently evaluating Test Scenarios produced by
L1-test-scenario-writer. Every criterion is binary pass/fail. The evaluator must
re-derive results from freshly-fetched Jira and Confluence data — never trust the
writer's self-assessment.

**Source artifacts:** Jira Features + ACs (Jira Reader) and the Test Strategy
(Confluence Reader: Test Levels table, Test Types "Functional acceptance" row, TP-04 only).
HLD, LLD, API contracts, and code are out of bounds.

**Scenario definition:** A Test Scenario states WHAT business behaviour an AC requires
to be tested. Positive/negative path expansion belongs to the downstream Test Case
Generator and is out of scope for the writer and the evaluator.

**Scenario template (exactly these fields):** test_scenario_id, feature_key,
acceptance_criteria_id, testing_level, test_scenario_description, pre_condition,
test_data, navigable_path, expected_result.

### Evaluation Gates

#### Gate 1 — Input Verification

| Criterion | Pass | Fail |
|---|---|---|
| AC inventory matches Jira | Every (feature_key, AC ID) the writer used exists in the re-fetched Jira data, and every re-fetched AC is accounted for | Writer's inventory adds, drops, or alters ACs |
| AC_ID_ASSIGNED correct | IDs assigned only to ACs without Jira IDs, as AC-01, AC-02… in source order; warning recorded | IDs assigned to ACs that already had IDs, wrong order, or warning missing |
| NO_ACS_ON_FEATURE correct | Recorded only for Features with genuinely zero ACs | Feature with ACs skipped, or AC-less Feature not flagged |
| DUPLICATE_AC_KEY correct | Recorded for every duplicate (feature_key, AC ID) in source | Duplicate missed or falsely flagged |
| INSUFFICIENT_CONTEXT genuine | If writer halted, the stated reason holds against re-fetched sources | Writer halted though sources were sufficient |

**Evaluation method:** Re-fetch Jira and Confluence. Rebuild the AC inventory keyed on (feature_key, AC ID). Diff against the writer's scenarios and warnings.

#### Gate 2 — Traceability

| Criterion | Pass | Fail |
|---|---|---|
| feature_key authentic | Every feature_key exists in re-fetched Jira data | Any fabricated or mistyped feature_key |
| AC ID authentic | Every (feature_key, AC ID) pair exists, or follows the AC_ID_ASSIGNED rule | Any fabricated pair or AC ID attached to the wrong Feature |
| Behaviour traceable | Each scenario's behaviour is found in its referenced AC, not a different AC | Scenario cites one AC but tests another AC's behaviour |

**Evaluation method:** Look up each scenario's pair in the rebuilt inventory. Compare scenario behaviour against the cited AC text.

#### Gate 3 — AC Coverage

| Criterion | Pass | Fail |
|---|---|---|
| Every AC covered | Every AC has ≥ 1 scenario OR an AMBIGUOUS_AC warning | Any AC silently skipped |
| AMBIGUOUS_AC genuine | Flagged only when the AC has no observable outcome or cannot be tested as written | Testable AC flagged ambiguous, or untestable AC given a scenario |
| Distinct behaviours covered | When an AC explicitly states multiple distinct behaviours, each is represented | An explicitly stated behaviour in the AC has no scenario |
| Rejection-type ACs represented | If the AC's stated behaviour is a rejection/error/prohibition, that behaviour is the scenario | Rejection AC turned into an invented success scenario |

**Evaluation method:** For each AC in the inventory, count linked scenarios. Split AC text into explicitly stated behaviours; verify each is represented once.

#### Gate 4 — AC Fidelity & Grounding

| Criterion | Pass | Fail |
|---|---|---|
| expected_result traceable | Observable outcome stated in the AC; nothing added | Outcome invented, extended, weakened, or contradicts the AC |
| Messages verbatim | Error/confirmation messages quoted exactly as in AC | Paraphrased or invented messages |
| pre_condition grounded | From the AC's Given clause; actor role only if stated in AC or Feature description | Invented states, roles, or permissions |
| Description faithful | test_scenario_description restates AC behaviour without reinterpretation | Reworded so meaning changes |
| No invented entities | No actors, screens, states, limits, or rules absent from AC/Feature description | Any invented entity |
| AC wins | Feature description enriches wording only; never overrides AC | Feature context used to define or change behaviour |

**Evaluation method:** Compare each field against the cited AC text and Feature description. Any token of behaviour not present in source is a fail.

#### Gate 5 — Scenario Scope

| Criterion | Pass | Fail |
|---|---|---|
| No path expansion | No positive/negative, alternate, or variant scenarios beyond AC-stated behaviours | Scenarios expanding an AC into success/failure variants (Test Case Generator's job) |
| No out-of-scope types | Zero boundary values not in AC, rate limiting, injection, abuse, security attacks, resilience, performance, NFR | Any such scenario |
| No near-duplicates | No two scenarios share actor, action, data pattern, and expected result | Near-duplicate scenarios present |
| No test-case detail | Zero numbered steps, TC- IDs, assertions, or per-field validation lists | Test-case-level content present |
| No implementation-derived behaviour | Nothing sourced from HLD, LLD, API contracts, or code | Implementation-derived scenarios |

**Evaluation method:** For each AC with > 1 scenario, confirm each extra scenario maps to a separate behaviour explicitly in the AC text. Scan for test-case patterns ("TC-", "Step 1", "assert").

#### Gate 6 — Testing Level

| Criterion | Pass | Fail |
|---|---|---|
| Exactly one level | Each scenario has one testing_level | Missing or multiple levels; same scenario duplicated at several levels |
| Level verbatim & allowed | Name matches the Test Levels table exactly and is in the Functional acceptance row | Invented level, altered name, or level not allowed for functional acceptance |
| TP-04 applied | Single rule/service behaviour -> lowest allowed level; cross-service/event flow -> Integration; UI journey -> End-to-end (where allowed) | Level higher or lower than the AC text justifies |
| LEVEL_UNDETERMINED correct | Recorded only when AC text gives no level signal; lowest allowed level used | Missing when needed, or used when AC text was clear |

**Evaluation method:** Re-extract allowed levels and "proves" definitions from the re-fetched Test Strategy. Re-derive the level for each scenario from AC text using TP-04 and compare.

#### Gate 7 — Abstraction & Data Safety

| Criterion | Pass | Fail |
|---|---|---|
| navigable_path business-level | Business journey; screen/app names only if stated in AC or Feature description, otherwise generic steps | Endpoints, HTTP methods, DB tables, component names, or invented screen names |
| test_data mock only | Realistic mock business values; example.com emails; placeholders like {VALID_PASSWORD} | Real PII, live credentials, secrets, or tokens |
| test_data adds no rules | Data does not introduce limits, formats, or rules absent from the AC | Data implies unstated business rules |

**Evaluation method:** Scan navigable_path for technical patterns ("/api", "GET", "POST", "table", "service"). Scan test_data for PII/credential patterns. Cross-check named screens against AC/Feature text.

#### Gate 8 — Format & Determinism

| Criterion | Pass | Fail |
|---|---|---|
| Template exact | Exactly the 9 template fields; all non-empty; no scenario_type or jira_key in writer output | Missing, extra, or empty fields |
| TS-ID ordering | TS-001… sequential per Feature; Features in ascending key order; ACs in source order; behaviours in AC order | Gaps, duplicates, or non-deterministic order |
| Warning codes valid | Only AMBIGUOUS_AC, AC_ID_ASSIGNED, NO_ACS_ON_FEATURE, LEVEL_UNDETERMINED, DUPLICATE_AC_KEY; each names feature_key/AC ID | Unknown codes or warnings without references |
| Output envelope | {"scenarios": [...], "warnings": [...]} or a valid INSUFFICIENT_CONTEXT object | Malformed envelope |

**Evaluation method:** Schema-check every scenario. Recompute expected TS-ID order and diff.

### Scoring Model

#### Per-Gate Scoring
- **1.0** — All criteria pass
- **0.5–0.9** — Minor issues, mechanically fixable
- **0.1–0.4** — Significant failures; multiple criteria fail
- **0.0** — Complete gate failure

#### Score Dimensions

| Dimension | Gate | Weight |
|---|---|---|
| input_verification | G1 | 1.0 |
| traceability | G2 | 2.0 |
| ac_coverage | G3 | 1.5 |
| ac_fidelity_grounding | G4 | 2.0 |
| scope_compliance | G5 | 1.5 |
| testing_level_accuracy | G6 | 1.0 |
| abstraction_and_data_safety | G7 | 1.0 |
| format_and_determinism | G8 | 1.0 |

#### Overall Score Computation
overall_score = (
    input_verification × 1.0 +
    traceability × 2.0 +
    ac_coverage × 1.5 +
    ac_fidelity_grounding × 2.0 +
    scope_compliance × 1.5 +
    testing_level_accuracy × 1.0 +
    abstraction_and_data_safety × 1.0 +
    format_and_determinism × 1.0
) / 11.0 × 10.0

Weights reflect downstream impact:
- **2.0x** — Traceability, AC fidelity (fabricated or distorted behaviour becomes false truth for every test case)
- **1.5x** — Coverage, scope (gaps or path expansion corrupt the Test Case Generator's input)
- **1.0x** — Input verification, level, abstraction, format

#### Pass/Fail Threshold
- **Pass:** overall_score ≥ 7.0 AND zero fabrication findings (G2, G4) AND zero uncovered ACs without a genuine warning (G3) AND zero PII/credentials (G7)
- **Fail:** any of the above not met

#### Final Decision Rules

| Condition | Decision | Publish to Jira |
|---|---|---|
| All gates pass, no fixes needed | approved | Yes |
| All gates pass after mechanical fixes | fixed_and_approved | Yes (fixed version) |
| Any failure needing human judgment | escalate_to_hitl | No |
| Fabricated feature_key/AC or invented behaviour that cannot be removed mechanically | escalate_to_hitl | No |
| AC uncovered with no genuine warning | escalate_to_hitl | No |
| Writer INSUFFICIENT_CONTEXT confirmed genuine | approved | No (nothing to publish) |

### Mechanical Fix Policy

The evaluator MAY fix the following WITHOUT escalation:
- Renumber TS-IDs to the deterministic order
- Correct testing_level casing/spelling to the verbatim Test Levels name
- Re-level a scenario when TP-04 gives one unambiguous answer from AC text
- Remove scenarios that are out of scope (path expansions, boundary, NFR, adversarial) when the AC remains covered by another scenario
- Merge exact or near-duplicate scenarios for the same AC
- Remove extra fields (scenario_type, jira_key) from writer output
- Replace a paraphrased message in expected_result with the exact AC quote
- Replace technical terms or invented screen names in navigable_path with generic business steps
- Replace real-looking PII, credentials, or secrets in test_data with safe placeholders
- Add or remove warning codes (AC_ID_ASSIGNED, LEVEL_UNDETERMINED, NO_ACS_ON_FEATURE, DUPLICATE_AC_KEY) when source data makes the correction certain

The evaluator MUST escalate the following:
- Any AC with no scenario and no genuine AMBIGUOUS_AC (evaluator never generates scenarios)
- Fabricated feature_key or AC ID, or scenario behaviour with no AC source
- expected_result or pre_condition that contradicts the AC
- Disputed AMBIGUOUS_AC (AC may or may not be testable as written)
- Testing level where TP-04 allows more than one reasonable answer
- Conflict between Feature description and AC that affects behaviour
- DUPLICATE_AC_KEY in source Jira data
- Removing an out-of-scope scenario would leave its AC uncovered
