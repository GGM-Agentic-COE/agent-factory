# Common Testing Standards — Knowledge Base
 
## kb-L0-testing-standards v1.0.0
 
Enterprise testing standards and governance rules shared by testing agents and downstream testing components.
 
---
 
## 1. Purpose and Scope
 
This knowledge base defines reusable testing standards, controlled terminology, traceability rules, quality expectations, and governance requirements.
 
It does **not** define the responsibility, runtime input contract, or output schema of any individual testing agent. Each agent's prompt and artifact contract determines:
 
- The agent's responsibilities and boundaries
- Required and optional runtime inputs
- Required output schema
- Artifacts the agent may create
- The subset of this KB applicable to its task
 
This KB may be consumed by:
 
- Test Strategy Agent
- Test Scenario Agent
- Test Case Writer Agent
- Adversarial Test Case Writer Agent
- Test Case Evaluator Agent
- Synthetic Test Data Agent
- Test Automation or Script Generation Agent
- Test Execution and Defect-Triage components
- Test-management integration components
 
An agent MUST NOT perform another agent's responsibility merely because the related standard exists in this KB.
 
---
 
## 2. Source Grounding
 
### 2.1 Mandatory rules
 
- Testing artifacts MUST be generated only from approved runtime inputs and approved knowledge bases.
- Testing agents MUST NOT invent requirements, fields, validations, business rules, roles, permissions, statuses, API responses, error messages, workflow transitions, integrations, dependencies, risks, data values, or expected behavior.
- Supplied source identifiers MUST be preserved exactly.
- Missing, ambiguous, or contradictory information MUST be reported as a review issue.
- An explicit review flag MUST be preferred over an unsupported assumption.
- Derived testing artifacts MUST remain within the scope of their approved upstream sources.
 
### 2.2 General source precedence
 
When multiple approved sources apply, use the following general precedence unless the agent contract defines a stricter artifact-specific order:
 
1. Approved requirements and acceptance criteria
2. Approved feature and story context
3. Approved test strategy
4. Approved test scenarios
5. Approved requirement, impact, dependency, architecture, and risk context
6. Existing approved testing artifacts
7. This testing standards KB
 
This KB governs **how** testing artifacts are authored and validated. It MUST NOT override requirement-specific behavior supplied at runtime.
 
### 2.3 Conflict handling
 
- A lower-precedence source MUST NOT override an explicit higher-precedence source.
- Contradictions MUST be reported with the conflicting source IDs.
- An agent MUST NOT silently select one interpretation.
- If the conflict prevents a reliable artifact, the artifact MUST be marked `human-review-required`.
 
---
 
## 3. Common Runtime Governance
 
Runtime inputs differ by agent. An agent MUST validate only the inputs required by its own contract.
 
Common validation rules:
 
| Condition | Required behavior |
|---|---|
| Required source ID is missing | Stop affected final-ID allocation and request human review |
| No upstream traceability is available | Report a traceability gap |
| Expected behavior is contradictory | Report the contradiction; do not choose silently |
| Required rule is unavailable | Use a review marker; do not invent the rule |
| Existing artifacts are unavailable | Proceed only when allowed and record that duplicate comparison was not performed |
| Priority cannot be derived | Use `review` unless an approved project default is supplied |
| Exact data value is unavailable | Describe the data requirement or constraint instead of fabricating a value |
| Security-sensitive, destructive, regulated, or production-like access is involved | Require approved human review |
 
---
 
## 4. Common Identifier Standards
 
### 4.1 Identifier principles
 
Every managed testing artifact identifier MUST be:
 
- Stable
- Unique within its configured system of record
- Resolvable to exactly one artifact
- Preserved across downstream artifacts
- Allocated by an approved allocator or system of record
 
### 4.2 Temporary identifiers
 
If a stable identifier cannot be allocated:
 
- The responsible agent MAY use an explicitly temporary identifier defined by its artifact contract.
- The artifact MUST be marked `human-review-required`.
- Temporary identifiers MUST NOT be represented as final system-of-record identifiers.
 
### 4.3 Naming principles
 
Artifact titles SHOULD:
 
- Describe a specific behavior, risk, objective, or outcome
- Include the relevant condition where needed
- Use approved domain terminology
- Avoid vague wording such as `Test feature`, `Validate system`, or `Verify everything works`
 
Recommended behavioral title pattern when applicable:
 
```text
<Expected behavior> when <condition or action>
```
 
---
 
## 5. Common Testing Classification
 
Agents MUST use the controlled values below when their output contract requires the corresponding classification.
 
### 5.1 Test level
 
