# L0-solution-architect

> **Status: built (Cycle 0 invocation).** `spec.yaml`, `output_schema.json`,
> `evaluation.md`, `prompts/L0-solution-architect/instructions.md`
> and two examples (happy path + `TARGET_NOT_APPROVED`) exist. The happy-path
> output validates against `output_schema.json`, and a script checked it
> against the target it was built from (entity set, owners, classes, edges,
> demands, constraints, security rows, PEND references). `golden/` is not
> built. **Read "Relationship to the three viewpoint architects" before wiring
> this into a workflow.**

## Purpose

Cycle 0 of the ADLC architecture regime
([Architecture in the ADLC](../../foundational_arch_rationale_v2.html) § 6).
It writes `solution-architecture.md`: how each demand in the approved
`target-architecture.md` is met. It names technologies; the target never
does.

The document follows a fixed twelve-section shape (overview, drivers,
application, data, integration, flows, platform, security, traceability,
open items, decisions, glossary), written in an architect's voice with
Mermaid figures. The reference rendering is
[examples/artifacts/solution-architecture.md](examples/artifacts/solution-architecture.md).

| Part | Sections | What it decides | Read by |
|---|---|---|---|
| Application | APL-1..4 | Component catalogue, service responsibilities and dependencies, shared patterns, failure policy | HLD agents |
| Data | DAT-1..4 | Entity model with retention and residency, data rules per invariant, snapshot register, event envelope, classification policy, planes | HLD agents, test data agents, baseline generator |
| Integration | INT-1..4 | One protocol decision per APP-2.3 edge, contract rules, planned contracts, topics and consumer declarations, end-to-end flows | API-spec and HLD agents, contract tests |
| Platform | PLT-1..6 | Runtime, environments, pipeline and **Cycle 0 exit proof**, observability, resilience and retention tiers, **capability register** | Impact assessor (every change), Platform Lead |
| Security | SEC | How each target SEC-* control and TB-* boundary is implemented | Security review, test agents |
| Index | Section 10 traceability, "Constraints honoured" | Every target REQ-* → **Met** or **Not yet built** with a reason; every CON-* → its realising rule | gr-L0-architecture-conformance |
| Open items | Section 11 PEND rows | Every decision not yet made, with its owner, the condition that resolves it, and what it blocks | Impact assessor, approvers |

It runs after the Enterprise Architect approves the target. It refuses a
DRAFT target unless `allow_draft_target` is set for a dry run.

## Decisions worth knowing

**1. Cycle 0 decides only what Cycle 0 needs.** A capability is decided now
if it is band First, has High lead time, is part of the exit proof, or is a
policy every context needs before the first feature. Everything else is
**deferred**: its PLT-6 row is NOT PRESENT with the band that needs it, its
REQ is NOT_YET_BUILT, and the impact assessor raises the first change that
needs it to Tier 2. In the example, search, scheduled jobs and email are
deferred. That matches what HarvestLink actually did: search arrived at C2,
jobs at C4a, email at BF-2c.

**2. Technology is grounded or labelled PROPOSED.** Approval comes from
`kb-L0-enterprise-architecture` **EA11**, the approved platform catalogue
(STD-TECH-01), added in KB v1.2.0. Selection order: estate mandate (EA9 API
gateway) → EA11 `adopt` → `contain` only with an exception → otherwise
**PROPOSED, lifecycle unverified**. `retire` is never selectable. The schema
enforces it: lifecycle `unverified` forces `decision_status: PROPOSED`, an
EA11 product can't be DECIDED unless EA11's catalogue status is APPROVED,
`contain` requires an `exception_ref`, and `retire` isn't in the enum. If
EA11 is missing or not approved, the document's first line says so.

**3. Every rejected alternative names what it lost on.** That is a REQ
budget, a lifecycle status or an estate rule, never "industry standard"
(PRIN-01). Examples: Service Bus can't meet the 24 h replay budget; Azure SQL
can't natively refuse overlapping validity windows (INV-08); B2C is `retire`.

**4. No invented numbers.** A timeout is the REQ-INT budget or an allocation
from a parent budget with the arithmetic shown (INT-1.06: 800 − 200 → 100 ms).
Anything else is PENDING with a condition trigger. RTO/RPO, Session
retention and catalogue retention are PENDING in the example, because no
source states them.

