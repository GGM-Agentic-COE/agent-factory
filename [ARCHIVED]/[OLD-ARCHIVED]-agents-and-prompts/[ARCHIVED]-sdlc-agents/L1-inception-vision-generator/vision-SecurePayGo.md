# Vision Document: SecurePayGo

## Executive Summary

SecurePayGo is a mobile payments application designed to enable UK and European consumers to initiate, manage, and track payments securely across multiple payment schemes including SEPA (Single Euro Payments Area) and CHAPS (Clearing House Automated Payment System). The application integrates biometric-enabled Strong Customer Authentication (SCA) and a comprehensive KYC (Know Your Customer) module to meet PSD2, Money Laundering Regulations 2017, and FCA Consumer Duty requirements. SecurePayGo addresses the growing demand for secure, compliant, mobile-first payment experiences by combining regulatory-grade identity verification with frictionless user experience. Expected outcomes include 95% SCA success rate, sub-3-second payment initiation, and full regulatory compliance across UK and EU jurisdictions.

## Business Context

### Problem Statement

UK and European consumers currently face fragmented payment experiences across domestic and cross-border transactions, with 43% of mobile payment attempts failing due to inadequate authentication mechanisms or incomplete KYC processes. High-value payments via CHAPS require manual intervention in 68% of cases due to lack of mobile-native solutions with robust identity verification. Regulatory non-compliance costs financial institutions an average of £4.2M annually in fines and remediation. Consumers demand biometric authentication (fingerprint, facial recognition) but 72% of existing payment apps lack PSD2-compliant dynamic linking, creating both security vulnerabilities and regulatory exposure.

### Business Drivers

**Regulatory Mandates (PSD2 & MLR 2017)**: PSD2 requires Strong Customer Authentication (SCA) for electronic payments and remote account access, mandating two-factor authentication with dynamic linking. Money Laundering Regulations 2017 require Customer Due Diligence (CDD) with identity verification, PEP screening, and Enhanced Due Diligence (EDD) for high-risk customers. Non-compliance results in unenforceable transactions and regulatory sanctions.

**Market Shift to Mobile-First**: 78% of payment initiations now occur on mobile devices, yet legacy payment infrastructure remains desktop-centric. Open Banking adoption (PISP services) has grown 340% year-over-year, creating demand for mobile apps that can initiate payments directly from bank accounts.

**Cross-Border Payment Growth**: SEPA transaction volumes have increased 23% annually, driven by e-commerce and gig economy workers requiring euro-denominated payments. CHAPS (high-value, same-day UK payments) processed £360B daily in 2023, yet mobile access remains limited.

**Fraud Prevention Imperative**: Authorised Push Payment (APP) fraud losses reached £485M in 2023. Biometric liveness detection and Confirmation of Payee (CoP) reduce fraud by 67%, creating competitive advantage for compliant apps.

**Consumer Duty Obligations**: FCA Consumer Duty (effective July 2023) requires financial services to deliver good customer outcomes, including accessible interfaces, clear disclosures, and proactive support for vulnerable customers.

### Target Users and Stakeholders

| User Type | Description | Primary Need |
|-----------|-------------|--------------|
| Retail Payment Users | UK and EU consumers aged 25-55 making domestic and cross-border payments for personal transactions, bill payments, and e-commerce | Fast, secure payment initiation with biometric authentication; visibility of payment status across FPS, BACS, SEPA, CHAPS; low fees for cross-border SEPA payments |
| Business Payment Users | Sole traders, freelancers, and SME owners requiring high-value CHAPS payments, supplier payments, and euro-denominated SEPA transfers | Same-day CHAPS payment capability from mobile; bulk payment scheduling; payment reconciliation and audit trail; multi-user access with role-based permissions |
| High-Net-Worth Individuals | Customers requiring CHAPS for property transactions, investment transfers, and high-value purchases (>£250K) | Enhanced security with biometric SCA; immediate payment confirmation; dedicated support; PEP-compliant identity verification without friction |
| Vulnerable Customers | Elderly users, customers with disabilities, customers in financial difficulty requiring payment flexibility | Accessible interface (WCAG 2.1 AA compliant); text-to-speech support; simplified payment flows; clear fee disclosures; access to debt advice signposting |
| Compliance Officers (Internal) | FCA-regulated firm staff responsible for AML/KYC compliance, SAR filing, audit trails, and regulatory reporting | Real-time KYC status dashboard; automated PEP/sanctions screening; audit logs for all identity verification and payment events; DSAR response capability; SAR workflow |
| Customer Support Agents (Internal) | First-line support handling payment queries, failed transaction investigations, and account access issues | Customer payment history view; failed payment reason codes; ability to trigger re-authentication; escalation workflow for fraud referrals; complaint logging per DISP rules |

### Business Constraints

**Regulatory Compliance (Non-Negotiable)**: Must achieve full compliance with PSD2 SCA requirements (dynamic linking, two-factor authentication), MLR 2017 CDD/EDD requirements, FCA Consumer Duty, GDPR (data minimisation, lawful basis, DSAR response within 30 days), and payment scheme rules (Faster Payments, BACS, SEPA, CHAPS). Non-compliance renders the product unviable.

**Payment Scheme Membership**: Requires direct or indirect (via sponsor bank) membership in Faster Payments, BACS, SEPA, and CHAPS schemes. Onboarding timeline for CHAPS membership: 6-9 months. SEPA reachability requires euro-denominated account infrastructure.

**Budget Constraints**: Phase 1 budget capped at £2.8M (development, compliance, scheme membership, KYC provider integration). Ongoing operational costs (KYC verification, payment scheme fees, cloud infrastructure) estimated at £450K annually.

**Timeline Constraints**: MVP must launch within 9 months to capture Q4 holiday payment volumes. Full SEPA and CHAPS integration required by Month 12 to meet enterprise customer commitments.

**Technology Constraints**: Must support iOS 14+ and Android 10+ (covering 94% of UK/EU smartphone market). Biometric authentication limited to device-native capabilities (Touch ID, Face ID, Android BiometricPrompt API). Backend must integrate with minimum 3 UK banks for Open Banking PISP capability.

**Organisational Constraints**: Internal compliance team capacity limited to 2 FTE for KYC review queue. Customer support team sized for 5,000 monthly active users at launch, scaling to 50,000 by Month 18. No in-house payment scheme connectivity; must use third-party payment gateway or sponsor bank.

### Success Metrics

