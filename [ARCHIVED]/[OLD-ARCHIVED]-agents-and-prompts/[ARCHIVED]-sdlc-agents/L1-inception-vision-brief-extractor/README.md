# L1-inception-vision-brief-extractor

## Purpose

S5 token optimisation agent. Compresses large vision documents (10-15K tokens) into structured extraction briefs (≤3K tokens) that downstream agents can process within constrained context windows.

## Why This Agent Exists

The `L1-inception-requirements-extractor` was overflowing its context window when processing large vision documents directly. A 12K vision doc + 7K EA KB + 2K instructions + 4K output = ~25K tokens — exceeding 16K model limits.

This agent sits between the vision generator and the requirements extractor, reducing the input from ~12K to ~3K tokens (75% reduction).

## Pipeline Position

```
L1-inception-vision-generator → [this agent] → L1-inception-requirements-extractor → evaluator → summariser
```

## I/O Summary

| Direction | Type | Size |
|-----------|------|------|
| Input | Vision document (markdown) | 10-15K tokens |
| Output | Structured brief (markdown inside JSON) | ≤3K tokens |

## What It Extracts

- Product name and problem statement
- User types with primary needs
- All capabilities/features as terse bullets
- Quality expectations (NFR signals)
- Constraints (technology, regulatory, business, timeline)
- Integration systems (name, direction, purpose)
- Data entities (name, attributes, PII flag)
- Success metrics (metric: target)
- Risks and dependencies
- MVP boundary (in-scope vs out-of-scope)
- Open questions/gaps

## What It Does NOT Do

- Does not assign IDs, priorities, or MoSCoW classification
- Does not generate PRD or structured requirements
- Does not add reasoning or citations
- Does not load any knowledge bases (pure extraction)

## Token Budget

Instructions: ~1K tokens. No KB load. Total context: input doc + ~1K instructions ≈ fit within 16K easily.