**5. Target questions are checked before being carried.** The agent asks
whether its design makes a target open question moot. In the example, local
token validation answers OQ-01 (there's no runtime call to budget), and
archiving the rendered statement alongside its figures answers OQ-03. OQ-02
is carried as PEND-05.

**6. The agent never certifies Cycle 0.** Every exit-proof criterion is
`NOT_YET_PROVEN` (a schema constant); the Platform Lead signs it.

**7. `items` keys match the baseline generator.** `entity_ownership`,
`classification_register`, `events`, `data_planes`, `flows`, `contracts`,
`capability_register`, `pending_decisions`, `exceptions_recorded` and
`cycle0_exit_proof` are the keys `L0-arch-baseline-generator` already reads
from the three viewpoint outputs, so one output from this agent can feed it.
`flows` holds the per-edge INT-1 decisions; the INT-4 register is
`end_to_end_flows`.

## Relationship to the three viewpoint architects

The repo already has `L0-design-data-architect`,
`L0-design-integration-architect` and `L0-design-platform-architect`, each
writing its own document (`data-architecture.md` DAT-1..10,
`integration-architecture.md` INT-1..13, `platform-architecture.md`
PLT-1..19). The v2 regime replaces them with **one** agent and **one** file,
as `harvestlink-docs/architecture/solution-architecture.md` shows. The
regime allows a split by viewpoint only when the file grows too large to
read, and only if the section IDs are kept.

This agent follows v2. The two section spines overlap but are not the same:

| | v2 (this agent) | Viewpoint agents |
|---|---|---|
| DAT-1..4 | entity model, envelope, classification, planes | same meaning |
| INT-1..4 | protocol rules, contracts, topics, flows | principles, styles, contract rules, flow register |
| PLT-2..5 | environments, pipeline, observability, resilience | topology, persistence, messaging, object storage |
| PLT-6 | capability register | capability register |

Running both in one workflow would give two answers for the same section ID.
Pick one. **Recommended: adopt this agent and mark the three viewpoint
agents superseded.** Their prompts hold good detailed guidance (the
templates in `DAT-/INT-/PLT-template.md` at the repo root) that could later
seed a split-by-viewpoint mode if the file outgrows a single read.

## What it reads

| Input | Source | Required? | Why |
|---|---|---|---|
| `target-architecture.md` | Direct input, upload, or Confluence page (`target_architecture_page_id`) | **Yes**, approved (status **Approved**, Enterprise Architect row signed) | Every entity, interaction (R-nn), registered read model, demand, QA, constraint, control and open item (OI-nn), and the resolved principles (Section 3). The older layout (front matter, APP-2.3 E-nn edges, § 4.2 bands) is still read |
| `prd.md` | Direct input, upload, or Confluence page (`prd_page_id`) | No | NFRs the target didn't carry (recovery objectives, per-entity retention); never overrides a target budget |
| `kb-L0-enterprise-architecture` v1.2.0+ | Confluence page (`enterprise_architecture_kb_page_id`) | Must (unreadable → `REFERENCE_UNAVAILABLE`) | **EA11 approved platform catalogue and regions**; BP8 lifecycle rule; PRIN-08; EA2/EA3/EA4/EA6/EA9/EA10 estate rules and mandates |
| `kb-L0-enterprise-security` | Confluence page (`enterprise_security_kb_page_id`) | Must (unreadable → `REFERENCE_UNAVAILABLE`) | ES1, ES3, ES4, ES5, ES9, ES10 |
| `kb-L0-food-domain-api-patterns` | Confluence page (`domain_api_patterns_kb_page_id`) | Should; swap per domain (unreadable → degraded run) | FD4 sync table and degraded modes, FD5 versioning, FD7 consumer declarations, FD8 signals |
| Document Template `solution-architecture-template.md` | GitHub (`template_repo`, `template_branch`, `template_folder`) — in agentic-sdlc-knowledge-bases at `3. design-and-architecture/solution-architecture/templates` | Must (unreadable → `REFERENCE_UNAVAILABLE`) | **Headings, tables, callouts and every cell's fill rule.** Not embedded in the prompt; edit it in the repo |
| Reference example `solution-architecture.md` | GitHub (`example_repo`, `example_branch`, `example_folder`) | No — leave the three empty to skip it; unreadable means the run proceeds on the template alone | **Voice and density only**: a document written by a real solution architect. Never a source of facts, ids, numbers or technology |

The three KBs are read every run with `tool-L0-confluence-reader`, one call
per page id; they are not attached at runtime. The agent tells them apart by
content, not page title, and the evaluator reads the same three pages.

**Not inputs:** `binding-principles.json` (the approved target already
carries the resolved principles and deviations) and a per-run platform
catalogue file (the catalogue is enterprise-wide, so it lives in the KB as
EA11).

**Three ways in.** Each input is resolved separately, using the first route
present: (1) **direct input** (`target_architecture_output` / `prd_output`,
an upstream JSON output or pasted text); (2) **uploaded file** (`.md`,
`.json`, or a Confluence `.html`/`.xml` export), identified by file name or,
if renamed, by its content; (3) **Confluence page**, fetched only when the
input did not arrive by 1 or 2. No page id is required when the target is
passed or uploaded. `items.document_control` records the route
(`target_source`, `prd_source`); the document itself carries no front
matter.

**Confluence specifics.** `tool-L0-confluence-reader` takes a `page_id`
only (no base URL) and returns storage-format XHTML, not markdown. The
prompt tells the agent to read headings and tables and match section ids in
their text. A copy supplied directly (`target_architecture_output`) or
uploaded takes precedence and skips the target call.

**Output.** The full document is saved to S3 with `tool-L0-s3-writer`
(one call: `folder_name = s3_folder_name`, `file_name =
solution-architecture.md`), and the final JSON carries the S3 location in
`artifacts[0].storage` (`bucket`, `key`, `write_mode: saved`) with an empty
`content`. The document is written once, into the tool call, so the long
output is split over two model turns (document ~20k tokens, then items
~8k) instead of one ~27k-token answer. When the S3 writer is not
attached, `s3_folder_name` is not supplied, or the save fails after one
retry, the full document is returned in `artifacts[0].content` instead
(`write_mode: not_saved | failed`), never as a file path.
`L0-solution-architect-evaluator` reads it from S3 (or from the JSON),
evaluates it, corrects it and publishes it to Confluence as
`<product>-solution-architecture.md`.

## Composition

```
greenfield/agents/L0-solution-architect/
├── spec.yaml
├── output_schema.json
├── evaluation.md
├── README.md                                   # this file
└── examples/
    ├── input-01-harvestlink-cycle0.json        # Confluence page ids + target supplied directly (approved)
    ├── output-01-harvestlink-cycle0.json       # items + the artifact below embedded in artifacts[0].content
    ├── artifacts/solution-architecture.md      # full Cycle 0 document, DRAFT
    ├── input-02-draft-target.json              # target still DRAFT
    └── output-02-draft-target.json             # TARGET_NOT_APPROVED, nothing derived

greenfield/prompts/L0-solution-architect/
└── instructions.md                             # embedded solution-architecture.md template (S4)
```

`input-01` is generated from `L0-design-target-architect/examples/output-01`
with the approval applied, so the two agents' examples chain exactly.

## Open items

1. **Choose between this agent and the three viewpoint architects** (see
   above). Until then, don't wire both.
2. **EA11 is illustrative.** Like the rest of `kb-L0-enterprise-architecture`,
   it describes the fictional Thornbury Foods scenario: Azure-based to match
   EA2, with one `contain` and one `retire` entry. Every DECIDED technology
   in the example rests on it. Replace it with the real organisation's
   catalogue, owned by Enterprise Architecture, on deployment.
3. **Per-change invocation not built.** After Cycle 0 this file is edited in
   place on change branches (Step 2). That mode reads a change brief and
   edits named sections; it is a separate build.
4. **Not wired into `L1-WF-greenfield-idea-to-pr.yaml`.** It belongs at
   Cycle 0, after roadmap planning: this agent, then
   `L0-solution-architect-evaluator` (which publishes to Confluence),
   then the Solution Architect and Platform Lead HITL gates, then
   `L0-arch-baseline-generator`. The workflow must pass the target page id
   (unless the target is uploaded), the three KB page ids, the S3 folder
   (`s3_folder_name`, the same for both agents), the rubric repo,
   branch and folder, and the Confluence space key. Page ids only, no base
   URL.
9. **The target architect still writes to blob** and still reads
   `binding-principles.json`. Its output needs to reach Confluence for this
   agent's page-id input to work; until then, upload the target.
5. **Baseline generator inputs.** It currently requires four separate
   outputs. Pointing it at this agent means accepting one
   `solution_architecture_output` in place of the data, integration and
   platform outputs. The keys already line up (decision 7).
6. **`gr-L0-secret-scanner` and `gr-L0-architecture-conformance` aren't
   built.** The check script used on the example (entity, edge, demand,
   constraint and PEND cross-references against the target) could seed the
   conformance guardrail's mechanical half.
7. **Rubric copy.** Evaluators read `evaluation.md` from
   `agentic-sdlc-knowledge-bases` at runtime, so copy it there.
8. **`golden/` is not built.**
