# W01-Orchestrator: Architecture & Design Workflow — Pipeline Configuration
# ═══════════════════════════════════════════════════════════════
# This file defines the pipeline rules that govern how Steps 1–8 connect,
# error handling, evaluation thresholds, and retry policies.
# Each step prompt (W01-step1 through W01-step8) must be read WITH this file.
# ═══════════════════════════════════════════════════════════════

## PIPELINE FLOW

```yaml
pipeline:
  name: architecture-design-workflow
  steps:
    - id: step1
      prompt: W01-step1-input-validator.md
      input: epic + stories (from Jira or uploaded doc)
      output_to: step2
      gate: validation_result must be "PASS" to proceed
      on_fail: STOP — return rejection reasons to architect

    - id: step2
      prompt: W01-step2-system-discovery.md
      input: step1.output (validated epic + mode + classification)
      output_to: [step3, step4, step5, step6]  # parallel fan-out
      gate: change_impact must have at least one non-empty array
      on_fail: STOP — no changes identified, nothing to design

    - id: step3
      prompt: W01-step3-ux-ui-design.md
      input: step2.output.change_impact (screens_modified + screens_new) + step1.output.ui_changes
      output_to: step7
      skip_if: step1.output.steps_required.step3_ux_ui == false
      gate: all UI stories must have corresponding wireframe
      on_fail: RETRY once, then flag for architect review

    - id: step4
      prompt: W01-step4-api-spec.md
      input: step2.output.change_impact (apis_modified + apis_new) + step1.output.api_changes
      output_to: [step6, step7]  # LLD needs API spec for consistency
      skip_if: step1.output.steps_required.step4_api_spec == false
      gate: OpenAPI YAML must parse without errors
      on_fail: RETRY once (likely syntax error)

    - id: step5
      prompt: W01-step5-architecture-docs.md
      input: step2.output (full change_impact + architecture_decisions)
      output_to: step7
      gate: documents must not contradict step2 decisions
      on_fail: RETRY once

    - id: step6
      prompt: W01-step6-hld-lld.md
      input: step2.output + step4.output (API spec for consistency)
      depends_on: [step4]  # must wait for API spec
      output_to: step7
      gate: LLD entities must match API spec schemas
      on_fail: RETRY once — likely inconsistency with step4

    - id: step8
      prompt: W01-step8-test-creation.md
      input: step1.output (stories+ACs) + step2.output (change_impact) + step4.output (API spec)
      depends_on: [step6]  # runs after LLD is ready (needs domain model for test data)
      gate: coverage_matrix shows 0 gaps, all stories have tests
      on_fail: RETRY once — likely missing scenario for an AC

    - id: step7
      prompt: W01-step7-github-storage.md
      input: ALL artifacts from steps 3, 4, 5, 6, 8
      depends_on: [step3, step4, step5, step6, step8]  # runs LAST — stores everything
      gate: all files valid, no PII, branches created
      on_fail: RETRY once (likely git conflict)
      storage:
        github: design docs + API spec + LLD + automated tests
        jira: test scenarios as sub-tasks under stories
        xray: manual test cases in test set, linked to stories
      produces: execution summary posted to Jira epic

  execution_order: step1 → step2 → [step3, step4, step5] → step6 → step8 → step7
  note: Step 7 runs LAST despite numbering — it is the unified storage/delivery step

  parallelism:
    - [step3, step4, step5] can run in parallel after step2
    - step6 waits for step4 (needs API spec)
    - step7 waits for all (3, 4, 5, 6)

  max_retries_per_step: 1
  total_timeout: 10 minutes
```

## INTER-STEP DATA CONTRACT

Each step must output a JSON object. The orchestrator passes relevant
fields to downstream steps. Here is what each step MUST include in output:

```yaml
step1_output:
  required: [validation_result, mode, epic_summary, classification, steps_required, existing_docs_found]
  passed_to_step2: [mode, epic_summary, classification, existing_docs_found]

step2_output:
  required: [mode, change_impact, architecture_decisions, risks]
  passed_to_step3: [change_impact.screens_modified, change_impact.screens_new, mode]
  passed_to_step4: [change_impact.apis_modified, change_impact.apis_new, mode]
  passed_to_step5: [change_impact, architecture_decisions, mode]
  passed_to_step6: [change_impact, mode]

step3_output:
  required: [files_produced]
  files_produced: [wireframes.md, design-system.md, user-flows.md]
  passed_to_step7: [files_produced with full content]

step4_output:
  required: [api_spec_yaml, changes_summary]
  files_produced: [api-spec.yaml]
  passed_to_step6: [api_spec_yaml]  # for LLD consistency check
  passed_to_step7: [files_produced with full content]

step5_output:
  required: [files_produced]
  files_produced: [solution-architecture.md, integration-architecture.md]
  passed_to_step7: [files_produced with full content]

step6_output:
  required: [files_produced]
  files_produced: [hld.md, lld.md]
  passed_to_step7: [files_produced with full content]

step7_output:
  required: [branches_created, pull_requests, jira_updates, summary]

step8_output:
  required: [test_scenarios, manual_test_cases, automated_test_cases, coverage_matrix, regression_pack, storage_plan]
  storage_targets:
    jira: test_scenarios (as sub-tasks under stories)
    xray: manual_test_cases (in test set, linked to stories)
    github: automated_test_cases.feature_files + step_definitions (in feature branch)
```

## EVALUATION THRESHOLDS (per kb-L0-agent-quality-standards B11)

Each step's output is evaluated before passing to the next step.
These thresholds override the defaults from B11 for this workflow:

