# Evaluation — L1-requirements-prd-composer

## Quality Gates
- [ ] Zero-drop: every FR-NNN in requirements.md appears in requirements[], same id, same statement text
- [ ] Zero-drop: every NFR boundary condition attached to an FR in nfr-spec.md appears in that FR's nfrs[], carried verbatim (or the FR's nfrs is genuinely empty, matching "No NFR categories apply")
- [ ] compound_splits carried forward verbatim from requirements.md — not re-derived, not dropped
- [ ] Every assumption/constraint/risk is traceable to vision.md's Regulatory Posture or Open Risks Carried Forward, OR to a specific FR-NNN that reveals a premise vision.md couldn't have known — never an invented product-level claim
- [ ] Every assumption/constraint/risk names the FR(s) it underlies/constrains/affects, or is explicitly "program-level" — never left untagged
- [ ] Success metrics are genuinely absent — no field, section, or summary duplicates vision.md's north_star_metrics
- [ ] open_questions rolls up every TBD boundary condition across all requirements, plus any genuine coverage gap noticed while composing — no TBD silently dropped
- [ ] executive_summary introduces no claim absent from the sections below it; written last

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.95 | Every requirement/NFR matches its upstream source exactly; highest bar in Phase 1 since this composes two already-approved documents |
| Hallucination | ≤ 0.05 | No FR, NFR, assumption, constraint, or risk invented beyond requirements.md/nfr-spec.md/vision.md |
| Consistency | 0.95 | No requirement or boundary condition dropped between input and output — the concrete zero-drop test |
| Relevance | 0.85 | Output is usable as-is by L1-planning-impact-assessor and L1-planning-dependency-mapper |
| Reasoning quality | 0.80 | Every requirement's reasoning explains the composition, not a re-derivation of the FR itself |
| Citation completeness | N/A | This agent composes from agent_output directly, not a KB — traces_to / underlies_or_affects substitute for citation |

## Reflection Checklist
- [ ] FR count in requirements[] exactly matches requirements.md's FR count — no gaps, no duplicates
- [ ] No summary/short_title/`*_summary` field silently contains the full artifact prose instead of a distillation
- [ ] No success-metrics field or claim smuggled into any section despite the template's explicit exclusion

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
