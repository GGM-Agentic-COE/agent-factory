# Automated Test Case Best Practices — Knowledge Base
### kb-L0-automated-testcase-standards v1.0.0
### Standards for creating Cucumber/Selenium automated tests. All test agents MUST comply.

---

## AT1: Cucumber Feature File Structure

```gherkin
@epic-EP01 @regression
Feature: {Business capability name}
  As a {role}
  I want {capability}
  So that {benefit}

  Background:
    Given the Tasheel Finance API is running
    And {common preconditions for all scenarios}

  @story-US004 @critical @smoke
  Scenario: {Descriptive title matching test scenario}
    Given {precondition with specific data}
    When {user action}
    Then {observable outcome with specific values}
    And {additional assertion}

  @story-US004 @boundary
  Scenario Outline: {Parameterised scenario title}
    Given a BridgeNow application with income <income>
    When the decision engine assesses the application
    Then the result should be <status> with amount <approved>

    Examples:
      | income | status   | approved |
      | 15000  | Approved | 15000    |
      | 40000  | Approved | 30000    |
      | 3500   | Referred | 0        |
```

## AT2: Feature File Rules

1. One feature file per story or per tightly-coupled story group
2. Feature description matches the user story format (As a / I want / So that)
3. File naming: `{story-id}-{kebab-description}.feature` (e.g., `US-004-de-bridgenow-offer-amount.feature`)
4. File location: `tests/bdd/features/{epic-id}/`
5. Tags are mandatory:
   - `@epic-{id}` on Feature
   - `@story-{id}` on each Scenario
   - `@critical | @high | @medium | @low` for priority
   - `@regression` for regression pack inclusion
   - `@smoke` for smoke pack inclusion
   - `@negative` for error/rejection paths
   - `@boundary` for boundary value tests
   - `@security` for security tests
   - `@accessibility` for accessibility tests

## AT3: Step Definition Standards

```javascript
// Step definitions: tests/bdd/steps/{domain}.steps.js

import { Given, When, Then } from '@cucumber/cucumber';

// State shared across steps within a scenario
let state = {};

// GIVEN steps: setup preconditions
Given('a BridgeNow application with income {int}', async function(income) {
  const res = await api('POST', '/api/v1/applications', {
    productId: BRIDGENOW_PRODUCT_ID,
    monthlySalary: income,
    // ... other required fields with synthetic test data
  });
  state.applicationId = res.data.id;
  await api('POST', `/api/v1/applications/${state.applicationId}/submit`);
});

// WHEN steps: perform actions
When('the decision engine assesses the application', async function() {
  state.assessmentResult = await api('POST',
    `/api/v1/applications/${state.applicationId}/assess`);
});

// THEN steps: verify outcomes
Then('the result should be {word} with amount {int}', function(status, amount) {
  expect(state.assessmentResult.data.status).toBe(status);
  if (amount > 0) expect(state.assessmentResult.data.approvedAmount).toBe(amount);
});
```

## AT4: Step Definition Rules

1. Steps are reusable across scenarios — write generic, parameterised steps
2. One step = one action or one assertion (not both)
3. Given steps: setup only, no assertions
4. When steps: actions only, no assertions
5. Then steps: assertions only, no actions
6. State shared via scenario-scoped object (reset in Before hook)
7. No hardcoded URLs — use environment config
8. No hardcoded test data — use step parameters or data tables
9. API calls use shared helper (handles auth, headers, error logging)
10. Async/await for all API and UI interactions

## AT5: Selenium/UI Test Standards

```javascript
// Page Object Model for UI tests
class ApplicationFormPage {
  constructor(driver) { this.driver = driver; }

  get nameField() { return this.driver.findElement(By.id('f-name')); }
  get salaryField() { return this.driver.findElement(By.id('f-salary')); }
  get submitButton() { return this.driver.findElement(By.css('.btn-primary')); }

  async fillForm(data) {
    await this.nameField.clear();
    await this.nameField.sendKeys(data.name);
    await this.salaryField.clear();
    await this.salaryField.sendKeys(data.salary.toString());
  }

  async submit() { await this.submitButton.click(); }
}
```

**UI Test Rules:**
1. Page Object Model (POM) mandatory — one class per screen
2. Selectors: prefer `id` > `data-testid` > `css class` > `xpath` (last resort)
3. Explicit waits (not Thread.sleep): wait for element visible/clickable
4. Screenshots on failure (auto-captured by framework)
5. Tests independent — each test starts from a known state
6. No test-to-test dependencies
7. Headless mode for CI/CD, headed mode for local debugging

## AT6: Test Data Management

1. Synthetic test data only — NEVER real PII
2. Test data factories:
   ```javascript
   const TestData = {
     standardApplicant: () => ({
       fullName: `Test User ${Date.now()}`,
       nationalId: '1234567890',
       monthlySalary: 15000,
       employer: 'Test Corp',
     }),
     lowIncomeApplicant: () => ({ ...TestData.standardApplicant(), monthlySalary: 5000 }),
     citcFailApplicant: () => ({ ...TestData.standardApplicant(), employer: 'FAIL_CORP' }),
   };
   ```
3. Each test creates its own data (no shared state between tests)
4. Cleanup: tests clean up after themselves OR use isolated DB per test run

## AT7: Directory Structure

