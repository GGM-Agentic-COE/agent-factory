# L1-inception-requirements-extractor-agent

## Purpose

Extracts structured functional and non-functional requirements from a plain-text product idea or vision document. Transforms unstructured thinking into actionable, categorised requirements that downstream agents can consume.

## What does it do?

Takes a product idea, feature description, or vision document in plain text and produces:
- **Functional requirements (FRs)** — what the system must do
- **Non-functional requirements (NFRs)** — how the system must perform (measurable)
- **Constraints** — fixed decisions that limit solution space (technology, business, regulatory)
- **Assumptions** — things inferred but not explicitly stated (flagged for confirmation)
- **Gaps** — information missing from the input with suggested clarification questions

Every requirement is traceable to a specific phrase in the input, prioritised using MoSCoW, and confidence-scored (explicit = 0.9+, inferred = 0.7-0.8).

## How does it work?

1. Ingests input (plain text, file upload, or prior agent output)
2. Validates input is non-empty and describes a product/feature idea
3. Reads entire input to identify the core concept
4. Extracts FRs using "The system shall..." format
5. Extracts NFRs with measurable criteria (time, percentage, uptime)
6. Identifies constraints (fixed tech/business decisions)
7. Identifies assumptions (inferred, flagged for confirmation)
8. Identifies gaps (missing info with impact + suggested question)
9. Assigns MoSCoW priority based on input language strength
10. Reflects against evaluation.md checklist — fixes gaps and inconsistencies
11. Delivers final output with plain-text execution summary

## Input

- **Source:** direct_input, agent_output, or file_upload (.md, .txt, .pdf, .docx)
- **Required:** `idea` (string) — plain-text product idea or vision document
- **Optional:** `domain` (string, default "general"), `priority_guidance` (string)

## Output

- **Type:** `requirements`
- **Items:** Object with 5 arrays: functional_requirements[], non_functional_requirements[], constraints[], assumptions[], gaps[]
- **Each FR/NFR has:** id, title, description, priority, metadata (confidence, reasoning, citation, trajectory)
- **Summary:** Plain-text with counts, key decisions, reflection findings, gaps needing stakeholder input

## Composition

```
agents/L1-inception-requirements-extractor/
├── spec.yaml                 # Agent specification
├── evaluation.md             # Quality rubric and reflection checklist
├── output_schema.json        # JSON Schema for output validation
├── README.md                 # This file
├── examples/                 # Input/output pairs
│   ├── input-01-expense-tracker.json
│   └── output-01-expense-tracker.json
└── golden/v1.0.0/            # Benchmark responses
    ├── input-golden-01-expense-tracker.json
    ├── golden-01-expense-tracker.json
    ├── input-golden-02-insufficient.json
    └── golden-02-empty-input.json

prompts/L1-inception-requirements-extractor/
└── instructions.md           # Agent prompt
```