```yaml
test_level:
  - component
  - integration
  - system
  - end-to-end
  - review
```
 
`review` MUST be used when the approved context does not support a reliable test-level classification and the agent contract permits it.
 
### 5.2 Test or coverage type
 
```yaml
test_type:
  - positive
  - negative
  - boundary
  - validation
  - permission
  - integration
  - regression
  - exception
  - adversarial
```
 
### 5.3 Priority
 
```yaml
priority:
  - critical
  - high
  - medium
  - low
  - review
```
 
Priority MUST be derived only from approved runtime impact, criticality, or risk context.
 
| Priority | Apply only when approved context establishes |
|---|---|
| `critical` | Failure blocks a critical flow or creates a severe approved risk |
| `high` | Failure significantly affects an important capability |
| `medium` | Failure has limited impact or an approved workaround |
| `low` | Behavior is low-impact or optional |
| `review` | Impact cannot be derived reliably |
 
### 5.4 Automation suitability
 
```yaml
automation_candidate:
  - "yes"
  - "no"
  - review
```
 
| Value | Rule |
|---|---|
| `yes` | Repeatable, deterministic, stable, execution-accessible, and valuable for repeated validation |
| `no` | Requires unsupported physical interaction, subjective human judgment, or one-time exploratory investigation |
| `review` | Feasibility depends on unavailable interface, environment, tool, access, or stability information |
 
Classification as an automation candidate does not authorize an agent to generate automation code unless automation generation is explicitly part of that agent's contract.
 
---
 
## 6. Test Design Techniques
 
Testing agents MUST apply a technique only when the approved runtime input contains sufficient information to support it.
 
| Technique | Apply when | Required behavior |
|---|---|---|
| Equivalence partitioning | Inputs form behaviorally equivalent valid or invalid classes | Select representative values or data requirements from each relevant class |
| Boundary-value analysis | An explicit minimum, maximum, length, range, date, quantity, or threshold exists | Consider applicable values around each supplied boundary |
| Decision table | Outcome depends on multiple supplied conditions | Map testing artifacts to supported condition combinations |
| State-transition testing | Approved states and transitions are provided | Cover relevant permitted and prohibited transitions |
| Pairwise testing | Many independent parameters create excessive combinations | Reduce combinations while preserving mandatory and high-risk combinations |
| Risk-based testing | Approved context identifies business, security, integration, operational, or data-integrity risk | Increase depth or priority only as supported by the supplied risk |
 
### 6.1 Technique safeguards
 
- A boundary MUST NOT be inferred when none is supplied.
- States or transitions MUST NOT be invented.
- A condition combination MUST NOT be removed unless the approved context marks it impossible or out of scope.
- Data variations SHOULD be parameterized when the workflow and expected outcome pattern remain the same.
- Pairwise reduction MUST NOT remove mandatory, regulatory, critical, or explicitly high-risk combinations.
 
---
 
## 7. Coverage Standards
 
### 7.1 Coverage definitions
 
| Coverage type | Standard |
|---|---|
| Positive | Covers explicitly defined successful behavior |
| Negative | Covers supplied invalid, rejected, or prohibited behavior |
| Boundary | Covers behavior at and around explicit limits |
| Validation | Covers supplied mandatory, format, allowed-value, uniqueness, conditional, or cross-field rules |
| Permission | Covers supplied actor, role, entitlement, or authorization rules |
| Integration | Covers documented dependency behavior and documented failure handling |
| Exception | Covers only approved exception behavior |
| Regression | Covers approved existing behavior identified as being at risk |
| Adversarial | Covers supported failure, misuse, abuse, rule-violation, resilience, or security-oriented conditions within approved scope |
 
### 7.2 Responsibility boundary
 
- The Test Scenario Agent identifies scenario-level coverage intent when that responsibility is assigned by its contract.
- A Test Case Writer implements supplied scenario coverage as detailed test specifications.
- An Adversarial Test Case Writer generates adversarial cases only from approved scenarios and supporting context.
- An evaluator verifies coverage, grounding, consistency, and completeness; it MUST NOT silently repair or replace the generator's artifact unless its contract explicitly permits correction.
- A downstream component MUST NOT reinterpret a coverage classification without recording the change and its approved basis.
 
### 7.3 Coverage safeguards
 
- Negative coverage MUST NOT be generated from unsupported assumptions.
- Boundary coverage MUST be generated only when explicit limits exist.
- Permission coverage MUST rely on supplied roles or authorization rules.
- Integration coverage MUST rely on documented integration behavior.
- Regression coverage MUST rely on approved impact or change context.
- Adversarial coverage MUST remain tied to approved scope, rules, risks, interfaces, or behaviors.
 
