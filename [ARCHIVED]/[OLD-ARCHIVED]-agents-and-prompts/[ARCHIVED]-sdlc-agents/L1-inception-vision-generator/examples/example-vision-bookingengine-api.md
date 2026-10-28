# Vision Document: BookingEngine API

**Version:** 1.0  
**Last Updated:** 2026-06-20  
**Owner:** Platform Engineering — Healthcare Integration Team  
**Status:** Draft for Review

---

## Executive Summary

BookingEngine API is a new internal REST API that provides a unified, standards-compliant interface for managing patient appointment scheduling across NHS Trust hospital sites. It serves internal development teams building patient-facing portals, clinician dashboards, and operational reporting tools by abstracting the complexity of querying multiple existing Patient Administration Systems (PAS) and Electronic Patient Record (EPR) systems. The API eliminates the current fragmented integration landscape where each consuming application maintains its own bespoke connections to Lorenzo, Cerner Millennium, and the Trust's legacy scheduling databases. The expected outcome is a 60% reduction in integration development time for new applications, a single source of truth for appointment availability logic, and improved patient experience through consistent booking rules enforced at the API layer.

---

## Business Context

### Problem Statement

- **Fragmented integrations:** Five internal applications currently maintain independent, inconsistent connections to Lorenzo PAS and Cerner Millennium EPR, resulting in duplicated logic, divergent availability calculations, and 3-4 weeks of integration effort per new consumer.
- **Inconsistent booking rules:** Each consuming application implements its own slot availability logic, leading to double-bookings (averaging 23 per week across sites), overbooking of clinic sessions, and 12% appointment no-show rates partially attributed to scheduling errors.
- **Slow onboarding of new services:** When a new clinical service (e.g., Community Diagnostic Centre) needs appointment capability, the current lead time is 8-12 weeks to wire up direct database reads, clinical safety validation, and booking confirmations.
- **Audit and compliance gaps:** Direct database access by multiple applications makes it impossible to produce a unified audit trail of who queried or modified appointment data, creating CQC compliance risk and failing the Trust's 2025 IG Toolkit self-assessment on access logging.
- **Scalability ceiling:** The current point-to-point architecture cannot support the Trust's Digital Front Door programme, which requires real-time slot availability for 40,000+ patient interactions per day by Q2 2027.

### Business Drivers

- **NHS Digital Front Door mandate:** The Trust Board committed (January 2026) to offering online self-service booking for 80% of outpatient appointments by March 2027, requiring a performant, reliable scheduling API.
- **CQC Well-Led framework:** The 2025 inspection flagged insufficient audit controls on appointment data access; a centralised API with OAuth2 scoping and request logging directly remediates this finding.
- **Cost pressure on development teams:** The Trust's ICT budget has been reduced by 15% for FY26/27; eliminating duplicated integration work across teams saves an estimated £320K annually in developer effort.
- **Cerner Millennium upgrade (Oracle Health):** The EPR system is migrating to Oracle Health Cloud in Q4 2026; a single API abstraction layer means only one team adapts to the new interfaces rather than five teams reworking independently.
- **Patient satisfaction targets:** The Trust's target of 85% FFT (Friends and Family Test) satisfaction for outpatient experience by March 2027 depends on reducing booking friction and errors.

### Target Users and Stakeholders

