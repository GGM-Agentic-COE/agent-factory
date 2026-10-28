# kb-L1-enterprise-security

**Domain covered:** Thornbury Foods Group's established security
standards — identity, data classification, retention, audit-log tiering,
secure SDLC, incident response, third-party/external-user risk.

**Why it exists:** same reasoning as `kb-L1-enterprise-architecture`'s
README — HarvestLink is a new *product*, not a new *enterprise*, and an
already-established company has already-established security standards a
new digital product must satisfy. Assessed against a real (if illustrative)
policy set, several of `nfr-spec.md`'s open "TBD — needs stakeholder
input" boundary conditions turn out to already have an answer here — see
"What this resolves" below.

**Who uses it?** `L1-requirements-nfr-classifier` (primary), `L1-planning-impact-assessor`.

**What does it cover?**
- Identity/access boundary: employee SSO vs. external-party identity
- Data classification (Public/Internal/Confidential/Restricted)
- UK GDPR retention and right-to-erasure handling
- Audit-log availability tiering for new legally-relevant systems
- Secure-SDLC pre-launch requirements for external-facing products
- Incident response and breach-notification timelines (UK GDPR Art. 33/34)
- Third-party/external-user vetting requirements

**What this resolves (worked example continuity, back-ported 2026-08-08):**
three of `phase-1/examples/nfr-spec.md`'s (and `prd.md`'s, which composes
it) open boundary conditions have a real answer via this KB — no longer
marked TBD in either worked example:
- FR-001 (Compliance) "Attestation record retention period" → **ES3: 6 years**
- FR-003 (Availability) "Audit-log uptime SLA" → **ES4: 99.9%** (traceability records may be required for active regulatory defence)
- FR-008 (Availability) "Measurement pipeline uptime SLA" → **ES4: best-effort / Tier 3**, since it's an outbound-only reporting feed, not a compliance record

Checking this KB's identity boundary (ES1) also surfaced a genuinely new
external dependency not visible at vision/requirements stage — HarvestLink
needs its own external identity provider, since Thornbury's Azure AD is
employee-only. That finding is now reflected in
`phase-1/examples/impact-assessment.md` and as a node in
`phase-1/examples/dependency-graph.json`, where it ties with the
compliance-completeness-methodology chain for the graph's critical path —
both converge on `allergen-declaration-service`, making it a compounded
bottleneck blocked by two independent, unresolved external dependencies at
once.

**Sources:** Illustrative — invented for this reference scenario. The
6-year retention figure and 72-hour ICO notification window are modelled on
real UK practice (HMRC/Companies Act record-keeping guidance; UK GDPR
Art. 33) as plausible reference points, not verified legal advice.

**Update frequency:** Quarterly.

**Quality bar:** Every rule must be prescriptive (MUST/MUST NOT) and
specific enough that `nfr-classifier` could cite it directly as a Source
column entry — a vague "follow good security practice" line would fail
this bar.

**Owner:** Agentic-AI CoE

**Consumers:** `L1-requirements-nfr-classifier`, `L1-planning-impact-assessor`
