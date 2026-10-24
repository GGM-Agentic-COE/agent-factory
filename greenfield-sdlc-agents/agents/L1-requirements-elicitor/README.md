# L1-requirements-elicitor

## Purpose

Every Phase 1 agent downstream — NFR classification, PRD composition,
impact assessment, dependency mapping — and Phase 3's story generation all
need the same atomic, traceable requirement set. Without this agent, each
would re-read and re-interpret `vision.md` independently and drift on
scope. This agent is the single point where an approved vision becomes a
structured, ISO/IEC/IEEE 29148-quality requirement set.

## What does it do?

Accepts an approved `vision.md` (with a recorded Product Lead approval
comment — it refuses to run without one) and produces:
- Atomic functional requirements, each stating exactly one testable
  capability, traced to exactly one `vision.md` section
- An explicit record of every compound clause `vision.md` bundled two
  capabilities into, and which FR ids it was split into

It never invents a capability `vision.md` doesn't support, and never lets a
compound "X and Y" clause pass through as a single requirement — a system
could satisfy one half without the other, so each half gets its own id and
its own acceptance test.

## How does it work?

1. Validates a Product Lead approval comment is present — fails fast
   (`INSUFFICIENT_CONTEXT`) if not; fetches it via
   `tool-L1-confluence-fetch-page` if it lives on the vision.md Confluence
   page rather than being passed inline
2. Reads `vision.md` section by section — Problem, Target Users, Value
   Proposition, Regulatory Posture, Roadmap Outline, North-Star Metrics
3. Extracts one atomic requirement per testable capability; splits any
   clause bundling two capabilities into separate FRs instead of passing
   it through compound
4. Traces every FR to the exact `vision.md` section it came from
5. Self-checks mechanically against `kb-L1-requirements-quality-standard`:
   vague-term scan (Unambiguous) and compound-clause scan (Singular) — the
   cheap, deterministic checks only; full rubric (Complete's coverage
   check, Verifiable, Consistent, Feasible/Correct) is delegated to
   `L1-requirements-elicitor-evaluator` downstream, per S6. No document is
   produced or saved — `items` carries the full FR statements directly (not
   condensed — see output_schema.json's own note on why this differs from
   Phase 0's meta-points pattern)

## Input

- **Source:** agent_output (`vision.md` from `L1-vision-statement-generator`)
- **Required:** `vision_output` — the vision agent's full output, status
  must be `success` with a recorded Approval; `approval_comment` — the
  Product Lead's comment, quoted verbatim

## Output

- **Type:** `requirements`
- **Items:** `functional_requirements[]`, `compound_splits[]` — see
  `output_schema.json`. Unlike Phase 0, FR statements are carried in FULL
  in items, not summarized — a functional requirement is already atomic,
  and downstream agents need the exact wording, not a gloss
- **Metadata:** every FR carries `confidence` and `reasoning`; `traces_to`
  is this agent's citation equivalent, since it grounds against `vision.md`
  directly, not a knowledge base
- **Summary:** requirement count, compound splits made, what reflection
  found, guardrail results, tools invoked, gaps flagged

## Composition

```
agents/L1-requirements-elicitor/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-typical.json
│   ├── output-01-typical.json
│   ├── input-02-no-approval.json
│   └── output-02-no-approval.json
└── golden/v1.0.0/
    ├── input-golden-01-harvestlink.json
    ├── golden-01-harvestlink.json
    ├── input-golden-02-insufficient.json
    └── golden-02-insufficient.json

prompts/L1-requirements-elicitor/
└── instructions.md
```
