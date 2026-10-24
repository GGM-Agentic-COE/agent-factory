# Evaluation — L1-requirements-elicitor

## Quality Gates
- [ ] All required fields present: functional_requirements (≥1), compound_splits (array, may be empty)
- [ ] Every FR is Singular (ISO/IEC/IEEE 29148) — no "and"/"or" joining two independently testable capabilities; a compound clause is split, not passed through
- [ ] Every FR is Traceable — traces_to names exactly one real vision.md section, not a paraphrase-only claim
- [ ] No statement contains an unqualified vague term (fast, user-friendly, appropriate, secure, robust, intuitive) without a measurable qualifier — kb-L1-requirements-quality-standard's Unambiguous scan
- [ ] IDs sequential (FR-001, FR-002...), no gaps or duplicates
- [ ] Agent refused to run (status: failed) if no recorded Product Lead approval was provided — never proceeds on an unapproved vision

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every FR traces to a real vision.md clause via `traces_to` |
| Hallucination | ≤ 0.10 | No invented capability absent from vision.md |
| Consistency | 0.90 | No two FRs contradict (kb-L1-requirements-quality-standard's Consistent check) |
| Relevance | 0.85 | Output is usable as-is by nfr-classifier/prd-composer/story-generator |
| Reasoning quality | 0.80 | Every `reasoning` field explains the extraction, not just restates the statement |
| Citation completeness | N/A | This agent grounds against vision.md directly, not a KB — `traces_to` substitutes for citation |

## Reflection Checklist
- [ ] Every FR is independently Verifiable — could a tester write one pass/fail test directly from the statement alone?
- [ ] Coverage: does every vision.md Problem/Value-Proposition/Regulatory-mitigation/Roadmap item have at least one covering FR? (kb-L1-requirements-quality-standard's Complete check — set membership, not a count)
- [ ] No FR over-specifies a solution vision.md never asked for (Correct — drift check)

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