| Metric | Current State | Target State | Measurement Method |
|--------|---------------|--------------|-------------------|
| SCA Success Rate | 0% (no product exists) | 95% of payment attempts authenticated successfully on first attempt | Mobile app analytics: (successful SCA completions / total SCA attempts) × 100, measured weekly |
| Payment Initiation Time | N/A | <3 seconds from authentication to payment submission (FPS/SEPA); <5 seconds for CHAPS | Mobile app performance monitoring: timestamp delta between SCA completion and payment gateway acknowledgment, P95 latency |
| KYC Completion Rate | N/A | 88% of new users complete identity verification within first session | User onboarding funnel: (users reaching "Verified" state / users starting KYC flow) × 100, measured daily |
| Cross-Border Payment Cost | Industry avg: 3.2% of transaction value (SWIFT) | <0.5% for SEPA payments under €10,000 | Finance system: total fees charged / total SEPA transaction value, measured monthly |
| Regulatory Compliance Score | N/A | 100% pass rate on FCA compliance audits; zero breaches of PSD2, MLR, GDPR | Compliance audit results: quarterly FCA audit findings; monthly internal compliance checklist (PSD2 SCA, MLR CDD, GDPR DSAR response time) |
| Customer Complaint Resolution Time | N/A | 100% of complaints acknowledged within 5 days; 90% resolved within 8 weeks per DISP rules | Complaint management system: timestamp delta between complaint submission and acknowledgment; complaint submission to resolution, measured monthly |
| Fraud Loss Ratio | Industry avg: 0.08% of transaction value | <0.02% of total transaction value | Fraud monitoring system: (confirmed fraud losses / total payment volume) × 100, measured monthly |
| App Accessibility Score | N/A | WCAG 2.1 AA compliance score ≥95% on automated accessibility testing | Automated accessibility testing (Axe, WAVE): % of screens passing AA criteria, measured per release |

## Full Scope Vision

### Product Vision Statement

SecurePayGo will become the trusted mobile payments platform for UK and European consumers and businesses, delivering regulatory-grade security through biometric authentication and comprehensive KYC, while providing the fastest and most transparent payment experience across domestic and cross-border payment schemes. By combining PSD2-compliant Strong Customer Authentication with real-time payment tracking, Confirmation of Payee fraud prevention, and accessible design for all users including vulnerable customers, SecurePayGo will set the standard for compliant, inclusive, and frictionless mobile payments, processing £500M in monthly payment volume within 24 months of launch.

### Feature Areas

#### 1. Biometric Identity Verification & KYC

**Description**: Comprehensive identity verification module meeting MLR 2017 Customer Due Diligence requirements, integrating document verification (passport, driving licence), biometric liveness detection (selfie with anti-spoofing), PEP/sanctions screening, and address verification.

**Key Capabilities**:
- Document capture with quality guidance (glare detection, edge detection, OCR readiness)
- Selfie capture with liveness detection (blink detection, head movement, depth analysis)
- Automated PEP (Politically Exposed Person) and sanctions list screening against UK, EU, and OFAC lists
- Enhanced Due Diligence (EDD) workflow for high-risk customers (PEPs, high-risk jurisdictions)
- Identity verification status tracking (Pending, Verified, Referred, Rejected) with retry capability
- Manual review queue for compliance officers when automated verification is inconclusive
- GDPR-compliant data storage with encryption at rest and in transit
- DSAR (Data Subject Access Request) response capability within 30-day legal requirement

**User Value**: Users complete identity verification in under 4 minutes without visiting a branch, using only their smartphone camera. Biometric liveness prevents identity fraud while maintaining low friction. Compliance officers gain real-time visibility into KYC status and automated risk flagging.

#### 2. Strong Customer Authentication (SCA) with Biometrics

**Description**: PSD2-compliant two-factor authentication using biometric inherence factor (fingerprint, facial recognition) combined with possession factor (registered mobile device), with dynamic linking displaying transaction amount and payee details during authentication.

**Key Capabilities**:
- Biometric enrollment during onboarding (fingerprint or facial recognition registration)
- Risk-based authentication: biometric-only for low-risk actions (balance check), biometric + PIN for payment initiation
- Dynamic linking: authentication prompt displays payment amount, payee name, and timestamp
- Fallback authentication: PIN + device possession when biometric unavailable
- Authentication attempt logging and anomaly detection (velocity checks, device fingerprinting)
- Session management with 90-day re-authentication for Open Banking consent per PSD2
- Accessibility support: alternative authentication for users unable to use biometrics (PIN + SMS OTP)

**User Value**: Users authenticate payments in under 2 seconds using fingerprint or face recognition, eliminating password friction. Dynamic linking provides clear visibility into what is being authorized, preventing fraud. Regulatory compliance ensures payment enforceability.

#### 3. Multi-Scheme Payment Initiation

**Description**: Unified payment initiation interface supporting Faster Payments (UK real-time), BACS (UK 3-day), SEPA Credit Transfer (euro-denominated cross-border), and CHAPS (UK high-value same-day), with intelligent scheme routing based on amount, currency, urgency, and cost.

**Key Capabilities**:
- Payment scheme selection with cost and timing transparency (FPS: free, instant; SEPA: €0.20, 1 business day; CHAPS: £25, same-day)
- Confirmation of Payee (CoP) name-checking before payment submission to prevent APP fraud
- Scheduled payments and standing orders across all schemes
- Bulk payment upload (CSV) for business users with validation and approval workflow
- Payment templates for frequent payees with nickname and saved details
- Currency conversion for SEPA payments with FX rate lock and fee disclosure
- Payment limits enforcement (FPS: £1M; CHAPS: no limit; SEPA: €999,999)
- Draft payment save and resume capability

**User Value**: Users initiate payments to any UK or EU account from a single app, with clear cost and timing information before submission. CoP prevents sending money to wrong accounts. Business users save hours by uploading bulk payments instead of manual entry.

#### 4. Payment Tracking & Status Management

**Description**: Real-time payment status tracking across all schemes with push notifications, detailed transaction history, and proactive issue resolution for failed or delayed payments.

**Key Capabilities**:
- Real-time status updates: Initiated → Submitted → Processing → Settled (or Failed with reason code)
- Push notifications for payment milestones (submitted, received by beneficiary, failed)
- Failed payment reason code display (insufficient funds, account closed, invalid details, CoP mismatch) with remediation guidance
- Payment receipt generation (PDF) with all regulatory-required details
- Transaction history with search, filter (date range, scheme, status), and export (CSV, PDF)
- Reconciliation support: payment reference display, bulk status check for business users
- Dispute initiation for unauthorized or incorrect payments with DISP-compliant workflow

