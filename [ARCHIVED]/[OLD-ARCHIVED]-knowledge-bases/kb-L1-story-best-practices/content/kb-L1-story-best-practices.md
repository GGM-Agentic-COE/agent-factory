# Best Practices for Composing User Stories

---

## 1. Writing the User Story Statement (ref: PM-BP-015)

**Best Practices:**
- Always follow the format: "As a [role], I want [capability], so that [benefit]"
- The role must be a specific banking persona, not "user" or "someone"
- The capability must describe what the user does, not what the system does internally
- The benefit must state the business or personal value — why this matters
- One story = one capability. If you write "and" between two distinct actions, split into two stories

**Role Specificity:**

| Too Vague | Correct |
|---|---|
| As a user | As a retail banking customer |
| As an admin | As a branch operations manager |
| As a banker | As a relationship manager for premium clients |
| As a system | (Not a user story — this is a technical task) |

**Capability Specificity:**

| Too Vague | Correct |
|---|---|
| I want to manage my money | I want to transfer funds to a registered beneficiary |
| I want to see my account | I want to view my current account balance and last 10 transactions |
| I want to do payments | I want to schedule a recurring bill payment to a utility provider |

**Benefit Specificity:**

| Too Vague | Correct |
|---|---|
| So that it works | So that I can make payments without visiting a branch |
| So that I'm happy | So that I can track my spending in real time |
| So that we comply | So that suspicious transactions are flagged within 5 minutes per AML requirements |

**Common Mistakes:**
- Writing stories from the system's perspective ("As the system, I want to validate...") — reframe as user need
- Omitting the benefit — the "so that" clause drives prioritization and design decisions
- Combining multiple capabilities ("I want to transfer funds and view my balance") — split them
- Using technical language ("I want to call the REST API") — describe the user's goal

---

## 2. Writing Acceptance Criteria with Security & Compliance Checks (ref: PM-BP-016)

**Best Practices:**
- Structure acceptance criteria into three dedicated sections: Functional, Security, and Compliance
- Use Given/When/Then format consistently for all three sections
- Every criterion must be independently testable with a clear pass/fail outcome
- Include both positive (happy path) and negative (rejection/error) criteria
- Include boundary conditions (limits, edge cases, thresholds)
- Security and compliance criteria are not optional extras — they are first-class acceptance criteria

**Functional Acceptance Criteria:**
Focus on business behavior — what the user experiences.
```
Given [user context and preconditions],
When [user action],
Then [observable outcome with specific values].
```

**Security Acceptance Criteria (ref: PM-BP-016):**
Focus on security controls — what prevents misuse.
```
# Authentication enforcement
Given an unauthenticated user,
When they attempt to access the transfer endpoint,
Then they receive 401 Unauthorized with no data leakage.

# Authorization enforcement
Given Customer A authenticated,
When they attempt to access Customer B's account via API parameter manipulation,
Then they receive 403 Forbidden and the attempt is logged and alerted.

# Input validation
Given a user submitting a transfer,
When the amount field contains SQL injection or XSS payload,
Then the input is rejected server-side and the attempt is logged.

# Session management
Given a user session inactive for 15 minutes,
When they attempt any action,
Then the session is expired and re-authentication is required.

# MFA enforcement
Given a user initiating a fund transfer,
When they provide an expired OTP (>90 seconds),
Then the OTP is rejected and a new one must be requested.
```

**Compliance Acceptance Criteria (ref: PM-BP-016):**
Focus on regulatory obligations — what the law requires.
```
# AML reporting
Given a completed transfer of $10,000 or more,
When the transaction settles,
Then a Currency Transaction Report is automatically generated with all required fields.

# PSD2 SCA
Given a customer initiating a payment,
When step-up authentication is triggered,
Then two independent authentication factors are required per PSD2 Art. 97.

# GDPR consent
Given a customer opting into marketing communications,
When they provide consent,
Then the consent is recorded with timestamp, purpose, and mechanism per GDPR Art. 7.

# Data retention
Given a transaction older than 7 years,
When the retention policy runs,
Then the transaction is archived/anonymized per the data retention policy.
```

