# Vision Document: SecurePayHub

## Executive Summary

SecurePayHub is a mobile payments application designed to enable secure, compliant payment transactions for UK and European consumers and businesses. The application addresses the critical need for a payments platform that adheres to UK payment scheme regulations (FPS, BACS, CHAPS) and PSD2 requirements while integrating robust KYC verification and biometric authentication. By combining regulatory compliance with modern biometric security (fingerprint, facial recognition), SecurePayHub will reduce payment fraud, streamline identity verification, and provide users with a trusted platform for domestic and cross-border payments. The expected outcome is a 40% reduction in payment fraud incidents, 90% KYC completion rate within 24 hours, and 200,000 active users within 12 months of launch.

## Business Context

### Problem Statement

UK and European payment users face three critical challenges: (1) payment fraud losses reached £1.2 billion in 2022, with APP fraud accounting for £485 million; (2) existing payment applications have fragmented KYC processes that take 3-5 days to complete, causing 35% abandonment rates; (3) compliance with evolving PSD2 Strong Customer Authentication requirements creates friction, with 22% of payment transactions failing due to authentication issues. These problems result in financial losses, poor user experience, and regulatory penalties for non-compliant payment service providers.

### Business Drivers

**Regulatory Pressure**: PSD2 mandates Strong Customer Authentication for electronic payments and account access, requiring two-factor authentication with dynamic linking. The Money Laundering Regulations 2017 require Customer Due Diligence for all payment account holders, with Enhanced Due Diligence for PEPs and high-risk customers. Non-compliance results in FCA enforcement action and potential loss of payment service provider authorization.

**Fraud Epidemic**: APP fraud has increased 39% year-over-year, with criminals exploiting weak authentication and identity verification. Confirmation of Payee (CoP) is now mandatory for Faster Payments, requiring real-time name-checking before payment execution.

**Open Banking Opportunity**: PSD2 enables Payment Initiation Service Providers (PISP) to initiate payments directly from customer bank accounts, bypassing card networks and reducing transaction costs by 60-80%. Variable Recurring Payments (VRP) capability is emerging, enabling automated payment arrangements with customer control.

**Mobile-First Behaviour**: 73% of UK consumers use mobile banking as their primary channel, with 89% expecting biometric authentication as standard. Biometric authentication reduces authentication time from 45 seconds (SMS OTP) to 3 seconds (fingerprint/face).

### Target Users and Stakeholders

| User Type | Description | Primary Need |
|-----------|-------------|--------------|
| Consumer Payment User | UK/EU individuals aged 18-65 making domestic and cross-border payments via mobile | Fast, secure payment execution with minimal authentication friction while maintaining fraud protection |
| Business Payment User | SME owners and finance managers initiating bulk payments, supplier payments, and payroll | Batch payment capability with audit trail, multi-user authorization workflows, and reconciliation support |
| Compliance Officer | Internal compliance team responsible for AML/CTF monitoring, SAR filing, and regulatory reporting | Real-time transaction monitoring dashboard, automated sanctions screening, and audit-ready reporting for FCA inspections |
| Fraud Analyst | Fraud operations team investigating suspicious transactions and managing fraud cases | Fraud alert queue with risk scoring, customer communication tools, and case management workflow for SAR filing |
| Customer Support Agent | First-line support handling payment queries, failed transaction investigations, and account issues | Customer transaction history view, payment status tracking, and guided troubleshooting scripts for common issues |

### Business Constraints

**Regulatory Compliance**: Must obtain FCA authorization as Authorized Payment Institution or register as Small Payment Institution before launch. Requires compliance with PSD2, MLR 2017, GDPR, and UK payment scheme rules (FPS, BACS, CHAPS). Non-compliance risk: loss of authorization, unlimited fines, criminal liability for money launering offences.

**Budget**: £2.5 million development budget over 18 months, with £800k allocated to regulatory compliance, KYC provider integration, and security infrastructure. Ongoing operational cost of £150k/month for payment scheme membership, KYC verification costs (£1.50 per verification), and cloud infrastructure.

**Timeline**: MVP launch required within 9 months to meet strategic market window before two major competitors launch similar products. Full vision delivery within 18 months to capture early adopter market share.

**Integration Dependencies**: Dependent on third-party KYC provider (e.g., Onfido, Jumio) for identity verification, CRA integration for sanctions screening, and payment scheme access provider for FPS/BACS connectivity. Any provider outage or contract termination creates critical operational risk.

