# Phase 1 Knowledge Bases — Requirements → PRD → Impact Assessment → Dependency Graph

## Why 2 KBs, not 4

The BOM (`Agent_Factory_Greenfield_BOM.html`) originally listed 4 KB slots
across Phase 1: `kb-L1-sdlc-templates` and `kb-L2-domain-regulatory` for
`L1-requirements-elicitor`, `kb-L1-enterprise-architecture` +
`kb-L1-enterprise-security` for `L1-requirements-nfr-classifier` (also
reused by `L1-planning-impact-assessor` / `L1-planning-dependency-mapper`).
Auditing them against the same test Phase 0 applied ("Why 3 KBs, not 4" in
`../phase-0/knowledge-bases/README.md`) found that three of those four
don't belong as listed:

| Agent | Original BOM KB | What it actually needs | Verdict |
|---|---|---|---|
| `L1-requirements-elicitor` | `kb-L1-sdlc-templates` | The requirements-document *structure* — already built as `../templates/requirements.template.md` | **Fold into `instructions.md`.** ≤3K tokens, purely structural — S4 says embed it in the prompt, exactly the Phase 0 idea-intake precedent. |
| `L1-requirements-elicitor` | `kb-L2-domain-regulatory` | Nothing — every requirement traces to a `vision.md` clause, and vision.md already carries the regulatory posture forward from Phase 0 | **Removed.** The elicitor never independently re-queries regulatory facts; a KB reference here was never actually exercised. |
| `L1-requirements-elicitor`, `L1-requirements-elicitor-evaluator` | *(none listed — gap)* | A generic, reusable method for judging requirement quality (Unambiguous/Complete/Singular/Feasible/Verifiable/Correct/Traceable — ISO/IEC/IEEE 29148), before checking domain-specific correctness | **New KB (2026-08-08): `kb-L1-requirements-quality-standard`.** Same role as `kb-L1-nfr-classification-taxonomy` — the elicitor loses `kb-L1-sdlc-templates` but gains a genuinely different, genuinely reusable quality-method KB; this is not the same KB slot re-added under a new name. |
| `L1-requirements-nfr-classifier` | (implicitly, via its own worked example citing `regulatory-feasibility.md` directly) | Phase 0's regulatory-feasibility artifact, not a KB, for Compliance-category citations | **Added `regulatory-feasibility.md` as a direct input** instead of inventing a KB the agent was already bypassing in practice. |
| `L1-requirements-nfr-classifier` | *(none listed — gap)* | A generic, reusable method for classifying NFRs into the six standard categories, before checking for grounded values | **New KB: `kb-L1-nfr-classification-taxonomy`.** Genuinely domain-agnostic, genuinely reusable by any future NFR-touching agent — same role as `kb-L1-regulatory-frameworks-index` in Phase 0. |
| `L1-requirements-nfr-classifier`, `L1-planning-impact-assessor`, `L1-planning-dependency-mapper` | `kb-L1-enterprise-architecture`, `kb-L1-enterprise-security` | The org's actual system landscape / security posture | **Correction (2026-08-08):** initially left unbuilt on the reasoning that "greenfield" meant no existing systems to document. That was wrong — greenfield describes the *product*, not the *enterprise*; a new product built inside an already-established company has a real landscape to assess against. Both are now built, with illustrative content for a fictional parent enterprise (Thornbury Foods Group) — see `../../knowledge-bases/` at the project root, not here, since they're enterprise-wide and reused across Phases 1–6, not Phase-1-specific. |

This isn't a stylistic preference — it's the same distinction Phase 0 drew:
*knowledge* (facts or methods that are genuinely reusable and warrant their
own KB) versus *instructions* (document structure that belongs in the
prompt) versus *artifact references* (an upstream document, not a KB, is
the right grounding source) versus *out-of-scope enterprise data* (real,
but not buildable without a specific deployment). The original 4-KB list
conflated all four.

One related decision that did NOT produce a new KB: `L1-planning-impact-
assessor`'s Low/Medium/High blast-radius criteria are small and narrowly
specific to that one agent's own judgment calls — an S4 prompt-embed
candidate once that agent is actually built, not a KB. The NFR taxonomy
passed the reusability test (useful to any future NFR-touching agent, not
just this one); blast-radius classification didn't.

## What's here

```
kb-L1-nfr-classification-taxonomy/     L1, cross-domain NFR classification method
kb-L1-requirements-quality-standard/   L1, cross-domain requirements quality method (ISO/IEC/IEEE 29148)
```

Follows the KB Spec Template from `02-agent-development-guide.html`
(`spec.yaml` with a real, computed `content_hash` and `total_tokens_estimate`
— not placeholders) and the README requirements from
`agent-standards-best-practices.html` (domain, sources, update frequency,
quality bar, owner, consumers). Content follows the same micro-KB content
rules as Phase 0's KBs: max 1 line per bullet, max 15 words, no
explanations, each bullet annotated with the category/section it feeds.

Well under the ≤3,000-token S4 embed threshold by raw size (1,233 estimated
tokens) — kept as a standalone KB anyway, per the reusable-method-vs-
structural-template distinction above, not a token-count threshold alone.

## Freshness note

This KB is a classification *method*, not a domain fact set — it reviews
annually, not quarterly/monthly like Phase 0's market/regulatory KBs. It
also never asserts a number, threshold, or regulation citation itself;
`nfr-spec.template.md`'s zero-tolerance rule requires every boundary-
condition value to trace to `requirements.md` or `vision.md` (including its
Regulatory Posture section) — this KB only supplies the question to ask and
the form to fill in once a grounded value is found.

## Reconciled into the BOM (2026-08-07, corrected 2026-08-08)

`Agent_Factory_Greenfield_BOM.html`'s Phase 1 table matches this corrected
KB set: the elicitor's row shows no KB (with the S4/artifact-grounding
rationale inline), the nfr-classifier's row lists
`regulatory-feasibility.md` as a direct input alongside the new taxonomy
KB, and `kb-L1-enterprise-architecture`/`kb-L1-enterprise-security` now
point at real content under `../../knowledge-bases/` rather than being
flagged out-of-scope. See the BOM's two Phase 1 update callouts
(2026-08-07 and its 2026-08-08 correction) for the full change log,
including what checking the security KB's identity boundary surfaced in
`phase-1/examples/impact-assessment.md` (a genuinely new external
dependency that wasn't visible at vision or requirements stage).

**Superseded 2026-08-07:** `regulatory-feasibility.md` is no longer a saved
document — `L1-vision-regulatory-feasibility-checker` dropped it as an
artifact (same discriminator that dropped `idea-brief.md`/`market-analysis.md`
earlier the same day). The nfr-classifier's direct input described above is
now `vision.md` § Regulatory Posture instead, which already reconciles the
same Phase 0 regulatory findings. See the BOM's Phase 1 callout dated
2026-08-07 (the later one) for the full rationale.
