# L1-design-data-architect

> **Status: built (foundational invocation).** `spec.yaml`,
> `output_schema.json`, `evaluation.md` and
> `prompts/L1-design-data-architect/instructions.md` exist. `examples/` and
> `golden/v1.0.0/` are **not** built — see open item 3. The delta invocation
> (BOM Phase 4) is a separate build — see "Two invocations" below. Read this
> file before changing any of the built files.

## Purpose

BOM **Phase 2.25 — Platform & Data Foundation (Cycle 0)**, marked
`RE-SCOPED`. Owns the data viewpoint `DAT-*` for the whole product: the
canonical entity model, the system-of-record register (exactly one owner per
entity), classification / retention / residency policy, the event envelope
standard, and the operational-vs-analytical plane decision **or its trigger
condition**.

## Why "RE-SCOPED" is the important word

The previous version of this agent was triggered **from the LLD**. That made
the data model a *consequence* of how someone happened to design their
classes — an inverted dependency in a DDD regime, where the entity model
should constrain the class design rather than emerge from it.

The foundational invocation runs **before epics**. The canonical entity model
exists before anything is built against it. Two decisions in particular are
effectively permanent once code exists:

- **Two writers on one entity.** Once two services both write `Order`, the
  fix is a migration, not an edit. `PRIN-02-C1` is `BLOCKING` for this
  reason.
- **A retention period invented under delivery pressure.** A feature cycle
  needs an answer that afternoon; whatever number gets typed becomes the
  policy, and it is indistinguishable from a researched one six months later.

Deciding both once, at Cycle 0, is what makes them cheap to get right.

## What it reads

| Input | Source | Required? | Why |
|---|---|---|---|
| `foundational-solution-architecture.md` | `L1-design-foundational-architect`, via blob | **Yes** | `APP-1` contexts, `APP-3` aggregates and invariants, `CON-*`, `REQ-DAT-*`, `SEC-*`, § 4 `PRIN` rows. Must contain an `APP-3` model — without it there is no entity set to assign ownership over, which is this document's whole reason to exist |
| `prd.md` | `L1-requirements-prd-composer`, via blob | **Yes** | The regulatory posture. Classification and retention decided without one is guesswork wearing a table |
| `binding-principles.json` | per-product resolution, via blob | No | Read per `kb-L1-enterprise-architecture` `BP11`. Absent is normal today |

Both required inputs match the BOM row exactly (`Agent: foundational-solution-architecture.md
from foundational-architect; prd.md from prd-composer`). The FSA **names no
technology** — that is this agent's job, within the bounds `PRIN-07` sets.

### Why blob, and why one call

Per the build instruction, the foundational architecture arrives **from blob
storage** and the document goes **back to blob storage** —
`tool-L1-azure-blob-reader` and `tool-L1-azure-blob-writer`, matching the
pattern `L1-vision-statement-generator` already uses. The prompt requires at
most **one** read call naming all three files, because three sequential reads
of the same folder is three round trips for one folder listing.

### On `binding-principles.json` being optional

`binding-principles.template.json` names
`L1-design-foundational-architect` as the consumer that writes `PRIN` and
`DEV` rows into FSA § 4. So by the time this agent runs, the principle
decisions are **already in the FSA** — the resolution file is richer (it
carries `conformance_checks`, `exceptions`, `precedence_rules`) but not
load-bearing. Making it required would block Cycle 0 on a file that may not
exist yet.

The fallback is explicit rather than silent: when the file is absent, apply
the catalogue entries for the principles FSA § 4 *names*, at the binding
level it states, and **say so in the document**. The two failure modes the
prompt forbids are applying the whole catalogue as if every principle were
`MANDATORY`, and skipping § 4 as if none were.

## Why the KB pair, and what changed in them

- **`kb-L1-enterprise-architecture`** — bumped to **v1.1.0** for this build.
  A new content document, `content/binding-principles.md`, carries the
  enterprise principle **catalogue** (`PRIN-01`..`PRIN-08` in nine-field
  form, conformance checks, FSA hooks, precedence rules) plus `BP11`, the
  contract for reading a resolution file. The catalogue is enterprise
  knowledge on the same cadence and owner as the landscape document; the
  per-product **resolution** stays an input artifact, because baking one
  product's exceptions into a KB makes them read as enterprise policy to
  every other product.
- **`kb-L1-enterprise-security`** — bumped to **v1.1.0**. It already had
  `ES2` classification and `ES3` retention, but **no residency standard and
  no encryption standard**. `PRIN-06-C1` checks classification *and*
  retention *and* residency, so without a residency rule every `DAT-3.2`
  residency cell was forced to `PENDING` — a fabricated gap, caused by the
  KB rather than by the product. `ES9` (residency & sovereignty) and `ES10`
  (encryption & key management) close it.

## Output

