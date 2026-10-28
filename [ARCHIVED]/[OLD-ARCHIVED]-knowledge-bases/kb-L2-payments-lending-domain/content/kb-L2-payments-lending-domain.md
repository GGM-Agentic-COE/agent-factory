# Payments & Lending Domain Knowledge Base
### kb-L2-payments-domain v1.0.0
### Domain knowledge for UK consumer lending. All agents creating epics, stories, or designs for lending products MUST ground their decisions in this KB.

---

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

**Personal Information**
| Field | Type | Validation | Regulatory Basis |
|---|---|---|---|
| Full legal name | String | Must match ID document | MLR 2017 reg.28(2) |
| Date of birth | Date | Age ≥ 18 | CCA s.8 (minors excluded) |
| Address history (3 years) | Array of addresses | Continuous, no gaps > 30 days | CRA reporting requirement |
| Residential status | Enum: Homeowner, Tenant, LivingWithFamily, Other | Required for credit scoring | CONC 5.2A |
| Marital status | Enum | Optional but aids affordability | — |
| Number of dependents | Integer | ≥ 0 | Affordability calculation |
| Contact: mobile | String | UK format validated | — |
| Contact: email | String | RFC 5322 validated | — |

**Employment Information**
| Field | Type | Validation |
|---|---|---|
| Employment type | Enum: Employed, SelfEmployed, Contractor, Retired, Student, Unemployed | Drives conditional fields |
| Employer name | String | Required if Employed |
| Job title | String | Required if Employed/Contractor |
| Employment start date | Date | Must be in the past |
| Gross annual income | Currency (GBP) | > 0 |
| Net monthly income | Currency (GBP) | > 0, ≤ gross/12 |

**Financial Information**
| Field | Type | Notes |
|---|---|---|
| Gross annual income | Currency | Primary income |
| Net monthly income | Currency | Take-home pay |
| Other income (monthly) | Currency | Benefits, rental, investments |
| Monthly credit commitments | Currency | Existing loans, cards, HP |
| Monthly housing cost | Currency | Rent or mortgage |
| Monthly living expenditure | Currency | Validated against ONS benchmarks |
| Number of dependents | Integer | Affects expenditure floor |

### Address History

Three years of continuous address history is required for CRA matching and identity verification. Implementation must:
- Use PAF (Royal Mail Postcode Address File) or OS Places API for address lookup and standardisation.
- Allow manual entry fallback for addresses not found in PAF.
- Validate no gaps > 30 days between move-in/move-out dates.
- Store UPRN (Unique Property Reference Number) where available.
- Previous addresses feed into CRA search to link historical credit files.

### Employment Types & Impact on Application

| Employment Type | Minimum Tenure | Income Evidence | Form Path Differences |
|---|---|---|---|
| **Employed** | 3 months (typical) | Latest payslip, P60 | Standard path: employer name, job title, start date |
| **Self-employed** | 2 years trading | SA302 (HMRC tax calc) + 2 years accounts | Additional fields: trading name, company number, accountant details |
| **Contractor** | 6 months contracting history | Contract document, 3 months bank statements | Day rate × contracted days, IR35 status |
| **Retired** | N/A | Pension statement, P60 | Pension income only, no employer fields |
| **Student** | N/A | Typically ineligible | Application may be declined at eligibility stage |
| **Unemployed** | N/A | Benefit award letter | Limited to secured lending or guarantor products |

### Income Verification by Type

| Income Source | Verification Method | Accepted Documents | Auto-Verify Option |
|---|---|---|---|
| PAYE salary | Payslip + bank statement match | Latest payslip, 3 months bank statements | Open Banking (AISP) |
| Self-employment | HMRC tax calculation | SA302 + tax year overview (2 years) | HMRC API integration |
| Pension | Pension provider statement | Annual pension statement, P60 | Open Banking |
| Benefits | DWP award letter | Universal Credit statement | — |
| Rental income | Tenancy agreement + bank statement | AST + 3 months bank statements | Open Banking |
| Investment income | Tax return | SA100 + dividend vouchers | — |

### Document Requirements by Applicant Type

| Applicant Type | Identity (1 required) | Address (1 required) | Income (all required) |
|---|---|---|---|
| Employed | Passport, Driving licence | Utility bill (< 3 months), Bank statement, Council tax bill | Latest payslip, 3 months bank statements |
| Self-employed | Passport, Driving licence | Utility bill, Bank statement | SA302 (2 years), Tax year overview (2 years), 2 years accounts |
| Contractor | Passport, Driving licence | Utility bill, Bank statement | Current contract, 3 months bank statements, 3 months invoices |
| Retired | Passport, Driving licence | Utility bill, Bank statement | Pension statement, P60 |

### Auto-Save

FCA principle of treating customers fairly (CONC 1.1.2G) and general data protection expectations mean the application must auto-save progress. Customers should not be required to re-enter data unnecessarily. Implementation:
- Save on field blur or every 30 seconds.
- Encrypt PII at rest (AES-256) and in transit (TLS 1.2+).
- Draft applications retained for 30 days, then purged.
- Resume via magic link (email) or authenticated session.

### Joint Applications

- Two applicants apply together — both are jointly and severally liable for the full debt
- Combined income used for affordability (both incomes verified independently)
- Both applicants must pass KYC, credit check, and affordability individually AND jointly
- Credit file: a financial association is created between the two applicants at the CRA — this links their credit files permanently until a disassociation is requested
- If one applicant has adverse credit, it affects the joint application even if the other has a clean file
- Both must sign the credit agreement (both e-signatures required)
- Both receive all communications (arrears notices, statements)
- PM IMPLICATION: joint applications double the KYC, credit check, and signature flows. Stories must cover: second applicant data capture, combined affordability calculation, joint agreement signing, and the scenario where one applicant passes but the other fails.

### Guarantor Loans

- A third party (guarantor) agrees to repay if the primary borrower defaults
- Guarantor must pass independent affordability assessment (can they afford the repayments if called upon?)
- Guarantor must receive independent legal advice or adequate explanation (CONC 4.2.5R)
- Guarantor has their own cooling-off right (14 days)
- If borrower defaults, lender must exhaust reasonable steps to collect from borrower before pursuing guarantor
- Guarantor's credit file is affected if the loan defaults
- PM IMPLICATION: guarantor loans add a parallel onboarding flow for the guarantor (KYC, affordability, agreement signing, cooling-off). This is effectively a second user journey within the same application.

### Top-Up Loans

- Existing customer borrows additional funds on a new agreement
- Previous repayment history informs credit decision (internal data advantage)
- Combined exposure must be assessed (total debt to this lender)
- New agreement required (cannot simply increase existing facility for fixed-sum credit)
- Existing Direct Debit may need updating or a second DD set up
- PM IMPLICATION: top-up requires a streamlined application flow (pre-filled data from existing account) but still needs full affordability assessment including the existing loan repayments.

### PM IMPLICATION

Each employment type drives a different form path with conditional fields, different document upload requirements, and different income verification logic. Epics must include: (1) a dynamic form engine or branching logic per employment type, (2) document upload with OCR/classification, (3) Open Banking integration for auto-verification, (4) address lookup integration (PAF/OS Places), (5) auto-save with encryption. Stories should be sliced by employment type — each type is effectively a separate user journey through the same form. Joint applications, guarantor loans, and top-up loans are common product variants that each require distinct user journeys and should be planned as separate epics or feature sets.

---

## PD3: Affordability & Creditworthiness

### Creditworthiness Assessment (FCA CONC 5.2A)

Creditworthiness and affordability are legally distinct assessments under FCA rules. Both must be performed before a credit agreement is entered into (CONC 5.2A.5R).

**CRA Data (Experian / Equifax / TransUnion)**
- Lenders typically query at least one CRA; many query two for coverage.
- Data returned: credit accounts (open/closed), payment history, public records (CCJs, IVAs, bankruptcy), electoral roll, address links, financial associations.

**Soft Search vs Hard Search**
| Aspect | Soft Search | Hard Search |
|---|---|---|
| Visibility to other lenders | No | Yes (for 12 months) |
| Impact on credit score | None | Temporary reduction (typically 5–10 points) |
| Use case | Eligibility check, quotation search | Full application, credit decision |
| Regulatory basis | Not a "credit search" under CCA | Recorded as application search |
| Customer consent required | General consent sufficient | Explicit consent required (CONC 5.2A.15R) |

**Credit Score Factors**
- Payment history (35% weighting typical): on-time payments, missed payments, defaults.
- Credit utilisation (30%): proportion of available credit used.
- Length of credit history (15%): age of oldest account, average account age.
- Credit mix (10%): variety of credit types (revolving, instalment, mortgage).
- New credit (10%): recent applications, new accounts opened.

**Adverse Credit Markers & Duration**

