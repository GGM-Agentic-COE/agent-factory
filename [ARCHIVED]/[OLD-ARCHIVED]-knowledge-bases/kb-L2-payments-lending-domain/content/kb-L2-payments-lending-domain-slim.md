# Payments & Lending Domain Knowledge Base (Vision-Optimised)
### kb-L2-payments-lending-domain v1.0.0-slim
### Optimised for: vision-generator, requirements-extractor, epics-generator
### Contains: PM implications (what to build), user journeys (full), state machines (full), glossary (full)
### Removed: field-level schemas, validation rules, API implementation detail, regulatory full-text

---

### kb-L2-payments-domain v1.0.0
### Domain knowledge for UK consumer lending. All agents creating epics, stories, or designs for lending products MUST ground their decisions in this KB.
## PD1: Lending Lifecycle
### Customer Journey

1. **Discovery** — Customer encounters loan product via comparison site, direct marketing, or in-app promotion. FCA financial promotions rules (CONC 3) require representative APR and risk warnings in all ads.
2. **Eligibility Check** — Soft-search pre-qualification. No credit footprint. Returns indicative rate and limit. Must not constitute a credit agreement offer (CCA s.60).
3. **Application** — Full data capture (see PD2). FCA expects adequate explanations of the product (CONC 4.2.5R).
4. **KYC / Verification** — Identity verification (MLR 2017 reg.28), address verification, income verification. Electronic verification preferred; manual fallback required.
5. **Credit Decision** — Hard search at CRA, affordability assessment, automated or referred decision (see PD3).
6. **Offer** — Binding pre-contract credit information (SECCI) per CCA s.55A. Must include APR, total amount payable, repayment schedule, right to withdraw.
7. **Acceptance** — Customer accepts offer. 14-day withdrawal right begins (CCA s.66A).
8. **Disbursement** — Funds transferred via Faster Payments (typically < 2 hours) or BACS (next working day).
9. **Repayment** — Direct Debit collection via Bacs scheme. Continuous Payment Authority (CPA) restricted to two failed attempts for high-cost short-term credit (CONC 7.6.12R).
10. **Settlement / Closure** — Early settlement per CCA s.94. Settlement figure valid 28 days (CCA s.97). Account closed, CRA updated within 30 days.

### Lender Journey

1. **Product Configuration** — Define rate bands, term ranges, fee structures, eligibility rules, scorecard thresholds.
2. **Lead Capture** — Ingest applications from direct channel, broker API, or aggregator feed.
3. **Application Processing** — Validate completeness, de-duplicate, enrich with CRA data.
4. **Identity Verification** — KYC checks against PEP/sanctions lists, document verification (passport/driving licence), liveness check where applicable.
5. **Credit Assessment** — CRA hard search, internal scorecard, policy rules engine.
6. **Affordability Check** — Income vs expenditure analysis, ONS benchmark comparison, stress test at +3pp interest rate.
7. **Offer Generation** — Risk-based pricing, fee calculation, APR computation (see PD4), SECCI document generation.
8. **Agreement Execution** — E-signature capture (eIDAS-compliant), agreement storage (6 years post-closure per FCA SYSC 9.1.1R).
9. **Funds Transfer** — Payment initiation via Faster Payments / BACS. Reconciliation against bank statement.
10. **Servicing** — Statement generation, payment processing, balance enquiries, complaints handling (DISP rules).
11. **Collections** — Arrears management per CONC 7.3 (treat customers fairly), forbearance options, income & expenditure review.
12. **Write-off / Closure** — Debt sale or write-off, CRA default registration (6 years), account closure.

### Loan State Machine

