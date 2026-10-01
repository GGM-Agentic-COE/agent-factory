# kb-L2-food-domain-api-patterns

**Domain covered:** food supply chain and producer-marketplace integration —
the patterns that recur when physical goods, regulatory evidence and
externally-operated counterparties all move through the same platform.

## Why it exists

`L1-design-integration-architect` is an L1 agent: it must work for a
payments platform, a healthcare registry or a food marketplace without
modification. But an integration architecture that is unaware of its domain
produces a document that is technically valid and practically useless — it
will state "async by default, sync where justified" and leave the reader to
work out which of *their* flows genuinely cannot be async.

This KB carries that domain judgement. It is the swappable half of the pair:
replace this file for a different domain and the agent is unchanged. That
split is why the Phase 2.25 BOM row lists it alongside
`kb-L1-enterprise-architecture` rather than folding its content into the
agent's prompt.

## Who uses it?

`L1-design-integration-architect` (Phase 2.25 foundational invocation, and
the Phase 4 delta invocation).

## What does it cover?

- **FD1–FD2** — what is distinctive about this domain's integration, the
  participant model, and the trust boundary at each participant
- **FD3** — the four-kind event taxonomy (lifecycle / evidence / movement /
  notification) and the ordering, retention and replay policy each kind
  implies. The domain's most consequential modelling rule lives here:
  replaying an evidence event does not re-deliver a fact, it asserts the
  fact a second time
- **FD4** — the decision table for synchronous vs asynchronous, with the
  reason for each entry, and the domain's standing rule that an unknown
  availability, fee or eligibility is a refusal, never an optimistic
  assumption
- **FD5** — what regulatory change does to contract versioning (it arrives
  as new mandatory fields on existing evidence records, not as new
  endpoints), and why an evidence contract's version must be stored on the
  record rather than only on the message
- **FD6** — the governed transitional pattern for file-based partner
  exchange, which is not an approved style and will still be requested
- **FD7** — duplicate handling, idempotency and recovery, including why a
  deduplication key derives from the business act and never from a message
  id
- **FD8** — the two domain-specific observability signals a generic list
  misses: evidence-chain completeness and external-party contract-version
  distribution

## How to use

Attached automatically to the agents in `spec.yaml` `consumers`. The agent
reads it per `INT` section rather than wholesale — FD3 for the event
taxonomy, FD4 for the flow register's sync justifications, FD5 for the
change policy, FD7 for reliability obligations, FD8 for observability. FD6
is read only when a file-based exchange is actually proposed.

## What it deliberately does not cover

- **Enterprise integration principles.** `PRIN-03` (governed interfaces) and
  `PRIN-08` (observability) live in
  `kb-L1-enterprise-architecture § binding-principles`. This KB cites them.
- **Identity, classification, retention, residency.** Those are
  `kb-L1-enterprise-security` ES1–ES10.
- **Any product name.** No bus, no gateway, no broker. Naming a product is
  the platform viewpoint's job, and a domain KB that names one has quietly
  made a platform decision on the platform architect's behalf.

## Maintenance

- **Owner:** Agentic-AI CoE
- **Review cadence:** quarterly
- **Last reviewed:** 2026-09-22
- **Update trigger:** a new mandatory regulatory field applies to an evidence
  record, a new participant category joins, or a partner segment's
  integration capability shifts
- **Sources:** Illustrative — invented for this reference scenario, not a
  real regulator's requirements

**Quality bar:** every pattern states its *reason*. A pattern recorded
without the reason cannot be reassessed when the domain changes, and the
agent cannot cite it — it would be copying a rule rather than applying one.
