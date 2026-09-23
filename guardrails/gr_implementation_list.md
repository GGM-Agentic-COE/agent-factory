# Guardrails Implementation Requirements

This document outlines the guardrail coverage required for the system, distinguishing between guardrails already handled by AAVA and those that must be implemented separately.

---

## 1. Already Implemented by AAVA (No Action Required)

The following guardrails are already covered by AAVA and do **not** need to be re-implemented:

| # | Guardrail | Description |
|---|-----------|--------------|
| 1 | **Hate Speech** | Detects and blocks content containing hate speech, discriminatory language, or targeted harassment. |
| 2 | **Jailbreak** | Detects and prevents prompt injection or jailbreak attempts aimed at bypassing model safety constraints. |
| 3 | **Self Harm** | Detects and blocks content related to self-harm, suicide, or related risk indicators. |
| 4 | **Sexual** | Detects and blocks sexually explicit or inappropriate content. |
| 5 | **Violence** | Detects and blocks violent or graphic content. |

> **Note:** These guardrails are inherited from AAVA's existing safety layer. No additional development or integration work is required for the above categories.

---

## 2. Compulsory Implementation

The following guardrails **must** be implemented as part of this project. Each is described below along with its purpose and scope.

### 2.1 `gr-L1-input-validator`
- **Layer:** L1 (Input)
- **Purpose:** Validates all incoming user input before it reaches the model or downstream systems.
- **Scope:** Enforces expected input formats, schema constraints, length limits, and rejects malformed or malicious input payloads.

### 2.2 `gr-L1-pii-detection`
- **Layer:** L1 (Input)
- **Purpose:** Detects and flags/redacts Personally Identifiable Information (PII) present in user input.
- **Scope:** Covers common PII types (names, addresses, phone numbers, email addresses, government IDs, financial information, etc.) to prevent unintended exposure or processing of sensitive personal data.

### 2.3 `gr-L1-secrets-protection`
- **Layer:** L1 (Input)
- **Purpose:** Detects and blocks secrets (API keys, credentials, tokens, passwords, connection strings, etc.) from being passed into or leaked out of the system.
- **Scope:** Applies to both inbound user input and any generated output that may inadvertently expose secrets.

### 2.4 `gr-L2-policy-enforcement`
- **Layer:** L2 (Policy)
- **Purpose:** Enforces business/use-case-specific policies and rules.
- **Scope:** **Must be created individually for each agent / specific task / use case** — this is not a one-size-fits-all guardrail. Each agent or workflow requires its own tailored policy definition covering permitted actions, response boundaries, and domain-specific compliance rules.
- **Action Required:** Define and implement a dedicated policy enforcement guardrail per agent/task/use case prior to deployment.

### 2.5 `gr-L3-hallucination-detector`
- **Layer:** L3 (Output)
- **Purpose:** Detects potential hallucinations or factually unsupported claims in model-generated output.
- **Scope:** Validates output against source data/context (where applicable) and flags or blocks responses that are not grounded in verified information.

### 2.6 'quality/confidence gate'
### 2.7 'Output-validator'
### 2.8 'token control'
---

## Summary Table

| Guardrail ID | Layer | Status | Notes |
|---|---|---|---|
| Hate Speech | — | ✅ Already implemented (AAVA) | No action needed |
| Jailbreak | — | ✅ Already implemented (AAVA) | No action needed |
| Self Harm | — | ✅ Already implemented (AAVA) | No action needed |
| Sexual | — | ✅ Already implemented (AAVA) | No action needed |
| Violence | — | ✅ Already implemented (AAVA) | No action needed |
| `gr-L1-input-validator` | L1 | 🔴 Compulsory | To be implemented |
| `gr-L1-pii-detection` | L1 | 🔴 Compulsory | To be implemented |
| `gr-L1-secrets-protection` | L1 | 🔴 Compulsory | To be implemented |
| `gr-L2-policy-enforcement` | L2 | 🔴 Compulsory | To be created per agent/task/use case |
| `gr-L3-hallucination-detector` | L3 | 🔴 Compulsory | To be implemented |