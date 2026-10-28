# L0-nfr-classifier-evaluator

## Purpose

The classifier's self-check is mechanical; it can't judge whether a TBD was
actually resolvable or whether a cited source really supports its number.
This agent is the independent check (S6) that re-derives the classification
and catches both. Its corrected output, not the raw classifier output, is
what `L0-prd-composer` composes into the PRD.

## What does it do?

Accepts `L0-nfr-classifier`'s output plus its original input and produces:
- The **corrected NFR set** — `nfr_classifications[]` in exactly the
  classifier's structure, with every fix already applied
- An **evaluation block**:
  - `scores` — faithfulness, hallucination, consistency, relevance,
    reasoning quality, citation completeness
  - `overall_score` (0-10) and `pass`
  - `findings[]` — pass/fail per gate, each naming a taxonomy category or
    generator gate
  - `fixes_applied[]` — before/after and the reasoning for every change
  - `final_decision` — approved, fixed_and_approved, or escalate_to_hitl

It writes nothing to any external store. All corrections live in the JSON
output.

## How does it work?

1. Inherits `workflow_execution_id` from the classifier's output and
   generates a fresh `execution_id`
2. Retrieves the classifier's evaluation file and
   `kb-L0-nfr-classification-taxonomy` from GitHub
3. Approves a legitimate INSUFFICIENT_CONTEXT (status: failed) as-is
4. **Category coverage:** re-asks all six taxonomy questions against each
   FR's statement; a missing applicable category is a fail finding
5. **Citation integrity:** confirms every non-TBD boundary condition's
   source actually states or directly implies the value
6. **TBD resolvability:** checks every TBD against the regulatory
   feasibility analysis — a TBD a real source already answers is the
   highest-value finding
7. Fixes grounded gaps in the JSON (a resolvable TBD, a mis-cited source);
   never invents a number — escalates gaps that need stakeholder input
8. Emits the corrected JSON, the evaluation block, and a plain-text
   execution summary

## Input

- **Source:** agent_output from `L0-nfr-classifier`
- **Required:** `original_input` — the classifier's input
  (`requirements_output`, `regulatory_feasibility_output`)
- **Required:** `generator_output` — the classifier's JSON output
- **Required:** `github-nfr-evaluator-folder-location`,
  `github-nfr-evaluator-repo-name`, `github-nfr-evaluator-branch` — where
  the classifier's evaluation file lives
- **Required:** `github-nfr-classifier-kb-folder-location`,
  `github-nfr-classifier-kb-repo-name`, `github-nfr-classifier-kb-branch` —
  where `kb-L0-nfr-classification-taxonomy` lives

## Output

- **Type:** `nfr_classification` (same structure as the classifier) plus
  `evaluation`
- **Items:** corrected `nfr_classifications[]`
- **Evaluation:** `scores`, `overall_score`, `pass`, `findings[]`,
  `fixes_applied[]`, `final_decision`
- **Summary:** overall score and decision, category-coverage result,
  TBD-resolvability result, what was modified and why, KBs consulted,
  guardrails, gaps flagged

## Composition

```
agents/L0-nfr-classifier-evaluator/
├── L0-nfr-classifier-evaluator-prompt.md
├── evaluation.md
├── spec.yaml
└── README.md
```

Upstream: `L0-nfr-classifier`.
Downstream: `L0-prd-composer`.
