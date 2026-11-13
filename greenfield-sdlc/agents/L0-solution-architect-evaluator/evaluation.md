# Evaluation — L0-solution-architect-evaluator

This covers THIS evaluator's own meta-quality — not the generator's rubric
(loaded at runtime from GitHub: `../L0-solution-architect/evaluation.md`).

## Quality Gates
- [ ] Entity completeness was checked by set membership (entity-id ∈ DAT-1), not by count — a generator that lists "14 entities covered" while dropping one and adding another passes a count check and fails this one
- [ ] Edge completeness was checked by set membership (R-nn, or E-nn in the older layout, ∈ INT-1 decisions), not by count — a dropped edge or a renamed edge is exactly the class of defect a count cannot catch
- [ ] Registered copies were checked by set membership: every registered read model ∈ the DAT-4 register, every captured value ∈ the snapshot register
- [ ] Component completeness was checked by set membership (APP-2 component ∈ APL-1)
- [ ] The rubric's Style gates were run on the document, and every fix kept its voice: no correction note, self-check row or front matter was added to the page
- [ ] REQ-* coverage was checked by set membership (REQ-id ∈ Section 10 traceability table), built from the original target, not from what the generator carried into its own items
- [ ] CON-* coverage was checked by set membership (CON-id ∈ "Constraints honoured"), built from the original target
- [ ] Capability coverage was checked by set membership (REQ-PLT-*, or § 4.2 class in the older layout, ∈ PLT-6 rows), not inferred from the generator's self-check
- [ ] SEC-*/TB-* coverage was checked by set membership (every SEC-id, and any TB-id, ∈ Section 9 implemented controls) — "Not yet built" is a valid row; absence is not
- [ ] Residency was checked against the target's own residency demand, not only the group rule; a mismatch with no blocking PEND is a finding and is escalated, never fixed by changing region or cloud
- [ ] Technology grounding was verified independently: every technology traced to EA11 source, lifecycle and decision status; any **Approved** tag verified against EA11 approval status
- [ ] A PENDING value was verified to have a condition trigger (not a date) in a PEND row — trusting the generator's PEND count is not verification
- [ ] Cross-section consistency was re-derived: DAT-1 classifications match DAT-3 classes; INT-1 sync rows align with INT-2 planned contracts; INT-1 event rows align with INT-3 topics; PLT-6 AVAILABLE rows appear in the Cycle 0 exit proof; PLT-6 status agrees with each REQ's satisfaction-index status; every snapshot is captured over an existing INT-1 edge; every producer and consumer is a target context or component
- [ ] Every `cross_section_consistency` flag is false wherever a finding of that kind exists — a true flag beside a contradicting finding is the evaluator's own defect
- [ ] The Cycle 0 scope check was judged against the fixed exit-proof list, never the document's own exit-proof table
- [ ] Residency used DAT-1's Personal data column: Yes rows retagged, doubtful No rows escalated to Data Protection
- [ ] Integrity mechanisms, degraded modes, snapshot placement and topic retention were checked (rules 6i–6k)
- [ ] No style fix produced `****` or nested bold
- [ ] Each check used the id set the target's layout defines (current template or older layout); a check neither layout supports is reported as not applicable with null counts — never run against an undefined id set and reported as passing
- [ ] No fix writes **Approved** without naming the EA11 row it read; a target REQ-* budget is preferred over a KB default
- [ ] A legitimate INSUFFICIENT_CONTEXT (target missing or DRAFT without allow_draft_target) is approved as-is — an honest upstream refusal is not something to fix

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.92 | Findings accurately describe the actual generator output — no finding fabricated, no pass awarded without independent derivation |
| Hallucination | ≤ 0.08 | No fix introduces a technology, entity, edge, number or region not grounded in the target or a KB section |
| Consistency | 0.90 | Cross-section checks pass: DAT-1 ↔ DAT-3, INT-1 ↔ INT-2/INT-3, PLT-6 ↔ satisfaction index and exit proof |
| Reasoning quality | 0.88 | Every completeness finding names the specific id that is missing or mismatched, not "some entities may be missing" |
| Citation completeness | 0.95 | Every technology finding names the section, the technology and the specific EA11 or estate source that was missing or wrong |

## Reflection Checklist
- [ ] No completeness finding is a rubber stamp ("all REQs look covered") — each lists the specific ids verified and the method used
- [ ] escalate_to_hitl used only for a genuinely unresolvable gap, not overused for any deviation
- [ ] fixes_applied preserves every correct entity, edge, demand and constraint already present
- [ ] The corrected solution-architecture.md published to Confluence carries every fix, and no pre-fix text remains

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
