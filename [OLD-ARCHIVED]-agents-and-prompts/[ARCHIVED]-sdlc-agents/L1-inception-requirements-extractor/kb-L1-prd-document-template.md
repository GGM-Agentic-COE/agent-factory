# Product Requirements Document (PRD)

> **Product:** {Product Name}
> **Version:** {1.0}
> **Status:** {Draft | In Review | Approved}
> **Owner:** {Product Owner}
> **Approved By:** {Stakeholder Name, Date}

---

## 1. Executive Summary

{2-3 paragraph overview of what this product/feature is, why it exists, and what business outcome it drives. Written for a senior stakeholder who needs context in 60 seconds.}

---

## 2. Problem Statement

### Business Problem
{What problem does this solve? Who experiences it? What is the cost of not solving it?}

### Current State
{How is this handled today? What are the pain points?}

### Desired Outcome
{What does success look like? What measurable change do we expect?}

---

## 3. Scope

### In Scope
- {Capability 1}
- {Capability 2}

### Out of Scope
- {Explicitly excluded capability 1}
- {Explicitly excluded capability 2}

### MVP Boundary
{What is the minimum viable product? What gets deferred to subsequent releases?}

---

## 4. Stakeholders & Users

| Role | Name | Responsibility |
|------|------|---------------|
| Product Owner | | Final prioritisation decisions |
| Technical Lead | | Architecture and feasibility |
| Business Sponsor | | Funding and business case |
| UX Lead | | User experience and design |

### Target Users

| Persona | Description | Primary Needs |
|---------|-------------|---------------|
| {Persona 1} | {Description} | {What they need from this product} |
| {Persona 2} | {Description} | {What they need from this product} |

---

## 5. Functional Requirements

| ID | Title | Description | Priority | User-Facing | Tags |
|----|-------|-------------|----------|-------------|------|
| FR-01 | {Title} | The system shall {description} | Must-Have | Yes/No | {tags} |
| FR-02 | {Title} | The system shall {description} | Must-Have | Yes/No | {tags} |
| FR-03 | {Title} | The system shall {description} | Should-Have | Yes/No | {tags} |

### Priority Definitions

| Priority | Definition |
|----------|-----------|
| **Must-Have** | Required for launch. Product cannot ship without this. |
| **Should-Have** | High value, expected for launch. Can be descoped with stakeholder agreement. |
| **Could-Have** | Desirable. Included if time/budget permits. |
| **Won't-Have (this release)** | Explicitly deferred to a future release. |

---

## 6. Non-Functional Requirements

| ID | Category | Title | Description | Priority |
|----|----------|-------|-------------|----------|
| NFR-01 | Performance | {Title} | {Measurable requirement with target threshold} | Must-Have |
| NFR-02 | Security | {Title} | {Measurable requirement with target threshold} | Must-Have |
| NFR-03 | Scalability | {Title} | {Measurable requirement with target threshold} | Must-Have |
| NFR-04 | Reliability | {Title} | {Measurable requirement with target threshold} | Should-Have |
| NFR-05 | Usability | {Title} | {Measurable requirement with target threshold} | Should-Have |

### NFR Categories

| Category | Covers |
|----------|--------|
| Performance | Response times, throughput, latency targets |
| Security | Auth, encryption, data protection, compliance |
| Scalability | User volumes, data growth, peak load handling |
| Reliability | Uptime SLA, failover, data consistency, DR |
| Usability | Accessibility (WCAG), device support, browser compatibility |

---

## 7. Constraints

| ID | Type | Description |
|----|------|-------------|
| C-01 | Technology | {e.g., Must use existing AWS infrastructure} |
| C-02 | Business | {e.g., Must not disrupt existing customer workflows} |
| C-03 | Regulatory | {e.g., Must comply with GDPR data residency requirements} |
| C-04 | Timeline | {e.g., Must be market-ready by Q3 2026} |

### Constraint Types