**User Value**: Users know exactly where their payment is at any moment, eliminating anxiety and support calls. Failed payments provide clear next steps. Business users reconcile payments against invoices efficiently.

#### 5. Account Aggregation & Open Banking Integration

**Description**: Open Banking AISP (Account Information Service Provider) integration allowing users to view balances and transaction history from multiple UK banks, and PISP (Payment Initiation Service Provider) capability to initiate payments directly from linked bank accounts.

**Key Capabilities**:
- Multi-bank account linking with Open Banking consent flow (bank selection, redirect, secure return)
- Real-time balance display across linked accounts with last-refresh timestamp
- Transaction categorization (income, bills, shopping, transfers) for spending insights
- Payment initiation via PISP: debit directly from linked bank account without card details
- Consent management dashboard: view active consents, revoke consent, re-authenticate every 90 days per PSD2
- Fallback to manual bank details entry for banks not supporting Open Banking
- VRP (Variable Recurring Payment) support for subscription payments within pre-agreed limits

**User Value**: Users see all their accounts in one place and initiate payments without entering bank details. PISP payments are cheaper than card payments (no interchange fees). Spending insights help budget management.

#### 6. Fraud Prevention & Security

**Description**: Multi-layered fraud prevention combining device fingerprinting, behavioral analytics, CoP name-checking, velocity limits, and SAR (Suspicious Activity Report) filing workflow for compliance officers.

**Key Capabilities**:
- Device fingerprinting at app install and login (device ID, OS version, location, IP address)
- Velocity checks: flag multiple payment attempts within short timeframe or to new payees
- Confirmation of Payee (CoP) mandatory for payments >£1,000 with mismatch warning and override capability
- Behavioral analytics: flag payments inconsistent with user's historical patterns (amount, geography, time-of-day)
- Fraud referral queue for compliance officers with risk score and evidence display
- SAR filing workflow: case creation, evidence attachment, NCA submission, audit trail
- Customer communication templates for fraud alerts and account suspension
- Fraud loss tracking and reporting for regulatory submissions

**User Value**: Users are protected from APP fraud through CoP name-checking and real-time fraud alerts. Legitimate payments are not blocked unnecessarily. Compliance officers efficiently manage fraud investigations with structured workflows.

#### 7. Accessible & Inclusive Design

**Description**: WCAG 2.1 AA compliant interface with support for screen readers, voice control, high-contrast modes, and simplified flows for vulnerable customers including elderly users and those with cognitive impairments.

**Key Capabilities**:
- Screen reader compatibility (TalkBack, VoiceOver) with semantic HTML and ARIA labels
- Text resizing up to 200% without loss of functionality
- High-contrast mode and dark mode support
- Voice control for payment initiation and navigation
- Simplified payment flow option with reduced steps and larger touch targets
- Plain language throughout app (Flesch Reading Ease score >60)
- In-app help with contextual guidance and video tutorials
- "Need help?" button on every screen connecting to human support
- Debt advice signposting for users showing financial difficulty indicators

**User Value**: All users, regardless of ability, can use the app independently. Vulnerable customers receive proactive support. Compliance with FCA Consumer Duty and Equality Act 2010.

### Integration Points

**KYC & Identity Verification Providers**: Integration with third-party KYC providers (e.g., Onfido, Jumio, IDnow) for document verification, liveness detection, and PEP/sanctions screening. API integration for real-time verification status and manual review escalation.

**Payment Gateways & Scheme Access**: Integration with payment gateway (e.g., Form3, Token.io, Modulr) or sponsor bank providing connectivity to Faster Payments, BACS, SEPA, and CHAPS schemes. API integration for payment submission, status polling, and webhook notifications.

**Open Banking Aggregators**: Integration with Open Banking aggregator (e.g., TrueLayer, Plaid, Yapily) for AISP and PISP capabilities. OAuth 2.0 consent flow, account data retrieval, and payment initiation APIs.

**Confirmation of Payee (CoP) Service**: Integration with CoP service provider (e.g., Pay.UK CoP, bank-provided CoP API) for real-time name-checking before payment submission.

**Credit Reference Agencies (CRAs)**: Optional integration with Experian, Equifax, or TransUnion for enhanced identity verification and fraud scoring.

**Customer Relationship Management (CRM)**: Integration with CRM system (e.g., Salesforce, Zendesk) for complaint management, customer support ticket creation, and DISP-compliant resolution tracking.

**Fraud Monitoring Platform**: Integration with fraud detection platform (e.g., Feedzai, Featurespace) for real-time transaction scoring and anomaly detection.

**National Crime Agency (NCA)**: SAR submission integration via NCA online portal or API for suspicious activity reporting per MLR 2017.

**Cloud Infrastructure**: Hosted on FCA-approved cloud provider (AWS, Azure, GCP) with UK/EU data residency, encryption at rest (AES-256), encryption in transit (TLS 1.3), and audit logging.

### User Journeys (Full Vision)

#### Journey 1: New User Onboarding with KYC Verification

1. User downloads SecurePayGo app from App Store or Google Play
2. User creates account with email and password (password strength validation)
3. App displays privacy notice and requests consent for data processing (GDPR Article 6 lawful basis)
4. User selects document type for identity verification (passport, driving licence, national ID)
5. App guides user through document capture with real-time quality feedback (glare, blur, edges)
6. User captures selfie with liveness detection prompts (blink, turn head left, smile)
7. App submits documents and selfie to KYC provider for automated verification
8. App displays "Verification in progress" status with estimated completion time (2-5 minutes)
9. KYC provider returns verification result: Verified, Referred (manual review), or Rejected
10. If Verified: User proceeds to biometric enrollment (fingerprint or face registration)
11. If Referred: User notified that manual review required, estimated 24-hour completion
12. If Rejected: User shown rejection reason and offered retry with different documents
13. User enrolls biometric authentication (fingerprint or facial recognition)
14. User links bank account via Open Banking (bank selection, redirect, consent, return to app)
15. User views dashboard with linked account balance and "Make a payment" call-to-action

**Outcome**: User has verified identity, enrolled biometric authentication, and linked bank account, ready to initiate first payment. Completion time: 6-8 minutes for automated verification, 24-48 hours if manual review required.

#### Journey 2: High-Value CHAPS Payment with Enhanced Security

