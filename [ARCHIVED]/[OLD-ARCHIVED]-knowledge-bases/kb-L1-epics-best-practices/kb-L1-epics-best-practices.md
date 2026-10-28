# Best Practices for Composing Epics

---

## 1. Structuring Epics Around Business Capabilities (ref: PM-BP-011)

**Best Practices:**
- Name and scope epics by the business outcome they deliver, not the technology used to deliver them
- Ask: "What can the business do after this epic that it couldn't do before?" — that's your epic title
- One epic = one cohesive business capability or a tightly related set of capabilities
- Avoid epics scoped to a single technical layer (e.g., "Build Payment API" or "Create Database Schema") — these are features, not epics
- Epics should be understandable by business stakeholders without technical translation

**Naming Convention:**
> [Business Action] — [Business Context/Scope]

**Good Epic Titles:**
- "Digital Payments Modernization — Domestic Fund Transfers"
- "Customer Onboarding — Digital KYC for Retail Accounts"
- "Lending Origination — Personal Loan Application and Decisioning"
- "Regulatory Reporting — Automated AML Transaction Monitoring"
- "Treasury Operations — Real-Time FX Rate Management"

**Bad Epic Titles:**
- "Build Payment Microservice" (technical component, not business capability)
- "Database Migration to PostgreSQL" (infrastructure task, not business outcome)
- "API Gateway Implementation" (technical enabler, not business value)
- "Sprint 5 Work" (time-based, not capability-based)

**Decomposition Guide:**

| If the epic... | Then... |
|---|---|
| Spans more than 3 months | Split by business capability or customer journey phase |
| Covers multiple business domains | Split into domain-specific epics |
| Has independent value streams | Split so each epic delivers standalone value |
| Has mixed risk categories | Consider splitting high-risk from low-risk capabilities |
| Serves different user personas | Consider splitting by persona if journeys diverge significantly |

**Business Capability Mapping:**
- List the specific business capabilities the epic enables (not technical features)
- Each capability should be independently valuable or a necessary enabler for another capability
- Capabilities should map to the organization's business capability model if one exists

---

## 2. Including Compliance Checkpoints (ref: PM-BP-012)

**Best Practices:**
- Embed compliance gates into the epic lifecycle — don't treat compliance as a final hurdle
- Identify which checkpoints are required based on epic scope (data sensitivity, regulatory linkage, risk category)
- Schedule checkpoints in the delivery plan with specific dates and owners
- Checkpoint failures must block progression — they're gates, not suggestions
- Document checkpoint outcomes (approved, conditionally approved, rejected) with rationale

**Checkpoint Timing:**

| Phase | Checkpoints | Purpose |
|---|---|---|
| **Inception** | Privacy Impact Assessment, Regulatory Impact Assessment, Data Classification Review | Identify compliance obligations before design begins |
| **Design** | Security Architecture Review, Compliance Requirements Review | Ensure design satisfies compliance obligations |
| **Development** | Ongoing SAST/SCA scanning, Code review for compliance controls | Catch compliance issues during build |
| **Testing** | Compliance Test Plan Review, Security Test Results Review | Verify compliance controls work as designed |
| **Pre-Production** | Compliance Sign-Off, Security Sign-Off | Final gate before go-live |
| **Post-Deployment** | Post-Deployment Compliance Verification | Confirm compliance in production environment |

**When Each Checkpoint Is Required:**

| Checkpoint | Always | If PII | If Regulated | If Restricted Data | If High Risk |
|---|---|---|---|---|---|
| Data Classification Review | ✅ | ✅ | ✅ | ✅ | ✅ |
| Privacy Impact Assessment | — | ✅ | — | ✅ | — |
| Regulatory Impact Assessment | — | — | ✅ | — | ✅ |
| Security Architecture Review | — | — | — | ✅ | ✅ |
| Compliance Test Plan Review | — | — | ✅ | ✅ | — |
| Security Test Results Review | ✅ | ✅ | ✅ | ✅ | ✅ |
| Compliance Sign-Off | — | — | ✅ | ✅ | ✅ |
| Post-Deployment Verification | — | — | ✅ | ✅ | — |

