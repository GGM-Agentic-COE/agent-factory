# Evaluation — L0-feature-decomposer-evaluator

This covers THIS evaluator's own meta-quality — not the L0-feature-
decomposer's generation rubric. The decomposer's rubric and the applicable
Feature-decomposition knowledge base are loaded at runtime and are not duplicated
here.

The evaluator must independently re-derive its findings from the approved Epic input,
the Feature Decomposer output, the decomposer's evaluation.md, and the applicable
knowledge-base guidance. It must not accept the generator's scores, conclusions,
coverage claims, or rationale without verification.

## Quality Gates

### Epic and Feature Coverage (→ Reasoning quality, Faithfulness)
- [ ] Every approved Epic was independently checked for at least one valid child Feature —
      not accepted merely because the generator reported complete coverage.
- [ ] The parent-Epic set represented in the Feature output matches the approved Epic set
      exactly: no approved Epic omitted and no unsupported Epic introduced.
- [ ] Every in-scope Epic requirement and acceptance criterion was independently mapped to
      one or more Features by content and identifiers, not by row count alone.
- [ ] Every generated Feature was checked against its parent Epic's scope, business value,
      acceptance criteria, dependencies, constraints, and carried source requirements.
- [ ] Any intentionally uncovered Epic content is supported by an explicit approved exclusion;
      otherwise it is reported as a coverage gap.
- [ ] Epic and requirement order is preserved where the required output contract mandates it.

### Independent Decomposition Review (→ Reasoning quality, Relevance)
- [ ] Every Feature boundary was independently re-derived from the parent Epic — not accepted
      because the generator's decomposition "looks reasonable."
- [ ] Every Feature is independently valuable and shippable without being a task, story,
      subtask, implementation step, or restatement of the complete Epic.
- [ ] Features within and across Epics were checked for duplication, material overlap,
      fragmentation, and unsupported consolidation.
- [ ] Shared capabilities are represented once and connected through grounded dependencies
      rather than duplicated across Features.
- [ ] Every dependency was re-checked for necessity, direction, and valid target; no dependency
      was accepted solely because the generator supplied it.
- [ ] No Feature introduces unsupported functionality, actor, workflow, system, integration,
      rule, outcome, priority, estimate, owner, release, sprint, or delivery date.

### Acceptance-Criteria Verification (→ Faithfulness, Consistency)
- [ ] Every Feature contains acceptance criteria that are specific, observable, testable, and
      written at Feature level.
- [ ] Every acceptance criterion was checked against the Feature description and parent Epic;
      unsupported criteria are removed or reported, not rationalized.
- [ ] Collectively, the acceptance criteria cover the Feature outcome, required boundaries,
      and all traceable conditions inherited from the parent Epic.
- [ ] Negative, exception, integration, compliance, and non-functional criteria are included
      only when supported by the parent Epic or its traceable source context.
- [ ] No criterion merely repeats the title or description, combines unrelated outcomes, or
      prescribes implementation without an approved constraint.
- [ ] Acceptance criteria do not contradict one another, the Feature scope, or the parent Epic.

### Grounding and Citation (→ Faithfulness, Hallucination)
- [ ] Every finding names the specific Feature ID, parent Epic ID, affected field, and specific
      gate from the decomposer's evaluation.md or applicable knowledge base.
- [ ] Every Feature cites a valid parent Epic and the exact supporting requirement identifiers
      or approved scope statements.
- [ ] Every cited Epic ID, requirement ID, acceptance criterion, dependency, and source reference
      was dereferenced and confirmed to exist in the supplied approved input.
- [ ] Source requirement identifiers are preserved exactly and are not renamed, reformatted,
      merged, or invented.
- [ ] Every finding distinguishes generator-output evidence from approved-source evidence.
- [ ] No vague finding such as "looks incorrect," "insufficient detail," or "not compliant"
      is returned without the exact evidence and violated gate.

### Fabrication Prevention (→ Hallucination)
- [ ] No correction invents missing business rules, scope, acceptance criteria, dependencies,
      source references, estimates, owners, dates, or technical decisions.