Every required source behavior MUST be covered or reported as a coverage gap by the agent responsible for coverage validation.
 
---
 
## 8. BDD and Gherkin Standards
 
These standards apply only when an agent's artifact contract requires Gherkin or BDD output.
 
### 8.1 General pattern
 
```gherkin
Feature: <business capability>
 
  @<ARTIFACT-ID>
  @<SOURCE-ID>
  Scenario: <specific behavior under test>
    Given <approved initial state>
    And <additional approved precondition>
    When <single primary action or event>
    Then <observable expected result>
    And <additional expected result>
```
 
### 8.2 Keyword rules
 
| Keyword | MUST contain | MUST NOT contain |
|---|---|---|
| `Given` | Initial state, actor state, data state, or dependency state | Primary user action |
| `When` | Primary action or event | Multiple unrelated workflows |
| `Then` | Observable and verifiable result | Vague claims such as `works correctly` |
| `Background` | Preconditions common to every scenario in the feature | Scenario-specific data or actions |
| `Scenario Outline` | One flow with meaningful data variations | Different business flows forced into one table |
 
### 8.3 Gherkin safeguards
 
- Tags MUST preserve approved identifiers exactly.
- A scenario MUST represent an independently understandable behavior.
- Illustrative values in documentation MUST NOT be reused as runtime values unless they are supplied or approved at runtime.
- Gherkin output MUST NOT replace a required structured artifact unless the applicable agent contract permits it.
 
---
 
## 9. Preconditions and State
 
### 9.1 Preconditions
 
- Preconditions MUST describe required state.
- Preconditions MUST NOT contain execution actions such as clicking, entering, navigating, or submitting.
- Preconditions MUST use approved domain terminology.
- Shared preconditions SHOULD be reusable without hiding scenario-specific state.
- If no additional state is required, the applicable artifact MAY state `No additional preconditions`.
 
| Good precondition | Invalid precondition |
|---|---|
| User is authenticated | Click the Login button |
| User has the required permission | Navigate to the page |
| An approved reference record exists | Enter the record details |
 
### 9.2 Postconditions
 
- Postconditions MUST be included only when supported by approved runtime context.
- Cleanup, rollback, persistence, notification, audit, or resulting state MUST NOT be invented.
- If the output schema requires a value and none is supplied, use `No additional postconditions specified` or a review marker as permitted by the agent contract.
 
---
 
## 10. Test Data Standards
 
### 10.1 Common data classifications
 
```yaml
data_classification:
  - valid
  - invalid
  - boundary
  - reference
  - synthetic
```
 
### 10.2 Data rules
 
- Testing artifacts MUST describe the category and constraints of required data.
- Exact data values MUST NOT be fabricated when only a requirement is available.
- Production personal, customer, financial, confidential, credential, token, key, certificate, or secret data MUST NOT be copied into generated artifacts.
- Synthetic or formally approved masked data SHOULD be used.
- Boundary values MUST come from supplied requirements.
- Invalid data MUST violate a supplied rule, not an assumed rule.
- Data dependencies and referential constraints MUST be preserved when provided.
- A Synthetic Test Data Agent MUST follow the constraints supplied by upstream testing artifacts and MUST NOT introduce new business rules.
 
### 10.3 Generic requirement pattern
 
```yaml
test_data_requirement:
  data_id: string
  description: string
  classification: valid | invalid | boundary | reference | synthetic
  constraints:
    - string
```
 
This pattern is illustrative. Each agent MUST follow its own approved output schema.
 
---
 
## 11. Actions, Steps, and Expected Results
 
These rules apply when an artifact contains executable actions or steps.
 
### 11.1 Action and step rules
 
- Each step MUST contain one clear action.
- Each action MUST have a directly related expected result when the artifact contract requires step-level results.
- Steps MUST use runtime domain terminology consistently.
- Unrelated actions or assertions MUST NOT be combined.
- UI implementation details SHOULD be avoided unless required by the approved source or necessary for the assigned test level.
- Steps MUST be independently understandable and ordered logically.
 
### 11.2 Expected-result rules
 
Expected results MUST be:
 
- Observable
- Deterministic
- Measurable or verifiable
- Linked to approved behavior
- Specific enough to determine pass or fail
 
Expected results MUST NOT contain:
 
- Vague claims such as `The system works correctly`
- Unsupported exact messages, codes, statuses, events, database changes, notifications, or workflow transitions
- Assumptions about implementation behavior not present in approved inputs
 
If the exact result is unavailable, preserve the relevant source reference and require human review rather than inventing the outcome.
 
