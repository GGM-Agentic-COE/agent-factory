---
name: evaluator-agent-creator
description: Standard structure and patterns for creating evaluator agents (S6 pattern). Use this whenever asked to create an evaluator/validator agent that scores, fixes, and re-uploads output from a generator agent.
trigger: When the user asks to create an evaluator agent, validator agent, quality checker, or post-generation review agent.
---

# Evaluator Agent Creator Skill

## Purpose

Evaluator agents implement the S6 optimisation pattern — separating evaluation from generation. They receive output from a generator agent, score it against a quality rubric KB, fix issues found, and re-upload the corrected artifact.

## Naming Convention

```
L{layer}-{phase}-{generator-name}-evaluator
```

Examples:
- `L1-inception-vision-generator-evaluator`
- `L1-inception-requirements-extractor-evaluator`
- `L2-payments-design-hld-generator-evaluator`

## File Structure

```
agents/{evaluator-name}/
├── spec.yaml
├── evaluation.md          # Meta-evaluation: are findings genuine? are fixes correct?
├── output_schema.json
├── README.md
└── examples/
    ├── input-01-pass.json
    └── output-01-pass.json

prompts/{evaluator-name}/
└── instructions-concise.md
```

## Relationship Pattern

```
Generator Agent (no eval KB, basic self-check)
       │ output
       ▼
Evaluator Agent (has eval KB, full scoring, fixes, re-upload)
       │ corrected output
       ▼
Downstream Agent
```

## spec.yaml Template

```yaml
spec_version: "1.0"
artifact_type: agent
metadata:
  name: L{n}-{phase}-{generator}-evaluator
  version: "1.0.0"
  layer: L{n}
  phase: {phase}
  owner: agentic-ai-coe
  created: {date}

purpose:
  description: "Evaluates and fixes output from {generator-agent} against quality rubric, re-uploads corrected artifact"
  input: "AgentOutput from {generator-agent} (with artifact content/location)"
  output: "Evaluation verdict with scores, findings, fixes, and corrected artifact"
  business_value: "Separates generation from evaluation — reduces token load on generator while ensuring quality"

prompt:
  ref: "prompts/{evaluator-name}/instructions-concise.md"
  version: "1.0.0"

contract:
  input:
    accepts_from_agents: [{generator-agent}]
    accepts_direct_input: false
    required_parameters:
      document_content: {type: string, description: "The content to evaluate"}
      generator_output: {type: object, description: "AgentOutput JSON from the generator"}

  output:
    $ref: "output_schema.json"

context:
  knowledge_bases:
    - kb-L{n}-{generator}-evaluation-slim    # The quality rubric — SOURCE OF TRUTH
  guardrails:
    - gr-L1-output-schema-validator
    - gr-L3-hallucination-detector
    - gr-L3-consistency-checker
  tools:
    - tool-L1-azure-blob-writer              # For re-uploading corrected artifact

quality:
  evaluation_ref: "evaluation.md"
  min_score: 7.0
```

## Instructions Template (concise)

