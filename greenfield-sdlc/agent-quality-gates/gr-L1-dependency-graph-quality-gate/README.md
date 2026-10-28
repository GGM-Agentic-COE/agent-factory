# gr-L1-dependency-graph-quality-gate

**Layer:** L1
**Triggers on:** post_execution (output rail) — fires when `L1-planning-dependency-mapper-evaluator` concludes
**On fail:** Retry once, then escalate to HITL
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid mode (recommended)
**Applies to:** `L1-planning-dependency-mapper-evaluator` only (`configured_agents`)

## What does it do?

`L1-planning-dependency-mapper-evaluator` independently scores
`L1-planning-dependency-mapper`'s draft dependency graph against
`L1-planning-dependency-mapper/evaluation.md` and fixes what it can. This
guardrail fires at that point but validates a different thing: the
**resultant** `L1-planning-dependency-mapper` output — its own `items`, with
the evaluator's `fixes_applied` resolved in — is what actually flows to
`L1-planning-backlog-prioritizer` (as literal topological-sort input) and
Phase 4's `L1-design-hld`. This gate checks THAT content.

Unlike the other three quality gates in this batch, most of what this gate
checks is **not** a schema/regex check. `cycle_check` and `critical_path`
are claims about a graph traversal — a schema validator cannot tell a
correct traversal result from a wrong one, and neither can eyeballing the
graph. So this guardrail's core job is to **independently re-run the exact
same traversal** (DFS cycle detection, longest-path computation) in Python
against the resultant nodes/edges, and compare the result against what the
resultant content claims — never trusting either the generator's own
`cycle_check`/`critical_path` fields, or the evaluator's own (scored,
self-reported) re-derivation, at face value.

This is exactly the class of bug
`L1-planning-dependency-mapper-evaluator/golden/v1.0.0/golden-02-edge-direction-bug.json`
exists to demonstrate: a reversed `depends-on` edge that is schema-valid,
does not happen to create a cycle in that particular graph, and still
produces a `critical_path` that inverts the real build order.
`phase-1/README.md` documents the same class of bug shipping in an earlier
revision of the framework's own worked example. This guardrail is the
independent, mechanical check that catches it regardless of what either
agent in the pair concluded.

1. **Output schema validation** — does the resultant content conform to
   `L1-planning-dependency-mapper/output_schema.json` (not the evaluator's
   own output shape)?
2. **Rubric adherence (independent re-derivation)** — does the resultant
   content's `cycle_check` and `critical_path` actually match what a real
   DFS / longest-path traversal over the resultant nodes/edges produces? Is
   a real cycle escalated to overall status `"failed"`? Does FR coverage
   hold by set equality against `prd.md`?

This is NOT a re-score of the evaluator's own
faithfulness/hallucination/consistency judgment, and NOT a check on the
evaluator's own `scores`/`pass`/`final_decision` bookkeeping — it is an
independent re-derivation of graph correctness, run against what actually
ships downstream.

**Why it matters:** a `fixed_and_approved` verdict is a claim, not a proof.
If a "fix" corrected one reversed edge but the recomputed `critical_path`
still doesn't match, or a genuine tie exists that the fix's rationale never
mentions, that is exactly the defect this gate exists to catch — independent
of what either agent's own bookkeeping says. A cyclic graph silently shipped
downstream is not a quality nuance; it is a build-blocking defect that only
surfaces two phases later, in `L1-design-hld`, when it is far more expensive
to unwind.

### Rules

| # | Rule | Category | Action | Severity |
|---|------|----------|--------|----------|
| 1 | schema-compliance | Output schema validation | block | critical |
| 2 | edge-endpoints-valid | Output schema validation | block | critical |
| 3 | independent-cycle-recheck | Rubric adherence | block | critical |
| 4 | cycle-status-escalation-check | Rubric adherence | block | critical |
| 5 | independent-longest-path-recheck | Rubric adherence | block | critical |
| 6 | fr-coverage-recheck | Rubric adherence | block | high |
| 7 | critical-path-rationale-quality | Rubric adherence | flag | medium |

