# Application Baseline — Knowledge Base
### kb-L3-application-baseline v1.0.0
### Current state of the Tasheel Finance application. Used by agents to classify requirements as new/enhancement/existing.

---

## BL1: Product Inventory

| Product ID | Name | Type | Status | Parameters |
|---|---|---|---|---|
| 11111111-... | Cash Finance | Cash | Live | Tenure: 3-60mo, Rate: 15-35% (risk-based), Amount: SAR 5k-250k, Early Closure: 1%, Admin: 1.5% |
| 22222222-... | Combo Finance | Combo | Live | Tenure: 6-60mo, Rate: 18% (risk-based), Amount: SAR 10k-500k, Early Closure: 1.5%, Admin: 1% |

---

## BL2: Feature Inventory

| Feature ID | Feature Name | Status | Module | Description |
|---|---|---|---|---|
| F-01 | Product Catalog | ✅ Live | Products | Display available products with parameters |
| F-02 | Application Creation | ✅ Live | Applications | Multi-step form: personal → employment → income → review |
| F-03 | Application Submission | ✅ Live | Applications | Validate completeness, move to Submitted |
| F-04 | Decision Engine (Assessment) | ✅ Live | Applications | CITC check, SIMAH score, DBR check, risk-grade pricing, approved amount |
| F-05 | Offer Generation | ✅ Live | Offers | Create offer from assessment (amount, tenure, rate, monthly payment, total) |
| F-06 | Offer Acceptance | ✅ Live | Offers | Accept offer, trigger disbursement flow |
| F-07 | Debit Card Collection | ✅ Live | Applications | Card details entry, token storage, SINGLE-date auto-debit setup |
| F-08 | Disbursement | ✅ Live | Loans | Transfer funds post contract signing |
| F-09 | Settlement Figure | ✅ Live | Loans | Calculate: principal + accrued interest + fees - rebate + early closure fee |
| F-10 | Liability Letter | ✅ Live | Loans | Generate letter with balance, rate, term, monthly payment, next payment date |
| F-11 | Top Up Eligibility | ✅ Live | Loans | Check DBR, exposure, tenure for existing Cash/Combo customers |
| F-12 | Back Office App Creation | ✅ Live | BackOffice | Agent creates application on behalf of customer (Cash/Combo only) |
| F-13 | Payment Collection | ✅ Live | Payments | Auto-debit on scheduled date, manual payment, status tracking |
| F-14 | Payment Failure Handling | ✅ Live | Payments | Failure detection, single retry, customer notification |
| F-15 | MIS Reporting | ✅ Live | Reporting | Dashboard with product filters (Cash/Combo), application/approval/disbursement metrics |
| F-16 | Audit Logging | ✅ Live | Cross-cutting | All state transitions and PII access logged via MediatR pipeline |

---

## BL3: Screen Inventory (Mobile)

| Screen | Route | Features Used | Status |
|---|---|---|---|
| Login | /auth/login | Auth | ✅ Live |
| Product List | /products | F-01 | ✅ Live |
| Product Detail | /products/{id} | F-01 | ✅ Live |
| Application Form (4-step) | /apply/{productId} | F-02, F-03 | ✅ Live |
| Card Collection | /apply/{appId}/card | F-07 | ✅ Live |
| Offer | /offer/{appId} | F-05, F-06 | ✅ Live |
| Dashboard | /dashboard | F-13, F-09, F-10 | ✅ Live |

---

## BL4: API Inventory

| Endpoint | Method | Handler | Status |
|---|---|---|---|
| /api/v1/products | GET | GetProductsQuery | ✅ Live |
| /api/v1/applications | POST | CreateApplicationCommand | ✅ Live |
| /api/v1/applications/{id} | GET | GetApplicationQuery | ✅ Live |
| /api/v1/applications/{id}/submit | POST | SubmitApplicationCommand | ✅ Live |
| /api/v1/applications/{id}/assess | POST | AssessApplicationCommand | ✅ Live |
| /api/v1/applications/{id}/card | POST | RegisterCardCommand | ✅ Live |
| /api/v1/applications/{id}/offer | GET | GetOfferQuery | ✅ Live |
| /api/v1/applications/{id}/offer/accept | POST | AcceptOfferCommand | ✅ Live |
| /api/v1/loans | GET | GetLoansQuery | ✅ Live |
| /api/v1/loans/{id} | GET | GetLoanQuery | ✅ Live |
| /api/v1/loans/{id}/settlement-figure | GET | GetSettlementFigureQuery | ✅ Live |
| /api/v1/loans/{id}/liability-letter | GET | GetLiabilityLetterQuery | ✅ Live |
| /api/v1/loans/{id}/topup-eligibility | GET | GetTopUpEligibilityQuery | ✅ Live |
| /api/v1/loans/{id}/payments | GET | GetPaymentsQuery | ✅ Live |
| /api/v1/loans/{id}/payments | POST | CreatePaymentCommand | ✅ Live |
| /api/v1/backoffice/applications | POST | CreateBoApplicationCommand | ✅ Live |
| /health | GET | HealthController | ✅ Live |
| /health/ready | GET | HealthController | ✅ Live |