| User Type | Role | Interaction with BookingEngine API | Key Need |
|-----------|------|-----------------------------------|----------|
| Patient Portal Team | Internal dev team (6 engineers) | Primary consumer — books/cancels/reschedules appointments on behalf of patients | Reliable RESTful endpoints, <200ms response, clear error contracts |
| Clinician Dashboard Team | Internal dev team (4 engineers) | Reads clinic schedules, views patient appointment history | Read-only access to filtered appointment views by clinician/specialty |
| Operational Reporting Team | Internal dev team (3 engineers) | Aggregates appointment utilisation, DNA rates, wait times | Bulk query endpoints with date-range filtering and pagination |
| Community Diagnostic Centre (CDC) Platform | Internal dev team (5 engineers) | Books diagnostic slots across networked sites | Multi-site availability queries, cross-site booking capability |
| Integration Engine Team (Rhapsody) | Platform team (2 engineers) | Pushes HL7 ADT/SIU messages into existing PAS when bookings confirmed | Webhook/event notifications on booking state changes |
| Patients (indirect) | 180,000+ registered patients | Do not consume API directly; benefit through portal and NHS App | Accurate availability, fewer cancelled appointments, self-service |
| Clinical Operations Manager | Stakeholder | Defines booking rules, clinic templates, embargo periods | Confidence that business rules are consistently enforced |
| Chief Clinical Information Officer (CCIO) | Executive sponsor | Accountable for digital clinical safety | Assurance of audit trail, data accuracy, clinical safety controls |

### Business Constraints

1. **No database ownership:** BookingEngine API does not own or migrate any data stores; it reads from Lorenzo PAS (SQL Server), Cerner Millennium (Oracle), and the Trust's Clinic Template Repository (PostgreSQL) via existing read replicas.
2. **Read replica latency:** Lorenzo read replica has up to 90-second replication lag; the API must communicate data freshness to consumers via response headers.
3. **Existing authentication infrastructure:** Must integrate with the Trust's existing Keycloak instance (v22.x) for OAuth2/OIDC — no new identity provider permitted.
4. **IG and DSPT compliance:** All endpoints handling patient-identifiable data must enforce Role-Based Access Control aligned to the Trust's DSPT 2025/26 submission and log access per NHS Digital spine-compliant audit requirements.
5. **No breaking changes to PAS:** The API must not write directly to Lorenzo or Cerner; booking confirmations flow via the existing Rhapsody integration engine using HL7v2 SIU messages.
6. **Deployment environment:** Must deploy to the Trust's existing Azure Kubernetes Service (AKS) cluster in UK South region; no AWS or third-party cloud hosting permitted.
7. **Team capacity:** Delivery team is 4 backend engineers + 1 QA + 0.5 architect; no frontend developers are allocated or required.

### Success Metrics

| Metric | Target | Measurement Method | Frequency |
|--------|--------|--------------------|-----------|
| API response time (p95) | ≤ 200ms | Azure Application Insights request duration | Continuous |
| Availability (uptime) | ≥ 99.5% | Synthetic monitoring + AKS health probes | Monthly |
| Double-booking incidents | Reduce from 23/week to ≤ 2/week | Incident tickets tagged `double-booking` in ServiceNow | Weekly |
| Consumer onboarding time | ≤ 5 days from API key request to first production call | Onboarding ticket SLA in Jira | Per consumer |
| Number of active consumers | ≥ 4 applications in production within 6 months of launch | API Management subscription count | Monthly |
| Appointment slot accuracy | ≥ 99% alignment with PAS ground truth | Daily reconciliation batch comparing API cache vs Lorenzo live | Daily |
| Developer satisfaction (consumer teams) | ≥ 4.2/5.0 | Quarterly internal developer experience survey | Quarterly |
| Audit compliance | 100% of PID-accessing requests logged with user context | Log completeness check via Splunk query | Monthly |

---

## Full Scope Vision

### Product Vision Statement

BookingEngine API will become the Trust's single, authoritative scheduling layer — a high-performance, clinically-safe REST API that any internal or approved partner application can consume to query availability, create bookings, manage waitlists, and receive real-time appointment lifecycle events. By abstracting the complexity of heterogeneous source systems behind a clean, versioned contract, BookingEngine API will accelerate the Trust's Digital Front Door programme, enable patient self-service at scale, and ensure that every booking decision — whether initiated by a patient on their phone or a clerk at a reception desk — is governed by identical clinical rules, capacity constraints, and audit controls. It will evolve to support intelligent scheduling (ML-driven DNA prediction, optimal slot suggestion) and federated booking across Integrated Care System (ICS) partner organisations.

### Feature Areas