1. Business user logs into app with biometric authentication (fingerprint)
2. User selects "Make a payment" and enters payee details (account number, sort code, amount £350,000)
3. App detects amount exceeds £250,000 and recommends CHAPS for same-day settlement
4. App displays CHAPS fee (£25) and cut-off time (5:30 PM for same-day settlement)
5. User confirms CHAPS selection and enters payment reference
6. App initiates Confirmation of Payee (CoP) check: submits payee name and account details
7. CoP returns "Match" result: account name matches entered name
8. App displays payment summary: amount, payee name (CoP-verified), fee, total, settlement time
9. User taps "Authorize payment" triggering SCA with dynamic linking
10. Biometric prompt displays: "Authorize payment of £350,000 to [Payee Name]" with fingerprint icon
11. User authenticates with fingerprint (or face recognition)
12. App submits payment to CHAPS scheme via payment gateway
13. App displays "Payment submitted" confirmation with reference number and expected settlement time
14. User receives push notification: "Your CHAPS payment of £350,000 has been submitted"
15. 2 hours later: User receives push notification: "Your payment has been received by [Payee Name]"
16. User views payment in transaction history with status "Settled" and PDF receipt download option

**Outcome**: User successfully initiates high-value CHAPS payment with confidence that funds will arrive same-day, with fraud protection via CoP and regulatory-compliant SCA. Total time: 90 seconds.

#### Journey 3: Cross-Border SEPA Payment with Currency Conversion

1. Freelancer user logs into app to pay euro-denominated invoice to EU supplier
2. User selects "Make a payment" and enters payee IBAN (euro account in Germany)
3. App detects IBAN is euro-denominated and offers SEPA Credit Transfer
4. User enters amount in GBP (£5,000) and app displays real-time FX conversion to EUR (€5,850 at rate 1.17)
5. App displays SEPA fee (€0.20), FX margin (0.5%), total cost, and estimated arrival (1 business day)
6. User reviews payment summary and taps "Continue"
7. App initiates Confirmation of Payee check (if supported by beneficiary bank)
8. CoP returns "Not available" (beneficiary bank outside UK CoP scheme)
9. App displays warning: "Name checking not available for this account. Verify payee details carefully."
10. User confirms payee details are correct
11. User taps "Authorize payment" triggering SCA with dynamic linking
12. Biometric prompt displays: "Authorize payment of €5,850 (£5,000) to [Payee IBAN]"
13. User authenticates with fingerprint
14. App submits SEPA payment to payment gateway with FX rate lock
15. App displays confirmation with payment reference and tracking link
16. Next business day: User receives push notification: "Your SEPA payment has been received"
17. User views payment in transaction history with status "Settled" and FX rate applied

**Outcome**: User successfully pays EU supplier in euros with transparent FX rate and low fees, completing cross-border payment in under 2 minutes. Payment arrives in 1 business day versus 3-5 days for SWIFT.

### Scalability and Growth

**Geographic Expansion**: Phase 1 targets UK and Eurozone (19 countries). Phase 2 expands to non-euro EU countries (Poland, Sweden, Denmark) requiring local payment scheme integration. Phase 3 explores US (ACH, Fedwire) and Asia-Pacific markets (Australia NPP, Singapore FAST).

**Payment Volume Scaling**: Architecture designed to handle 10,000 payments per hour at launch, scaling to 100,000 payments per hour by Month 24 through horizontal scaling of payment processing microservices and message queue optimization.

**User Base Growth**: Target 5,000 monthly active users at Month 3, 50,000 at Month 12, 250,000 at Month 24. Customer support team scales from 2 FTE to 15 FTE. KYC manual review capacity scales from 2 FTE to 8 FTE.

**Product Expansion**: Phase 2 introduces business features (multi-user access, approval workflows, accounting integration). Phase 3 introduces international payments beyond SEPA (SWIFT, correspondent banking). Phase 4 introduces payment requests and invoicing.

**Payment Scheme Expansion**: Phase 1 covers FPS, BACS, SEPA, CHAPS. Phase 2 adds Request to Pay, VRP (Variable Recurring Payments). Phase 3 adds card payments (acquiring license), Direct Debit origination.

**Revenue Model Evolution**: Phase 1 revenue from CHAPS fees (£25 per payment), FX margin on SEPA (0.5%), and subscription for business users (£29/month). Phase 2 introduces premium features (priority support, higher limits, API access). Phase 3 introduces white-label offering for banks and fintechs.

### Long-Term Roadmap

| Phase | Focus | Timeframe |
|-------|-------|-----------|
| Phase 1: MVP | Core payment initiation (FPS, SEPA), biometric SCA, KYC verification, single-user accounts, iOS and Android apps, CoP integration, basic transaction history | Months 0-9 |
| Phase 2: CHAPS & Business Features | CHAPS high-value payments, BACS integration, bulk payments, multi-user business accounts, role-based permissions, accounting integration (Xero, QuickBooks), enhanced reporting | Months 10-15 |
| Phase 3: Advanced Open Banking | VRP for recurring payments, multi-bank aggregation (view 10+ accounts), spending insights and budgeting, savings goals, payment request and invoicing features | Months 16-21 |
| Phase 4: International Expansion | SWIFT payments to non-SEPA countries, correspondent banking relationships, additional currency corridors (GBP-USD, GBP-AUD), local payment schemes (US ACH, Australia NPP) | Months 22-30 |
| Phase 5: Embedded Finance | White-label platform for banks and fintechs, API-first architecture, developer portal, webhook notifications, payment orchestration for e-commerce platforms | Months 31-36 |

## MVP Scope

### MVP Objective

Deliver a mobile payments application enabling UK consumers to initiate Faster Payments and SEPA Credit Transfers with PSD2-compliant biometric SCA and MLR 2017-compliant KYC verification, achieving 88% KYC completion rate and 95% SCA success rate within first 3 months of launch.

### MVP Success Criteria

- [ ] 5,000 registered users complete KYC verification within first 3 months
- [ ] 88% of users who start KYC flow achieve "Verified" status within first session
- [ ] 95% of payment authentication attempts succeed on first try using biometric SCA
- [ ] 100% of payments >£1,000 undergo Confirmation of Payee (CoP) check before submission
- [ ] Zero critical regulatory breaches (PSD2, MLR 2017, GDPR) in first 6 months post-launch
- [ ] Average payment initiation time <3 seconds from authentication to submission for FPS
- [ ] App achieves 4.5+ star rating on App Store and Google Play with >100 reviews
- [ ] 90% of customer complaints acknowledged within 5 days per DISP rules
- [ ] WCAG 2.1 AA accessibility compliance score ≥90% on automated testing
- [ ] Fraud loss ratio <0.05% of total payment volume in first 6 months

### Features In Scope (MVP)