| Marker | CRA Retention | Impact | Typical Lender Policy |
|---|---|---|---|
| Late payment (1–2 months) | 6 years | Moderate | Accept with rate loading |
| Late payment (3+ months) | 6 years | Significant | Decline or refer |
| Default | 6 years from default date | Severe | Decline if < 3 years old |
| CCJ (County Court Judgment) | 6 years (removed if paid within 1 month) | Severe | Decline if < 6 years old |
| IVA (Individual Voluntary Arrangement) | 6 years from start date | Very severe | Decline |
| Bankruptcy | 6 years from discharge | Very severe | Decline |
| Debt Relief Order | 6 years | Very severe | Decline |

**Decline Reason Requirements**
Under CONC 5.2A.25R, if a credit application is declined based on CRA data, the lender must:
- Inform the applicant that the decision was based on CRA data.
- Provide the name and address of the CRA(s) consulted.
- Inform the applicant of their right to obtain a copy of their credit file (free under GDPR Article 15).

### Affordability Assessment (FCA CONC 5.2A.20R)

Affordability is a separate legal requirement. The lender must assess whether the borrower can sustainably make repayments without undue difficulty, specifically without having to borrow further to meet repayments (CONC 5.2A.17R).

**ONS Expenditure Benchmarks**
- Office for National Statistics (ONS) publishes average household expenditure data by household composition and region.
- Used as a floor: if a customer declares expenditure significantly below ONS benchmarks for their household type, the application should be flagged for review.
- Categories: food & non-alcoholic drinks, housing (fuel & power), transport, recreation, clothing, communication, education, health, household goods.

**Disposable Income Calculation**

```
Disposable Monthly Income =
    Net Monthly Income
  + Verified Other Monthly Income
  − Monthly Housing Cost (rent/mortgage)
  − Monthly Credit Commitments (existing loans, cards, HP)
  − Monthly Living Expenditure (max of: declared, ONS benchmark for household type)
  − Monthly Childcare Costs
  − New Loan Monthly Repayment (proposed)
```

Result must be ≥ 0 for approval. Lenders typically require a buffer (e.g., ≥ GBP 100 disposable income remaining).

**Stress Testing**
- CONC 5.2A.20R requires consideration of future interest rate increases for variable-rate products.
- Typical stress: +3 percentage points on the interest rate.
- For fixed-rate loans, stress testing applies to the revert rate if applicable.
- Affordability must hold under stressed scenario.

**Income Verification Thresholds**
| Loan Amount | Verification Level |
|---|---|
| < GBP 5,000 | Self-declaration accepted (with ONS benchmark check) |
| GBP 5,000 – GBP 15,000 | Payslip or Open Banking verification |
| > GBP 15,000 | Full documentary evidence (payslip + bank statements or Open Banking + SA302 for self-employed) |

### Open Banking Affordability

- PSD2 enables Account Information Service Providers (AISPs) to access customer bank transaction data with explicit consent
- Transaction categorisation: automated classification of transactions into income (salary, benefits, rental), essential expenditure (rent, utilities, food, transport), discretionary expenditure (entertainment, dining, subscriptions), credit commitments (loan repayments, credit card payments), and risk indicators (gambling, payday loans)
- Benefits over traditional verification: real-time data (not 3-month-old payslips), covers all income sources, reveals actual spending patterns, detects undisclosed credit commitments
- Implementation: customer consents via their bank's app (SCA required), AISP retrieves 3-12 months of transactions, categorisation engine processes data, results feed into affordability model
- Regulatory position: FCA supports Open Banking for affordability but it must not be the ONLY method offered — customers who don't want to share bank data must have an alternative (document upload)
- Risk indicators detected via Open Banking: gambling transactions (vulnerability marker), payday loan usage (financial stress), returned Direct Debits (cash flow issues), county court payments (existing CCJs)
- PM IMPLICATION: Open Banking affordability is a major feature set — consent flow, bank selection, transaction retrieval, categorisation display (show customer what was detected), manual override (customer can dispute categorisation), and fallback to document upload. Stories must cover the happy path AND the customer who declines Open Banking.

### Debt Burden Ratio (DBR)

- DBR = Total monthly debt obligations / Net monthly income × 100
- Debt obligations include: all existing loan repayments, credit card minimum payments, hire purchase, the proposed new loan repayment
- UK: no statutory DBR cap, but FCA expects affordability assessment to ensure repayments are sustainable. Typical lender policy: DBR should not exceed 40-50% after the new loan.
- Saudi Arabia (SAMA): DBR cap of 33% of gross salary for personal finance, 65% including mortgage. These are regulatory limits, not guidelines.
- Multiple loans with same lender: total exposure must be assessed. If customer already has a loan, the combined repayment must still be within DBR limits.
- DBR calculation must use verified income (not self-declared) for loans above the verification threshold.
- PM IMPLICATION: the affordability engine must calculate DBR including the proposed loan. If DBR exceeds the limit, the application must be declined or the offered amount reduced. Stories must cover: DBR calculation display for underwriters, auto-decline when DBR exceeded, and the scenario where reducing the loan amount brings DBR within limits (counter-offer).

### Responsible Lending Obligation

- FCA CONC 5.2A.6R: a lender must NOT enter into a regulated credit agreement if the creditworthiness assessment or affordability assessment indicates the agreement is not affordable or the credit risk is too high
- This means: even if the customer WANTS the loan and passes the automated checks, the lender must decline if the assessment indicates unaffordability
- The lender cannot rely solely on the customer's self-declaration — if the data suggests the customer cannot afford the repayments, the lender must act on that data
- Irresponsible lending is a conduct risk — FCA can fine firms and require redress to affected customers
- PM IMPLICATION: the system must have hard blocks (not just warnings) when affordability fails. An underwriter override must be logged with justification. Stories must include: automated decline when affordability fails, underwriter override with mandatory reason capture, and audit trail for all lending decisions.

### PM IMPLICATION

The application must collect granular expenditure data (not just a single "monthly outgoings" field) to enable ONS benchmark comparison. Stories must include: (1) expenditure breakdown form with ONS-aligned categories, (2) automated ONS benchmark flagging (if declared < benchmark, trigger manual review), (3) disposable income calculator shown to underwriters, (4) stress test results displayed alongside base-case affordability, (5) decline reason notification flow with CRA details. The affordability model is a separate microservice/module — it must be independently testable and auditable.

---

## PD4: Pricing, Fees & APR

### Interest Rate Types

| Type | Description | Regulatory Notes |
|---|---|---|
| **Fixed** | Rate locked for the full term of the loan | Most common for personal loans. Rate stated in agreement is the rate charged. |
| **Variable** | Rate linked to a reference rate (e.g., Bank of England base rate + margin) | Must disclose reference rate and margin. Customer must be notified of rate changes (CCA s.78A). |
| **Promotional** | Reduced rate for an initial period, reverting to standard rate | Revert rate must be clearly disclosed. Affordability assessed on revert rate (CONC 5.2A.20R). |

### APR Calculation

APR is calculated per the Consumer Credit Act 1974 (as amended) and the Consumer Credit (Total Charge for Credit) Order 2010.

**Formula basis:**
- APR is the annual rate that equates the present value of all future repayments and charges to the present value of the credit advanced.
- Iterative calculation (Newton-Raphson method typical).
- Rounded to one decimal place (e.g., 6.1% APR).
- Must include all mandatory charges: interest, arrangement fees, compulsory insurance premiums.
- Must exclude: default charges, early repayment charges, optional insurance.

**Representative APR (51% Rule)**
- Under CCA s.55B and FCA CONC 3.5.3R, a "representative APR" must be shown in financial promotions.
- The representative APR is the rate at or below which the lender reasonably expects at least 51% of agreements resulting from the promotion to be made.
- If risk-based pricing means different customers get different rates, the representative APR must still reflect the rate available to the majority.

**Actual APR vs Representative APR**
- Representative APR: used in marketing and promotions.
- Personal/Actual APR: the rate offered to a specific customer after credit assessment. May be higher than representative APR for higher-risk customers.
- Both must be disclosed: representative APR in promotions, actual APR in the pre-contract credit information (SECCI) and credit agreement.

### Fee Types & UK Regulatory Caps

| Fee Type | Description | Regulatory Cap | Reference |
|---|---|---|---|
| **Arrangement fee** | One-off fee for setting up the loan | No statutory cap, but must be included in APR calculation | CCA Total Charge for Credit Order 2010 |
| **Late payment fee** | Charged when a scheduled payment is missed | Max GBP 12 per missed payment | CONC 7.7.5R |
| **Early repayment charge** | Charged when customer repays early (partial or full) | Max 1% of amount repaid early if > 1 year remaining; max 0.5% if ≤ 1 year remaining | CCA s.95A (implementing EU Directive 2008/48/EC Art.16) |
| **Default charge** | Charged when account enters default | Must be a reasonable pre-estimate of cost; not punitive (Unfair Terms, CRA 2015 s.62) | CONC 7.7.5R, CRA 2015 |
| **Statement fee (paper)** | Charge for paper statements | First copy free per year (CCA s.77–78); subsequent copies may be charged at cost | CCA s.77 |

### Total Amount Payable

Under CCA s.55A and CONC 4.4.3R, the pre-contract credit information must clearly state:
- **Total amount of credit** — the loan principal.
- **Total charge for credit** — all interest and mandatory fees over the full term.
- **Total amount payable** — sum of the above. This is the single most important figure for the customer.