| State | Trigger | Validations | Next States | Timeout |
|---|---|---|---|---|
| **Draft** | Customer starts application | None | Submitted, Abandoned | 30 days inactivity → Abandoned. Abandoned apps: data retained 90 days (customer can resume), then purged. Customer notified at 7 days and 21 days of inactivity. |
| **Submitted** | Customer completes & submits | All mandatory fields populated, consent captured | IdentityVerification | — |
| **IdentityVerification** | Submission accepted | KYC provider call, PEP/sanctions screen, document check | CreditCheck (pass), Referred (inconclusive), Closed (fail) | 7 days → Closed |
| **CreditCheck** | Identity verified | CRA hard search, scorecard evaluation, policy rules | AffordabilityCheck (pass), Referred (marginal), Closed (decline) | — |
| **AffordabilityCheck** | Credit check passed | Income verification, expenditure analysis, stress test | Approved (pass), Referred (marginal), Closed (decline) | — |
| **Referred** | Any check inconclusive | Manual underwriter review, additional docs requested | Approved, Closed | 14 days → Closed |
| **Approved** | All checks passed or underwriter approves | Final policy check, rate lock | OfferGenerated | 24 hours → OfferGenerated (auto) |
| **OfferGenerated** | Approval confirmed | APR calculation, SECCI generation, fee schedule | OfferSent | — |
| **OfferSent** | Offer dispatched to customer | Delivery confirmation (email/SMS/in-app) | OfferAccepted, Closed (declined/expired) | 30 days → Closed |
| **OfferAccepted** | Customer accepts offer | Acceptance timestamp, IP address, device fingerprint | AgreementSigned | 7 days → Closed |
| **AgreementSigned** | E-signature captured | Signature validation, agreement PDF stored | Disbursing | — |
| **Disbursing** | Agreement executed | Bank account validation (CoP check), payment initiation | Active (funds confirmed), Disbursing (retry on failure) | 3 retries → Referred |
| **Active** | Funds received by customer | Repayment schedule activated, DD mandate confirmed | InArrears, Settled, Closed | — |
| **InArrears** | Payment missed (DD failure + 3 day grace) | Arrears notification (CONC 7.3.4R), forbearance assessment | Active (payment received), Default (90+ days), Settled | — |
| **Default** | 90+ days in arrears or 3 consecutive missed payments | Default notice issued (CCA s.87), CRA default registered | Settled (full payment), Closed (write-off/debt sale) | — |
| **Settled** | Full balance paid (including early settlement) | Settlement figure reconciliation, CRA update | Closed | — |
| **Closed** | Settlement confirmed, write-off, or application terminated | Final CRA update, record retention flag set | Terminal state | — |

### PM IMPLICATION

Every state transition is a notification trigger (email/SMS/push), a dashboard status update, and a compliance checkpoint. Epics must include notification templates, status tracking UI, and audit logging for each transition. Stories should map 1:1 to state transitions where possible. The 14-day withdrawal right (CCA s.66A) after acceptance requires a dedicated "withdrawal" flow that reverses disbursement — this is a separate epic.

---

## PD2: Loan Origination
### Application Data Model
### Address History
### Employment Types & Impact on Application
### Income Verification by Type
### Document Requirements by Applicant Type
### Auto-Save
### Joint Applications
### Guarantor Loans
### Top-Up Loans
### PM IMPLICATION

Each employment type drives a different form path with conditional fields, different document upload requirements, and different income verification logic. Epics must include: (1) a dynamic form engine or branching logic per employment type, (2) document upload with OCR/classification, (3) Open Banking integration for auto-verification, (4) address lookup integration (PAF/OS Places), (5) auto-save with encryption. Stories should be sliced by employment type — each type is effectively a separate user journey through the same form. Joint applications, guarantor loans, and top-up loans are common product variants that each require distinct user journeys and should be planned as separate epics or feature sets.

---

## PD3: Affordability & Creditworthiness
### Creditworthiness Assessment (FCA CONC 5.2A)
### Affordability Assessment (FCA CONC 5.2A.20R)
### Open Banking Affordability
### Debt Burden Ratio (DBR)
### Responsible Lending Obligation
### PM IMPLICATION

The application must collect granular expenditure data (not just a single "monthly outgoings" field) to enable ONS benchmark comparison. Stories must include: (1) expenditure breakdown form with ONS-aligned categories, (2) automated ONS benchmark flagging (if declared < benchmark, trigger manual review), (3) disposable income calculator shown to underwriters, (4) stress test results displayed alongside base-case affordability, (5) decline reason notification flow with CRA details. The affordability model is a separate microservice/module — it must be independently testable and auditable.

---

## PD4: Pricing, Fees & APR
### Interest Rate Types
### APR Calculation
### Fee Types & UK Regulatory Caps
### Total Amount Payable
### Representative Example (FCA-Required Format)
### PM IMPLICATION

The offer screen is the most heavily regulated screen in the application. Every fee must be visible, the representative example must be displayed in the FCA-mandated format, and the total amount payable must be prominent. Epics must include: (1) APR calculation engine (iterative solver, independently auditable, tested against FCA worked examples), (2) offer screen with full representative example, (3) fee schedule display, (4) early repayment calculator (with correct cap applied based on remaining term), (5) rate change notification flow for variable-rate products. The APR engine is complex — it should be a separate, well-tested service. Stories should cover: offer screen layout, APR calculation accuracy tests, fee cap enforcement, early settlement quote generation, and representative example rendering across all channels (web, mobile, email, PDF).