| Type | Definition |
|------|-----------|
| Technology | Platform, stack, or integration constraints imposed by existing architecture |
| Business | Commercial, operational, or organisational constraints |
| Regulatory | Legal, compliance, or industry-mandated constraints |
| Timeline | Delivery deadlines or phasing constraints |

---

## 8. Assumptions

| ID | Assumption | Needs Confirmation | Risk if Invalid |
|----|------------|-------------------|-----------------|
| A-01 | {Assumption text} | Yes/No | {Impact if this assumption proves false} |
| A-02 | {Assumption text} | Yes/No | {Impact if this assumption proves false} |

---

## 9. Dependencies

| ID | Dependency | Type | Owner | Status | Impact if Delayed |
|----|-----------|------|-------|--------|-------------------|
| D-01 | {External system / team / decision} | Internal/External | {Team} | {Green/Amber/Red} | {What happens if this isn't ready} |

---

## 10. Gaps & Open Questions

| ID | Description | Impact | Suggested Question | Status |
|----|-------------|--------|-------------------|--------|
| G-01 | {What information is missing} | {How it affects delivery} | {Question to ask stakeholder} | Open/Resolved |
| G-02 | {What information is missing} | {How it affects delivery} | {Question to ask stakeholder} | Open/Resolved |

---

## 11. User Journeys & Acceptance Criteria

### {Journey 1: e.g., Customer Enrollment}

**Preconditions:** {What must be true before this journey starts}

**Steps:**
1. {Step 1}
2. {Step 2}
3. {Step 3}

**Acceptance Criteria:**
- Given {context}, When {action}, Then {expected outcome}
- Given {context}, When {action}, Then {expected outcome}

**Edge Cases:**
- {Edge case 1 and expected behaviour}

---

## 12. Data Requirements

### Data Entities

| Entity | Key Attributes | Source | Retention |
|--------|---------------|--------|-----------|
| {Entity 1} | {attributes} | {System of record} | {Retention period} |

### Data Flows

{Description of how data moves between systems — which system produces, which consumes, sync/async, frequency}

### Data Privacy & Classification

| Data Element | Classification | PII | Encryption Required | Consent Required |
|-------------|---------------|-----|--------------------|--------------------|
| {Element} | {Public/Internal/Confidential/Restricted} | Yes/No | Yes/No | Yes/No |

---

## 13. Integration Requirements

| System | Direction | Protocol | Frequency | Purpose |
|--------|-----------|----------|-----------|---------|
| {System 1} | Inbound/Outbound/Bidirectional | REST/Event/Batch | Real-time/Daily | {Why} |

---

## 14. Release Strategy

### Phasing

| Phase | Scope | Target Date | Success Criteria |
|-------|-------|-------------|-----------------|
| MVP | {Core capabilities} | {Date} | {Measurable criteria} |
| Phase 2 | {Extended capabilities} | {Date} | {Measurable criteria} |

### Feature Flags
{Which features will be behind flags? Rollout strategy (% rollout, canary, etc.)}

### Rollback Plan
{What triggers a rollback? How is it executed? Data implications?}

---

## 15. Success Metrics

| Metric | Baseline | Target | Measurement Method |
|--------|----------|--------|-------------------|
| {e.g., Enrollment conversion rate} | {Current value} | {Target value} | {How it's measured} |
| {e.g., Points redemption rate} | {Current value} | {Target value} | {How it's measured} |

---

## 16. Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|------------|
| R-01 | {Risk description} | High/Medium/Low | High/Medium/Low | {Mitigation strategy} |

---

## 17. Glossary

| Term | Definition |
|------|-----------|
| {Term 1} | {Definition} |
| {Term 2} | {Definition} |

---

## Appendix

### A. Traceability Matrix

| Requirement | Epic | Story | Test Case |
|-------------|------|-------|-----------|
| FR-01 | EP-01 | US-001 | TC-001 |

### B. Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {Date} | {Author} | Initial draft |

### C. Sign-Off

| Stakeholder | Role | Date | Signature |
|-------------|------|------|-----------|
| | | | ☐ Approved |