Display format: `Total amount payable: GBP XX,XXX.XX`

### Representative Example (FCA-Required Format)

FCA CONC 3.5.5R requires a representative example in the following format whenever a representative APR is shown:

> **Representative Example:**
> Borrow GBP {loan_amount} over {term_months} months at an interest rate of {annual_interest_rate}% p.a. (fixed). Representative {representative_apr}% APR. Monthly repayment: GBP {monthly_repayment}. Total amount payable: GBP {total_amount_payable}. Total charge for credit: GBP {total_charge_for_credit}.

All six values must be present. The representative example must be given equal prominence to any trigger information (rate, monthly payment, or other cost figure).

### PM IMPLICATION

The offer screen is the most heavily regulated screen in the application. Every fee must be visible, the representative example must be displayed in the FCA-mandated format, and the total amount payable must be prominent. Epics must include: (1) APR calculation engine (iterative solver, independently auditable, tested against FCA worked examples), (2) offer screen with full representative example, (3) fee schedule display, (4) early repayment calculator (with correct cap applied based on remaining term), (5) rate change notification flow for variable-rate products. The APR engine is complex — it should be a separate, well-tested service. Stories should cover: offer screen layout, APR calculation accuracy tests, fee cap enforcement, early settlement quote generation, and representative example rendering across all channels (web, mobile, email, PDF).

---

## PD5: Loan Offers & Agreements

The legal process from offer to binding agreement:

### Pre-Contract Information

CCA requires adequate explanations before commitment. The lender must ensure the borrower understands the product, its risks, and their obligations (CONC 4.2.5R). This is not optional — failure to provide adequate explanations can render the agreement unenforceable.

### PCCI (Pre-Contract Credit Information)

Standardised document per Consumer Credit (Disclosure of Information) Regulations 2010. Contents:

- **Type of credit** — e.g., fixed-sum unsecured personal loan
- **Total amount of credit** — the loan principal
- **Duration** — term in months
- **Rate of interest** — annual fixed or variable, and how it is applied
- **APR** — representative and/or personal APR
- **Total amount payable** — principal + total charge for credit
- **Repayment schedule** — amount, frequency, number of payments
- **Right to withdraw** — 14-day cooling-off period, how to exercise it
- **Right to early repayment** — CCA s.94 right, any applicable compensation

The PCCI must be provided in a durable medium (PDF, email, in-app persistent document) in good time before the agreement is signed. It must be a separate, identifiable document — not buried in T&Cs.

### Credit Agreement

Legally binding contract. Prescribed terms per CCA s.61:

- Names and addresses of creditor and debtor
- Amount of credit
- Rate of interest and how it is calculated
- Total charge for credit
- Total amount payable
- Repayment amounts and dates
- Default charges and consequences
- Right to withdraw (s.66A)
- Right to early repayment (s.94)

Electronic signature is valid under eIDAS Regulation (EU 2014/910, retained in UK law) and the Electronic Communications Act 2000. The agreement must be executed as a document (not merely a click-wrap) and a copy provided to the borrower immediately.

### Right to Withdraw

- **Period**: 14 calendar days from the day after signing (CCA s.66A)
- **No reason needed**: the borrower can withdraw without giving any reason
- **Repayment obligation**: repay principal + accrued interest within 30 days of giving notice of withdrawal
- **No fees**: no penalty or fee may be charged for withdrawal
- **How to exercise**: written notice (email, letter, or in-app message) to the lender

### Offer Expiry

- Typically 7–30 days depending on lender policy
- After expiry, a new credit check may be required (previous hard search remains on file for 12 months)
- Rate may change if risk profile or market conditions have shifted
- Customer must be clearly informed of expiry date and consequences

### Execution Process

1. Customer reviews offer (PCCI displayed)
2. Customer accepts terms (explicit opt-in, not pre-ticked)
3. E-signature captured (timestamp, IP address, device fingerprint)
4. Credit agreement generated and stored (6 years post-closure per FCA SYSC 9.1.1R)
5. Cooling-off period starts (day after signing)
6. Disbursement initiated (immediately or after cooling-off, per lender policy)

### PM IMPLICATION

The acceptance flow is legally prescribed — you cannot skip the PCCI, cannot hide the cooling-off right, and the e-signature must be legally valid. The withdrawal flow is often forgotten in product builds but is a legal requirement. Epics must include: (1) PCCI generation and display, (2) acceptance flow with e-signature capture, (3) agreement PDF generation and storage, (4) cooling-off period tracking, (5) withdrawal request flow (initiation, principal repayment, interest calculation, confirmation), (6) offer expiry management and re-application flow. Stories should cover: PCCI rendering across channels, e-signature capture and validation, agreement document generation, withdrawal happy path, withdrawal after disbursement (funds must be returned), offer expiry notification, and re-application after expiry.

---

## PD6: Disbursement

How funds reach the customer after agreement execution.

### Payment Methods

| Method | Speed | Availability | Limit | Irrevocable |
|---|---|---|---|---|
| **Faster Payments (FPS)** | Seconds | 24/7/365 | Varies by bank (GBP 250K–1M) | Yes |
| **BACS** | Next working day (D+1 for credits) | Working days only | No practical limit | No (can be recalled before settlement) |
| **CHAPS** | Same day | Banking hours (Mon–Fri, 06:00–18:00) | No limit | Yes, once settled |

### Faster Payments Detail

- Settlement in seconds, available 24/7/365 including bank holidays
- Limit varies by sending bank (typically GBP 250K–1M for business accounts)
- Uses sort code + account number
- Irrevocable once sent — cannot be recalled
- ISO 20022 messaging format (migrating from ISO 8583)
- Most fintechs use FPS as the default disbursement method for speed and customer experience

### Timing: Immediate vs Cooling-Off

- **Immediate disbursement**: funds sent as soon as agreement is signed. Better customer experience. Risk: customer withdraws during cooling-off, lender must recover funds.
- **Wait for cooling-off**: funds sent after 14-day period expires. Conservative but eliminates withdrawal recovery risk. Poor customer experience.
- Most fintechs disburse immediately and manage withdrawal risk operationally.

### Account Verification

- Funds must be sent to an account in the borrower's name (AML requirement under MLR 2017 reg.28)
- Account verified during application via Open Banking, bank statement upload, or manual entry + Confirmation of Payee (CoP)
- Sort code validated via Modulus checking (Vocalink)

### Failed Disbursement

Common failure reasons:
- Account closed or dormant
- Invalid sort code or account number
- Name mismatch (CoP failure)
- Receiving bank rejection (fraud block, sanctions match)

Handling:
- Automated retry (max 2 attempts, different times)
- Customer notification (push + email) with reason and next steps
- Loan status reverts to **AgreementSigned** (not Disbursed)
- Customer prompted to provide alternative account details
- If unresolved within 7 days, offer expires and application may need to restart

### Confirmation

- Push notification + email sent on successful disbursement
- Includes: amount sent, destination account (last 4 digits), expected arrival time, loan reference
- For FPS: "Funds should arrive within minutes"
- For BACS: "Funds should arrive by the next working day"

### PM IMPLICATION

Disbursement has critical edge cases: bank rejection, frozen account, withdrawal after disbursement (funds already sent, must be recovered). Stories must cover: (1) successful disbursement via FPS, (2) successful disbursement via BACS, (3) failed disbursement with retry, (4) failed disbursement with account update, (5) disbursement confirmation notifications, (6) cooling-off interaction (withdrawal before disbursement, withdrawal after disbursement with recovery flow), (7) CoP name mismatch handling. The disbursement status must be clearly visible in the customer dashboard and internal servicing tools.

---

## PD7: Repayment & Collections

Split into two subsections covering normal repayment and arrears/collections.

### Repayment

#### Methods

- **Direct Debit** (most common): customer sets up a Direct Debit Instruction (DDI) during onboarding. Governed by the Direct Debit Guarantee (customer can claim full and immediate refund from their bank for any incorrect payment). Advance notice required: 10 working days before the first collection, 5 working days before subsequent collections (or as agreed in DDI).
- **Manual bank transfer**: customer initiates payment via their bank. Uses loan-specific payment reference for reconciliation.
- **Card payment**: debit or credit card via payment gateway. Note: Continuous Payment Authority (CPA) restricted for high-cost short-term credit (CONC 7.6.12R — max 2 failed attempts, then must stop).

#### Payment Allocation Waterfall

When a payment is received, it is allocated in the following order:
1. **Outstanding fees** (late payment fees, default charges)
2. **Accrued interest**
3. **Principal**

This waterfall is standard industry practice and must be clearly disclosed in the credit agreement.

#### Repayment Schedule

- Fixed monthly payments (annuity method — equal instalments comprising varying proportions of interest and principal)
- Schedule generated at disbursement and provided to the customer
- Each row shows: payment date, total amount, interest portion, principal portion, remaining balance
- Schedule recalculated if overpayment or term change occurs

#### Overpayment