- [ ] No correction silently changes a Feature's parent Epic or requirement mapping without
      documenting the evidence that supports the change.
- [ ] No unsupported Feature is retained merely to preserve the generator's reported coverage.
- [ ] Missing source context results in INSUFFICIENT_CONTEXT or escalation when it prevents a
      grounded correction; it is never filled using plausible assumptions.
- [ ] Optional fields remain empty or omitted when no approved source supports a value.

### Consistency and Output Parity (→ Consistency)
- [ ] Feature IDs are unique and conform to the required naming convention.
- [ ] Parent Epic references resolve exactly to the approved Epic input.
- [ ] Dependency references resolve to valid Features or approved external dependencies.
- [ ] Terminology remains consistent with the approved Epic and source requirements.
- [ ] The structured Feature items and the rendered Feature artifact contain the same Feature
      set, fields, acceptance criteria, dependencies, and traceability.
- [ ] No correction is applied only to structured items or only to the rendered artifact.
- [ ] The validated or corrected artifact is returned inline in the required AgentOutput shape,
      without truncation or relocation into a summary field.

### Status and Correction Handling (→ Consistency)
- [ ] A legitimate INSUFFICIENT_CONTEXT or failed generator output is approved as such when the
      missing context cannot be recovered from the supplied approved inputs.
- [ ] An ungrounded generator output is never "fixed" by fabricating Features or missing fields.
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
- [ ] The final validated or corrected Feature artifact is suitable for the downstream Jira
      formatter/uploader without manual restructuring.
- [ ] No generator score, evaluator score, approval status, or downstream execution result is
      copied or fabricated as artifact content.

## Scores (≥ threshold to pass)

| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.95 | Findings and corrections accurately reflect the approved Epics, source requirements, and actual Feature output |
| Hallucination | ≤ 0.05 | No finding or correction introduces unsupported scope, criteria, dependency, identifier, or delivery metadata |
| Coverage | 0.95 | Every approved Epic and every in-scope Epic requirement is represented by valid Features |
| Consistency | 0.90 | Status, pass boolean, scores, findings, structured items, and rendered artifact agree |
| Relevance | 0.85 | Features remain independently valuable, shippable, and usable by downstream Jira consumers |
| Reasoning quality | 0.85 | Every finding identifies the specific Feature, Epic, evidence, and violated evaluation gate |
| Acceptance-criteria quality | 0.90 | Criteria are complete, testable, traceable, non-contradictory, and appropriate for Feature level |
| Citation completeness | 0.95 | Every Feature and evaluator finding includes complete parent-Epic and source-requirement grounding |

## Reflection Checklist

- [ ] No finding is a rubber stamp such as "looks fine" without an independent re-check.
- [ ] Every approved Epic and each in-scope requirement was checked by set membership and content,
      not inferred from counts or the generator's summary.
- [ ] Every Feature boundary, dependency, and acceptance criterion was re-derived from evidence.
- [ ] Every finding names the affected Feature ID, parent Epic ID, evidence, and violated gate.
- [ ] No correction introduces unsupported content or silently changes traceability.
- [ ] Legitimate INSUFFICIENT_CONTEXT is preserved rather than converted into fabricated Features.
- [ ] `escalate_to_hitl` is used only when the issue is genuinely unfixable from supplied evidence.
- [ ] Any correction is applied consistently to both structured Feature items and the inline artifact.
- [ ] Final status, pass boolean, scores, findings, and corrected output are mutually consistent.
- [ ] No blob persistence or Jira upload was attempted.

## Reflection Process

1. Evaluate the Feature Decomposer output →
2. Independently check all gates above against the approved Epic input, decomposer evaluation.md,
   and runtime knowledge-base guidance →
3. Recalculate scores from observed evidence →
4. Fix evidence-supported defects silently and consistently across items and artifact →
5. Re-run all gates and determine PASS, CORRECTED, or REJECTED →
6. Deliver the final evaluator AgentOutput only.

Do NOT print interim analysis, generator self-checks, or unevaluated output.