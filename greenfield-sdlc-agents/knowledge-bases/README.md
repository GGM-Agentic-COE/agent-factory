# Phase 0 Knowledge Bases — Food Production & Distribution Domain

## Why 3 KBs, not 4

The original BOM (`Agent_Factory_Greenfield_BOM.html`) lists 4 KB slots for
Phase 0: `kb-L1-sdlc-templates` (× 2 agents), `kb-L1-market-intelligence`,
`kb-L1-regulatory-frameworks`, and `kb-L2-payments-domain`. Building these
out for real, against `agent-standards-best-practices.html`'s token-
optimisation rules (specifically **S4: Template as Instruction**), surfaced
that two of those four don't belong as knowledge bases at all:

| Agent | Original BOM KB | What it actually needs | Verdict |
|---|---|---|---|
| `L1-vision-idea-intake` | `kb-L1-sdlc-templates` | The idea-brief document *structure* — already built as `../templates/idea-brief.template.md` | **Fold into `instructions.md`.** It's ≤3K tokens and purely structural (headings + requirements per section) — S4 says embed it in the prompt, don't pay for a separate KB retrieval. This agent ends up with **no KB**. |
| `L1-vision-statement-generator` | `kb-L1-sdlc-templates` | The vision document *structure* — already built as `../templates/vision.template.md` | Same reasoning. **No KB.** It synthesizes purely from upstream artifacts (idea-brief, market-analysis, regulatory-feasibility) plus the instruction-embedded template — no additional facts needed. |
| `L1-vision-market-analyzer` | `kb-L1-market-intelligence` | Real food-industry facts (channel types, players, trends) — this is domain data, not a generic-across-any-domain methodology | Re-scoped to **`kb-L2-domain-market`** — genuinely domain-specific, so L2 is the correct layer, not L1. |
| `L1-vision-regulatory-feasibility-checker` | `kb-L1-regulatory-frameworks` + `kb-L2-payments-domain` | A generic cross-domain regulator index (real L1 content) **and** real food-specific regulatory facts | Kept as **`kb-L1-regulatory-frameworks-index`** (generic, genuinely reusable) **plus `kb-L2-domain-regulatory`** (food-specific, replacing the payments-domain KB from the earlier scenario). |

This isn't a stylistic preference — it's the difference between *knowledge*
(facts that change independently of the agent's prompt and need their own
version/review cadence) and *instructions* (static structure that should
live in the prompt so it doesn't cost a retrieval call every execution). The
BOM's original 4-KB list conflated the two.

## What's here

```
kb-L1-regulatory-frameworks-index/     L1, cross-domain regulator lookup
kb-L2-domain-market/         L2, food market/competitor facts
kb-L2-domain-regulatory/     L2, food safety/hygiene/labelling/cold-chain facts
```

Each follows the KB Spec Template from `02-agent-development-guide.html`
(`spec.yaml` with real, computed `content_hash` and `total_tokens_estimate`
— not placeholders) and the README requirements from
`agent-standards-best-practices.html` (domain, sources, update frequency,
quality bar, owner, consumers). Content follows the micro-KB content rules:
max 1 line per bullet, max 15 words, no explanations, numbers not words,
each bullet annotated with the downstream section it feeds (e.g.
`(→ Constraint: Cold Chain)`).

All three are well under the ≤1.5K-token micro-KB budget (346 / 720 / 624
estimated tokens respectively) — none needed further splitting.

## Freshness note

Regulatory content (quarterly review) and market content (monthly review)
have different cadences on purpose — market/competitor status ages faster
than food-safety law. Neither KB is a substitute for live verification: the
kb-L2-domain-regulatory KB explicitly says to check current FSA/FSS
guidance before a real authorization decision, and the
kb-L2-domain-market KB explicitly says any
named company is a category example, not a confirmed current-market claim —
that's what `tool-L1-web-search-competitor-scan` is for at execution time.

## Reconciled into the BOM/diagram (2026-08-05)

`Agent_Factory_Greenfield_BOM.html` and
`Agent_Factory_E2E_SDLC_Diagram_Greenfield.html` now match this corrected
3-KB set, and the food-domain re-scope has been extended through the full
pipeline (Phases 1–7), the Phase 0/1 worked examples (now "HarvestLink"),
and the workflow YAML. See the BOM's Phase 0 callout for the full change
log.
