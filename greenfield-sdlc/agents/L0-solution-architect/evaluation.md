# Evaluation — L0-solution-architect

> **Self-check and evaluator rubric.** The real gates are human: the Solution
> Architect signs Sections 2–7 and 9–12, and the Platform Lead signs
> Section 8 and the Cycle 0 exit proof. The prompt's Reflection block runs
> these gates before delivery, and L0-solution-architect-evaluator
> re-runs them independently. `gr-L0-architecture-conformance` later checks
> Section 10 and "Constraints honoured" mechanically, but it is not built.
> The reference rendering is `examples/artifacts/solution-architecture.md`.

## Quality Gates

**Content boundary (BLOCKING)**
- [ ] No request or response schema, OpenAPI fragment, DDL statement or IaC. Indicative operation paths appear only in the INT-2 catalogue; schema, table, topic and consumer-group names are allowed; the DAT-2 envelope JSON is required
- [ ] The target is quoted, never amended. Target ids are verbatim (including its `R-`, `QA-`, `DRV-` and `OI-` keys); only `APL-`, `DAT-1.x`, `SN-`, `FLOW-`, `SD-`, `RK-`, `AS-` and `PEND-` keys are minted, and `QA-` only when the target defines none. No `SEC-` or `TB-` id is minted

**Target status (BLOCKING)**
- [ ] The target is approved: status line **Approved** and the Enterprise Architect's approval row signed and dated (older layout: front matter `status: APPROVED`). Otherwise the output is TARGET_NOT_APPROVED, or, on a dry run, the document carries the draft-target line and gate_ready is false

**Completeness (BLOCKING)**
- [ ] APL-1 has every APP-2 component, plus any platform component the target names
- [ ] DAT-1 has every entity in the target's APP-1 ownership lists exactly once, in context order; DAT-3 has every class DAT-1 uses
- [ ] INT-1 has every request and event in the target's interaction table (R-nn; older layout: APP-2.3 E-nn) exactly once
- [ ] Every registered analytical read model the target names has a DAT-4 register row; every value the target says is captured has a snapshot register row
- [ ] Section 10 has every target `REQ-*` exactly once; every **Not yet built** says why (band, first change that needs it, or a PEND). No REQ is **Met** while it waits on a **Not present** PLT-6 capability or a "To be set" value
- [ ] "Constraints honoured" has every target `CON-*`
- [ ] Every capability the target demands (its `REQ-PLT-*`; older layout: § 4.2 classes) has a PLT-6 row; every **Available** row appears in the Cycle 0 exit proof
- [ ] Every target `SEC-*` and any `TB-*` has a Section 9 row (**Not yet built** is valid; absence is not)

**Grounding (BLOCKING)**
- [ ] Every technology carries a source, lifecycle and status tag. None is `retire`. Every `contain` has an exception. Every `unverified` product is **Requires validation**
- [ ] Nothing is **Approved** unless EA11 is APPROVED and lists it for the chosen cloud, or an estate mandate requires it; if EA11 is missing or not APPROVED, the line under the subtitle says so
- [ ] Every retention, residency, timeout, availability, recovery and alert value traces to a target budget, a supplied input, a KB section or an arithmetic split of a parent budget, or reads "To be set" with a PEND row. A proposed figure states its basis and is **Requires validation**
- [ ] Every residency satisfies the target's own residency demand (for example "resident in the EU"), which binds even where the group residency rule is looser; if no approved region of the chosen cloud satisfies it, a PEND row blocks approval
- [ ] That residency gap covers every place personal data is held (every entity naming or describing a person, snapshots copying it, event payloads, logs, backups), and the region is **Requires validation** wherever it is stated for that data, including the Section 12 region decision. The PEND is owned by the Enterprise Architect with Data Protection, and never offers hosting one context on another cloud
- [ ] Every tool the pipeline or the Cycle 0 exit proof uses is named as a specific product; one the catalogue does not list is **Requires validation** with a PEND row that blocks the Cycle 0 exit
- [ ] Every candidate (PLT-6, SD rows) is a specific product on the chosen cloud or cloud-neutral; when the catalogue has none for that cloud the row reads "No catalogued candidate", lifecycle unverified. Another cloud's product is never a candidate
- [ ] Every classification the target states for an entity is kept (for example tax rates classified Financial)
- [ ] Every retention is a sourced period that applies to the entities its source names, or "To be set" with a PEND row. A description ("operational", "no statutory minimum", "until account closure") is not a retention
- [ ] Every availability figure is the target's, or a group tier whose condition actually holds for that component's records (99.9% for active regulatory defence, 99.5% for audit records, best-effort only for data-warehouse reporting pipelines); otherwise "To be set". Each component has exactly one availability row
- [ ] The database layout reads the same in Sections 2, 5, 8 and 12
- [ ] Every DAT-1 row has Personal data decided (**Yes** when it names or describes a person, references a buyer or producer, or holds an address or destination); every **Yes** row's residency satisfies the target's demand or is **Requires validation** under the residency PEND, which lists every Yes entity
- [ ] Every Available PLT-6 row names the Cycle 0 test it meets (exit proof from the fixed list, high lead time with its source, cross-context policy, band First). Adding a capability to the document's own exit proof never qualifies it; a capability decided to make a demand Met is out of scope
- [ ] Every PLT-3 pipeline stage names its tool, including dependency, vulnerability and secret scanning
- [ ] Every topic retention is a transport replay window or "To be set"; no topic cites an entity's retention demand
- [ ] Every invariant with a bypassable mechanism has a second one that does not depend on database privileges or the application, and the step that writes it is named. Two mechanisms an administrator can both undo count as one
- [ ] No degraded mode shows a remembered, cached or last-known value owned by another context
- [ ] Every event consumer is named by a target interaction; no context consumes its own event; an internal projection is built inside its context
- [ ] Every snapshot sits on the table whose row it describes (a per-listing price on the order line, not the order header)
- [ ] No Section 12 basis contradicts an open item or risk in the document
- [ ] Every PEND row has a condition in "Resolved when", never a date; PEND ids run without gaps, and every PEND that blocks approval or the Cycle 0 exit comes before every PEND that blocks nothing
- [ ] Every synchronous INT-1 decision is permitted by a target CON exception or DEV, or is carried in a PEND row named in "Permitted by"
- [ ] Every snapshot is captured by the context that holds the immutable record, over an INT-1 edge; a target count with no names is a PEND row, never invented entries
- [ ] Only what Cycle 0 needs was decided (band First where the target gives bands, High lead time, exit proof, cross-context policy). Everything else is **Not present** in PLT-6 with its band or "first change that needs it"; a component the target says is not yet realised, or one that depends on a Not present capability, is **Not yet built**. A target open item about when a context is scheduled is read as delivery planning, not job-scheduling design
- [ ] A demand that needs an event raised on a timer or a date (an expiry warning, a statement run) waits on scheduled jobs, and is **Not yet built** while they are Not present

