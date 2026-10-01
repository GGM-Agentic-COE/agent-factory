# kb-L1-enterprise-architecture

**Domain covered:** Thornbury Foods Group's existing technology landscape —
the fictional parent enterprise building HarvestLink as a new digital
product, not from a blank slate.

**Why it exists — and why it was initially left unbuilt:** an earlier pass
on this project scoped HarvestLink as a pure greenfield build with no
parent organisation, on the reasoning that "greenfield" meant no existing
systems to document — so this KB was correctly out of scope (nothing real
to put in it without fabricating an organisation). That framing was
incomplete: greenfield describes the *product*, not necessarily the
*enterprise* — a genuinely new application is very often built inside an
already-established company with its own existing systems, and assessing
impact against that landscape is exactly `L1-planning-impact-assessor`'s
job. This KB supplies that landscape for the reference scenario, so
impact-assessment.md's existing-system checks are actually exercised
against something real, not "CMDB returned no entries" every time.

**Who uses it?** `L1-planning-impact-assessor`, `L1-planning-dependency-mapper`,
and `L1-requirements-nfr-classifier` (for SLA-tier context, not as a
substitute for confirming HarvestLink's own tier).

**What does it cover?**
- Organisation overview and existing technology stack
- Per-system integration relevance to HarvestLink — what it touches, what
  it deliberately does not, and why (the table impact-assessor should
  check against directly)
- Architecture patterns/principles new digital products must follow
- Service domains, support-tier SLAs, infrastructure scale
- Known technical debt and roadmap items that could affect future
  HarvestLink integration decisions
- Governance: when a new HarvestLink component needs Enterprise
  Architecture review vs. when the product unit has autonomy

**How to use:** attached automatically to the agents listed in `spec.yaml`.
`impact-assessor` should check every proposed component against this KB's
integration-relevance table (EA3) before writing "no existing internal
systems affected" — that claim is only true for components that
genuinely have no touch point here.

**Sources:** Illustrative — invented for this reference scenario, not a
real organisation's actual architecture.

**Update frequency:** Quarterly — integration boundaries and the
technology stack change faster than organisational structure.

**Quality bar:** Every system listed must state explicitly whether
HarvestLink touches it and why/why not — a system with no stated relevance
to HarvestLink shouldn't be listed at all; this isn't a general company
wiki, it's grounding for impact assessment specifically.

**Owner:** Agentic-AI CoE

**Consumers:** `L1-planning-impact-assessor`, `L1-planning-dependency-mapper`,
`L1-requirements-nfr-classifier`

---

## v1.1.0 — the binding principle catalogue (`content/binding-principles.md`)

**What was added.** A second content document holding the enterprise's
architecture principle catalogue: `PRIN-01`..`PRIN-08` in the standard
nine-field form (statement, business rationale, architectural implications,
scope, evidence of compliance, trade-offs, exception conditions, owner,
review cadence), each with machine-evaluable conformance checks and the FSA
hooks it seeds, plus the precedence rules (`PREC-01`..`PREC-04`), the
exception-handling contract and the outcome metrics.

**Why it is here and not in its own KB.** A principle catalogue *is*
enterprise architecture knowledge, on the same review cadence and with the
same owner as the landscape document. Splitting it into `kb-L1-binding-principles`
would have meant a second KB attachment on every agent that already needs
this one, for content that is never useful without it — a principle with no
estate to apply it to decides nothing.

**Why it is a separate FILE inside this KB.** The two documents change for
different reasons and at different rates: the landscape changes when a
system is replaced (quarterly-ish), the catalogue when the enterprise changes
its mind (annual + event-driven). Chunking is by section, so an agent that
needs only `PRIN-02` retrieves only `PRIN-02` either way.

**The boundary that matters.** This KB holds the **catalogue** — what the
enterprise believes. It does **not** hold the **resolution** — whether and
how hard a principle binds a specific product. That lives in a
`binding-principles.json` authored against
[`binding-principles.template.json`](../../../binding-principles.template.json)
and supplied to an agent as an input artifact per run. Baking one product's
resolution into a KB would make that product's exceptions read as enterprise
policy to every other product. `BP11` is the contract for reading the
resolution file, including what to do when none is supplied (fall back to the
FSA § 4 `PRIN` rows, and say so in the output).

**New consumers.** `L1-design-platform-architect`, `L1-design-data-architect`
and `L1-design-integration-architect` — the Phase 2.25 Cycle 0 viewpoint
architects. `BP8`'s standing note is aimed squarely at them: `PRIN-07`
resolved `NOT_APPLICABLE` at the FSA level is still `MANDATORY` for the
Platform and Data viewpoint documents, because those are the first artifacts
in the pipeline permitted to name a product — and therefore the first that
can violate it.