## How It Works

```
L1-planning-dependency-mapper-evaluator concludes
        ↓
┌────────────────────────────────────────────────────────────────────────┐
│  DEPENDENCY GRAPH QUALITY GATE (post_execution, fires on evaluator)    │
│                                                                          │
│  Reconstruct RESULTANT content: nodes/edges/cycle_check/critical_path   │
│  with fixes_applied[].before→after resolved in (structural edge and    │
│  critical_path.nodes/rationale patterns, plus generic string fallback) │
│                                                                          │
│  DETERMINISTIC (actions.py):                                            │
│  1. Schema: required fields, node id/type/label, edge from/to/type,     │
│     kebab-case unique node ids?                                        │
│  2. Every edge's from/to references a real node id (no dangling edge)?  │
│  3. INDEPENDENT DFS CYCLE RECHECK — trace recursion-stack back-edge      │
│     detection over EVERY node/edge; does it match the resultant         │
│     cycle_check.status/cycles_found?              <-- MOST IMPORTANT   │
│  4. If a real cycle was found, is overall status "failed"?             │
│  5. INDEPENDENT LONGEST-PATH RECHECK (only if cycle recheck is PASS) —  │
│     trace the actual longest walk over depends-on/blocks edges only     │
│     from every root; does the resultant critical_path.nodes match one   │
│     of the (possibly tied) longest chains, and does the rationale name  │
│     every other tied chain if a genuine tie exists?                     │
│  6. FR coverage: does the SET of FR ids across every node's             │
│     source_requirement[] equal the full FR set in prd.md, exactly?      │
│                                                                          │
│  Any ✗ → BLOCK, retry once, then escalate_to_hitl                        │
│                                                                          │
│  SEMANTIC (self_check_output, LLM):                                     │
│  7. Does critical_path.rationale genuinely state the path length and    │
│     any tie in readable prose, not just repeat the node id list?        │
│                                                                          │
│  Any ✗ → BLOCK, retry once, then escalate_to_hitl                        │
│                                                                          │
│  All ✓ → gate passes                                                    │
└────────────────────────────────────────────────────────────────────────┘
        ↓
Resultant dependency graph flows to backlog-prioritizer / design-hld
```

## File Structure

```
gr-L1-dependency-graph-quality-gate/
├── config.yml                                # Rail configuration
├── prompts.yml                               # LLM evaluation prompt (7 checks, LLM traces DFS/longest-path itself in LLM-only mode)
├── gr-L1-dependency-graph-quality-gate.co    # LLM-only Colang flow
├── dependency_graph_quality_gate.co          # Python-hybrid Colang flow (calls actions.py)
├── actions.py                                # Deterministic Python (schema, edge endpoints, independent DFS cycle recheck, cycle-status escalation, independent longest-path recheck, FR coverage)
├── spec.yaml                                 # Guardrail specification
└── README.md                                 # This file
```

**Two modes:**
- **LLM-only** (`gr-L1-dependency-graph-quality-gate.co`): all 7 checks via
  `self_check_output` — the LLM is instructed to trace the DFS and
  longest-path computation itself, step by step. Weaker for this particular
  guardrail than the hybrid mode, because a graph traversal is exactly the
  kind of deterministic computation an LLM can get wrong under load; kept
  for parity with the other guardrails and for environments without a
  Python action runtime.
