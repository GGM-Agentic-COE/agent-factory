# Evaluation — L0-impact-assessor

## Quality Gates

Evaluate the final, post-fix artifact against the original inputs, not the assessor’s account of them. Read `content.items.impact_assessment`, `content.items.dependency_graph` and `content.artifacts[0].content` from the assessor’s `impact_assesment` payload. A documented limit on what can be verified is not a failed gate; presenting an unverified claim as fact is.

- [ ] **Input sufficiency.** Accept a successful `prd_output` or a readable standalone PRD with identifiable requirements. If neither exists, verify `status: failed`, `INSUFFICIENT_CONTEXT` and no artifact. If the generator payload itself is absent, use the evaluator’s failure path. Do not score or forward a nonexistent assessment. A PRD and target architecture suffice to assess planned application impact; missing inventory alone must not trigger this failure. If target design is absent, requirement-derived components must be labelled as candidates.
- [ ] **Requirements and impact.** Every source FR appears in `components_identified` and in at least one component node’s `source_requirement`. Each rating identifies the failure, affected journey or obligation, and any supported fallback: High for a cross-application cascade or breached obligation; Medium for a contained journey/domain; Low for no operational effect. Check release scope, NFR values, data handling, regulatory constraints and open decisions against their respective sources; sample policy is not approved policy.
- [ ] **Capability check.** Independently compare every supplied in-scope service against the proposed capabilities. Verify the closest match and why it does or does not overlap. If the check cannot be run, require “Not assessed” with the reason. With partial coverage, “none found” applies only to the checked scope.
- [ ] **Technical impact.** Independently check each relevant CI. A modified application CI reuses its component node; a partner reuses its external node. An unchanged but used partner retains its integration edges. Only an evidenced exclusion with no dependency is an isolated `existing-ci`. An interface relationship alone is not proof of modification. No invented CIs or duplicate nodes across roles.
- [ ] **Assessment basis.** Verify the declared application boundary and the matching evidence rule below. If multiple scenarios are presented, keep their findings separate and identify the baseline of the single structured graph.
  - **Confirmed greenfield:** an identified owner or source confirms a new application. In-scope planned builds may be new; shared platforms and external partners are assessed separately.
  - **Assumed greenfield:** the scenario was explicitly requested. Label its builds and counts as conditional, identify who should confirm (or TBD), and state which findings would change.
  - **Change to existing application:** compare the target with an as-built inventory or attributed team baseline. Distinguish modified, reused unchanged and explicitly new components; identify which facts are owner-stated rather than independently verified.
  - **Current state unknown:** assess planned responsibilities, dependencies and failures. Unless supported for an individual component, use JSON `null` for undetermined `component_type`; use `null` for unknown `existing_systems_impacted` or `existing_systems_excluded`. Report known partial findings separately. Zero means a checked zero within the stated scope. Empty exports establish neither greenfield nor absence of a parent enterprise.
- [ ] **Source authority and coverage.** The PRD supports requirements, the target supports planned design, current-state evidence supports deployment, and applicable standards support mandates—not availability. Trace standards-only dependency nodes to a specific mandate and the components they gate. Flag material contradictions, stale or post-change exports, and unknown freshness; apply only supplied freshness thresholds. Do not substitute target approval for deployment evidence or force unknowns into a schema that rejects `null`.
- [ ] **Edge semantics.** Verify each edge’s evidence, type and endpoints: `blocks` external prerequisite → component; `depends-on` prerequisite → dependent; `integrates-with` producer → consumer. Do not turn a nonblocking integration into a build prerequisite.
- [ ] **Cycle check.** Independently run depth-first traversal over all directed edges, including disconnected subgraphs. Compare `cycle_check`, verify reported cycles close on actual edges, and accept equivalent traversal orders. On FAIL require `critical_path.nodes = []` and a blocked rationale. Correct a reversed edge only when source evidence establishes its direction. Never drop an edge for acyclicity; an unresolved cycle blocks backlog approval even when correctly reported.
- [ ] **Critical path.** On PASS, independently compute longest paths on `blocks` and `depends-on` edges only; length is edge count. Verify the unique chain in `critical_path.nodes`, or, for ties, `nodes = []` with every tied chain and their common length in `rationale`. No gating edges means no gating chain and length 0.
- [ ] **Mermaid equivalence.** Compare individual nodes and edges with the JSON graph: IDs, counts, quoted labels, shapes, classes, directions and styles. An undetermined component is a rectangle labelled “build/reuse TBD” exactly once, with no new/existing styling. Verify cycle highlighting and one `%% CYCLE` comment per reported cycle on FAIL; on PASS, one `%% CRITICAL PATH` comment per longest gating chain when one exists.
- [ ] **Identity and counts.** Graph node IDs are unique kebab-case; all edge endpoints resolve. Aggregate FR references on one node per distinct component. Count distinct dependencies and components, not requirement rows. Never invent FR, CI or service identifiers.
- [ ] **Distillation.** `executive_summary` ≤ 20 words; each `rationale_summary` ≤ 15 words. The full Markdown belongs in `artifacts[0].content`, not in summary fields.
- [ ] **Executive synthesis.** Every executive claim, including overall impact, component counts, exclusions, overlaps and limitations, traces to a finding below it. Distinguish verified counts from scenario counts and unknown totals.

