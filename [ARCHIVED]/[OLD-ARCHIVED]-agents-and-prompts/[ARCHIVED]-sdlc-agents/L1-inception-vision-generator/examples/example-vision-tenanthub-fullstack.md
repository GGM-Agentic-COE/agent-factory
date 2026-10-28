# Vision Document: TenantHub

**Version:** 1.0  
**Date:** 2026-06-20  
**Status:** Draft  
**Owner:** Product & Technology  

---

## Executive Summary

TenantHub is a greenfield full-stack tenant portal and property management platform designed for Meridian Commercial Properties, a mid-size commercial real estate company managing 47 properties across 12 markets. The platform replaces fragmented email-based workflows, legacy spreadsheets, and disconnected vendor systems with a unified digital experience for tenants, property managers, and maintenance teams. TenantHub will reduce tenant service request resolution time by 60%, eliminate manual lease administration overhead, and increase tenant retention by providing a modern self-service experience comparable to leading residential proptech portals (AppFolio, Buildium). The expected outcome is a 15-point NPS improvement within 12 months of launch and $2.1M annual operational savings through workflow automation and reduced administrative headcount needs.

---

## Business Context

### Problem Statement

- **Fragmented Communication Channels:** Tenants currently submit maintenance requests via email, phone, or in-person visits to the management office, resulting in 23% of requests being lost or duplicated and an average first-response time of 3.2 business days.
- **Manual Lease Administration:** Lease documents, rent escalation schedules, and CAM reconciliations are tracked in Excel workbooks maintained by individual property managers, leading to $340K in annual revenue leakage from missed escalations and billing errors.
- **No Tenant Self-Service:** Tenants cannot view their lease terms, payment history, or outstanding balances without contacting their property manager, generating approximately 1,200 routine inquiry calls per month across the portfolio.
- **Disconnected Maintenance Operations:** Work orders are dispatched to vendors via email with no status tracking, resulting in 31% of maintenance jobs exceeding SLA timelines with no visibility until tenant complaint.
- **Tenant Retention Blind Spots:** There is no systematic method to measure tenant satisfaction or identify at-risk tenants before lease expiration, contributing to a current 24% annual vacancy-driven revenue loss on preventable move-outs.

### Business Drivers

- **Lease Cycle Pressure:** 38% of Meridian's commercial leases (by revenue) are up for renewal in the next 18 months; improving tenant experience before renewal negotiations is time-critical.
- **Competitive Market Dynamics:** Three competing REIT operators in Meridian's core markets have launched tenant portals in the past 12 months; tenants are now explicitly requesting digital access during lease negotiations.
- **Operational Scalability:** Meridian's Board has approved acquisition of 8 additional properties in 2027, but current manual processes cannot scale without proportional headcount growth (estimated +12 FTEs at $1.4M/year).
- **Insurance and Compliance Requirements:** New property insurance underwriters require documented maintenance response SLAs and audit trails, which are impossible to produce from current email-based workflows.
- **Technology Debt Elimination:** The current "system" consists of Yardi Voyager (financials only), 14 separate Excel trackers, a shared Outlook mailbox, and paper-based vendor dispatch — none of which integrate or produce reliable reporting.

### Target Users and Stakeholders

| User Type | Count | Primary Need | Access Pattern |
|-----------|-------|--------------|----------------|
| Commercial Tenants (Primary Contacts) | ~320 | Self-service lease info, maintenance requests, payments | Web + Mobile, daily-weekly |
| Property Managers | 12 | Portfolio oversight, tenant communication, lease tracking | Web, all-day desktop use |
| Maintenance Coordinators | 6 | Work order triage, vendor dispatch, SLA tracking | Web + Tablet, field + office |
| Vendor/Contractor Teams | ~45 firms | Receive and update work orders, submit invoices | Mobile-first, on-demand |
| Finance/Accounting Team | 4 | Rent roll reconciliation, CAM billing, payment tracking | Web, weekly batch workflows |
| Executive Leadership (VP Asset Mgmt) | 3 | Portfolio KPIs, tenant health, occupancy dashboards | Web, weekly review cadence |
| Leasing Agents | 5 | Prospect tracking, lease document generation, renewals | Web, deal-cycle driven |

