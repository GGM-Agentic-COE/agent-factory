# L0-binding-principles-generator-evaluator

## Purpose

The binding-principles document is the governance baseline that the target
architecture must honour and that conformance is assessed against at every
release. A wrong verdict, an unbounded deviation or a PRD/KB conflict
resolved without being surfaced spreads into every design written against
it. This agent is the independent check (S6) on
`L0-binding-principles-generator`. It re-derives rather than re-reads: it
asks each catalogue principle's question against the PRD and the knowledge
bases itself, then compares its answer with the document's. It fixes what
can be recovered mechanically and escalates what needs human judgment.

## What does it do?

Reads `{product_name}-binding-principles.json` from S3 and produces:
- **Corrected items** in exactly the generator's structure (`principles[]`,
  `open_questions[]`, `delta[]`), built from the corrected document
- **An evaluation block**:
  - `scores`: faithfulness, hallucination, consistency, relevance,
    reasoning quality, citation completeness
  - `overall_score` and `pass`
  - `findings[]`: pass/fail per gate, each naming the principle ID and the
    rule involved
  - `fixes_applied[]`: before/after excerpts (150 characters or fewer) and
    the reasoning for every change
  - `final_decision`: `approved`, `fixed_and_approved` or
    `escalate_to_hitl`
- **The evaluated document** written back to the same S3 path, still
  `status: "draft"`, plus a top-level `review` object (decision, score,
  fixes, unfixed findings) so the stored document explains its own
  corrections. A human approves or rejects it where it is stored

## How does it work?

1. Inherits `workflow_execution_id` from the generator's output and
   generates a fresh `execution_id`
2. Reads the document from `<workflow_execution_id>/{product_name}-binding-principles.json`
   via `tool-L0-s3-files-reader` (exact path, never lists the folder), the
   PRD and KBs from Confluence, and its own `evaluation.md` from GitHub
3. Validates the document. A non-JSON or wrong-product document is escalated
   with nothing written. An honest INSUFFICIENT_CONTEXT record is approved
   as-is
4. **Catalogue completeness:** compares AP2 IDs and document IDs by set
   membership in both directions
5. **Statement and kind fidelity:** both must match AP2 verbatim
6. **Verdict permissibility:** a technology-selecting principle is never
   `satisfied`
7. **Evidence integrity:** dereferences every `prd:` and KB locator and
   confirms that it supports its note
8. **Verdict re-derivation:** checks that the cited evidence actually
   supports each verdict
9. **Deviation records:** checks for a bounded scope, a forcing requirement,
   an approver role consistent with RULE-03, and `approved_by`
10. **Conflict surfacing:** the stricter value is applied, both sources are
    cited and an open question is raised. No "TBD" is used as a value
11. **Open questions** are sequential, real and present for every `at-risk`
    principle
12. **Baseline fidelity** (when supplied): unchanged principles are
    byte-identical, every difference has one `delta[]` entry, and approved
    deviations have not been changed without `reviewer_notes`
13. Checks document control (`document_version`, `status`, `product`)
14. Applies every fix to both the in-memory document and `items`, scores,
    and decides `final_decision`
15. Always writes the evaluated document back via `tool-L0-s3-writer`,
    whatever the decision (only a failed read or a non-binding-principles
    document leaves nothing to write)

## Input

- **Source:** agent_output from `L0-binding-principles-generator`
  (`workflow_execution_id` only). The document itself comes from S3
- **Required:** `workflow_execution_id`: inherited; names the S3 folder
- **Required:** `prd-confluence-page-id` and the three KB page IDs
  (`architecture-patterns-`, `enterprise-architecture-`,
  `enterprise-security-confluence-page-id`)
- **Required:** `binding-principles-eval-github-folder-location`,
  `agent-github-repo-name`, `agent-github-repo-branch`: where this
  evaluator's `evaluation.md` lives
- **Optional:** `existing_binding_principles`: the baseline, which enables
  the baseline-fidelity check
- **Optional:** `reviewer_notes`: human decisions the document was told to
  honour

## Output

- **Type:** `binding-principles` (same structure as the generator) plus
  `evaluation`
- **Items:** corrected `document_version`, `document_status`,
  `principles[]`, `open_questions[]`, `delta[]`
- **Evaluation:** `scores`, `overall_score`, `pass`, `findings[]`,
  `fixes_applied[]`, `final_decision`
- **Artifacts:** `{product_name}-binding-principles.json`,
  `storage.provider: s3`, location `<bucket>/<key>`. The location is null
  when not written
- **Summary:** score and decision; results for catalogue completeness,
  evidence integrity, verdicts, deviations, conflicts and baseline fidelity;
  what was modified and where it was written; KBs, tools and guardrails;
  gaps

## Composition

```
agents/L0-binding-principles-generator-evaluator/
├── evaluation.md
├── spec.yaml
└── README.md

prompts/L0-binding-principles-generator-evaluator/
└── instructions.md
```

Upstream: `L0-binding-principles-generator`.
Downstream: `L0-target-architecture-generator`, which reads the evaluated
document from the same S3 folder.
