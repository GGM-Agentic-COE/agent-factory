# Evaluation — L1-testing-case-writer-evaluator

This document evaluates the **meta-quality of L1-testing-case-writer-evaluator**. It does not duplicate the Test Case Writer's output-quality rubric. The evaluator MUST load and apply the approved writer evaluation rubric and any required knowledge bases supplied at runtime, as identified by its instructions.

The evaluator reviews the combined three-agent oracle chain: scenario output, ordinary test-case output, and adversarial test-case output. It independently verifies coverage and citations from the supplied source material before deciding whether the chain may proceed.

## Quality Gates

All applicable gates must pass. If required input is unavailable, apply the evaluator's `INSUFFICIENT_CONTEXT` behavior; do not infer missing chain content.

### 1. Input Completeness and Independence

- [ ] All three required chain outputs are present before a full-chain verdict is issued.
- [ ] Acceptance criteria, architecture sections, and regulatory posture are extracted from the supplied evaluator input when present and required by the contract.
- [ ] A partial chain is not scored as though complete; missing required output produces `INSUFFICIENT_CONTEXT` with `status: failed`.
- [ ] `workflow_execution_id` is inherited from the chain and is not fabricated.
- [ ] Coverage is independently recounted from acceptance-criteria clauses, not copied from the chain's coverage block.
- [ ] Every citation is re-resolved against the supplied source sections and checked for whether it supports the claim.
- [ ] The evaluator's verdict does not rely solely on the chain's self-assessment or reflection.

### 2. Coverage Recount

- [ ] Every in-scope acceptance-criteria clause is enumerated before coverage is assessed.
- [ ] Cases asserting each clause are identified from the actual scenario, ordinary case, and adversarial outputs.
- [ ] Recount results are compared with the chain's reported coverage; discrepancies are reported even when the independently recounted coverage is adequate.
- [ ] Compliance-tagged clauses are identified from supplied source material.
- [ ] Adversarial cases are counted specifically for each compliance-tagged clause; a happy-path case alone does not satisfy this gate.
- [ ] A compliance-tagged clause with no adversarial case is always a blocker and is recorded as not fixed for routing to the adversarial writer.
- [ ] Coverage claims state their scope and do not imply broader completeness than was checked.
- [ ] Recount evidence shows the clause/source identifier, matching case identifiers, and the resulting coverage determination.

### 3. Citation and Source Validation

- [ ] Each citation is checked against the actual supplied acceptance criteria or architecture sections.
- [ ] A citation that resolves and supports its claim is distinguished from one that resolves but does not support the claim (`false_citation`).
- [ ] A citation that does not resolve to a supplied source is classified as fabricated or unresolved according to the evaluator contract.
- [ ] A real section identifier is not accepted as sufficient evidence unless the section supports the associated claim.
- [ ] Findings identify the source claim, citation, resolution outcome, and affected stage/artifact ID.
- [ ] No finding is raised when the citation and claim are supported.

### 4. Invariant Preservation

- [ ] Each case derived from an invariant is identified and checked against the source invariant.
- [ ] The evaluator checks whether the case names the failure path it closes, where the supplied sources support that path.
- [ ] The evaluator verifies that the assertion addresses the prohibited state/invariant, not only rejection of one request or input.
- [ ] A case that reduces a state invariant to request rejection is reported as `downgraded_invariant` and treated as a blocker.
- [ ] The evaluator does not invent import, migration, concurrency, or other paths; it checks only paths supported by supplied architecture or requirements.

### 5. Stage Boundaries and Case Polarity

- [ ] Findings identify the chain stage they concern and reference an artifact ID that exists in that stage's output.
- [ ] The scenario output is checked for prohibited negative assertions as defined by the evaluator contract.
- [ ] The adversarial output is checked for prohibited positive/happy-path cases as defined by the evaluator contract.
- [ ] Any polarity leak is supported with specific evidence and is not inferred from category labels alone.
- [ ] The evaluator does not assume the ordinary case set or adversarial case set contains content absent from the supplied output.

### 6. Identifier and Cross-Artifact Consistency

- [ ] IDs are checked for uniqueness and valid references across all three chain stages.
- [ ] Sequential, gap-free ID rules are checked only where the applicable contract and supplied allocation context establish them.
- [ ] Reuse of a retired case ID is checked only when retired-ID information is supplied; unavailable retirement data is reported as a limitation, not guessed.
- [ ] Orphan, missing, duplicate, or mismatched IDs are identified with concrete evidence.
- [ ] Carried citations and source IDs remain exact; the evaluator does not normalize or replace them.

### 7. Finding Quality

- [ ] Every finding names a specific evaluator-rubric criterion or applicable runtime-rubric gate.
- [ ] Every finding includes evidence from the actual input/output and identifies the affected stage and existing artifact ID.
- [ ] Finding category and severity match the demonstrated issue and its impact.
- [ ] Findings distinguish generator defects from missing, ambiguous, or contradictory upstream context.
- [ ] No finding is a rubber stamp, vague impression, or unsupported assumption.
- [ ] The evaluator reports no issue when the chain is sound.
- [ ] Finding completeness is assessed across all required gates; the evaluator does not omit a material issue to preserve a passing verdict.

### 8. Correction Boundaries