**Organizational Capacity**: Development team of 12 (4 backend, 3 mobile, 2 QA, 1 DevOps, 1 product, 1 compliance specialist). Limited in-house payments domain expertise requires external consultancy for payment scheme integration and regulatory compliance design.

### Success Metrics

| Metric | Current State | Target State | Measurement Method |
|--------|---------------|--------------|-------------------|
| Payment Fraud Rate | Industry average 0.8% of transaction value | <0.2% of transaction value | Monthly fraud loss value / total transaction value, reported to FCA quarterly |
| KYC Completion Rate | Industry average 65% within 24 hours | 90% within 24 hours | Count of users completing KYC / total users starting KYC, measured daily via KYC provider API |
| Authentication Success Rate | Industry average 78% first-attempt SCA success | 95% first-attempt SCA success | Successful biometric auth / total auth attempts, tracked per authentication method (fingerprint, face, PIN) |
| Payment Success Rate | Industry average 92% (FPS), 96% (BACS) | 98% (FPS), 99% (BACS) | Successful payments / total payment attempts, excluding user-cancelled transactions, measured per payment scheme |
| Active User Growth | 0 (new product) | 200,000 active users (≥1 payment/month) within 12 months | Monthly active users tracked via analytics platform, segmented by consumer vs business users |
| CoP Match Rate | Industry average 82% exact match | 95% exact match or close match accepted | CoP exact+close matches / total CoP checks, measured per payment via CoP API response codes |
| Average Payment Time | Industry average 45 seconds (authentication + execution) | <10 seconds (authentication + execution) | Time from payment initiation to FPS submission, measured via application performance monitoring |

## Full Scope Vision

### Product Vision Statement

SecurePayHub will become the trusted mobile payments platform for UK and European users who demand bank-grade security without sacrificing speed or simplicity. By combining biometric authentication, real-time fraud detection, and seamless integration with UK payment schemes and Open Banking, we will eliminate the trade-off between security and convenience. Our vision extends beyond simple person-to-person payments to encompass business payments, international transfers, payment requests, and intelligent payment scheduling—all protected by continuous biometric authentication and AI-powered fraud prevention. SecurePayHub will set the standard for what a regulated, secure, user-centric payment application should be.

### Feature Areas

#### 1. Identity Verification & KYC
**Description**: Comprehensive digital identity verification meeting MLR 2017 Customer Due Diligence requirements, with automated document verification, biometric liveness detection, and sanctions screening.

**Key Capabilities**:
- Multi-document support (passport, driving licence, national ID card) with OCR extraction
- Selfie capture with liveness detection (blink, head turn) to prevent photo/video spoofing
- Real-time PEP and sanctions list screening against OFAC, EU, UN, and UK HMT lists
- Enhanced Due Diligence workflow for high-risk customers with manual review queue
- Continuous monitoring with periodic re-verification for PEPs and high-value users
- GDPR-compliant identity data storage with encryption at rest and in transit

**User Value**: Users complete identity verification in under 3 minutes from their mobile device without visiting a branch or mailing documents. Instant verification enables immediate payment access for 85% of users, with manual review completed within 4 hours for edge cases.

#### 2. Biometric Authentication & SCA
**Description**: Multi-modal biometric authentication (fingerprint, facial recognition, device biometrics) integrated with PSD2 Strong Customer Authentication requirements, providing dynamic linking for payment authorization.

**Key Capabilities**:
- Fingerprint authentication using device secure enclave (Touch ID, Android Fingerprint API)
- Facial recognition using device face unlock (Face ID, Android Face Unlock)
- Dynamic linking: biometric prompt displays payment amount, recipient name, and timestamp
- Fallback authentication: PIN, SMS OTP, or hardware token for devices without biometrics
- Transaction risk analysis: low-risk transactions use single-factor, high-risk require two-factor
- Continuous authentication: periodic biometric re-authentication during active session
- Biometric template storage in device secure enclave (never transmitted to server)

**User Value**: Users authorize payments with a fingerprint or glance in under 2 seconds, eliminating password entry and SMS code delays. Dynamic linking displays payment details during authentication, preventing man-in-the-middle attacks where users unknowingly authorize fraudulent payments.