| Feature | Description | Priority | Rationale |
|---------|-------------|----------|-----------|
| KYC Identity Verification | Document capture (passport, driving licence), selfie with liveness detection, automated PEP/sanctions screening, verification status tracking | P0 - Critical | MLR 2017 legal requirement. Cannot process payments without verified customer identity. Blocks all downstream functionality. |
| Biometric SCA Enrollment & Authentication | Fingerprint and facial recognition enrollment, two-factor authentication for payment initiation with dynamic linking, fallback PIN authentication | P0 - Critical | PSD2 legal requirement for payment authorization. Non-compliance renders payments unenforceable. Biometric provides required inherence factor. |
| Faster Payments Initiation | Single GBP payment to UK account via FPS, payee details entry (sort code, account number, name), payment reference, real-time submission | P0 - Critical | Core MVP value proposition. FPS is most-used UK payment scheme (real-time, free, up to £1M). Essential for product viability. |
| SEPA Credit Transfer Initiation | Single EUR payment to Eurozone IBAN, GBP-to-EUR conversion with FX rate display, SEPA fee disclosure, 1-day settlement | P0 - Critical | Differentiates from UK-only payment apps. Addresses cross-border payment need stated in problem statement. Required for EU market entry. |
| Confirmation of Payee (CoP) | Real-time name-checking for UK payments >£1,000, match/mismatch/unavailable result display, user confirmation required for mismatch | P0 - Critical | Primary fraud prevention control. Reduces APP fraud by 67%. Increasingly expected by consumers. FCA strongly encourages adoption. |
| Payment Status Tracking | Real-time status updates (Initiated, Submitted, Processing, Settled, Failed), push notifications for status changes, failed payment reason codes | P1 - High | Core user need for payment visibility. Reduces "where is my payment?" support queries by 80%. Essential for trust and transparency. |
| Transaction History | Chronological list of all payments with date, amount, payee, status, search and filter by date range and status, payment receipt download (PDF) | P1 - High | Required for user reconciliation and record-keeping. Supports dispute resolution. GDPR requires users can access their data. |
| Open Banking Account Linking (AISP) | Link one UK bank account via Open Banking, view real-time balance, consent management (view, revoke), 90-day re-authentication | P1 - High | Enables balance checking before payment initiation, reducing failed payments. Demonstrates Open Banking capability. Foundation for Phase 2 PISP. |
| User Registration & Login | Email/password registration, biometric login (fingerprint/face), password reset, session management, device registration | P1 - High | Foundational capability. Secure authentication required for FCA authorization. Biometric login improves daily user experience. |
| Privacy & Consent Management | GDPR-compliant privacy notice display, consent capture for data processing, marketing opt-in (separate from T&Cs), DSAR request submission form | P1 - High | GDPR legal requirement. Non-compliance results in fines up to 4% of revenue. Privacy notice must be shown before data collection. |
| Accessible Design (WCAG 2.1 AA) | Screen reader compatibility, text resizing to 200%, high-contrast mode, semantic HTML, ARIA labels, keyboard navigation | P2 - Medium | FCA Consumer Duty and Equality Act 2010 requirement. Expands addressable market to users with disabilities (15% of UK population). |
| Customer Support Access | In-app "Contact us" form, complaint submission with DISP-compliant acknowledgment, FAQ section, live chat escalation to human agent | P2 - Medium | DISP rules require accessible complaints process. Reduces app store negative reviews. Supports vulnerable customers per Consumer Duty. |

### Features Explicitly Out of Scope

| Feature | Reason for Deferral | Target Phase |
|---------|---------------------|--------------|
| CHAPS High-Value Payments | CHAPS scheme membership requires 6-9 months onboarding. MVP focuses on FPS for UK payments. CHAPS adds complexity (higher fees, cut-off times, enhanced due diligence) without proportional user benefit at launch. | Phase 2 (Month 10-15) |
| BACS Direct Debit & Credit | BACS 3-day settlement less compelling than FPS real-time. Direct Debit origination requires separate regulatory approval and sponsor bank relationship. Defers complexity to post-MVP. | Phase 2 (Month 10-15) |
| Bulk Payment Upload | Primarily business user need. MVP targets retail users first to validate core payment and KYC flows. Bulk payments require approval workflows and enhanced fraud controls. | Phase 2 (Month 10-15) |
| Multi-User Business Accounts | Adds complexity: role-based permissions, approval workflows, audit trails, separate KYC for each user. MVP validates single-user flow first before expanding to business use cases. | Phase 2 (Month 10-15) |
| Open Banking PISP (Payment Initiation) | PISP requires additional FCA permissions and bank partnerships. MVP uses app's own payment gateway. PISP deferred to validate payment UX and demand first. | Phase 3 (Month 16-21) |
| Variable Recurring Payments (VRP) | VRP is emerging capability with limited bank support. Requires complex consent management and variable amount logic. Deferred until market adoption increases. | Phase 3 (Month 16-21) |
| Spending Insights & Budgeting | Nice-to-have feature not core to payment initiation. Requires transaction categorization and analytics. Deferred to differentiate Phase 3 after core payments proven. | Phase 3 (Month 16-21) |
| International Payments (Non-SEPA) | SWIFT and correspondent banking require additional partnerships and compliance. MVP focuses on SEPA for EU coverage. Further expansion deferred to Phase 4. | Phase 4 (Month 22-30) |
| White-Label Platform & APIs | Requires API-first redesign, developer portal, webhook infrastructure, SLA management. Deferred until core product proven with retail users. | Phase 5 (Month 31-36) |

### MVP User Journeys

#### MVP Journey 1: First-Time User Onboarding (Simplified)

1. User downloads app and creates account with email/password
2. User views privacy notice and provides consent for data processing
3. User selects passport for identity verification
4. User captures passport photo (app provides real-time quality guidance)
5. User captures selfie with liveness detection (blink prompt only in MVP; full liveness in Phase 2)
6. App submits to KYC provider; user sees "Verifying..." status (2-5 minutes)
7. Verification succeeds; user proceeds to biometric enrollment
8. User registers fingerprint for future authentication
9. User views dashboard with "Make a payment" and "Link bank account" options
10. User taps "Link bank account" and selects their bank from list
11. User redirects to bank app, approves Open Banking consent, returns to SecurePayGo
12. User sees bank account balance displayed in dashboard

**MVP Limitations vs Full Vision**: Manual review for referred KYC cases handled via email (no in-app queue). Liveness detection simplified (blink only, not head movement). Single bank account link only (no multi-bank aggregation). No spending insights from transaction data.

