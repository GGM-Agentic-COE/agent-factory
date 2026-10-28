# Enterprise Architecture Standards — Knowledge Base
### kb-L1-ntuc-enterprise-architecture v1.0.0
### This KB defines the enterprise-level architecture standards for NTUC First Campus (NFC). All design, development, and support agents MUST ground their decisions in these standards.

---

## EA1: Organisation Overview

| Attribute | Details |
|-----------|---------|
| Organisation | NTUC First Campus Limited (NFC) |
| Established | 1977 |
| Domain | Early childhood education and services |
| Headquarters | 16 Raffles Quay, #23-01, Hong Leong Building, Singapore 048581 |
| Staff Strength | 7,000+ |
| Centres | 180+ childcare centres across Singapore |
| UEN | 202308481C |

### Business Units

| Unit | Type | Centres | Focus |
|------|------|---------|-------|
| MyFirstSkool (MFS) | Anchor Operator | 160+ | Childcare services |
| Little Skool House (LSH) | Partner Operator | 14 | Childcare services |
| ChangeMakers Explorer | Premium Operator | 6 | Childcare services |
| SEED Institute | Enrichment arm | — | Afterschool student care, enrichment programmes, outdoor adventure camps |

---

## EA2: Technology Stack

| Layer | Technology | Purpose | Status |
|-------|-----------|---------|--------|
| Backend (SN2) | Go (Golang) | Core backend language | Mandatory |
| Frontend (SN2) | React | Web application | Mandatory |
| Mobile (SN2) | React Native | Cross-platform mobile app | Mandatory |
| Unit Testing | Jest | JavaScript/React testing | Mandatory |
| Code Quality | SonarCloud | Static analysis | Mandatory |
| Database (Relational) | MySQL | Primary relational store | Mandatory |
| Database (NoSQL) | MongoDB | Document store | Mandatory |
| Data Analytics | BigQuery | Analytics and reporting | Mandatory |
| CI/CD | Bitbucket Pipelines | Backend CI/CD | Mandatory |
| CI/CD (Mobile) | Bitrise | Mobile app CI/CD | Mandatory |
| Source Control | Bitbucket | Git repository hosting | Mandatory |
| Observability | OpenTelemetry | Distributed tracing | Mandatory |
| Monitoring | Datadog | Infrastructure & app monitoring | Mandatory |
| Monitoring | Cron Jobs | Scheduled job monitoring (SN2) | Mandatory |
| Monitoring | GCP Cloud Native Logging | Cloud logging | Mandatory |
| Feature Flags | Split.io | Feature flag management | Mandatory |
| Communications | Twilio | SMS/Voice | Mandatory |
| Email | SendGrid | Transactional email | Mandatory |
| Push Notifications | Firebase Cloud Messaging | Mobile push | Mandatory |
| Chat | Sendbird | In-app messaging | Mandatory |
| Live Chat (Support) | Freshchat | Customer support chat | Mandatory |
| Ticketing | ServiceNow | ITSM / incident management | Mandatory |
| Ticketing (Dev) | JIRA | Development tracking | Mandatory |
| ITSM | ServiceNow | Primary IT service management | Mandatory |
| RPA | UiPath | Robotic process automation (3 attended + 1 dev license) |  Mandatory |
| HR Management | SuccessFactors | Employee lifecycle management | Mandatory |
| CRM / Marketing | HubSpot | Marketing & Sales Hub | Mandatory |
| CRM Middleware | Middle Stage | Custom integration middleware | Mandatory |
| Google Workspace | Google Admin Console | Enterprise collaboration | Mandatory |
| Google Automation | GAM API | Advanced Google administration | Mandatory |
| Test Automation (UI) | TestSigma | UI test automation | Mandatory |
| Performance Testing | JMeter | Load and performance testing | Mandatory |

### Infrastructure Stack (Multi-Cloud)

