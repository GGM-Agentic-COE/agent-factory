# Evaluation — L0-target-architecture-generator-evaluator

This covers THIS evaluator's own meta-quality — not the quality of the
target architecture it evaluates (the checks for that live in this
evaluator's prompt, `kb-L0-target-architecture-template` and
`kb-L0-architecture-patterns`, loaded at runtime, not duplicated here).

## Quality Gates

### Template & Key Integrity (→ Faithfulness, Reasoning quality)
- [ ] Template conformance was checked section by section, callout by
      callout and column by column against the actual template — not by
      scanning headings and assuming the body follows.
- [ ] The key index was rebuilt independently (every key defined, every key
      cited) and compared by set membership — a dangling citation, a
      duplicate or a numbering gap was never inferred from counts.
- [ ] On an update, every key was checked against the baseline to confirm
      none was renumbered or reused for a different item.

### Independent Re-derivation (→ Reasoning quality, Faithfulness)
- [ ] The PRD entity set was rebuilt from the PRD itself and each entity
      matched to exactly one owning context — not accepted because the
      document's ownership table "looks complete".
- [ ] Every PRD functional requirement was traced to a citing capability by
      set membership, and every `prd:` citation dereferenced to confirm the
      cited item supports the statement it is attached to.
- [ ] Every Section 3 position was compared to the input verdict in
      `binding_principles` and every `DEV-NN` to the input deviation's
      scope, rationale and approver — a changed verdict was never accepted.
- [ ] Every `R-NN` was checked for a covering `DEV`, a sourced budget and a
      failure mode; every event for a consistency bound; every read model
      for owner and freshness — individually, not by sampling.

### Grounding & Citation (→ Faithfulness, Hallucination)
- [ ] Every numeric target in `QA`, `R` and `REQ-*` was traced to a PRD
      quality requirement or a KB standard; an unsourced figure was
      replaced with "Requires validation" plus an `OI-NN`, never kept
      because it is plausible.
- [ ] Every finding cites a specific document key or section AND a specific
      rule (template section, PAT/RULE key, `prd:` key, principle ID, ES/EA
      key) — never a vague impression.
- [ ] No fix invents a requirement, entity, budget, external system,
      principle, pattern, ADR or approver; no fix draws or moves a boundary.
- [ ] The technology-neutrality check was run over the full document text,
      including Mermaid figures and tables, not only prose.

### Baseline Fidelity (→ Faithfulness, Consistency)
- [ ] When a baseline was supplied, unchanged sections were diffed verbatim
      against it and every difference matched to exactly one Appendix B
      row — a missing row was added, an unexplained change restored.
- [ ] Version bump and status were recomputed from the actual change set
      (major for a context or constraint change, minor otherwise), not
      copied from the document.

### Publication & Status Handling (→ Consistency)
- [ ] Every fix was applied to the in-memory document AND to `items`; the
      published text and the `fixes_applied` patches describe the same
      final document.
- [ ] The document was published only on `approved` or
      `fixed_and_approved`; on `escalate_to_hitl` or INSUFFICIENT_CONTEXT
      nothing was published and `artifacts[0].storage.location` is null.
- [ ] A legitimate INSUFFICIENT_CONTEXT (status: failed) input is approved
      as-is, never "fixed" into a fabricated architecture.

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.95 | Findings accurately describe the actual document, PRD, binding principles and template |
| Hallucination | ≤ 0.05 | No fix introduces a requirement, entity, budget, system, principle, pattern, ADR or approver not grounded in the inputs, KBs, baseline or reviewer_notes |
| Consistency | 0.90 | overall_score and pass boolean agree with the individual dimension scores; published document, items and patches agree |
| Reasoning quality | 0.85 | Every finding's detail names the specific document key/section and rule involved |

## Reflection Checklist
- [ ] No finding is a rubber stamp ("looks fine") without a specific re-check
- [ ] escalate_to_hitl used only when genuinely unfixable — an entity with
      no settled owner, an uncovered requirement with no evident home, a
      contested boundary — not as a shortcut
- [ ] final_decision never claims fixed_and_approved while the published
      document still holds pre-fix text
- [ ] fixes_applied preserves everything that was already correct

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
