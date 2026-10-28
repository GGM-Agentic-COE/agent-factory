# L1-inception-stories-generator-agent

## Purpose

Decomposes epics and features into implementable user stories ordered for incremental delivery. Stories are sequenced from foundational setup through simple features to complex enhancements, enabling teams to deliver sprint after sprint with each increment production-deployable.

## What does it do?

Takes epics with features (from the epics generator) and produces:

- **User stories** in "As a / I want / So that" format with short descriptive titles
- **Acceptance criteria** in Given/When/Then (3-5 per story, testable by QA)
- **Story points** (1, 2, 3, 5, 8 — each story should fit within one sprint)
- **Data sensitivity** classified per story (Public, Internal, Confidential, Restricted)
- **Dependencies** between stories (acyclic, enabling parallel work where possible)
- **Regulatory linkage** where stories implement regulatory requirements
- **Coverage matrix** mapping features → stories → total points for traceability
- **Enterprise architecture adherence** — stories respect EA technology constraints and patterns

Stories are grouped by parent epic and ordered for incremental delivery so teams can start immediately with foundation stories and build up complexity.

## How does it work?

1. Ingests epics with features (from L1-inception-epics-generator-agent or direct input)
2. Validates at least one epic with features exists
3. For each feature, decomposes into stories covering the full implementation scope
4. Assigns story points based on complexity
5. Tags data sensitivity and regulatory linkage per story
6. Maps dependencies (no circular refs, foundation stories independent within feature)
7. Builds coverage matrix (feature → stories → total effort)
8. Validates against enterprise architecture KB — stories must not contradict EA mandates
9. Reflects against evaluation.md checklist — fixes gaps and inconsistencies
10. Delivers final output with execution summary

## Input

- **Source:** agent_output (from L1-inception-epics-generator-agent) or direct_input
- **Required:** `epics` (array) — epics with features including feature_id, description, requirements_covered
- **Optional:** `target_feature` (string — generate for one feature only), `cycle_duration_days` (integer, default 5)
- **Knowledge bases:** kb-L1-enterprise-architecture (or client-specific EA KB), kb-L1-story-best-practices

## Output

- **Type:** `stories`
- **Structure:** `items` is an object with:
  - `total_stories` — count of all stories
  - `total_story_points` — sum of all points
  - `epics[]` — stories grouped by parent epic, each with:
    - `epic_id`, `epic_title`
    - `stories[]` — array of story objects
    - `coverage_matrix[]` — feature → stories → points mapping
- **Each story has:** story_id (US-XXX), feature_id (F-XX.X), title, user_story, acceptance_criteria[], story_points, data_sensitivity, change_type, regulatory_linkage, depends_on[], metadata (confidence, reasoning, citation, trajectory)
- **Summary:** Plain-text execution_summary with counts, dependency chain, sequencing decisions, reflection findings

## Composition

```
L1-inception-stories-generator/
├── spec.yaml                 # Agent specification
├── evaluation.md             # Quality rubric and reflection checklist
├── output_schema.json        # JSON Schema for output validation
├── README.md                 # This file
├── examples/
│   └── output-01.json        # Full output example (61 stories)
└── golden/v1.0.0/
    ├── input-golden-01-auth.json      # Auth epic input
    ├── golden-01-auth.json            # 6 stories with full traceability
    ├── input-golden-02-empty.json     # Empty input
    └── golden-02-empty.json           # INSUFFICIENT_CONTEXT handling

prompts/L1-inception-stories-generator-agent/
└── instructions.md           # Agent prompt (Role/Goal/BackStory/Instructions/Output)
```
