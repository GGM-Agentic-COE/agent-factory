# L1-vision-idea-intake

## Purpose

Every Phase 0 agent downstream (market analysis, regulatory feasibility,
vision synthesis) needs the same structured starting facts about an idea.
Without this agent, each would re-read and re-interpret a raw, inconsistently-
written idea brief independently, and drift from each other on basic facts
like who the target user actually is. This agent is the single point where a
raw idea becomes a structured, traceable brief, and it is the pipeline root:
nothing sits upstream of it.

## What does it do?

Accepts a raw idea brief (free text, inconsistent length, never pre-structured)
and produces:
- A problem statement (1-3 sentences, grounded in the input)
- One or more target user segments (`TU-01`, `TU-02`, ...)
- A value proposition
- Success metrics (`SM-01`, ...), each explicitly marked `stated` (in the
  input) or `suggested` (inferred, never presented as if the input said it)
- Open questions the input left unresolved (`OQ-01`, ...)

It never invents a fact the input doesn't support. If the input is too vague
to ground a problem statement, at least one target user, and a value
proposition, it fails explicitly (`INSUFFICIENT_CONTEXT`) rather than filling
gaps with plausible-sounding guesses. On success it also stores the brief as
`idea-brief.json` in Amazon S3 for downstream agents.

## How does it work?

1. Resolves the source: uses `idea_brief_text` if non-blank; otherwise fetches
   the page via `tool-L1-confluence-fetch-page` from `confluence_page_ref`.
   If both are given, the text wins and Confluence is not called
2. Extracts the product name from the runtime source filename (never from the
   brief itself); if it can't be determined, records an open question instead
   of guessing
3. Validates the input is substantive enough to process; fails fast with
   `INSUFFICIENT_CONTEXT` if it can't ground all three core fields
4. Extracts problem, users, value proposition, and metrics, each tagged with
   the exact input excerpt it's grounded in (`traced_to`, max 50 words)
5. Separates explicitly-stated metrics from inferred ones (`classification`
   field); suggested metrics always score below 0.90 confidence
6. Surfaces anything unresolved as an open question rather than guessing
7. Self-checks grounding, classification, ID sequencing, and schema conformance
   (internal only, not output)
8. Runs the quality gate guardrail once on the final candidate
9. Only after the gate passes, stores `idea-brief.json` in Amazon S3 at
   `<product-name>/wf-<workflow-id>/idea-brief.json`. The stored file contains
   exactly `content.items`, with no envelope or runtime metadata

A storage write is never claimed unless the storage result confirms it, and
the execution summary reports only tools and guardrails actually invoked.

## Input

- **Source:** direct_input or file_upload
- **Required (one of):** `idea_brief_text` (raw free-text idea brief) or
  `confluence_page_ref` (fetch the brief from Confluence instead of inline
  text; used only when `idea_brief_text` is blank)
- **Optional:** `stakeholder_list` (sponsoring stakeholders, if known; never
  used to infer target users)
- **Runtime metadata:** source filename (product name), workflow ID, execution
  ID, and the configured S3 bucket. Missing values are recorded as open
  questions or failures, never fabricated

## Output

- **Type:** `idea_brief`
- **Items:** `problem_statement`, `target_users[]`, `value_proposition`,
  `success_metrics[]`, `open_questions[]`. See `output_schema.json`.
  No separate document artifact is produced; the narrative fields (`text`)
  carry the full statement directly
- **Metadata:** every narrative item carries `confidence` and `traced_to`
  (this agent's substitute for KB citation, since it grounds against the raw
  input, not a knowledge base). Open questions carry only `id` and `question`
- **Document reference:** on success, the confirmed S3 location (`provider`,
  `bucket`, `folder`, `workflow_id`, `key`). `null` on any failure
- **Summary:** counts produced (target users, stated vs. suggested metrics,
  open questions), key extraction decisions and gaps, and the actual results
  of Confluence retrieval, the quality gate, and S3 storage, where invoked
- **Failures:** `status: failed` with `INSUFFICIENT_CONTEXT` for sufficiency
  failures, the guardrail's own message for quality-gate failures, or the
  actual storage error for infrastructure failures

## Composition

```
agents/L1-vision-idea-intake/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-internal-tool.json
│   ├── output-01-internal-tool.json
│   ├── input-02-vague.json
│   └── output-02-vague.json
└── golden/v1.0.0/
    ├── input-golden-01-harvestlink.json
    ├── golden-01-harvestlink.json
    ├── input-golden-02-insufficient.json
    └── golden-02-insufficient.json

prompts/L1-vision-idea-intake/
└── instructions.md
```