---
 
## 12. Traceability
 
### 12.1 End-to-end chain
 
```text
Requirement
  -> Feature
  -> Story
  -> Acceptance Criterion
  -> Test Scenario
  -> Test Case or Adversarial Test Case
  -> Automation Script, when applicable
  -> Execution Result
  -> Defect, when applicable
```
 
Not every artifact is created by every workflow, but each generated artifact MUST link to its approved immediate upstream source and preserve applicable higher-level source IDs.
 
### 12.2 Traceability rules
 
- Source IDs MUST come from approved runtime inputs.
- Missing source IDs MUST NOT be generated.
- Every derived artifact MUST identify its immediate upstream artifact.
- An artifact linked to multiple source items MUST remain atomic and explain the valid grouping when the artifact contract supports such explanation.
- Cross-scenario or cross-requirement artifacts are permitted only when the approved process and artifact contract explicitly allow them.
- Each stable artifact ID MUST resolve to exactly one artifact in the designated registry or system of record.
- Traceability changes MUST be explicit and auditable.
 
### 12.3 Traceability validation
 
The responsible evaluator or integration component MUST verify, as applicable:
 
- Source identifiers exist in the supplied context.
- Identifier values are preserved exactly.
- Upstream and downstream references agree.
- No artifact is orphaned.
- No single identifier resolves to multiple artifacts.
 
---
 
## 13. Reuse and Deduplication
 
### 13.1 Comparison dimensions
 
When existing approved artifacts are supplied, compare:
 
- Objective or behavior being proven
- Preconditions and required state
- Primary action or event
- Expected outcome
- Traceability and requirement coverage
- Test or coverage type
- Data variation
- Permission or role
- State transition
- Risk addressed
 
### 13.2 Rules
 
- Existing approved artifacts MUST be compared when they are supplied and when deduplication is part of the agent's responsibility.
- Reuse or parameterization SHOULD be preferred when only data varies and diagnostic clarity is preserved.
- Separate artifacts MUST be retained when workflow, permission, state transition, expected result, source coverage, or risk differs materially.
- Artifacts MUST NOT be merged when merging reduces failure diagnosis, independent execution, ownership, or traceability.
- If existing artifacts are unavailable, the output MUST state that duplicate detection was not performed when the artifact contract provides a place to record it.
- A suspected duplicate MUST be identified for human review with the candidate artifact reference.
 
---
 
## 14. Security, Privacy, and Environment Safety
 
- Testing agents MUST NOT include production credentials, secrets, access tokens, private keys, or unapproved confidential data.
- Security-sensitive or destructive test activities MUST require approved human review.
- Production-like access MUST NOT be assumed from environment names or supplied endpoints.
- An artifact MUST distinguish a data requirement from an actual sensitive value.
- Regulated or restricted data handling MUST follow approved runtime policies and constraints.
- Testing agents MUST NOT claim that an environment, account, integration, or dataset is safe or approved unless that status is explicitly supplied.
 
---
 
## 15. Test-Management and Integration Boundaries
 
- Common testing artifacts SHOULD be mapping-ready when their agent contract requires downstream integration.
- This KB MUST NOT hardcode project-specific custom-field IDs, workflow IDs, issue types, or integration credentials.
- The designated test-management integration or orchestration component owns project-specific mapping and controlled writes.
- Generation and evaluation agents MUST NOT claim that an artifact was uploaded, created, updated, executed, or synchronized unless their contract explicitly includes that action and the action result is available.
- Upload, synchronization, and execution statuses MUST NOT be inferred from artifact generation.
 
---
 
## 16. Evaluator Standards
 
An evaluator MUST assess the supplied artifact against:
 
- Applicable runtime requirements
- Applicable upstream sources
- The generating agent's output contract
- Applicable rules in this KB
 
### 16.1 Evaluator rules
 
- The evaluator MUST preserve the generator's artifact for traceable assessment.
- It MUST identify failed checks with clear reasons and affected source or artifact IDs.
- It MUST NOT introduce unsupported requirements while evaluating completeness.
- It MUST distinguish an artifact defect from a missing or contradictory upstream input.
- It MUST NOT mark an artifact as passed when a mandatory traceability, grounding, schema, or safety check fails.
- It MUST use `human-review-required` when correctness depends on an unavailable decision.
 
### 16.2 Common validation result
 
```yaml
validation_result:
  status: pass | fail | human-review-required
  failed_checks:
    - check_id: string
      message: string
      affected_artifact_ids: [string]
      source_ids: [string]
  warnings:
    - string
```
 
An evaluator MUST follow its own approved schema when it differs from this illustrative structure.
 