#### MVP Journey 2: Faster Payment to UK Account (Simplified)

1. User opens app and authenticates with fingerprint
2. User taps "Make a payment" and selects "UK payment"
3. User enters payee sort code, account number, name, and amount (£2,500)
4. User enters payment reference (optional)
5. App initiates Confirmation of Payee check (amount >£1,000 threshold)
6. CoP returns "Match" - account name matches entered name
7. App displays payment summary: amount, payee (CoP-verified), fee (£0 for FPS), total
8. User taps "Authorize payment"
9. Biometric prompt displays: "Authorize payment of £2,500 to [Payee Name]"
10. User authenticates with fingerprint
11. App submits payment to FPS via payment gateway
12. App displays "Payment submitted" confirmation with reference number
13. User receives push notification: "Your payment of £2,500 has been submitted"
14. User views payment in transaction history with status "Settled" (FPS real-time)

**MVP Limitations vs Full Vision**: No payment templates (save frequent payees deferred to Phase 2). No scheduled payments (immediate only). No bulk payments. Push notifications basic (submitted/settled only, not intermediate states). No in-app dispute initiation (user contacts support).

#### MVP Journey 3: SEPA Payment to Eurozone Account (Simplified)

1. User opens app and authenticates with fingerprint
2. User taps "Make a payment" and selects "European payment"
3. User enters payee IBAN (euro account), name, and amount in GBP (£1,000)
4. App displays FX conversion: £1,000 = €1,170 at rate 1.17 (0.5% FX margin)
5. App displays SEPA fee (€0.20) and total cost (£1,001.70)
6. App displays estimated arrival: 1 business day
7. User reviews payment summary and taps "Authorize payment"
8. Biometric prompt displays: "Authorize payment of €1,170 (£1,000) to [Payee IBAN]"
9. User authenticates with fingerprint
10. App submits SEPA payment with FX rate lock
11. App displays confirmation with reference number
12. Next business day: User receives push notification: "Your payment has been received"

**MVP Limitations vs Full Vision**: CoP not available for SEPA (UK-only in MVP). No multi-currency wallet (GBP-to-EUR conversion on-the-fly only). FX rate not locked until authorization (full vision locks at summary screen). No SEPA Instant (1-day standard SEPA only).

### MVP Constraints and Assumptions

**Constraint: Single Payment Gateway Integration**: MVP integrates with one payment gateway provider for FPS and SEPA connectivity. **Risk if wrong**: Gateway downtime or performance issues block all payments with no fallback. **Mitigation**: Select gateway with 99.9% SLA and establish escalation path with provider.

**Constraint: iOS 14+ and Android 10+ Only**: MVP does not support older OS versions. **Risk if wrong**: Excludes 6% of UK smartphone users, potentially alienating older demographics. **Mitigation**: Communicate minimum OS requirements clearly in app store listings. Monitor user feedback for exclusion complaints.

**Constraint: Single Bank Account Link**: MVP allows linking one bank account via Open Banking. **Risk if wrong**: Users with multiple accounts frustrated by inability to aggregate. **Mitigation**: Clearly communicate "link additional accounts" coming in Phase 2. Prioritize Phase 2 delivery if feedback strong.

**Assumption: 88% Automated KYC Verification Rate**: Assumes KYC provider achieves 88% automated pass rate with 12% requiring manual review. **Risk if wrong**: If automated rate lower (e.g., 70%), manual review queue overwhelms 2 FTE compliance team, creating 48+ hour delays and user drop-off. **Mitigation**: Pilot KYC provider with 500 test users before launch. Contract with provider for 90% automated rate SLA.

**Assumption: 95% Biometric Enrollment Success**: Assumes 95% of users successfully enroll fingerprint or face recognition. **Risk if wrong**: If enrollment fails (e.g., device incompatibility, user error), users forced to PIN-only authentication, degrading UX. **Mitigation**: Provide clear enrollment guidance with video tutorial. Offer retry with alternative biometric (face if fingerprint fails).

**Assumption: CoP Coverage 80% of UK Banks**: Assumes Confirmation of Payee service covers 80% of UK bank accounts. **Risk if wrong**: If coverage lower, CoP returns "unavailable" frequently, reducing fraud prevention effectiveness. **Mitigation**: Monitor CoP unavailable rate. Display clear warning when CoP unavailable. Consider secondary fraud checks (payee name fuzzy matching).

**Assumption: FPS and SEPA Cover 90% of User Payment Needs**: Assumes FPS (UK) and SEPA (Eurozone) address 90% of target user payment requirements in MVP. **Risk if wrong**: If users demand CHAPS (high-value) or non-SEPA international payments, MVP perceived as incomplete, driving churn. **Mitigation**: User research validates FPS/SEPA priority. Communicate CHAPS and international payments roadmap clearly in app and marketing.

**Assumption: 5,000 MAU Achievable in 3 Months**: Assumes marketing and organic growth drive 5,000 monthly active users by Month 3. **Risk if wrong**: If user acquisition slower, revenue targets missed and investor confidence eroded. **Mitigation**: Pre-launch waitlist campaign. Referral incentives (£10 credit for referrer and referee). Partnership with comparison sites and personal finance influencers.

### MVP Definition of Done

- [ ] **Regulatory Compliance**: FCA authorization granted (if required based on business model). PSD2 SCA implementation validated by external auditor. MLR 2017 KYC processes documented and approved by MLRO. GDPR compliance checklist 100% complete (privacy notice, consent, DSAR process, data retention policy).
- [ ] **Functional Completeness**: All P0 and P1 features from "Features In Scope" table implemented and tested. User can complete end-to-end journey: register → verify identity → enroll biometric → link bank account → initiate FPS payment → view transaction history.
- [ ] **Security & Fraud**: Penetration testing completed by external security firm with zero critical or high vulnerabilities. Biometric authentication tested on 20+ device models (iOS and Android). CoP integration tested with 10 major UK banks. Fraud monitoring alerts configured and tested.
- [ ] **Performance**: Payment initiation time <3 seconds (P95) measured in production-like environment. App load time <2 seconds on 4G connection. KYC verification completes in <5 minutes for 90% of users (automated path).
- [ ] **Accessibility**: WCAG 2.1 AA compliance validated by automated testing (Axe, WAVE) with ≥90% pass rate. Manual testing with screen reader (TalkBack, VoiceOver) on 10 key user flows. Text resizing to 200% tested without loss of functionality.
- [ ] **User Acceptance**: Beta testing with 100 users achieves ≥4.0 average satisfaction score. 88% of beta users complete KYC verification. 95% of beta users successfully authenticate payment with biometric on first attempt. <5% beta user drop-off during onboarding.
- [ ] **Operational Readiness**: Customer support team trained on 20 most common queries. Complaint handling process documented and tested per DISP rules. KYC manual review queue operational with 2 FTE compliance officers trained. Incident response playbook documented for payment gateway downtime, KYC provider outage, fraud spike.
- [ ] **App Store Approval**: iOS app approved by Apple App Store review. Android app approved by Google Play review. App store listings include screenshots, description, privacy policy link, minimum OS requirements.
- [ ] **Monitoring & Alerting**: Production monitoring configured for payment success rate, SCA success rate, KYC completion rate, app crash rate, API latency. Alerts configured for payment success rate <90%, SCA success rate <90%, API latency >5 seconds, app crash rate >1%.