- Customer can make payments above the scheduled amount at any time
- Excess amount reduces the outstanding principal
- Customer chooses: **shorter term** (same monthly payment, fewer months) or **lower payment** (same term, reduced monthly amount)
- No fee for overpayment (distinct from early settlement — overpayment is partial, settlement is full)
- Schedule recalculated and new schedule provided to customer

#### Salary Date & Payment Scheduling

- Salary date is collected during application to align Direct Debit collection with income receipt.
- Validation: salary date should be cross-referenced against bank statement data (if Open Banking is used) or employer payroll cycle.
- If salary date falls on a weekend or bank holiday, the DD collection should be scheduled for the next working day.
- If customer provides incorrect salary date, DD collections may fail due to insufficient funds. System should detect pattern of DD failures and prompt customer to update salary date.
- Payment date change: customer can request to change their payment date (once per 12 months is typical). New date takes effect from the next billing cycle.
- PM IMPLICATION: stories must cover salary date capture during application, salary date validation against bank data, payment date change request flow, and the scenario where repeated DD failures suggest incorrect salary date.

### Collections

Arrears management follows a prescribed regulatory timeline. All communications must comply with CONC 7.3 (treating customers in default or arrears fairly).

#### Day 1: Payment Missed

- Automated reminder (SMS/push/email)
- No fee charged
- Tone: helpful, not threatening
- Internal status: **1 day past due**

#### Day 3–7: Second Contact

- Second reminder sent
- Offer to discuss financial difficulties
- Signpost free debt advice services (FCA requirement under CONC 7.3.7AR):
  - **StepChange** (0800 138 1111)
  - **Citizens Advice** (citizensadvice.org.uk)
  - **National Debtline** (0808 808 4000)
- Tone: supportive, offer forbearance discussion

#### Day 14: Formal Arrears Notice

- CCA s.86B requires a formal notice of sums in arrears when the borrower is at least 2 payments behind or the total shortfall equals at least 2 payments
- Notice must contain:
  - Amount in arrears
  - Total amount owed
  - Consequences of continued non-payment
  - FCA contact details
  - Free debt advice contacts
- Must be sent by post or durable medium

#### Day 30: One Month in Arrears

- Arrears reported to Credit Reference Agencies (Experian, Equifax, TransUnion)
- Late payment fee applied: maximum GBP 12 per missed payment (CONC 7.7.5R)
- Customer's credit file shows 1 month arrears marker
- Internal status: **30 days past due**

#### Day 60: Two Months in Arrears

- Second formal arrears notice (CCA s.86C — must be sent at least every 6 months while in arrears)
- Proactive offer of forbearance options
- Income & expenditure review offered
- Internal status: **60 days past due**

#### Day 90: Three Months in Arrears — Default Warning

- Default warning notice issued
- 14 days given to remedy the arrears (CCA s.87 — default notice must give at least 14 days)
- Notice must specify: breach, action required to remedy, consequences of failure to remedy
- Internal status: **90 days past due, default warning issued**

#### Default Registration

- If arrears not remedied within 14 days of default notice
- Default registered with all CRAs (CCA s.87)
- Default remains on credit file for 6 years from date of default
- Account may be passed to external collections agency or debt sold
- Customer must be notified of any assignment of the debt

#### Forbearance Options

Lenders must consider forbearance before enforcement (CONC 7.3.4R):

| Option | Description | Duration |
|---|---|---|
| **Payment holiday** | Suspend payments entirely | 1–3 months |
| **Reduced payment plan** | Lower monthly payments based on I&E review | 3–12 months |
| **Term extension** | Extend loan term to reduce monthly payment | Varies |
| **Interest freeze** | Stop charging interest on arrears balance | During forbearance period |
| **DMP referral** | Refer to Debt Management Plan provider | Ongoing |

### Breathing Space (Debt Respite Scheme 2021)

- Legal moratorium giving debtors 60 days of protection from creditor action
- Two types: Standard breathing space (60 days, applied for via debt advisor) and Mental health crisis breathing space (lasts duration of crisis treatment + 30 days)
- During breathing space, the lender MUST:
  - Freeze interest and charges on the debt
  - Stop all enforcement action (no default registration, no legal proceedings)
  - Stop contacting the customer about the debt (except to respond to customer-initiated contact)
  - Not pursue guarantors
- The lender is notified via the Insolvency Service's electronic portal
- After breathing space ends: normal collections resume, frozen interest/charges are NOT retrospectively applied
- PM IMPLICATION: breathing space requires a system flag that automatically freezes interest accrual, suppresses all automated collections communications, and blocks enforcement actions. Stories must cover: breathing space notification receipt, automatic account freeze, interest/charge suspension, communication suppression, breathing space expiry and resumption of normal collections.

### PM IMPLICATION

Collections is heavily regulated with specific timelines and prescribed notices. The customer dashboard must show arrears status clearly. Notifications must follow the prescribed timeline and include mandatory content (debt advice signposting). Epics must include: (1) repayment schedule display and recalculation, (2) Direct Debit setup and management, (3) overpayment flow with term/payment choice, (4) arrears detection and automated reminder sequence, (5) formal arrears notice generation (CCA s.86B compliant), (6) default warning and registration flow, (7) forbearance request and management, (8) collections dashboard for internal teams. Stories must cover: normal repayment view, arrears dashboard, each stage of the collections timeline, forbearance request flow, debt advice signposting, CRA reporting, and default registration. Do not forget the Direct Debit Guarantee — customers can reclaim payments, and the system must handle indemnity claims.

---

## PD8: Early Repayment & Settlement

### Legal Right

CCA s.94 gives every borrower the right to repay early at any time, in full or in part. The lender cannot refuse or unreasonably delay settlement.

### Settlement Figure Calculation

The settlement figure is calculated as:

`Settlement Figure = Outstanding Principal + Accrued Interest to Settlement Date + Outstanding Fees − Rebate`

- **Rebate**: calculated using the Actuarial Method per the Consumer Credit (Early Settlement) Regulations 2004
- The rebate represents the interest the borrower would have paid over the remaining term, adjusted for the time value of money
- The calculation must be penny-accurate — rounding errors are a compliance risk

### Settlement Figure Validity

- Valid for **28 days** from date of calculation (CCA s.97)
- After 28 days, a new figure must be requested and recalculated
- The figure must be provided within 7 working days of request

### Compensation Caps

Per CCA s.95A (implementing EU Consumer Credit Directive Art.16):

| Remaining Term | Maximum Compensation |
|---|---|
| **> 12 months** | 1% of the amount repaid early |
| **≤ 12 months** | 0.5% of the amount repaid early |

Additional constraint: compensation cannot exceed the total remaining interest that would have been payable. Many UK fintechs charge **zero** early repayment compensation as a competitive differentiator.

### Partial Early Repayment

- Customer makes a lump sum payment above the scheduled amount
- Lump sum reduces the outstanding principal
- Customer chooses:
  - **Reduce monthly payment**: same term, lower instalments
  - **Reduce term**: same monthly payment, fewer months remaining
- Repayment schedule recalculated and new schedule provided
- No compensation charged for partial early repayment (CCA s.94 applies to partial as well as full)

### Settlement Process

1. Customer requests settlement figure (in-app, phone, or written request)
2. Figure calculated and displayed (valid 28 days, date shown)
3. Customer makes payment (FPS, BACS, card, or manual transfer)
4. Payment matched to loan via reference
5. Loan marked as **Settled** (distinct from **Closed** — settled means early, closed means term completed)
6. Confirmation sent (push + email): settlement confirmed, no further payments due
7. CRA updated: account marked as settled, balance zero, within 30 days
8. Documents available for download: settlement letter, final statement, transaction history

### PM IMPLICATION

Early settlement is a key differentiator for fintechs — zero fees should be prominent in marketing and the in-app experience. The settlement figure calculation must be penny-accurate and independently auditable. Epics must include: (1) settlement figure calculator (actuarial method, tested against worked examples), (2) settlement figure display (amount, validity date, payment instructions), (3) partial early repayment flow (lump sum input, term vs payment choice, schedule recalculation), (4) full settlement payment flow, (5) post-settlement confirmation and document generation, (6) CRA update on settlement. Stories must cover: settlement figure request and display, partial vs full settlement choice, payment execution, confirmation, CRA update, settlement letter generation, figure expiry and recalculation, and the edge case where a scheduled Direct Debit is collected after settlement (must be refunded).

---

## PD9: Payment Processing

The technical infrastructure behind all payment movements in a UK lending product.

### UK Payment Schemes

| Scheme | Type | Speed | Availability | Use Case |
|---|---|---|---|---|
| **Faster Payments Service (FPS)** | Real-time gross | Seconds | 24/7/365 | Disbursement, ad-hoc repayments |
| **BACS** | Batch net | 3-day cycle | Working days | Direct Debit collections, bulk credits |
| **CHAPS** | Real-time gross | Same day | Banking hours | High-value payments (rare in consumer lending) |
| **Direct Debit** | BACS-based | 3-day cycle | Working days | Scheduled repayment collections |

