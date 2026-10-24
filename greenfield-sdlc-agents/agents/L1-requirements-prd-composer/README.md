# L1-requirements-prd-composer

## Purpose

`L1-planning-impact-assessor` and `L1-planning-dependency-mapper` need one
composed source of truth instead of cross-referencing the elicitor's and
classifier's items separately. This agent is also the last automated
checkpoint that could silently drop a requirement or an NFR boundary
condition between elicitation/classification and downstream planning —
zero-drop composition is the concrete test, not just formatting.

## What does it do?

Accepts `functional_requirements`/`compound_splits` items (from
`L1-requirements-elicitor` — items only, no document, 2026-08-07),
`nfr_classifications` items (from `L1-requirements-nfr-classifier` — items
only, no document, 2026-08-07), `vision.md` (read-only artifact, from
`L1-vision-statement-generator`), and this agent's own `approval_comment`
input parameter, and produces one composed `prd.md`:
- Every FR-NNN together with its full NFR boundary-condition table, in one
  block, carried verbatim from the two upstream agents' items — this agent
  does not re-derive requirements or NFRs, it composes what already exists
- Assumptions, Constraints, and Risks condensed from `vision.md`'s
  Regulatory Posture and Open Risks Carried Forward sections, each tagged
  with the FR(s) it underlies/constrains/affects (or `program-level`)
- An Open Questions rollup covering every NFR TBD plus any requirement-
  coverage gap noticed only once FR and NFR are read side by side

It never re-classifies an NFR or invents a new product-level assumption,
constraint, or risk — the one narrow exception is a requirement-level
refinement that a specific FR reveals but `vision.md` couldn't have known
about yet (see `prd.template.md`'s own header comment). Success metrics are
deliberately out of scope: `vision.md`'s north-star metrics stay the single
authoritative source, referenced via each FR's own trace.

## How does it work?

1. Validates all three upstream inputs are present with `status: success` —
   fails fast (`INSUFFICIENT_CONTEXT`) if `requirements_output` or
   `nfr_spec_output` is missing/failed; these two are hard preconditions
2. Carries every FR's statement, `traces_to`, and NFR table forward verbatim
   from the elicitor's/classifier's items — same ids and order
3. Condenses `vision.md`'s Regulatory Posture and Open Risks Carried Forward
   into Assumptions / Constraints / Risks, each tagged to specific FR(s) or
   `program-level`
4. Rolls up every TBD boundary condition and any coverage gap noticed while
   composing into Open Questions
5. Writes the Executive Summary last, introducing no new claim
6. Self-checks mechanically: FR count matches, no boundary condition
   dropped, no success-metrics field smuggled in
7. Saves the filled `prd.md` template to blob storage; items carry the same
   FR/NFR facts in full, and Assumptions/Constraints/Risks/executive summary
   condensed — see `output_schema.json`'s own note on why the mix differs
   from a single Phase 0/1 pattern

## Input

- **Source:** agent_output (elicitor's/classifier's items — no document; and
  read-only `vision.md` artifact) plus a direct `approval_comment` input
  parameter
- **Required:** `requirements_output`, `nfr_spec_output` — both must be
  `status: success`; `vision_output` — read-only, Assumptions/Constraints/
  Risks only; `approval_comment` — the Product Lead's approval text, quoted
  verbatim (no requirements document header to retrieve it from, 2026-08-07)

## Output

- **Type:** `prd`
- **Items:** `executive_summary`, `compound_splits[]`, `assumptions[]`,
  `constraints[]`, `risks[]`, `requirements[]`, `open_questions[]` — see
  `output_schema.json`. `requirements[]` and `compound_splits[]` carry FULL
  text (already-atomic upstream content); `executive_summary`,
  `assumptions[]`, `constraints[]`, `risks[]` are condensed (genuinely new
  synthesized narrative, full text only in `prd.md`)
- **Artifacts:** `prd.md` — the human-readable, self-contained document
- **Metadata:** every item carries `confidence` and `reasoning`;
  `traces_to` / `underlies_or_affects` are this agent's citation equivalent
- **Summary:** requirement/NFR/open-question counts, key composition
  decisions, what reflection found, guardrail results, gaps flagged

## Composition

```
agents/L1-requirements-prd-composer/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-typical.json
│   ├── output-01-typical.json
│   ├── input-02-missing-nfr-spec.json
│   └── output-02-missing-nfr-spec.json
└── golden/v1.0.0/
    ├── input-golden-01-harvestlink.json
    ├── golden-01-harvestlink.json
    ├── input-golden-02-insufficient.json
    └── golden-02-insufficient.json

prompts/L1-requirements-prd-composer/
└── instructions.md
```