### Business Constraints

| # | Constraint | Implication |
|---|-----------|-------------|
| 1 | Total budget capped at $1.8M for Year 1 (build + operate) | Must prioritize ruthlessly; phased delivery required |
| 2 | MVP must be live within 6 months of project kickoff | Limits scope; requires proven technology stack, no R&D |
| 3 | Must integrate with existing Yardi Voyager 7S for financial data | Cannot replace GL system; must consume Yardi APIs or flat-file exports |
| 4 | SOC 2 Type II compliance required before handling tenant PII | Security architecture must be designed-in from Day 1; audit timeline ~4 months |
| 5 | No more than 2 hours of scheduled downtime per month | High-availability architecture required; zero-downtime deployments |
| 6 | Must support tenants across US time zones (Eastern to Pacific) | Support and monitoring coverage 6 AM–10 PM ET minimum |
| 7 | Meridian IT team is 3 people; ongoing maintenance must be manageable | Favor managed cloud services; minimize operational burden |

### Success Metrics

| Metric | Current Baseline | 6-Month Target | 12-Month Target | Measurement Method |
|--------|-----------------|----------------|-----------------|-------------------|
| Maintenance Request Resolution Time | 8.4 days avg | 4.0 days | 3.2 days | System timestamp: created → closed |
| Tenant NPS Score | +12 | +20 | +27 | Quarterly in-app survey (Delighted integration) |
| Rent Collection Timeliness (% on-time) | 71% | 85% | 92% | Payment received date vs. due date in system |
| Monthly Admin Inquiries (calls/emails) | 1,200 | 600 | 300 | Call tracking + support ticket count |
| Lease Escalation Revenue Capture | 76% of owed | 95% | 99% | Automated escalation vs. actual billed (Yardi reconciliation) |
| Tenant Portal Adoption Rate | 0% (no portal) | 65% of tenants active | 85% of tenants active | Monthly active users / total tenant contacts |
| Mean Time to First Response (maintenance) | 3.2 business days | 4 hours | 1 hour | System timestamp: created → first status update |
| Preventable Tenant Move-outs | 24% of expirations | 15% | 10% | Exit survey + renewal rate tracking |

---

## Full Scope Vision

### Product Vision Statement

TenantHub will become the central nervous system of Meridian Commercial Properties' tenant relationships — a platform where every interaction between tenant and landlord is digital, transparent, and delightful. From the moment a prospect signs a letter of intent through daily building operations and eventual lease renewal, TenantHub provides a single pane of glass that eliminates information asymmetry, automates routine administration, and transforms property management from a reactive cost center into a proactive retention engine. The platform will set a new standard for mid-market commercial real estate technology, demonstrating that enterprise-grade tenant experience doesn't require enterprise-grade budgets, and positioning Meridian as an operator of choice for tenants evaluating their next 5-10 year commitments.

### Feature Areas

#### 1. Tenant Self-Service Portal

**Description:** A responsive web application providing tenants 24/7 access to their lease information, financial history, building documents, and communication tools without needing to contact property management.

**Key Capabilities:**
- View current lease terms, key dates (expiration, renewal options, escalation schedule), and executed documents
- Access real-time account balance, payment history, and downloadable invoices/statements
- Submit and track maintenance requests with photo uploads and real-time status updates
- View building announcements, emergency notifications, and planned maintenance schedules
- Manage authorized contacts and delegate portal access to office managers or facilities staff

**User Value:** Tenants gain instant answers to routine questions, reducing frustration and building confidence that their landlord operates professionally and transparently.

---

#### 2. Maintenance & Work Order Management

**Description:** End-to-end digital workflow for maintenance requests — from tenant submission through triage, vendor dispatch, execution tracking, and tenant confirmation of completion.

**Key Capabilities:**
- Intelligent categorization and priority scoring of incoming requests (emergency/urgent/routine/cosmetic)
- Automated vendor matching based on trade category, availability, property assignment, and SLA performance history
- Real-time status tracking with automated tenant notifications at each stage transition
- Photo/video documentation at submission, during work, and at completion for audit trail
- SLA monitoring with escalation triggers when response or resolution times approach threshold

**User Value:** Tenants experience Amazon-like visibility into their request status; property managers eliminate manual dispatch coordination and gain proactive SLA management.