---
 
## 17. Common Quality Gates
 
Before a testing artifact is published to its next approved workflow stage, verify all applicable checks:
 
- [ ] Mandatory fields defined by the agent's output contract are present.
- [ ] Stable IDs are used, or temporary IDs are clearly marked.
- [ ] Supplied source IDs are preserved exactly.
- [ ] Required upstream traceability is present.
- [ ] Required source behavior is covered or reported as a gap.
- [ ] Test-design techniques are applied only where supported.
- [ ] Preconditions describe state rather than actions.
- [ ] Actions and steps are atomic where applicable.
- [ ] Expected results are observable and requirement-grounded.
- [ ] No unsupported requirement, behavior, data, status, message, or implementation detail is invented.
- [ ] No production secret, credential, or unapproved confidential data is included.
- [ ] Duplicate comparison is performed or marked unavailable when applicable.
- [ ] Related artifacts agree on IDs, classifications, and traceability.
- [ ] Agent responsibility boundaries are respected.
- [ ] Test-management upload, synchronization, or execution success is not falsely claimed.
- [ ] Review status reflects unresolved ambiguity, risk, or governance requirements.
 
---
 
## 18. Human Review
 
The applicable artifact MUST be marked `human-review-required` when any of the following is true:
 
| Condition | Required response |
|---|---|
| Requirements or approved sources are contradictory | Identify the conflicting source IDs |
| Expected behavior is ambiguous | State the missing decision without inventing it |
| Exact expected result is unavailable | Preserve the source reference and flag review |
| Stable artifact ID cannot be allocated | Use an approved temporary ID |
| Priority cannot be derived | Set priority to `review` when applicable |
| Test level cannot be derived | Set test level to `review` when permitted |
| Integration mapping is unavailable | Produce mapping-ready fields only when required |
| Duplicate is suspected | Provide the candidate artifact reference |
| Automation feasibility is uncertain | Set `automation_candidate: review` when applicable |
| Security-sensitive or destructive behavior is involved | Require approved human review |
| Regulated data or production-like access is involved | Require approved human review |
| Required upstream artifact is missing | Report the missing dependency and affected output |
 
---
 
## 19. Responsibility Matrix
 
| Component | Primary responsibility | MUST NOT assume |
|---|---|---|
| Test Strategy Agent | Define approved testing approach, scope, levels, environments, and governance according to its contract | Detailed scenario or case generation unless explicitly assigned |
| Test Scenario Agent | Define scenario-level coverage intent and traceability | Detailed executable steps or unsupported behavior |
| Test Case Writer Agent | Convert approved scenarios and requirement context into detailed test specifications | New scenario coverage outside approved input or Xray write success |
| Adversarial Test Case Writer Agent | Generate grounded adversarial cases from approved scenarios, rules, risks, and context | Unsupported threats, actors, controls, or requirement behavior |
| Synthetic Test Data Agent | Produce synthetic or masked data aligned with approved constraints | New validations or business rules |
| Test Case Evaluator Agent | Validate grounding, quality, traceability, schema, and coverage | Silent assumption, unsupported repair, or downstream upload |
| Automation or Script Generation Agent | Convert approved automatable specifications into automation assets | Requirement reinterpretation or test-management status |
| Test-Management Orchestrator | Map approved artifacts to project configuration and perform controlled writes | Change artifact meaning without an explicit recorded decision |
| Execution Component | Execute approved tests and record actual outcomes | Claim success without execution evidence |
| Defect-Triage Component | Associate supported execution failures with defects and evidence | Infer a root cause without supporting evidence |
 
---
 
## 20. Glossary
 
| Term | Definition |
|---|---|
| Acceptance criterion | Approved condition defining expected story behavior |
| Test strategy | Approved approach governing the scope and method of testing |
| Test scenario | High-level statement of behavior, condition, or risk to be tested |
| Test case | Executable specification containing required state, data, action, and expected result |
| Adversarial test case | Grounded test specification intended to expose supported failure, misuse, abuse, rule-violation, resilience, or security conditions |
| Gherkin | Structured `Given/When/Then` notation for behavior examples |
| Traceability | Recorded relationship between an artifact and its approved upstream and downstream sources |
| Automation candidate | Classification indicating whether a test is suitable for further automation assessment |
| Runtime context | Requirement-specific information supplied when an agent runs |
| Human review | Required decision or validation by an authorized person when automation cannot safely resolve an issue |
| System of record | Approved platform responsible for authoritative storage or identifier allocation |
| KB | Versioned knowledge base containing reusable standards or domain knowledge |
 
---
 

 