- **Python-hybrid** (`dependency_graph_quality_gate.co`, recommended): the 6
  deterministic checks (1-6) reconstruct the resultant content and run an
  *actual* DFS and *actual* longest-path computation directly in
  `actions.py`; the LLM handles only the genuinely semantic check (7) — the
  mechanical part of the tie-check ("does the rationale text contain every
  tied chain's node ids") is already covered deterministically inside
  `independent-longest-path-recheck`, so the LLM's job is only judging
  whether the prose itself reads as a genuine explanation.

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

**Valid resultant output (expected: "yes")** — a clean, acyclic, 3-node
graph with a correctly-computed cycle_check and critical_path:

```json
{
  "product_name": "Internal Expense Reimbursement Tool",
  "source_artifacts": { "impact_assessment": "artifact-1", "prd": "artifact-2" },
  "nodes": [
    { "id": "sso-provider", "type": "external-dependency", "label": "SSO Provider" },
    { "id": "claim-service", "type": "component", "label": "Claim Service", "source_requirement": ["FR-001"] },
    { "id": "dashboard-service", "type": "component", "label": "Dashboard Service", "source_requirement": ["FR-002"] }
  ],
  "edges": [
    { "from": "sso-provider", "to": "claim-service", "type": "blocks" },
    { "from": "claim-service", "to": "dashboard-service", "type": "depends-on" }
  ],
  "cycle_check": { "status": "PASS", "cycles_found": [] },
  "critical_path": { "nodes": ["sso-provider", "claim-service", "dashboard-service"], "rationale": "Longest blocking chain is 2 edges: sso-provider -> claim-service -> dashboard-service. No tie." },
  "generated": "2026-08-09", "execution_id": "exec-1", "workflow_execution_id": "wf-1"
}
```

**Invalid resultant output (expected: "no")** — claims `cycle_check: PASS`
but a real cycle exists (an added edge back to `sso-provider`):

```json
{
  "...": "same as above but with an added edge",
  "edges": [
    { "from": "sso-provider", "to": "claim-service", "type": "blocks" },
    { "from": "claim-service", "to": "dashboard-service", "type": "depends-on" },
    { "from": "dashboard-service", "to": "sso-provider", "type": "depends-on" }
  ],
  "cycle_check": { "status": "PASS", "cycles_found": [] }
}
```

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Clean acyclic resultant graph | None | "yes" |
| Claimed PASS, real cycle exists | Added edge closes a cycle, cycle_check left at PASS | "no" |
| Real cycle but status "success" | Cycle present, cycle_check correctly FAIL, but overall status not escalated | "no" |
| critical_path shorter than true longest path | critical_path.nodes truncated to fewer hops than the real longest chain | "no" |
| Genuine tie, only one chain reported | Two roots tie at the same max length; rationale/nodes name only one | "no" |
| Dangling edge | An edge's `to` references a node id not in nodes[] | "no" |
| FR coverage gap | An FR in prd.md not covered by any node's source_requirement | "no" |
| Reversed depends-on edge (golden-02 class) | from/to swapped on a depends-on edge, no cycle results, critical_path built on the wrong order | "no" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L1-dependency-graph-quality-gate")
rails = LLMRails(config)

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<clean resultant dependency-graph JSON>"}]
)
assert "blocked" not in response["content"].lower()
print("Clean resultant graph passed")

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<graph claiming PASS with a real cycle>"}]
)
assert "blocked" in response["content"].lower()
print("Undetected cycle blocked")
```

### Option 3: Python Unit Testing (standalone actions.py)

```python
import asyncio, json
from actions import check_dependency_graph_quality_gate

generator_output = json.dumps({
    "status": "success",
    "content": {"items": {
        "product_name": "P", "source_artifacts": {"impact_assessment": "a", "prd": "b"},
        "nodes": [
            {"id": "a", "type": "component", "label": "A", "source_requirement": ["FR-001"]},
            {"id": "b", "type": "component", "label": "B", "source_requirement": ["FR-002"]},
        ],
        "edges": [
            {"from": "a", "to": "b", "type": "depends-on"},
            {"from": "b", "to": "a", "type": "depends-on"},   # closes a real cycle
        ],
        "cycle_check": {"status": "PASS", "cycles_found": []},   # falsely claims PASS
        "critical_path": {"nodes": [], "rationale": "n/a"},
        "generated": "2026-08-09", "execution_id": "e", "workflow_execution_id": "w",
    }},
})

result = asyncio.run(check_dependency_graph_quality_gate(output="{}", generator_output=generator_output))
assert result is True  # independent-cycle-recheck catches the undetected cycle
```

See the accompanying standalone test suite (run during this guardrail's
build) for the full set of five scenarios: clean pass, undetected cycle,
un-escalated real cycle, understated critical_path length, and an unreported
genuine tie.