---

#### 3. Lease Administration & Document Management

**Description:** Centralized repository and automation engine for lease lifecycle management — from execution through amendments, escalations, options exercise, and renewal.

**Key Capabilities:**
- Structured lease data extraction and storage (rent schedules, escalation formulas, option dates, special provisions)
- Automated escalation calculations and billing triggers synced to Yardi Voyager
- Critical date alerts (60/90/120 days before options, expirations, and escalation dates)
- Version-controlled document storage with e-signature integration for amendments and renewals
- CAM reconciliation worksheet generation with tenant-facing transparency reports

**User Value:** Finance teams eliminate revenue leakage from missed escalations; tenants gain trust through transparent billing backed by accessible source documents.

---

#### 4. Communications & Notifications Engine

**Description:** Multi-channel communication platform enabling targeted, trackable messaging between property management and tenants with full audit history.

**Key Capabilities:**
- In-app messaging with read receipts and response tracking
- Automated notification workflows (maintenance updates, payment reminders, lease milestones)
- Building-wide and portfolio-wide announcement broadcasting with delivery confirmation
- Emergency notification system with SMS fallback for critical building events
- Communication history searchable by tenant, property, topic, and date range

**User Value:** Property managers replace untrackable emails with documented, auditable communication; tenants receive timely, relevant information through their preferred channel.

---

#### 5. Financial Operations & Payments

**Description:** Tenant-facing payment experience integrated with back-office accounting, enabling online rent payment, automated billing, and real-time financial visibility.

**Key Capabilities:**
- Online rent payment via ACH, wire, and credit card with configurable convenience fee pass-through
- Automated recurring payment setup with tenant-controlled scheduling
- Real-time payment posting and balance updates visible to tenants within 15 minutes
- Automated late-fee calculation and application per lease terms
- Accounts receivable aging dashboard with tenant risk scoring for property managers

**User Value:** Tenants pay rent as easily as any modern SaaS subscription; finance teams reduce collection effort and gain earlier visibility into delinquency trends.

---

#### 6. Analytics, Reporting & Tenant Health

**Description:** Portfolio-wide intelligence layer providing property managers and executives with actionable insights on operational performance, tenant satisfaction, and financial health.

**Key Capabilities:**
- Real-time operational dashboards (maintenance SLAs, occupancy rates, collection rates by property)
- Tenant health scoring combining payment behavior, request frequency, satisfaction survey data, and communication sentiment
- Predictive renewal probability model highlighting at-risk tenants 6+ months before expiration
- Automated monthly property performance reports with variance commentary
- Benchmarking across properties for operational efficiency and tenant satisfaction

**User Value:** Leadership transitions from backward-looking spreadsheet reviews to forward-looking portfolio intelligence, enabling proactive intervention before problems become vacancies.

---

### Integration Points

| # | System | Direction | Data Exchanged | Method | Criticality |
|---|--------|-----------|---------------|--------|-------------|
| 1 | Yardi Voyager 7S | Bidirectional | Tenant records, rent rolls, payment postings, GL entries, lease abstracts | REST API (Yardi API Suite) + nightly flat-file reconciliation | Critical — financial system of record |
| 2 | Stripe Connect | Outbound/Inbound | Payment intents, ACH transfers, refunds, fee calculations, payout reconciliation | Stripe API v2024-06 + webhooks | Critical — payment processing |
| 3 | DocuSign eSignature | Outbound/Inbound | Lease documents, amendment envelopes, signature status callbacks | DocuSign REST API + Connect webhooks | High — lease execution workflow |
| 4 | Twilio (SMS/Voice) | Outbound | Emergency notifications, 2FA codes, maintenance status SMS | Twilio Programmable Messaging API | High — emergency comms fallback |
| 5 | SendGrid | Outbound | Transactional emails (payment confirmations, request updates, lease alerts) | SendGrid Mail Send API v3 | High — primary notification channel |
| 6 | Building Access Control (Brivo) | Read-only | Tenant access logs, visitor management events | Brivo API (property-specific, phased rollout) | Medium — Phase 2 enhancement |
| 7 | Microsoft Entra ID (Azure AD) | Inbound | Meridian staff SSO, role provisioning, group membership | SAML 2.0 / OIDC | High — internal authentication |
| 8 | Delighted (NPS) | Bidirectional | Survey triggers, response scores, verbatim comments | REST API + webhooks | Medium — tenant health scoring input |