---

## BL5: Data Model (Tables)

| Table | Key Columns | PII Encrypted | Status |
|---|---|---|---|
| Products | Id, Name, Type, MinAmount, MaxAmount, MinTenure, MaxTenure, BaseRate, EarlyClosureFeePercent, AdminFeePercent | No | ✅ Live |
| LoanApplications | Id, UserId, ProductId, Status, RequestedAmount, ApprovedAmount, Tenure, Income, GrossIncome, OtherIncome, EmployerName, EmploymentType, EmploymentStartDate, FullName, NationalId, DateOfBirth, Address, City, Region, IsListed, SalaryDate | Income, GrossIncome, NationalId, DateOfBirth (AES-256) | ✅ Live |
| Offers | Id, ApplicationId, Amount, Tenure, ProfitRate, AdminFee, TotalAmount, MonthlyPayment, ValidUntil | No | ✅ Live |
| Loans | Id, ApplicationId, OfferId, DisbursedAmount, OutstandingPrincipal, Status, DisbursedAt | No | ✅ Live |
| Payments | Id, LoanId, Amount, Type, Status, AttemptNumber, FailureReason, ProcessedAt | No | ✅ Live |
| DebitCards | Id, ApplicationId, TokenReference, Last4Digits, SalaryDate, IsActive | TokenReference (encrypted) | ✅ Live |
| AutoDebitSchedules | Id, LoanId, DebitCardId, ScheduledDate, Amount, Status | No | ✅ Live |
| AuditLogs | Id, UserId, Action, Resource, ResourceId, Changes, Reason, Timestamp | No (append-only) | ✅ Live |

---

## BL6: Integration Inventory

| System | Protocol | Status | Circuit Breaker |
|---|---|---|---|
| SIMAH (Credit Bureau) | REST (sync) | ✅ Live | 5 failures / 30s → 60s break |
| CITC (Employment) | REST (sync) | ✅ Live | 3 failures / 30s → 30s break |
| Geolocation | REST (sync) | ✅ Live | 5 failures / 30s → 30s break |
| Open Banking (AISP) | REST (async redirect) | ✅ Live | 3 failures / 60s → 120s break |
| Payment Processor | REST + Webhooks | ✅ Live | 5 failures / 30s → 60s break |
| SMS Gateway | REST (fire-and-forget) | ✅ Live | 10 failures / 60s → 30s break |

---

## BL7: Known Limitations

| LIM ID | Description | Impact | Planned Resolution |
|---|---|---|---|
| LIM-01 | Card collection uses direct input (not hosted fields) | PCI-DSS risk — card data touches our frontend | BridgeNow EP-02 F-02.3 migrates to hosted fields |
| LIM-02 | Single-date auto-debit only | No retry on salary date + 3 | BridgeNow EP-02 F-02.3 adds dual-date |
| LIM-03 | No product switch capability in BO | Agent cannot switch product type mid-application | BridgeNow EP-03 F-03.2 adds switch |
| LIM-04 | No staging log for failed CITC/geo checks | Customer data lost on verification failure | BridgeNow EP-03 F-03.3 adds staging log |
| LIM-05 | No feature flag infrastructure on mobile | Cannot gradually roll out new features | BridgeNow EP-01 US-002 + EP-02 US-025 adds flags |
| LIM-06 | Settlement figure includes early closure fee for all products | Cannot offer zero-fee settlement | BridgeNow EP-01 F-01.4 adds product-type override |
| LIM-07 | Top Up only available for Cash/Combo source products | BridgeNow customers cannot top up | BridgeNow EP-05 F-05.1 adds BridgeNow as source |
| LIM-08 | No STP rate monitoring | Cannot track straight-through processing rate | BridgeNow EP-06 F-06.2 adds monitoring |

---

## BL8: Decision Engine Logic (Current)

```
AssessApplication(applicationId):
  1. Validate status == Submitted
  2. Set status = Verifying
  3. CITC employment check → if fail → Referred
  4. SIMAH credit score → if < 500 → Referred
  5. DBR check: maxMonthlyPayment = income × 0.33
  6. Calculate maxLoan using annuity formula with product.BaseRate
  7. approvedAmount = min(requestedAmount, maxLoan, product.MaxAmount)
  8. If approvedAmount < product.MinAmount → Referred
  9. Set approvedAmount, status = Approved
```

**BridgeNow changes to DE:**
- Step 5: Same DBR 33% but applied to gross salary (not net)
- Step 6: For BridgeNow, maxLoan = 1x income, capped SAR 30,000 (no annuity calc)
- Step 7: Customer cannot modify amount (read-only)
- New: Income from API only (no manual override)
- New: Flat rate 27% p.a. (bypasses risk-grade lookup)
