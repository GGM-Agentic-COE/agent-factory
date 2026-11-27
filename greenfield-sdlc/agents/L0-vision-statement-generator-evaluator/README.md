# L0-vision-statement-generator-evaluator

## Purpose

This is the last automated checkpoint before a human (the Product Lead)
reads the vision document. If a serious regulatory finding was dropped anywhere in
the pipeline, this is the last place it can still be caught before it
reaches a person who will reasonably assume nothing was silently lost. This
agent's entire job is verifying that reconciliation is real, not just
claimed in the generator's own execution_summary.

## What does it do?

Reads the vision document `L0-vision-statement-generator` saved to S3
(`vision.md`), and produces:
- A reconciliation coverage check: every Amber/Red regulatory constraint_id
  must appear in at least one `open_risks` entry's `related_ids` — checked
  by set membership, not by trusting a count
- A groundedness check: the Amber/Red set rebuilt from
  `regulatory-feasibility.md` itself, so a constraint dropped *before*
  `regulatory_posture` is caught rather than scored as full coverage
- An executive-summary integrity check: every sentence checked individually
  against the sections below it
- A viability_score consistency check across `regulatory-feasibility.md`,
  `items` and `vision.md` — plus a narrative check that a
  capped score is matched by a Bottom line and Section 12 naming the constraint that
  caused the cap
- Fixes for mechanically-recoverable gaps (built from the constraint's own
  mitigation_summary); escalation for anything requiring new judgment

## How does it work?

```
generator ──► S3: <product>/<wf id>/vision.md ──► this evaluator (evaluate + fix) ──► Confluence: <Product Name>-vision
```

1. Reads `vision.md` (written by the generator), `regulatory-feasibility.md`,
   `idea-brief.json` and (optionally) `market-analysis.md` from **S3** with
   `tool-L0-s3-files-reader`: `vision.md` and `regulatory-feasibility.md`
   from the run folder, `idea-brief.json` and `market-analysis.md` from the
   brief's original folder. Both folders come from the generator's
   `artifacts[0].storage` (`run_folder`, `source_folder`); there is no folder
   input. Everything checked is built from `vision.md`; the
   generator's JSON output supplies only `workflow_execution_id`, plus the
   document itself when the generator could not save it to S3. The brief is
   **JSON**, parsed by key path
2. Reads the scoring rubric (`evaluation.md`) from GitHub with
   `tool-L0-github-reader-using-app` — one call, fixed in the prompt: repo
   `agentic-sdlc-knowledge-bases`, branch `main`, folder
   `planning/vision-statement-generator/L0-vision-statement-generator`. No
   examples are read. An unreadable rubric fails with `REFERENCE_UNAVAILABLE`
   rather than scoring against a remembered bar
3. Computes the coverage-gap set (Amber/Red constraint_ids minus covered ids)
4. Checks each executive_summary sentence for grounding elsewhere in the document
5. Checks viability_score wasn't silently altered — against
   `regulatory-feasibility.md` as the authoritative source. It is **never
   re-derived here**: that already happened in
   `L0-regulatory-feasibility-checker-evaluator`, and a discrepancy at
   this point is a finding to report, not arithmetic to redo
6. Checks the Product Name: the H1 and the Document Control Product row carry the same
   name, and an agent-proposed name is labelled as proposed. It aligns or
   labels a name, and never picks one of its own
7. Fixes what's mechanically recoverable in its working copy of the
   document; escalates anything requiring new analysis rather than
   inventing content. Nothing is written back to S3 — the S3
   `vision.md` stays as the generator's draft
8. **Publishes** the corrected document to Confluence with
   `tool-L0-confluence-writer` — `title = <Product Name>-vision`, content
   converted to XHTML, `space_key = 514162689` — for **every** decision,
   including `escalate_to_hitl`. The human reviews it in Confluence; issues
   that couldn't be fixed are listed in the findings

## Input

- **Source:** `vision.md` in S3, written by `L0-vision-statement-generator`
- **Required:** none — both S3 folders come from `L0-vision-statement-generator`'s output
- **Fixed in the prompt:** the rubric's GitHub repo, branch and folder

## Output

- **Type:** `vision_statement` — the generator's own type. This agent
  re-emits the corrected result with the evaluation attached under
  `items.evaluation`, not a separate evaluation-only shape
- **Items:** the generator's full item sections, plus `evaluation` carrying
  `scores`, `overall_score`, `findings[]`, `fixes_applied[]`,
  `reconciliation_check`, `final_decision` — see `output_schema.json`
- **Artifacts:** the Confluence page `<Product Name>-vision`, always published
- **Summary:** overall score, coverage-gap result, executive-summary
  integrity result, viability_score consistency, guardrail results

## Composition

```
agents/L0-vision-statement-generator-evaluator/
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

prompts/L0-vision-statement-generator-evaluator/
└── instructions.md
```
