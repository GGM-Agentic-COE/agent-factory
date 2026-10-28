# L1-inception-vision-generator

## Purpose

Converts a product idea into a comprehensive, industry-grade vision document by grounding content in a domain knowledge base. The generated document is uploaded as a markdown artifact to Azure Blob Storage and the agent returns a standard AgentOutput with artifact location and document summary.

## What does it do?

- Accepts a product idea (text) and domain knowledge base (attached at runtime)
- Generates a 5-section vision document following the template in `kb-L1-vision-document-template`:
  1. Executive Summary (3–5 sentences)
  2. Business Context (problem, drivers, target users, constraints, success metrics)
  3. Full Scope Vision (vision statement, feature areas, integrations, user journeys, scalability, roadmap)
  4. MVP Scope (objective, success criteria, in/out scope features, MVP journeys, constraints/assumptions, DoD)
  5. Risks and Dependencies (key risks with likelihood/impact/mitigation, external dependencies, open questions)
- Grounds all content in the domain KB (user roles, regulations, terminology, business rules, integrations)
- Uploads the final markdown to Azure Blob Storage at `/<workflow_execution_id>/vision-doc/vision-<product-name>.md`
- Returns AgentOutput with artifact location, document summary counts, and grounding metadata

## How does it work?

1. Ingest the idea and validate it has ≥ 10 words and a discernible product concept
2. Derive product name if not provided
3. Query domain KB for: target user roles, business rules, regulations, terminology, existing systems, pain points
4. Generate the vision document following `kb-L1-vision-document-template` structure
5. Ground every feature area, user type, constraint, and risk in domain KB content
6. Separate full vision from MVP scope with explicit in/out boundaries and deferral rationale
7. Reflect against `kb-L1-inception-vision-generator-evaluation` criteria (specificity, grounding, no vague language)
8. Upload the final markdown to Azure Blob Storage via `tool-L1-azure-blob-upload`
9. Return AgentOutput with artifact location, document summary, and grounding coverage

## Input

- **Source:** direct_input or agent_output
- **Required:** `idea` — text description of the product idea (≥ 10 words)
- **Optional:** `product_name` — preferred name (agent derives one if not provided)
- **Optional:** `target_market` — market segment hint
- **Optional:** `constraints` — known business constraints or boundaries

## Output

- **Type:** `vision_document`
- **Status:** `success` or `failed` (INSUFFICIENT_CONTEXT if idea is too vague or domain KB is missing)
- **Items (object):**
  - `product_name` — derived or provided product name
  - `document_summary` — section/feature/risk/question counts + executive summary text
  - `artifact` — blob storage location (URL, container, blob_path, filename)
  - `metadata` — domain_kb_used, confidence score, grounding_coverage proportion
- **Summary:** Plain-text bullet points covering what was produced, section counts, KB used, reflection fixes, and upload location

## Composition

```
agents/L1-inception-vision-generator/
├── spec.yaml                                    # Agent specification
├── evaluation.md                                # Quality rubric and reflection checklist
├── output_schema.json                           # JSON Schema for output validation
├── kb-L1-vision-document-template.md            # Markdown template structure (attached as KB)
├── kb-L1-vision-document-template.pdf           # PDF version of template
├── kb-L1-inception-vision-generator-evaluation.pdf  # Evaluation criteria (attached as KB)
├── README.md
├── examples/
│   ├── example-vision-tenanthub-fullstack.md    # Full example vision document (fullstack app)
│   └── example-vision-bookingengine-api.md      # Full example vision document (API service)
└── golden/v1.0.0/
    ├── input-golden-01-fullstack-childcare.json
    ├── golden-01-fullstack-childcare.json
    ├── input-golden-02-api-payments.json
    ├── golden-02-api-payments.json
    ├── input-golden-03-insufficient-context.json
    └── golden-03-insufficient-context.json

prompts/L1-inception-vision-generator/
└── instructions.md
```

## Knowledge Bases

| KB | Purpose |
|----|---------|
| `kb-L2-*` (domain KB) | Provides domain context — users, regulations, business rules, terminology, integrations |
| `kb-L1-vision-document-template` | Structural template defining all sections and subsections |
| `kb-L1-inception-vision-generator-evaluation` | Evaluation rubric and reflection checklist |

## Tools Used

- `tool-L1-azure-blob-upload` — uploads the generated markdown to Azure Blob Storage

## Downstream

The vision document feeds into:
- `L1-inception-requirements-extractor` — extracts FRs, NFRs, constraints from the vision doc
- Human review for stakeholder alignment