**Style (BLOCKING)**
- [ ] The twelve numbered sections, Document Control and the appendix appear with their fixed headings and italic subtitles, in order
- [ ] No narration about the agent, its run or its inputs ("this document cannot", "per instructions", "cannot be invented", "was not supplied", "appears above exactly once", input parameter names such as `hosting_cloud`, upload names, tool names)
- [ ] No front matter, input-source table, gate banner or self-check record in the document
- [ ] No KB section code (EA11, ES1–ES10, FD…, PRIN-…) in prose or table cells, including parenthetical citations; sources are named in words
- [ ] Table cells hold one clause, at most 25 words; first columns are bold; status tags use the fixed vocabulary
- [ ] Every figure is a Mermaid block with a `***FIGURE n** · …*` caption; no image file is referenced
- [ ] Each open issue is stated in full once, in Section 11, and cited by key elsewhere

## Scores (>= threshold to pass)
| Evaluator | >= | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every entity, edge, demand, constraint and budget matches the target verbatim |
| Hallucination | <= 0.10 | No technology, region, number, module name or lifecycle status that neither EA11, the target nor the PRD supports |
| Consistency | 0.90 | DAT-1 agrees with DAT-3; INT-1 agrees with INT-2 and INT-3; PLT-6 agrees with Section 10; the technology view, PLT-1 and Section 12 name the same decisions |
| Relevance | 0.85 | The impact assessor can answer "do we have this?" from PLT-6 alone; HLD and API-spec agents can start from APL-2, DAT-1 and INT-1 without re-deriving |
| Reasoning quality | 0.80 | Each rejected alternative names the budget, lifecycle or estate rule it lost on |
| Citation completeness | 0.95 | Every realising section names the `REQ-*` it satisfies and the `CON-*` / `INV-*` it realises; every technology has a source |
| Traceability completeness | 1.00 | REQ → Section 10 and CON → "Constraints honoured" coverage is total. Binary |
| Readability | 0.85 | Reads as written by the owning architect: declarative, one idea per sentence, a callout per section stating the takeaway |

## Reflection Checklist
- [ ] PROPOSED technologies are never tagged **Approved**, in the document or in items
- [ ] The Cycle 0 exit proof is **Not yet proven**; the agent never certifies it
- [ ] Target open questions were checked for being answered by design before being carried as PENDs
- [ ] Estate mandates (EA9 API gateway, EA4 integration routes, ES1 external identity) were applied before any catalogue choice
- [ ] Deferred capabilities are **Not present** in PLT-6, not PEND rows — they are resolved by the change that first needs them
- [ ] Sections 2, 3, 11 and 12 restate decisions made elsewhere and introduce none
- [ ] No `*_summary` field in items silently contains the full artifact text

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Record honest results in items.self_check → 5. Deliver final only