**Common Mistakes:**
- Security criteria buried inside functional criteria — keep them separate and visible
- "The system should be secure" — not a testable criterion
- No negative test criteria — only testing happy path misses vulnerabilities
- Compliance criteria without regulation reference — always cite the article

---

## 3. Tagging Stories with Data Sensitivity (ref: PM-BP-017)

**Best Practices:**
- Every story must have a Data Sensitivity Tag at the story level (highest sensitivity of data touched)
- Additionally, list individual Data Fields Involved with per-field classification and CRUD operation
- The tag drives downstream requirements: encryption, access control, audit depth, testing rigor, non-prod data handling
- Review the tag when story scope changes — adding a data field can change the classification
- Stories tagged Restricted or Confidential automatically require security acceptance criteria

**Tagging Decision Flow:**

```
Does the story touch card data (PAN, CVV, PIN)?
  → Yes → Restricted

Does the story touch passwords, biometrics, or encryption keys?
  → Yes → Restricted

Does the story touch customer PII (name, address, DOB, email, phone, national ID)?
  → Yes → Confidential

Does the story touch financial data (account numbers, balances, transaction amounts)?
  → Yes → Confidential

Does the story touch internal business data (policies, configs, employee data)?
  → Yes → Internal

None of the above?
  → Public
```

**Tag-Driven Requirements:**

| Requirement | Restricted | Confidential | Internal | Public |
|---|---|---|---|---|
| Security acceptance criteria | Mandatory | Mandatory | Recommended | Optional |
| Compliance acceptance criteria | Mandatory | Mandatory (if regulated) | If applicable | Optional |
| Audit logging | Full (all access) | Full (all modifications) | Auth events | Minimal |
| MFA requirement | Always | For modifications | Not required | Not required |
| Input validation testing | Mandatory (DAST) | Mandatory (SAST) | Standard | Standard |
| Data masking in non-prod | Full anonymization | Tokenization | Recommended | Not required |
| Encryption at rest | AES-256 + HSM | AES-256 | Recommended | Not required |

**Per-Field Classification Format:**
> Field Name | Classification | CRUD | Validation | Masking

**Example:**
```
Source Account  | Confidential | Read    | Dropdown (own accounts only) | Mask in logs (last 4 digits)
Amount          | Confidential | Create  | Decimal, 2dp, min 0.01, max 999,999,999.99 | Plain in logs
Beneficiary     | Confidential | Read    | Dropdown (registered only)  | Mask in logs (last 4 digits)
OTP             | Restricted   | Create  | 6-digit numeric, single-use, 90s expiry | Never log
Transaction Ref | Internal     | Create  | System-generated UUID       | Plain in logs
```

---

## 4. Specifying Authentication & Authorization Requirements (ref: PM-BP-018)

**Best Practices:**
- Every story must explicitly state the authentication level required — never assume "logged in is enough"
- Every story must explicitly state the authorization scope — what the user can access and what they cannot
- Auth requirements must follow the principle of least privilege
- Step-up authentication must be specified for high-risk operations (fund transfers, profile changes, limit modifications)
- Authorization must be enforced at the resource level, not just the role level

**Authentication Level Selection:**

| Operation Risk | Auth Level | When to Use |
|---|---|---|
| No risk | None | Public information (rates, branch locator) |
| Low risk | Basic session | View own non-sensitive data (preferences, notifications) |
| Medium risk | Authenticated session | View own financial data (balance, transactions) |
| High risk | MFA / Step-Up MFA | Financial transactions, profile changes, beneficiary management |
| Critical risk | MFA + additional verification | Large transfers (above threshold), international transfers, limit changes |
| Administrative | MFA + JIT privileged access | System configuration, user management, role assignment |

**Authorization Specification Format:**
```
Role: [specific role]
Scope: [own-account / own-profile / assigned-customers / all (admin)]
Resource check: [what resource-level validation is performed]
Segregation of duties: [maker-checker requirement if applicable]
Limit check: [transaction/daily/monthly limits if applicable]
```

