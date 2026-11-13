# L0-solution-architect-evaluator

## Purpose

`L0-solution-architect`'s own Reflection block covers what the
generator thought it did. This evaluator checks whether it actually did it.
A schema-valid solution-architecture.md can drop an entity from DAT-1, omit
an APP-2.3 edge from INT-1, leave a REQ-* out of the satisfaction index, or
mark a technology DECIDED when EA11 was absent — and none of those failures
would show up in the generator's own self-check count. This agent catches
them before the Solution Architect and Platform Lead gates by running every
completeness check as set membership against the original target.

## What does it do?

Reads `solution-architecture.md` from the generator's JSON output (or an
upload), the original `target-architecture.md` it was built from (upload or
Confluence page id), the three KBs (Confluence page ids, the same pages the
generator read) and the rubric (GitHub), and produces:
- **Six set-membership completeness checks**, each derived independently from
  the target: entities → DAT-1, edges → INT-1, REQ-* → satisfaction index,
  CON-* → constraint realisation table, § 4.2 capability classes → PLT-6,
  SEC-*/TB-* → security controls
- **Technology grounding check**: every technology traces to EA11 (source,
  lifecycle, decision status); no DECIDED claim where EA11 was absent or
  not APPROVED; every `contain` has a recorded exception; nothing marked
  `retire`
- **Number grounding check**: every retention, residency, timeout, RTO, RPO
  traces to a target budget, KB section or arithmetic allocation, or is
  PENDING with a condition trigger in a PEND row
- **Scope check**: only band-First, high-lead-time, exit-proof and
  cross-context-policy capabilities are DECIDED; everything else is NOT
  PRESENT with its band
- **Cross-section consistency check**: DAT-1 classifications match DAT-3
  classes; INT-1 sync edges align with INT-2 contracts; INT-1 event edges
  align with INT-3 topics; PLT-6 AVAILABLE rows appear in the Cycle 0 exit
  proof
- Fixes what is mechanically recoverable from the upstream target; escalates
  genuine judgment calls
- **Publishes** the corrected document to Confluence for every final_decision,
  including `escalate_to_hitl` — the Solution Architect and Platform Lead
  review it there

## How does it work?

```
generator JSON (artifacts[0].content) ──► this evaluator (evaluate + fix) ──► Confluence: <product>-solution-architecture.md
                     target + KBs from Confluence (page ids) ─┘   rubric from GitHub ─┘
```

1. Takes `solution-architecture.md` from **S3** with `tool-L0-s3-files-reader`
   (`s3_folder_name`, or the folder in the generator JSON's
   `artifacts[0].storage`), else from the generator JSON's
   `artifacts[0].content`, else from an upload,
   and `target-architecture.md` / `prd.md` from an upload or by Confluence
   page id
2. Reads the three KBs from **Confluence** by page id (the same pages the
   generator read), and the scoring rubric (`evaluation.md`) from **GitHub**
   with `tool-L0-github-reader-using-app` — one call, with `rubric_repo`,
   `rubric_branch` and `solution_architect_rubric_folder` from the request.
   An unreadable rubric fails with `REFERENCE_UNAVAILABLE`
3. Builds six id sets from `target-architecture.md` (entities, edges,
   REQ-*, CON-*, capability classes, SEC-*/TB-*) and checks each by set
   membership against the corresponding section of `solution-architecture.md`
4. Verifies technology grounding section by section (PLT-1 decisions first,
   then data and integration choices)
5. Verifies every PEND row has a condition trigger; checks every PENDING
   value has a PEND row
6. Re-derives cross-section consistency independently (DAT-1 ↔ DAT-3,
   INT-1 ↔ INT-2/INT-3, PLT-6 ↔ exit proof)
7. Fixes mechanically-recoverable gaps (a missing satisfaction-index row
   restorable from the target's REQ-* text; a corrected decision status
   where EA11 was absent). Never invents a technology, entity or constraint
   not grounded in the target
8. **Publishes** the corrected document to Confluence with
   `tool-L0-confluence-writer` — `title = <product>-solution-architecture.md`,
   content converted to XHTML, `space_key` from the request — for **every**
   final_decision. Issues that could not be fixed are in findings

## Input

- **Source:** `solution-architecture.md` from S3 (`s3_folder_name`, the
  same folder the generator saved to), else `L0-solution-architect`'s JSON
  output (`artifacts[0].content`), else an upload
- **Required:** `rubric_repo`, `rubric_branch`,
  `solution_architect_rubric_folder`, `confluence_space_key`,
  `enterprise_architecture_kb_page_id`, `enterprise_security_kb_page_id`,
  and the target as an upload or `target_architecture_page_id`
- **Optional:** `s3_folder_name`, `prd_page_id`, `domain_api_patterns_kb_page_id`

## Output

- **Type:** `solution_architecture` — the generator's own type, re-emitted
  with the evaluation under `items.evaluation`
- **Items:** the generator's full item sections, plus `evaluation` carrying
  `scores`, `overall_score`, `findings[]`, `fixes_applied[]`,
  `coverage_check`, `final_decision` — see `output_schema.json`
- **Artifacts:** the Confluence page `<product>-solution-architecture.md`,
  always published, in chunks of whole sections (one writer call each, about
  12,000 characters of markdown) so no single call times out
- **Summary:** overall score, completeness check results per dimension,
  grounding findings, cross-section consistency results, guardrail results

## Composition

```
agents/L0-solution-architect-evaluator/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-missing-entity.json
│   ├── output-01-missing-entity.json
│   ├── input-02-decided-without-ea11.json
│   └── output-02-decided-without-ea11.json
└── golden/v1.0.0/
    ├── input-golden-01-harvestlink.json
    ├── golden-01-harvestlink.json
    ├── input-golden-02-edge-dropped.json
    └── golden-02-edge-dropped.json

prompts/L0-solution-architect-evaluator/
└── instructions.md
```