| Layer | GCP | AWS | Purpose |
|-------|-----|-----|---------|
| Compute | GCE, GKE | EC2, EKS | Virtual machines, Kubernetes |
| Storage | Cloud Storage (GCS) | S3, Glacier | Object storage, archival |
| Block Storage | Persistent Disk | EBS | VM-attached storage |
| File Storage | Filestore | EFS | Shared file systems |
| Database (Relational) | Cloud SQL | RDS (PostgreSQL/MySQL) | Managed databases |
| Database (NoSQL) | Firestore | DynamoDB | Document databases |
| Database (Wide-column) | Bigtable | — | Time-series, analytics |
| Cache | Memorystore (Redis) | ElastiCache (Redis) | In-memory caching |
| Networking | Shared VPC, Cloud Load Balancing | ELB (ALB/NLB) | VPC, load balancing |
| DNS | Cloud DNS | Route53 | Domain name resolution |
| CDN | Cloud CDN | CloudFront | Content delivery |
| Connectivity | Cloud Interconnect | Direct Connect | Dedicated connectivity |
| IaC | Terraform (state in GCS) | Terraform (state in S3) | Infrastructure as Code |
| Image Management | Packer | Packer | Golden images |
| Config Management | Ansible | Ansible | Server configuration |
| CI/CD | Jenkins, GitHub Actions | — | Build and deploy pipelines |
| GitOps | ArgoCD / Flux | — | Kubernetes deployments |
| Container Registry | Artifact Registry | ECR | Docker image storage |
| Observability | Google Cloud Operations (Stackdriver) | — | Cloud monitoring |
| Metrics | Prometheus, Grafana | — | Metrics and dashboards |
| Logging | ELK Stack / Fluentd | — | Centralised logging |
| Alerting | PagerDuty / OpsGenie | — | Incident alerting |
| Security (WAF) | Cloud Armor | AWS WAF | Web application firewall |
| Security (IAM) | Cloud IAM | IAM | Identity & access |
| Security (Keys) | KMS | KMS | Key management |
| Security (Secrets) | Secret Manager | — | Secrets storage |
| Security (Posture) | Security Command Center | Security Hub | Security monitoring |
| FinOps | GCP Billing & Cost Management | AWS Cost Explorer, Trusted Advisor | Cost optimisation |
| Identity | On-premises Active Directory (GCP-hosted), Microsoft Entra ID | — | Identity management |
| PKI | Certificate Authority (AD CS) | — | Certificate management |

**MANDATORY RULE:** Core enterprise applications (including SN2) are hosted on GCP. AWS is used primarily for storage services and DNS. Any architectural change must maintain this separation.

---

## EA3: Core Application — SkoolNet 2 (SN2)

### Purpose
End-to-end preschool management system — "single source of truth" for preschool data.

### Capabilities
- Automates enrolment planning, attendance, and vacancy tracking
- Online parent registration with integrated payments (PayNow)
- Child safety via digital check-in/out
- Direct integration with ECDA (regulatory body) for subsidies and reporting
- Data accuracy and consistency across all business units

### Users

| User Type | Count | Interface | Key Actions |
|-----------|-------|-----------|-------------|
| Parents | ~44,000+ | Parent App/Portal | Registration, fee payments, child portfolios |
| Children (served) | ~28,000 | — | — |
| Guardians | ~29,000+ | Guardian App | Child attendance check-in/out |
| Teachers | 5,000+ | Staff App | Classroom management, attendance, learning observations |
| Principals | 180+ | Staff Portal | Centre administration, enrolment management, event planning |
| Head Office | — | Staff Portal | Strategic planning, financial auditing, data analytics |

### Development Statistics (2025)

| Metric | Value |
|--------|-------|
| Release Cycle | Monthly |
| Sprint Duration | 2 weeks |
| Number of Squads | 3 |
| FTE Capacity/Month | 180 man-days (9 headcounts × 20 days) |
| Contractor Capacity/Month | 400 man-days (20 headcounts × 20 days) |
| Feature Releases/Month | 13 |
| Bug Fixes/Month | 8 |

### L2 Support Statistics

| Metric | Value |
|--------|-------|
| Ticket Volume | 260–300 tickets/month (baseline) |
| Support Hours | Mon-Fri, 08:30–18:00 SGT (excl. public holidays) |
| Peak Periods | Weekdays 7–9 AM & 5–7 PM; Oct-Dec (new enrolments); Monday after releases |
| Team Size | 8 resources (2 Team Leads, 6 Support Engineers) |

### SLA (L2 Support)

| Severity | Response | Resolution | Definition |
|----------|----------|-----------|------------|
| Blocker | 30 min | 4 hours | System blocker, no workaround |
| High | 30 min | 8 hours | System blocker with workaround |
| Medium | 1 hour | 3 working days | Intermittent / non-critical |
| Low | 2 hours | 7 working days | Cosmetic / minor bugs |

---

## EA4: Architecture Patterns

### Backend: Go (Golang) Microservices
- Core backend built in Go
- REST APIs for client-server communication
- MySQL for relational data, MongoDB for document storage
- BigQuery for analytics workloads
- OpenTelemetry for distributed tracing

### Frontend: React Web + React Native Mobile
- React for web portal (Staff Portal, Parent Portal)
- React Native for cross-platform mobile (Parent App, Guardian App, Staff App)
- Jest for unit testing, SonarCloud for quality gates

