# L0 Test Scenario — Evaluation Criteria

**Knowledge Base:** kb-L0-test-scenario-eval  
**Consumed by:** L0-test-scenario-evaluator  
**Purpose:** Rubric for independently evaluating Test Scenarios produced by `L0-test-scenario-writer`. Every criterion is binary pass/fail. The evaluator must re-derive results from freshly fetched Jira and Confluence data. Never trust the writer's Feature inventory, AC inventory, scenario content, or self-assessment.

**Source artifacts:** Scenario file from Blob Storage (`<wf-execution-id>/test_scenarios.json`), source Epic and its valid child Features + Feature ACs (Jira Reader), and the Test Strategy (Confluence Reader: Test Levels table, Test Types `Functional acceptance` row, TP-04 only).

HLD, LLD, API contracts, and code are out of bounds.

**Source authority:**

```text
Epic
  -> evaluation scope and business context only

Feature
  -> Feature-specific context and explicit relationships only

Feature Acceptance Criteria
  -> sole authority for expected test behaviour

Test Strategy
  -> testing-level authority
```

Epic Acceptance Criteria, Feature descriptions, Constraints, Dependencies, Risks, and MVP information must not independently create expected test behaviour.

**Scenario definition:** A Test Scenario states WHAT business behaviour a Feature AC requires to be tested. Positive/negative path expansion belongs to the downstream Test Case Generator and is out of scope for the writer and evaluator.

**Scenario template (exactly these fields):**

- `test_scenario_id`
- `SourceIssueId`
- `acceptance_criteria_id`
- `testing_level`
- `issueType`
- `summary`
- `description`
  - `Pre-condition`
  - `Test Data`
  - `Navigable Path`
  - `Expected Result`
- `label`

`SourceIssueId` must be the real Jira key of the source **Feature**, not the Epic.

`issueType` must always be exactly `Task`.

---

### Evaluation Gates

#### Gate 1 — Input Verification

| Criterion | Pass | Fail |
|---|---|---|
| Source Epic authentic | The writer's `epic_read` identifies the Epic returned by the re-fetched Jira data | Epic missing, fabricated, mistyped, or resolves to a non-Epic work item |
| Feature inventory rebuilt | Evaluator independently identifies all valid Features under the re-fetched Epic | Writer's Feature list is trusted without independent reconstruction, or a valid Feature is missed |
| Non-Feature children excluded | Tasks, existing Test Scenarios, unrelated items, malformed children, and downstream artifacts are excluded | Any non-Feature child is treated as a source Feature |
| AC inventory matches Jira | Every `(SourceIssueId, AC ID)` used by the writer exists within a valid re-fetched Feature, and every re-fetched Feature AC is accounted for | Writer adds, drops, alters, or attributes ACs incorrectly |
| AC IDs assigned correctly | IDs are assigned only to ACs without Jira IDs as `AC-01`, `AC-02`... in source order | IDs assigned to ACs that already have IDs, or assigned in the wrong order |
| AC-less Features handled correctly | Valid Features with genuinely zero ACs have no generated scenarios | Feature with ACs skipped, or AC-less Feature treated as containing requirements |
| Duplicate AC keys identified | Every duplicate `(SourceIssueId, AC ID)` in source is identified | Duplicate missed |
| INSUFFICIENT_CONTEXT genuine | If writer halted, the stated reason holds against re-fetched sources | Writer halted although sources were sufficient |

**Evaluation method:** Re-fetch the source Epic from Jira. Independently discover valid Features beneath it. Exclude non-Feature children and existing generated Test Scenario Tasks. Rebuild the AC inventory keyed on `(SourceIssueId, AC ID)`. Diff the rebuilt inventory against scenarios in the Blob file.

The writer's `features_read` output is informational only and is never authoritative.

---

#### Gate 2 — Traceability

| Criterion | Pass | Fail |
|---|---|---|
| SourceIssueId authentic | Every SourceIssueId identifies a valid Feature belonging to the re-fetched source Epic | SourceIssueId identifies the Epic, a non-Feature child, unrelated Jira issue, generated Task, or fabricated/mistyped issue |
| AC ID authentic | Every `(SourceIssueId, AC ID)` pair exists within the identified Feature, or follows the source-order AC ID assignment rule | Fabricated pair or AC attached to the wrong Feature |
| Feature relationship valid | Scenario's SourceIssueId belongs to the source Epic | Scenario points to a Feature outside the Epic |
| Behaviour traceable | Scenario behaviour is found in its referenced Feature AC | Scenario cites one AC but tests another AC's behaviour or behaviour sourced only from contextual information |