### Faster Payments Detail

- Real-time settlement, available 24/7/365
- Maximum varies by sending bank (typically GBP 250K–1M for business accounts)
- Uses sort code + account number
- Irrevocable once sent
- ISO 20022 messaging format (UK migration from ISO 8583 completed)
- Primary method for disbursement and customer-initiated repayments

### BACS Processing Cycle

| Day | Activity |
|---|---|
| **Day 1 (Input)** | Payment file submitted to BACS by 22:30 |
| **Day 2 (Processing)** | BACS processes the file, sends to receiving banks |
| **Day 3 (Settlement)** | Funds debited from payer and credited to payee |

- Used for Direct Debit collections and bulk salary/credit payments
- Files submitted in Standard 18 format or via BACS API
- Cut-off times are strict — missed cut-off delays by one full cycle

### Direct Debit Lifecycle

1. **DDI Setup (AUDDIS)**: Direct Debit Instruction submitted via Automated Direct Debit Instruction Service. Customer authorises via paper mandate, online mandate, or phone mandate. Lodged with customer's bank.
2. **Advance Notice**: lender sends notice of upcoming collection — amount, date, frequency. 10 working days before first collection, 5 working days before subsequent (or as agreed).
3. **Collection**: BACS submission on Day 1 of cycle. Funds arrive Day 3.
4. **Payment Confirmation**: reconcile received funds against expected collections.
5. **Cancellation**: customer can cancel DDI at any time via their bank. Lender is notified via ARUDD (Automated Return of Unpaid Direct Debits) or ADDACS (Automated Direct Debit Amendment and Cancellation Service).
6. **Indemnity Claims**: under the Direct Debit Guarantee, the customer's bank will refund any payment the customer disputes. The lender receives an indemnity claim and must either accept or challenge it within the prescribed timeframe.

### Payment Statuses

| Status | Description |
|---|---|
| **Initiated** | Payment created in the system, not yet submitted |
| **Submitted** | Payment file sent to payment scheme (BACS/FPS) |
| **Processing** | Payment is being processed by the scheme |
| **Settled** | Funds have been transferred and confirmed |
| **Failed** | Payment rejected by scheme or receiving bank |
| **Returned** | Payment returned after settlement (e.g., ARUDD for DD) |
| **Reversed** | Payment reversed due to indemnity claim or error |

### Reconciliation

- **Daily reconciliation**: compare expected payments (from repayment schedules) against actual payments received (from bank statement feed)
- **Unmatched payments**: investigate and resolve — could be overpayment, wrong reference, payment from third party
- **Suspense account**: unallocated funds held in a suspense account until matched to a loan. Must be cleared within 5 working days (FCA client money rules, CASS where applicable)
- **Reconciliation breaks**: escalated to operations team, root cause analysis, corrective action

### Payment References

- Unique reference per loan for reconciliation: `LOAN-{loanId}-{paymentType}-{sequence}`
- `paymentType`: DISB (disbursement), REPAY (repayment), SETTLE (settlement), REFUND (refund)
- `sequence`: incrementing number per payment type per loan
- Reference included in all payment instructions and customer communications

### Sort Code Validation

- **Modulus checking** (Vocalink): validates that a sort code + account number combination is mathematically valid
- Does not confirm the account exists or is open — only that the format is correct
- Must be performed before any payment is initiated
- Validation rules updated monthly by Vocalink

### Confirmation of Payee (CoP)

- Name matching service operated by Pay.UK
- Checks that the account name provided by the payer matches the name held by the receiving bank
- Results: **Match**, **Close Match** (e.g., typo), **No Match**
- **No Match**: customer warned, can proceed at own risk or correct details
- Reduces misdirected payments and APP (Authorised Push Payment) fraud
- Mandatory for FPS and CHAPS payments since 2020

### Open Banking Payments

- PSD2 (Payment Services Directive 2, retained in UK law as Payment Services Regulations 2017) enables Payment Initiation Service Providers (PISPs) to initiate payments directly from the customer's bank account
- Alternative to card payments for repayments — lower cost, no card network fees
- Customer authenticates via their bank's app (Strong Customer Authentication — SCA)
- Payment initiated via API, settled via FPS
- Growing adoption for one-off repayments and settlement payments

### PM IMPLICATION

