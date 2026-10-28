# L1-vision-idea-intake

## Purpose

Every Phase 0 agent downstream — market analysis, regulatory feasibility,
vision synthesis — needs the same structured starting facts about an idea.
Without this agent, each would re-read and re-interpret a raw, inconsistently-
written idea brief independently, and drift from each other on basic facts
like who the target user actually is. This agent is the single point where a
raw idea becomes a structured, traceable brief.

## What does it do?

Accepts a raw idea brief (free text, up to ~2,000 words) and produces:
- A problem statement (1-3 sentences, grounded in the input)
- One or more target user segments
- A value proposition
- Candidate success metrics, each explicitly marked stated (in the input) or
  suggested (inferred — never presented as if the input said it)
- Open questions the input left unresolved

It never invents a fact the input doesn't support. If the input is too vague
to extract anything real, it fails explicitly (`INSUFFICIENT_CONTEXT`) rather
than filling gaps with plausible-sounding guesses.

## How does it work?

1. Ingests the raw idea text (direct input, or fetched from Confluence via
   `tool-L1-confluence-fetch-page` if only a page reference was given)
2. Validates the input is substantive enough to process; fails fast if not
3. Extracts problem, users, value proposition — each tagged with the exact
   input excerpt it's grounded in (`traced_to`)
4. Separates explicitly-stated metrics from inferred ones (`status` field)
5. Surfaces anything unresolved as an open question rather than guessing
6. Self-checks completeness and ID sequencing before returning (full scoring
   is delegated to `L1-vision-idea-intake-evaluator` downstream, per S6)

## Input

- **Source:** direct_input or file_upload
- **Required:** `idea_brief_text` — raw free-text idea brief
- **Optional:** `confluence_page_ref` — fetch the brief from Confluence instead
  of inline text; `stakeholder_list` — sponsoring stakeholders, if known

## Output

- **Type:** `idea_brief`
- **Items:** `problem_statement`, `target_users[]`, `value_proposition`,
  `candidate_success_metrics[]`, `open_questions[]` — see `output_schema.json`.
  No document artifact is produced; the narrative fields (`statement`) carry
  the full text directly.
- **Metadata:** every item carries `confidence`, `reasoning`, and `traced_to`
  (this agent's substitute for KB citation, since it grounds against the raw
  input, not a knowledge base)
- **Summary:** counts produced, what was inferred vs. stated, guardrail
  results, tools invoked, and the open questions flagged

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
