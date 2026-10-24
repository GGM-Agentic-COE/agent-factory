# Phase 0 — Idea → Vision: Output Templates & Worked Example

Templates in `templates/` define the required shape of each artifact — every
section marked ✅ is a hard requirement; an evaluator FAILs the gate if it's
missing. Placeholders use `{{snake_case}}`; HTML comments at the top of each
template name the producing/evaluating agent and the upstream artifact it
depends on.

**Update 2026-08-07:** `idea-brief.md`, `market-analysis.md`, and
`regulatory-feasibility.md` are dropped as saved documents — each agent's
full content lives only under `items` in its own `agent_output`; `vision.md`
is the only real document Phase 0 still produces (it has an explicit Product
Lead approval gate, and is reused directly by later phases). The three
`templates/*.template.md` files and their worked `examples/*.md` files below
remain on disk as historical reference but are no longer produced, fetched,
or gated against by any agent — the "every section marked ✅ is a hard
requirement" rule above now applies only to `vision.template.md`. See
`Agent_Factory_Greenfield_BOM.html`'s Phase 0 callouts for the full
rationale.

`examples/` is one coherent worked example (a fictional product,
"HarvestLink" — a compliance-enabled producer-to-foodservice marketplace,
food production & distribution domain) run through the full chain, so you
can see exactly how facts must propagate rather than just what the section
headings are:

```
idea-brief.md            (L1-vision-idea-intake)
      │  problem statement, target users, candidate metrics
      ▼
market-analysis.md       (L1-vision-market-analyzer)
      │  consumes idea-brief's problem/users → competitor gap analysis
      ▼
regulatory-feasibility.md (L1-vision-regulatory-feasibility-checker)
      │  consumes idea-brief's geography/category → Green/Amber/Red per constraint
      ▼
vision.md                (L1-vision-statement-generator)  ← FINAL OUTCOME
   reconciles all three inputs:
   - problem/users/value prop carried forward verbatim, not restated differently
   - market-analysis's competitive gap → Market Context section
   - regulatory-feasibility's Amber/Red items → Regulatory Posture, AND every
     Amber/Red item must reappear in Open Risks Carried Forward
   - the single worst risk (the Red item) must become roadmap Phase 1 —
     this is the concrete test of "reconciliation," not just summarization
```

**What to check when validating a real agent's output against these examples:**
- `workflow_execution_id` is identical across all four agent outputs in one
  run — only `vision.md` is a real document; the other three exist solely as
  `agent_output.content.items`.
- `execution_id` is unique per agent output.
- Every named entity in a downstream output (problem statement, target
  users, artifact IDs) traces back to an upstream agent's items — no drift,
  no restating the same fact two different ways.
- Every Amber/Red regulatory item survives all the way to `vision.md`'s Open
  Risks section. If one goes missing between `regulatory-feasibility.md` and
  `vision.md`, that's the evaluator's `gr-L1-hallucination-check` /
  `gr-L1-consistency-check` catching a dropped constraint — not a stylistic
  choice by the generator.

The example content is illustrative only — synthetic company names,
regulatory citations, and a fictional product, written to demonstrate the
pipeline's shape. It is not real market research or legal advice, and
shouldn't be reused as either.