**Example:**
```
Role: Retail Customer
Scope: Own-account only
Resource check: Source account must belong to authenticated customer; beneficiary must be in customer's registered list
Segregation of duties: N/A (single-user operation)
Limit check: Daily transfer limit — $50,000 retail / $500,000 premium
```

**What to Specify in the Story:**
- Auth level for the primary action
- Auth level for any secondary actions within the story
- What happens on auth failure (error message, lockout, alert)
- Session timeout behavior for this operation
- Whether the auth token/session is sufficient or step-up is needed

**Common Mistakes:**
- "User must be logged in" — too vague; specify the auth level
- No resource-level authorization — role check alone allows IDOR vulnerabilities
- No step-up for financial operations — violates PSD2 SCA
- Auth requirements not in acceptance criteria — they must be testable

---

## 5. Specifying Audit Logging Requirements (ref: PM-BP-019)

**Best Practices:**
- Every story touching sensitive data or financial transactions must specify what gets logged
- Define audit events for each significant action in the story (not just the final outcome)
- Specify the exact fields to capture per event — don't leave it to developer interpretation
- Specify what must NOT be logged (passwords, full PAN, OTPs, tokens)
- Specify retention period aligned with regulatory requirements
- Specify that logs must be immutable and stored separately from application data
- Include audit log verification in the Definition of Done

**Audit Event Specification Format:**
```
Event: [what happened]
Trigger: [what action triggers this log entry]
Fields: [list of fields captured]
Sensitivity: [are any logged fields sensitive — masking required?]
Retention: [how long to keep]
```

**Example — Fund Transfer Story Audit Events:**
```
Event 1: Transfer Initiated
Trigger: Customer submits transfer form
Fields: user_id, session_id, source_ip, device_fingerprint, source_account (masked), beneficiary_id, amount, currency, timestamp
Sensitivity: Account numbers masked to last 4 digits
Retention: 7 years

Event 2: MFA Verified
Trigger: Customer completes step-up MFA
Fields: user_id, mfa_method, mfa_outcome (success/failure), timestamp, device_fingerprint
Sensitivity: OTP value never logged
Retention: 3 years

Event 3: Fraud Check Completed
Trigger: Fraud engine returns result
Fields: user_id, transaction_ref, fraud_score, fraud_decision (approve/hold/reject), timestamp, correlation_id
Sensitivity: None
Retention: 7 years

Event 4: Transfer Executed
Trigger: Core banking confirms debit/credit
Fields: user_id, transaction_ref, source_account (masked), beneficiary_account (masked), amount, currency, status, core_banking_ref, timestamp
Sensitivity: Account numbers masked
Retention: 7 years

Event 5: Transfer Failed/Rejected
Trigger: Any failure in the flow
Fields: user_id, transaction_ref, failure_reason, failure_step, timestamp, correlation_id
Sensitivity: None
Retention: 7 years
```

**What Must Never Be Logged:**
- Passwords or password hashes
- Full card numbers (PAN) — log only last 4 digits
- CVV, PIN, or track data
- OTP values
- Authentication tokens or session secrets
- Encryption keys
- Full national ID numbers — mask to last 4 digits

**Common Mistakes:**
- No audit specification — developers log inconsistently or not at all
- Logging sensitive data in clear text — creates a data breach vector via logs
- Only logging success — failures and rejections are equally important for forensics
- No retention specification — logs kept forever (storage cost) or deleted too early (compliance risk)
- Audit logging as afterthought — must be designed into the story from the start

---

## 6. Writing the Definition of Done

**Best Practices:**
- Every story must have a DoD checklist — it's the quality gate before "done"
- DoD must include security, compliance, audit, and accessibility items — not just "code works"
- DoD items must be verifiable — each item is a yes/no check
- DoD should be consistent across stories but can have additional items for high-sensitivity stories

**Standard DoD for Banking User Stories:**