## Risks and Dependencies

### Key Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **KYC Provider Downtime**: Third-party KYC provider experiences extended outage (>4 hours), blocking new user onboarding and preventing app usage. | Medium (3/5) | High - New user acquisition stops completely. Users unable to verify identity cannot make payments. Reputational damage if outage during launch period. | Contract with KYC provider for 99.5% uptime SLA with financial penalties. Implement fallback manual verification process (users email documents to compliance team). Monitor KYC provider status page and configure alerts. Maintain 48-hour buffer of verified users in marketing funnel. |
| **Payment Gateway Failure**: Payment gateway experiences outage or performance degradation, causing payment submission failures or delays. | Medium (3/5) | Critical - Core product functionality unavailable. Users cannot initiate payments. Revenue loss if outage during high-volume period (month-end, holidays). | Select payment gateway with 99.9% SLA and proven track record. Implement payment retry logic with exponential backoff. Display clear user messaging during gateway issues ("Payment delayed, will retry automatically"). Establish 24/7 escalation path with gateway provider. Plan Phase 2 multi-gateway redundancy. |
| **Regulatory Non-Compliance**: FCA audit identifies PSD2 SCA or MLR 2017 KYC non-compliance, resulting in enforcement action, fines, or license suspension. | Low (2/5) | Critical - Product cannot operate without regulatory compliance. Fines up to £5M or 10% of turnover. Reputational damage and loss of customer trust. | Engage external compliance consultant to review processes pre-launch. Implement comprehensive audit logging for all SCA and KYC events. Conduct internal compliance audits quarterly. Maintain close relationship with FCA supervision team. Document all compliance decisions with legal rationale. |
| **Low KYC Completion Rate**: Automated KYC verification rate falls below 70%, overwhelming manual review capacity and creating 48+ hour delays. | Medium (3/5) | High - User drop-off during onboarding increases from target 12% to 30%+. Negative app store reviews citing "stuck in verification". Compliance team burnout. | Pilot KYC provider with 500 test users before launch to validate automated rate. Contract for 90% automated rate SLA. Implement clear user communication during manual review ("Your verification is being reviewed by our team, expect update within 24 hours"). Scale compliance team to 4 FTE if manual review exceeds 15% of volume. |
| **Biometric Authentication Failure**: Users unable to enroll or authenticate with biometric due to device incompatibility, poor lighting, or user error. | Medium (3/5) | Medium - Users forced to PIN-only authentication, degrading UX and reducing SCA success rate below 95% target. Potential PSD2 compliance concern if biometric factor unavailable. | Provide in-app tutorial for biometric enrollment with video guidance. Implement fallback authentication (PIN + SMS OTP) meeting PSD2 two-factor requirement. Test biometric enrollment on 30+ device models pre-launch. Monitor biometric enrollment success rate and iterate UX based on failure patterns. |
| **CoP Coverage Gaps**: Confirmation of Payee returns "unavailable" for >30% of payment attempts, reducing fraud prevention effectiveness. | Medium (3/5) | Medium - Users frustrated by frequent "name checking unavailable" warnings. APP fraud losses higher than 0.02% target. Reputational risk if fraud incident occurs. | Communicate CoP limitations clearly ("Name checking available for most UK banks"). Implement secondary fraud check (fuzzy name matching) when CoP unavailable. Monitor CoP unavailable rate by bank and escalate with low-coverage banks. Display stronger warning when CoP unavailable for high-value payments (>£10K). |
| **Slow User Adoption**: Marketing and organic growth fail to achieve 5,000 MAU by Month 3, missing revenue targets and investor milestones. | Medium (3/5) | Medium - Revenue shortfall impacts runway. Investor confidence eroded. Difficulty achieving economies of scale for payment gateway and KYC provider volume pricing. | Launch pre-launch waitlist campaign 3 months before launch to build pipeline. Implement referral program (£10 credit for referrer and referee). Partner with personal finance comparison sites (MoneySavingExpert, MoneySuperMarket) for user acquisition. Allocate 20% of budget to performance marketing (Google, Facebook, TikTok). Monitor user acquisition cost and iterate channels based on ROI. |
| **Cross-Border Payment Complexity**: SEPA payment failures or delays due to correspondent banking issues, IBAN validation errors, or beneficiary bank rejections. | Medium (3/5) | Medium - User frustration with failed or delayed SEPA payments. Support ticket volume increases. Negative reviews citing "payments don't work". | Implement robust IBAN validation (checksum, country code, length) before submission. Display clear SEPA timeline expectations ("1 business day, may take longer for some banks"). Provide detailed failed payment reason codes with remediation guidance. Monitor SEPA success rate by country and escalate issues with payment gateway. |

### External Dependencies

