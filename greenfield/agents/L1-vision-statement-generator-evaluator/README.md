# L1-vision-statement-generator-evaluator

## Purpose

This is the last automated checkpoint before a human (the Product Lead)
reads the vision page in Confluence. If a serious regulatory finding was dropped anywhere in
the pipeline, this is the last place it can still be caught before it
reaches a person who will reasonably assume nothing was silently lost. This
agent's entire job is verifying that reconciliation is real, not just
claimed in the generator's own execution_summary.

## What does it do?

Accepts the original input (the upstream item sets plus viability_score) and
draft output from `L1-vision-statement-generator`, and produces:
- A reconciliation coverage check: every Amber/Red regulatory constraint_id
  must appear in at least one `open_risks` entry's `related_ids` — checked
  by set membership, not by trusting a count
- A groundedness check: the Amber/Red set rebuilt from
  `regulatory-feasibility.md` itself, so a constraint dropped *before*
  `regulatory_posture` is caught rather than scored as full coverage
- An executive-summary integrity check: every sentence checked individually
  against the sections below it
- A viability_score consistency check across `regulatory-feasibility.md`,
  `original_input`, `items` and the Confluence vision page — plus a narrative check that a
  capped score is matched by an executive summary naming the constraint that
  caused the cap
- Fixes for mechanically-recoverable gaps (built from the constraint's own
  mitigation_summary); escalation for anything requiring new judgment

## How does it work?

1. Ingests the generator's original input and draft output
2. Reads the vision page the generator wrote from **Confluence** with
   `tool-L1-confluence-reader` — `page_id = 519110668`, fixed in the prompt.
   No agent output is passed in; everything checked is built from that page.
   It also reads `regulatory-feasibility.md`,
   `idea-brief.json` and (optionally) `market-analysis.md` in a single
   blob-storage call. The brief is **JSON**, parsed by key path
3. Reads `L1-vision-statement-generator/evaluation.md` from GitHub with
   `tool-L1-github-reader-using-app` as the scoring source of truth, plus this
   evaluator's `examples/` folder for shape — repo, branch and folders all from
   the request. An unreadable rubric fails with `REFERENCE_UNAVAILABLE` rather
   than scoring against a remembered bar; corrections go back to Confluence
4. Computes the coverage-gap set (Amber/Red constraint_ids minus covered ids)
5. Checks each executive_summary sentence for grounding elsewhere in the document
6. Checks viability_score wasn't silently altered — against
   `regulatory-feasibility.md` as the authoritative source. It is **never
   re-derived here**: that already happened in
   `L1-vision-regulatory-feasibility-checker-evaluator`, and a discrepancy at
   this point is a finding to report, not arithmetic to redo
6a. Checks the Product Name: the H1, Product Name row and page title carry
   the same name, and an agent-proposed name is labelled as proposed. It aligns
   or labels a name, never changes the page title, and never picks one of its own
7. Fixes what's mechanically recoverable and rewrites the Confluence page with
   `tool-L1-confluence-writer` (`title`, full corrected XHTML `content`,
   `space_key = 514162689`) — only when a fix changed the document, never to
   blob storage; escalates anything requiring new analysis rather than
   inventing content

## Input

- **Source:** agent_output from `L1-vision-statement-generator`
- **Required:** `reference_repo`, `reference_branch`, `evaluation_rubric_kb_folder`, `folder_name`
- **Optional:** `examples_folder`
- **Fixed in the prompt:** vision page `page_id = 519110668`

## Output

- **Type:** `vision_statement` — the generator's own type. This agent
  re-emits the corrected result with the evaluation attached under
  `items.evaluation`, not a separate evaluation-only shape
- **Items:** the generator's full item sections, plus `evaluation` carrying
  `scores`, `overall_score`, `pass`, `findings[]`, `fixes_applied[]`,
  `reconciliation_check`, `final_decision` — see `output_schema.json`
- **Artifacts:** the Confluence page `<Product Name>-vision.md` — rewritten if
  corrected (new version from the writer), otherwise the generator's page as it stands
- **Summary:** overall score, coverage-gap result, executive-summary
  integrity result, viability_score consistency, guardrail results

## Composition

```
agents/L1-vision-statement-generator-evaluator/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-coverage-gap.json
│   ├── output-01-coverage-gap.json
│   ├── input-02-unsupported-summary-claim.json
│   └── output-02-unsupported-summary-claim.json
└── golden/v1.0.0/
    ├── input-golden-01-harvestlink.json
    ├── golden-01-harvestlink.json
    ├── input-golden-02-fabricated-risk.json
    └── golden-02-fabricated-risk.json

prompts/L1-vision-statement-generator-evaluator/
└── instructions.md
```
