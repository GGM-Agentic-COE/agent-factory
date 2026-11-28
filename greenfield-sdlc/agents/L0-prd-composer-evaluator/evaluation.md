# Evaluation — L0-requirements-prd-composer-evaluator

This covers THIS evaluator's own meta-quality — not L0-requirements-prd-composer's
rubric (that lives in `../L0-requirements-prd-composer/evaluation.md`, loaded
at runtime, not duplicated here).

## Quality Gates

### Zero-Drop Verification (→ Faithfulness, Reasoning quality)
- [ ] The zero-drop FR check was done by set membership (every
      requirements.md FR-id → present in prd.md's requirements[]), not by
      counting and assuming enough exist.
- [ ] The zero-drop NFR check was done per-FR, per-category (every
      nfr-spec.md boundary condition → present in the SAME FR's nfrs[] and
      exactly once in prd.md Section 7, as NFR-NN if agreed or NQ-NN if
      TBD), not by a total-row-count comparison that could mask a swap
      between FRs.
- [ ] Every FR's and NFR/NQ row's release tag was checked for a stated basis
      (roadmap phase, value proposition or Priority), not accepted on trust.
- [ ] Every carried-forward field (Statement, Traces to, Compound
      Requirements Split) was diffed word-for-word against its source
      document — verbatim means verbatim, not paraphrased.

### Narrative Section Grounding (→ Faithfulness, Hallucination)
- [ ] Every AS/CON/DP/OR finding cites the specific vision.md
      constraint_id/open_risk id or FR-NNN it should trace to — not a vague
      impression.
- [ ] Every Risk present in vision.md was checked for presence in prd.md's
      OR rows verbatim (zero-drop on risks, same rigor as FRs/NFRs).
- [ ] Any new AS, CON, DP or OR row not present in vision.md was
      checked to genuinely originate from a specific FR the composer had
      in front of it — not invented to fill out the section.
- [ ] Every NSM/LI metric and target was checked against vision.md's
      north_star_metrics and leading indicators — none accepted because it
      "sounds like" a metric the product would track.

### Template Conformance (→ Consistency)
- [ ] Section, callout and table-column checks were made against the
      retrieved kb-L0-prd-template, not against memory of what a PRD
      usually contains.

### Out of Scope Verification (→ Faithfulness, Hallucination)
- [ ] Every Out of Scope entry was checked against the actual FR set in
      requirements.md to confirm no FR covers it, even partially — not
      accepted because it "sounds like" it's out of scope.
- [ ] Every Out of Scope entry traces to a specific vision.md section or
      Roadmap phase — not a vague impression of what the product probably
      doesn't do yet.
- [ ] "None identified..." was only accepted after confirming the FR set
      genuinely exhausts vision.md's Problem/Value Proposition/Roadmap
      Outline for this phase — not accepted by default.

### Glossary Verification (→ Faithfulness, Hallucination)
- [ ] Every Glossary term was confirmed to actually recur (>1 occurrence)
      across vision.md and/or requirements.md — not included because it's
      domain-sounding.
- [ ] Every Glossary definition was checked against its cited source to
      confirm the definition matches how the term is actually used there —
      not a generic or external definition substituted in.
- [ ] No generic PM/SDLC term (FR, NFR, stakeholder, etc.) was included —
      only domain- or regulation-specific terms.

### Consistency Across Sections (→ Consistency)
- [ ] Every Open Question tagged as a TBD boundary condition was checked
      against nfr-spec.md to confirm that boundary condition is still
      "TBD — needs stakeholder input" and hasn't since been resolved.
- [ ] Appendix A's quality-attribute categories and "Targets to be set"
      counts per FR were recomputed independently from Sections 6 and 7,
      not copied from the composer's own summary.
- [ ] "THE PRODUCT" callout and Bottom-line position claims (requirement
      counts, releases, biggest obligation/risk) were each independently
      verified against the sections that follow — no claim accepted on
      trust.

### Fabrication Prevention & Status Handling (→ Hallucination, Consistency)
- [ ] No fix introduces an FR, NFR, assumption, constraint, or risk not
      grounded in requirements.md/nfr-spec.md/vision.md.
- [ ] A legitimate INSUFFICIENT_CONTEXT (status: failed) generator output is
      approved as-is, never "fixed" into fabricated requirements.

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.95 | Findings accurately describe the actual generator output and the retrieved prd.md |
| Hallucination | ≤ 0.05 | No fix introduces an FR, NFR, assumption, constraint, or risk not grounded in requirements.md/nfr-spec.md/vision.md |
| Consistency | 0.90 | overall_score and pass boolean agree with the individual dimension scores |
| Reasoning quality | 0.85 | Every finding's detail names the specific FR-id/category/constraint-id involved |

## Reflection Checklist
- [ ] No finding is a rubber stamp ("looks fine") without a specific check
- [ ] escalate_to_hitl used when genuinely unfixable, not overused as a shortcut
- [ ] Every fix that touched prd.md content was actually pushed back to the
      SAME s3 location — final_decision never claims fixed_and_approved while
      the document still holds the pre-fix text
- [ ] fixes_applied preserves everything that was already correct

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
