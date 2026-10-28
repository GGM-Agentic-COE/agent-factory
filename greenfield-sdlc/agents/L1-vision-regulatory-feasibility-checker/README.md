# L1-vision-regulatory-feasibility-checker

## Purpose

A viable-looking idea can be dead on arrival for licensing, data-residency,
or consumer-protection reasons. This needs to surface before roadmap
commitment, not after a team has already built against it. This agent
exists because "someone should check the regulations" is exactly the kind
of step that gets skipped under deadline pressure — this makes it
mandatory, structured, and impossible to silently drop a serious finding.

## What does it do?

Accepts the problem statement and target geography from `L1-vision-idea-intake`
and produces:
- A list of applicable regulatory constraints, each classified Green/Amber/Red
- A citation to a specific regulation/section for every constraint — no
  generic "comply with regulations" statements
- A concrete mitigation for every Amber/Red constraint, or an explicit
  `requires_legal_review` flag when no precedented mitigation exists
- An overall feasibility verdict, justified by the specific constraints
  driving it

Zero tolerance for omitting a Red-classified constraint — the output schema
itself structurally rejects a Red or Amber constraint that has neither a
mitigation nor a legal-review flag.

## How does it work?

1. Ingests `problem_statement` and target geography/category from the upstream agent
2. Queries `kb-L1-regulatory-frameworks-index` to identify which regulator
   categories apply at all
3. Queries `kb-L2-domain-regulatory` (and `tool-L1-regulatory-db-lookup`
   for anything beyond the KBs) for the specific applicable rules
4. Classifies each constraint Green/Amber/Red with a citation
5. Provides a mitigation for every Amber/Red item — `requires_legal_review`
   is reserved for genuinely unprecedented cases, not a default
6. Sets `overall_status` from the worst constraint, unless every Amber/Red
   item has a precedented mitigation — in which case it explicitly justifies
   why the verdict is one level better than the worst individual item
7. Self-checks that no Red item was silently dropped before returning (full
   scoring delegated to `L1-vision-regulatory-feasibility-checker-evaluator`, per S6)

## Input

- **Source:** agent_output from `L1-vision-idea-intake`
- **Required:** `problem_statement`, `target_geography`
- **Optional:** `product_category` — narrows the regulator lookup if known

## Output

- **Type:** `regulatory_feasibility`
- **Items:** `constraints[]` (id, status, citation, rationale, mitigation,
  requires_legal_review), `overall_status`, `open_items[]` — see `output_schema.json`;
  items carry the full rationale and mitigation directly, there is no separate
  document produced
- **Metadata:** every constraint carries `citation` (BLOCKER guardrail
  `gr-L1-citation-verifier`, 100% required, not just scored) and `reasoning`
- **Summary:** constraint counts by status, overall verdict rationale, KB
  content used, guardrail results, open items flagged

## Composition

```
agents/L1-vision-regulatory-feasibility-checker/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-typical.json
│   ├── output-01-typical.json
│   ├── input-02-novel-question.json
│   └── output-02-novel-question.json
└── golden/v1.0.0/
    ├── input-golden-01-harvestlink.json
    ├── golden-01-harvestlink.json
    ├── input-golden-02-insufficient.json
    └── golden-02-insufficient.json

prompts/L1-vision-regulatory-feasibility-checker/
└── instructions.md
```
