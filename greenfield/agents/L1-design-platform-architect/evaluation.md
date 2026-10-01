# Evaluation — L1-design-platform-architect

> **No evaluator agent, by design.** There is no
> `L1-design-platform-architect-evaluator`. The real downstream check is the
> **Cycle 0 exit test**, signed off by the Platform Lead at the Phase 2.25
> human gate — and that gate is **boolean**, not scored, because a scalar
> cannot express "the pipeline half works". The prompt's Reflection block is
> the only automated gate before `L1-testing-env-provisioner` (which cannot
> provision anything until this document exists) and
> `L1-planning-impact-assessor` (which trusts `PLT-6` mechanically) read it.

## Quality Gates
- [ ] `PLT-6` has a row for **every** capability class implied by a `REQ-PLT-*`, a `PLT`-binding `CON-*`, a `SEC-*` control, or an available sibling viewpoint — **including the ones that are `NOT PRESENT`**. A capability absent from the register cannot be looked up, and the mechanical lookup is the register's entire purpose
- [ ] **Every `AVAILABLE` status is a claim about provisioning, not about a product having been chosen.** This is the single most damaging error available to this agent: the impact assessor trusts the field mechanically, so a wrong `AVAILABLE` makes a feature's platform delta disappear from its estimate. When in doubt the status is `NOT PRESENT`
- [ ] Every product named carries a lifecycle-check outcome, and none is in `contain` or `retire` status without a recorded approved exception (`PRIN-07-C1`)
- [ ] Every bounded context in the FSA's `APP-1` has at least one independently deployable component (`PRIN-04-C2`), and no component is recorded against two contexts (`PRIN-04-C1`)
- [ ] Every availability target, RTO, RPO, capacity figure and scaling threshold traces to an `nfr-spec.md` boundary condition, a `REQ-PLT-*` demand or a KB standard (e.g. `kb-L1-enterprise-security § ES4`) — or it is `PENDING` with a `PLT-PEND-nn` trigger. "99.9% is standard for this kind of service" was not accepted; a sector norm is not a source
- [ ] No two bounded contexts share an application credential; every component has its own workload identity; secrets are rotatable without redeploying unrelated consumers (`PRIN-06-C2`, `ES10`)
- [ ] Encryption at rest and in transit is realised for exactly the classes `DAT-3` marks — the data viewpoint states the requirement, this document records the realisation, and the two do not restate each other
- [ ] Every `REQ-PLT-*` demand and every `CON-*` binding `PLT` has a traceability entry; an unanswered demand appears in `open_questions` rather than being given a hopeful row
- [ ] `PLT-16` checks are machine-evaluable expressions, not prose, and cover at minimum: isolation, technology lifecycle, deployability, classified-data protection
- [ ] `PLT-19` states **exactly six** proofs — build, deploy, run, observe, emit event, consume event — each with an honest `supported` value. A `false` is useful: it names exactly what blocks Cycle 0 exit. Five of six is not 83% ready
- [ ] Only **platform-component** HLD/LLDs were emitted. No application-service HLD was written — those belong to Phase 4's per-component design agents, and one written here would be a second, drifting source
- [ ] **No claim was made that IaC was committed to a repository.** The manifests were written to blob storage; the commit is `github-orchestrator`'s separate step
- [ ] `PRIN-07` is addressed in § 4 **even if the resolution marks it `NOT_APPLICABLE`** at FSA level — per `BP8`'s standing note, it is still `MANDATORY` for this document, which is one of the first two in the pipeline permitted to name a product

## Scores (>= threshold to pass)
| Evaluator | >= | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every context name, component name, demand id and constraint id traces to the FSA verbatim |
| Hallucination | <= 0.10 | No uptime percentage, RTO, RPO, capacity figure, product or capability present that no cited source supports |
| Consistency | 0.90 | `capability_register` and `runtime_workloads` agree; no section contradicts another on status, technology or ownership |
| Relevance | 0.85 | Usable as-is by the env provisioner and the impact assessor without re-deriving the capability set |
| Reasoning quality | 0.80 | Every `consumer_reason` says who consumes the capability and why, or why there is no current requirement |
| Citation completeness | 0.95 | Every non-`PENDING` resilience value and every security capability carries a specific, checkable source |
| Register honesty | 1.00 | Every `AVAILABLE` is provisioned-and-consumable — binary, no partial credit, because the impact assessor cannot apply judgement to it |

## Reflection Checklist
- [ ] Capability **demands** were derived before any realization was chosen — demands first, products second
- [ ] Capability rows name a capability **class** ("Relational persistence"), not a product, so the approved-platform lookup remains possible and the realization can change without the demand changing
- [ ] `NOT PRESENT` rows carry a real reason ("no current requirement" is complete and respectable; silence is not)
- [ ] Every `PENDING` has a matching `PLT-17` row with a **trigger condition** (not a date), and every `PLT-17` row is referenced from the section it defers
- [ ] Where the sibling viewpoints were absent, the document says so and records that the capability set must be re-checked before Cycle 0 closes
- [ ] Text diagrams are plain ASCII in fenced `text` blocks, readable in a terminal, a diff and a PR review
- [ ] No IaC manifest contains a literal credential, key or connection string — secrets come from the managed capability (`ES5`, `ES10`). `gr-L1-secret-scanner` is load-bearing here specifically, because this is the agent that emits IaC
- [ ] No `*_summary` field in `items` silently contains the full artifact text instead of a distillation

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
