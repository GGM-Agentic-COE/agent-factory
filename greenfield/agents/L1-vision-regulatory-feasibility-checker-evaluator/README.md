# L1-vision-regulatory-feasibility-checker-evaluator

## Purpose

This is the highest-stakes evaluator in Phase 0. A false negative here — a
Red constraint that slips through unmitigated, or gets quietly relabeled
Amber to avoid writing a mitigation — is a compliance risk that reaches a
human decision-maker looking already handled. This agent's entire job is to
re-derive severity independently rather than trust the generator's own
classification at face value.

Since v2.0 it also holds the gate number itself. The viability score is
derived by the generator and **re-derived here from the final, post-fix
constraints** — because a severity fix that failed to move the score would
let a blocked idea clear `qg-L1-viability-score` and auto-publish.

## What does it do?

Accepts the original input and draft output from
`L1-vision-regulatory-feasibility-checker` and produces:
- Independent scores across 5 dimensions
- A severity-mismatch check: does each constraint's rationale actually
  support its stated Green/Amber/Red label?
- Validation of any overall_status "discount" claim — confirming every
  Amber/Red item genuinely has a non-legal-review mitigation before
  accepting a one-level-better verdict
- A jurisdiction check: the brief's `target_geography` against the
  jurisdiction each KB declares, then every citation against the resolved
  answer. A real regulation of the wrong country passes both an existence
  check and a plausibility check — this is the only check that catches it,
  and it also catches *false equivalence*, where the correct local regime is
  named but reasoned through a foreign analogue's mechanics
- A category coverage sweep: every applicable category in
  `kb-L1-regulatory-frameworks-index#coverage-categories` must be either a
  constraint or a declared `categories_not_applicable` entry — absent from
  both is a finding. That list is read from the KB, not authored here, so
  this audit and the generator's sweep are provably the same list
- An independent re-derivation of `viability_score` from the final
  constraints, with every cap the constraints actually trigger
- Fixes for mechanically-correctable issues; escalation for any
  genuinely-unmitigated Red constraint, with zero exceptions

## How does it work?

1. Ingests the generator's original input and draft output
2. Reads `regulatory-feasibility.md` and `idea-brief.json` from blob storage
   — the brief is **JSON**, parsed by key path, not scanned as markdown
3. Reads both regulatory KBs from **Confluence** with `tool-L1-confluence-reader`
   — `page_id = 518422550` and `page_id = 519012353`, fixed in the prompt, the same pages the
   generator reads — to sanity-check citations and re-run the category sweep.
   Because both agents read the same location, the audit and the sweep cannot
   diverge. Anchors are matched as headings in the returned XHTML
4. Reads the scoring rubric (`evaluation.md`) from GitHub with
   `tool-L1-github-reader-using-app` — one call, fixed in the prompt: repo
   `agentic-sdlc-knowledge-bases`, branch `main`, folder
   `planning/vision-regulatory-feasiblity/L1-vision-regulatory-feasibility-checker`.
   No examples are read. An unreadable rubric, or no KB carrying `#coverage-categories`, fails with
   `REFERENCE_UNAVAILABLE`. Corrections still go back to blob storage, never
   to the repository or Confluence
5. Checks every constraint's citation, mitigation/legal-review status, and
   whether its severity label actually matches its rationale
6. Validates any claimed overall_status discount against its precondition
7. Re-derives viability: `regulatory_posture × 0.60 + idea_clarity × 0.40`,
   then the lowest of that and every cap (`red_constraint` 6.0,
   `regulatory_overall_red` 6.0, `requires_legal_review` 6.5). A score at or
   above 7 emitted while a Red or legal-review constraint stands is both a
   fail finding and an automatic `escalate_to_hitl`
8. Fixes mechanical issues and writes any content change back into
   `regulatory-feasibility.md` — a viability correction touches **both** the
   header table and the Viability Score section; escalates anything
   requiring a mitigation this evaluator can't independently justify

## Input

- **Source:** agent_output from `L1-vision-regulatory-feasibility-checker`
- **Required:** `original_input`, `generator_output` (constraints,
  overall_status, categories_not_applicable, viability, open_items)

## Output

- **Type:** `regulatory_feasibility` — the generator's own type. This agent
  re-emits the corrected result with the evaluation attached under
  `items.evaluation`, not a separate evaluation-only shape
- **Items:** the generator's full result including the re-derived
  `viability`, plus `evaluation` carrying `scores`, `overall_score`, `pass`,
  `findings[]`, `fixes_applied[]`, `groundedness_check`, `viability_check`,
  `final_decision` — see `output_schema.json`
- **Artifacts:** `regulatory-feasibility.md` — re-saved if corrected,
  otherwise referenced at its original location
- **Summary:** overall score, severity-mismatch findings, discount validation
  result, uncovered categories, the re-derived score with its caps, guardrail
  results

## Composition

```
agents/L1-vision-regulatory-feasibility-checker-evaluator/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-mislabeled-severity.json
│   ├── output-01-mislabeled-severity.json
│   ├── input-02-invalid-discount.json
│   └── output-02-invalid-discount.json
└── golden/v1.0.0/
    ├── input-golden-01-harvestlink.json
    ├── golden-01-harvestlink.json
    ├── input-golden-02-unmitigated-red.json
    └── golden-02-unmitigated-red.json

prompts/L1-vision-regulatory-feasibility-checker-evaluator/
└── instructions.md
```