- [ ] Only mechanical corrections are applied: coverage miscounts, policy-inconsistent tier labels, or a missing carried citation that can be resolved from supplied sources.
- [ ] Every correction maps to a genuine finding.
- [ ] Every correction is supported by supplied sources and preserves correct content and identifiers.
- [ ] The evaluator does not write a missing test case, rewrite a substantive assertion, or make a judgment-call tier change.
- [ ] A compliance gap is never marked fixed by this evaluator; it is recorded under `not_fixed` and routed to the responsible adversarial writer.
- [ ] Corrections do not silently resolve ambiguity or contradiction.
- [ ] Any corrected output is rechecked for consistency and source support.

### 9. Verdict and Scores

- [ ] The evaluator uses only the permitted decisions: `approved`, `fixed_and_approved`, or `rejected`.
- [ ] A blocking issue, including uncovered compliance adversarial coverage or a downgraded invariant, prevents approval.
- [ ] `fixed_and_approved` is used only when permitted mechanical fixes were applied and the final chain passes all blocking checks.
- [ ] Scores are within the defined range and supported by findings/evidence.
- [ ] Scores and verdict are consistent; unresolved blockers cannot coexist with an approval decision.
- [ ] A legitimate `INSUFFICIENT_CONTEXT` result is preserved as failed; missing inputs are not fabricated to achieve a complete-looking assessment.

### 10. Output and Summary Contract

- [ ] Output is a valid AgentOutput JSON object with the correct `agent_id`, `agent_version`, `execution_id`, inherited `workflow_execution_id`, `status`, and `content.type: oracle_chain_evaluation`.
- [ ] Required content items are present: findings, recount, scores, final decision, and not-fixed items.
- [ ] `status` accurately represents whether evaluation could be completed; it is not substituted for the business decision.
- [ ] `execution_summary` is present and includes the required factual summary: findings by severity and stage, decision, recount versus chain claim, citation resolution results, deliberately unfixed issues and routing, knowledge bases consulted and their use, guardrails evaluated, and tools invoked as required by the contract.
- [ ] The plain-text summary follows the structured JSON as required by the evaluator contract.
- [ ] No interim reflection, hidden reasoning, or unsupported completion claim is included.

## Meta-Evaluation Scores

Score each dimension from 0.0 to 1.0. All dimensions must meet their minimum, and no critical failure condition may be present.

| Dimension | Minimum | What it evaluates |
|---|---:|---|
| Finding Validity | 0.95 | Findings accurately identify genuine, evidence-backed defects and avoid false positives |
| Finding Completeness | 0.90 | All material failures required by the applicable rubric and these gates are reported |
| Fix Correctness | 0.95 | Permitted fixes are mechanical, source-supported, minimal, and validated |
| Independence | 1.00 | Coverage is recounted and citations are re-resolved independently from supplied sources |
| Verdict and Output Integrity | 0.95 | Scores, blockers, decision, status, IDs, and output contract are mutually consistent |

A meta-evaluation passes only when every dimension meets its minimum, all critical gates pass, and no critical failure condition is present.

## Critical Failure Conditions

The evaluator fails meta-evaluation if it:

1. Issues a complete-chain verdict when any required chain output is missing instead of returning `INSUFFICIENT_CONTEXT`.
2. Copies the chain's coverage block without independently recounting coverage from acceptance criteria.
3. Accepts a citation merely because its identifier exists, without checking that it supports the claim.
4. Fails to block an uncovered compliance-tagged clause that has no adversarial case.
5. Fails to report an invariant downgraded to request/input rejection as a blocker.
6. Writes a missing test case or makes a substantive, unsupported change to an assertion.
7. Marks a compliance gap as fixed rather than not fixed and routed.
8. Invents requirements, evidence, citations, IDs, retired-ID history, or source-supported paths.
9. Returns approval while a blocking issue remains.
10. Alters the inherited `workflow_execution_id` or fabricates execution metadata.
11. Omits required output fields or emits invalid JSON / contract-incompatible summary structure.
12. Exposes internal reasoning or reflection logs.

## Reflection Checklist

Before final delivery, silently verify:

- [ ] All required chain inputs are present, or `INSUFFICIENT_CONTEXT` is returned.
- [ ] Coverage was enumerated and recounted clause by clause from source acceptance criteria.
- [ ] Adversarial coverage was counted separately for each compliance-tagged clause.
- [ ] Every citation was re-resolved and checked for claim support.
- [ ] Invariant-derived cases were checked for state assertion and supported failure path.
- [ ] Every finding has evidence, a valid criterion, stage, and existing affected ID.
- [ ] No unsupported finding or correction was introduced.
- [ ] Only permitted mechanical fixes were made; unfixed issues were routed.
- [ ] All blocking findings prevent approval.
- [ ] Scores, verdict, status, and final artifacts agree.
- [ ] The output and execution summary satisfy the evaluator's contract.
- [ ] No reflection or hidden reasoning appears in the final response.

## Reflection Process

1. Evaluate the final chain against the runtime-supplied writer rubric and required knowledge bases.
2. Check every applicable gate in this meta-quality evaluation.
3. Apply only permitted mechanical corrections and revalidate them.
4. Deliver the contract-compliant final result without exposing internal reflection.

## Separation of Responsibilities

This `evaluation.md` evaluates the evaluator's own meta-quality. The Test Case Writer evaluation rubric and applicable knowledge bases evaluate the generated test artifacts. Do not duplicate or replace those runtime evaluation criteria here.