#### 3. Payment Execution & Processing
**Description**: Multi-scheme payment execution supporting Faster Payments Service (FPS), BACS, CHAPS, and Open Banking Payment Initiation (PISP), with real-time payment tracking and intelligent routing.

**Key Capabilities**:
- FPS payments: real-time execution, 24/7 availability, £1M single payment limit, funds arrive in seconds
- BACS payments: 3-day processing cycle, unlimited amount, lower cost for non-urgent payments
- CHAPS payments: same-day high-value payments (>£250k), guaranteed settlement, cut-off time management
- Open Banking PISP: direct bank account debit, bypassing card networks, supporting VRP for recurring payments
- Confirmation of Payee (CoP): mandatory name-checking before FPS execution, with mismatch warning and override flow
- Payment scheduling: future-dated payments, recurring payments, payment templates for frequent recipients
- Batch payments: CSV upload for business users, bulk payment validation, multi-user approval workflow
- Payment status tracking: real-time status updates (pending, processing, completed, failed) with push notifications

**User Value**: Users choose the optimal payment method based on urgency, cost, and amount. FPS delivers instant payments for urgent transfers, BACS reduces costs for salary payments, and CHAPS enables same-day high-value property transactions. CoP prevents misdirected payments by verifying recipient names before execution.

#### 4. Fraud Detection & Prevention
**Description**: Multi-layered fraud prevention combining device fingerprinting, behavioral analytics, transaction risk scoring, and real-time sanctions screening to detect and block fraudulent payments before execution.

**Key Capabilities**:
- Device fingerprinting: unique device identification, detection of emulators and rooted devices
- Behavioral analytics: typing patterns, swipe gestures, session duration to detect account takeover
- Transaction risk scoring: amount, recipient, time, location, device analyzed against user baseline
- Velocity checks: limits on transaction count and value per hour/day/week to prevent rapid-fire fraud
- Sanctions screening: real-time check of recipient against PEP, sanctions, and watchlists before payment
- APP fraud detection: warnings for payments to new recipients, first-time large payments, unusual patterns
- Fraud alert queue: suspicious transactions routed to fraud analyst for manual review before execution
- SAR filing workflow: automated Suspicious Activity Report generation and submission to National Crime Agency

**User Value**: Users are protected from APP fraud through intelligent warnings when sending payments to suspicious recipients. Genuine payments are not blocked, but users receive clear risk indicators (e.g., "This recipient is new and you're sending £5,000—are you sure?") enabling informed decisions. Fraud losses are minimized through multi-layered detection without creating authentication friction for legitimate users.

#### 5. Account & Transaction Management
**Description**: Comprehensive account dashboard providing transaction history, payment status tracking, recipient management, and self-service account maintenance.

**Key Capabilities**:
- Transaction history: searchable, filterable list of all payments (sent, received, scheduled, failed)
- Payment details: full audit trail including timestamp, amount, recipient, payment reference, scheme, status
- Recipient management: saved payees with nicknames, payment history, favorite recipients
- Payment disputes: in-app dispute initiation for unauthorized or incorrect payments
- Account settings: communication preferences, notification settings, biometric enrollment
- Statement download: PDF/CSV export for accounting and reconciliation
- Payment limits: view and request changes to daily/weekly payment limits
- Direct Debit management: view and cancel Direct Debit mandates (AUDDIS integration)

**User Value**: Users have complete visibility and control over their payment activity. Transaction history enables expense tracking and reconciliation. Saved recipients eliminate repetitive data entry for frequent payments. Self-service settings reduce support contact volume.

#### 6. Compliance & Reporting
**Description**: Automated compliance monitoring, regulatory reporting, and audit trail generation to meet FCA, PSD2, MLR, and GDPR requirements.

**Key Capabilities**:
- Transaction monitoring: automated detection of suspicious patterns (structuring, rapid movement, high-risk jurisdictions)
- AML/CTF reporting: automated SAR generation with case management workflow
- Regulatory reporting: automated submission of payment statistics, fraud data, and incident reports to FCA
- Audit trail: immutable log of all user actions, authentication events, and system decisions
- GDPR compliance: DSAR fulfillment workflow, consent management, right to erasure
- Data retention: automated purging of personal data per retention policy (6 years for financial records)
- Incident management: security incident logging, breach notification workflow (72-hour GDPR requirement)