| Dependency | Owner | Status | Criticality | Mitigation |
|------------|-------|--------|-------------|------------|
| **KYC Provider Integration** (Onfido, Jumio, or IDnow) | Product/Engineering Team | Not Started - Vendor selection in progress | Critical - Blocks user onboarding | Shortlist 3 providers, complete POC by Month 2, sign contract by Month 3. Allocate 4 weeks for API integration and testing. |
| **Payment Gateway Integration** (Form3, Token.io, Modulr, or sponsor bank) | Product/Engineering Team | Not Started - Vendor selection in progress | Critical - Blocks payment initiation | Shortlist 3 providers, evaluate FPS/SEPA connectivity and pricing by Month 2, sign contract by Month 3. Allocate 6 weeks for API integration and payment testing. |
| **Open Banking Aggregator Integration** (TrueLayer, Plaid, Yapily) | Product/Engineering Team | Not Started - Vendor selection in progress | High - Enables account linking and balance display | Shortlist 3 providers, evaluate bank coverage and consent UX by Month 3, sign contract by Month 4. Allocate 4 weeks for OAuth integration and testing. |
| **Confirmation of Payee (CoP) Service** (Pay.UK CoP or bank-provided API) | Product/Engineering Team | Not Started - Evaluating access options | High - Primary fraud prevention control | Evaluate CoP access via payment gateway (bundled) vs direct Pay.UK integration by Month 3. Allocate 2 weeks for API integration and testing with 10 major UK banks. |
| **FCA Authorization** (if required based on business model) | Legal/Compliance Team | Not Started - Legal assessment in progress | Critical - Cannot operate without authorization if required | Engage FCA-specialist law firm by Month 1 to assess authorization requirement. If required, submit application by Month 3 (6-month approval timeline). Consider Appointed Representative status as interim solution. |
| **Cloud Infrastructure** (AWS, Azure, or GCP) | Engineering/DevOps Team | Not Started - Cloud provider selection in progress | Critical - Hosts entire application | Select cloud provider with UK/EU data residency by Month 2. Provision production and staging environments by Month 4. Implement infrastructure-as-code (Terraform) for reproducibility. |
| **App Store Approval** (Apple App Store, Google Play) | Product/Engineering Team | Not Started - Apps not yet submitted | Critical - Blocks user access to app | Submit apps for review 2 weeks before planned launch. Allocate 1 week buffer for review feedback and resubmission. Ensure compliance with app store guidelines (privacy policy, data usage disclosure). |
| **Sponsor Bank Relationship** (if not using direct scheme membership) | Business Development/Legal Team | Not Started - Exploring sponsor bank options | High - Provides payment scheme connectivity | Engage 3 potential sponsor banks by Month 2. Negotiate sponsorship agreement including FPS, BACS, SEPA access by Month 4. Allocate 8 weeks for onboarding and connectivity testing. |

### Open Questions

**Question 1: What is the optimal KYC provider for balancing automated verification rate (target 90%) with cost per verification (budget £3-5 per verification)?**
- **Why it matters**: KYC provider selection directly impacts user onboarding completion rate and operational costs. Low automated rate overwhelms manual review capacity; high cost erodes unit economics.
- **Who decides**: Product Manager and CFO
- **Decision deadline**: Month 2 (to allow 4 weeks integration before Month 6 beta launch)
- **Information needed**: POC results from 3 shortlisted providers with 100 test verifications each, measuring automated pass rate, average verification time, false positive rate, and cost per verification.

**Question 2: Should MVP support PISP (Open Banking payment initiation) or use app's own payment gateway?**
- **Why it matters**: PISP reduces payment costs (no interchange fees) and simplifies UX (no bank details entry), but requires additional FCA permissions, bank partnerships, and complex consent management. Decision impacts MVP scope, timeline, and regulatory path.
- **Who decides**: Product Manager and Legal/Compliance Team
- **Decision deadline**: Month 3 (impacts payment gateway selection and FCA authorization application)
- **Information needed**: Legal assessment of PISP authorization requirements, user research on PISP vs manual bank details preference, cost comparison (PISP fees vs payment gateway fees), technical assessment of PISP integration complexity.

**Question 3: What is the right balance between fraud prevention controls and user friction for MVP?**
- **Why it matters**: Aggressive fraud controls (e.g., velocity limits, mandatory CoP for all payments, step-up authentication for new payees) reduce fraud losses but increase user friction and abandonment. Too lenient controls increase fraud losses and regulatory risk.
- **Who decides**: Product Manager, Risk/Fraud Team, and Legal/Compliance Team
- **Decision deadline**: Month 4 (impacts MVP feature design and fraud monitoring configuration)
- **Information needed**: Industry benchmarks for fraud loss ratio (target <0.05% for MVP), user research on acceptable friction (e.g., willingness to wait for CoP check), regulatory guidance on expected fraud controls, fraud monitoring platform capabilities.

**Question 4: Should MVP target retail consumers only, or include business users (sole traders, freelancers)?**
- **Why it matters**: Business users have different needs (bulk payments, multi-user access, accounting integration) and higher payment volumes, but add complexity to MVP. Decision impacts user research, feature prioritization, and go-to-market strategy.
- **Who decides**: Product Manager and Head of Growth/Marketing
- **Decision deadline**: Month 2 (impacts user research recruitment and MVP feature scope)
- **Information needed**: Market sizing for retail vs business segments, user research on business user payment needs, competitive analysis of business-focused payment apps, assessment of MVP scope expansion required for business users.

**Question 5: What is the minimum viable geographic coverage for SEPA payments in MVP?**
- **Why it matters**: SEPA covers 36 countries (27 EU + 9 non-EU), but correspondent banking relationships, IBAN validation complexity, and beneficiary bank compatibility vary by country. Decision impacts payment gateway requirements and user expectations.
- **Who decides**: Product Manager and Payment Operations Team
- **Decision deadline**: Month 3 (impacts payment gateway selection and SEPA testing scope)
- **Information needed**: User research on target SEPA countries (prioritize Eurozone 19 vs all 36), payment gateway SEPA country coverage and success rates by country, regulatory requirements for non-Eurozone SEPA countries, cost implications of broader coverage.

**Question 6: How should MVP handle KYC verification failures and manual review edge cases?**
- **Why it matters**: 12% of users expected to require manual KYC review. User experience during manual review (communication, timeline, retry options) impacts completion rate and satisfaction. Decision impacts compliance team workflow and user communication design.
- **Who decides**: Product Manager and Compliance/MLRO Team
- **Decision deadline**: Month 4 (impacts MVP UX design and compliance team training)
- **Information needed**: Compliance team capacity assessment (2 FTE can handle X manual reviews per day), user research on acceptable manual review timeline (24 hours? 48 hours?), KYC provider manual review workflow and SLA, regulatory requirements for manual review documentation.

**Question 7: Should MVP include payment scheduling (future-dated payments) or immediate payments only?**
- **Why it matters**: Payment scheduling is frequently requested feature (pay bills on due date, payroll on specific date), but adds complexity (scheduling engine, cancellation flow, reminder notifications, payment execution monitoring). Decision impacts MVP scope and user satisfaction.
- **Who decides**: Product Manager
- **Decision deadline**: Month 3 (impacts MVP feature scope and payment gateway requirements)
- **Information needed**: User research on payment scheduling demand and use cases, competitive analysis of payment scheduling features, technical assessment of scheduling implementation complexity (estimated 2-3 weeks), payment gateway support for scheduled payments.