**Evaluation method:** Look up each scenario's `(SourceIssueId, acceptance_criteria_id)` in the independently rebuilt Feature AC inventory. Verify the Feature belongs to the source Epic. Compare scenario behaviour against the cited Feature AC.

---

#### Gate 3 — AC Coverage

| Criterion | Pass | Fail |
|---|---|---|
| Every Feature AC covered | Every AC belonging to every valid Feature under the Epic has ≥1 scenario, or genuinely has no observable outcome | Any testable Feature AC skipped |
| Skipped ACs genuine | AC skipped only when it contains no observable outcome or cannot be tested as written | Testable AC skipped, or untestable AC given a scenario |
| Distinct behaviours covered | When a Feature AC explicitly states multiple distinct behaviours, each is represented | Explicitly stated behaviour has no scenario |
| Rejection-type ACs represented | If the Feature AC states rejection/error/prohibition behaviour, that behaviour is represented | Rejection AC converted into an invented success scenario |
| Epic ACs not independently expanded | Epic AC is treated as context and parent intent only | Additional scenario created solely because behaviour appears at Epic level |

**Evaluation method:** For every AC in the independently rebuilt Feature AC inventory, count linked scenarios. Split Feature AC text into explicitly stated behaviours and verify each is represented.

Do not calculate coverage from the writer's `features_read` list.

Do not require independent coverage for Epic ACs.

---

#### Gate 4 — AC Fidelity & Grounding

| Criterion | Pass | Fail |
|---|---|---|
| Expected Result traceable | Observable outcome stated in the Feature AC; nothing added | Outcome invented, extended, weakened, or contradicts the Feature AC |
| Messages verbatim | Error/confirmation messages are quoted exactly when explicitly stated in the Feature AC | Message paraphrased or invented |
| Pre-condition grounded | State comes from the Feature AC; actor role may come from Feature or Epic context only when explicitly stated | Invented states, roles, permissions, or behavioural conditions |
| Summary faithful | Summary represents Feature AC behaviour without reinterpretation | Meaning changed or behaviour introduced |
| Context used safely | Epic and Feature context enrich terminology or wording only | Context defines, extends, or overrides expected behaviour |
| No invented behavioural entities | No invented states, limits, rules, errors, messages, or required outcomes | Behavioural entity absent from the Feature AC is introduced |
| Feature AC wins | Feature AC overrides conflicting Feature or Epic context | Epic/Feature context used to change AC behaviour |
| Context-only fields remain contextual | Epic ACs, Constraints, Dependencies, Risks, MVP Classification/Rationale do not independently define Expected Result | Expected behaviour derived from a contextual field instead of Feature AC |

**Evaluation method:** Compare each behavioural field against the cited Feature AC.

Feature and Epic context may support wording, actor identification, business terminology, and Navigable Path context where explicitly stated.

Any expected behaviour not traceable to the Feature AC is a fail.

---

#### Gate 5 — Scenario Scope

| Criterion | Pass | Fail |
|---|---|---|
| No path expansion | No positive/negative, alternate, boundary, or variant scenarios beyond Feature AC-stated behaviours | AC expanded into invented success/failure variants |
| No near-duplicates | No two scenarios represent materially the same AC behaviour | Near-duplicate scenarios present |
| No test-case detail | Zero numbered execution steps, TC IDs, implementation assertions, or per-field validation lists | Test-case-level content present |
| No Epic-derived scenarios | Every scenario originates from a Feature AC | Scenario generated solely from Epic summary, Epic AC, pillar, constraint, risk, or other Epic content |
| No implementation-derived behaviour | Nothing sourced from HLD, LLD, API contracts, or code | Implementation-derived scenario |

**Evaluation method:** For each Feature AC with >1 scenario, confirm every additional scenario maps to a separate behaviour explicitly present in the Feature AC. Scan for test-case patterns such as `TC-`, `Step 1`, or implementation assertions.