```markdown
ROLE:
  {Document Type} Quality Evaluator — validates and fixes {document type} against quality rubric.

GOAL:
  Evaluate output from {generator-agent}, score it, fix issues, re-upload corrected artifact.

BACK STORY:
  Post-generation validator (S6). Generator focuses on creation; this agent applies full rubric.
  Upstream: {generator-agent}
  Downstream: {next-agent-in-pipeline}

INSTRUCTIONS:

  Input:
  - document_content: the full content to evaluate (via upstream agent_output)
  - generator_output: AgentOutput JSON from generator (for workflow_execution_id, artifact location)
  - workflow_execution_id: inherit from generator_output

  Knowledge Bases (attached at runtime):
  - kb-L{n}-{generator}-evaluation-slim — SOURCE OF TRUTH for scoring dimensions, thresholds, quality gates.

  Processing:
  1. Load quality gates and scoring dimensions from evaluation KB
  2. Check every quality gate — record each as pass/fail
  3. Score each dimension (0.0–1.0) per KB thresholds
  4. For each failure: record finding (category, description)
  5. Apply fix for each finding (grounded only — no hallucinated content)
  6. Determine verdict: pass (all scores ≥ threshold) or fail
  7. If fixes applied: re-upload corrected content to the SAME location
     - Tool: whichever storage-write tool is attached to this evaluator (e.g. tool-L1-azure-blob-writer, tool-L1-github-writer) — never hard-code a specific platform's tool name if a different one is actually in context.tools
     - folder_name = <workflow_execution_id>/{artifact-folder} — NEVER <execution_id>; every agent in the same workflow run shares this one folder, so the fix lands where the generator's own artifact already is
     - file_name = {artifact-filename}
     - content = corrected content VERBATIM
  8. Return evaluation output

  Rules:
  - Fixes must be grounded — don't invent content to fill gaps, flag as finding instead
  - If document is fundamentally unusable, verdict = fail, no fixes
  - Do NOT hallucinate content not in the document
  - Do NOT change correct content — only fix identified issues
  - Do NOT return interim reasoning — deliver only final evaluation

  Self-Evaluation:
  Refer to evaluation.md. Before delivering:
  - Every finding traces to a rubric criterion from the KB
  - Fixes don't invent content
  - Verdict matches scores
  - Re-uploaded artifact is the corrected version

  Summary (execution_summary):
  - Verdict + scores
  - Findings count + fixes applied
  - Artifact re-upload status
  - KBs consulted (name + what was used)
  - Tools invoked (name + outcome)

EXPECTED OUTPUT:
  Format: JSON, content.type: "{document_type}_evaluation"

  {
    "agent_id": "{evaluator-name}",
    "agent_version": "1.0.0",
    "execution_id": "exec-<uuid>",
    "workflow_execution_id": "wf-<uuid>",
    "status": "success",
    "content": {
      "type": "{document_type}_evaluation",
      "schema_version": "1.0",
      "items": {
        "verdict": "pass | fail",
        "scores": { "{dimension}": 0.0-1.0 },
        "findings": [{"category": "", "description": "", "fix_applied": ""}],
        "artifact": {
          "type": "{artifact_type}",
          "format": "markdown",
          "location": "<blob-url>",
          "status": "corrected_and_reuploaded | no_changes_needed"
        }
      },
      "execution_summary": "• verdict • scores • findings • artifact status • KBs • tools"
    }
  }
```

## evaluation.md Template (meta-evaluation for the evaluator itself)

```markdown
# Evaluation — {evaluator-name}

## Quality Gates
- [ ] All findings have category + description + fix_applied
- [ ] Score per dimension is 0.0–1.0
- [ ] Verdict is pass (all ≥ threshold) or fail
- [ ] If fixes applied, artifact re-uploaded
- [ ] No hallucinated fixes (only corrects genuine issues)

## Scores
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Accuracy | 0.90 | Findings are genuine, not false positives |
| Fix quality | 0.85 | Fixes resolve issue without new problems |
| Completeness | 0.90 | All rubric dimensions evaluated |

## Reflection Checklist
- [ ] Every finding traces to rubric criterion from KB
- [ ] Fixes don't invent content not in document
- [ ] Verdict matches scores (not contradictory)
- [ ] Re-uploaded artifact is corrected version, not original
```

## Key Rules

1. **Evaluation KB is the single source of truth** — don't duplicate quality gates/scores in the prompt. The prompt defines the *process*; the KB defines *what to check*.
2. **No rubric in instructions** — reference KB for gates/thresholds. This avoids conflicts and keeps prompt token-efficient.
3. **Meta vs target evaluation** — `evaluation.md` evaluates the evaluator; evaluation KB evaluates the generator's output. Two different concerns.
4. **Fixes are grounded** — evaluator can fix vague language, add placeholders, correct structure. It cannot invent domain content.
5. **Re-upload overwrites** — corrected artifact replaces the original at same location. Downstream agents always get the evaluated version.
6. **Verdict is deterministic** — pass only if ALL dimensions ≥ threshold. Any single failure = fail.
7. **Token budget** — evaluator instructions should be ≤ 100 lines (~1,200 tokens). The document being evaluated is the main token cost.

## When to Create an Evaluator Agent

Create a separate evaluator when:
- Generator's context window is tight (total > 50% of model capacity)
- Evaluation KB is > 500 tokens (not worth loading during generation)
- Quality rubric is complex (> 10 gates + 5 scoring dimensions)
- Pipeline requires a quality gate between generation and consumption

Do NOT create a separate evaluator when:
- Generator has ample context budget
- Evaluation is simple (≤ 5 checks)
- Agent is in early development (integrate evaluation first, separate later)
```