**User Value**: Users trust that their data is handled compliantly and securely. GDPR rights are respected with transparent data usage and easy access to personal data. Regulatory compliance protects users from platform shutdown or service disruption due to enforcement action.

### Integration Points

**KYC Provider (Onfido/Jumio)**: Identity document verification, facial biometric matching, liveness detection, PEP/sanctions screening. API integration for verification initiation, status polling, and result retrieval. Webhook integration for asynchronous verification completion.

**Payment Scheme Access Provider (e.g., Form3, Token, Modulr)**: Connectivity to FPS, BACS, and CHAPS payment schemes. API integration for payment submission, status tracking, and inbound payment notification. CoP API for recipient name verification.

**Open Banking Provider (e.g., TrueLayer, Yapily)**: AISP for account information access (balance, transactions), PISP for payment initiation. OAuth consent flow for bank authorization, API integration for payment execution and status tracking.

**Credit Reference Agency (Experian/Equifax/TransUnion)**: Sanctions screening, PEP checking, fraud data sharing. API integration for real-time screening during KYC and payment execution.

**Device Biometric APIs**: iOS Touch ID/Face ID via Local Authentication framework, Android Fingerprint/Face Unlock via BiometricPrompt API. Native integration for biometric enrollment, authentication, and fallback handling.

**Push Notification Service**: Firebase Cloud Messaging (Android), Apple Push Notification Service (iOS) for payment status updates, fraud alerts, and security notifications.

**Analytics Platform (Mixpanel/Amplitude)**: User behavior tracking, funnel analysis, cohort analysis for product optimization and fraud pattern detection.

**Customer Support Platform (Zendesk/Intercom)**: In-app support chat, ticket creation, knowledge base integration for self-service support.

### User Journeys (Full Vision)

#### Journey 1: New User Onboarding with KYC and First Payment
1. User downloads SecurePayHub app from App Store/Google Play
2. User creates account with email and password, accepts terms and privacy policy
3. User enrolls biometric authentication (fingerprint/face) for future logins
4. System initiates KYC: user selects document type (passport/driving licence)
5. User captures document photo using in-app camera with real-time quality guidance
6. User captures selfie with liveness detection (blink, turn head)
7. System submits verification to KYC provider, displays "Verifying your identity..." screen
8. KYC provider returns result in 30 seconds: PASS (85% of cases), user proceeds to dashboard
9. User adds first recipient: enters sort code, account number, recipient name
10. System performs CoP check: returns "Exact match" confirmation
11. User enters payment amount (£100), adds reference ("Dinner split")
12. User selects payment method: FPS (instant) vs BACS (3 days, lower cost)
13. User authorizes payment with biometric: fingerprint prompt displays amount, recipient, and "Authorize Payment" text
14. System performs fraud check: low risk, payment approved and submitted to FPS
15. User receives push notification: "Payment sent to John Smith - £100"
16. Payment arrives in recipient account within 10 seconds
**Outcome**: User completes onboarding, KYC, and first payment in under 5 minutes with zero friction. Biometric authentication and CoP verification provide security without complexity.

#### Journey 2: Business User Bulk Payment with Multi-User Approval
1. Business user (finance manager) logs in with biometric authentication
2. User navigates to "Batch Payments" feature, selects "Upload CSV"
3. User uploads CSV file containing 150 supplier payments (sort code, account, amount, reference)
4. System validates CSV: checks format, validates sort codes, performs CoP checks on all recipients
5. System displays validation results: 145 exact matches, 5 close matches requiring review
6. User reviews 5 close matches: 3 are acceptable variations (e.g., "Ltd" vs "Limited"), 2 are errors
7. User corrects 2 errors, confirms 3 close matches, proceeds to approval
8. System calculates total amount: £245,680.50, displays summary and fee breakdown
9. User submits batch for approval (business rule: >£100k requires dual authorization)
10. System sends push notification to approver (finance director): "Batch payment awaiting approval"
11. Approver logs in, reviews batch details, checks sample transactions
12. Approver authorizes batch with biometric authentication
13. System schedules batch for BACS submission (next processing day)
14. System sends confirmation to both users: "Batch scheduled for 2024-01-15"
15. On processing day, system submits batch to BACS, tracks individual payment status
16. Users receive daily status updates: "145/150 payments completed, 5 pending"
**Outcome**: Business user processes 150 payments in 10 minutes with built-in approval workflow, CoP validation, and audit trail. Dual authorization prevents unauthorized payments while maintaining efficiency.