### User Journeys (Full Vision)

#### Journey 1: Tenant Submits Emergency Maintenance Request

1. Tenant discovers water leak in their suite at 7:30 PM (outside business hours)
2. Tenant opens TenantHub mobile app and taps "New Request" → selects "Water/Plumbing" → marks "Emergency"
3. Tenant uploads two photos of the leak and adds description: "Water coming through ceiling tiles, spreading"
4. System auto-classifies as Priority 1 (Emergency), triggers immediate SMS to on-call maintenance coordinator
5. Maintenance coordinator receives push notification, reviews photos, and dispatches pre-approved plumber (ResponseMaster Plumbing) directly from mobile interface
6. Vendor receives dispatch with unit location, access instructions, and tenant contact number
7. Vendor arrives within 45 minutes, updates status to "In Progress" with arrival photo
8. Vendor resolves issue, uploads completion photos, marks work order complete at 9:15 PM
9. Tenant receives push notification: "Your emergency request has been resolved" with completion photos
10. Tenant confirms satisfaction via 1-tap rating; total elapsed time: 1 hour 45 minutes

**Outcome:** Emergency resolved same-evening with full documentation trail, zero phone calls to answering service, tenant feels confident in building management responsiveness.

---

#### Journey 2: Property Manager Processes Annual Rent Escalation

1. TenantHub triggers "Escalation Due" alert 90 days before annual escalation date for 34 tenants across 6 properties
2. Property Manager opens Escalation Queue dashboard showing each tenant, current rent, escalation formula (CPI-based or fixed %), and calculated new amount
3. System has auto-calculated new rents using latest CPI index (pulled from BLS API) or fixed percentage per lease terms
4. Property Manager reviews calculations, adjusts 2 cases where negotiated caps apply, and clicks "Approve Batch"
5. System generates escalation notices (using approved template) for each tenant and routes to DocuSign for PM signature
6. Signed notices are posted to each tenant's TenantHub portal with in-app notification and email
7. Tenant views notice, can see calculation methodology and source data (CPI tables or fixed rate clause from their lease)
8. New rent amounts automatically sync to Yardi Voyager, updating the rent roll and next billing cycle
9. System confirms billing alignment and marks escalation as "Completed — Billing Active"

**Outcome:** 34 escalations processed in 2 hours (vs. current 3 weeks of manual work), zero missed escalations, tenants receive transparent communication with source documentation.

---

#### Journey 3: Executive Reviews Portfolio Health Before Board Meeting

1. VP of Asset Management opens TenantHub Analytics dashboard on Monday morning
2. Dashboard shows portfolio snapshot: 94.2% occupancy, $18.3M monthly rent roll, 2.1-day avg maintenance resolution
3. VP clicks into "Tenant Health" view — sees 4 tenants flagged "At Risk" (score below 60/100)
4. Drills into highest-revenue at-risk tenant: declining satisfaction scores, 3 unresolved maintenance complaints, lease expires in 8 months
5. VP assigns follow-up action to property manager: "Schedule face-to-face within 2 weeks, bring resolution plan for open items"
6. VP exports auto-generated Board Report PDF covering: occupancy trends, financial performance vs. budget, maintenance KPIs, tenant retention forecast
7. Report includes 90-day predictive view: 2 tenants likely to not renew (based on model), estimated revenue impact of $420K/year

**Outcome:** Executive prepared for board meeting in 20 minutes with data-driven insights; proactive retention action initiated for at-risk tenant 8 months before potential vacancy.

### Scalability and Growth

| Dimension | Current State | 12-Month Target | 36-Month Vision |
|-----------|--------------|-----------------|-----------------|
| Properties Managed | 47 | 55 (post-acquisition) | 100+ (organic + acquisition) |
| Tenant Contacts | ~320 | ~450 | ~1,000 |
| Concurrent Users | N/A | 150 peak | 500 peak |
| Data Volume | Scattered | 2 TB (docs + media) | 10 TB (incl. IoT sensor data) |
| Geographic Coverage | 12 US markets | 15 US markets | 20+ markets, potential international |
| Integration Density | 1 (Yardi, partial) | 8 active integrations | 15+ integrations (IoT, energy, access control) |