| Category | DoD Item | Always | If Confidential/Restricted |
|---|---|---|---|
| Code | Code complete and peer-reviewed (2 reviewers for Restricted) | ✅ | ✅ (2 reviewers) |
| Tests | Unit test coverage ≥ 80% | ✅ | ✅ |
| Tests | Integration tests passing | ✅ | ✅ |
| Security | SAST scan — zero critical/high findings | ✅ | ✅ |
| Security | DAST scan — zero critical/high findings | — | ✅ |
| Security | Auth flow tested (positive + bypass attempts) | If auth involved | ✅ |
| Security | Input validation tested (injection, XSS) | ✅ | ✅ |
| Compliance | Compliance acceptance criteria verified | If regulated | ✅ |
| Audit | Audit logging verified — all events captured correctly | If sensitive data | ✅ |
| Audit | Sensitive data not in logs verified | If sensitive data | ✅ |
| Performance | Response time within NFR target | If customer-facing | ✅ |
| Accessibility | WCAG 2.1 AA verified | If UI involved | ✅ |
| Documentation | API contract documented | If API involved | ✅ |
| Deployment | Deployed to staging and smoke-tested | ✅ | ✅ |

---

## 7. Decomposing Epics into User Stories

**Best Practices:**
- Split by user action, not by technical layer — each story delivers a user-visible capability
- Each story must be independently testable and demonstrable
- Maintain the data sensitivity tag from the epic — individual stories may have lower sensitivity if they touch less data
- Carry forward regulatory linkage from the epic to each applicable story
- Ensure all epic acceptance criteria are covered by at least one story's acceptance criteria

**Decomposition Patterns for Banking:**

| Epic Capability | User Stories |
|---|---|
| Fund Transfer | Initiate transfer, View transfer status, Cancel pending transfer, View transfer history, Download transfer receipt |
| Beneficiary Management | Add beneficiary, Edit beneficiary, Delete beneficiary, View beneficiary list, Verify beneficiary (penny test) |
| Account Inquiry | View balance, View transaction history, Filter transactions, Download statement, View account details |
| Customer Onboarding | Submit application, Upload ID documents, Complete KYC questionnaire, Accept T&C, Receive account confirmation |

**INVEST Criteria:**
Every story should be:
- **I**ndependent — minimal dependencies on other stories
- **N**egotiable — details can be discussed, not a rigid contract
- **V**aluable — delivers value to the user or business
- **E**stimable — team can estimate the effort
- **S**mall — completable within one sprint
- **T**estable — clear pass/fail acceptance criteria

---

## 8. Banking-Specific Story Patterns

**Financial Transaction Stories:**
Must always include: MFA, fraud screening, limit validation, audit trail, error handling for insufficient funds, duplicate detection, regulatory reporting triggers.

**Data Access Stories:**
Must always include: authorization (own-account check), audit logging of access, data masking in UI where applicable, session timeout handling.

**Administrative Stories:**
Must always include: privileged access with JIT approval, dual-control (maker-checker), comprehensive audit trail, session recording reference.

**Reporting Stories:**
Must always include: data quality validation, access control on report data, audit trail of report generation/access, regulatory accuracy requirements.

**Integration Stories:**
Must always include: timeout handling, circuit breaker behavior, retry logic, error response handling, correlation ID propagation, integration audit logging.

---

## 9. Common Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|---|---|---|
| "As a user" | No role specificity, can't determine auth/authz | Use specific banking persona |
| No "so that" clause | Can't prioritize, can't validate design | Always state the benefit |
| Technical stories ("Build API endpoint") | No user value, not testable by business | Reframe as user capability |
| No security acceptance criteria | Vulnerabilities shipped to production | Mandatory for Confidential/Restricted stories |
| No data sensitivity tag | Unknown encryption/audit/masking needs | Tag every story |
| "User must be logged in" | Insufficient auth specification | Specify exact auth level and authz scope |
| No audit logging spec | Inconsistent logging, audit failures | Specify events, fields, retention |
| Acceptance criteria without values | Untestable, subjective | Include specific thresholds and values |
| Mega-stories (> 1 sprint) | Can't complete, can't demo | Split by user action |
| Security as separate story | Security not integrated into feature | Embed security in every story's criteria |
| No negative test criteria | Only happy path tested | Include rejection, error, and bypass criteria |
| Compliance criteria without article | Can't trace to regulation | Always cite specific regulation article |
