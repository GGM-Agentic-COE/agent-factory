# L0-binding-principles-generator

## Purpose

Enterprise architecture principles are written for every product; a
product's PRD is written without them in mind. This agent closes that gap
before any architecture is drawn. It decides what each principle in the
enterprise catalogue means for this product, and records the result as the
governance baseline that the target architecture must honour and that
conformance is assessed against at every release. It assesses; it does not
design. It never proposes bounded contexts, components or technology.

## What does it do?

Reads the PRD and three knowledge bases from Confluence and produces
`{product_name}-binding-principles.json` in S3, containing:
- **One entry per principle** in the `kb-L0-architecture-patterns` AP2
  catalogue: exactly once, ID and statement verbatim, nothing added, merged
  or dropped
- **A verdict** from RULE-04 for each principle:
  - `satisfied`: the AP3 pattern(s) that will realise it, in `applies_via[]`
  - `deviation-required`: a bounded deviation with `deviation_scope` (named
    flows, requirements or stores only), `rationale`, `approver_role` and
    `approved_by` (from `reviewer_notes`, else `"pending"`)
  - `applied-in-solution-architecture`: for technology-selecting
    principles, with the demand it will be assessed against
  - `at-risk`: the PRD open question, unset target or assumption that
    threatens it
  - `not-applicable`: the reasoning
- **Evidence**: every item cites a PRD key with the `prd:` prefix
  (`prd:FR-012`, `prd:NFR-06`) or a KB section key (`ES3`, `EA4`)
- **Conditions**: what must still be decided for the verdict to stand
- **Open questions** (`BPQ-NN`), including every PRD/KB conflict, where the
  stricter value is applied and both sources are cited
- **A delta register**, empty on a fresh document. With a baseline, it holds
  one entry per change, each marked `pending-human-review`

The output JSON carries only `items` (each principle's structural fields
with a `rationale_summary` of 150 characters or fewer, open questions, delta)
and the S3 location. The full rationale and evidence notes live only in the
stored document.

## How does it work?

1. Generates a new `workflow_execution_id` (this is the first step of the
   workflow) and a fresh `execution_id`
2. Reads the PRD and the three KBs from Confluence by page ID and takes
   `product_name` from the PRD
3. Builds a PRD index by meaning (FRs, quality requirements, unset targets,
   obligations, assumptions, risks, open questions, entities, glossary) and
   the AP2 catalogue with AP2.1 carried rules, AP3 patterns and AP4 rules
4. Returns INSUFFICIENT_CONTEXT if the PRD has no keyed FRs or the AP2
   catalogue is empty
5. For each principle, gathers evidence and decides the verdict under
   RULE-04. On a PRD/KB conflict it applies the stricter value, cites both
   sources and raises an open question. A "TBD" PRD value is never used as a
   value
6. With `existing_binding_principles`, carries unchanged principles
   verbatim, re-resolves only those with changed evidence or reviewer
   direction, and registers every difference in `delta[]`. An approved
   deviation is never changed without `reviewer_notes`
7. Sets `document_version` (1.0 fresh, major/minor bump on update) and
   `status: "draft"`
8. Runs a mechanical self-check: principle count, verdicts, deviation fields,
   no placeholders, delta completeness, summaries not holding the full
   rationale
9. Writes the document to `<workflow_execution_id>/{product_name}-binding-principles.json`
   via `tool-L0-s3-writer` and records the confirmed location

## Input

- **Source:** direct input (Confluence page IDs). The PRD is the one
  published by `L0-prd-composer-evaluator`
- **Required:** `prd-confluence-page-id`: the PRD page
- **Required:** `architecture-patterns-confluence-page-id`,
  `enterprise-architecture-confluence-page-id`,
  `enterprise-security-confluence-page-id`: the three KB pages
- **Optional:** `existing_binding_principles`: a previously approved
  document, which turns the run into an update with a delta register
- **Optional:** `reviewer_notes`: human decisions to honour (approvers,
  authorised deviation changes)

## Output

- **Type:** `binding-principles`
- **Items:** `document_version`, `document_status`, `principles[]` (id,
  verdict, evidence_locators, applies_via, deviation_scope, approved_by,
  rationale_summary, confidence, reasoning), `open_questions[]`, `delta[]`
- **Artifacts:** `{product_name}-binding-principles.json`, format `json`,
  `storage.provider: s3`, location `<bucket>/<key>`. The location is null
  when the write failed
- **Metadata:** `confidence` (0.9+ explicit, 0.7–0.8 inferred, below 0.7
  means `at-risk`) and `reasoning` per principle
- **Summary:** counts by verdict, deviations and approval state, open
  questions, delta entries (applied vs awaiting review), the S3 location or
  tool error, KBs consulted, tools invoked, gaps

## Composition

```
agents/L0-binding-principles-generator/
├── spec.yaml
└── README.md

prompts/L0-binding-principles-generator/
└── instructions.md
```

Upstream: PRD published to Confluence by `L0-prd-composer-evaluator`.
Downstream: `L0-binding-principles-generator-evaluator`, which reads the
document from the same S3 folder.