**Growth Implications:**
- System must support multi-property onboarding without per-property deployment effort
- Maintenance, payments, and communications workloads must scale independently
- Document and media storage must serve nationwide users with low latency
- Data architecture must support property-level isolation for potential future multi-owner deployment

### Long-Term Roadmap

| Phase | Timeline | Focus | Key Deliverables |
|-------|----------|-------|-----------------|
| **MVP** | Months 1–6 | Core tenant experience + maintenance workflow | Tenant portal, maintenance requests, basic payments, Yardi sync, property manager dashboard |
| **Phase 2: Operations Excellence** | Months 7–12 | Advanced operations + automation | Vendor portal, automated escalations, SLA management, document management, CAM reconciliation, NPS integration |
| **Phase 3: Intelligence & Growth** | Months 13–18 | Analytics + predictive capabilities | Tenant health scoring, predictive renewal model, executive dashboards, portfolio benchmarking, mobile app (native) |
| **Phase 4: Platform & Ecosystem** | Months 19–30 | Platform extensibility + ecosystem | Building access integration (Brivo), IoT sensor feeds, energy management dashboard, tenant amenity booking, white-label capability for third-party management clients |

---

## MVP Scope

### MVP Objective

Deliver a functional tenant portal with self-service maintenance requests, basic financial visibility, and property manager workflow tools within 6 months, achieving 65% tenant adoption and demonstrating measurable reduction in administrative overhead and maintenance response times.

### MVP Success Criteria

- [ ] 65% of tenant primary contacts have activated their TenantHub account within 60 days of launch
- [ ] 80% of maintenance requests submitted through portal (vs. email/phone) within 90 days of launch
- [ ] Mean time to first response on maintenance requests reduced from 3.2 days to under 4 hours
- [ ] Monthly routine inquiry calls/emails reduced by 50% (from 1,200 to 600)
- [ ] Zero critical security vulnerabilities in pre-launch penetration test
- [ ] 99.5% uptime achieved in first 90 days of production operation
- [ ] Successful bidirectional data sync with Yardi Voyager for all 47 properties
- [ ] Tenant NPS score improves from +12 to +18 within 90 days of launch

### Features In Scope (MVP)

| # | Feature | Priority | Rationale |
|---|---------|----------|-----------|
| 1 | Tenant Registration & Authentication (email + password, MFA optional) | Must Have | Foundation for all portal access; cannot launch without identity |
| 2 | Tenant Dashboard (lease summary, balance, recent activity) | Must Have | Primary landing experience; demonstrates immediate value on first login |
| 3 | Maintenance Request Submission (category, description, photos) | Must Have | #1 tenant pain point; highest-impact workflow to digitize |
| 4 | Maintenance Request Status Tracking (timeline view) | Must Have | Transparency is key value prop; submission without tracking is incomplete |
| 5 | Property Manager Work Order Dashboard (queue, filters, assignment) | Must Have | PM must be able to operate; otherwise requests go into void |
| 6 | Work Order Assignment & Status Updates (manual dispatch) | Must Have | Core operational workflow; vendors notified via email in MVP |
| 7 | Yardi Voyager Data Sync (tenant records, rent roll, payment history) | Must Have | Financial data must be accurate and current; Yardi is source of truth |
| 8 | Tenant Financial Summary (current balance, payment history, invoices) | Must Have | Second-highest source of routine inquiries; direct call reduction driver |
| 9 | Online Rent Payment (ACH via Stripe) | Should Have | Modern expectation; significant convenience factor for adoption |
| 10 | Building Announcements & Notifications (in-app + email) | Should Have | Replaces building-wide email blasts; demonstrates communication value |
| 11 | Tenant Document Vault (view executed lease, insurance certificates) | Should Have | Reduces "send me a copy of my lease" requests; relatively low-effort |
| 12 | Property Manager Communication Tools (message tenant, log interactions) | Should Have | Centralizes communication history; audit trail for disputes |
| 13 | Basic Reporting (open work orders, response times, payment status) | Should Have | PM and leadership need visibility into operations from Day 1 |
| 14 | Email Notification Engine (transactional: request updates, payment confirms) | Must Have | Drives engagement and ensures tenants don't miss critical updates |