---

## PD5: Loan Offers & Agreements
### Pre-Contract Information
### PCCI (Pre-Contract Credit Information)
### Credit Agreement
### Right to Withdraw
### Offer Expiry
### Execution Process
### PM IMPLICATION

The acceptance flow is legally prescribed — you cannot skip the PCCI, cannot hide the cooling-off right, and the e-signature must be legally valid. The withdrawal flow is often forgotten in product builds but is a legal requirement. Epics must include: (1) PCCI generation and display, (2) acceptance flow with e-signature capture, (3) agreement PDF generation and storage, (4) cooling-off period tracking, (5) withdrawal request flow (initiation, principal repayment, interest calculation, confirmation), (6) offer expiry management and re-application flow. Stories should cover: PCCI rendering across channels, e-signature capture and validation, agreement document generation, withdrawal happy path, withdrawal after disbursement (funds must be returned), offer expiry notification, and re-application after expiry.

---

## PD6: Disbursement
### Payment Methods
### Faster Payments Detail
### Timing: Immediate vs Cooling-Off
### Account Verification
### Failed Disbursement
### Confirmation
### PM IMPLICATION

Disbursement has critical edge cases: bank rejection, frozen account, withdrawal after disbursement (funds already sent, must be recovered). Stories must cover: (1) successful disbursement via FPS, (2) successful disbursement via BACS, (3) failed disbursement with retry, (4) failed disbursement with account update, (5) disbursement confirmation notifications, (6) cooling-off interaction (withdrawal before disbursement, withdrawal after disbursement with recovery flow), (7) CoP name mismatch handling. The disbursement status must be clearly visible in the customer dashboard and internal servicing tools.

---

## PD7: Repayment & Collections
### Repayment
### Collections
### Breathing Space (Debt Respite Scheme 2021)
### PM IMPLICATION

Collections is heavily regulated with specific timelines and prescribed notices. The customer dashboard must show arrears status clearly. Notifications must follow the prescribed timeline and include mandatory content (debt advice signposting). Epics must include: (1) repayment schedule display and recalculation, (2) Direct Debit setup and management, (3) overpayment flow with term/payment choice, (4) arrears detection and automated reminder sequence, (5) formal arrears notice generation (CCA s.86B compliant), (6) default warning and registration flow, (7) forbearance request and management, (8) collections dashboard for internal teams. Stories must cover: normal repayment view, arrears dashboard, each stage of the collections timeline, forbearance request flow, debt advice signposting, CRA reporting, and default registration. Do not forget the Direct Debit Guarantee — customers can reclaim payments, and the system must handle indemnity claims.

---

## PD8: Early Repayment & Settlement
### Legal Right
### Settlement Figure Calculation
### Settlement Figure Validity
### Compensation Caps
### Partial Early Repayment
### Settlement Process
### PM IMPLICATION

Early settlement is a key differentiator for fintechs — zero fees should be prominent in marketing and the in-app experience. The settlement figure calculation must be penny-accurate and independently auditable. Epics must include: (1) settlement figure calculator (actuarial method, tested against worked examples), (2) settlement figure display (amount, validity date, payment instructions), (3) partial early repayment flow (lump sum input, term vs payment choice, schedule recalculation), (4) full settlement payment flow, (5) post-settlement confirmation and document generation, (6) CRA update on settlement. Stories must cover: settlement figure request and display, partial vs full settlement choice, payment execution, confirmation, CRA update, settlement letter generation, figure expiry and recalculation, and the edge case where a scheduled Direct Debit is collected after settlement (must be refunded).

---

## PD9: Payment Processing
### UK Payment Schemes
### Faster Payments Detail
### BACS Processing Cycle
### Direct Debit Lifecycle
### Payment Statuses
### Reconciliation
### Payment References
### Sort Code Validation
### Confirmation of Payee (CoP)
### Open Banking Payments
### PM IMPLICATION