```yaml
evaluation_overrides:
  # All steps in this workflow handle regulated financial architecture
  gate:
    faithfulness: {threshold: 0.92}       # Tighter: architecture must be grounded
    hallucination: {threshold: 0.08}      # Tighter: no invented components/endpoints
    correctness: {threshold: 0.85}        # Default: architecture decisions are judgment calls
    relevance: {threshold: 0.90}          # Tighter: every artifact must serve the epic
    toxicity: {threshold: 0.05}           # Locked
    topic_adherence_eval: {threshold: 0.95}  # Default
    topic_adherence_refusal: {threshold: 0.95}  # Locked
    consistency: {threshold: 0.92}        # Tighter: cross-document consistency is critical

  recommended:
    answer_correctness: {threshold: 0.88}  # Tighter: technical accuracy matters
    answer_critic: {threshold: 0.85}       # Tighter: architecture quality
    context_recall: {threshold: 0.85}      # Must recall relevant KB sections

  tracked:
    conciseness: {threshold: 0.60}         # Relaxed: design docs are intentionally detailed

  # Step 8 (Test Creation) additional thresholds:
  step8_overrides:
    faithfulness: {threshold: 0.95}        # Tests MUST trace to ACs — no invented scenarios
    correctness: {threshold: 0.90}         # Financial calculation assertions must be exact
    consistency: {threshold: 0.95}         # Coverage matrix must match actual scenario count
```

## REFLECTION (MANDATORY FOR ALL STEPS)

Every step prompt implicitly includes this reflection checklist.
The agent MUST verify before returning output:

```
REFLECTION (apply to every step):
  1. GROUNDING: Is every claim traceable to input stories, existing code, or KB?
  2. CITATION: Are KB sections cited for every design decision?
  3. CONSISTENCY: Does output contradict any previous step's output?
  4. COMPLETENESS: Is every story in the epic addressed by at least one artifact?
  5. MODE COMPLIANCE: If brownfield, are existing artifacts preserved (not overwritten)?
  6. BACKWARD COMPATIBILITY: Do changes break existing functionality?
  7. PII CHECK: Is there any PII or secrets in the output?
  8. FORMAT: Does output match the specified FORMAT section?
  9. DOMAIN TERMS: Do all terms match PD17 glossary?
  10. ENTERPRISE STANDARDS: Do all technical choices comply with EA1-EA20?
```

## ERROR HANDLING

```yaml
error_handling:
  step_failure:
    action: retry_once
    if_retry_fails: flag_for_architect_review
    notification: "Step {N} failed after retry. Reason: {error}. Architect review required."

  consistency_error:
    description: "Output of step N contradicts output of step M"
    action: re-run step N with step M output as additional context
    example: "LLD entity has field 'amount' but API spec has 'approvedAmount' — re-run step6 with step4 output"

  missing_context:
    description: "Step cannot proceed because input is insufficient"
    action: return INSUFFICIENT_CONTEXT with specific questions
    example: "Step 3 cannot design screen — story US-015 has no acceptance criteria for error state"

  brownfield_conflict:
    description: "Planned change conflicts with existing system"
    action: flag as architecture_decision_required, include options
    example: "New endpoint /api/v1/bridgenow/applications conflicts with existing /api/v1/applications pattern"
```

## FILE OPERATION RULES (BROWNFIELD)

```yaml
file_operations:
  existing_file_found:
    action: READ existing content, then APPEND/MODIFY (never overwrite)
    annotation: mark all additions with [EPIC-{id}] or [NEW] markers
    preservation: existing content must remain intact and functional

  existing_file_not_found:
    action: CREATE new file from scratch
    annotation: mark as [NEW - EPIC-{id}]

  update_strategy:
    wireframes.md: append new screen wireframes, annotate modified screens
    design-system.md: append new components section if needed
    user-flows.md: append new flow diagrams, annotate existing flows with new branches
    api-spec.yaml: add new endpoints/schemas, extend existing schemas (additive only)
    solution-architecture.md: add new sections, update diagrams
    integration-architecture.md: add new integrations to tables
    hld.md: add new components to diagrams, new state transitions
    lld.md: add new entities/tables/handlers, show BEFORE/AFTER for modifications
```

## WORKFLOW SUMMARY LOG

After all steps complete, the orchestrator produces:

```
═══ ARCHITECTURE DESIGN WORKFLOW COMPLETE ═══
Epic: {id} — {title}
Mode: {greenfield|brownfield}
Steps executed: {list}
Steps skipped: {list with reason}

Artifacts produced:
  ✓ wireframes.md (3 screens added, 1 modified)
  ✓ api-spec.yaml (2 endpoints added, 1 extended)
  ✓ solution-architecture.md (1 section added)
  ✓ integration-architecture.md (no changes)
  ✓ hld.md (state machine updated, 1 component added)
  ✓ lld.md (2 handlers added, 1 table added, 1 handler modified)

GitHub:
  PR #42 → org/tasheel-design-docs (6 files)
  PR #18 → org/tasheel-mobile (2 files)
  PR #31 → org/tasheel-backend (3 files)

Testing:
  Test scenarios: {N} created in Jira (linked to stories)
  Manual test cases: {N} created in XRay (test set: EP-XX Test Set)
  Automated tests: {N} feature files + {N} step definitions → GitHub PR #{N}
  Regression pack: {N} scenarios tagged @regression
  Coverage: {N}/{N} ACs covered (100%)

Jira: EP-XX updated with PR links + test scenarios, status → Design Complete
═══════════════════════════════════════════════
```
