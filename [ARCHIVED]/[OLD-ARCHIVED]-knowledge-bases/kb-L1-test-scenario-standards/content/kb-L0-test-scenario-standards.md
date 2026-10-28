# Test Scenario Best Practices — Knowledge Base
### kb-L0-test-scenario-standards v1.0.0
### Standards for deriving test scenarios from epics and user stories. All test agents MUST comply.

---

## TS1: Scenario Derivation Rules

1. Every acceptance criterion (AC) in a story MUST produce at least one test scenario
2. Every story MUST have: happy path scenario, negative/error path scenario, boundary scenario
3. Scenarios are derived from ACs — never invented beyond what the story describes
4. If an AC is ambiguous, flag as `INSUFFICIENT_CONTEXT` — do not guess

## TS2: Scenario Structure

```
Scenario ID: TS-{epic}-{story}-{seq}     (e.g., TS-EP01-US004-01)
Title: One-line description of what is being verified
Priority: Critical | High | Medium | Low
Type: Functional | Negative | Boundary | Security | Accessibility | Regression | Integration
Preconditions: What must be true before the test
Steps (high-level): Numbered actions
Expected Result: Observable outcome
Story Reference: US-XXX
AC Reference: AC #N from the story
Data Sensitivity: Public | Internal | Confidential | Restricted
```

## TS3: Scenario Types

| Type | When Required | Example |
|---|---|---|
| Functional | Every AC | "Verify offer amount equals 1x income capped at SAR 30k" |
| Negative | Every user-facing story | "Verify system rejects income below SAR 4,000" |
| Boundary | Numeric fields, limits, thresholds | "Verify exactly SAR 4,000 is accepted (min boundary)" |
| Security | Confidential/Restricted data stories | "Verify PII not in logs after assessment" |
| Accessibility | User-facing stories | "Verify screen navigable via TalkBack" |
| Regression | Brownfield enhance/modify stories | "Verify Cash Finance DE unchanged after BridgeNow" |
| Integration | Stories involving external systems | "Verify SIMAH timeout handled gracefully" |

## TS4: Priority Assignment

| Priority | Criteria |
|---|---|
| Critical | Core business flow (DE approval, disbursement, payment), regulatory requirement |
| High | Key user journey step, data integrity, security control |
| Medium | Secondary flow, UI validation, error messages |
| Low | Cosmetic, edge case with low probability |

## TS5: Coverage Rules

1. 100% AC coverage — every AC maps to at least one scenario
2. Every story has at least one negative scenario
3. Every brownfield story has at least one regression scenario
4. Every Confidential/Restricted story has at least one security scenario
5. Every user-facing story has at least one accessibility scenario
6. Boundary scenarios for: min/max amounts, date ranges, string lengths, enum values

## TS6: Traceability

Every scenario MUST link to:
- Story ID (US-XXX)
- AC reference (which specific AC it verifies)
- Requirement ID (FR-XX or NFR-XX)
- Epic ID (EP-XX)

This enables impact analysis: when a story changes, affected scenarios are identified.

## TS7: Regression Pack Rules

1. All scenarios for brownfield stories automatically join the regression pack
2. Regression scenarios verify EXISTING behaviour is unchanged
3. Regression pack is tagged `regression` for selective execution
4. Regression pack runs on every deployment (CI/CD gate)
5. New scenarios from greenfield stories join regression pack after first successful execution

## TS8: Naming Convention

```
TS-{EpicNum}-{StoryNum}-{Seq}: {Action} {Object} {Condition}
```
Examples:
- `TS-EP01-US004-01: Verify DE approves amount at 1x income`
- `TS-EP01-US004-02: Verify DE rejects income below SAR 4,000`
- `TS-EP01-US004-03: Verify DE caps amount at SAR 30,000`
- `TS-EP01-US004-04: Verify existing Cash Finance DE unchanged (regression)`

---

## TS9: Worked Example — Deriving Scenarios from Story US-004

**Story US-004**: "DE: Calculate BridgeNow Offer Amount (1x Income, Capped SAR 30k)"

**Acceptance Criteria:**
1. Income SAR 12,000 → offered SAR 12,000 (1x income, below cap)
2. Income SAR 40,000 → offered SAR 30,000 (capped)
3. Income SAR 3,500 → ineligible (below SAR 4,000 minimum)
4. Amount is read-only — customer cannot modify
5. Only API-sourced income used — no manual override

**Derived Scenarios:**

| ID | Title | Type | Priority | AC Ref |
|---|---|---|---|---|
| TS-EP01-US004-01 | Verify DE approves 1x income when below cap | Functional | Critical | AC#1 |
| TS-EP01-US004-02 | Verify DE caps amount at SAR 30,000 | Boundary | Critical | AC#2 |
| TS-EP01-US004-03 | Verify DE rejects income below SAR 4,000 | Negative | Critical | AC#3 |
| TS-EP01-US004-04 | Verify offer amount is read-only | Functional | High | AC#4 |
| TS-EP01-US004-05 | Verify only API income accepted | Security | High | AC#5 |
| TS-EP01-US004-06 | Verify exactly SAR 4,000 income is accepted (min boundary) | Boundary | Medium | AC#3 |
| TS-EP01-US004-07 | Verify exactly SAR 30,000 income gives SAR 30,000 (cap boundary) | Boundary | Medium | AC#2 |
| TS-EP01-US004-08 | Verify Cash Finance DE unchanged after BridgeNow deployment | Regression | Critical | — |
| TS-EP01-US004-09 | Verify PII not in DE assessment logs | Security | High | — |

**Coverage**: 5 ACs → 9 scenarios (5 functional + 2 boundary + 1 regression + 1 security). 100% AC coverage.
