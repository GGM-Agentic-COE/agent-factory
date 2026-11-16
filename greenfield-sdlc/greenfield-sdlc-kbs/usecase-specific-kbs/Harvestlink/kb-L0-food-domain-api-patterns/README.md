# kb-L0-food-domain-api-patterns

**Domain covered:** integration patterns specific to the food supply chain /
producer marketplace domain that HarvestLink operates in.

**Why it exists:** `L0-solution-architect` is domain-agnostic. This KB is
what makes its integration decisions domain-aware: which flows genuinely
cannot be asynchronous, what an evidence event is, and what regulatory
change does to contract versioning. Deploying against a different domain
replaces this KB and leaves the agent unchanged.

**Who uses it?** `L0-solution-architect` and
`L0-solution-architect-evaluator`, read from Confluence by page id
(`domain_api_patterns_kb_page_id`).

**What does it cover?**
- FD1 What is distinctive about integration in this domain
- FD2 Participant model and trust boundaries
- FD3 Canonical event taxonomy (lifecycle, evidence, movement, notification)
- FD4 The synchronous-versus-asynchronous decision table, and degraded modes
- FD5 Contract versioning under regulatory change
- FD6 Partner and file-based integration (transitional only)
- FD7 Duplicate handling, idempotency and recovery
- FD8 Integration observability in this domain
- FD9 Glossary

**What it does not cover:** product names (the approved platform catalogue,
`kb-L0-enterprise-architecture` EA11), enterprise integration routes (EA3,
EA4), and identity, residency and classification (`kb-L0-enterprise-security`).
It cites those rather than restating them.

Illustrative content for the HarvestLink reference scenario.
