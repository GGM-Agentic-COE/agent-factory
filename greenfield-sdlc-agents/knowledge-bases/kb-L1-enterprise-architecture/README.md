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