Payment processing has multiple failure points and each must be handled gracefully. Stories must cover: (1) successful payment via each method (FPS, BACS, DD, card, Open Banking), (2) failed payment with specific reason codes (insufficient funds, account closed, invalid details), (3) Direct Debit setup flow (mandate creation, AUDDIS submission, confirmation), (4) Direct Debit cancellation by customer (ADDACS notification handling, alternative payment arrangement), (5) DD indemnity claim handling (refund to customer's bank, impact on loan balance, customer communication), (6) reconciliation discrepancy investigation and resolution, (7) Confirmation of Payee name mismatch (warn customer, allow override or correction), (8) payment reference generation and validation, (9) suspense account management, (10) Open Banking payment initiation flow. The payment status must be visible in both customer-facing and internal dashboards, with clear indication of next steps for failed or returned payments.

---

## PD10: PSD2 & Strong Customer Authentication (SCA)
### PM IMPLICATION

SCA affects multiple user flows. Login can use biometric (one factor) for low-risk access, but loan acceptance and payment initiation need two factors. Stories must specify which SCA level each action requires. The dynamic linking requirement means the biometric prompt for loan acceptance must show the loan amount.

---

## PD11: KYC & Identity Verification
### PM IMPLICATION

KYC is not just "upload your ID". It's a multi-step process with multiple outcomes. Stories must cover: document selection, camera capture with quality guidance, selfie with liveness, OCR review, verification status tracking, retry on failure, manual review escalation, sanctions/PEP screening (even if automated, the result must be handled). The referred state is critical — what happens when auto-verification fails but the customer might still be legitimate?

---

## PD12: FCA Consumer Duty
### PM IMPLICATION

Consumer Duty affects EVERY screen. Product listing must not mislead. Offer screen must be crystal clear. Dashboard must make repayment easy. Early repayment must not be hidden. Complaints must be accessible. Stories should include acceptance criteria like: "a customer with no financial background can understand the total cost from the offer screen without external help".

---

## PD13: Consumer Credit Act 1974 (as amended)
### PM IMPLICATION

CCA compliance is not optional — non-compliance makes the loan unenforceable (the lender cannot recover the money). Every story that touches the agreement, offer, or repayment flow must have acceptance criteria that reference the relevant CCA section. The agreement generation feature must include ALL prescribed terms. The settlement figure feature must respond within 7 working days (s.97).

---

## PD14: GDPR in Lending
### PM IMPLICATION

GDPR affects the entire application flow. The privacy notice must be shown before data collection starts. Consent for marketing must be separate and optional (not bundled with T&Cs). The DSAR flow needs a story (even if it's a back-office process). Automated decision-making disclosure is required if using AI for credit scoring. Stories for data collection screens must specify the lawful basis in acceptance criteria.

---

## PD15: Vulnerable Customers
### PM IMPLICATION

Vulnerability is not a separate feature — it's a lens applied to every feature. Stories should include acceptance criteria like: "screen is usable with TalkBack at 200% text size", "if affordability check shows high debt-to-income ratio, system flags for manual review", "collections notifications use empathetic language and include debt advice contacts". Consider adding a "need help?" option on every screen that connects to human support.

---

## PD16: Complaints & Dispute Resolution
### PM IMPLICATION

Complaints handling needs its own epic or at minimum a set of stories. In-app: "Submit a complaint" flow, complaint status tracking, FOS information display. Back-office: complaint logging, assignment, investigation, response generation, FOS escalation tracking. Acceptance criteria must include the 5-day acknowledgment and 8-week resolution timelines.

---

## PD17: Domain Glossary

Key terms used in UK consumer lending. Agents MUST use these terms consistently.

| Term | Definition |
|------|------------|
| APR | Annual Percentage Rate — the total cost of credit expressed as an annual percentage, including interest and mandatory fees. Calculated per CCA formula. |
| APRC | Annual Percentage Rate of Charge — used for mortgages (MCD), similar to APR but includes more cost components. |
| Arrears | When a borrower has missed one or more scheduled payments. Measured in months (1 month in arrears = 1 missed payment). |
| BACS | Bankers' Automated Clearing Services — UK payment system for Direct Debits and bank transfers. 3-day cycle. |
| CCJ | County Court Judgment — court order to repay a debt. Stays on credit file for 6 years. |
| CCA | Consumer Credit Act 1974 (as amended) — primary UK legislation governing consumer credit agreements. |
| CDD | Customer Due Diligence — identity verification required under Money Laundering Regulations. |
| CONC | Consumer Credit sourcebook — FCA's rules for consumer credit firms. |
| CoP | Confirmation of Payee — name-checking service that verifies account holder name before payment. |
| CRA | Credit Reference Agency — Experian, Equifax, or TransUnion. Holds credit file data. |
| DDI | Direct Debit Instruction — the mandate authorising a firm to collect payments from a customer's bank account. |
| Default | Formal notice that a borrower has failed to meet their obligations. Registered with CRAs, stays 6 years. |
| DISP | Dispute Resolution sourcebook — FCA's rules for complaints handling. |
| DMP | Debt Management Plan — informal arrangement to repay debts at reduced rate. |
| DSAR | Data Subject Access Request — GDPR right to obtain all personal data held by a firm. |
| EDD | Enhanced Due Diligence — additional identity checks for higher-risk customers (PEPs, high-risk countries). |
| FCA | Financial Conduct Authority — UK regulator for financial services firms. |
| Forbearance | Arrangements made with a borrower in financial difficulty (payment holiday, reduced payments, term extension). |
| FOS | Financial Ombudsman Service — independent body that resolves complaints between consumers and financial firms. |
| FPS | Faster Payments Service — UK real-time payment system. Funds arrive in seconds, 24/7. |
| Hard search | Credit check that leaves a visible footprint on the credit file. Other lenders can see it. Used for full applications. |
| IVA | Individual Voluntary Arrangement — formal agreement with creditors to repay debts over time. |
| KYC | Know Your Customer — the process of verifying a customer's identity and assessing risk. |
| MLR | Money Laundering Regulations 2017 — UK regulations implementing EU Anti-Money Laundering Directives. |
| ONS | Office for National Statistics — provides expenditure benchmarks used in affordability assessments. |
| PCCI | Pre-Contract Credit Information — standardised document that must be provided before a credit agreement. |
| PEP | Politically Exposed Person — individual who holds or has held a prominent public function. Requires EDD. |
| PSD2 | Payment Services Directive 2 — EU directive (retained in UK law) regulating payment services. Introduces SCA and Open Banking. |
| Representative APR | The APR that at least 51% of successful applicants will receive. Must be shown in advertising. |
| SCA | Strong Customer Authentication — two-factor authentication required by PSD2 for electronic payments and account access. |
| Settlement figure | The amount needed to repay a loan in full today. Includes principal, accrued interest, fees, minus any rebate. |
| Soft search | Credit check that does NOT leave a visible footprint. Used for eligibility checks and quotations. |
| Total amount payable | The total the borrower will pay over the life of the loan: principal + interest + all fees. Must be disclosed. |
| Total charge for credit | The total cost of credit to the borrower: interest + all mandatory fees. Used in APR calculation. |
| AISP | Account Information Service Provider — regulated entity that can access bank account data with customer consent under PSD2. Used for Open Banking affordability. |
| APP fraud | Authorised Push Payment fraud — customer is tricked into sending money to a fraudster. |
| Breathing space | Debt Respite Scheme (2021) — 60-day moratorium protecting debtors from creditor action. Interest and charges frozen. |
| CPA | Continuous Payment Authority — recurring card payment. Restricted to 2 failed attempts for high-cost credit (CONC 7.6.12R). |
| PISP | Payment Initiation Service Provider — regulated entity that can initiate payments from customer's bank account under PSD2. |
| SAR | Suspicious Activity Report — filed with National Crime Agency when fraud or money laundering is suspected. |
| VRP | Variable Recurring Payment — Open Banking payment with variable amounts within agreed parameters. Emerging capability. |
| AUDDIS | Automated Direct Debit Instruction Service — electronic system for setting up and cancelling Direct Debit mandates. |
| ADDACS | Automated Direct Debit Amendment and Cancellation Service — notifies originators of changes to or cancellations of DDIs. |
| ARUDD | Automated Return of Unpaid Direct Debits — notification that a Direct Debit collection has been returned unpaid. |
| Counter-offer | When a customer is declined for the requested amount but approved for a lower amount or different terms. |
| DBR | Debt Burden Ratio — total monthly debt obligations divided by net monthly income. Used to assess affordability. |
| I&E | Income and Expenditure review — detailed assessment of customer's financial situation for affordability and restructuring. |
| Liability letter | Formal document stating outstanding loan balance, remaining term, and monthly payment. |
| Notice of Correction | Statement (up to 200 words) a customer can add to their credit file to explain circumstances. |
| Restructuring | Formal change to loan terms when forbearance is insufficient. Creates a new credit agreement. |
| Settlement letter | Document confirming loan fully repaid and account closed. Issued after settlement. |
| SFS | Standard Financial Statement — standardised format for income and expenditure reviews. |

---

## PD18: Product Configuration & Eligibility
### Product Parameters
### Eligibility Rules
### Rate Tiering (Risk-Based Pricing)
### Product Governance (FCA PROD rules)
### PM IMPLICATION

Product configuration drives the entire eligibility and offer flow. Stories must cover: product catalog display (with representative APR and key facts), eligibility pre-check (soft search, instant result), rate personalisation (show personal rate after eligibility), product comparison (side-by-side for multiple products), and product governance reporting (arrears rate, complaints rate per product). The eligibility rules are the first filter — they determine what the customer sees before they even start an application.

---

## PD19: Loan Servicing & Account Management
### Statements
### Account Changes
### Interest Rate Changes (Variable Rate Products)
### Annual Percentage Rate Statement
### Liability Letters & Statements on Demand
### Communication Preferences
### PM IMPLICATION

Servicing is the longest phase of the loan lifecycle but often gets the least product attention. Stories must cover: annual statement generation and delivery, on-demand statement request, transaction history view, change of address/name/bank details flows (each with verification), rate change notification (variable products), communication preference management, and the distinction between marketing communications (opt-in) and regulatory communications (mandatory). The change-of-bank-details flow is particularly important — it's a common fraud vector and needs strong verification.

---

## PD20: Fraud Prevention
### Application Fraud Types
### Fraud Detection Signals
### Fraud Rules Engine
### Authorised Push Payment (APP) Fraud
### Regulatory Obligations
### PM IMPLICATION

Fraud prevention must be embedded in the application flow, not bolted on. Stories must cover: device fingerprinting at app install, velocity checks during application, KYC liveness as anti-fraud (not just compliance), income verification cross-checks, fraud referral queue for operations team, SAR filing workflow (back-office), and the balance between fraud prevention and customer friction (too many checks = abandonment, too few = fraud losses). The fraud rules engine is a separate system that needs its own configuration stories.

---

## PD21: Open Banking
### Account Information Services (AISP)
### Payment Initiation Services (PISP)
### Variable Recurring Payments (VRP)
### Customer Experience
### PM IMPLICATION

Open Banking is a major differentiator for fintechs. Stories must cover: AISP consent flow (bank selection, redirect, return), transaction data display (categorised income/expenditure), affordability calculation using Open Banking data, PISP payment flow (for repayments and settlement), consent management (view active consents, revoke consent), re-authentication every 90 days, multi-bank aggregation, and fallback for customers who decline Open Banking (document upload path). The consent flow involves leaving the lender's app and returning — this must be seamless and handle all error cases (timeout, decline, bank app crash).

---

## PD22: Financial Promotions
### CONC 3: Financial Promotions
### Required Content
### Prominence Rules
### Social Media & Digital
### Record Keeping
### PM IMPLICATION

Every screen that shows a loan product with any cost figure is a financial promotion. The product catalog, eligibility result, comparison page, and marketing emails all need representative APR and representative example. Stories must cover: product listing with compliant representative example, eligibility result display (personal rate + representative APR), marketing email templates with required content, push notification content compliance, and a financial promotions approval workflow (legal/compliance review before any promotion goes live).

---

## PD23: Refunds & Adjustments
### Refund Scenarios
### Refund Methods
### Regulatory Requirements
### PM IMPLICATION

Refunds are often forgotten in product builds but are a regulatory requirement. Stories must cover: overpayment refund (automatic detection and processing), post-settlement DD refund (detect DD after settlement, auto-refund), compensation payment (manual trigger from complaints team), fee reversal (operations tool), and the edge case of refunding to a closed account. The refund status must be visible to the customer in their dashboard.

---

## PD24: Credit Reporting Obligations
### Monthly Reporting
### What Triggers CRA Updates
### Customer Disputes
### PM IMPLICATION

Credit reporting is an ongoing operational obligation. Stories must cover: monthly CRA reporting batch job, real-time CRA updates for defaults and settlements, customer dispute handling workflow, and CRA data accuracy monitoring.

---

## PD25: Loan Restructuring
### Restructuring Options
### Legal Requirements
### Income & Expenditure Review
### PM IMPLICATION

Restructuring needs: I&E collection form, restructuring option calculation, old vs new terms comparison display, new agreement signing flow, CRA update, and updated repayment schedule.
