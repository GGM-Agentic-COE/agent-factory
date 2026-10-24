# L1-inception-requirements-extractor-evaluator

## Purpose

Post-generation quality evaluator for the PRD documents produced by `L1-inception-requirements-extractor`. Implements the S6 pattern — separating evaluation from generation to reduce token load during extraction while ensuring comprehensive quality validation.

## What It Does

1. Retrieves the PRD document (direct input, agent_output, or blob storage)
2. Checks 19 inline quality gates (structure, extraction quality, traceability, data/privacy, coherence)
3. Scores across 6 dimensions using the evaluation KB
4. Fixes issues it can resolve (vague NFRs, missing citations, wrong priorities)
5. Re-scores the corrected document (reports post-fix scores)
6. Re-uploads the corrected PRD to the same blob location
7. Returns verdict, scores, findings, and artifact status

## Pipeline Position

```
L1-inception-requirements-extractor → [this agent] → L1-inception-epics-generator
```

## I/O Summary

| Direction | Type | Description |
|-----------|------|-------------|
| Input | AgentOutput + PRD | Output from requirements extractor + original input for faithfulness |
| Output | Evaluation JSON | Verdict, scores (post-fix), findings with fixes, artifact location |

## Key Design Decisions

- **Inline critical gates** — 19 non-negotiable checks embedded in prompt (not KB-dependent)
- **Re-score loop** — scores reflect corrected document, not original
- **Unfixable pattern** — findings that can't be fixed without hallucinating are flagged with reason
- **Faithfulness requires original input** — evaluator compares PRD against what was actually provided to the extractor
- **Fix constraints** — cannot invent requirements not in original input

## Dependencies

- KB: `kb-L1-inception-requirements-extractor-evaluation` (scoring thresholds, additional checks)
- Tools: `tool-L1-azure-blob-reader`, `tool-L1-azure-blob-writer`
