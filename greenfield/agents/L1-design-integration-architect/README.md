# L1-design-integration-architect

> **Status: built (foundational invocation).** `spec.yaml`,
> `output_schema.json`, `evaluation.md` and
> `prompts/L1-design-integration-architect/instructions.md` exist.
> `examples/` and `golden/v1.0.0/` are **not** built — see open item 3. The
> delta invocation (BOM Phase 4) is a separate build. Read this file before
> changing any of the built files.

## Purpose

BOM **Phase 2.25 — Platform & Data Foundation (Cycle 0)**, marked `NEW`.
Owns the integration viewpoint `INT-*`: sync/async decision rules, edge
policy, event/topic taxonomy, contract versioning rules, and the canonical
register of end-to-end cross-context flows.

## Why this document exists at all

**Integration is not a deployable.** Every other design artifact in the
pipeline is shaped like a component — an HLD for a service, an LLD for a
service, an OpenAPI spec for a service. Integration rules have no service to
live in, which is exactly why, in a purely component-shaped document
topology, they had nowhere to live and got re-invented per service by
whoever needed an answer first. The results disagreed, and the disagreement
surfaced in production.

## Relationship to `L1-design-api-spec`

They are complements, not overlaps, and the split is worth stating precisely
because both produce "contract" artifacts:

| | `L1-design-api-spec` | this agent |
|---|---|---|
| Answers | "What does this endpoint look like?" | "Should this edge exist at all, in which direction, sync or not, and what happens when it fails?" |
| Produces | `openapi.yaml` — payloads, schemas, status codes | `integration-architecture.md` — topology, styles, budgets, degraded modes |
| Phase | 4 (per cycle) | 2.25 (once, Cycle 0) |

This agent runs **first** and sets the conventions `api-spec` conforms to.
The prompt therefore forbids endpoint payloads, request/response schemas and
field lists outright — including them would create a second, drifting source
for something `openapi.yaml` owns.

## What it reads

| Input | Source | Required? | Why |
|---|---|---|---|
| `foundational-solution-architecture.md` | `L1-design-foundational-architect`, via blob | **Yes** | `APP-2` component map **and its edges** — the edge set is the work. `CON-*`, `REQ-INT-*`, `SEC-*` trust boundaries, § 4 `PRIN` rows. An edge-less `APP-2` is `INSUFFICIENT_CONTEXT`: there are no integrations to govern |
| `nfr-spec.md` | `L1-requirements-nfr-classifier`, via blob | **Yes** | Performance, Availability and Security boundary conditions — where latency budgets come from. Without them the agent would be inventing millisecond figures, which is the specific failure it exists to prevent |
| `data-architecture.md` | `L1-design-data-architect`, via blob | No | `DAT-1` ownership and `DAT-2` envelope — enriching, see below |
| `binding-principles.json` | per-product resolution, via blob | No | Read per `kb-L1-enterprise-architecture` `BP11` |

The two required inputs match the BOM row exactly (`Agent:
foundational-solution-architecture.md from foundational-architect;
nfr_classifications items from nfr-classifier`).

### Why `data-architecture.md` is optional rather than required

The HarvestLink reference document lists Data Architecture among its inputs,
and the BOM's Phase 2.25 chain order is `platform → data → integration`, so
in the normal case data **has** run and the file is there. It is still
optional, for two reasons:

1. The BOM row does not list it as a required input, and inventing a fourth
   hard precondition would block Cycle 0 on file availability rather than on
   substance.
2. A re-run, a parallel invocation, or a product whose data viewpoint is
   still in draft must still be able to produce integration rules.

When present it does real work: `DAT-1` ownership means no registered flow
can imply a second writer, and `DAT-2`'s envelope is **extended** rather than
duplicated. When absent, the envelope is defined here and the prompt requires
recording that the reconciliation is owed before Cycle 0 closes — so the gap
is visible at the human gate rather than discovered when the two documents
disagree.

## Why the KB pair, and which half is swappable

- **`kb-L1-enterprise-architecture`** (v1.1.0) — `PRIN-03` governed
  interfaces, `PRIN-08` observability, `BP11` resolution contract, and the
  landscape's `EA2`/`EA3`/`EA4` integration boundaries.
- **`kb-L2-food-domain-api-patterns`** (new, built for this agent) — the
  **swappable** half.

That second KB is the interesting one. An L1 integration architect must work
for a payments platform or a healthcare registry without modification. But an
integration architecture unaware of its domain produces a document that is
technically valid and practically useless: it states "async by default, sync
where justified" and leaves the reader to work out which of *their* flows
genuinely cannot be async.