## Scores (≥ threshold to pass)

| Evaluator | Threshold | Checks |
|-----------|-----------|--------|
| Faithfulness | ≥ 0.90 | Material findings agree with the appropriate source and its scope. Neither planned design nor an assumed scenario is reported as deployed fact. |
| Hallucination | ≤ 0.10 | Measure unsupported factual claims, not disclosed unknowns. Check invented IDs, integrations, mandates, live status and zero-impact claims. Lower is better. |
| Consistency | ≥ 0.90 | Structured items, artifact, recomputed graph and Mermaid agree, including counts, nulls, dispositions and ties. |
| Relevance | ≥ 0.85 | Findings cover the application change. The graph identifies usable prerequisites or explains why a verified cycle blocks sequencing. |
| Reasoning quality | ≥ 0.80 | Failure effects, dependency direction, overlap, exclusions and baseline-sensitive conclusions have evidence-based explanations. |
| Citation completeness | ≥ 0.95 | Findings cite the applicable requirement, target section, CI/service ID, baseline declaration or policy reference. For an evidence gap, cite the missing input or unchecked scope; never fabricate an ID. |

Score only an evaluable artifact. Record the evidence for each score. Where no scoring implementation is configured, use the fraction of applicable checks satisfied for each dimension (unsupported claims ÷ factual claims for hallucination); record the numerator and denominator. For `overall_score` on the 0–10 scale, use 10 times the mean of the six scores with hallucination expressed as `1 − hallucination`. The aggregate does not override an individual threshold or a failed mandatory gate. A correctly documented unknown satisfies the evidence-handling check; it earns no credit for a verification that was not performed.

## Reflection Checklist

- [ ] All assessor template sections are present in an evaluable artifact. No unresolved template tokens; a sourced gap marked TBD or “Not assessed” is valid. The selected baseline and its limitations are visible.
- [ ] No summary contains the full artifact. Findings cite evidence; each fix records the reason, before and after. Corrected structured values are recoverable from the evaluator’s findings.
- [ ] FR coverage, node uniqueness, endpoint validity, traversal results, tied paths and Mermaid equivalence were rechecked after the last fix.
- [ ] `artifacts[0].content` is the complete evaluated Markdown, verbatim if unchanged. For every available artifact—including an escalated draft—verify the Confluence write and record only its literal returned URL in `storage.location` and `execution_summary`. If the write fails or returns no URL, retain the text inline, omit the location, report failure and withhold approval. If there is no document, skip the write and return `artifacts: []`.

## Reflection Process

1. **Load** the original inputs and assessor output; establish whether there is an evaluable artifact and identify its baseline.
2. **Check** the applicable gates independently. Record specific evidence, missing inputs and reproducible graph results.
3. **Fix and recheck** only mechanically supported errors across Markdown, structured items and Mermaid. Record fixes; escalate material ambiguities, unresolved cycles or contract failures.
4. **Persist and decide.** Return only the evaluator’s final `evaluation_result` envelope. Use `approved` if unchanged or `fixed_and_approved` if corrected only after all applicable gates, score thresholds and persistence checks pass. Otherwise withhold approval; use `escalate_to_hitl` for unresolved findings. Never forward a failed, escalated or no-document run to the backlog.