#### 1. Availability & Slot Management
- **Description:** Real-time query interface for retrieving bookable appointment slots across clinics, specialties, and sites, respecting clinic templates, embargo rules, and capacity limits.
- **Key Capabilities:**
  - Query available slots by specialty, clinician, site, date range, and appointment type
  - Apply booking rules (minimum lead time, maximum advance booking window, patient eligibility)
  - Return slot metadata including consultation mode (face-to-face, telephone, video)
  - Support bulk availability queries for multi-appointment pathways (e.g., pre-op + surgery + follow-up)
  - Real-time slot locking with configurable TTL to prevent race conditions
- **User Value:** Consuming applications display accurate, up-to-date availability without implementing their own rule engines or managing cache invalidation logic.

#### 2. Booking Lifecycle Management
- **Description:** Full CRUD operations for appointment bookings including creation, confirmation, rescheduling, cancellation, and DNA (Did Not Attend) recording.
- **Key Capabilities:**
  - Create provisional and confirmed bookings with idempotency keys
  - Reschedule with automatic cancellation-reason capture and audit
  - Cancel with configurable cancellation reason taxonomy (patient-initiated, clinician-initiated, hospital-initiated)
  - Record attendance outcomes (attended, DNA, cancelled-on-day)
  - Support partial booking (hold slot while awaiting patient confirmation)
- **User Value:** Consumer teams implement booking workflows without understanding HL7 messaging, PAS-specific field mappings, or state machine transitions.

#### 3. Waitlist & Scheduling Intelligence
- **Description:** Manage patient waiting lists, priority scoring, and intelligent slot suggestions to optimise clinic utilisation and reduce patient wait times.
- **Key Capabilities:**
  - Add/remove patients from specialty waiting lists with RTT (Referral to Treatment) clock tracking
  - Priority-based slot suggestion considering clinical urgency, wait duration, and patient preferences
  - DNA risk scoring integration to flag high-risk bookings for confirmation outreach
  - Overbooking management with configurable thresholds per clinic session
- **User Value:** Operations teams reduce clinic underutilisation (currently 18%) and accelerate RTT pathway compliance from 78% to target 92%.

#### 4. Event Notifications & Webhooks
- **Description:** Publish appointment lifecycle events to registered consumers via webhooks and an internal event bus, enabling reactive workflows without polling.
- **Key Capabilities:**
  - Publish events: `appointment.created`, `appointment.confirmed`, `appointment.cancelled`, `appointment.dna`, `slot.released`
  - Consumer webhook registration with retry policy (exponential backoff, 3 attempts, dead-letter)
  - Event filtering by specialty, site, appointment type
  - Integration with Azure Service Bus for durable event delivery
  - Event replay capability for consumer recovery scenarios
- **User Value:** Downstream systems (e.g., SMS reminders, transport booking, clinic prep lists) react to changes without polling, reducing integration latency from minutes to seconds.

#### 5. API Management & Consumer Experience
- **Description:** Self-service onboarding, comprehensive documentation, versioning, rate limiting, and observability tooling for API consumers.
- **Key Capabilities:**
  - OpenAPI 3.1 specification with interactive documentation (Swagger UI / Redoc)
  - API key and OAuth2 scope management per consumer application
  - Configurable rate limiting and quota allocation per consumer tier
  - Health check, readiness, and liveness endpoints for consumer monitoring
  - SDK generation for .NET and TypeScript consumers (auto-generated from OpenAPI spec)
- **User Value:** New consumer teams achieve first successful API call within hours, not weeks, with clear contracts and self-service tooling.

### Integration Points

