# Evaluation — L0-binding-principles-generator-evaluator

This covers THIS evaluator's own meta-quality — not the quality of the
binding-principles document it evaluates (the checks for that live in this
evaluator's prompt and in `kb-L0-architecture-patterns` AP2/AP4, loaded at
runtime, not duplicated here).

## Quality Gates

### Catalogue Completeness (→ Reasoning quality, Faithfulness)
- [ ] The catalogue check was done by set membership in both directions
      (every AP2 principle ID → present in the document; every document ID
      → present in AP2), not by comparing counts.
- [ ] Every principle's statement and kind were diffed word-for-word against
      AP2 — verbatim means verbatim, not paraphrased.
- [ ] A principle found missing was resolved only when its evidence could
      be gathered directly from the PRD and KBs; otherwise escalated, never
      filled with a placeholder verdict.

### Evidence Integrity (→ Faithfulness, Hallucination)
- [ ] Every `evidence[].locator` was dereferenced: a `prd:` locator against
      the actual PRD, a KB locator against the actual KB section — and the
      cited item confirmed to support the `note`, not merely to exist.
- [ ] Every finding cites a specific principle ID AND a specific rule
      (RULE-03, RULE-04, an AP2 kind, a `prd:` key, an ES/EA section key)
      — never a vague impression.
- [ ] No fix invents a `prd:` key, a KB section key, a pattern key, an
      approver or a numeric value not present in a real source.

### Verdict Re-derivation (→ Reasoning quality, Faithfulness)
- [ ] Every verdict was independently re-derived by asking the principle's
      question against the PRD evidence — not accepted because the
      rationale "reads convincingly" or because `confidence` is high.
- [ ] Every `deviation-required` was checked for a specific forcing
      requirement and a scope naming only the flows/stores that requirement
      touches — an unbounded scope was never accepted.
- [ ] Every technology-selecting principle was checked to carry
      `applied-in-solution-architecture`, never `satisfied`.
- [ ] Every `at-risk` verdict was traced to a real PRD open question, unset
      target or assumption, and has a matching `BPQ-NN`.

### Conflict Surfacing (→ Faithfulness, Consistency)
- [ ] Every obligation stated by both the PRD and a KB (retention, tier,
      classification, regulator) was compared independently; the stricter
      value confirmed applied, both cited, and an open question present.
- [ ] A PRD value marked "to be set"/"TBD"/deferred was confirmed NOT to
      have been used as a value anywhere.

### Baseline Fidelity (→ Faithfulness, Consistency)
- [ ] When a baseline was supplied, every unchanged principle was diffed
      byte-for-byte against it (including `approved_by`), and every
      differing field matched to exactly one `delta[]` entry.
- [ ] No approved deviation was widened, narrowed or withdrawn without a
      `reviewer_notes` instruction; an unauthorised change was restored and
      registered as a delta with `applied: false`.
- [ ] `document_version` and `status` were recomputed from the delta set,
      not copied from the document.

### Fabrication Prevention & Status Handling (→ Hallucination, Consistency)
- [ ] Every fix was applied to BOTH the in-memory document and `items`;
      the two were checked to agree after fixing, and the document written
      back to blob storage is that corrected copy.
- [ ] The document was written back whatever the verdict, with `status`
      `"draft"` and a `review` object whose decision, fixes and unfixed
      findings match the output's evaluation block exactly; nothing else
      in its structure changed. Only a legitimate INSUFFICIENT_CONTEXT
      input left nothing to write.
- [ ] The blob location reported in `artifacts[0].storage.location` was
      built from the writer tool's actual result lines, never assumed; a
      failed write was reported as null with the tool message.
- [ ] No document text, full rationale or evidence list appears in the
      output JSON; only `items` summaries, ≤150-character patch excerpts
      and the blob location.
- [ ] A legitimate INSUFFICIENT_CONTEXT (status: failed) input is approved
      as-is, never "fixed" into fabricated resolutions.

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.95 | Findings accurately describe the actual document and the actual PRD/KB evidence |
| Hallucination | ≤ 0.05 | No fix introduces a principle, locator, value, pattern or approver not grounded in the PRD, KBs, baseline or reviewer_notes |
| Consistency | 0.90 | overall_score and pass boolean agree with the individual dimension scores; document and items agree |
| Reasoning quality | 0.85 | Every finding's detail names the specific principle ID and rule involved |

## Reflection Checklist
- [ ] No finding is a rubber stamp ("looks fine") without a specific re-check
- [ ] escalate_to_hitl used only when genuinely unfixable — an unsupported
      verdict with no identifiable correct verdict, a deviation with no
      identifiable forcing requirement — not as a shortcut
- [ ] final_decision never claims fixed_and_approved while the document
      written to blob storage still holds pre-fix text
- [ ] fixes_applied preserves everything that was already correct

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
