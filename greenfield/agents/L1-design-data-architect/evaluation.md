# Evaluation — L1-design-data-architect

> **No evaluator agent, by design.** There is no
> `L1-design-data-architect-evaluator`. The real downstream checks are the
> Phase 2.25 human gate (Platform Lead signs the Cycle 0 exit test) and
> `gr-L1-architecture-conformance`, which evaluates the `DAT-C*` checks this
> agent writes. The prompt's Reflection block is the only automated gate
> before four downstream agents read `data-architecture.md`, so these gates
> are the self-check's own checklist.

## Quality Gates
- [ ] Every entity in the FSA's `APP-3` aggregate model appears **exactly once** in `DAT-1.1`, with exactly one owning context — and every context named exists in `APP-1`. A context owning no core entity is named as owning none, not omitted
- [ ] No entity has two writers. Where two contexts both appeared to need write access, the case was raised as an `ownership_ambiguity` open question against the FSA's `APP-1` boundaries — never resolved by permitting a second writer
- [ ] `DAT-3.2` covers the same entity set as `DAT-1.1`, same ids and same order, and every row carries classification **and** retention **and** residency — the three together, because that is what `PRIN-06-C1` checks
- [ ] Every retention period, residency region and staleness budget is traceable to the PRD's regulatory posture, `kb-L1-enterprise-security § ES3`/`ES9`, or a `REQ-DAT-*` demand — or it is the literal `PENDING` with a `DAT-PEND-nn` trigger. There is no third category
- [ ] Classification for an entity is identical in `DAT-1.1` and `DAT-3.2` — the two tables disagreeing is exactly the drift the register exists to prevent
- [ ] Every `REQ-DAT-*` demand, every `CON-*` binding `DAT`, and every applied principle has a `DAT-7` traceability row; an unanswered demand appears in `open_questions` rather than being given a hopeful row
- [ ] Every `PENDING` anywhere in the document has a matching `DAT-8` row with a **trigger condition** (not a date), and every `DAT-8` row is referenced from the section it defers
- [ ] `DAT-9` checks are machine-evaluable expressions, not prose, and cover at minimum: one writer per entity, no unregistered replication, protected data has classification+retention+residency
- [ ] The analytical plane was decided — `REQUIRED`, or `NOT PRESENT`/`PENDING` **with trigger conditions**. A plane was not created because it may eventually be useful, and the deferral was not left as a silence
- [ ] Any technology named (operational plane, object store) was checked against `PRIN-07` — lifecycle status not `contain`/`retire` — and the check's outcome is stated
- [ ] No physical schema leaked in: no `CREATE TABLE`, no column types, no indexes, no ORM classes. That is service HLD/LLD, one phase later
- [ ] Where `binding-principles.json` was absent, § 4 says so and names FSA § 4 as the source — the whole catalogue was not applied as if every principle were `MANDATORY`, nor skipped as if none were

## Scores (>= threshold to pass)
| Evaluator | >= | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every entity, context, demand id and constraint id traces to the FSA or PRD verbatim |
| Hallucination | <= 0.10 | No entity, retention period, residency region, staleness budget or event present that no cited source supports |
| Consistency | 0.90 | `DAT-1.1` and `DAT-3.2` agree on entity set, order and classification; no section contradicts another on ownership |
| Relevance | 0.85 | Usable as-is by integration architect, platform architect, baseline generator and the testing seed agents without re-deriving ownership |
| Reasoning quality | 0.80 | Every `reasoning` explains which invariant the owning context protects, not what the entity is for |
| Citation completeness | 0.95 | Every ownership assignment and every non-`PENDING` governance value carries a specific, checkable source |
| Traceability completeness | 1.00 | `REQ-DAT-*` and `DAT`-binding `CON-*` coverage is total — binary, no partial credit |

## Reflection Checklist
- [ ] Entity names, context names and `REQ`/`CON` ids were carried from the FSA **verbatim** — never renamed, renumbered or tidied
- [ ] Ownership was assigned to a bounded context, never to a team, a service name or a database
- [ ] `PENDING` values were left `PENDING` — no plausible period, no default region, no hedged invention ("approximately", "typically", "industry-standard")
- [ ] Every `x`-marked prohibition in `DAT-1.b` is expressed as a concrete forbidden shape for *this* product, not a generic rule
- [ ] `DAT-6` being empty was written as "None at Cycle 0" plus the registration rule — an empty register is correct, an absent section is not
- [ ] Text diagrams are plain ASCII in fenced `text` blocks, readable in a terminal, a diff and a PR review
- [ ] No `*_summary` field in `items` silently contains the full artifact text instead of a distillation

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