### Scalability and Growth

**User Growth**: MVP targets 10,000 users in first 3 months, scaling to 200,000 by month 12. Architecture supports 1 million users with current infrastructure, 10 million with horizontal scaling of application and database tiers.

**Transaction Volume**: MVP targets 50,000 transactions/month, scaling to 2 million by month 12. Payment processing infrastructure supports 100 transactions/second sustained, 500 TPS peak with auto-scaling.

**Geographic Expansion**: MVP focuses on UK market (FPS, BACS, CHAPS). Phase 2 adds SEPA Credit Transfer for Eurozone payments. Phase 3 adds SWIFT for international payments outside SEPA zone.

**Product Expansion**: MVP focuses on person-to-person and business payments. Phase 2 adds payment requests (request money from contacts), payment links (shareable payment URLs), and subscription management. Phase 3 adds merchant payments (QR code, NFC), loyalty integration, and expense management.

**Regulatory Expansion**: MVP obtains UK FCA authorization as Authorized Payment Institution. Phase 2 obtains passporting rights for EU operations under PSD2. Phase 3 obtains e-money license for stored value accounts.

### Long-Term Roadmap

| Phase | Focus | Timeframe |
|-------|-------|-----------|
| MVP (Phase 1) | Core payments (FPS, BACS), KYC, biometric auth, CoP, basic fraud detection | Months 1-9 |
| Phase 2 | CHAPS, Open Banking PISP, batch payments, payment requests, enhanced fraud analytics | Months 10-18 |
| Phase 3 | SEPA payments, international transfers (SWIFT), merchant payments (QR/NFC), expense management | Months 19-30 |
| Phase 4 | Stored value accounts (e-money license), multi-currency wallets, FX services, savings integration | Months 31-42 |
| Phase 5 | Embedded finance (API for third-party integration), white-label solution, B2B2C partnerships | Months 43+ |

## MVP Scope

### MVP Objective

Deliver a mobile payments application enabling UK users to send and receive FPS and BACS payments with biometric authentication and KYC verification, meeting all PSD2 and MLR 2017 regulatory requirements for FCA authorization.

### MVP Success Criteria

- [ ] 10,000 registered users complete KYC verification within first 3 months of launch
- [ ] 90% of KYC verifications complete within 24 hours (auto-approval or manual review)
- [ ] 95% of biometric authentication attempts succeed on first try
- [ ] 98% of FPS payments execute successfully (excluding user errors like insufficient funds)
- [ ] <0.3% fraud rate measured as fraudulent transaction value / total transaction value
- [ ] 100% of payments include CoP check with user confirmation for mismatches
- [ ] Zero critical security incidents (data breach, unauthorized access, payment fraud >£10k)
- [ ] FCA authorization as Small Payment Institution obtained before public launch
- [ ] App Store rating >4.5 stars with >100 reviews within first 3 months

### Features In Scope (MVP)

| Feature | Description | Priority | Rationale |
|---------|-------------|----------|-----------|
| User Registration & Login | Email/password registration, biometric login (fingerprint/face), PIN fallback | P0 | Foundation for all user access; biometric login is table stakes for mobile payments |
| KYC Verification | Document capture (passport/driving licence), selfie with liveness, PEP/sanctions screening, verification status tracking | P0 | Regulatory requirement under MLR 2017; cannot process payments without verified identity |
| Recipient Management | Add recipient (sort code, account number, name), save recipient, recipient list, delete recipient | P0 | Core capability for payment initiation; saved recipients reduce data entry errors |
| FPS Payment Execution | Initiate FPS payment, enter amount and reference, CoP check with mismatch handling, biometric authorization with dynamic linking, payment status tracking | P0 | Primary payment method for MVP; FPS provides instant payments that users expect |
| BACS Payment Execution | Initiate BACS payment (3-day processing), enter amount and reference, CoP check, biometric authorization, scheduled payment tracking | P0 | Essential for lower-cost, non-urgent payments; business users require BACS for payroll and supplier payments |
| Transaction History | List of sent/received payments, payment details (amount, recipient, date, status, reference), search and filter by date/recipient/amount | P0 | Users need visibility of payment activity for reconciliation and dispute resolution |
| Fraud Detection (Basic) | Device fingerprinting, velocity limits (max 10 payments/day, £5k/day for new users), sanctions screening, manual review queue for high-risk transactions | P0 | Regulatory requirement and fraud loss mitigation; basic controls prevent majority of fraud |
| Push Notifications | Payment status updates (sent, completed, failed), security alerts (new device login, biometric enrollment change), fraud warnings | P0 | Critical for user awareness of payment status and security events; reduces support contacts |
| Account Settings | View/edit profile, change password, manage biometric enrollment, view payment limits, communication preferences | P1 | Self-service reduces support load; users expect control over security settings |
| Customer Support (Basic) | In-app FAQ, contact support form, support ticket tracking | P1 | Essential for user assistance; in-app support reduces abandonment vs email/phone |

