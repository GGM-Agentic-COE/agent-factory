# L1-vision-regulatory-feasibility-checker

## Purpose

A viable-looking idea can be dead on arrival for licensing, data-residency,
or consumer-protection reasons. This needs to surface before roadmap
commitment, not after a team has already built against it. This agent
exists because "someone should check the regulations" is exactly the kind
of step that gets skipped under deadline pressure — this makes it
mandatory, structured, and impossible to silently drop a serious finding.

## Jurisdiction

**The agent is jurisdiction-neutral. The KBs are not.** Nothing in the prompt
names a country. Both KBs are **read from Confluence** with
`tool-L1-confluence-reader`, two calls, `page_id = 518422550` and `page_id = 519012353`, fixed in the
prompt. The pages hold the content of `kb-L1-regulatory-frameworks-index-ind`
and `kb-L2-domain-regulatory-ind`. They are not attached at runtime and not read
from GitHub. This agent reads nothing from GitHub. The two KBs are told apart
by their anchors, never by name, and are kept separate so their jurisdiction
declarations can be compared. Each regulatory KB declares the jurisdiction it
covers in its own `#jurisdiction` section, and the agent resolves that at
runtime against the brief's `target_geography` **before assessing anything**.

| Case | Behaviour |
|---|---|
| Brief's country = KB's declared country | Proceed |
| Brief names a state/province/city within the KB's country | Proceed — assess national law, raise the sub-national layer separately |
| Brief names a country the KBs don't declare | **Fail**: `JURISDICTION_MISMATCH`, naming both |
| Brief names several countries, some covered | Assess the covered ones; the rest go to the lookup tool with `requires_legal_review`, or become open items |
| Brief is vague ("global") | The KBs' jurisdiction is the assessable scope; state it as the basis, open item for the rest |
| The two KBs declare different countries | **Fail**: `JURISDICTION_MISMATCH` |
| A KB declares no jurisdiction | Don't guess — lower confidence and flag the limitation |

Swapping the deployment to another country means swapping the KBs. The prompt
does not change.

### Why this is a blocker, not a nicety

An out-of-jurisdiction citation passes every other check in the pipeline.
`gr-L1-citation-verifier` confirms a regulation exists and is specific — a
real foreign statute is both. The KB plausibility check confirms it suits the
category — genuine food law suits a food idea. So the output reads as
complete, confident and well-sourced while binding nothing at all. Only the
jurisdiction check catches it, which is why it's a BLOCKER in the rubric and
why the evaluator re-derives it independently.

The subtler variant is **false equivalence**: the correct local regime named,
but reasoned through the mechanics of the better-known foreign regime it
resembles. Data protection regimes are the usual trap — they borrow each
other's vocabulary while differing on exactly the mechanics that decide a
classification. Both agents are told to take the mechanics from the KB for
the jurisdiction in hand, never from the analogue they know best.

## What does it do?

Accepts `idea-brief.json` from `L1-vision-idea-intake` and produces:
- A list of applicable regulatory constraints, each classified Green/Amber/Red
- A citation to a specific regulation/section for every constraint — no
  generic "comply with regulations" statements
- A concrete mitigation for every Amber/Red constraint, or an explicit
  `requires_legal_review` flag when no precedented mitigation exists
- An overall feasibility verdict, justified by the specific constraints
  driving it
- The **viability score** that gates the pipeline at `qg-L1-viability-score`

Zero tolerance for omitting a Red-classified constraint — the output schema
itself structurally rejects a Red or Amber constraint that has neither a
mitigation nor a legal-review flag.

## Why the viability score lives here (v2.0)

It used to be a separate agent, `L1-vision-viability-scorer`. It is now
derived here, for two reasons. The score's binding term is always the
regulatory posture — an unresolved blocker caps it below the gate no matter
what else is true — so the gate belongs with the agent holding that
evidence. And the second component, market opportunity, could not be relied
on: `L1-vision-market-analyzer` runs in parallel and is optional, so the
score would have been derived from an input that may not exist.

The score is derived from two components, then capped:

| Component | Weight | Source |
|---|---|---|
| Regulatory posture | 0.60 | This agent's own constraints and `overall_status` |
| Idea clarity | 0.40 | `idea-brief.json` — problem specificity, reachable segment, differentiated value |

| Cap | Value | Fires when |
|---|---|---|
| `red_constraint` | 6.0 | Any constraint is Red |
| `regulatory_overall_red` | 6.0 | `overall_status` is Red |
| `requires_legal_review` | 6.5 | Any constraint requires legal review |