---

#### Gate 6 — Testing Level

| Criterion | Pass | Fail |
|---|---|---|
| Exactly one level | Each scenario has one `testing_level` | Missing or multiple levels; same scenario duplicated at several levels |
| Level verbatim & allowed | Level matches the Test Levels table exactly and appears in the Functional acceptance row | Invented/altered level or level not allowed for functional acceptance |
| TP-04 applied | Lowest allowed level capable of proving the required behaviour is selected | Level higher or lower than the source evidence justifies |
| Explicit dependencies used correctly | An explicitly stated Feature dependency may support Integration where the behaviour genuinely spans the dependency | Integration inferred merely because Features coexist under the Epic |
| Epic membership not used as integration evidence | Epic context helps understand scope but Feature co-membership alone does not trigger a higher level | Integration/End-to-end selected solely because Features share an Epic or pillar |
| UI journey handled correctly | Explicit user journey through UI uses the appropriate End-to-end level where allowed | End-to-end selected without sufficient source evidence |
| Undetermined level handled | Where source material gives insufficient level signal, lowest allowed functional level is used | Higher level used without source evidence |
| Level label matches | `label[2]` equals `testing_level` with spaces replaced by hyphens | Mismatch |

**Evaluation method:** Re-extract allowed levels and their `proves` definitions from the freshly fetched Test Strategy. Re-derive level using TP-04 from the Feature AC plus explicitly stated Feature/Epic scope and dependencies.

Never infer Integration solely from Epic membership, shared pillar, conceptual similarity, or adjacency.

---

#### Gate 7 — Abstraction & Data Safety

| Criterion | Pass | Fail |
|---|---|---|
| Navigable Path business-level | Business journey; app, workflow, actor, or screen names used only when explicitly present in Feature AC, Feature, or Epic context | Endpoints, HTTP methods, DB tables, implementation components, or invented screens |
| Context does not add behaviour | Epic/Feature context only contextualizes the journey | Navigable Path introduces new required system behaviour |
| Test Data mock only | Realistic mock business values and safe placeholders | Real PII, live credentials, secrets, or tokens |
| Test Data adds no rules | Data does not introduce limits, formats, mappings, or rules absent from source behaviour | Data implies unstated business rules |

**Evaluation method:** Scan Navigable Path for technical patterns such as `/api`, `GET`, `POST`, database/table terminology, or implementation components. Scan Test Data for PII and credential patterns. Cross-check named business/UI elements against Feature AC, Feature description, and Epic context.

---

#### Gate 8 — Format & Determinism

| Criterion | Pass | Fail |
|---|---|---|
| Template exact | Exactly the scenario template fields; `description` has exactly the four defined keys; required values non-empty; no `scenario_type`, `jira_key`, `publish_action`, `parentKey`, or duplicate SourceIssueId | Missing, extra, duplicate, or empty required fields |
| Issue type exact | `issueType` is exactly `Task` | Missing `issueType` or any other value |
| SourceIssueId exact | `SourceIssueId` is the real Jira key of the source Feature | Epic key, logical Feature ID, `parentKey`, or unrelated key used |
| Summary format | Summary starts with `[TS-XXX] Verify that` using its own `test_scenario_id` | Missing or mismatched prefix |
| Label exact | `label` contains exactly `ai-generated`, the agent label (`L0-test-scenario-writer` or `L0-e2e-scenario-writer`), the hyphenated layer label (e.g. `L2-Service`), and the trace-ID fingerprint `[SourceIssueId]-[acceptance_criteria_id]-[test_scenario_id]` | Missing, reordered, or mismatched label; `source-*` or level labels evaluated in G9 |
| TS-ID ordering | `TS-001...` sequential per Feature; Features ascending by Jira key; ACs source order; behaviours AC order | Gaps, duplicates, cross-Feature numbering, or nondeterministic ordering |
| Blob file valid | `test_scenarios.json` parses as JSON and contains only scenario objects | Malformed/unparseable file or unrelated content |

**Evaluation method:** Schema-check every scenario. Verify `issueType = Task`, Feature `SourceIssueId`, absence of `parentKey`, deterministic ordering, labels, and fingerprints.

---

