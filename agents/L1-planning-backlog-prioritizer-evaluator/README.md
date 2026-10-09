# L1-planning-backlog-prioritizer-evaluator

## Purpose

The generator's own self-check is a light, mechanical pass — complete? no placeholders? IDs valid? It never re-derives its own math or independently confirms a duplicate-ticket claim. This agent is the paired evaluator (S6 pattern): it takes the SAME source data the generator received and independently recomputes every score, re-walks the dependency graph, re-verifies duplicate flags, and fixes what's wrong — in both the structured items and the `prioritized-backlog.md` document itself when the document is wrong.

## What does it do?

Accepts:
- `generator_output` — the full AgentOutput from L1-planning-backlog-prioritizer
- The same `features`, `dependency_graph`, and `value_scoring_inputs` the generator was given

Produces:
- `verification_results[]` — one independently-recomputed entry per feature, comparing the generator's claim against this agent's own derivation
- `fixes_applied[]` — any correction made, and whether it also required correcting the document
- `guardrail_rechecks[]` — independent re-verification of the generator's own guardrail claims (never trusted at face value)
- `verdict` — `approved` / `fixed_and_approved` / `rejected`, with faithfulness/hallucination/consistency/citation scores
- A re-uploaded `prioritized-backlog.md` at the SAME artifact id and location, only if a fix touched the document

## How does it work?

1. Retrieve the generator's items AND the full document from `generator_output.content.artifacts[0].storage.location` — items' distilled summaries aren't enough for full-content scoring.
2. Independently recompute each feature's priority_score (WSJF/RICE) and dependency_unblocking_score from the original source data — never read the generator's numbers as ground truth.
3. Check every blocks/blocked_by pair: a feature ranked above its own blocker with no documented trade-off is a blocker-severity finding.
4. Re-verify any duplicate_flag via an independent `tool-L1-jira-fetch-issue` call, not by trusting the generator's stored flag.
5. Re-run each guardrail the generator claims to have passed, independently.
6. For every mismatch, record a fix; if the mismatched field also appears in the document, correct it there too and re-upload to the same location/id.
7. Compute the verdict and report it — `rejected` only when a blocker-severity issue can't be confidently fixed (e.g. contradictory source data).

## Input

- **Source:** agent output (`generator_output`) + direct input (the generator's original `features`, `dependency_graph`, `value_scoring_inputs`)
- **Required:** all four of the above — recomputation is impossible without the original source data, not just the generator's claims
- **Optional:** `adjacent_backlog_check` — re-verify duplicate_flag claims via Jira

## Output

- **Type:** `backlog_evaluation`
- **Items:** `verification_results[]`, `fixes_applied[]`, `guardrail_rechecks[]`
- **Verdict:** `final_decision` plus faithfulness/hallucination/consistency/citation scores
- **Artifact:** re-uploaded `prioritized-backlog.md` (same id/location as the generator's), only if a fix touched the document
- **Summary:** plain-text execution_summary covering what was verified, findings, guardrail rechecks, tools invoked, and the final verdict

## Composition

```
agents/L1-planning-backlog-prioritizer-evaluator/
├── spec.yaml
├── evaluation.md          # this agent's OWN meta-quality bar — NOT the generator's rubric
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-happy-path.json
│   ├── output-01-happy-path.json
│   ├── input-02-edge-case.json
│   └── output-02-edge-case.json
└── golden/v1.0.0/
    ├── input-golden-01-happy-path.json
    ├── golden-01-happy-path.json
    ├── input-golden-02-edge-case.json
    └── golden-02-edge-case.json

prompts/L1-planning-backlog-prioritizer-evaluator/
└── instructions.md
```

Wired against: `agents/L1-planning-backlog-prioritizer/evaluation.md` (referenced as `context.knowledge_bases[0].ref`, the scoring source of truth this agent applies — never duplicated into its own prompt).