### Infrastructure: Multi-Cloud (GCP Primary, AWS Secondary)
- GCP hosts core applications, data & analytics, Active Directory
- AWS for storage (S3), DNS (Route53), archival (Glacier)
- Kubernetes (GKE/EKS) for container orchestration
- Terraform (IaC) for all infrastructure provisioning
- GitOps (ArgoCD/Flux) for Kubernetes deployments

### Integration Patterns
- Twilio / SendGrid for communications
- Firebase Cloud Messaging for mobile push
- Sendbird for in-app messaging
- Freshchat for live customer support
- PayNow integration for payment processing
- ECDA integration for regulatory compliance

---

## EA5: Service Domains

| Area | Domain | Description |
|------|--------|-------------|
| A | SN2 Application Development & Support | Feature development, bug fixes, L2 technical support |
| B | Quality Assurance | Manual testing, automation (TestSigma), API testing, performance testing (JMeter) |
| C | Level 1 Help Desk | First-contact triage for internal staff and external parents |
| D | Google Workspace Support | Administration, security, governance of Google Workspace |
| E | Infrastructure Operations | CloudOps, FinOps, SecOps across GCP/AWS multi-cloud |
| F | Robotic Process Automation | UiPath-based automation (25 existing use cases) |
| G | Professional Services for SaaS | SuccessFactors (HR) and HubSpot (CRM/Marketing) enhancements |

---

## EA6: Support Model

### L1 Help Desk

| Metric | Value |
|--------|-------|
| Internal Users | 7,000+ staff (HQ + centres); ~40% Chinese-speaking educators |
| External Users | ~44,000+ parents |
| Ticket Volume | ~1,100 tickets/month |
| Support Hours | Mon-Fri, 07:00–19:00 SGT |
| Channels | ServiceNow (ITSM), Email (auto-ticket), Phone, Freshchat (live chat) |
| Languages | Primary: English; Secondary: Chinese |
| Peak Periods | Weekdays 7–9 AM & 5–7 PM; 1st of month; Monday after release |

### L1 SLA

| Priority | Response | Escalation to L2/L3 | Resolution | Adherence |
|----------|----------|---------------------|-----------|-----------|
| S1 | 20 min | 60 min | 4 hours | 90% |
| S2 | 30 min | 90 min | 8 hours | 90% |
| S3 | 1 hour | 1 working day | 3 working days | 90% |
| S4 | 2 hours | 2 working days | 7 working days | 90% |

### Infrastructure SLA

| Severity | Response | Resolution | Adherence |
|----------|----------|-----------|-----------|
| S1 (Critical) | 15 min | 4 hours | 99% |
| S2 (High) | 30 min | 48 hours | 95% |
| S3 (Normal) | 1 hour | 72 hours | 95% |
| S4 (Low) | 2 hours | 120 hours | 95% |

---

## EA7: Quality Assurance Standards

| Metric | Value |
|--------|-------|
| UI Automation Test Cases (SN2) | 2,200 |
| API Tests | 1,500 |
| Regression Scripts | 1,600 |
| Bug Fixes/Month | 8 |
| Test Automation Tool | TestSigma (UI) |
| Performance Testing Tool | JMeter |
| Strategy Direction | "Automation First" |

### Quality Gates
- Feature testing, regression testing, performance testing, sanity testing at every release
- Automated tests integrated into CI/CD pipelines
- Defect warranty: vendor bears cost of Severity 1 & 2 defects found in UAT or within 30-day post-release

---

## EA8: Security & Compliance

### Identity & Access Management
- On-premises Active Directory (hosted on GCP)
- Microsoft Entra ID (cloud identity)
- AD Connect for synchronisation
- Single Sign-On (SSO) for enterprise and third-party apps
- Conditional Access with MFA
- Least privilege enforcement

### Cloud Security (SecOps)
- Cloud Armor (GCP) / AWS WAF for web application protection
- GCP Security Command Center / AWS Security Hub for posture management
- KMS for encryption at rest
- TLS for encryption in transit
- Secret Manager for secrets storage
- IAM Role/Policy enforcement, Service Account management
- Network security: Security Groups, Firewall Rules, VPN tunnels

### Certificate Management (PKI)
- Internal Certificate Authority (AD CS)
- Certificate issuance, renewal, and revocation
- Validity monitoring and expiry alerting
- Template and trust chain management

### Compliance
- Integration with ECDA for regulatory reporting (early childhood)
- Audit support for infrastructure and identity management
- SLA adherence tracking and reporting

---

## EA9: Infrastructure Scale

