# {{tool-name}}

## 1. Executive summary

{{2–3 sentences: what goes in, what the tool does, what comes out.}}

**Key points** (details in [Section 6](#6-nuances)):

- {{Most important gotcha, e.g. required input format}}
- {{Behaviour that surprises users, e.g. what happens if X already exists}}
- {{Third gotcha, if any}}

---

## 2. How to use

### 2.1 Calling the tool in aava

Enter these values and click **Execute**.

**`{{param_1}}`**
```
{{value}}
```

**`{{param_2}}`**
```
{{value}}
```

**`{{param_3}}`**
```
{{value}}
```

### 2.2 Calling the tool in an agent

{{Which parameters change per call; which are fixed for the environment.}}

```
{{param_1}} = {{placeholder_or_variable}}
{{param_2}} = {{what the agent should pass}}
{{fixed_param}} = {{fixed value}}
```

---

## 3. Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `{{param_1}}` | {{type}} | ✓ | {{description, including format and constraints}} |
| `{{param_2}}` | {{type}} | ✓ | {{…}} |

---

## 4. Secrets & configuration

| Value | Source | Notes |
|-------|--------|-------|
| `{{secret_1}}` | AWS Secrets Manager — `{{secret-name}}`, key `{{key}}` | {{notes}} |

Before deploying to a new environment, review every value tagged `SETUP-REQUIRED:` in `{{production file}}`.

---

## 5. Import modules required

| Module | Package | Used for |
|--------|---------|----------|
| `{{module}}` | `{{pip package}}` | {{purpose}} |

---

## 6. Nuances

{{Things a user or agent must do differently because of how this tool or its target system works. One short paragraph each: the behaviour, then what to do about it.}}

### 6.1 {{Nuance}}
{{Behaviour.}} **Do:** {{action}}.

### 6.2 {{Nuance}}
{{Behaviour.}} **Do:** {{action}}.

---

## 7. Appendix

### 7.1 API workflow

| Step | API call | Purpose |
|------|----------|---------|
| 1 | `{{METHOD}} {{endpoint}}` | {{purpose}} |

### 7.2 Returns

**Success**
```
{{output}}
```

**Error**
```
{{error output format}}
```

| Error | Cause | Fix |
|-------|-------|-----|
| `{{code}}` | {{cause}} | {{fix}} |

### 7.3 Known limitations

{{What the tool cannot do by design, i.e. operations and options it does not support. Derive these from the code and parameters, not from guesses. Robustness gaps (timeouts, retries, validation) belong in 7.4, not here.}}

- {{Unsupported operation, e.g. "Cannot overwrite or delete content"}}
- {{Missing option, e.g. "No parameter for X; always defaults to Y"}}

### 7.4 Security & resilience

**Security**
- {{How credentials are handled and what is/isn't logged}}

**Resilience**

| Concern | Current state | Recommendation |
|---------|---------------|----------------|
| Timeout | {{state}} | {{recommendation}} |
| Retry | {{state}} | {{recommendation}} |
| Concurrency | {{state}} | {{recommendation}} |
| Input validation | {{state}} | {{recommendation}} |