| # | System | Direction | Protocol | Purpose |
|---|--------|-----------|----------|---------|
| 1 | Lorenzo PAS (DXC) | Read | SQL (read replica) | Source of truth for clinic templates, existing bookings, patient demographics reference |
| 2 | Cerner Millennium / Oracle Health | Read | Oracle DB (read replica) + HL7 FHIR R4 (future) | Source for inpatient scheduling, theatre bookings, and procedure appointments |
| 3 | Rhapsody Integration Engine | Write (outbound) | HL7v2 SIU S12/S14/S15 messages via MLLP | Confirmed bookings and cancellations pushed to PAS via existing integration engine |
| 4 | Keycloak Identity Provider | Authenticate | OAuth2 / OIDC | Token validation, scope enforcement, user identity resolution |
| 5 | Clinic Template Repository | Read | PostgreSQL (read replica) | Clinic session definitions, capacity rules, embargo periods, booking windows |
| 6 | NHS Spine / PDS (Personal Demographics Service) | Read | HL7 FHIR R4 | Patient identity verification, NHS Number validation, demographic cross-check |
| 7 | Azure Service Bus | Publish | AMQP | Event distribution to registered webhook consumers and internal subscribers |
| 8 | Splunk (Log Aggregation) | Write | HEC (HTTP Event Collector) | Structured audit logs for IG compliance and operational monitoring |

### User Journeys (Full Vision)

#### Journey 1: Patient Portal — New Outpatient Booking

1. **Portal requests available slots:** `GET /api/v1/slots?specialty=cardiology&site=RXH&dateFrom=2026-07-01&dateTo=2026-07-14&mode=face-to-face`
2. **API returns filtered availability:** Response includes 12 available slots with clinician name, time, location, and consultation mode; respects patient eligibility rules and minimum 48-hour lead time.
3. **Portal locks a slot:** `POST /api/v1/slots/{slotId}/lock` with 10-minute TTL — prevents race conditions while patient confirms.
4. **Portal creates booking:** `POST /api/v1/bookings` with patient NHS number, locked slot ID, and referral reference.
5. **API validates and confirms:** Checks RTT clock, validates against PAS via Rhapsody SIU message, returns booking confirmation with unique reference.
6. **Event published:** `appointment.confirmed` event triggers SMS reminder service and clinic prep list update.

#### Journey 2: CDC Platform — Multi-Site Diagnostic Booking

1. **CDC platform queries cross-site availability:** `GET /api/v1/slots?service=MRI&sites=RXH,RXP,RXQ&dateFrom=2026-07-01&dateTo=2026-07-28`
2. **API returns aggregated results:** Slots from three hospital sites returned in unified format, sorted by earliest availability.
3. **CDC platform presents options and books:** `POST /api/v1/bookings` with selected slot and patient pathway context.
4. **API enforces pathway rules:** Validates that diagnostic booking aligns with existing RTT pathway, checks preparation requirements (e.g., fasting, contrast consent).
5. **Confirmation flows to relevant site PAS:** Rhapsody routes SIU message to correct site's Lorenzo instance.

#### Journey 3: Reporting Platform — Utilisation Analytics

1. **Reporting tool queries appointment history:** `GET /api/v1/bookings?status=all&dateFrom=2026-04-01&dateTo=2026-06-30&specialty=all&page=1&pageSize=500`
2. **API returns paginated results:** Includes booking outcomes, wait times, DNA flags, cancellation reasons.
3. **Tool aggregates metrics:** Calculates clinic utilisation rates, DNA percentages, average wait-to-appointment duration.
4. **Tool queries slot capacity:** `GET /api/v1/clinics/{clinicId}/capacity?month=2026-07` for forward planning.
5. **Dashboard refreshed:** Operational managers see real-time clinic performance without direct database queries.

### Scalability and Growth

| Dimension | Current State | Full Vision Target | Growth Strategy |
|-----------|---------------|-------------------|-----------------|
| Request volume | N/A (new system) | 40,000 requests/day (peak 200 req/sec) | Horizontal pod autoscaling on AKS; Redis caching layer for slot availability |
| Consumer applications | 0 | 10+ internal applications | Self-service onboarding, tiered rate limiting, consumer-specific SLAs |
| Clinical sites | 3 acute hospital sites | 12 sites (acute + community + CDC) | Site-agnostic data model; federated queries across ICS partners |
| Appointment types | Outpatient face-to-face only (MVP) | All types: outpatient, inpatient, day-case, diagnostic, virtual, group | Extensible appointment type taxonomy with pluggable validation rules |
| Data sources | Lorenzo + Clinic Template Repo | Lorenzo + Cerner + Oracle Health Cloud + FHIR-native systems | Adapter pattern per source system; strategy interface for read operations |

