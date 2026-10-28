# Evaluation — L1-inception-epics-creator-evaluator

This covers THIS evaluator's own meta-quality — not the L1-inception-epics-
creator's generation rubric. The Epic Creator's evaluation.md and the applicable
Epic-authoring knowledge base are loaded at runtime and are not duplicated here.

The evaluator must independently re-derive its findings from the approved PRD input,
the Epic Creator output, the creator's evaluation.md, and the applicable knowledge-base
guidance. It must not accept the generator's scores, conclusions, coverage claims,
traceability claims, or rationale without verification.

## Quality Gates

### PRD and Epic Coverage (→ Reasoning quality, Faithfulness)
- [ ] Every approved in-scope PRD requirement was independently checked for coverage by at
      least one valid Epic — not accepted merely because the generator reported complete coverage.
- [ ] The requirement-ID set represented across the Epic output matches the approved in-scope
      PRD requirement set exactly: no required item omitted and no unsupported item introduced.
- [ ] Coverage was verified by requirement identifiers and content, not by Epic count,
      requirement count, section count, or the generator's coverage summary alone.
- [ ] Every generated Epic was checked against the PRD's objectives, scope, business outcomes,
      requirements, constraints, assumptions, dependencies, and source reference.
- [ ] Any intentionally uncovered PRD content is supported by an explicit approved exclusion;
      otherwise it is reported as a coverage gap.
- [ ] Requirement order is preserved where the required output contract mandates it.

### Independent Epic Derivation Review (→ Reasoning quality, Relevance)
- [ ] Every Epic boundary was independently re-derived from the approved PRD — not accepted
      because the generator's grouping "looks reasonable."
- [ ] Every Epic represents a coherent business capability or outcome and is not a Feature,
      story, task, implementation step, project phase, or restatement of the complete PRD.
- [ ] Epics were checked for duplication, material overlap, excessive fragmentation, and
      unsupported consolidation.
- [ ] Requirements grouped into the same Epic have a defensible shared outcome, capability,
      or value stream grounded in the PRD.
- [ ] Requirements that require distinct outcomes or independently governed delivery are not
      combined merely to reduce the Epic count.
- [ ] Shared capabilities are represented once and connected through grounded dependencies
      rather than duplicated across Epics.
- [ ] Every dependency was independently checked for necessity, direction, and valid target;
      no dependency was accepted solely because the generator supplied it.
- [ ] No Epic introduces unsupported functionality, actor, workflow, system, integration,
      policy, business rule, outcome, priority, estimate, owner, release, sprint, or delivery date.

### Epic Content Verification (→ Faithfulness, Relevance)
- [ ] Every Epic contains a unique Epic ID and an outcome-focused title.
- [ ] Every Epic contains a clear description of the capability, problem, and intended outcome.
- [ ] Every Epic contains business value directly supported by the approved PRD.
- [ ] Every Epic contains clear in-scope boundaries and, where needed, explicit out-of-scope
      boundaries that prevent overlap or ambiguity.
- [ ] Every Epic contains acceptance criteria that are specific, observable, testable, and
      appropriate for Epic-level validation.
- [ ] Every Epic contains dependencies, constraints, assumptions, and risks only when supported
      by the approved PRD or applicable runtime guidance.
- [ ] Every Epic contains the approved PRD source reference and exact supporting requirement IDs.
- [ ] Optional fields remain empty or omitted when no approved source supports a value.

### Acceptance-Criteria Verification (→ Faithfulness, Consistency)
- [ ] Every Epic's acceptance criteria were independently checked against the Epic description,
      business value, scope, and mapped PRD requirements.
- [ ] Collectively, the acceptance criteria validate the Epic outcome and all mandatory conditions
      inherited from the mapped PRD requirements.
- [ ] Acceptance criteria do not merely repeat the Epic title, description, or requirement text.
- [ ] Acceptance criteria do not decompose the Epic into implementation tasks or prescribe an
      unsupported solution.
- [ ] Negative, exception, integration, compliance, and non-functional conditions are included
      only when supported by the approved PRD or a loaded authoritative source.
- [ ] No criterion combines unrelated outcomes into one untestable statement.
- [ ] Acceptance criteria do not contradict one another, the Epic scope, or the approved PRD.

### Grounding and Citation (→ Faithfulness, Hallucination)
- [ ] Every finding names the specific Epic ID, affected PRD requirement ID, affected field,
      and specific gate from the creator's evaluation.md or applicable knowledge base.
- [ ] Every Epic cites the valid PRD source reference and exact supporting requirement IDs or
      approved scope statements.
- [ ] Every cited requirement, acceptance criterion, dependency, constraint, and source reference
      was dereferenced and confirmed to exist in the supplied approved input.
- [ ] PRD requirement identifiers are preserved exactly and are not renamed, reformatted,
      merged, split, or invented.
- [ ] Every finding distinguishes generator-output evidence from approved-source evidence.
- [ ] No vague finding such as "looks incorrect," "insufficient detail," or "not compliant"
      is returned without exact evidence and the violated gate.

### Fabrication Prevention (→ Hallucination)
- [ ] No correction invents missing scope, business value, requirements, acceptance criteria,
      dependencies, constraints, assumptions, risks, references, estimates, owners, or dates.