### Features Explicitly Out of Scope (MVP)

| # | Feature | Reason for Exclusion | Target Phase |
|---|---------|---------------------|--------------|
| 1 | Vendor/Contractor Portal | Requires vendor onboarding program; MVP uses email dispatch | Phase 2 |
| 2 | Automated Rent Escalation Processing | Complex business rules; manual process acceptable at current scale | Phase 2 |
| 3 | CAM Reconciliation & Transparency Reports | Requires deep Yardi integration + finance team workflow redesign | Phase 2 |
| 4 | Tenant Health Scoring & Predictive Analytics | Needs 6+ months of behavioral data to train meaningful models | Phase 3 |
| 5 | Native Mobile Application (iOS/Android) | Responsive web sufficient for MVP; native adds 3 months to timeline | Phase 3 |
| 6 | DocuSign E-Signature Integration | Lease execution volume doesn't justify build cost in MVP | Phase 2 |
| 7 | Building Access Control Integration (Brivo) | Hardware dependency + per-property rollout complexity | Phase 4 |
| 8 | IoT Sensor Integration (HVAC, energy, water) | Requires infrastructure investment beyond software platform | Phase 4 |
| 9 | Multi-language Support (Spanish) | 8% of tenant contacts are Spanish-primary; important but not blocking | Phase 3 |
| 10 | Automated Vendor Matching & Dispatch | Requires vendor performance data baseline; manual dispatch first | Phase 2 |

### MVP User Journeys

#### MVP Journey 1: Tenant Submits and Tracks a Maintenance Request

1. Tenant receives welcome email with registration link and temporary credentials
2. Tenant logs in, sets permanent password, and sees dashboard with lease summary and balance
3. Tenant clicks "New Maintenance Request" → selects category "HVAC" → subcategory "Temperature Issue"
4. Tenant describes problem: "AC not cooling in suite 301, thermostat reads 78°F but set to 72°F"
5. Tenant uploads photo of thermostat display and submits request
6. System assigns ticket number (WO-2026-00142), sends confirmation email, and places in PM queue
7. Property Manager sees new request in dashboard, reviews details, and manually assigns to "Comfort Systems HVAC"
8. PM updates status to "Vendor Dispatched" → tenant receives email: "A technician has been assigned"
9. PM updates status to "In Progress" when vendor confirms on-site → tenant receives email update
10. PM marks as "Resolved" after vendor confirms fix → tenant receives email with option to confirm or reopen

**Outcome:** Request submitted, tracked, and resolved with clear communication at each stage.

**Limitation vs. Full Vision:** In full vision, vendor receives dispatch directly in vendor portal, updates status themselves, emergency requests trigger immediate SMS to on-call coordinator, and AI categorizes and priority-scores automatically. MVP relies on PM as intermediary for dispatch and status updates.

---

#### MVP Journey 2: Tenant Views Balance and Makes Online Payment

1. Tenant logs into TenantHub and sees dashboard showing: "Current Balance: $12,450.00 — Due: July 1, 2026"
2. Tenant clicks "View Details" → sees itemized breakdown: Base Rent ($11,200), CAM ($890), Utility Reimbursement ($360)
3. Tenant clicks "Payment History" → sees last 12 months of payments with dates, amounts, and confirmation numbers
4. Tenant clicks "Make Payment" → enters amount ($12,450.00), selects "Bank Account (ACH)" payment method
5. First-time: Tenant enters bank routing number and account number, saves as payment method
6. Tenant confirms payment → Stripe processes ACH transfer → confirmation displayed with reference number
7. Payment posts to Yardi within 15 minutes via sync; balance updates on dashboard
8. Tenant receives email confirmation with payment details and updated balance

**Outcome:** Tenant pays rent online in under 2 minutes, receives immediate confirmation, and can verify posting.

**Limitation vs. Full Vision:** Full vision includes recurring auto-pay setup, credit card option with convenience fee, automated late-fee calculation, payment reminders 5 days before due date, and AR aging visibility for property managers. MVP supports one-time ACH payments only with manual late-fee application in Yardi.