### Long-Term Roadmap

| Phase | Timeline | Key Deliverables | Success Criteria |
|-------|----------|------------------|------------------|
| **MVP** | Q3 2026 (Aug–Oct) | Slot query, basic booking CRUD, Keycloak auth, Lorenzo read, Rhapsody write, OpenAPI spec, 2 consumers live | ≥2 consumers in production, p95 <200ms, zero double-bookings via API |
| **Phase 2: Events & Multi-Site** | Q4 2026 (Nov–Jan 2027) | Webhook events, CDC multi-site booking, cancellation/reschedule flows, Cerner read adapter | ≥4 consumers, event delivery <5s latency, CDC platform live |
| **Phase 3: Intelligence & Waitlist** | Q1–Q2 2027 | Waitlist management, RTT tracking, DNA risk scoring, slot suggestion engine, overbooking management | Clinic utilisation >88%, RTT compliance >92%, DNA rate <9% |
| **Phase 4: Federation & FHIR** | Q3–Q4 2027 | ICS federated booking, FHIR R4 Appointment/Slot resources, Oracle Health Cloud native adapter, partner API access | Cross-organisation booking live, FHIR conformance certified |

---

## MVP Scope

### MVP Objective

Deliver a production-ready REST API that enables the Patient Portal and Clinician Dashboard teams to query outpatient appointment availability from Lorenzo PAS and create/cancel bookings via the existing Rhapsody integration engine, with full audit logging and OAuth2 authentication, within a 10-week delivery window.

### MVP Success Criteria

- [ ] Patient Portal team successfully creates bookings via the API in production
- [ ] Clinician Dashboard team reads appointment schedules via the API in production
- [ ] API achieves p95 response time ≤ 200ms under load (validated by performance test at 100 req/sec)
- [ ] Zero double-bookings attributed to API race conditions during first 30 days of production use
- [ ] 100% of patient-identifiable data requests logged with OAuth2 subject, scope, and timestamp in Splunk
- [ ] OpenAPI 3.1 specification published and validated; SDK generated for .NET consumers
- [ ] Consumer onboarding completed in ≤ 5 working days for both launch consumers
- [ ] Availability uptime ≥ 99.5% measured over first full calendar month post-launch

### Features In Scope (MVP)

| # | Feature | Priority | Rationale |
|---|---------|----------|-----------|
| 1 | Slot Availability Query | Must Have | Core value proposition — enables portal to show bookable slots without direct PAS access |
| 2 | Booking Creation (confirmed) | Must Have | Enables end-to-end booking flow; validates against clinic rules and publishes to Rhapsody |
| 3 | Booking Cancellation | Must Have | Required for patient self-service; must capture cancellation reason for operational reporting |
| 4 | Booking Retrieval (by patient / by clinic) | Must Have | Clinician Dashboard requires filtered appointment views; Portal needs booking confirmation display |
| 5 | OAuth2 / Keycloak Authentication | Must Have | IG compliance requirement; all endpoints must enforce token validation and scope checking |
| 6 | Audit Logging (Splunk integration) | Must Have | CQC remediation requirement; every PID-accessing request must be logged with user context |
| 7 | Slot Locking (optimistic, TTL-based) | Must Have | Prevents double-booking race condition when multiple users select same slot simultaneously |
| 8 | OpenAPI Specification & Documentation | Must Have | Contract-first development; enables consumer teams to develop in parallel; required for SDK generation |
| 9 | Health Check & Readiness Endpoints | Must Have | Required for AKS deployment; enables consumer monitoring and alerting |
| 10 | Rate Limiting (per consumer) | Should Have | Prevents single consumer from degrading service for others; protects Lorenzo read replica |
| 11 | Booking Retrieval with Pagination | Should Have | Supports Reporting team's initial queries; prevents unbounded result sets |
| 12 | Cancellation Reason Taxonomy | Should Have | Structured cancellation data improves operational analytics; aligns with national reporting codes |