**Common Mistakes:**
- Treating compliance as a single final gate — issues found late are expensive to fix
- Not assigning checkpoint owners — checkpoints without owners don't happen
- Conditional approvals without tracking — conditions must be tracked to closure
- Skipping post-deployment verification — production behavior may differ from testing

---

## 3. Defining Acceptance Criteria Including Regulatory Requirements (ref: PM-BP-013)

**Best Practices:**
- Epic acceptance criteria must cover both business outcomes and regulatory obligations
- Separate business acceptance criteria from regulatory acceptance criteria for clarity
- Every regulatory requirement linked to the epic must have a corresponding acceptance criterion
- Acceptance criteria must be specific, measurable, and testable — cite regulation articles
- Include evidence requirements — what proof demonstrates the criterion is met

**Business Acceptance Criteria Pattern:**
```
Given [business context],
When [epic capability is used],
Then [measurable business outcome is achieved].
```

**Regulatory Acceptance Criteria Pattern:**
```
Given [regulatory obligation from Article X],
When [regulated activity occurs],
Then [specific compliance behavior is demonstrated]
  AND [evidence is generated and retained].
```

**Banking Regulatory Acceptance Criteria Examples:**

| Regulation | Acceptance Criterion |
|---|---|
| PSD2 Art. 97 | All payment transactions require Strong Customer Authentication with two independent factors; SCA bypass only for exemptions defined in Art. 10-18 of RTS |
| GDPR Art. 6 | All personal data processing has a documented legal basis; consent is obtained before optional processing; legal basis is recorded in processing register |
| GDPR Art. 17 | Customer erasure requests are processed within 30 days; downstream processors notified; audit trail generated; AML-exempt data retained with documented legal basis |
| AML Directive | Transactions ≥ $10,000 automatically generate CTR; suspicious patterns trigger alert within 5 minutes; SAR filed within 30 days of confirmed suspicion |
| PCI-DSS Req 3 | Card data (PAN) encrypted with AES-256 at rest; CVV/PIN never stored post-authorization; tokenization used in all non-production environments |
| SOX Sec 404 | All financial calculations have dual-control validation; audit trail captures every modification; segregation of duties enforced |
| DORA Art. 11 | ICT business continuity plan tested quarterly; RTO/RPO met during DR test; incident communication procedures validated |

**Definition of Done for Epics:**
The Definition of Done is the comprehensive checklist that must all be true. It should include:

| Category | DoD Items |
|---|---|
| Development | All features developed, code-reviewed, merged to main branch |
| Quality | Unit test coverage ≥ 80%, integration tests passing, no critical defects open |
| Security | SAST/DAST/SCA scans passed — zero critical/high findings |
| Performance | Performance tests passed against NFR targets |
| Compliance | All compliance checkpoints passed, compliance sign-off obtained |
| Audit | Audit trail verified — all defined events logged correctly |
| DR/BCP | DR failover tested for Tier 1 capabilities, recovery validated |
| Documentation | API docs, runbooks, architecture decision records updated |
| Deployment | Deployed to production, monitoring and alerting active |
| Acceptance | Business acceptance criteria met, regulatory acceptance criteria met |

---

## 4. Mapping Epics to Risk Categories (ref: PM-BP-014)

**Best Practices:**
- Assess every epic against all six risk categories: Operational, Credit, Market, Compliance, Reputational, Technology
- An epic can map to multiple risk categories — identify the primary and secondary risks
- Use Impact × Likelihood matrix to determine risk rating
- Define specific mitigation actions for each identified risk — not generic statements
- Risk assessment must be reviewed when epic scope changes
- High-risk epics require additional stakeholder sign-off and more frequent checkpoints