#### Gate 9 — Scenario Labels

| Criterion | Pass | Fail |
|---|---|---|
| Trace-ID fingerprint present | `label` contains exactly one entry matching `[SourceIssueId]-[acceptance_criteria_id]-[test_scenario_id]` | Fingerprint absent, malformed, or duplicated |
| Source label present | `label` contains exactly one `source-<KEY>` entry | `source-*` label absent or more than one present |
| Source key consistent | The `<KEY>` in the `source-*` label is identical to the Jira key at the start of the trace-ID fingerprint | Key in `source-*` differs from the leading key in the fingerprint |
| Source issue exists | The key in `source-*` resolves to a real Jira issue when re-fetched | Key does not resolve or Jira returns no issue |
| Level label present | `label` contains exactly one level label | No level label present, or more than one level label present |
| Level label allowed | The level label is one of `level-feature`, `level-task`, `level-e2e` | `level-api`, `level-nfr`, or any other value used as a level label |
| Level matches source issue type | `level-feature` ↔ source issue type is Feature; `level-task` ↔ source issue type is Task; `level-e2e` ↔ source issue type is Epic | Level label does not match the re-fetched source issue type |
| E2E multi-Feature coverage | `level-e2e` scenarios only: the scenario demonstrably covers at least two distinct valid Features of the Epic | Fewer than two Features covered |
| E2E business-result end | `level-e2e` scenarios only: the Expected Result is a complete business outcome, not an intermediate system state | Expected Result is a partial or technical state |
| E2E no step duplication | `level-e2e` scenarios only: the Navigable Path and Expected Result are not copied or trivially paraphrased from an existing Feature-level scenario | Steps or result duplicated from a Feature scenario |
| E2E per-Epic cap | `level-e2e` scenarios only: no Epic has more than five `level-e2e` scenarios in the evaluated set | More than five `level-e2e` scenarios present for a single Epic |

**Evaluation method:** For every scenario, extract the `label` array from the Blob file. Locate the trace-ID fingerprint, the `source-*` entry, and the level label. Re-fetch the source issue from Jira using the key from the `source-*` label and record its issue type. Compare the level label against the issue type mapping. For `level-e2e` scenarios, additionally cross-check the scenario's Navigable Path and SourceIssueId against the valid Feature inventory and existing Feature-level scenarios.

The trace-ID fingerprint must already be present before any source or level label check is performed. Checks for source key consistency, source existence, and level-type match are always derived from freshly fetched Jira data, never from the writer's metadata.

---

### Scoring Model

#### Per-Gate Scoring

- **1.0** — All criteria pass
- **0.5–0.9** — Minor issues, mechanically fixable
- **0.1–0.4** — Significant failures; multiple criteria fail
- **0.0** — Complete gate failure

#### Score Dimensions

| Dimension | Gate | Weight |
|---|---|---:|
| input_verification | G1 | 1.0 |
| traceability | G2 | 2.0 |
| ac_coverage | G3 | 1.5 |
| ac_fidelity_grounding | G4 | 2.0 |
| scope_compliance | G5 | 1.5 |
| testing_level_accuracy | G6 | 1.0 |
| abstraction_and_data_safety | G7 | 1.0 |
| format_and_determinism | G8 | 1.0 |
| scenario_labels | G9 | 1.0 |

#### Overall Score Computation

```text
overall_score = (
    input_verification × 1.0 +
    traceability × 2.0 +
    ac_coverage × 1.5 +
    ac_fidelity_grounding × 2.0 +
    scope_compliance × 1.5 +
    testing_level_accuracy × 1.0 +
    abstraction_and_data_safety × 1.0 +
    format_and_determinism × 1.0 +
    scenario_labels × 1.0
) / 12.0 × 10.0
```

Weights reflect downstream impact:

- **2.0x** — Traceability and AC fidelity. Fabricated or distorted behaviour becomes false truth for downstream Test Cases.
- **1.5x** — Coverage and scope. Missing AC behaviour or scenario expansion corrupts Test Case Generator input.
- **1.0x** — Input verification, testing level, abstraction/data safety, format, and scenario labels.

#### Pass/Fail Threshold