```
tests/
├── bdd/
│   ├── features/
│   │   ├── EP-01/
│   │   │   ├── US-001-product-type-registration.feature
│   │   │   ├── US-004-de-offer-amount.feature
│   │   │   └── US-010-settlement-figure.feature
│   │   ├── EP-02/
│   │   │   ├── US-013-landing-page.feature
│   │   │   └── US-020-card-collection.feature
│   │   └── regression/
│   │       └── cash-finance-baseline.feature
│   ├── steps/
│   │   ├── application.steps.js
│   │   ├── assessment.steps.js
│   │   ├── offer.steps.js
│   │   ├── loan.steps.js
│   │   ├── payment.steps.js
│   │   └── common.steps.js
│   ├── pages/                    # Page Objects (UI tests)
│   │   ├── LoginPage.js
│   │   ├── ProductListPage.js
│   │   ├── ApplicationFormPage.js
│   │   └── DashboardPage.js
│   └── support/
│       ├── hooks.js              # Before/After hooks
│       ├── world.js              # Shared context
│       └── api-helper.js         # HTTP request helper
```

## AT8: CI/CD Integration

1. Automated tests run in CI/CD pipeline (Azure DevOps per EA6)
2. Execution order: unit → contract → integration → BDD → UI
3. Failure in any gate blocks deployment
4. Test reports published as pipeline artifacts
5. Tags control execution:
   - `@smoke`: every dev deployment
   - `@regression`: every staging deployment
   - `@e2e`: nightly full run
   - `@critical`: every deployment (all environments)

## AT9: Regression Pack Management

1. All `@regression` tagged scenarios form the regression pack
2. Regression pack grows with each epic (new scenarios added, never removed)
3. Flaky test policy: 2 consecutive failures → investigate, 3 → quarantine with ticket
4. Regression execution time budget: < 15 minutes for API, < 30 minutes for UI
5. Parallel execution: scenarios within a feature run sequentially, features run in parallel

## AT10: Quality Checklist

- [ ] Feature file has @epic and @story tags
- [ ] Every scenario has priority tag (@critical/@high/@medium/@low)
- [ ] Regression scenarios tagged @regression
- [ ] Step definitions are reusable (parameterised)
- [ ] No hardcoded URLs or credentials
- [ ] Test data uses synthetic factories
- [ ] UI tests use Page Object Model
- [ ] Explicit waits (no sleep)
- [ ] Screenshots on failure
- [ ] Tests are independent (no shared state)
- [ ] Cleanup in After hooks
- [ ] Feature file readable by non-technical stakeholders

---

## AT11: Reference Implementation

The existing Tasheel Finance test suite at `backend/tests/` demonstrates the approved patterns:

| File | Pattern | Tests |
|---|---|---|
| `unit/api.test.js` | Unit tests per endpoint with isolated server | 33 |
| `contract/schema.test.js` | Response schema validation (assertShape) | 15 |
| `integration/flows.test.js` | End-to-end flow tests (full lifecycle) | 12 |
| `bdd/loan-lifecycle.steps.test.js` | BDD scenarios matching Gherkin feature | 11 |
| `bdd/features/loan-lifecycle.feature` | Gherkin feature file with 11 scenarios | — |

New automated tests MUST follow these established patterns:
- HTTP helper: raw `http.request` (no external test HTTP libraries)
- Server: `createApp()` from `helpers/test-app.js` (in-memory, isolated per suite)
- Assertions: Jest `expect` with specific value checks (not just truthy)
- State: shared within scenario via `state` object, reset in `beforeEach`

## AT12: Worked Example — Feature File for US-004

```gherkin
@epic-EP01 @regression
Feature: BridgeNow Decision Engine — Offer Amount Calculation
  As a system administrator
  I want the DE to calculate BridgeNow offer at 1x income capped at SAR 30,000
  So that customers receive compliant offers within product parameters

  Background:
    Given the Tasheel Finance API is running
    And BridgeNow product type is registered

  @story-US004 @critical @smoke
  Scenario: Approve 1x income when below cap
    Given a BridgeNow application with monthly salary SAR 12,000
    When the decision engine assesses the application
    Then the application should be Approved
    And the approved amount should be SAR 12,000

  @story-US004 @critical @boundary
  Scenario: Cap amount at SAR 30,000 for high income
    Given a BridgeNow application with monthly salary SAR 40,000
    When the decision engine assesses the application
    Then the application should be Approved
    And the approved amount should be SAR 30,000

  @story-US004 @critical @negative
  Scenario: Reject income below SAR 4,000 minimum
    Given a BridgeNow application with monthly salary SAR 3,500
    When the decision engine assesses the application
    Then the application should be Referred
    And the rejection reason should mention "minimum"

  @story-US004 @medium @boundary
  Scenario Outline: Boundary values for income-based amount calculation
    Given a BridgeNow application with monthly salary SAR <income>
    When the decision engine assesses the application
    Then the application should be <status>
    And the approved amount should be SAR <approved>

    Examples:
      | income | status   | approved | note                    |
      | 4000   | Approved | 4000     | Exact minimum boundary  |
      | 4001   | Approved | 4001     | Just above minimum      |
      | 3999   | Referred | 0        | Just below minimum      |
      | 30000  | Approved | 30000    | Exact cap boundary      |
      | 30001  | Approved | 30000    | Just above cap          |

  @story-US004 @critical @regression
  Scenario: Cash Finance DE unchanged after BridgeNow deployment
    Given a Cash Finance application with monthly salary SAR 15,000
    When the decision engine assesses the application
    Then the application should be Approved
    And the approved amount should use risk-grade-based calculation
    And the approved amount should NOT be capped at SAR 30,000
```