### MVP Constraints and Assumptions

| # | Constraint / Assumption | Risk if Wrong |
|---|------------------------|---------------|
| 1 | Yardi Voyager API provides reliable real-time tenant and financial data without rate-limiting issues | If Yardi API is unreliable or rate-limited, we fall back to nightly batch sync, degrading data freshness and requiring stale-data indicators in UI |
| 2 | 80% of commercial tenant primary contacts are comfortable with web-based self-service | If adoption is lower, we may need concierge onboarding support or phone-based account setup assistance, adding operational cost |
| 3 | Stripe Connect supports Meridian's banking structure for ACH rent collection with acceptable fee economics | If Stripe fees exceed 0.8% of rent collected, ROI model breaks; would need to evaluate alternatives (Dwolla, direct ACH via treasury bank) |
| 4 | Team of 6 engineers (4 backend, 2 frontend) + 1 designer + 1 PM can deliver MVP in 6 months | If team is under-resourced or velocity assumptions wrong, scope must be cut (likely: online payments and document vault move to Phase 1.5) |
| 5 | Existing tenant email addresses in Yardi are current and deliverable for registration invitations | If >20% of emails bounce, we need property manager-assisted registration campaign, delaying adoption timeline by 4-6 weeks |
| 6 | SOC 2 Type II audit can be initiated at Month 2 and completed by Month 5 (before launch) | If audit timeline extends, launch may need to proceed under SOC 2 Type I with Type II following, or launch delays to Month 7-8 |
| 7 | Property managers will adopt new digital workflow and reduce reliance on email/Excel within 30 days of training | If PM adoption lags, tenants will submit requests digitally but responses will come via email, creating fragmented experience and undermining portal value |

### MVP Definition of Done

- [ ] All 47 properties and associated tenant records synced from Yardi with <15-minute data freshness
- [ ] Tenant registration, login, and MFA flows pass security review and penetration test
- [ ] Maintenance request lifecycle (submit → assign → update → resolve) fully functional end-to-end
- [ ] Online ACH payment processing live with successful test transactions across 3 bank institutions
- [ ] Email notifications delivered with >98% delivery rate (SendGrid metrics) for all trigger events
- [ ] Property manager dashboard loads within 2 seconds with 200+ open work orders in queue
- [ ] Responsive web design validated on Chrome, Safari, Firefox, Edge; mobile viewports 375px+
- [ ] Accessibility compliance: WCAG 2.1 AA across all tenant-facing pages (automated + manual audit)
- [ ] Production environment deployed with multi-region redundancy, automated failover tested
- [ ] Load testing passed: 150 concurrent users, 95th percentile response time <800ms
- [ ] Disaster recovery tested: RTO <1 hour, RPO <15 minutes (database point-in-time recovery)
- [ ] User acceptance testing completed with 5 pilot tenants and 3 property managers; critical issues resolved

---

## Risks and Dependencies

### Key Risks

| # | Risk | Likelihood | Impact | Mitigation Strategy |
|---|------|-----------|--------|-------------------|
| 1 | Yardi Voyager API is unstable or lacks required endpoints for real-time tenant/financial data | Medium | High | Conduct API proof-of-concept in Sprint 1; design fallback batch-sync architecture; engage Yardi support early with specific endpoint requirements |
| 2 | Tenant adoption falls below 50% due to demographic resistance or poor onboarding experience | Medium | High | Plan white-glove onboarding support; assign property managers as "digital champions" per building; offer lunch-and-learn sessions at each property |
| 3 | Property manager resistance to workflow change undermines digital-first operations | Medium | High | Involve PMs in design process from Sprint 1; demonstrate time savings with real examples; executive mandate on digital-first with 90-day transition window |
| 4 | Payment processing compliance (PCI DSS, Nacha rules) introduces unexpected scope or delays | Low | High | Use Stripe Connect's hosted payment fields (PCI scope minimized to SAQ-A); engage compliance counsel in Month 1; build 4-week buffer in timeline |
| 5 | 6-month timeline is insufficient given team ramp-up, integration complexity, and security requirements | Medium | Medium | Define "Must Ship" vs. "Should Ship" MVP boundary; payments feature is first to descope if needed; plan Phase 1.5 release at Month 8 as relief valve |
| 6 | Data migration quality issues (incomplete/incorrect tenant data in Yardi) corrupt portal experience | High | Medium | Run data quality audit in Month 1; define minimum data completeness requirements; build admin tools for PM-assisted data correction; flag incomplete records in UI |
| 7 | Key team member departure during 6-month build (single points of failure on small team) | Low | High | Cross-train on all critical modules; document architectural decisions in ADRs; maintain relationship with 2 contract augmentation firms for emergency staffing |
| 8 | SOC 2 Type II audit findings require architectural rework that delays launch | Low | High | Engage auditor in Month 1 for pre-assessment; build logging, access controls, and encryption from Sprint 1; allocate 2-week remediation buffer before launch |

