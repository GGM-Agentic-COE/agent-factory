# PRD: DairyShield

## Legend

| Field | Value |
|---|---|
| Source 1 | Functional Requirements: `L0-requirements-elicitor-evaluator`, Date: Oct 24, 2026 |
| Source 2 | Non-Functional Requirements: `L0-nfrs-classifier-evaluator`, Date: Oct 24, 2026 |
| Source 3 | DairyShield-vision.md, https://schreiberfoods.atlassian.net/wiki/spaces/AAVAKB/pages/607059994/DairyShield-vision.md, Date: Oct 24, 2026 |
| Status (*Draft / In-Review / Approved*) | **Approved** |
| Approved by (Human Name) | *Varun R* |
| Date of Approval | *Oct 24, 2026* |
| Human Approval Comments | *Latest PRD, Approved by Varun* |

---

## Executive Summary

DairyShield is an IoT-and-ML cold-chain monitoring platform purpose-built for India's raw-milk supply chain, addressing the critical problem of preventable milk spoilage, opaque batch rejections that erode farmer trust, and unplanned cooler failures that disrupt procurement operations. The platform serves three primary user groups — truck supervisors who need real-time reroute guidance, farmers who need transparent root-cause attribution for rejected batches, and maintenance teams who need pre-failure equipment alerts — all of whom currently operate without actionable data. DairyShield solves this by ingesting IoT telemetry from cooler sensors, tanker sensors, and GPS devices, applying thermal decay modeling to project temperature-at-arrival, and triggering FSSAI-calibrated threshold alerts before breaches occur. The business case is anchored in four North-Star Metrics: reduction in rejected or downgraded loads (NSM-01), at-risk batches saved via reroute or prioritization (NSM-02), cooler failures prevented through pre-failure maintenance alerts (NSM-03), and improvement in farmer trust or satisfaction related to root-cause transparency (NSM-04), with quantitative baselines to be established in Phase 1. The platform is designed to operate within India's regulatory framework — DPDP Act 2023, CERT-In Directions 2022, FSSAI raw-milk chilling standards, and FSS Food Recall Procedure Regulations 2017 — from launch, with full user-facing app deployment and multi-state rollout targeted for Phase 3.

---

## Out of Scope

- **FBO Hygiene Standards (OR-03)**: If DairyShield is determined to operate as a Food Business Operator (pending OR-01 resolution), FSS hygiene standards will apply and require additional scoping. No FR covers this obligation because it is conditional on OR-01 resolution — deferred to post-Phase 1 legal determination per DairyShield-vision.md § Open Risks Carried Forward (OR-03).
- **State-Level Licensing (OR-05)**: Multi-state licensing obligations may arise during Phase 3 expansion, conditional on OR-01 resolution. No FR covers state-level licensing because the specific obligations depend on the FBO role determination — deferred per DairyShield-vision.md § Open Risks Carried Forward (OR-05).
- **Platform Integration Plan (OR-07)**: DairyShield-vision.md flags integration with the existing platform as an open question with no specified integration plan. No FR covers integration architecture because the vision document does not define what the system shall do — deferred to a design phase per DairyShield-vision.md § Open Risks Carried Forward (OR-07).
- **Quantitative NSM Targets**: DairyShield-vision.md explicitly defers numeric targets for NSM-01 through NSM-04 to Phase 1 baselining. FR-024 through FR-027 capture the tracking capability; the targets themselves are out of scope for this requirements phase per DairyShield-vision.md § North-Star Metric(s).

---

## Traceability Matrix

