# kb-L1-nfr-classification-taxonomy

**Domain covered:** None specific — a cross-domain method for classifying
a functional requirement's non-functional boundary conditions into the six
standard categories (performance, security, scalability, availability,
compliance, usability).

**Why it exists:** `L1-requirements-nfr-classifier` is a generic L1 agent,
reused across every domain the CoE builds for. Before it can classify a
specific FR's boundary conditions, it needs a consistent method for what
question to ask per category and what form the answer should take. This KB
is that method — genuinely domain-agnostic, so it stays at L1 rather than
being duplicated into every L2 domain KB. Same role as
`kb-L1-regulatory-frameworks-index` in Phase 0: a small, reusable,
cross-domain index, not a domain fact set.

**What it deliberately does NOT do:** supply a number, threshold, or
regulation citation. `nfr-spec.template.md`'s zero-tolerance rule requires
every boundary-condition number to trace to `requirements.md` or `vision.md`
(including its Regulatory Posture section) — this KB only tells the classifier what to look
for and how to phrase it once found; asserting a default value here would
be exactly the fabrication that rule exists to prevent.

**Sources:** Standard industry NFR taxonomy (the six categories are common
practice, not specific to any regulator or vendor) — percentile/SLA/blast-
radius terminology as commonly used across performance and reliability
engineering.

**Update frequency:** Annually, or when a new NFR category becomes standard
practice. This is a classification method, not a domain fact set, so it
changes far less often than a domain KB's quarterly/monthly cadence.

**Quality bar:** Every category must give an askable question and a
fill-in-the-blank FORM, never an example value presented as a default. If a
future edit adds a specific number anywhere in this file, that is a defect,
not an enhancement — re-read the header comment before merging.

**Owner:** Agentic-AI CoE

**Consumers:** `L1-requirements-nfr-classifier` (all domains)
