# L1-inception-template-agent

## Purpose

A simple reference agent that generates one interesting fact about a given topic. Serves as the baseline template for building new agents — demonstrates the standard structure, prompt format, and output schema.

## What does it do?

Takes a topic as input and produces a single unique, lesser-known fact about it. The fact must be accurate, verifiable, and formatted in the AgentOutput standard.

This agent is primarily used as:
- A template for creating new agents (copy and modify)
- A test harness for validating the agent platform pipeline
- A reference implementation for prompt structure and evaluation patterns

## How does it work?

1. Receives a topic via direct input or from a prior agent's output
2. Validates the topic is non-empty and safe
3. Identifies a lesser-known fact about the topic
4. Self-assesses confidence (0.9+ for established facts, 0.7-0.9 for less certain)
5. Reflects on accuracy — verifies the fact is real, non-trivial, and on-topic
6. Delivers the fact in AgentOutput format with citation and reasoning

## Input

- **Source:** direct_input or agent_output
- **Required:** `topic` (string) — the subject to generate a fact about
- **Accepts file upload:** No

## Output

- **Type:** `fact`
- **Items:** Single item with title and description ("A unique fact is: ...")
- **Metadata:** confidence, reasoning, citation (general-knowledge), trajectory
- **Summary:** Plain-text describing what was produced

## Composition

```
L1-inception-template-agent/
├── spec.yaml                 # Agent specification
├── evaluation.md             # Quality rubric and reflection checklist
├── output_schema.json        # JSON Schema for output validation
├── examples/                 # Input/output pairs (3 cases)
│   ├── input-01-honeybees.json
│   ├── output-01-honeybees.json
│   ├── input-02-blackholes.json
│   ├── output-02-blackholes.json
│   ├── input-03-empty-topic.json
│   └── output-03-empty-topic.json
└── golden/v1.0.0/            # Benchmark responses for evaluation
    ├── golden-01-tardigrades.json
    ├── golden-02-internet.json
    └── golden-03-empty-input.json

prompts/L1-inception-template-agent/
└── instructions.md           # Agent prompt (Role/Goal/BackStory/Instructions/Output)
```
