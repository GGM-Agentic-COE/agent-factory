<!--
kb-L1-nfr-classification-taxonomy · content · nfr-classification-taxonomy.md
Layer: L1 (enterprise, domain-agnostic). Consumed by:
L1-requirements-nfr-classifier. Micro-KB content rules apply: max 1
line/bullet, max 15 words, no explanations, numbers not words, annotated
with target category. This KB describes HOW to classify, not WHAT the
numbers are — it never asserts a default threshold. A boundary condition
is a real number ONLY if requirements.md or vision.md (including its
Regulatory Posture section) states or directly implies it; otherwise it MUST read "TBD — needs
stakeholder input" per nfr-spec.template.md. Any example value below is a
FORM to fill in from a grounded source, never a default to assert.
-->

# NFR Classification Taxonomy (Cross-Domain)

Use to classify a functional requirement's non-functional boundary
conditions before marking any of the six categories "not applicable."

## The Six Categories
- Performance → how fast/responsive the capability must be (→ Category: Performance)
- Security → what must be protected, and from whom (→ Category: Security)
- Scalability → what volume/growth the capability must sustain (→ Category: Scalability)
- Availability → what uptime/resilience the capability requires (→ Category: Availability)
- Compliance → what regulation/policy the capability must satisfy (→ Category: Compliance)
- Usability → what a user must be able to do without confusion (→ Category: Usability)

## Performance
- Ask: does this FR have a latency, throughput, or response-time expectation? (→ Category: Performance)
- Form: "{{percentile}} {{operation}} under {{grounded number}}{{unit}}" (→ Category: Performance)
- Common percentiles: P50 (typical), P95 (near-worst-case), P99 (tail) (→ Category: Performance)
- No stated/implied number → "TBD — needs stakeholder input", never a guess (→ Category: Performance)

## Security
- Ask: what data/action does this FR expose, and who must be excluded? (→ Category: Security)
- Form: "{{action}} must be {{server-side enforced | authenticated | encrypted}}" (→ Category: Security)
- Common concerns: authN/authZ, tamper-resistance, encryption at rest/in transit (→ Category: Security)
- A stated business rule (e.g. "server-side enforced") is grounded, not a guess (→ Category: Security)

## Scalability
- Ask: does this FR's volume grow with users, data, or time? (→ Category: Scalability)
- Form: "{{grounded volume/rate}} expected at {{grounded time horizon}}" (→ Category: Scalability)
- No stated/implied volume → "TBD — needs stakeholder input" (→ Category: Scalability)
- A pilot/cohort cap stated elsewhere IS a grounded scalability boundary (→ Category: Scalability)

## Availability
- Ask: what happens if this FR's component is down — must it still work? (→ Category: Availability)
- Form: "{{uptime target}} SLA" or "{{explicit fallback behaviour}}" (→ Category: Availability)
- No stated SLA or fallback → "TBD — needs stakeholder input" (→ Category: Availability)
- Distinguish "no SLA stated" from "no fallback behaviour defined" — both matter (→ Category: Availability)

## Compliance
- Ask: does a named regulation/policy constrain this FR? (→ Category: Compliance)
- Form: cite the specific regulation/section — never "comply with regulations" (→ Category: Compliance)
- Primary source: vision.md § Regulatory Posture's per-constraint citation, not this KB (→ Category: Compliance)
- This KB never supplies a regulation citation — it only flags when to look (→ Category: Compliance)

## Usability
- Ask: could a user misread this FR's outcome as something it isn't? (→ Category: Usability)
- Form: "{{user}} must see/receive {{explicit, unambiguous signal}}" (→ Category: Usability)
- Common concerns: silent failure, buried/optional steps, ambiguous state (→ Category: Usability)
- Usability boundary conditions are rarely numeric — a clear behaviour rule is enough (→ Category: Usability)

## When a Category Does Not Apply
- Not every FR needs all six categories — apply what's relevant, not a checklist (→ Category: Method)
- Omitting a category silently is a gap; write "No NFR categories apply" if genuinely none (→ Category: Method)
- A category applying with no known number is still applicable — mark TBD, don't omit it (→ Category: Method)

## Glossary
- P50/P95/P99 — percentile of a measured distribution (e.g. response time) (→ Glossary)
- SLA — Service Level Agreement; a committed uptime/performance target (→ Glossary)
- Blast radius — how much else breaks if this component fails (→ Glossary)
- Server-side enforced — a rule the client cannot bypass by altering its own request (→ Glossary)

---
*Last reviewed: 2026-08-07 · Review cadence: annually (this is a
classification METHOD, not a domain fact set — it changes far less
frequently than the domain/regulatory KBs it sits alongside).*