**Risk Assessment Matrix:**

|  | **Low Likelihood** | **Medium Likelihood** | **High Likelihood** |
|---|---|---|---|
| **High Impact** | Medium Risk | High Risk | Critical Risk |
| **Medium Impact** | Low Risk | Medium Risk | High Risk |
| **Low Impact** | Low Risk | Low Risk | Medium Risk |

**Risk-Driven Epic Planning:**

| Risk Rating | Additional Requirements |
|---|---|
| **Critical** | Executive sponsor required; weekly risk review; all compliance checkpoints mandatory; enhanced testing (pen test, chaos engineering); DR Tier 1 |
| **High** | Business owner + compliance sign-off; bi-weekly risk review; security architecture review mandatory; performance and DR testing required |
| **Medium** | Standard compliance checkpoints; monthly risk review; standard testing |
| **Low** | Standard process; risk review at epic completion |

**Banking-Specific Risk Indicators:**

| Risk Signal | Risk Category | Action |
|---|---|---|
| Epic involves money movement | Operational + Compliance | Fraud screening, transaction limits, MFA, full audit trail |
| Epic involves customer PII | Compliance + Reputational | PIA, encryption, access control, breach notification readiness |
| Epic involves credit decisions | Credit + Compliance | Model validation, dual approval, regulatory reporting |
| Epic involves market data/pricing | Market + Operational | Real-time validation, reconciliation, fallback pricing |
| Epic involves third-party integration | Technology + Operational | Vendor security assessment, SLA monitoring, circuit breakers |
| Epic involves regulatory reporting | Compliance | Data quality checks, automated validation, audit trail |
| Epic is customer-facing | Reputational + Operational | Performance testing, accessibility, UX review, monitoring |
| Epic involves legacy system changes | Technology + Operational | Regression testing, rollback plan, extended monitoring |

**Risk Mitigation Patterns:**

| Risk Category | Common Mitigations |
|---|---|
| Operational | Automation, monitoring, alerting, DR/BCP, runbooks, circuit breakers |
| Credit | Validation rules, dual approval, model backtesting, limit management |
| Market | Real-time data validation, reconciliation, hedging, fallback mechanisms |
| Compliance | Compliance checkpoints, audit trails, automated reporting, legal review |
| Reputational | Security controls, performance testing, UX review, incident response plan |
| Technology | Architecture review, tech debt reduction, patching, vendor diversification |

---

## 5. Writing the Business Value Statement

**Best Practices:**
- Quantify the value wherever possible — revenue, cost savings, risk reduction, customer metrics
- Link to strategic objectives or OKRs
- Include both tangible (measurable) and intangible (strategic) value
- State the cost of not doing this epic (opportunity cost, regulatory penalty, competitive disadvantage)

**Formula:**
> This epic will [deliver/enable/reduce/improve] [specific outcome] for [target users], resulting in [quantified benefit]. Without this, [consequence of inaction].

**Good Example:**
> This epic will enable retail customers to initiate domestic fund transfers via digital channels, reducing branch transaction volume by 40% (saving $2M/year in operational costs) and improving customer satisfaction (target NPS +15). Without this, we risk losing 15% of digital-first customers to competitors and face PSD2 non-compliance penalties.

**Bad Example:**
> This epic will modernize our payment system.

---

## 6. Scoping Epics Correctly

**Best Practices:**
- Explicitly define what's in scope and what's out of scope — ambiguity causes scope creep
- Out-of-scope items should reference the epic where they will be addressed
- Scope should be achievable within 3 months (max) — split larger initiatives
- Include non-functional scope (performance, security, compliance, DR) explicitly — these are often forgotten
- Validate scope with all stakeholders before development begins

**Scope Checklist:**

