# L1-inception-epics-generator-agent

## Purpose

Converts structured requirements into delivery-ready epics and features. Groups requirements by capability, assigns priorities and dependencies, and produces plannable units that delivery teams can schedule into feature cycles.

## What does it do?

Takes structured requirements (from the requirements extractor) and produces:
- **Epics** — large capability areas (3-8 features each, deliverable in 2-4 feature cycles)
- **Features** — independently deliverable units within each epic
- **Traceability** — every feature links back to the FRs it implements
- **Dependencies** — which epics must be delivered before others
- **Cross-cutting concerns** — NFRs, constraints, and risks mapped to affected epics

The agent groups requirements by capability cohesion, ensuring each epic represents a logical delivery unit that a team can plan and execute.

## How does it work?

1. Ingests structured requirements (from requirements extractor or direct input)
2. Validates at least one functional requirement exists
3. Analyses FRs and identifies logical capability groupings
4. Creates one epic per group with title, description, priority, size estimate
5. Decomposes each epic into features (each implementing 1-3 FRs)
6. Assigns NFRs as cross-cutting concerns to relevant epics
7. Maps constraints as technical notes, assumptions as risks
8. Identifies inter-epic dependencies (minimises for parallel delivery)
9. Reflects against evaluation.md — verifies 100% FR coverage, right-sizing, dependency correctness
10. Delivers final output with plain-text execution summary

## Input

- **Source:** agent_output (from L1-inception-requirements-extractor-agent) or direct_input
- **Required:** `requirements` (object) — structured requirements with functional_requirements[], non_functional_requirements[], constraints[]
- **Optional:** `max_epics` (integer, default 10), `grouping_strategy` (string: capability|user_journey|domain_area)

## Output

- **Type:** `epics`
- **Items:** Array of epics, each with: id, title, description, priority, size, estimated_cycles, requirements_covered[], features[], depends_on[], nfrs_applicable[], metadata
- **Features have:** id, title, description, implements[], supports[], acceptance_summary, estimated_effort
- **Summary:** Plain-text with epic/feature counts, coverage, grouping decisions, reflection changes, dependencies

## Composition

```
L1-inception-epics-generator/
├── spec.yaml                 # Agent specification
├── evaluation.md             # Quality rubric and reflection checklist
├── output_schema.json        # JSON Schema for output validation
├── examples/                 # Input/output pairs
│   ├── input-01-expense-tracker.json
│   └── output-01-expense-tracker.json
└── golden/v1.0.0/            # Benchmark responses
    ├── golden-01-expense-tracker.json
    └── golden-02-empty-input.json

prompts/L1-inception-epics-generator-agent/
└── instructions.md           # Agent prompt
```
