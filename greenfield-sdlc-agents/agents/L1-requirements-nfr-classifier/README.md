# L1-requirements-nfr-classifier

## Purpose

`L1-requirements-prd-composer` and Phase 4's design agents need every
functional requirement's cross-functional constraints — performance,
security, scalability, availability, compliance, usability — resolved to a
real, checkable source before design starts. A fabricated SLA or throughput
number discovered at design time is far more expensive to unwind than one
caught here. This agent is the single point where each `requirements.md` FR
is classified once, consistently, against a real source or an honest
"TBD" — never a plausible-sounding guess.

## What does it do?

Accepts `functional_requirements` items (from `L1-requirements-elicitor` —
items only, no document, 2026-08-07) and `vision.md` (artifact, from
`L1-vision-statement-generator`, cited directly for its Regulatory Posture
section) and produces:
- One NFR-classification entry per functional requirement, tagging only the
  categories that genuinely apply (never a padded fixed six)
- For each applicable category, a boundary condition that is either an
  explicit number/rule grounded in `requirements.md`, `vision.md` (including
  its Regulatory Posture section), or `kb-L1-enterprise-security`, or the
  literal "TBD — needs stakeholder input" if genuinely ungrounded

It never invents a number, threshold, or regulation citation not actually
present in a real source, and it never marks something TBD that a group
security policy or vision.md's Regulatory Posture already answers.

## How does it work?

1. Reads every FR in `requirements.md`, in order
2. For each FR, walks `kb-L1-nfr-classification-taxonomy`'s six categories
   and asks that category's question — applies only the categories that are
   genuinely relevant to that FR's statement
3. For each applicable category, checks `requirements.md` (the FR's own
   statement) and `vision.md` (e.g. a North-Star Metric target, or its
   Regulatory Posture section for Compliance) for an explicit or
   directly-implied number/rule; checks `kb-L1-enterprise-security` for a
   group policy that already answers a Security/Compliance/Availability
   question (e.g. a retention period or uptime tier) before ever writing TBD
4. Writes the literal "TBD — needs stakeholder input" only when genuinely
   ungrounded — never a fabricated placeholder value
5. Self-checks mechanically: every non-TBD condition carries a specific
   source, every TBD condition carries source "—", ids match
   `requirements.md` exactly. No document is produced — `items` is the
   sole, authoritative output

## Input

- **Source:** agent_output (elicitor's items — no document; `vision.md`
  artifact from `L1-vision-statement-generator`)
- **Required:** `requirements_output` — the elicitor's full output, status
  must be `success`; `vision_output` — the vision agent's full output,
  read directly for Compliance citations (vision.md § Regulatory Posture),
  not a KB

## Output

- **Type:** `nfr_classification`
- **Items:** `nfr_classifications[]` — one entry per FR, each with
  `boundary_conditions[]` (`category`, `boundary_condition`, `source`); see
  `output_schema.json`. Boundary conditions are carried in FULL in items,
  not summarized — a boundary condition is already a short, atomic phrase,
  so unlike Phase 0's meta-points pattern there is nothing long to condense.
  No document artifact is produced; items is the sole, authoritative record
- **Metadata:** every classification carries `confidence` and `reasoning`;
  `source` is this agent's citation equivalent for each boundary condition
- **Summary:** FR count classified, categories applied, TBDs left open and
  why, guardrail results, KBs consulted, gaps flagged

## Composition

```
agents/L1-requirements-nfr-classifier/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-typical.json
│   ├── output-01-typical.json
│   ├── input-02-no-requirements.json
│   └── output-02-no-requirements.json
└── golden/v1.0.0/
    ├── input-golden-01-harvestlink.json
    ├── golden-01-harvestlink.json
    ├── input-golden-02-insufficient.json
    └── golden-02-insufficient.json

prompts/L1-requirements-nfr-classifier/
└── instructions.md
```