### Features Explicitly Out of Scope

| Feature | Reason for Deferral | Target Phase |
|---------|---------------------|--------------|
| CHAPS Payments | Low volume use case (high-value property transactions); complex same-day cut-off time management; FPS covers 99% of user needs | Phase 2 (Month 10-18) |
| Open Banking PISP | Requires additional PSD2 authorization as PISP; adds integration complexity with 20+ UK banks; FPS/BACS from user's existing bank account sufficient for MVP | Phase 2 (Month 10-18) |
| Batch Payments (CSV Upload) | Business user feature with low initial demand; complex validation and approval workflow; individual payments sufficient for MVP business users | Phase 2 (Month 10-18) |
| Payment Requests | Requires bidirectional payment flow and notification system; adds UX complexity; users can communicate payment requests via other channels (SMS, WhatsApp) | Phase 2 (Month 10-18) |
| International Payments (SEPA, SWIFT) | Requires additional regulatory authorization, FX provider integration, and correspondent banking relationships; UK-only focus for MVP | Phase 3 (Month 19-30) |
| Merchant Payments (QR, NFC) | Requires merchant onboarding, acceptance infrastructure, and settlement process; consumer-to-consumer payments are core MVP focus | Phase 3 (Month 19-30) |
| Stored Value Accounts | Requires e-money license from FCA; adds complexity of balance management, interest calculation, and FSCS protection; MVP uses pass-through payments only | Phase 4 (Month 31-42) |
| Multi-Currency Wallets | Requires FX provider integration, currency conversion pricing, and multi-currency balance management; GBP-only sufficient for UK MVP | Phase 4 (Month 31-42) |

### MVP User Journeys

#### MVP Journey 1: First-Time User Registration and Payment (Simplified)
1. User downloads app, creates account with email/password
2. User enrolls fingerprint for biometric login
3. User completes KYC: captures passport photo and selfie
4. System verifies identity (auto-approved in 30 seconds for 85% of users)
5. User adds recipient: enters sort code, account number, name
6. System performs CoP check: displays "Exact match - John Smith"
7. User enters amount (£50), selects FPS, adds reference
8. User authorizes with fingerprint (dynamic linking shows amount and recipient)
9. System performs fraud check: low risk, payment submitted to FPS
10. User receives push notification: "Payment sent - £50 to John Smith"
**Limitations vs Full Vision**: No CHAPS or Open Banking options. No batch payments. Basic fraud detection only (no behavioral analytics). No payment scheduling (future-dated or recurring).

#### MVP Journey 2: Business User Sending Multiple Supplier Payments (Simplified)
1. Business user logs in with biometric authentication
2. User sends first payment: adds recipient (supplier 1), enters amount (£1,200), reference ("Invoice 12345"), selects BACS
3. System performs CoP check, user authorizes with biometric
4. User sends second payment: selects saved recipient (supplier 2), enters amount (£800), reference ("Invoice 12346"), selects BACS
5. User authorizes with biometric
6. User repeats for 8 more suppliers (total 10 payments)
7. User views transaction history: sees all 10 payments with status "Scheduled for BACS processing"
8. User receives push notification next day: "10 payments submitted to BACS"
9. User receives push notification 3 days later: "10 payments completed"
**Limitations vs Full Vision**: No CSV upload (must enter payments individually). No multi-user approval workflow. No payment templates. Manual entry for each payment increases time and error risk.

### MVP Constraints and Assumptions

**Constraint**: KYC provider (Onfido) SLA is 95% verification within 4 hours, 5% require manual review up to 24 hours. **Risk if wrong**: If manual review rate exceeds 15% or SLA degrades, user abandonment will spike above 35%, missing user acquisition targets.