`data-architecture.md`, written back to the input folder in blob storage,
with the section structure the BOM row specifies: `DAT-1` entity model ·
`DAT-2` event schemas · `DAT-3` classification/retention · `DAT-4` planes.
Two additions to the BOM's four:

- **`DAT-4.4` lineage** — the BOM row calls `DAT-4` "lineage & planes", so
  lineage is part of the contract, not an extra.
- **`DAT-5`..`DAT-10`** — consistency model, read-model register, demand
  traceability, pending decisions, conformance checks, change model. These
  are what make the document *checkable* rather than merely descriptive:
  `gr-L1-architecture-conformance` evaluates `DAT-9`, and the Phase 4 delta
  invocation depends on `DAT-10` existing.

`items` follows the meta-points pattern — capped summaries only, with the
full prose in the artifact. Structural fields (ids, enums, `check`
expressions, `trigger` strings) stay full, because the conformance checker
and the delta merger read them.

### Two invariants enforced by the schema rather than by prose

1. **One writer per entity.** `entity_ownership` takes a single
   `owning_context` per entity and entity values are unique, so a second
   writer is not *expressible* in the output.
2. **No invented governance value.** A `retention` or `residency` of
   `PENDING` requires a `pending_ref` into `pending_decisions`; a non-`PENDING`
   pair requires a `source`. A plausible-sounding period with nothing behind
   it fails validation instead of shipping into a register that reads as
   decided.

## Prompt length — a flagged, deliberate overage

`instructions.md` is ~410 lines against the skill's ≤150-line budget. The
overage is almost entirely the **embedded document template** (S4). It is
justified rather than accepted silently:

- There is no template KB for `data-architecture.md`, and the document's
  section structure **is** the contract downstream agents read — the
  integration architect looks for `DAT-1` ownership, the testing seed agents
  look for `DAT-1`/`DAT-3`, the delta merger looks for section anchors. A
  paraphrased description of the template would let those anchors drift.
- The duplication the skill says to cut *was* cut: the numbered Processing
  Rules do not restate the template's own inline guidance, they only cover
  derivation order, cross-checks and the fail-fast conditions.

If the budget has to be met, the honest lever is extracting the template into
`kb-L1-architecture-document-templates` shared by all three viewpoint
architects — not thinning the template.

## Composition

```
greenfield/agents/L1-design-data-architect/
├── spec.yaml
├── output_schema.json
├── evaluation.md
└── README.md                  # this file

greenfield/prompts/L1-design-data-architect/
└── instructions.md            # embedded data-architecture.md template (S4)
```

## Two invocations — only one is built here

| Invocation | BOM phase | Reads | Emits | Built? |
|---|---|---|---|---|
| **Foundational** | 2.25, once per project | FSA + PRD | `data-architecture.md` v1.0 | **Yes** |
| **Delta** | 4, per cycle | `lld-{component}.delta.json`, `functional_requirements`, **current `data-architecture.md`** | `data-architecture.delta.json`, `db-schema.sql` | No |

The delta invocation is a genuinely different agent shape: it reads the
current canonical document and emits a structured diff, and it is the only
one of the two that emits physical schema (`db-schema.sql`). The foundational
invocation emits **no** physical schema at all — `DAT-10` defines the delta
contract it will consume. `tool-L1-db-schema-diff`, listed "(optional)" on
the BOM row, belongs to the delta invocation and is deliberately not attached
here.

## Open items

1. **`gr-L1-schema-validator` and `gr-L1-pii-detection` are not built.** Both
   are named on the BOM row and referenced in `spec.yaml`. Guardrails were
   out of scope for this build. `gr-L1-schema-validator` needs a decision
   first: for this agent it should validate `items` against
   `output_schema.json`, which is what `gr-L1-output-schema-validator`
   already does — the BOM row may mean a *data*-schema validator, which has
   nothing to validate in the foundational invocation since it emits no
   physical schema.
2. **`gr-L1-architecture-conformance` is not built.** It is the real consumer
   of `DAT-9`. Until it exists, the `DAT-C*` checks are written but never
   evaluated.
3. **`examples/` and `golden/v1.0.0/` are not built.** The repo convention is
   two examples (happy path + edge) and two goldens. The edge case is already
   specified in the prompt: an FSA with no `APP-3` aggregate model →
   `INSUFFICIENT_CONTEXT`.
4. **No `L1-design-foundational-architect` exists yet.** This agent's
   required input has no producer in `greenfield/agents/` today. The three
   Phase 2.25 viewpoint architects are built against the FSA's *specified*
   shape (`APP-1`/`APP-2`/`APP-3`, `CON-*`, `REQ-DAT/INT/PLT-*`, `SEC-*`,
   § 4 `PRIN`); if the foundational architect ships with a different section
   vocabulary, all three inputs need re-checking together.
5. **Not wired into `L1-WF-greenfield-idea-to-pr.yaml`.** No Phase 2.25 stage
   exists in the workflow. Wiring all four Phase 2.25 agents (including
   `L1-arch-baseline-generator`) is one change, not three.