- **Pass:** `overall_score >= 7.0` AND zero fabrication findings in G2/G4 AND zero testable Feature ACs left uncovered in G3 AND zero PII/credentials in G7 AND zero blocking label failures in G9.
- **Fail:** Any of the above conditions is not met.

---

#### Final Decision Rules

| Condition | Decision | Publish to Jira |
|---|---|---|
| All gates pass, no fixes needed | `approved` | Yes |
| All gates pass after mechanical fixes | `fixed_and_approved` | Yes, fixed version |
| Any failure needing human judgment | `escalate_to_hitl` | No |
| Fabricated Feature/SourceIssueId/AC or invented behaviour that cannot be mechanically removed | `escalate_to_hitl` | No |
| Valid Feature under Epic omitted and one or more testable ACs left uncovered | `escalate_to_hitl` | No |
| Testable Feature AC left uncovered | `escalate_to_hitl` | No |
| Writer `INSUFFICIENT_CONTEXT` confirmed genuine | `approved` | No, nothing to publish |

---

### Mechanical Fix Policy

The evaluator MAY fix the following WITHOUT escalation:

- Renumber TS-IDs into deterministic per-Feature order and update the summary prefix and `label[3]` fingerprint accordingly.
- Correct `testing_level` casing/spelling to the verbatim Test Levels name and update `label[2]`.
- Re-level a scenario when TP-04 gives one unambiguous answer from the re-fetched Feature AC, explicit Feature relationships/dependencies, and Test Strategy.
- Correct `issueType` to `Task`.
- Correct `label[0]` or `label[1]` when the required value is deterministic.
- Correct `SourceIssueId` only when the correct Feature Jira key is unambiguous from the scenario's valid `(Feature, AC)` relationship.
- Remove `parentKey` or other prohibited extra fields.
- Remove scenarios that are out of scope, including path expansions or variants, when their Feature AC remains covered by another valid scenario.
- Merge exact or near-duplicate scenarios for the same Feature AC when the AC remains fully covered.
- Remove extra fields such as `scenario_type`, `jira_key`, or `publish_action`.
- Replace a paraphrased explicitly stated message in Expected Result with the exact Feature AC quote.
- Replace technical terms or invented screen names in Navigable Path with generic business steps.
- Replace real-looking PII, credentials, or secrets in Test Data with safe placeholders.

The evaluator MUST escalate the following:

- Any testable Feature AC with no scenario. The evaluator never generates scenarios.
- A valid Feature under the Epic omitted by the writer when that omission leaves testable Feature ACs uncovered.
- Fabricated Feature, SourceIssueId, or AC ID where the correct source cannot be mechanically and unambiguously established.
- Scenario behaviour with no Feature AC source.
- Expected Result or Pre-condition that contradicts the Feature AC.
- Behaviour derived only from an Epic AC, Epic summary, Constraint, Dependency, Critical Risk, MVP Rationale, or other contextual field.
- Disputed skipped AC where the AC may or may not be testable as written.
- Testing level where TP-04 permits more than one reasonable answer.
- Conflict between Epic context, Feature description, and Feature AC that affects required behaviour.
- Duplicate `(SourceIssueId, AC ID)` in the source Jira Feature inventory.
- Removing an out-of-scope or duplicate scenario would leave its Feature AC uncovered.
- Missing trace-ID fingerprint in `label` (G9). The fingerprint is a prerequisite; without it, source and level checks cannot proceed.
- Level label that conflicts with the re-fetched source issue type (G9).
- `level-api` or `level-nfr` present in `label` (G9).
- Multiple level labels present in `label` (G9).
- `level-e2e` scenario that fails any of the multi-Feature, business-result, step-duplication, or per-Epic-cap checks (G9).

The evaluator MAY fix the following label issues WITHOUT escalation (G9):

- **Missing `source-<KEY>` label:** Add it only when the correct key can be taken directly and unambiguously from the trace-ID fingerprint already present in the scenario's `label`. The added entry is `source-<KEY>` where `<KEY>` is the leading Jira key in the fingerprint.
- **Missing level label:** Add it only when the correct value can be taken directly and unambiguously from the Jira issue type of the re-fetched source issue (`level-feature` for Feature, `level-task` for Task, `level-e2e` for Epic). If the source issue type is ambiguous or unavailable, escalate.