**Constraint**: FPS availability is 99.9% per scheme rules, but our payment access provider (Form3) adds additional dependency. **Risk if wrong**: If combined availability falls below 99%, user trust erodes and support costs spike due to "payment not working" complaints.

**Assumption**: 85% of UK users have biometric-capable devices (iPhone 5S+, Android 6.0+). 15% will use PIN fallback. **Risk if wrong**: If biometric adoption is lower, authentication friction increases, reducing conversion and increasing fraud risk from weaker PIN authentication.

**Assumption**: CoP exact match rate will be 82% (industry average), close match 10%, no match 8%. Users will accept close matches 70% of time. **Risk if wrong**: If no-match rate exceeds 15%, user friction increases significantly as users must contact recipients to verify account details, reducing payment completion rate.

**Assumption**: Average payment value is £150, average user sends 8 payments/month. **Risk if wrong**: If average value is lower or frequency is lower, transaction fee revenue will miss projections, requiring pricing adjustment or cost reduction.

**Constraint**: MVP targets Small Payment Institution authorization (€3M monthly payment volume limit). **Risk if wrong**: If user adoption exceeds projections and volume approaches limit within first 6 months, must accelerate Authorized Payment Institution application, adding 6-month delay and £200k cost.

**Assumption**: Fraud rate will be <0.3% with basic device fingerprinting and velocity limits. **Risk if wrong**: If fraud rate exceeds 0.5%, fraud losses will consume 60% of transaction fee revenue, requiring investment in advanced fraud analytics (£150k) and manual review team expansion (+3 FTEs).

### MVP Definition of Done

- [ ] iOS and Android apps published to App Store and Google Play with age rating 4+ (iOS) / Everyone (Android)
- [ ] User registration, login, and biometric enrollment functional with <2 second response time
- [ ] KYC verification integrated with Onfido, achieving 90% completion rate within 24 hours in production testing
- [ ] FPS and BACS payment execution functional with CoP integration, achieving 98% success rate in production testing
- [ ] Biometric authentication with dynamic linking implemented per PSD2 requirements, achieving 95% first-attempt success rate
- [ ] Device fingerprinting and velocity limits active, with fraud rate <0.3% in production testing
- [ ] Push notifications functional for payment status, security alerts, and fraud warnings
- [ ] Transaction history displays all payment details with search and filter capability
- [ ] FCA Small Payment Institution authorization obtained (or application submitted with interim permissions)
- [ ] Security audit completed by third-party firm with zero critical findings
- [ ] Penetration testing completed with all high/critical vulnerabilities remediated
- [ ] GDPR compliance verified: privacy policy published, consent management functional, DSAR workflow tested
- [ ] Load testing completed: 100 TPS sustained, 500 TPS peak, <1 second p95 response time
- [ ] Disaster recovery tested: RTO <4 hours, RPO <15 minutes
- [ ] Customer support documentation complete: FAQ, troubleshooting guides, escalation procedures
- [ ] App Store rating >4.5 stars in beta testing with >50 beta testers

## Risks and Dependencies

### Key Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| FCA authorization delayed beyond 9 months, blocking public launch | Medium | Critical | Start authorization application in Month 1 (parallel with development). Engage FCA-specialist consultancy to guide application. Prepare fallback: soft launch to closed beta under interim permissions while awaiting full authorization. |
| KYC provider (Onfido) manual review rate exceeds 15%, causing user abandonment >35% | Medium | High | Negotiate SLA with penalty clauses. Implement secondary KYC provider (Jumio) as failover. Optimize document capture UX to reduce poor-quality submissions. Monitor manual review rate daily and escalate to Onfido account manager if threshold breached. |
| Payment access provider (Form3) outage causes payment service disruption >4 hours | Low | Critical | Negotiate 99.95% SLA with financial penalties. Implement health check monitoring with automatic failover to secondary provider (Token) if outage detected. Maintain hot standby integration with secondary provider. |
| Biometric authentication adoption <70%, increasing fraud risk and authentication friction | Medium | High | Implement progressive onrollment: allow users to start with PIN, prompt biometric enrollment after first successful payment. Provide in-app education on biometric benefits (speed, security). Track adoption rate weekly and adjust UX if below target. |
| Fraud rate exceeds 0.5% due to inadequate fraud controls in MVP | Medium | High | Implement conservative velocity limits (£2k/day for first 30 days). Require manual review for first payment >£500 to new recipient. Monitor fraud rate daily with automatic alert if >0.4%. Accelerate Phase 2 fraud analytics if threshold breached. |
| GDPR breach due to inadequate data protection, resulting in ICO fine and reputational damage | Low | Critical | Engage GDPR specialist for compliance audit before launch. Implement encryption at rest and in transit for all personal data. Conduct annual penetration testing. Implement data breach response plan with 72-hour notification procedure. Maintain cyber insurance with £5M coverage. |
| App Store rejection due to payment/financial app policy violations | Medium | Medium | Review App Store and Google Play payment app policies in Month 1. Engage app review consultancy with payment app expertise. Submit early beta builds for pre-review feedback. Prepare detailed policy compliance documentation for app review submission. |