### Features Explicitly Out of Scope (MVP)

| # | Feature | Reason | Target Phase |
|---|---------|--------|--------------|
| 1 | Rescheduling (change appointment date/time) | Requires complex state management and PAS interaction patterns not yet validated | Phase 2 |
| 2 | Webhook Event Notifications | Adds architectural complexity (Service Bus, retry logic, dead-letter); consumers can poll in MVP | Phase 2 |
| 3 | Multi-site / Cross-site Booking | Requires Cerner adapter and cross-PAS routing logic; Lorenzo-only for MVP | Phase 2 |
| 4 | Waitlist Management | Complex priority scoring and RTT clock logic requires dedicated design spike | Phase 3 |
| 5 | DNA Risk Scoring | Requires ML model training on historical data; data science team dependency | Phase 3 |
| 6 | FHIR R4 Resource Format | Standard REST/JSON for MVP; FHIR conformance adds significant schema complexity | Phase 4 |
| 7 | Overbooking Management | Requires clinical governance sign-off on overbooking thresholds per specialty | Phase 3 |
| 8 | Virtual/Video Appointment Type | Requires integration with Trust's video consultation platform (Attend Anywhere) | Phase 2 |

### MVP User Journeys

#### Journey 1: Patient Portal — Book an Outpatient Appointment

| Step | Action | API Interaction |
|------|--------|-----------------|
| 1 | Patient selects specialty and preferred date range in portal | Portal calls `GET /api/v1/slots?specialty=ENT&site=RXH&dateFrom=2026-08-01&dateTo=2026-08-14` |
| 2 | Portal displays available slots | API returns available slots from Lorenzo with clinician, time, location |
| 3 | Patient selects a slot | Portal calls `POST /api/v1/slots/{slotId}/lock` — receives lock token valid for 10 minutes |
| 4 | Patient confirms booking | Portal calls `POST /api/v1/bookings` with NHS number, slot lock token, referral ID |
| 5 | Booking confirmed | API validates rules, sends SIU S12 to Rhapsody, returns booking reference |
| 6 | Patient views confirmation | Portal calls `GET /api/v1/bookings/{bookingId}` to display confirmation details |

**Outcome:** Patient has a confirmed outpatient appointment; PAS is updated via Rhapsody; audit log captured.

**Limitation vs Full Vision:** Patient cannot reschedule (must cancel and rebook). No SMS confirmation triggered (no events in MVP). Single-site only (RXH). No DNA risk flag to trigger reminder outreach.

#### Journey 2: Clinician Dashboard — View Clinic Schedule

| Step | Action | API Interaction |
|------|--------|-----------------|
| 1 | Clinician opens their schedule for the day | Dashboard calls `GET /api/v1/bookings?clinicianId=C1234&date=2026-08-15&status=confirmed` |
| 2 | Dashboard displays patient list | API returns confirmed bookings with patient name, NHS number, appointment time, type |
| 3 | Clinician checks specific patient's history | Dashboard calls `GET /api/v1/bookings?patientNhsNumber=9876543210&dateFrom=2026-01-01` |
| 4 | Clinician notes patient DNA | Dashboard calls `PATCH /api/v1/bookings/{bookingId}` with `{"outcome": "dna"}` |

**Outcome:** Clinician has full visibility of their clinic schedule and can record attendance outcomes.

**Limitation vs Full Vision:** No waitlist visibility. No suggested rebooking for DNA patients. No cross-site view of patient appointments at other Trust hospitals. Attendance recording is manual (no auto-detection via check-in kiosk integration).

### MVP Constraints and Assumptions