| FR | Priority | MVP | NFR Categories | Open Questions |
|---|---|---|---|---|
| FR-001 | High | Yes | Security, Compliance, Availability | 1 |
| FR-002 | High | Yes | Performance, Compliance | 1 |
| FR-003 | High | Yes | Performance, Compliance, Usability | 1 |
| FR-004 | High | Yes | Performance, Usability | 1 |
| FR-005 | High | Yes | Usability, Security | 0 |
| FR-006 | High | Yes | Performance, Security, Usability | 0 |
| FR-007 | Medium | Yes | Security, Compliance | 0 |
| FR-008 | High | Yes | Performance, Usability | 0 |
| FR-009 | High | Yes | Compliance, Usability | 0 |
| FR-010 | High | Yes | Compliance, Performance | 1 |
| FR-011 | High | Yes | Compliance, Performance | 1 |
| FR-012 | High | Yes | Performance, Compliance, Usability | 0 |
| FR-013 | High | Yes | Performance, Compliance, Usability | 0 |
| FR-014 | High | Yes | Compliance, Security, Performance | 0 |
| FR-015 | High | No | Compliance, Performance | 1 |
| FR-016 | High | No | Compliance, Security | 0 |
| FR-017 | High | No | Availability, Scalability | 2 |
| FR-018 | High | No | Availability, Scalability | 2 |
| FR-019 | Medium | No | Compliance, Usability | 0 |
| FR-020 | Medium | No | Compliance, Performance, Usability | 0 |
| FR-021 | High | Yes | Compliance, Security, Performance | 1 |
| FR-022 | High | Yes | Compliance, Performance | 0 |
| FR-023 | High | Yes | Security, Compliance | 0 |
| FR-024 | Medium | Yes | Performance | 1 |
| FR-025 | Medium | Yes | Performance | 1 |
| FR-026 | Medium | Yes | Performance | 1 |
| FR-027 | Low | No | Performance | 1 |

---

## Compound Requirements Split

| Source Clause | Split Into |
|---|---|
| Combining IoT telemetry with thermal decay modeling to project temperature-at-arrival | FR-001, FR-002 |
| Project temperature-at-arrival, trigger threshold alerts, detect cooler degradation, and provide farmer-facing attribution | FR-002, FR-003, FR-004, FR-005 |

---

## Assumptions

| ID | Title | Assumption | Underlies | Source |
|---|---|---|---|---|
| ASSUM-001 | IoT Sensor Infrastructure Exists | Cooler and tanker IoT sensors plus GPS devices are already deployed or will be deployed before Phase 1 begins. | FR-001 | DairyShield-vision.md § Value Proposition |
| ASSUM-002 | FSSAI Raw-Milk Chilling Standards Are Published and Stable | FSSAI raw-milk chilling temperature standards are published, accessible, and will not change materially during Phase 1–2 development. | FR-003, FR-016 | DairyShield-vision.md § Regulatory Posture |
| ASSUM-003 | Data Principals Are Identifiable Before Collection | Farmer and truck supervisor identities can be established and linked to data collection events before consent is requested. | FR-009, FR-010, FR-023 | DairyShield-vision.md § Roadmap Outline (Phase 1) |
| ASSUM-004 | FBO Role Will Be Clarified in Phase 1 | The Food Business Operator role (OR-01) will be legally clarified before Phase 2 development begins, enabling OR-03 and OR-05 obligations to be scoped. | FR-021, FR-022 | DairyShield-vision.md § Open Risks Carried Forward (OR-01) |
| ASSUM-005 | Existing Platform Integration Plan Will Be Defined | A plan for integrating DairyShield with the existing platform (OR-07) will be defined before Phase 3 app deployment. | FR-017, FR-018 | DairyShield-vision.md § Open Risks Carried Forward (OR-07) |
| ASSUM-006 | NSM Baselines Established in Phase 1 | Quantitative baselines for NSM-01 through NSM-04 will be established during Phase 1 before targets are set. | FR-024, FR-025, FR-026, FR-027 | DairyShield-vision.md § North-Star Metric(s) |

---

## Constraints