### External Dependencies

| Dependency | Owner | Status | Risk Mitigation |
|------------|-------|--------|-----------------|
| FCA Small Payment Institution Authorization | FCA Authorizations Team | Not started (Month 1) | Engage FCA consultancy to prepare application. Submit in Month 1 to allow 6-9 month review period. Prepare interim permissions application if delays occur. |
| Onfido KYC Verification Service | Onfido (Contract signed) | Active | 99.5% SLA with penalty clauses. Secondary provider (Jumio) integrated as failover. Monthly service review meetings. |
| Form3 Payment Scheme Access | Form3 (Contract signed) | Active | 99.95% SLA with financial penalties. Secondary provider (Token) on standby. Quarterly business review meetings. |
| Apple Touch ID / Face ID APIs | Apple | Active | Native iOS APIs, no contract required. Monitor iOS release notes for API changes. Maintain compatibility with iOS 14+. |
| Android Fingerprint / Face Unlock APIs | Google | Active | Native Android APIs, no contract required. Monitor Android release notes for API changes. Maintain compatibility with Android 8.0+. |
| CoP Service (Pay.UK) | Pay.UK via Form3 | Active | Mandatory for FPS per scheme rules. Included in Form3 contract. No separate dependency. |
| Cloud Infrastructure (AWS) | AWS | Active | Multi-AZ deployment for high availability. Auto-scaling for traffic spikes. Reserved instances for cost optimization. |

### Open Questions

**Question 1**: What is the optimal balance between fraud prevention friction and user experience? Specifically, should we require manual review for all first payments >£500, or only for payments to new recipients flagged as high-risk by device fingerprinting?
- **Impact**: Affects fraud rate, user abandonment, and operational cost (manual review team size)
- **Owner**: Product Manager + Fraud Analyst
- **Resolution needed by**: Month 3 (before fraud rules finalization)

**Question 2**: Should MVP support joint accounts (two users sharing one payment account) or defer to Phase 2? Joint accounts add complexity to KYC (both users must verify), authorization (who can approve payments?), and liability (who is responsible for fraud?).
- **Impact**: Affects 15-20% of potential users (couples, business partners) but adds 3-4 weeks to development timeline
- **Owner**: Product Manager + Compliance Officer
- **Resolution needed by**: Month 2 (before account model finalization)

**Question 3**: What is the appropriate daily payment limit for new users (first 30 days)? Industry ranges from £1k (conservative, low fraud) to £5k (permissive, high conversion). Higher limits increase fraud risk but reduce user friction.
- **Impact**: Affects fraud rate, user satisfaction, and revenue (higher limits enable higher transaction volume)
- **Owner**: Fraud Analyst + Product Manager
- **Resolution needed by**: Month 4 (before fraud rules finalization)

**Question 4**: Should we support payment references with emojis (increasingly common in consumer payments) or restrict to alphanumeric characters only? Emojis improve UX but may cause issues with legacy banking systems that don't support Unicode.
- **Impact**: Affects user experience and payment scheme compatibility
- **Owner**: Product Manager + Payment Operations
- **Resolution needed by**: Month 5 (before payment UX finalization)

**Question 5**: What is the customer support model for MVP? In-app chat with human agents (high cost, high satisfaction) vs FAQ + email support (low cost, lower satisfaction)? Budget allows for 2 FTE support agents, sufficient for 10k users with 5% monthly contact rate.
- **Impact**: Affects user satisfaction, support cost, and operational complexity
- **Owner**: Product Manager + Customer Support Lead
- **Resolution needed by**: Month 6 (before support infrastructure build)