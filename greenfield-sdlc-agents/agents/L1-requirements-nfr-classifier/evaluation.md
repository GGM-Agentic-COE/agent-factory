# Evaluation — L1-requirements-nfr-classifier

## Quality Gates
- [ ] Every FR in requirements.md has exactly one nfr_classifications entry, same id/order — none dropped, none reordered, none merged
- [ ] Every requirement has >=1 category checked against kb-L1-nfr-classification-taxonomy's 6 categories WHERE APPLICABLE — not a fixed 6 on every FR; an empty boundary_conditions array is valid only with reasoning stating "No NFR categories apply"
- [ ] Every boundary condition with a real number/rule cites requirements.md § FR-NNN, vision.md § <section> (e.g. vision.md § Regulatory Posture for Compliance), or kb-L1-enterprise-security § ES<n> specifically — never a bare guess, never a plausible-sounding figure with no matching citation
- [ ] A TBD boundary condition is honestly TBD ("TBD — needs stakeholder input") when genuinely ungrounded — never fabricated, and never marked TBD when a grounded value was actually available in the input or an attached KB
- [ ] source is "—" if and only if boundary_condition ends in the literal TBD phrase (schema-enforced; self-check confirms no mismatch slipped through)
- [ ] IDs match requirements.md exactly (FR-001, FR-002...) — no gaps, no duplicates, no invented ids

## Scores (>= threshold to pass)
| Evaluator | >= | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every boundary condition traces to a real requirements.md/vision.md/kb-L1-enterprise-security statement |
| Hallucination | <= 0.10 | No invented number, rule, or regulation not actually present in a cited source |
| Consistency | 0.90 | No two boundary conditions for the same FR contradict; TBD/source pairing never mismatched |
| Relevance | 0.85 | Output is usable as-is by prd-composer without re-classification |
| Reasoning quality | 0.80 | Every `reasoning` field explains why each category applies and why its value is grounded or TBD |
| Citation completeness | 0.95 | Every non-TBD boundary condition carries a specific, checkable source |

## Reflection Checklist
- [ ] Every applicable category was actually checked per kb-L1-nfr-classification-taxonomy's "ask" question for that FR — not skipped because a value wasn't obvious
- [ ] No boundary_condition silently pastes a long narrative instead of the short, atomic phrase the template expects
- [ ] Before marking anything TBD, kb-L1-enterprise-security and vision.md § Regulatory Posture were actually checked for a group policy or constraint that already answers it

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
