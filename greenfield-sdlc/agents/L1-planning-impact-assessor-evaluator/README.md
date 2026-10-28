# L1-planning-impact-assessor-evaluator

## Purpose

`L1-planning-impact-assessor` checks a PRD's requirements against
`service_catalog`, `cmdb_export`, and `kb-L1-enterprise-architecture` — but
a generator re-checking its own capability/technical-touch findings against
the estate it just checked is exactly the failure mode a quality gate
exists to catch (a wrongly-dismissed service-catalog match, a CI the CMDB
and KB actually disagree about that the generator's pass missed). This
agent independently re-derives both checks from the same source data.

## What does it do?

Scores the impact assessor's draft output against
`L1-planning-impact-assessor/evaluation.md`, sourced from
`kb-L1-enterprise-architecture` for the narrative cross-check. Fixes what's
mechanically recoverable (a touched/not-touched finding that contradicts
both the CMDB and the KB); escalates what needs new judgment (a genuine
KB/data disagreement with no clear resolution).

## How does it work?

1. Loads `L1-planning-impact-assessor/evaluation.md` as source of truth
2. Retrieves `impact-assessment.md` from s3 via
   `generator_output.content.artifacts[0].storage.location` — items already
   carry full facts (not meta-points), but the retrieved document is still
   the artifact of record any document-touching fix must be pushed back to
3. Re-derives the capability check independently: compares
   `original_input.service_catalog.services[]` against the PRD's proposed
   capabilities itself, rather than accepting `matched_service_id`/
   `is_duplicate` because they "look reasonable"
4. Re-derives the technical-touch check independently: for every relevant
   CI in `original_input.cmdb_export`, checks touched/not-touched against
   BOTH the CMDB relationships and `kb-L1-enterprise-architecture`'s
   narrative — a CI where the two sources disagree, or where the
   generator's row contradicts either source, is a finding
5. Checks every FR has a component with a blast-radius rationale, and that
   external_dependencies includes anything newly surfaced by step 4
6. Fixes mechanically-recoverable gaps; escalates genuine judgment calls
7. If a fix changes content also present in `impact-assessment.md` (a
   touched/not-touched finding, a blast-radius rationale), corrects the
   document too and overwrites it at the SAME s3 location — a fix recorded
   only in items and left uncorrected in the document is incomplete
8. `final_decision` per the standard rule

## Input

- **Source:** agent_output (`L1-planning-impact-assessor`'s original input
  + draft output)

## Output

- **Type:** `evaluation_result`
- **Items:** `scores`, `overall_score`, `pass`, `findings[]`,
  `fixes_applied[]`, `final_decision` — shared shape across all Phase 0/1
  evaluators, see `output_schema.json`
- **Summary:** overall_score, pass/fail, findings breakdown, what was
  fixed (including any document correction), knowledge bases consulted,
  gaps flagged

## Composition

```
agents/L1-planning-impact-assessor-evaluator/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-minor-fix.json
│   ├── output-01-minor-fix.json
│   ├── input-02-legitimate-failure.json
│   └── output-02-legitimate-failure.json
└── golden/v1.0.0/
    ├── input-golden-01-thornbury.json
    ├── golden-01-thornbury.json
    ├── input-golden-02-mismatch.json
    └── golden-02-mismatch.json

prompts/L1-planning-impact-assessor-evaluator/
└── instructions.md
```