| Scope Dimension | Questions to Answer |
|---|---|
| Functional | What capabilities are delivered? What user journeys are covered? |
| Channels | Which channels? (Mobile, web, branch, API, batch) |
| User segments | Which customer segments? (Retail, premium, corporate) |
| Data | What data is created, read, updated, deleted? |
| Integrations | Which systems are integrated? |
| Non-functional | Performance targets, availability, scalability? |
| Security | Authentication, authorization, encryption requirements? |
| Compliance | Which regulations apply? What evidence is needed? |
| DR/BCP | Recovery tier? Degraded mode behavior? |
| Geography | Which markets/jurisdictions? |

---

## 7. Managing Epic Dependencies

**Best Practices:**
- Identify dependencies early — they are the #1 cause of epic delays in banking
- Classify dependencies: hard (blocking) vs. soft (can work around)
- For each dependency, identify: what's needed, from whom, by when, and the fallback if delayed
- Track dependencies actively — review weekly for high-risk epics
- Design for dependency failure — what happens if a dependency is late or unavailable

**Common Banking Epic Dependencies:**

| Dependency Type | Examples | Mitigation |
|---|---|---|
| Core banking system | API availability, data model changes | Early engagement, API contract-first, mock services |
| Regulatory approval | License, product approval, compliance sign-off | Early submission, parallel workstreams, regulatory liaison |
| Third-party vendor | Integration readiness, SLA commitment | Vendor management, contract SLAs, fallback options |
| Infrastructure | Environment provisioning, network configuration | IaC automation, early provisioning, shared services |
| Other epics | Shared capabilities (auth, notifications) | Dependency mapping, priority alignment, interface contracts |
| Data migration | Legacy data transformation, quality remediation | Early data profiling, parallel migration, rollback plan |

---

## 8. Success Metrics & KPIs

**Best Practices:**
- Define success metrics before development — they guide design decisions
- Include leading indicators (adoption rate, usage patterns) and lagging indicators (revenue, cost savings)
- Set specific targets with timeframes (e.g., "60% adoption within 3 months")
- Include both business metrics and technical metrics
- Plan how metrics will be measured — instrumentation must be part of the epic scope

**Banking Epic Metrics Framework:**

| Category | Metrics | Example Targets |
|---|---|---|
| Adoption | Feature adoption rate, active users, transaction volume | 60% adoption in 3 months |
| Business | Revenue impact, cost reduction, process efficiency | $2M/year cost savings |
| Customer | NPS, CSAT, task completion rate, support ticket reduction | NPS +15, support tickets -30% |
| Quality | Defect rate, incident count, availability | < 0.1% error rate, zero P1 incidents |
| Compliance | Audit findings, compliance test pass rate, regulatory reporting accuracy | Zero findings, 100% pass rate |
| Performance | Response time, throughput, availability | p95 < 500ms, 99.95% uptime |

---

## 9. Common Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Technical epics ("Build API Gateway") | No business value articulated, hard to prioritize | Reframe around business capability delivered |
| Mega-epics (> 3 months) | Delayed value delivery, scope creep, stale requirements | Split by capability, journey phase, or user segment |
| No compliance checkpoints | Compliance issues found late, expensive rework | Embed checkpoints from inception |
| Vague acceptance criteria | Endless debate on "done", scope creep | Specific, measurable, regulation-linked criteria |
| No risk assessment | Surprises during delivery, unmitigated risks | Assess all 6 risk categories upfront |
| Missing out-of-scope | Scope creep, unplanned work | Explicitly state what's excluded |
| No Definition of Done | Inconsistent quality, missing compliance evidence | Comprehensive DoD checklist |
| Business value not quantified | Hard to prioritize, hard to measure success | Quantify value and cost of inaction |
| Dependencies not tracked | Delays, blocked teams, missed deadlines | Identify, classify, and track weekly |
| Success metrics defined post-delivery | Can't measure impact, can't prove value | Define metrics and instrumentation upfront |
| Single risk category | Incomplete risk picture | Assess against all 6 categories |
| Compliance as afterthought | Failed audits, regulatory penalties | Compliance-by-design from epic inception |