| ID | Title | Constraint | Constrains | Source |
|---|---|---|---|---|
| CON-001 | DPDP Act 2023 Compliance | All personal data processing must comply with the Digital Personal Data Protection Act 2023 from Phase 1 launch. | FR-009, FR-010, FR-011, FR-012, FR-023 | DairyShield-vision.md § Regulatory Posture |
| CON-002 | CERT-In Directions 2022 Compliance | Cybersecurity incident reporting within six hours and log retention for 180 days are mandatory from Phase 1 launch. | FR-013, FR-014 | DairyShield-vision.md § Roadmap Outline (Phase 1) |
| CON-003 | FSSAI Raw-Milk Chilling Standards | Alert thresholds must be calibrated to FSSAI raw-milk chilling temperature standards; no custom threshold may override them. | FR-003, FR-016 | DairyShield-vision.md § Regulatory Posture |
| CON-004 | FSS Food Recall Procedure Regulations 2017 | Batch traceability must satisfy one-step-back, one-step-forward requirements of FSS Food Recall Procedure Regulations 2017. | FR-021, FR-022 | DairyShield-vision.md § Open Risks Carried Forward (OR-04) |
| CON-005 | FSS Advertising and Claims Regulations 2018 | Predictive performance claims about thermal modeling must be substantiated via validated data per FSS Advertising and Claims Regulations 2018. | FR-002, FR-015 | DairyShield-vision.md § Roadmap Outline (Phase 2) |
| CON-006 | WCAG 2.1 Level AA Accessibility | Both user-facing apps must meet WCAG 2.1 Level AA or equivalent Indian accessibility standard before Phase 3 deployment. | FR-019 | DairyShield-vision.md § Roadmap Outline (Phase 3) |
| CON-007 | Consumer Protection Grievance Obligations | Grievance redressal mechanism must comply with consumer protection obligations (CON-10) before Phase 3 deployment. | FR-020 | DairyShield-vision.md § Roadmap Outline (Phase 3) |

---

## Risks

| ID | Title | Risk | Affects | Source | Status |
|---|---|---|---|---|---|
| RISK-001 | OR-01 FBO Role Ambiguity | Legal ambiguity over whether DairyShield operates as an FBO may trigger FSSAI licensing and hygiene obligations not yet scoped. | program-level | DairyShield-vision.md § Open Risks Carried Forward (OR-01) | Open |
| RISK-002 | OR-02 DPDP Act 2023 Compliance Gap | Incomplete consent, rights interface, or breach notification implementation may result in regulatory penalties under DPDP Act 2023. | FR-009, FR-010, FR-011, FR-012, FR-023 | DairyShield-vision.md § Open Risks Carried Forward (OR-02) | Open |
| RISK-003 | OR-03 Hygiene Standards if FBO | If OR-01 resolves DairyShield as an FBO, FSS hygiene standards will apply and require additional scoping not currently in the FR set. | program-level | DairyShield-vision.md § Open Risks Carried Forward (OR-03) | Open |
| RISK-004 | OR-04 Traceability and Recall Obligations | Failure to implement one-step-back, one-step-forward traceability and a documented recall plan may violate FSS Food Recall Procedure Regulations 2017. | FR-021, FR-022 | DairyShield-vision.md § Open Risks Carried Forward (OR-04) | Open |
| RISK-005 | OR-05 State-Level Licensing | Multi-state rollout in Phase 3 may trigger state-level licensing obligations not yet scoped, conditional on OR-01 resolution. | FR-017, FR-018 | DairyShield-vision.md § Open Risks Carried Forward (OR-05) | Open |
| RISK-006 | OR-06 Thermal Model Accuracy Unvalidated | Thermal decay model accuracy is unvalidated until Phase 2; predictive alerts may generate false positives or miss actual breaches. | FR-002, FR-003, FR-015 | DairyShield-vision.md § Open Risks Carried Forward (OR-06) | Open |
| RISK-007 | OR-07 Platform Integration Undefined | No integration plan exists for connecting DairyShield with the existing platform; app deployment in Phase 3 may be delayed. | FR-017, FR-018 | DairyShield-vision.md § Open Risks Carried Forward (OR-07) | Open |

---

## Requirements

### FR-001: IoT Telemetry Data Collection

**Statement:** The system shall collect IoT telemetry data from cooler temperature sensors, tanker temperature sensors, and GPS devices. **Citation:** DairyShield-vision.md § Value Proposition