| # | Constraint / Assumption | Risk if Wrong |
|---|------------------------|---------------|
| 1 | Lorenzo read replica is available with ≤ 90-second lag and supports required query patterns | If replica unavailable or schema restricted, core slot query feature is blocked; fallback would require Rhapsody QBP queries adding 2-3 weeks |
| 2 | Rhapsody integration engine can accept SIU S12/S14 messages for new booking confirmations within existing message throughput capacity | If Rhapsody is at capacity or message format differs from spec, booking creation cannot complete end-to-end; would require Rhapsody team capacity |
| 3 | Keycloak instance supports custom scopes for BookingEngine API without infrastructure changes | If Keycloak requires upgrade or realm restructure, authentication delivery is delayed by 2-4 weeks pending platform team |
| 4 | Clinic Template Repository (PostgreSQL) schema is stable and documented | If schema is undocumented or changes frequently, slot availability logic may return incorrect results; requires data team engagement |
| 5 | Consumer teams (Portal, Dashboard) can dedicate 1 engineer for integration during weeks 6-10 | If consumer teams are unavailable, launch validation is impossible; API ships without production consumers, defeating MVP purpose |
| 6 | AKS cluster has sufficient capacity for 3 additional pods without infrastructure provisioning | If capacity is exhausted, platform team must provision nodes, adding 1-2 weeks to deployment timeline |
| 7 | Lorenzo slot/session data model maps cleanly to our unified slot schema | If mapping is lossy or ambiguous (e.g., slot types not consistently coded), availability accuracy target (99%) may not be achievable at launch |

### MVP Definition of Done

- [ ] All Must Have features implemented, code-reviewed, and merged to main branch
- [ ] Unit test coverage ≥ 80% on business logic (slot rules, booking validation, auth scopes)
- [ ] Integration tests passing against Lorenzo read replica in staging environment
- [ ] Performance test validates p95 ≤ 200ms at 100 requests/second sustained for 30 minutes
- [ ] Security review completed: OWASP API Top 10 checklist passed, penetration test on auth flows
- [ ] OpenAPI 3.1 spec published to internal developer portal; .NET SDK generated and validated
- [ ] Audit logging confirmed in Splunk: sample queries demonstrate full request traceability
- [ ] Deployment pipeline (CI/CD) delivers to AKS staging and production with blue-green rollout
- [ ] Runbook published: incident response, rollback procedure, consumer communication template
- [ ] Both launch consumers (Patient Portal, Clinician Dashboard) have completed integration testing in staging
- [ ] Data Protection Impact Assessment (DPIA) approved by IG team
- [ ] Clinical safety case (DCB0129) signed off by CCIO for booking rule logic

---

## Risks and Dependencies

### Key Risks

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| 1 | Lorenzo read replica schema changes during development (DXC-managed, no change notification SLA) | Medium | High | Establish fortnightly sync with DXC support; implement schema version detection in adapter layer; maintain integration test suite that fails fast on schema drift |
| 2 | Rhapsody message throughput insufficient for booking volume at scale | Low | High | Load test Rhapsody SIU pathway in staging with 2x expected peak volume; agree capacity plan with Integration Engine team; implement async queue buffer if needed |
| 3 | Double-booking race condition not fully eliminated by slot locking | Medium | High | Implement distributed lock via Redis with TTL; add secondary validation at booking creation (re-check slot availability); monitor with automated reconciliation |
| 4 | Consumer teams unable to allocate integration effort during MVP window | Medium | Medium | Begin consumer engagement in week 1; provide SDK and mock server early (week 4); offer pairing sessions; escalate to delivery manager if blockers persist |
| 5 | Keycloak custom scope provisioning delayed by platform team backlog | Medium | Medium | Submit scope request in sprint 0 (2 weeks ahead); prepare fallback with API-key-only auth for staging; scopes mandatory for production only |
| 6 | Performance target missed due to Lorenzo read replica query latency | Low | Medium | Implement Redis caching for slot availability (60-second TTL); add query optimisation layer with pre-computed clinic session views; monitor replica lag via health endpoint |
| 7 | Clinical safety challenge to booking rule logic delays go-live | Medium | High | Engage CCIO in sprint 0; present booking rules in clinical safety workshop (week 3); iterate rules in staging with clinical end-user testing; begin DCB0129 process early |
| 8 | AKS cluster resource contention with other Trust workloads | Low | Medium | Request dedicated node pool for BookingEngine; implement resource limits and pod disruption budgets; monitor with Azure Container Insights |