A cap is a ceiling, never an average, and `final_score` is the lowest of the
weighted score and every cap that fired. `L1-vision-statement-generator`
receives the number as an input parameter and is forbidden from computing or
adjusting it — the agent whose auto-publish depends on the score must never
be the agent that sets it.

## How does it work?

1. Reads and parses `idea-brief.json` — by key path, never scanned as markdown
1a. Reads the two knowledge bases (the frameworks index and the domain
   regulatory facts) from **Confluence** — `tool-L1-confluence-reader`,
   `page_id = 518422550` and `page_id = 519012353`, one call per page, each retried once on failure. The return is
   Confluence XHTML, so anchors are matched as headings. They are identified by their anchors —
   `#coverage-categories` / `#cross-domain-index` for the index, domain facts
   for the other — never by name, and are never merged, since each declares its
   own `#jurisdiction`. The sweep list must be retrieved in full; a fragment is
   a degraded run, never the whole list. No KB carrying `#coverage-categories`
   or `#jurisdiction` fails the run with `REFERENCE_UNAVAILABLE` rather than
   falling back on remembered categories; the index KB alone is a degraded run,
   with `requires_legal_review: true` on every affected constraint.
   Confluence is read-only here: `regulatory-feasibility.md` goes to blob storage
2. Uses the regulatory frameworks index KB to identify which regulator
   categories apply at all
3. Walks the **sweep list** in that KB's `#coverage-categories` section —
   licensing, data protection, international transfer, automated
   decision-making, consumer protection, advertising claims, product safety
   and labelling, sector safety regimes, AML/payments, employment,
   environmental, accessibility, IP and third-party data, sanctions, tax,
   competition, age-restricted supply. A category that does not apply is
   recorded as assessed-and-not-applicable, never silently dropped.
   The list lives in the KB, not this prompt, so the evaluator's coverage
   audit reads the identical list — see below
4. Reads the domain regulatory KB (and `tool-L1-regulatory-db-lookup`
   for anything beyond the KBs) for the specific applicable rules
5. Classifies each constraint Green/Amber/Red with a citation, applying the
   scenario patterns in the prompt's Edge Cases Section D — rules not yet in
   force, transition and grandfathering, unresolved thresholds, de minimis
   carve-outs, extraterritorial reach, sandboxes, soft law, third-party
   permissions, pre-approval regimes, ongoing duties, overlapping
   regulators, post-divergence regimes, and design-dependent application.
   These stay in the prompt rather than the KB: each names a *behaviour*
   when a rule applies awkwardly, and a KB states what is true while a
   prompt states what to do about it
6. Provides a mitigation for every Amber/Red item — `requires_legal_review`
   is reserved for genuinely unprecedented cases, not a default
7. Sets `overall_status` from the worst constraint, unless every Amber/Red
   item has a precedented mitigation — in which case it explicitly justifies
   why the verdict is one level better than the worst individual item
8. Derives `viability_score` from the two components and applies every
   qualifying cap
9. Self-checks that no Red item was silently dropped and that the score
   derivation is arithmetically sound before returning (full scoring
   delegated to `L1-vision-regulatory-feasibility-checker-evaluator`, per S6)

## Input

- **Source:** `idea-brief.json` from `L1-vision-idea-intake` — uploaded with
  the request, or read from blob storage. **JSON, not markdown:** it is
  parsed and read by key path
- **Required:** `problem_statement`, `target_geography`
- **Optional:** `product_category`, `target_users`, `value_proposition` —
  narrow the regulator lookup and feed the `idea_clarity` component

## Output

- **Type:** `regulatory_feasibility`
- **Items:** `constraints[]` (id, status, citation, rationale, mitigation,
  requires_legal_review), `overall_status`, `categories_not_applicable[]`,
  `viability` (score, recommendation, derivation, components, caps),
  `open_items[]` — see `output_schema.json`
- **Artifacts:** `regulatory-feasibility.md` — now carrying a Viability Score
  section and the score in its header table
- **Metadata:** every constraint carries `citation` (BLOCKER guardrail
  `gr-L1-citation-verifier`, 100% required, not just scored) and `reasoning`
- **Summary:** constraint counts by status, overall verdict rationale, the
  score with its weighted value and every cap that fired, categories swept
  and found not applicable, KB content used, guardrail results, open items

## Composition

```
agents/L1-vision-regulatory-feasibility-checker/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-typical.json
│   ├── output-01-typical.json
│   ├── input-02-novel-question.json
│   └── output-02-novel-question.json
└── golden/v1.0.0/
    ├── input-golden-01-harvestlink.json
    ├── golden-01-harvestlink.json
    ├── input-golden-02-insufficient.json
    └── golden-02-insufficient.json

prompts/L1-vision-regulatory-feasibility-checker/
└── instructions.md
```