The domain KB carries that judgement — `FD4`'s decision table, `FD3`'s event
taxonomy by kind, `FD5`'s versioning under regulatory change, `FD7`'s
deduplication rules, `FD8`'s two domain-specific observability signals.
Replace the file for a different domain; the agent does not change. That is
why the BOM row lists it alongside the L1 KB rather than folding its content
into the prompt.

## Output

`integration-architecture.md`, written back to the input folder in blob
storage. The BOM row specifies `INT-1`–`INT-4`; the document runs to `INT-13`
for the same reason the data viewpoint runs to `DAT-10` — `INT-1`–`INT-4` is
the *substance*, and `INT-5`–`INT-13` (contract register, reliability policy,
trust boundaries, observability, change policy, traceability, conformance
checks, pending decisions, delta model) is what makes it **checkable** and
**evolvable**. `gr-L1-architecture-conformance` evaluates `INT-11`; the Phase
4 delta invocation depends on `INT-13` existing.

### Two invariants enforced by the schema rather than by prose

1. **A synchronous edge is not expressible without its four obligations.**
   Choosing `style: "synchronous"` makes `sync_justification`,
   `latency_budget`, `timeout` and `degraded_mode` required. A sync call
   whose failure behaviour nobody wrote down works perfectly until the callee
   is down, and then fails in whatever way the first implementer happened to
   choose.
2. **No invented budget.** A non-`PENDING` `latency_budget` requires a
   `source`; a `PENDING` one requires a `pending_ref`. A plausible-sounding
   millisecond figure with nothing behind it fails validation instead of
   shipping into a register that reads as agreed.

`degraded_mode` is required for **asynchronous** edges too — an event
consumer that is down still has a failure behaviour, and "the events queue
up" is an assumption about retention that someone should have written down.

## Prompt length — a flagged, deliberate overage

`instructions.md` is ~415 lines against the skill's ≤150-line budget, almost
entirely the embedded document template (S4). Same justification as the sibling
viewpoint architects: there is no template KB, the section structure **is**
the contract downstream agents read, and the numbered Processing Rules were
kept free of restatements of the template's own inline guidance. The honest
lever, if the budget must be met, is a shared
`kb-L1-architecture-document-templates` across all three architects — not a
thinner template.

## Composition

```
greenfield/agents/L1-design-integration-architect/
├── spec.yaml
├── output_schema.json
├── evaluation.md
└── README.md                  # this file

greenfield/prompts/L1-design-integration-architect/
└── instructions.md            # embedded integration-architecture.md template (S4)
```

## Two invocations — only one is built here

| Invocation | BOM phase | Reads | Emits | Built? |
|---|---|---|---|---|
| **Foundational** | 2.25, once per project | FSA + `nfr-spec.md` | `integration-architecture.md` v1.0 | **Yes** |
| **Delta** | 4, per cycle | `00-overview.md` cross-component sequence, `openapi.yaml` from `design-api-spec`, **current `integration-architecture.md`** | `integration-architecture.delta.json` | No |

Note the inversion between the two: the foundational invocation sets the
conventions `api-spec` conforms to, while the delta invocation *reads*
`openapi.yaml` to detect contracts that appeared without a registered flow
behind them. `INT-13` defines the delta contract it will consume.

## Open items

1. **`gr-L1-consistency-check` and `gr-L1-schema-validator` are not built.**
   Both are named on the BOM row and referenced in `spec.yaml`. The repo has
   `gr-L3-consistency-checker`, not an L1 build — the same naming mismatch
   `L1-design-api-spec`'s README already flags. Guardrails were out of scope
   for this build.
2. **`gr-L1-architecture-conformance` is not built.** It is the real consumer
   of `INT-11`. Until it exists the `INT-C*` checks are written but never
   evaluated.
3. **`examples/` and `golden/v1.0.0/` are not built.** The edge case is
   already specified in the prompt: an `APP-2` map with no edges →
   `INSUFFICIENT_CONTEXT`.
4. **No `L1-design-foundational-architect` exists yet.** See the matching
   item in the data architect's README — all three viewpoint architects are
   built against the FSA's *specified* section vocabulary and need
   re-checking together if the foundational architect ships with a different
   one.
5. **`kb-L2-food-domain-api-patterns` is illustrative.** It is invented for
   the reference scenario, not a real regulator's requirements. Deploying
   against a different domain means replacing that file — and *only* that
   file.
6. **Not wired into `L1-WF-greenfield-idea-to-pr.yaml`.** No Phase 2.25 stage
   exists in the workflow yet.