### External Dependencies

| # | Dependency | Owner | Current Status | Impact if Delayed |
|---|-----------|-------|----------------|-------------------|
| 1 | Lorenzo read replica access (network route + credentials) | DXC / Trust Infrastructure Team | Requested — awaiting firewall rule approval | Blocks all slot query development; 3-week lead time estimated |
| 2 | Keycloak realm configuration (new client + scopes) | Platform Engineering — Identity Team | Not yet requested | Blocks authenticated testing; 1-2 week lead time |
| 3 | Rhapsody SIU message specification and test endpoint | Integration Engine Team | Specification available; test endpoint being provisioned | Blocks end-to-end booking confirmation testing |
| 4 | AKS namespace and deployment pipeline setup | Platform Engineering — DevOps Team | In backlog for sprint 2 | Blocks staging deployment; team can develop locally until resolved |
| 5 | Splunk HEC endpoint and index provisioning | Cyber Security / Logging Team | Agreed in principle; HEC token not yet issued | Blocks audit logging validation; non-blocking for core feature development |
| 6 | Clinical safety sign-off (DCB0129) | CCIO / Clinical Safety Officer | Process not yet initiated | Blocks production go-live; does not block development or staging |
| 7 | DPIA approval | Information Governance Team | Draft submitted; review pending | Blocks production go-live with patient data; staging can use synthetic data |

### Open Questions

| # | Question | Owner | Needed By | Impact of No Answer |
|---|----------|-------|-----------|---------------------|
| 1 | What is the exact Lorenzo database schema for clinic sessions and slot availability? Is there existing documentation or must we reverse-engineer? | DXC / Trust PAS Lead | Sprint 1 (Week 1-2) | Delays slot availability feature by 2+ weeks; risk of incorrect data mapping |
| 2 | Should booking cancellations initiated via the API trigger a patient notification (letter/SMS), or is that the responsibility of the consuming application? | Clinical Operations Manager / Product Owner | Sprint 1 | Unclear responsibility boundary; risk of patients not being informed of cancellations |
| 3 | What is the maximum acceptable slot lock duration before timeout? Clinical vs. patient-facing consumers may need different TTLs. | Product Owner + Clinical Lead | Sprint 2 | Incorrect TTL causes either abandoned locks (too long) or failed bookings (too short) |
| 4 | How should the API handle scenarios where Rhapsody confirms booking creation but Lorenzo replica hasn't yet replicated the change (90-second lag)? | Technical Architect | Sprint 2 | Consumer confusion if immediate GET after POST doesn't reflect new booking; needs consistency model decision |
| 5 | Are there specialties or clinic types that must be excluded from API-based booking (e.g., cancer two-week-wait pathways with specific allocation rules)? | Clinical Operations Manager | Sprint 1 | Risk of API enabling bookings that violate clinical pathway rules; patient safety concern |
| 6 | What rate limiting thresholds are appropriate per consumer? Should the Reporting team (bulk queries) have different limits than the Portal (interactive)? | Technical Architect + Consumer Teams | Sprint 2 | Without tiered limits, bulk consumers may degrade experience for interactive consumers |
| 7 | Is there an existing patient consent model for appointment data sharing between Trust applications, or does BookingEngine API need to implement consent checking? | IG Team / Data Protection Officer | Sprint 1 | Potential IG breach if patient data shared without appropriate legal basis between applications |

---

*Document ends. For questions, contact the BookingEngine API Product Owner or Technical Lead.*
