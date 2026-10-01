# Evaluation — L1-design-integration-architect

> **No evaluator agent, by design.** There is no
> `L1-design-integration-architect-evaluator`. The real downstream checks are
> the Phase 2.25 human gate (Platform Lead signs the Cycle 0 exit test) and
> `gr-L1-architecture-conformance`, which evaluates the `INT-C*` checks this
> agent writes. The prompt's Reflection block is the only automated gate
> before `L1-design-api-spec`, `L1-design-platform-architect` and
> `L1-testing-env-provisioner` read this document.

## Quality Gates
- [ ] **Every** edge in the FSA's `APP-2` component map has an `INT-4` subsection **and** an `INT-5` contract row — checked in both directions. An edge governed in one table and missing from the other is a defect, and an edge in neither is an ungoverned integration
- [ ] Every synchronous edge carries all four: a justification naming the transaction that cannot complete without the answer, a latency budget, a timeout, and a degraded mode. "It is simpler" and "it is faster to build" were not accepted as justifications
- [ ] **No degraded mode is an optimistic assumption about the unknown answer.** Assuming availability sells goods that do not exist; assuming eligibility lets an unvetted party create regulatory evidence. The degraded mode is a refusal or a deferral, and it is stated for asynchronous edges too
- [ ] Every latency budget, timeout, retry count and staleness figure traces to an `nfr-spec.md` boundary condition, a `REQ-INT-*` demand or a KB standard — or it is `PENDING` with an `INT-PEND-nn` trigger. A `TBD — needs stakeholder input` boundary condition was carried through as `PENDING`, never resolved into a millisecond figure
- [ ] Every event is classified by **kind** (`lifecycle` / `evidence` / `movement` / `notification`), and its ordering and replay policy follow from the kind. Evidence events state their replay policy explicitly rather than leaving it implied
- [ ] Contract ownership sits with the **producing** context in every row; no consumer is recorded as owner of a contract or of the entity behind it
- [ ] Where `data-architecture.md` was available: no registered flow implies a second writer for an entity `DAT-1` owns elsewhere, and the event envelope **extends** `DAT-2` rather than defining a second one. Where it was absent, the document says so and records the reconciliation as owed before Cycle 0 closes
- [ ] Database integration, shared mutable tables and unmanaged point-to-point file exchange are recorded as **prohibited** styles, not omitted. Any genuinely unavoidable file exchange is a `TRANSITIONAL` exception with an owner and an exit date, never an approved style
- [ ] Every `REQ-INT-*` demand and every `CON-*` binding `INT` has an `INT-10` row; an unanswered demand appears in `open_questions` rather than being given a hopeful row
- [ ] `INT-11` checks are machine-evaluable expressions, not prose, and cover at minimum: every cross-context edge has a contract, no cross-context DB grants, every synchronous call is budgeted with a degraded mode
- [ ] No endpoint payload, request/response schema or field list leaked in — that is `L1-design-api-spec`'s `openapi.yaml`, and this document would be a second, drifting source for it
- [ ] `INT-7` names no identity **product**. The exact identity technology belongs to the platform viewpoint

## Scores (>= threshold to pass)
| Evaluator | >= | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every context name, component name, edge, demand id and constraint id traces to the FSA verbatim |
| Hallucination | <= 0.10 | No latency, timeout, retry figure, contract or event present that no cited source supports |
| Consistency | 0.90 | `flows[]` and `contracts[]` agree in both directions; no two sections contradict on style, ownership or degraded mode |
| Relevance | 0.85 | Usable as-is by api-spec, platform architect and the testing env provisioner without re-deriving the edge set |
| Reasoning quality | 0.80 | Every `sync_justification` names the transaction; every event `reasoning` explains what follows from the kind |
| Citation completeness | 0.95 | Every non-`PENDING` budget carries a specific, checkable source |
| Edge coverage | 1.00 | `APP-2` edge coverage is total — binary, no partial credit |

## Reflection Checklist
- [ ] Context names, component names and `REQ`/`CON` ids were carried from the FSA **verbatim**
- [ ] Async was the default and sync was the exception — the ratio was a consequence of the domain KB's decision table, not of convenience
- [ ] Every `PENDING` has a matching `INT-12` row with a **trigger condition** (not a date), and every `INT-12` row is referenced from the section it defers
- [ ] Event names follow `{context}.{entity}.{event}`, lowercase, past tense, with a bounded-context first segment — never a team, system or product name
- [ ] Deduplication keys for trade and evidence events derive from the business act, never from a message id
- [ ] Text diagrams are plain ASCII in fenced `text` blocks, readable in a terminal, a diff and a PR review
- [ ] No `*_summary` field in `items` silently contains the full artifact text instead of a distillation

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
