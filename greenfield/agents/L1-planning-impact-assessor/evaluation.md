# Evaluation — L1-planning-impact-assessor

This is the generator's own basic self-check only. Deep, independent re-derivation is delegated
downstream to ONE single evaluator agent (not part of this pack):
- an impact-assessment evaluator, which re-checks the catalog/CMDB findings against
  L1-impact-assessment.md, and independently re-derives the cycle_check/critical_path from the
  JSON graph items.

## Quality Gates

### Phase A — Impact Assessment
- [ ] Phase A ran to completion (or a valid INSUFFICIENT_CONTEXT) before Phase B started
- [ ] Every FR-NNN in prd_output appears in Components Identified — no FR left unmapped
- [ ] Every service_catalog entry and every relevant cmdb_export CI was checked, not skipped
- [ ] No CMDB/KB mismatch was silently reconciled instead of flagged
- [ ] Export freshness validated: export_metadata.exported_at checked against run date;
      stale export flagged as data-quality risk in Gaps
- [ ] Export contamination checked: exports represent the estate BEFORE this assessment;
      no proposed component appears in either export
- [ ] Empty enterprise fallback: if both service_catalog and cmdb_export are empty, "no parent
      enterprise" is explicitly stated in the assessment header and KB-authority mode is activated
- [ ] KB-mandatory infrastructure (IdP, API Gateway, observability stack, secrets manager) surfaced
      as external-dependency nodes when both exports are empty (KB-authority mode)
- [ ] Every KB guardrail violation flagged in Gaps (not silently ignored)
- [ ] All 7 document sections populated: Executive Summary & Overview, Non-Functional & Regulatory
      Impact, Existing-System Impact, Components Identified, Data Model & Schema Impact,
      Integration Landscape & External Dependencies, Assumptions & Out of Scope
- [ ] Executive Summary & Overview populated LAST — synthesis of steps 1-3 only; no new impact
      claim first appears there
- [ ] `executive_summary` in JSON output ≤ 20 words (distillation only); `rationale_summary` ≤ 15 words

### Phase B — Dependency Graph
- [ ] Phase B nodes/edges trace 1:1 to Phase A's own Components Identified / External
      Dependencies — no node invented, none dropped
- [ ] One node per Components Identified row (type "component"), one node per Integration Landscape
      entry (type "external-dependency"), one node per not-impacted CI row (type "existing-ci",
      isolated — no edges)
- [ ] Impacted CI rows share the same node as the component from step 6 (no duplicate node)
- [ ] Edge direction uniform: "blocks" from=dependency to=component; "depends-on"
      from=prerequisite to=dependent; "integrates-with" from=producer to=consumer — never mixed
- [ ] cycle_check.status is the output of an actual DFS trace (rationale names the traversal, not
      just "no cycles found")
- [ ] FAIL → critical_path.nodes = [], rationale = blocked pending cycle resolution; no edge
      dropped to "fix" the cycle
- [ ] PASS → critical_path from actual longest-path computation over depends-on/blocks edges only;
      genuine ties are ALL reported, none arbitrarily dropped
- [ ] Every FR-NNN in prd_output appears in some node's source_requirement[] (Phase A ↔ Phase B
      cross-check, step 12)
- [ ] All node IDs unique, kebab-case (^[a-z0-9-]+$)

### Mermaid Graph
- [ ] The embedded mermaid graph in L1-impact-assessment.md matches the JSON graph items
      node-for-node, edge-for-edge, including cycle annotations when FAIL
- [ ] Node shapes correct per type: component → rectangle `[]`, existing-ci → subroutine `[[]]`,
      external-dependency → stadium `([])`
- [ ] Node labels containing special characters (like parentheses) are properly enclosed in
      double quotes (e.g., `id(["Label (Extra Info)"])`)
- [ ] Edge styles correct per type: "blocks"/"depends-on" → solid arrow `-->`, "integrates-with"
      → dashed arrow `-.->` 
- [ ] classDef and class assignments present: newNode, existingNode, unaffectedNode
- [ ] FAIL → classDef cycleNode + class assignments + `%% CYCLE: ...` comment per cycle
- [ ] PASS → one `%% CRITICAL PATH: ...` comment per tied chain

### Output Shape
- [ ] Full L1-impact-assessment.md text inlined as `content` field of `content.artifacts[0]` —
      not in any summary field, not truncated
- [ ] No blob storage write performed by this agent (persistence delegated to workflow summarizer)
- [ ] No `summary`/`*_summary` item field contains the full artifact text instead of a distillation

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every item traces to prd_output / service_catalog / cmdb_export / KB / Phase A |
| Hallucination | ≤ 0.10 | No invented FR, CI, service, node, or edge |
| Consistency | 0.90 | Phase B never contradicts Phase A; JSON items and the embedded mermaid graph never diverge |
| Relevance | 0.85 | The single artifact (L1-impact-assessment.md) is directly usable by its named downstream consumers |
| Reasoning quality | 0.80 | Blast-radius, edge-direction, and cycle/critical-path decisions explained |
| Citation completeness | 0.95 | Components Identified rows cite FR-NNN; graph nodes cite source_requirement |


## Reflection Process
1. Generate Phase A → self-check → 2. Generate Phase B from Phase A's own output →
self-check → render mermaid graph → append to document → 3. Run Quality Gates above → 4. Fix silently →
5. Deliver final combined AgentOutput JSON only, with the full markdown text inline. Do NOT print interim output.
