<!--
TEMPLATE: prd.md
Produced by: L1-requirements-prd-composer (Core)
Evaluated by: L1-requirements-prd-composer-evaluator
Consumes: requirements.md + nfr-spec.md (both in full — this agent does not
          re-derive requirements or NFRs, it composes what already exists)
          + vision.md (read-only, for its Open Risks Carried Forward and
          Regulatory Posture sections — carried forward, not re-analyzed)
Consumed by: L1-planning-impact-assessor, L1-planning-dependency-mapper

This is a SYNTHESIS agent, not an extraction agent — same pattern as
L1-vision-statement-generator in Phase 0. Every FR-NNN in requirements.md
MUST appear here with ALL of its nfr-spec.md boundary conditions attached —
zero requirements dropped, zero boundary conditions dropped. Do NOT
re-classify or re-derive NFRs here; carry them forward verbatim from
nfr-spec.md. The value of this document is composition (one place to read
a requirement and everything cross-functional about it), not new analysis.

Assumptions / Constraints / Risks follow the SAME carry-forward discipline:
pull from vision.md's Regulatory Posture and Open Risks Carried Forward
sections rather than re-deriving from scratch. The one exception is
requirement-level refinement — a risk, assumption, or constraint that only
becomes visible once a concrete FR exists (e.g. "FR-003's audit-log
immutability may need legal review against a data-erasure right") may be
added even though vision.md never stated it, since vision.md was written
before any FR existed to reveal it. Do NOT invent a new PRODUCT-level risk,
assumption, or constraint that isn't traceable to either vision.md or a
specific FR-NNN — that would be new analysis, not composition, and belongs
in a different pipeline step if it's needed at all.

Success metrics are deliberately OUT of scope for this document — vision.md's
North-Star Metric(s) remain the single authoritative product-level metrics
(FRs trace to them directly where relevant, e.g. FR-008/FR-009 below); adding
a third, PRD-level metrics section here would just be a copy that can drift
out of sync with vision.md's.

Required sections marked ✅. A requirement with no attached boundary
conditions is possible (nfr-spec.md may have found none applicable) — in
that case write "No NFR categories apply" rather than omitting the
subsection, so a reader can tell "none found" apart from "forgot to check."

Write the Executive Summary LAST, once every other section is final — same
rule as vision.md's own executive summary. It must introduce NO claim
absent from the sections below it; it condenses, it never adds. Name the
requirement count, the single biggest constraint or risk (whichever most
shapes the requirement set), and the open-question count, so a reader
without time to read the full document still knows what to worry about.
-->

# PRD: {{product_name}}

| Field | Value |
|---|---|
| Source requirements | `requirements.md` (items from `L1-requirements-elicitor` — no document, 2026-08-07) |
| Source NFR spec | `nfr-spec.md` (items from `L1-requirements-nfr-classifier` — no document, 2026-08-07) |
| Source vision | `vision.md` ({{vision_artifact_id}}) — Assumptions/Constraints/Risks only |
| Approval consumed | {{approver_name_role}}, {{yyyy-mm-dd}}: "{{approval_comment_text}}" — passed in directly as this agent's own `approval_comment` input parameter (same vision-approval gate `L1-requirements-elicitor` consumed; no requirements document header to retrieve it from) |
| Generated | {{yyyy-mm-dd}} |

## ✅ Executive Summary
{{3-5 sentences, written LAST: what this PRD covers (requirement count),
which vision.md approval it follows, the single biggest constraint or risk
that shapes the requirement set, and the open-question count — every claim
here must already appear in a section below}}

## Compound Requirements Split
{{carried forward verbatim from requirements.md's own Compound Requirements
Split section — do not re-derive; this document is self-contained so a
reader never needs to open requirements.md separately}}

## ✅ Assumptions
{{list what the requirements below take as given but have not yet been
validated — things a specific FR depends on being true. Each item should
name which FR(s) it underlies. This is NOT the same as a risk (a risk is
something that could go wrong; an assumption is something believed true
that hasn't been checked yet). Carry forward anything vision.md already
implied as an unvalidated premise (e.g. a roadmap step described as "design
and validate X" implies X is currently assumed, not yet validated); add a
new one only if a specific FR reveals a premise vision.md never stated.}}
- **{{short assumption title}}** (underlies {{FR-NNN, FR-NNN}}): {{the
  assumption, stated as a belief not yet confirmed}}

## ✅ Constraints
{{list real limits on the solution space — regulatory, technical, or
business — carried forward from vision.md's Regulatory Posture and Roadmap
Outline. Each item should name which FR(s) it constrains. A constraint
shapes what an FR is ALLOWED to do; don't restate the FR itself here, name
the limit that produced it.}}
- **{{short constraint title}}** (constrains {{FR-NNN, FR-NNN}}): {{the
  limit, and its source — "vision.md § Regulatory Posture" or similar}}

## ✅ Risks
{{carry forward every still-open item from vision.md's Open Risks Carried
Forward section verbatim — do not drop one. Tag each with the FR(s) it
affects if it maps to specific requirements; some risks (e.g. a competitive-
timing risk) are program-level and don't map to any single FR — say so
rather than forcing a false tag. Add a new risk only if a specific FR
reveals one vision.md couldn't have known about yet.}}
- **{{short risk title}}** ({{affects FR-NNN, FR-NNN | program-level, not
  tied to a specific requirement}}): {{the risk, carried from vision.md or
  newly surfaced at requirement level — say which}}

## ✅ Requirements

### FR-{{NNN}}: {{short title, matching requirements.md}}
**Statement:** {{single, atomic, testable capability — carried verbatim
from requirements.md}}
**Traces to:** vision.md § {{section name}}

**Non-Functional Requirements:**
| Category | Boundary Condition | Source |
|---|---|---|
| {{Performance \| Security \| Scalability \| Availability \| Compliance \| Usability}} | {{carried verbatim from nfr-spec.md — explicit number/rule, or "TBD — needs stakeholder input"}} | {{"vision.md § X" if explicit, else "—"}} |

{{repeat the NFR table row per category that applies to this FR, or write
"No NFR categories apply" if nfr-spec.md found none; repeat this whole
block (statement + NFR table) once per requirement, same FR ids and order
as requirements.md}}

## ✅ Open Questions
{{two kinds of gap, both belong here — don't split them into separate
sections, a reviewer wants one list:
(1) every boundary condition across all requirements above that reads "TBD
    — needs stakeholder input", tagged with its FR-NNN and category;
(2) any requirement-COVERAGE gap noticed while composing FR+NFR side by
    side — e.g. a lifecycle state (offboarding, disputes, suspension) that
    no FR currently covers. This is a genuine benefit of composition: a gap
    invisible in requirements.md alone can become obvious once every FR is
    read together with its NFRs. Do not invent a gap for its own sake — only
    include one you can point at specifically.}}
- {{FR-NNN}} ({{category}}): {{the TBD boundary condition text}}
- **Coverage gap:** {{what's missing, and why composing this document surfaced it}}

---
*Generated by `L1-requirements-prd-composer` · execution_id: `{{execution_id}}` · workflow_execution_id: `{{workflow_execution_id}}`*