### External Dependencies

| # | Dependency | Owner | Current Status | Required By | Risk if Delayed |
|---|-----------|-------|---------------|-------------|-----------------|
| 1 | Yardi Voyager API access credentials and sandbox environment | Yardi Account Team (Sarah Chen) | Requested — awaiting provisioning | Month 1, Week 2 | Blocks all integration development; critical path item |
| 2 | Stripe Connect account approval and underwriting for Meridian entity | Stripe Partnerships (via application) | Application submitted 2026-06-15 | Month 2 | Payments feature cannot be developed or tested without approved account |
| 3 | SendGrid account with dedicated IP and domain authentication (SPF/DKIM) | Meridian IT (James Rivera) | DNS records pending | Month 2 | Email deliverability will suffer without proper authentication; transactional emails may be spam-filtered |
| 4 | Microsoft Entra ID tenant configuration for staff SSO | Meridian IT (James Rivera) | Scoping meeting scheduled | Month 3 | Staff would need separate portal credentials, creating friction; not blocking but degrading |
| 5 | SOC 2 Type II auditor engagement and readiness assessment | GRC Team / External auditor (Coalfire) | RFP in review | Month 2 | Late engagement risks audit findings requiring late-stage rework |
| 6 | AWS Organization sub-account with production-grade guardrails (SCPs, networking) | Meridian IT (James Rivera) | Not started | Month 1 | Development environment could proceed on sandbox, but production readiness blocked |
| 7 | Tenant contact list with verified email addresses for registration invitations | Property Management Team | Partial — 70% verified | Month 5 (pre-launch) | Undeliverable invitations directly reduce adoption metrics |

### Open Questions

| # | Question | Owner | Needed By | Impact of No Answer |
|---|----------|-------|-----------|-------------------|
| 1 | What is Meridian's policy on credit card payment acceptance for rent? Should convenience fees be tenant-paid or absorbed? | CFO (Maria Thompson) | Month 2 | Cannot configure payment methods; MVP may launch ACH-only if undecided |
| 2 | Will Meridian require tenants to use TenantHub exclusively, or maintain parallel email/phone channels during transition? | VP Asset Management (David Park) | Month 3 | Affects adoption targets, staffing model, and whether we build email-ingest capabilities |
| 3 | What is the approved vendor dispatch workflow? Can maintenance coordinators authorize spend up to what threshold without PM approval? | Operations Director (Lisa Nguyen) | Month 2 | Work order approval workflow design depends on authorization limits |
| 4 | How should multi-tenant suites (shared spaces, co-working tenants) be represented? One account per suite or per sub-tenant? | Product + Leasing Team | Month 1 | Data model design is foundational; changing later requires migration |
| 5 | Is there an existing disaster recovery or business continuity requirement from insurance underwriters that dictates RTO/RPO? | Risk Management / Insurance Broker | Month 1 | Architecture decisions (multi-region, backup frequency) depend on this answer |
| 6 | Should tenant payment data (bank account numbers) be stored for recurring payments, or re-entered each time? | Security + Compliance Team | Month 2 | Affects PCI scope, Stripe integration pattern (Customer objects vs. one-time tokens), and UX |
| 7 | What is the support model for after-hours portal issues? Should TenantHub include a support chat, or route to existing answering service? | Operations Director (Lisa Nguyen) | Month 4 | Determines whether live support features are needed at launch or post-MVP |

---

*End of Document*