- [ ] No correction silently changes an Epic's requirement mapping without documenting the
      approved evidence supporting the change.
- [ ] No unsupported Epic is retained merely to preserve the generator's reported coverage.
- [ ] Missing source context results in INSUFFICIENT_CONTEXT or escalation when it prevents a
      grounded correction; it is never filled using plausible assumptions.
- [ ] No requirement is marked covered solely because its identifier appears in an Epic without
      substantive representation in the Epic's description, scope, or acceptance criteria.

### Consistency and Output Parity (→ Consistency)
- [ ] Epic IDs are unique and conform to the required naming convention.
- [ ] Requirement references resolve exactly to the approved PRD input.
- [ ] Dependency references resolve to valid Epics or approved external dependencies.
- [ ] Terminology remains consistent with the approved PRD.
- [ ] The structured Epic items and rendered Epic artifact contain the same Epic set, fields,
      acceptance criteria, dependencies, and traceability.
- [ ] No correction is applied only to structured items or only to the rendered artifact.
- [ ] Coverage summaries and traceability matrices, when present, match the actual Epic mappings.
- [ ] The validated or corrected artifact is returned inline in the required AgentOutput shape,
      without truncation or relocation into a summary field.

### Status and Correction Handling (→ Consistency)
- [ ] A legitimate INSUFFICIENT_CONTEXT or failed generator output is approved as such when the
      missing context cannot be recovered from the supplied approved inputs.
- [ ] An ungrounded generator output is never "fixed" by fabricating Epics or mandatory fields.
- [ ] PASS is used only when all mandatory gates and score thresholds pass without content changes.
- [ ] CORRECTED is used only when all identified defects were corrected using supplied evidence
      and the corrected output then passes all mandatory gates and thresholds.
- [ ] REJECTED is used when mandatory defects remain, correction requires unsupported context,
      or the output cannot safely proceed downstream.
- [ ] `escalate_to_hitl` is used only for genuinely unfixable ambiguity, conflicting approved
      sources, or missing stakeholder decisions — never as a shortcut for evaluator work.
- [ ] The overall status, pass boolean, dimension scores, findings, and corrected artifact agree.

### Persistence and Downstream Safety (→ Consistency, Relevance)
- [ ] No blob-storage write is performed when the workflow contract requires inline handoff.
- [ ] No Jira create, update, or upload action is attempted by this evaluator.
- [ ] The final validated or corrected Epic artifact is suitable for the downstream Feature
      Decomposer, Feature Decomposer Evaluator, and Jira formatter/uploader without restructuring.
- [ ] No generator score, evaluator score, approval status, or downstream execution result is
      copied or fabricated as Epic artifact content.

## Scores (≥ threshold to pass)

| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.95 | Findings and corrections accurately reflect the approved PRD and actual Epic output |
| Hallucination | ≤ 0.05 | No finding or correction introduces unsupported scope, criteria, dependency, identifier, or delivery metadata |
| Coverage | 0.95 | Every approved in-scope PRD requirement is substantively represented by one or more valid Epics |
| Consistency | 0.90 | Status, pass boolean, scores, findings, structured items, artifact, and coverage mappings agree |
| Relevance | 0.85 | Epics remain outcome-oriented, appropriately scoped, and usable by downstream consumers |
| Reasoning quality | 0.85 | Every finding identifies the specific Epic, PRD requirement, evidence, and violated gate |
| Acceptance-criteria quality | 0.90 | Criteria are complete, testable, traceable, non-contradictory, and appropriate for Epic level |
| Citation completeness | 0.95 | Every Epic and evaluator finding includes complete PRD-source and requirement grounding |

## Reflection Checklist

- [ ] No finding is a rubber stamp such as "looks fine" without an independent re-check.
- [ ] Every approved in-scope PRD requirement was checked by set membership and content, not
      inferred from counts or the generator's summary.
- [ ] Every Epic boundary, grouping decision, dependency, and acceptance criterion was re-derived
      from approved evidence.
- [ ] Every finding names the affected Epic ID, PRD requirement ID, evidence, and violated gate.
- [ ] No correction introduces unsupported content or silently changes traceability.
- [ ] Legitimate INSUFFICIENT_CONTEXT is preserved rather than converted into fabricated Epics.
- [ ] `escalate_to_hitl` is used only when the issue is genuinely unfixable from supplied evidence.
- [ ] Any correction is applied consistently to structured Epic items, coverage mappings, and
      the inline artifact.
- [ ] Final status, pass boolean, scores, findings, and corrected output are mutually consistent.
- [ ] No blob persistence or Jira upload was attempted.

## Reflection Process

1. Evaluate the Epic Creator output →
2. Independently check all gates above against the approved PRD input, creator evaluation.md,
   and runtime knowledge-base guidance →
3. Recalculate scores from observed evidence →
4. Fix evidence-supported defects silently and consistently across items, mappings, and artifact →
5. Re-run all gates and determine PASS, CORRECTED, or REJECTED →
6. Deliver the final evaluator AgentOutput only.

Do NOT print interim analysis, generator self-checks, or unevaluated output.