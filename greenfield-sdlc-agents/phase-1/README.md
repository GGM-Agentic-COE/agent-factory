# Phase 1 — Requirements → PRD → Impact Assessment → Dependency Graph: Templates & Worked Example

Continues the HarvestLink scenario from `../phase-0/`. `vision.md`'s recorded
Product Lead approval (2026-08-04) is the entry point — `L1-requirements-elicitor`
refuses to run without it, and consumes that exact approval comment directly
as its own `approval_comment` input parameter (carried forward to
`L1-requirements-prd-composer` the same way, 2026-08-07).

**Update 2026-08-07:** `requirements.md` and `nfr-spec.md` are dropped as
saved documents — the elicitor's and classifier's full content lives only
under `items` in their own `agent_output`, same treatment as
`idea-brief.md`/`market-analysis.md`/`regulatory-feasibility.md` in Phase 0.
The `templates/requirements.template.md`, `templates/nfr-spec.template.md`,
and their worked `examples/*.md` files below remain on disk as historical
reference (same precedent as Phase 0's own orphaned templates) but are no
longer produced or fetched by any agent. Two markdown artifacts remain real
documents (`templates/prd.template.md`, `templates/impact-assessment.template.md`);
`dependency-graph.json` is JSON, so its "template" is the JSON Schema it must
validate against (`templates/dependency-graph.template.json`), consistent
with how `output_schema.json` works everywhere else in this framework — a
prose template with `{{placeholders}}` doesn't make sense for a
machine-consumed graph.

```
vision.md (Phase 0, approved)
      │  approval comment consumed directly
      ▼
requirements.md          (L1-requirements-elicitor)
      │  9 atomic FRs, each tracing to one vision.md clause
      │  — Roadmap Phase 3's compound clause ("cohort cap AND value limits")
      │    is explicitly split into FR-007 and FR-005
      ▼
nfr-spec.md               (L1-requirements-nfr-classifier)
      │  one section per FR-NNN, same ids and order as requirements.md
      │  — every boundary condition either traces to an explicit number in
      │    vision.md (including its Regulatory Posture section), or is
      │    honestly marked TBD
      ▼
prd.md                     (L1-requirements-prd-composer)
      │  composes requirements.md + nfr-spec.md into one document — every
      │    FR-NNN together with its NFR boundary conditions in one block
      │  — Assumptions/Constraints/Risks carried forward from vision.md's
      │    Regulatory Posture and Open Risks Carried Forward, refined only
      │    where a specific FR reveals something vision-stage couldn't have
      │    known (e.g. a new per-FR risk or assumption)
      │  — Open Questions rolls up every NFR TBD plus any requirement-
      │    coverage gap noticed while composing (e.g. a lifecycle state no
      │    FR covers) — a genuine benefit of reading FR+NFR together
      │  — success metrics deliberately excluded: vision.md's North-Star
      │    Metric(s) stay the one authoritative source, referenced via each
      │    FR's own trace, not copied into a third place that could drift
      │  — pure synthesis, same pattern as L1-vision-statement-generator in
      │    Phase 0: no new requirements or NFRs introduced, zero dropped
      ▼
impact-assessment.md      (L1-planning-impact-assessor)
      │  every FR-NNN mapped to a component + blast radius
      │  — HarvestLink is built WITHIN an already-established enterprise
      │    (Thornbury Foods Group, kb-L1-enterprise-architecture), not a
      │    standalone company — CMDB is real, not empty: 3 existing systems
      │    genuinely touched (SMDS read-check, Snowflake outbound feed, Kong
      │    Gateway pattern), 2 explicitly excluded by architecture decision
      │  — checking kb-L1-enterprise-security's identity boundary (ES1)
      │    surfaced a 3rd external dependency not visible at vision/
      │    requirements stage: HarvestLink needs its own external identity
      │    provider, since Thornbury's Azure AD is employee-only
      ▼
dependency-graph.json     (L1-planning-dependency-mapper)  ← FINAL OUTCOME
   nodes = every component + external dependency from impact-assessment.md
   edges = uniform prerequisite → dependent direction, for ALL edge types
   cycle_check.status = PASS (verified programmatically, not just asserted)
   critical_path = a GENUINE TIE at 3 edges: the compliance-completeness-
     methodology chain and the new external-identity-provider chain both
     converge on allergen-declaration-service and share its entire
     downstream tail — allergen-declaration-service is a compounded
     bottleneck blocked by two independent, unresolved external
     dependencies at once; resolving only one does not clear the critical
     path. Both beat the legal-structure-validation chain (2 edges) by one
     hop, same as before this update.
```

Note: `impact-assessor` and `dependency-mapper` consume `prd.md`, not the
elicitor's/classifier's items directly — those two agents' items are read
directly by other consumers instead (Phase 3's `story-generator` and
Phase 4's `design-api-spec`/`design-hld`/`design-data-architect` all read
`agent_output` from `L1-requirements-elicitor`/`L1-requirements-nfr-classifier`
directly, per the workflow YAML), but Phase 1's own downstream steps read
the composed PRD as their single source of truth.

**What to check when validating a real agent's output against these examples:**
- Same `workflow_execution_id` across all five Phase 1 outputs
  (`wf-6d3f8b04` here) — different from Phase 0's, since each phase is its own
  workflow execution.
- Every `FR-NNN` in the elicitor's `functional_requirements` items reappears
  in the classifier's `nfr_classifications` items (same id),
  `prd.md` (composed, with its NFR table attached), `impact-assessment.md`
  (mapped to a component), and `dependency-graph.json` (in some node's
  `source_requirement` array). A requirement that vanishes partway through
  the chain is a real defect, not a rounding error — an
  earlier revision of this worked example (the original payments-domain
  scenario) shipped with exactly this gap (one FR missing from the graph),
  caught only by the validation pass described below, not by inspection.
- **Edge direction in `dependency-graph.json` must be uniform**: `from` is
  always upstream/prerequisite, `to` is always downstream/dependent,
  regardless of whether the edge `type` is `depends-on`, `blocks`, or
  `integrates-with`. Mixing directions across types is exactly the bug this
  worked example initially shipped with (`blocks` edges ran blocker→blocked
  while `depends-on` edges ran dependent→prerequisite) — it validated fine
  against the JSON Schema (schemas can't express traversal direction) but
  produced a `critical_path` that a real topological sort couldn't
  reconstruct. Schema-valid is not the same as semantically correct — run an
  actual graph traversal, don't just eyeball it.

Validated mechanically, not just by inspection: `dependency-graph.json`
passes JSON Schema validation, an independently-computed DFS cycle check
matches the declared `cycle_check.status`, and an independently-computed
longest prerequisite chain matches the declared `critical_path.nodes`
exactly. Example content is illustrative only, as in Phase 0.