| Metric | Value |
|--------|-------|
| Total Cloud Resources | ~830+ |
| Primary Cloud | Google Cloud Platform (GCP) |
| Secondary Cloud | Amazon Web Services (AWS) |
| Migration Status | Full migration from on-premise completed 2024 |
| Uptime Target | 99.9% |
| IaC Coverage | Terraform |
| Container Orchestration | Kubernetes (GKE on GCP, EKS on AWS) |

### FinOps
- Project-level budget alerts to prevent bill shock
- Billing anomaly monitoring for spend spikes
- Committed Use Discounts (CUDs) management based on historical spend
- AWS Cost Explorer and Trusted Advisor for AWS spend

---

## EA10: Challenges & Technical Debt

| Area | Challenges |
|------|-----------|
| SN2 Development | Outdated backend/frontend libraries; unpatched vulnerabilities; insufficient test automation; legacy complex codebase; lack of code quality ownership; fragmented end-to-end design knowledge |
| SN2 L2 Support | Burst volumes above baseline; recurring issues needing permanent fixes; knowledge retention; ticket bouncing between L1/L2/L3; L2 lacks code-level RCA skills |
| QA | Reliance on manual testing slows releases; inconsistent test data; slow automation-first transition; automated tests not integrated into CI/CD |
| Help Desk | Language coverage (40% Chinese educators); channel fragmentation; ServiceNow maintenance |
| Google Workspace | Reactive troubleshooting; delays in complex/high-risk resolution; increasing security/compliance demands |
| Infrastructure | Fragmented multi-cloud knowledge; manual processes; scaling team up/down |

---

## EA11: Future Roadmap

### Technology Refresh (Planned Replacements)
| Current System | Purpose | Status |
|---------------|---------|--------|
| Sage 300/Accpac | Financial management | To be replaced |
| Sage eProcurement | Procurement | To be replaced |
| Anaplan | Planning & budgeting | To be replaced |
| PageUp | Application Tracking System | To be replaced |
| SuccessFactors | HR (Succession, Performance, Learning, Employee Central, Payroll) | To be replaced |

### Strategic Direction
- AI/ML POCs and MVPs leveraging new AI capabilities
- SN2 roadmap: feature enhancements + regulatory compliance
- Transition from manual to "Automation First" in QA
- Self-service features to reduce L2 support reliance
- RPA expansion beyond 25 current use cases
- Real-time alerting for Google Workspace admin actions
- Administrative role reassessment and PAM controls

---

## EA12: Operating Model Expectations

### Strategic Partnership Model
NFC seeks a single strategic technology partner operating as an extension of the internal technology team:

| Principle | Description |
|-----------|-------------|
| Outcomes-driven | Focused on service reliability, platform modernisation, delivery acceleration |
| Single partner | Coordinated delivery across all 7 service domains |
| Scalable | Scale team up/down based on business demands |
| Governed | Strong governance, security, and SLA adherence |
| Delivery Manager | Partner provides single point of contact removing management burden |
| Knowledge continuity | Reduce dependency on individual resources |
| Modern tooling | Proactively identify efficiency gains through modern tools |
| Talent pool | Support new technologies: AI/ML, Low Code Platforms |

### Delivery Structure

| Category | Services |
|----------|----------|
| Day 1 Services | SN2 Engineering (A), QA (B), RPA (F), Professional Services for SaaS (G) |
| Day 2 Services | SN2 L2 Support (A), L1 Helpdesk (C), Google Workspace (D), Infrastructure (E) |

### Current Operating Models

| Area | Model | Composition |
|------|-------|-------------|
| SN2 Development | Staff augmentation (near-term), Managed service (long-term) | Mix of FTEs (9) and contractors (20); internal Product Owner retained |
| SN2 L2 Support | Managed service | Incumbent vendor, 8 resources (2 TLs + 6 engineers), SLA-driven |
| L1 Help Desk | Outsourced managed service | Vendor-operated from 2 offshore locations, SLA-driven on volumetrics |
| Google Workspace | Internal SME (to be transitioned) | Currently small internal team; transitioning to strategic partner |
| Infrastructure | Managed service | Dedicated partner team for monitoring, security hardening, SLA adherence |
| RPA | Single contract resource | 1 resource supporting 25 use cases + new implementations |
| QA | Hybrid workforce | Mix of manual testers + automation engineers embedded in squads |

### Delivery Composition Expectations
- Partner proposes optimal onsite-offshore mix per service area
- Shared vs dedicated resources based on domain complexity
- Scale up/down flexibility based on business demand
- Delivery Manager as single point of contact (partner-provided)
- Periodic performance reviews with replacement capability