Payment processing has multiple failure points and each must be handled gracefully. Stories must cover: (1) successful payment via each method (FPS, BACS, DD, card, Open Banking), (2) failed payment with specific reason codes (insufficient funds, account closed, invalid details), (3) Direct Debit setup flow (mandate creation, AUDDIS submission, confirmation), (4) Direct Debit cancellation by customer (ADDACS notification handling, alternative payment arrangement), (5) DD indemnity claim handling (refund to customer's bank, impact on loan balance, customer communication), (6) reconciliation discrepancy investigation and resolution, (7) Confirmation of Payee name mismatch (warn customer, allow override or correction), (8) payment reference generation and validation, (9) suspense account management, (10) Open Banking payment initiation flow. The payment status must be visible in both customer-facing and internal dashboards, with clear indication of next steps for failed or returned payments.

---

## PD10: PSD2 & Strong Customer Authentication (SCA)

Payment Services Directive 2 and its impact on lending:

- **PSD2 overview**: EU directive (retained in UK law post-Brexit as UK PSD2), regulates payment services, introduces SCA and Open Banking
- **SCA requirement**: two of three factors — knowledge (password/PIN), possession (phone/device/token), inherence (fingerprint/face). Required for: accessing payment account online, initiating electronic payment, any action through remote channel that may imply risk of fraud
- **SCA in lending context**: required for loan acceptance (it's a payment initiation), required for viewing sensitive financial data (account balance, transaction history), required for setting up Direct Debit, required for making manual repayment
- **SCA exemptions**: viewing product catalog (no account access), viewing own application status (low risk), recurring payments of same amount to same payee (after first SCA-authenticated setup), low-value transactions (under EUR30, but cumulative limit EUR100 or 5 transactions)
- **SCA implementation**: biometric (fingerprint/face) + device possession (the phone itself) satisfies two factors. Password + OTP also satisfies two factors. Must use different channels for the two factors where possible.
- **Dynamic linking**: for payment initiation, the authentication must be dynamically linked to the amount and payee. The customer must see the amount and payee during authentication.
- **Regulatory Technical Standards (RTS)**: EBA RTS on SCA specify technical requirements. UK FCA has adopted equivalent standards.

### PM IMPLICATION

SCA affects multiple user flows. Login can use biometric (one factor) for low-risk access, but loan acceptance and payment initiation need two factors. Stories must specify which SCA level each action requires. The dynamic linking requirement means the biometric prompt for loan acceptance must show the loan amount.

---

## PD11: KYC & Identity Verification

Know Your Customer requirements for lending:

- **Legal basis**: Money Laundering Regulations 2017 (MLR 2017), reg.28 — must verify identity before establishing a business relationship
- **Customer Due Diligence (CDD)**: verify identity (name, DOB, address), verify they are who they claim to be (document + biometric), understand the purpose of the relationship (it's a loan)
- **Enhanced Due Diligence (EDD)**: required for higher-risk customers — Politically Exposed Persons (PEPs), customers from high-risk countries, unusual transaction patterns. Additional checks: source of funds, source of wealth.
- **Identity documents accepted**: UK passport, UK driving licence (photocard), EU/EEA national ID card, biometric residence permit. Each has different verification methods and confidence levels.
- **Document verification**: check document is genuine (security features, MRZ validation, NFC chip reading for e-passports), check it belongs to the applicant (photo match), check it's not expired, check it's not on a lost/stolen database
- **Biometric verification**: selfie compared to document photo (face matching), liveness detection (blink, head turn — prevents photo-of-photo attacks), anti-spoofing (detect screens, masks, deepfakes)
- **OCR pre-fill**: extract data from document (name, DOB, document number, expiry, nationality), pre-fill application form, customer reviews and confirms
- **Electronic verification**: check name + DOB + address against multiple data sources (electoral roll, credit reference agencies, utility records). Score-based: if enough sources match, identity is verified without document upload.
- **Ongoing monitoring**: not just at onboarding. Must monitor for changes in risk profile. For lending: mainly at origination, but also if customer requests significant changes (e.g., large early repayment from unknown source).
- **Sanctions screening**: check customer name against UK sanctions list (OFSI), EU sanctions list, UN sanctions list, OFAC (US). Must screen at onboarding and periodically.
- **PEP screening**: check if customer is a Politically Exposed Person or family member/close associate. If PEP: Enhanced Due Diligence required, senior management approval for relationship.
- **Verification outcomes**: Verified (proceed), Referred (manual review needed — partial match, document quality issue), Failed (cannot verify — decline or request alternative documents), Expired (verification took too long, restart)

### PM IMPLICATION

KYC is not just "upload your ID". It's a multi-step process with multiple outcomes. Stories must cover: document selection, camera capture with quality guidance, selfie with liveness, OCR review, verification status tracking, retry on failure, manual review escalation, sanctions/PEP screening (even if automated, the result must be handled). The referred state is critical — what happens when auto-verification fails but the customer might still be legitimate?

---

## PD12: FCA Consumer Duty

The FCA's flagship regulation (PS22/9, effective July 2023):

- **Overarching principle**: firms must act to deliver good outcomes for retail customers
- **Four outcomes**:
  1. **Products and services**: products designed to meet needs of target market, not cause foreseeable harm. For lending: loan products must be appropriate for the customer segment (don't offer high-rate loans to customers who qualify for lower rates).
  2. **Price and value**: fair value — the relationship between price and benefit must be reasonable. For lending: total cost of credit must be proportionate to the service provided. Fees must be justified. No excessive charges.
  3. **Consumer understanding**: customers must be given information they can understand to make effective decisions. For lending: plain language (not legal jargon), clear fee breakdown, representative examples, total cost visible before commitment.
  4. **Consumer support**: customers must be able to use products as reasonably expected and not face unreasonable barriers. For lending: easy to make repayments, easy to get settlement figure, easy to complain, easy to switch/exit.
- **Vulnerable customers**: firms must pay special attention to customers in vulnerable circumstances (see PD15)
- **Monitoring**: firms must monitor outcomes and take action if poor outcomes are identified. For lending: track approval rates by demographic, track complaints by product, track arrears rates.
- **Product governance**: products must be reviewed at least annually. Target market must be defined. Distribution strategy must be appropriate.

### PM IMPLICATION

Consumer Duty affects EVERY screen. Product listing must not mislead. Offer screen must be crystal clear. Dashboard must make repayment easy. Early repayment must not be hidden. Complaints must be accessible. Stories should include acceptance criteria like: "a customer with no financial background can understand the total cost from the offer screen without external help".

---

## PD13: Consumer Credit Act 1974 (as amended)

The foundational UK legislation for consumer lending:

- **Scope**: regulated credit agreements where the borrower is an individual (not a company) and the credit amount is up to GBP25,000 (or any amount if secured on land). Most personal loans fall within scope.
- **Key sections relevant to a loan app**:
  - **s.55A**: pre-contract explanations (adequate explanations before agreement)
  - **s.55B**: assessment of creditworthiness (must assess before entering agreement)
  - **s.60-61**: form and content of agreements (prescribed terms, signature requirements)
  - **s.66A**: right to withdraw (14-day cooling-off period)
  - **s.77-78**: duty to provide information (customer can request copy of agreement and statement of account at any time)
  - **s.86B-86C**: arrears notices (must send notice when 2 payments missed)
  - **s.87**: default notices (must give 14 days to remedy before taking action)
  - **s.94**: right to complete payments ahead of time (early repayment)
  - **s.95A**: compensatory amount for early repayment (the fee cap)
  - **s.97**: duty to give settlement information within 7 working days of request
  - **s.140A-140C**: unfair relationships (court can reopen agreement if relationship is unfair)
- **Prescribed terms**: the credit agreement MUST contain: names and addresses of parties, amount of credit, credit limit, rate of interest, APR, total charge for credit, repayment amounts and timing, default charges, right to withdraw, right to early repayment
- **Consequences of non-compliance**: if agreement doesn't contain prescribed terms, it may be unenforceable. If pre-contract information not provided, agreement may be unenforceable. This is a serious business risk.
- **Electronic agreements**: valid under Electronic Communications Act 2000 and eIDAS. Must be durable (customer can save/print). Must be provided to customer immediately after signing.

### PM IMPLICATION

CCA compliance is not optional — non-compliance makes the loan unenforceable (the lender cannot recover the money). Every story that touches the agreement, offer, or repayment flow must have acceptance criteria that reference the relevant CCA section. The agreement generation feature must include ALL prescribed terms. The settlement figure feature must respond within 7 working days (s.97).

---

## PD14: GDPR in Lending

Data protection specific to lending:

- **Lawful basis for processing**: Contract performance (processing the loan application, managing the loan), Legitimate interest (fraud prevention, credit risk assessment), Legal obligation (CCA record keeping, AML checks), Consent (marketing communications only — never use consent as basis for core lending, because consent can be withdrawn)
- **Data collected in lending and its basis**: name/DOB/address (contract), employment/income (contract), credit file data (legitimate interest for risk assessment), bank statements (contract — affordability), ID documents (legal obligation — AML), biometric data (consent for biometric login, legitimate interest for KYC liveness), device data (legitimate interest for fraud prevention)
- **Special category data**: biometric data is special category under GDPR Article 9. Requires explicit consent or substantial public interest. Liveness check biometric data should be processed and discarded, not stored long-term.
- **Data minimisation**: only collect what's needed for the lending decision. Don't ask for employer phone number if you won't call them. Don't collect social media profiles.
- **Right to access (DSAR)**: customer can request all data held about them. Must respond within 1 calendar month. For lending: includes application data, credit check results, affordability assessment, correspondence, call recordings, decision rationale.
- **Right to erasure**: customer can request deletion. BUT lending has exemptions: legal obligation to retain (CCA requires records for duration of agreement + 6 years), legitimate interest in retaining (debt recovery). Can erase marketing data and non-essential data. Must explain what was erased and what was retained and why.
- **Right to portability**: customer can request data in machine-readable format. Applies to data provided by the customer (application data) and data generated by automated processing (credit score). Does not apply to data from third parties (CRA data).
- **Automated decision-making (Article 22)**: if the lending decision is fully automated (no human involvement), customer has the right to: obtain meaningful information about the logic involved, request human intervention, express their point of view, contest the decision. If using AI/ML for credit scoring, this is directly relevant.
- **Data retention**: application data (7 years after loan closure for CCA compliance), rejected applications (3 years — for complaints and regulatory review), KYC documents (5 years after relationship end per MLR 2017), marketing consent records (duration + 1 year), credit check results (retain decision, not raw CRA data)
- **Privacy notice**: must be provided at point of data collection. Must explain: what data, why, lawful basis, who it's shared with (CRAs, KYC providers), retention periods, rights.

### PM IMPLICATION

GDPR affects the entire application flow. The privacy notice must be shown before data collection starts. Consent for marketing must be separate and optional (not bundled with T&Cs). The DSAR flow needs a story (even if it's a back-office process). Automated decision-making disclosure is required if using AI for credit scoring. Stories for data collection screens must specify the lawful basis in acceptance criteria.

---

## PD15: Vulnerable Customers

FCA's expectations for treating vulnerable customers fairly:

- **Definition (FCA FG21/1)**: a vulnerable customer is someone who, due to their personal circumstances, is especially susceptible to harm, particularly when a firm is not acting with appropriate levels of care
- **Four drivers of vulnerability**: Health (physical disability, mental health conditions, cognitive impairment, severe illness), Life events (bereavement, job loss, relationship breakdown, domestic abuse), Resilience (low financial resilience, over-indebtedness, low savings), Capability (low literacy, low financial literacy, low digital literacy, language barriers)
- **Prevalence**: FCA estimates 50% of UK adults show one or more characteristics of vulnerability. This is not a niche concern.
- **What firms must do**: understand the nature and scale of vulnerability in their customer base, ensure products and services meet needs of vulnerable customers, ensure staff (and agents) are equipped to recognise and respond to vulnerability, monitor outcomes for vulnerable customers
- **In a loan app context**:
  - **Accessibility**: WCAG 2.1 AA is the minimum. Consider screen readers, large text, simple language, alternative formats.
  - **Affordability**: extra care when customer shows signs of financial difficulty (high existing debt, recent job loss). Don't just approve because they pass the algorithm.
  - **Communication**: plain language, avoid jargon, provide summaries alongside legal text, offer alternative channels (phone, branch) for customers who struggle with digital.
  - **Collections**: if customer indicates vulnerability during arrears, pause collections, refer to specialist team, consider forbearance. Never use aggressive language.
  - **Gambling markers**: if bank statement analysis shows gambling transactions, this is a vulnerability indicator. Must be handled sensitively.
  - **Bereavement**: if a borrower dies, the loan doesn't disappear. Must have a process for dealing with the estate. Sensitive communication with next of kin.
- **Reasonable adjustments**: firms must make reasonable adjustments for disabled customers (Equality Act 2010). Examples: longer time to complete forms, alternative verification methods, human assistance option.

### PM IMPLICATION

Vulnerability is not a separate feature — it's a lens applied to every feature. Stories should include acceptance criteria like: "screen is usable with TalkBack at 200% text size", "if affordability check shows high debt-to-income ratio, system flags for manual review", "collections notifications use empathetic language and include debt advice contacts". Consider adding a "need help?" option on every screen that connects to human support.

---

## PD16: Complaints & Dispute Resolution

How complaints must be handled in UK financial services:

- **FCA requirements (DISP rules)**: firms must have a written complaints procedure, acknowledge complaints promptly, investigate fairly, provide a final response within 8 weeks
- **Complaint definition**: any expression of dissatisfaction, whether oral or written, and whether or not justified. "I'm not happy with my interest rate" is a complaint. It doesn't need to use the word "complaint".
- **Timeline**: Day 0 — complaint received, acknowledge within 5 business days. Investigate. If resolved within 3 business days to customer's satisfaction — summary resolution communication. If not resolved within 3 days — formal investigation. Final response within 8 weeks. If cannot resolve within 8 weeks — must send holding letter explaining delay and informing of right to go to FOS.
- **Financial Ombudsman Service (FOS)**: if customer is not satisfied with final response (or 8 weeks pass without response), they can escalate to FOS. FOS can award up to GBP 430,000 (2024/25 limit). Firm must inform customer of FOS right in final response.
- **Root cause analysis**: FCA expects firms to analyse complaints for root causes and systemic issues. If multiple customers complain about the same thing, the firm must fix the underlying issue.
- **Complaints data**: firms must report complaints data to FCA every 6 months (REP-COBS). Published on FCA website. Reputational risk.
- **In a loan app**: must have accessible complaints channel (in-app, email, phone). Must track complaint status. Must meet timelines. Must inform of FOS right.

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

How loan products are defined and who qualifies:

### Product Parameters

Every loan product is defined by a set of configurable parameters:

| Parameter | Description | Example |
|---|---|---|
| Product name | Marketing name | "Personal Loan", "Debt Consolidation Loan" |
| Loan amount range | Min and max borrowing | GBP 1,000 – GBP 25,000 |
| Term range | Min and max repayment period | 12 – 60 months |
| Rate bands | Interest rates by risk tier | Tier 1: 3.9%, Tier 2: 6.9%, Tier 3: 12.9% |
| Representative APR | Rate for 51%+ of applicants | 6.9% APR |
| Fees | Arrangement, late, early repayment | GBP 0 arrangement, GBP 12 late, 0% early |
| Repayment type | Fixed, variable | Fixed monthly |
| Secured/unsecured | Whether collateral required | Unsecured |

### Eligibility Rules

Pre-qualification rules applied BEFORE a full application:

| Rule | Typical Criteria | Regulatory Basis |
|---|---|---|
| Age | 18–75 (varies by product) | CCA s.8 (minors excluded) |
| Residency | UK resident, 3+ years address history | CRA matching requirement |
| Employment | Employed, self-employed, retired (varies) | Affordability requirement |
| Minimum income | GBP 10,000–15,000 annual (varies) | Affordability floor |
| Credit history | No active defaults, CCJs, IVAs, bankruptcy | Risk appetite |
| Existing customer | May have different criteria for existing borrowers | Internal data advantage |
| Debt-to-income ratio | Typically < 40–50% | Affordability ceiling |

### Rate Tiering (Risk-Based Pricing)

Customers receive different rates based on their risk profile:

1. Credit score from CRA mapped to internal risk tier (Tier 1 = lowest risk, Tier 5 = highest)
2. Each tier has a base rate
3. Adjustments applied for: loan amount (larger = slightly lower rate), term (longer = slightly higher rate), existing customer (loyalty discount)
4. Final rate must be >= representative APR for at least 51% of applicants
5. Rate offered to customer is the personal rate — may differ from representative APR

### Product Governance (FCA PROD rules)

- Target market must be defined for each product (who is it designed for?)
- Distribution strategy must be appropriate (direct, broker, aggregator)
- Products reviewed at least annually for continued suitability
- If product is causing harm (high arrears rate, high complaints), it must be modified or withdrawn

### PM IMPLICATION

Product configuration drives the entire eligibility and offer flow. Stories must cover: product catalog display (with representative APR and key facts), eligibility pre-check (soft search, instant result), rate personalisation (show personal rate after eligibility), product comparison (side-by-side for multiple products), and product governance reporting (arrears rate, complaints rate per product). The eligibility rules are the first filter — they determine what the customer sees before they even start an application.

---

## PD19: Loan Servicing & Account Management

What happens during the life of an active loan:

### Statements

- Annual statement: must be sent at least once per year (CCA s.77A). Contains: opening balance, payments made, interest charged, fees charged, closing balance, remaining term.
- On-demand statement: customer can request a copy of their agreement and statement of account at any time (CCA s.77-78). Must be provided within 12 working days. First copy free; subsequent copies may be charged at cost.
- Transaction history: customer should be able to view all transactions (payments, interest accruals, fees) in-app at any time.

### Account Changes

| Change | Process | Verification |
|---|---|---|
| Change of address | Customer updates via app or phone | New address verified (PAF lookup, utility bill) |
| Change of name | Customer provides deed poll or marriage certificate | Document verified, agreement updated |
| Change of bank details | Customer provides new sort code + account number | CoP check, new DDI setup, old DDI cancelled |
| Change of contact details | Customer updates email/phone | Verification via OTP to new contact |

- All changes must be audit-logged (who, what, when, why)
- CRA must be notified of address changes
- Change of bank details is high-risk (potential fraud) — requires SCA and may trigger additional verification

### Interest Rate Changes (Variable Rate Products)

- Customer must be notified before any rate change takes effect (CCA s.78A)
- Notice period: typically 30 days
- Notification must state: old rate, new rate, new monthly payment, effective date
- Customer has the right to repay early without penalty if they don't accept the new rate

### Annual Percentage Rate Statement

- If the actual cost of credit differs from the APR stated in the agreement by more than 1%, the lender must notify the customer (CCA s.77B)

### Liability Letters & Statements on Demand

- Liability letter: formal document stating the outstanding balance, remaining term, and monthly payment. Used by customers for mortgage applications, visa applications, or other financial assessments.
- Customer can request a liability letter at any time (in-app, phone, or written request).
- Generation: automated from loan data. Must include: customer name, loan reference, outstanding balance as of date, original loan amount, interest rate, remaining term, monthly payment amount, next payment date.
- Delivery: PDF generated and available for download in-app. Also sent via email.
- Turnaround: within 2 working days of request (automated generation should be instant).
- Fee: typically free (first per year). Some lenders charge for additional copies.
- Settlement letter: issued after loan is fully repaid. Confirms zero balance and that the account is closed. Must be provided within 14 days of settlement.
- PM IMPLICATION: stories must cover liability letter request flow, automated PDF generation, in-app download, email delivery, and settlement letter generation post-closure. The liability letter is a common customer request that is often missing from initial builds.

### Communication Preferences

- Customer can choose: email, SMS, push notification, post
- Marketing communications require separate GDPR consent
- Regulatory communications (arrears notices, rate changes, annual statements) cannot be opted out of — they are legal requirements
- Customer can request paper copies of any digital communication

### PM IMPLICATION

Servicing is the longest phase of the loan lifecycle but often gets the least product attention. Stories must cover: annual statement generation and delivery, on-demand statement request, transaction history view, change of address/name/bank details flows (each with verification), rate change notification (variable products), communication preference management, and the distinction between marketing communications (opt-in) and regulatory communications (mandatory). The change-of-bank-details flow is particularly important — it's a common fraud vector and needs strong verification.

---

## PD20: Fraud Prevention

Fraud risks specific to consumer lending:

### Application Fraud Types

| Type | Description | Detection |
|---|---|---|
| Identity theft | Fraudster uses stolen identity to apply | KYC liveness check, device fingerprinting, velocity checks |
| Synthetic identity | Fabricated identity using mix of real and fake data | CRA data inconsistencies, thin credit file, no electoral roll match |
| First-party fraud | Applicant has no intention to repay | Behavioural analysis, income inflation detection, multiple applications |
| Facility takeover | Fraudster gains access to existing customer's account | Unusual login patterns, device change, immediate bank detail change |
| Broker fraud | Broker submits inflated or fabricated applications | Broker performance monitoring, application quality scoring |

### Fraud Detection Signals

- Device fingerprinting: is this device associated with previous fraud?
- Velocity checks: multiple applications from same device/IP/email in short period
- Email age: newly created email addresses are higher risk
- Phone verification: is the phone number active and registered to the applicant?
- Address verification: does the address exist? Is it a known fraud address (e.g., vacant property)?
- Income verification: does declared income match CRA data, Open Banking data, or employer records?
- Behavioural biometrics: typing speed, mouse movement, form completion time (bots vs humans)

### Fraud Rules Engine

- Rules-based: hard rules that block or refer (e.g., "if applicant age < 18, block", "if 3+ applications from same IP in 24 hours, refer")
- Score-based: fraud score combining multiple signals, threshold for auto-approve/refer/block
- Machine learning: anomaly detection on application patterns (requires GDPR Article 22 compliance for automated decisions)

### Authorised Push Payment (APP) Fraud

- Customer is tricked into making a payment to a fraudster (not directly a lending risk, but relevant if customer uses loan funds for a scam payment)
- Contingent Reimbursement Model (CRM) Code: participating banks reimburse victims of APP fraud in most cases
- Confirmation of Payee (CoP) is the primary defence

### Regulatory Obligations

- MLR 2017: firms must have systems and controls to prevent money laundering and terrorist financing
- FCA SYSC 6.1.1R: firms must have adequate policies and procedures to counter the risk of financial crime
- Suspicious Activity Reports (SARs): if fraud is suspected, firm must file a SAR with the National Crime Agency (NCA). Must NOT tip off the customer.

### PM IMPLICATION

Fraud prevention must be embedded in the application flow, not bolted on. Stories must cover: device fingerprinting at app install, velocity checks during application, KYC liveness as anti-fraud (not just compliance), income verification cross-checks, fraud referral queue for operations team, SAR filing workflow (back-office), and the balance between fraud prevention and customer friction (too many checks = abandonment, too few = fraud losses). The fraud rules engine is a separate system that needs its own configuration stories.

---

## PD21: Open Banking

Open Banking capabilities relevant to lending:

### Account Information Services (AISP)

- Read-only access to customer's bank account data with explicit consent
- Data available: account details, balances, transaction history (typically 12 months)
- Use in lending: income verification (salary credits), expenditure analysis (spending patterns), affordability assessment (real-time financial picture), risk indicators (gambling, payday loans, returned DDs)
- Consent: customer authenticates via their bank's app (SCA), grants access to specific accounts, consent valid for 90 days (re-authentication required)
- Multi-bank: customer can share data from multiple bank accounts for a complete financial picture
- Regulatory basis: PSD2 / Payment Services Regulations 2017, regulated by FCA

### Payment Initiation Services (PISP)

- Initiate payments directly from customer's bank account (alternative to card or manual transfer)
- Use in lending: one-off repayments, settlement payments, overpayments
- Customer authenticates via their bank's app (SCA with dynamic linking — amount and payee shown)
- Lower cost than card payments (no interchange fees)
- Irrevocable once authorised (like Faster Payments)
- Regulatory basis: PSD2, regulated by FCA

### Variable Recurring Payments (VRP)

- Emerging capability: customer authorises recurring payments with variable amounts within agreed parameters (max amount, frequency)
- Use in lending: could replace Direct Debit for loan repayments — real-time settlement, better control for customer
- Currently limited to sweeping use cases (moving money between own accounts) but commercial VRP expanding
- PM IMPLICATION: VRP is future-state but worth designing for — the repayment architecture should be payment-method-agnostic

### Customer Experience

- Bank selection screen: customer chooses their bank from a list of supported banks
- Redirect to bank app: customer authenticates in their bank's app (biometric or password)
- Return to lender app: after authentication, customer is redirected back with consent confirmed
- Error handling: bank app not installed, authentication timeout, consent declined, bank unavailable

### PM IMPLICATION

Open Banking is a major differentiator for fintechs. Stories must cover: AISP consent flow (bank selection, redirect, return), transaction data display (categorised income/expenditure), affordability calculation using Open Banking data, PISP payment flow (for repayments and settlement), consent management (view active consents, revoke consent), re-authentication every 90 days, multi-bank aggregation, and fallback for customers who decline Open Banking (document upload path). The consent flow involves leaving the lender's app and returning — this must be seamless and handle all error cases (timeout, decline, bank app crash).

---

## PD22: Financial Promotions

FCA rules on advertising and marketing lending products:

### CONC 3: Financial Promotions

- Any communication that invites or induces a person to enter into a credit agreement is a financial promotion
- This includes: app store listing, website landing page, email marketing, social media posts, in-app product catalog, comparison site listings, push notifications about loan products

### Required Content

If a financial promotion includes a "trigger" (any of: interest rate, amount of credit, repayment amount, or any other cost figure), it MUST also include:
- Representative APR
- Representative example (see PD4)
- Total amount payable

All three must be given equal prominence to the trigger.

### Prominence Rules

- Representative APR must be more prominent than any other rate or cost figure (CONC 3.5.3R)
- Risk warnings must not be hidden in small print
- "From" rates (e.g., "rates from 3.9%") must be accompanied by representative APR
- Personalised rates shown after eligibility check are not financial promotions (they are pre-contract information)

### Social Media & Digital

- Character-limited formats (tweets, stories): if a trigger is included, the representative APR and example must be accessible (e.g., via link to landing page with full details)
- Influencer marketing: if an influencer promotes a loan product, it is a financial promotion and must comply with CONC 3
- In-app notifications: a push notification saying "You're pre-approved for GBP 5,000" is a financial promotion

### Record Keeping

- All financial promotions must be retained for at least 3 years (FCA SYSC 9.1.1R)
- Must be able to demonstrate compliance with CONC 3 for any promotion

### PM IMPLICATION

Every screen that shows a loan product with any cost figure is a financial promotion. The product catalog, eligibility result, comparison page, and marketing emails all need representative APR and representative example. Stories must cover: product listing with compliant representative example, eligibility result display (personal rate + representative APR), marketing email templates with required content, push notification content compliance, and a financial promotions approval workflow (legal/compliance review before any promotion goes live).

---

## PD23: Refunds & Adjustments

When the lender owes money to the customer:

### Refund Scenarios

| Scenario | Trigger | Amount | Timeline |
|---|---|---|---|
| Overpayment beyond settlement | Customer pays more than settlement figure | Excess amount | Refund within 5 working days |
| DD collected after settlement | Direct Debit collected after loan was settled | Full DD amount | Refund within 5 working days |
| Cooling-off withdrawal | Customer withdraws within 14 days, overpaid | Excess over principal + accrued interest | Refund within 30 days of withdrawal |
| Compensation | Complaint upheld, FOS award | Determined amount | Per FOS timeline |
| Fee reversal | Fee charged in error or as goodwill gesture | Fee amount | Immediate |
| Interest overcharge | Calculation error discovered | Overcharged amount + 8% statutory interest | As soon as identified |

### Refund Methods

- Refund to the account the payment came from (anti-money laundering best practice)
- If original account is closed: refund to customer's nominated account (verified via CoP)
- Cheque as last resort (some customers don't have bank accounts)

### Regulatory Requirements

- FCA Principle 6 (treating customers fairly): refunds must be processed promptly
- If a systematic error is discovered (e.g., interest calculation bug affecting multiple customers), the firm must proactively identify and refund all affected customers — not wait for complaints
- Refund amounts and reasons must be audit-logged

### PM IMPLICATION

Refunds are often forgotten in product builds but are a regulatory requirement. Stories must cover: overpayment refund (automatic detection and processing), post-settlement DD refund (detect DD after settlement, auto-refund), compensation payment (manual trigger from complaints team), fee reversal (operations tool), and the edge case of refunding to a closed account. The refund status must be visible to the customer in their dashboard.

---

## PD24: Credit Reporting Obligations

Lender's duty to report accurate data to Credit Reference Agencies:

### Monthly Reporting

- Lenders must report account data to CRAs (Experian, Equifax, TransUnion) monthly.
- Data reported: account status (active, settled, defaulted), current balance, credit limit, payment status (up to date, 1 month arrears, 2 months, etc.), payment amount, account open date, settlement date.
- Reporting must be accurate and timely — within 5 working days of month-end.
- Incorrect reporting can result in FCA enforcement action and customer complaints.

### What Triggers CRA Updates

| Event | CRA Update | Timing |
|---|---|---|
| Loan disbursed | New account reported | Next monthly report |
| Payment received | Payment status updated, balance reduced | Next monthly report |
| Payment missed | Arrears marker added | Next monthly report |
| Default registered | Default marker added (stays 6 years) | Within 5 working days |
| Loan settled | Account marked as settled, balance zero | Within 30 days |
| Early settlement | Account marked as settled early | Within 30 days |
| Forbearance arrangement | Arrangement flag added | Next monthly report |
| Address change | New address linked | Next monthly report |

### Customer Disputes

- Customer can dispute data with CRA or lender. Lender must investigate within 28 days.
- If data is wrong: correct and notify CRA. If correct: explain to customer.
- During investigation, CRA may add a "notice of dispute".
- GDPR Article 16: customer has right to have inaccurate data corrected without undue delay.

### PM IMPLICATION

Credit reporting is an ongoing operational obligation. Stories must cover: monthly CRA reporting batch job, real-time CRA updates for defaults and settlements, customer dispute handling workflow, and CRA data accuracy monitoring.

---

## PD25: Loan Restructuring

When forbearance is insufficient and loan terms need formal change:

### Restructuring Options

| Option | Description | Impact |
|---|---|---|
| Term extension | Extend repayment period | Lower monthly payment, more total interest |
| Rate reduction | Reduce interest rate | Lower monthly payment |
| Balance write-down | Write off portion of balance | Reduced debt, lender takes loss |
| Capitalisation of arrears | Add arrears to balance, recalculate | Clears arrears status, higher balance |

### Legal Requirements

- Creates a NEW credit agreement (CCA s.82). Original superseded.
- New agreement must contain all prescribed terms (CCA s.61).
- New PCCI required. New 14-day cooling-off period.
- CRA updated with restructured status.

### Income & Expenditure Review

- Full I&E review required before restructuring.
- Standard Financial Statement (SFS) format used by debt advice sector.
- If customer has a debt advisor, their I&E should be accepted.

### PM IMPLICATION

Restructuring needs: I&E collection form, restructuring option calculation, old vs new terms comparison display, new agreement signing flow, CRA update, and updated repayment schedule.
