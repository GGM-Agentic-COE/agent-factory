# L1-vision-idea-intake-evaluator

## Purpose

Letting a generator grade its own homework defeats the point of a quality
gate. This agent is the independent, different-prompt check the
Generator→Evaluator pattern (S6) requires. It scores the `idea-brief.json`
produced by `L1-vision-idea-intake` against the enterprise evaluation rubric,
applies only corrections the document itself supports, and reports a finding
for everything else, rather than trusting the generator's own self-assessment
or filling gaps with invented content.

## What does it do?

Accepts the generator's idea brief and its agent output, and produces:
- Independent scores (0.0–1.0) on 8 thresholded dimensions: accuracy, fix
  quality, completeness, grounding, schema compliance, traceability, metric
  classification, and execution reporting, drawn from 15 evaluation
  dimensions defined in the evaluation KB
- A status (pass, fail, not_evaluated, or not_applicable) for each of 20
  quality gates
- Findings, each with category, specific issue, affected content, rubric
  criterion, severity, and whether a fix was applied
- Grounded fixes applied directly to the brief and re-uploaded to the same
  location, rather than triggering a full re-generation
- A final verdict: pass or fail

A dimension or gate that wasn't actually evaluated is reported as
`not_evaluated` with a null score, never as 0.0 or fail.

## How does it work?

1. Resolves the document: uses `document_content` if supplied inline;
   otherwise reads the artifact from the location in `generator_output`; as a
   last resort lists the working directory and reads a single
   `idea-brief*.json` (never guessing if several exist). If no valid JSON can
   be obtained, stops and returns an input-failure result without retrieving
   the KB, scoring, or fixing
2. If `generator_output` or `workflow_execution_id` is missing, continues in
   read-only mode: scores normally, applies no fixes, does no re-upload, and
   records the recommended corrections in each finding
3. Retrieves the evaluation KB (`Vision-Idea-Evaluation.md` via the GitHub
   reader) and consults the attached `kb-L1-vision-idea-intake-evaluation-slim`
   if present. The attached KB is the source of truth; any conflict between
   the two is recorded as a finding. If no KB can be loaded, it does not
   invent gates or thresholds, and returns a fail with all scores
   `not_evaluated`
4. Validates the brief's structure, evaluates every applicable quality gate,
   scores each dimension, and records a finding for every failed criterion
5. Applies a fix only when the document or its source evidence directly
   supports it. A gap that can't be safely corrected stays in place and is
   reported as a finding
6. Re-uploads the corrected `idea-brief.json` verbatim to the same artifact
   location, only if fixes were applied and a storage-write tool exists.
   Never creates a second location
7. Returns a verdict: pass only if all mandatory scores and gates pass and no
   critical grounding, schema, or traceability issue remains. Fails rather
   than forcing a pass on a fundamentally unusable brief or one that would
   need invented content to fix
8. Returns the evaluation result as raw JSON in a plain-text final message,
   never ending on a tool call and never returning the brief itself

It only calls tools that appear in its tool list, with at most one KB
retrieval, one artifact read, and one re-upload.

## Input

- **Source:** idea brief and agent output from `L1-vision-idea-intake`
- **Required:** `document_content` (full `idea-brief.json`, preferably inline
  or as a file upload) and `generator_output` (the generator's Agent Output
  JSON, which provides the workflow ID and artifact location)
- **Inherited:** `workflow_execution_id` comes from `generator_output`; it is
  never generated or substituted

## Output

- **Type:** `evaluation_result`
- **Items:** `verdict`, scores per dimension, status for all 20 quality gates,
  `findings[]` (with `fix_applied` and `fix_description`), `retrieval_status`,
  `dimensions_evaluated`, `artifact_reupload_status`, `evaluation_kb`,
  `tools_invoked`, and `guardrails_invoked`. See `output_schema.json`
- **Input-failure result:** verdict fail, every score null and
  `not_evaluated`, `input_content_sufficient` fail with all other gates
  `not_evaluated`, one critical finding per missing input stating the exact
  reason, and `retrieval_status` and `artifact_reupload_status` both
  `not_attempted`
- **Summary:** verdict, scores and gate results, findings breakdown, fixes
  applied and re-upload status, and only the tools, KBs, and guardrails that
  actually ran

## Composition

```
agents/L1-vision-idea-intake-evaluator/
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
    ├── input-golden-01-harvestlink.json
    ├── golden-01-harvestlink.json
    ├── input-golden-02-unfixable.json
    └── golden-02-unfixable.json

prompts/L1-vision-idea-intake-evaluator/
└── instructions.md
```