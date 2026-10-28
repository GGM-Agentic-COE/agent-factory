# L0-inception-epics-creator

## Purpose
Convert one approved PRD into grounded business-altitude Jira Epics with exact source traceability.

## What does it do?
- Accepts: One approved PRD from direct input, file upload, or Confluence, plus Project and source_reference_path.
- Produces `epics` in the standard AgentOutput envelope.
- Preserves workflow lineage and exact source traceability.
- Performs a light mechanical self-check before downstream evaluation.

## How does it work?
1. Validates mandatory inputs and workflow identifiers.
2. Loads the configured standards and knowledge bases.
3. Processes only grounded source content.
4. Validates IDs, required fields, and traceability.
5. Returns the final structured AgentOutput and execution summary.

## Input
- **Source:** One approved PRD from direct input, file upload, or Confluence, plus Project and source_reference_path.
- **Required:** Valid source content and required workflow parameters.
- **Optional:** Alternate source supported by the prompt precedence rules.

## Output
- **Type:** `epics`
- **Items:** `epics` plus `gaps`.
- **Metadata:** Confidence, concise reasoning, and exact citation for primary items.
- **Summary:** Item counts, decisions, self-check outcome, KBs, guardrails, tools, and gaps.

## Composition
```text
agents/L0-inception-epics-creator/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-happy-path.json
│   ├── output-01-happy-path.json
│   ├── input-02-insufficient-context.json
│   └── output-02-insufficient-context.json
└── golden/v1.0.0/
    ├── input-golden-01-happy-path.json
    ├── golden-01-happy-path.json
    ├── input-golden-02-failure.json
    └── golden-02-failure.json
prompts/L0-inception-epics-creator/
└── instructions.md
```