**MVP:** Yes *(Basis: DairyShield-vision.md Value Proposition frames IoT telemetry collection as the foundational capability for all predictive alerts — core to solving the stated problem.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Security | Telemetry data must be encrypted in transit using TLS 1.2 or higher | requirements.md § FR-023 | Yes |
| Security | Telemetry data must be encrypted at rest using AES-256 or equivalent | requirements.md § FR-023 | Yes |
| Compliance | GPS location data collection requires consent per DPDP Act 2023 | requirements.md § FR-009 | Yes |
| Availability | TBD — needs stakeholder input | — | Yes |

---

### FR-002: Thermal Decay Modeling

**Statement:** The system shall apply thermal decay modeling to telemetry data to project temperature-at-arrival for milk tankers. **Citation:** DairyShield-vision.md § Value Proposition

**MVP:** Yes *(Basis: DairyShield-vision.md Value Proposition frames thermal decay modeling as the core predictive capability.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Performance | TBD — needs stakeholder input | — | Yes |
| Compliance | Model validation required per FSS Advertising and Claims Regulations 2018 | requirements.md § FR-015 | No *(Basis: DairyShield-vision.md Roadmap Outline explicitly places model validation in Phase 2 — later-phase hardening.)* |

---

### FR-003: Temperature Threshold Alert Generation

**Statement:** The system shall trigger threshold alerts when projected arrival temperature will breach safe limits defined by FSSAI raw-milk chilling temperature standards. **Citation:** DairyShield-vision.md § Value Proposition

**MVP:** Yes *(Basis: DairyShield-vision.md Value Proposition frames threshold alerts as core to solving the spoilage problem.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Performance | TBD — needs stakeholder input | — | Yes |
| Compliance | Alert threshold based on FSSAI raw-milk chilling temperature standards | requirements.md § FR-016 | Yes |
| Usability | Alert must include projected temperature, current location, and estimated arrival time | requirements.md § FR-003 | Yes |

---

### FR-004: Cooler Degradation Detection

**Statement:** The system shall detect cooler degradation by analyzing chilling-rate trends over time. **Citation:** DairyShield-vision.md § Value Proposition

**MVP:** Yes *(Basis: DairyShield-vision.md Value Proposition explicitly frames cooler degradation detection as a core value proposition.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Performance | TBD — needs stakeholder input | — | Yes |
| Usability | Detection must occur before complete cooler failure | requirements.md § FR-004 | Yes |

---

### FR-005: Farmer-Facing Attribution for At-Risk Batches

**Statement:** The system shall provide farmer-facing attribution that identifies the root cause for at-risk or rejected milk batches. **Citation:** DairyShield-vision.md § Value Proposition

**MVP:** Yes *(Basis: DairyShield-vision.md Value Proposition explicitly frames farmer-facing attribution as core to solving the transparency problem.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Usability | Attribution must distinguish between farmer-origin issues and cold-chain issues | requirements.md § FR-005 | Yes |
| Security | Attribution data access must be restricted to authenticated farmer | requirements.md § FR-007 | Yes |

---

### FR-006: Urgent Alert Delivery to Truck Supervisors

**Statement:** The system shall deliver urgent alerts to truck supervisors when projected arrival temperature will breach safe limits. **Citation:** DairyShield-vision.md § Target Users

**MVP:** Yes *(Basis: DairyShield-vision.md Target Users frames urgent alert delivery to truck supervisors as the primary operational use case.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Performance | Alert delivered within 60 seconds of detection | requirements.md § FR-006 | Yes |
| Security | Alert delivery must be authenticated to truck supervisor identity | requirements.md § FR-009 | Yes |
| Usability | Alert must include actionable information for reroute or prioritization decisions | requirements.md § FR-006 | Yes |

---

### FR-007: Quality-Assurance Log Access for Farmers

**Statement:** The system shall provide farmers with access to quality-assurance logs for their batches via the Farmer App passbook. **Citation:** DairyShield-vision.md § Target Users

**MVP:** Yes *(Basis: DairyShield-vision.md Value Proposition frames farmer transparency as core to solving the stated problem; Priority Medium per evaluated requirements used as secondary signal.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Security | Access restricted to batches belonging to authenticated farmer | requirements.md § FR-007 | Yes |
| Security | Log data must be encrypted at rest using AES-256 or equivalent | requirements.md § FR-023 | Yes |
| Compliance | Log access subject to data principal access rights per DPDP Act 2023 | requirements.md § FR-010 | Yes |

---

### FR-008: Pre-Failure Maintenance Alerts for Maintenance Teams

**Statement:** The system shall deliver alerts to maintenance teams when chilling-rate trends indicate cooler degradation before failure occurs. **Citation:** DairyShield-vision.md § Target Users

**MVP:** Yes *(Basis: DairyShield-vision.md Target Users frames pre-failure maintenance alerts as a core use case.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Performance | Alert delivered at least 24 hours before projected failure | requirements.md § FR-008 | Yes |
| Usability | Alert must include cooler identifier, degradation trend data, and recommended action | requirements.md § FR-008 | Yes |

---

### FR-009: DPDP-Compliant Consent Management

**Statement:** The system shall obtain and record consent from data principals for processing personal data including GPS location, farmer identity, and supervisor identity, in compliance with the DPDP Act 2023. **Citation:** DairyShield-vision.md § Roadmap Outline (Phase 1)

**MVP:** Yes *(Basis: DairyShield-vision.md Roadmap Outline Phase 1 explicitly scopes DPDP consent management as a Phase 1 deliverable.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Compliance | Consent obtained before data collection per DPDP Act 2023 § 6 | requirements.md § FR-009 | Yes |
| Compliance | Consent recorded with timestamp and scope per DPDP Act 2023 § 6 | requirements.md § FR-009 | Yes |
| Usability | Consent request presented before data collection begins | requirements.md § FR-009 | Yes |

---

### FR-010: Data Principal Rights Interface

**Statement:** The system shall provide a data principal rights interface enabling access, correction, and erasure requests in compliance with the DPDP Act 2023. **Citation:** DairyShield-vision.md § Roadmap Outline (Phase 1)

**MVP:** Yes *(Basis: DairyShield-vision.md Roadmap Outline Phase 1 explicitly scopes data principal rights interface.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Compliance | Access, correction, and erasure requests per DPDP Act 2023 § 11-14 | requirements.md § FR-010 | Yes |
| Performance | TBD — needs stakeholder input | — | Yes |

---

### FR-011: Data Retention Limit Enforcement

**Statement:** The system shall enforce data retention limits such that personal data is retained only for the duration necessary for operational purposes. **Citation:** DairyShield-vision.md § Roadmap Outline (Phase 1)

**MVP:** Yes *(Basis: DairyShield-vision.md Roadmap Outline Phase 1 explicitly scopes data retention limit enforcement.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Compliance | Personal data retained only for duration necessary per DPDP Act 2023 § 8 | requirements.md § FR-011 | Yes |
| Performance | TBD — needs stakeholder input | — | Yes |

---

### FR-012: Data Breach Notification

**Statement:** The system shall notify affected data principals and the Data Protection Board of personal data breaches within 72 hours of detection. **Citation:** DairyShield-vision.md § Roadmap Outline (Phase 1)

**MVP:** Yes *(Basis: DairyShield-vision.md Roadmap Outline Phase 1 explicitly scopes breach notification.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Performance | Notification delivered within 72 hours of breach detection | requirements.md § FR-012 | Yes |
| Compliance | Notification to data principals and Data Protection Board per DPDP Act 2023 § 8 | requirements.md § FR-012 | Yes |
| Usability | Notification must include nature of breach, affected data categories, and remedial actions | requirements.md § FR-012 | Yes |

---

### FR-013: CERT-In Incident Reporting

**Statement:** The system shall report cybersecurity incidents to CERT-In within six hours of detection in compliance with CERT-In Directions 2022. **Citation:** DairyShield-vision.md § Roadmap Outline (Phase 1)

**MVP:** Yes *(Basis: DairyShield-vision.md Roadmap Outline Phase 1 explicitly scopes CERT-In compliance.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Performance | Report delivered within six hours of incident detection | requirements.md § FR-013 | Yes |
| Compliance | Incident reporting per CERT-In Directions 2022 § 4 | requirements.md § FR-013 | Yes |
| Usability | Report must include incident type, affected systems, and initial assessment | requirements.md § FR-013 | Yes |

---

### FR-014: CERT-In Log Retention

**Statement:** The system shall retain cybersecurity logs for a minimum of 180 days in compliance with CERT-In Directions 2022. **Citation:** DairyShield-vision.md § Roadmap Outline (Phase 1)

**MVP:** Yes *(Basis: DairyShield-vision.md Roadmap Outline Phase 1 explicitly scopes CERT-In log retention.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Compliance | Cybersecurity logs retained for minimum 180 days per CERT-In Directions 2022 § 3 | requirements.md § FR-014 | Yes |
| Security | Logs stored in tamper-evident format | requirements.md § FR-014 | Yes |
| Performance | Logs retrievable within 24 hours of request | requirements.md § FR-014 | Yes |

---

### FR-015: Thermal Model Validation Against Actual Arrival Temperatures

**Statement:** The system shall validate the thermal decay model by comparing projected arrival temperatures against actual measured arrival temperatures. **Citation:** DairyShield-vision.md § Roadmap Outline (Phase 2)

**MVP:** No *(Basis: DairyShield-vision.md Roadmap Outline explicitly places thermal model validation in Phase 2.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Compliance | Validation required per FSS Advertising and Claims Regulations 2018 | requirements.md § FR-015 | No |
| Performance | TBD — needs stakeholder input | — | No |

---

### FR-016: FSSAI Temperature Threshold Configuration

**Statement:** The system shall configure alert thresholds based on FSSAI raw-milk chilling temperature standards. **Citation:** DairyShield-vision.md § Roadmap Outline (Phase 2)

**MVP:** No *(Basis: DairyShield-vision.md Roadmap Outline explicitly places FSSAI threshold configuration in Phase 2.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Compliance | Alert thresholds based on FSSAI raw-milk chilling temperature standards | requirements.md § FR-016 | No |
| Security | Threshold configuration must be auditable and version-controlled | requirements.md § FR-016 | No |

---

### FR-017: Truck Supervisor App Deployment

**Statement:** The system shall deploy a Truck Supervisor App that delivers alerts and enables reroute or prioritization decisions. **Citation:** DairyShield-vision.md § Roadmap Outline (Phase 3)

**MVP:** No *(Basis: DairyShield-vision.md Roadmap Outline explicitly places Truck Supervisor App deployment in Phase 3.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Availability | TBD — needs stakeholder input | — | No |
| Scalability | TBD — needs stakeholder input | — | No |

---

### FR-018: Farmer App Passbook Deployment

**Statement:** The system shall deploy a Farmer App passbook that provides quality-assurance logs and root-cause attribution for batches. **Citation:** DairyShield-vision.md § Roadmap Outline (Phase 3)

**MVP:** No *(Basis: DairyShield-vision.md Roadmap Outline explicitly places Farmer App passbook deployment in Phase 3.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Availability | TBD — needs stakeholder input | — | No |
| Scalability | TBD — needs stakeholder input | — | No |

---

### FR-019: Accessibility Compliance for User-Facing Apps

**Statement:** The system shall ensure the Truck Supervisor App and Farmer App passbook comply with accessibility standards defined in CON-09. **Citation:** DairyShield-vision.md § Roadmap Outline (Phase 3)

**MVP:** No *(Basis: DairyShield-vision.md Roadmap Outline explicitly places accessibility compliance in Phase 3.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Compliance | Apps meet WCAG 2.1 Level AA accessibility guidelines or equivalent Indian standard | requirements.md § FR-019 | No |
| Usability | Accessibility features include screen reader support and high-contrast mode | requirements.md § FR-019 | No |

---

### FR-020: Consumer Protection Grievance Redressal

**Statement:** The system shall provide a grievance redressal mechanism for farmers and truck supervisors in compliance with consumer protection obligations defined in CON-10. **Citation:** DairyShield-vision.md § Roadmap Outline (Phase 3)

**MVP:** No *(Basis: DairyShield-vision.md Roadmap Outline explicitly places grievance redressal in Phase 3.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Compliance | Grievance redressal per consumer protection obligations defined in CON-10 | requirements.md § FR-020 | No |
| Performance | Grievances acknowledged within 24 hours of submission | requirements.md § FR-020 | No |
| Usability | Grievance submission interface accessible in both user-facing apps | requirements.md § FR-020 | No |

---

### FR-021: Batch Traceability Record Maintenance

**Statement:** The system shall maintain one-step-back, one-step-forward traceability records for every milk batch including batch identifiers, timestamps, temperature logs, and custody chain. **Citation:** DairyShield-vision.md § Open Risks Carried Forward (OR-04)

**MVP:** Yes *(Basis: DairyShield-vision.md Open Risks OR-04 frames traceability as a binding regulatory obligation under FSS Food Recall Procedure Regulations 2017 that must be addressed from launch.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Compliance | One-step-back, one-step-forward traceability per FSS Food Recall Procedure Regulations 2017 | requirements.md § FR-021 | Yes |
| Security | Traceability records must be tamper-evident and auditable | requirements.md § FR-021 | Yes |
| Performance | TBD — needs stakeholder input | — | Yes |

---

### FR-022: Documented Recall Plan

**Statement:** The system shall support a documented recall plan by providing retrievable batch traceability records and affected-batch identification capability. **Citation:** DairyShield-vision.md § Open Risks Carried Forward (OR-04)

**MVP:** Yes *(Basis: DairyShield-vision.md Open Risks OR-04 frames recall plan support as a binding regulatory obligation from launch.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Compliance | Recall plan per FSS Food Recall Procedure Regulations 2017 | requirements.md § FR-022 | Yes |
| Performance | Batch records retrievable within 15 minutes | requirements.md § FR-022 | Yes |
| Performance | Affected-batch identification within 30 minutes | requirements.md § FR-022 | Yes |

---

### FR-023: Security Safeguards for Personal Data

**Statement:** The system shall implement security safeguards including encryption at rest and in transit, access control, and audit logging for all personal data. **Citation:** DairyShield-vision.md § Open Risks Carried Forward (OR-02)

**MVP:** Yes *(Basis: DairyShield-vision.md Open Risks OR-02 frames security safeguards as a binding DPDP Act 2023 obligation from launch.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Security | Personal data encrypted at rest using AES-256 or equivalent | requirements.md § FR-023 | Yes |
| Security | Personal data encrypted in transit using TLS 1.2 or higher | requirements.md § FR-023 | Yes |
| Security | Access to personal data must be logged and auditable | requirements.md § FR-023 | Yes |
| Compliance | Security safeguards per DPDP Act 2023 § 8 | requirements.md § FR-023 | Yes |

---

### FR-024: NSM-01 Tracking for Rejected or Downgraded Loads

**Statement:** The system shall track the number of rejected or downgraded milk loads to measure reduction over time as defined in NSM-01. **Citation:** DairyShield-vision.md § North-Star Metric(s)

**MVP:** Yes *(Basis: DairyShield-vision.md North-Star Metrics requires NSM-01 baseline to be established in Phase 1.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Performance | TBD — needs stakeholder input | — | Yes |

---

### FR-025: NSM-02 Tracking for At-Risk Batches Saved

**Statement:** The system shall track the number of at-risk batches saved via reroute or prioritization as defined in NSM-02. **Citation:** DairyShield-vision.md § North-Star Metric(s)

**MVP:** Yes *(Basis: DairyShield-vision.md North-Star Metrics requires NSM-02 baseline to be established in Phase 1.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Performance | TBD — needs stakeholder input | — | Yes |

---

### FR-026: NSM-03 Tracking for Cooler Failures Prevented

**Statement:** The system shall track the number of cooler failures prevented through pre-failure maintenance alerts as defined in NSM-03. **Citation:** DairyShield-vision.md § North-Star Metric(s)

**MVP:** Yes *(Basis: DairyShield-vision.md North-Star Metrics requires NSM-03 baseline to be established in Phase 1.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Performance | TBD — needs stakeholder input | — | Yes |

---

### FR-027: NSM-04 Tracking for Farmer Trust or Satisfaction

**Statement:** The system shall track farmer trust or satisfaction improvement related to root-cause transparency as defined in NSM-04. **Citation:** DairyShield-vision.md § North-Star Metric(s)

**MVP:** No *(Basis: NSM-04 is a lagging indicator dependent on FR-018 Farmer App passbook deployment, which is explicitly Phase 3; Priority Low per evaluated requirements.)*

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Performance | TBD — needs stakeholder input | — | No |

---

## Open Questions

- **FR-001 (Availability):** What is the fallback behavior when the IoT telemetry stream fails? What uptime SLA is required for telemetry ingestion?
- **FR-002 (Performance):** What is the maximum acceptable latency for thermal decay model projection calculation?
- **FR-003 (Performance):** What is the maximum acceptable latency for alert generation after threshold breach is projected?
- **FR-004 (Performance):** What is the maximum acceptable detection latency or lookback window for chilling-rate trend analysis?
- **FR-010 (Performance):** What is the maximum acceptable processing time for data principal access, correction, and erasure requests?
- **FR-011 (Performance):** What is the maximum acceptable latency for automated deletion or anonymization jobs when retention periods expire?
- **FR-015 (Performance):** What prediction error threshold triggers model recalibration? What is the acceptable validation report generation latency?
- **FR-017 (Availability):** What uptime SLA is required for the Truck Supervisor App? What is the offline fallback behavior?
- **FR-017 (Scalability):** What is the target concurrent user count for the Truck Supervisor App at Phase 3 multi-state rollout?
- **FR-018 (Availability):** What uptime SLA is required for the Farmer App passbook? What is the offline fallback behavior?
- **FR-018 (Scalability):** What is the target concurrent user count for the Farmer App passbook at Phase 3 multi-state rollout?
- **FR-021 (Performance):** What is the maximum acceptable latency for creating a traceability record at the batch collection point?
- **FR-024 (Performance):** What is the acceptable latency for logging rejected/downgraded loads and generating monthly reduction reports?
- **FR-025 (Performance):** What is the acceptable latency for logging at-risk batch outcomes and generating monthly saved-batch reports?
- **FR-026 (Performance):** What is the acceptable latency for logging prevented cooler failures and generating monthly prevention reports?
- **FR-027 (Performance):** What is the acceptable latency for logging farmer app feedback and generating quarterly satisfaction reports?
- **Coverage gap:** FR-005 (Farmer-Facing Attribution) and FR-007 (Quality-Assurance Log Access) together imply a data pipeline linking batch rejection events to attribution records accessible in the Farmer App passbook. Neither FR nor any NFR boundary condition specifies how attribution data flows from the core system to the passbook before FR-018 (app deployment) is complete. This gap is not visible from either FR or NFR in isolation and surfaces only when reading the two requirements side by side.

---

## Glossary

| Term | Definition | Source |
|---|---|---|
| Batch | A discrete quantity of raw milk collected from one or more farmers at a single collection point and tracked as a unit through the cold chain. | DairyShield-vision.md § Value Proposition |
| Chilling Rate | The rate at which raw milk temperature decreases over time in a cooler, used as an indicator of cooler health and performance. | DairyShield-vision.md § Value Proposition |
| Cold Chain | The temperature-controlled supply chain from milk collection at the farm through tanker transport to the processing facility. | DairyShield-vision.md § Value Proposition |
| CERT-In | Indian Computer Emergency Response Team; the national nodal agency for cybersecurity incident response under the Ministry of Electronics and Information Technology. | DairyShield-vision.md § Regulatory Posture |
| Data Principal | An individual whose personal data is being processed; in DairyShield's context, this includes farmers and truck supervisors whose GPS location and identity data are collected. | DairyShield-vision.md § Roadmap Outline (Phase 1) |
| DPDP Act 2023 | Digital Personal Data Protection Act 2023; India's primary data protection legislation governing the collection, processing, and storage of personal data. | DairyShield-vision.md § Regulatory Posture |
| FBO | Food Business Operator; a legal entity responsible for compliance with FSSAI regulations. Whether DairyShield qualifies as an FBO is an open risk (OR-01). | DairyShield-vision.md § Open Risks Carried Forward (OR-01) |
| Farmer App Passbook | A mobile application interface for farmers that displays quality-assurance logs, temperature history, and root-cause attribution for their milk batches. | DairyShield-vision.md § Target Users |
| FSSAI | Food Safety and Standards Authority of India; the regulatory body that sets food safety standards including raw-milk chilling temperature requirements. | DairyShield-vision.md § Regulatory Posture |
| NSM | North-Star Metric; a primary outcome measure used to track DairyShield's business impact. Four NSMs are defined: NSM-01 (rejected/downgraded loads), NSM-02 (at-risk batches saved), NSM-03 (cooler failures prevented), NSM-04 (farmer trust/satisfaction). | DairyShield-vision.md § North-Star Metric(s) |
| Temperature-at-Arrival | The projected temperature of a milk tanker's contents when it reaches the processing facility, calculated via thermal decay modeling from current telemetry data. | DairyShield-vision.md § Value Proposition |
| Thermal Decay Modeling | A predictive algorithm that uses current temperature readings, ambient conditions, and route data to project how milk temperature will evolve during transit. | DairyShield-vision.md § Value Proposition |
| Truck Supervisor App | A mobile application interface for truck supervisors that delivers urgent temperature breach alerts and supports reroute or prioritization decisions. | DairyShield-vision.md § Target Users |