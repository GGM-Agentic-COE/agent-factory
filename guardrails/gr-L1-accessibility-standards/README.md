# gr-L1-accessibility-standards

**Layer:** L1 Enterprise  
**Triggers on:** post_execution (output rail)  
**On fail:** Retry once, then escalate  
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid mode

## What does it do?

This guardrail ensures every agent response is accessible and inclusive — usable by people of all abilities, including those using screen readers, those with cognitive disabilities, and those with visual impairments. It enforces WCAG 2.1 AA standards, EN 301 549 (European accessibility standard), and inclusive design principles.

**On output (post-execution):** After the agent generates a response, this guardrail evaluates it against 12 accessibility criteria before delivery. If any criterion is violated, the output is sent back for regeneration with accessibility guidance.

### Standards Adherence

| Standard | Coverage | Details |
|----------|----------|---------|
| **WCAG 2.1 Level A** | ✅ Full | Non-text content (1.1.1), Info & relationships (1.3.1), Sensory characteristics (1.3.3), Use of colour (1.4.1), Page titled (2.4.2), Link purpose (2.4.4), Language of page (3.1.1), Labels (3.3.2) |
| **WCAG 2.1 Level AA** | ✅ Full | Contrast minimum (1.4.3), Headings and labels (2.4.6) |
| **WCAG 2.1 Level AAA** | Partial | Reading level (3.1.5) — enforced as guidance, not hard block |
| **EN 301 549** | ✅ Key clauses | Inclusive language, non-discriminatory content, accessibility of digital output |
| **ADA / Section 508** | ✅ Covered via WCAG | WCAG AA compliance satisfies ADA digital accessibility requirements |

### Rules — Text Content (applies to ALL output)

| # | Rule | WCAG Ref | What It Catches |
|---|------|----------|-----------------|
| 1 | Plain language | 3.1.5 (AAA) | Jargon without explanation, overly complex sentences, excessive acronyms |
| 2 | Alt text for visuals | 1.1.1 (A) | Images, diagrams, charts, ASCII art without text descriptions |
| 3 | Structured content | 1.3.1 (A), 2.4.6 (AA) | Dense unstructured paragraphs, missing headings/lists, illogical flow |
| 4 | Colour independence | 1.4.1 (A) | "Red items are errors" without labels — meaningless to 8% of men who are colour-blind |
| 5 | Actionable instructions | 1.3.3 (A), 2.4.4 (A) | "Click here", "see above", "button on the right" — fails with screen readers |
| 6 | Inclusive language | EN 301 549 | Ableist terms (blind spot, lame, crazy), gendered assumptions, exclusionary phrasing |
| 7 | Reading level | 3.1.5 (AAA) | Academic prose, nested subordinate clauses, unexpanded acronyms |

### Rules — HTML/Code Output (applies when agent generates HTML, CSS, or UI code)

| # | Rule | WCAG Ref | What It Catches |
|---|------|----------|-----------------|
| 8 | Contrast ratio | 1.4.3 (AA) | Text/background combinations below 4.5:1 (normal) or 3:1 (large text) |
| 9 | Language attribute | 3.1.1 (A) | `<html>` without `lang="en"` — screen readers can't determine pronunciation |
| 10 | Page title | 2.4.2 (A) | Missing or generic `<title>` — users can't identify the page |
| 11 | Form labels | 3.3.2 (A) | `<input>` without `<label>` or `aria-label` — form fields unnamed for screen readers |
| 12 | Link purpose | 2.4.4 (A) | `<a href="...">click here</a>` — link text must describe destination |

**Why it matters:** Enterprise agents serve diverse users. Inaccessible output creates barriers, excludes users, and can violate accessibility regulations (WCAG, ADA, EN 301 549, Equality Act 2010). This guardrail ensures output is usable by everyone — including screen reader users, colour-blind users, users with cognitive disabilities, and non-native language speakers.

## How It Works

```
Agent generates output
        ↓
┌──────────────────────────────────────────────────┐
│  ACCESSIBILITY CHECK (self_check_output)         │
│                                                  │
│  Detect output type:                             │
│  • Plain text → apply rules 1-7                  │
│  • Contains HTML → apply rules 1-12             │
│                                                  │
│  TEXT CHECKS (WCAG 3.1.5, 1.1.1, 1.3.1, 1.4.1):│
│  1. Plain language? → ✓/✗                       │
│  2. Alt text for visuals? → ✓/✗                 │
│  3. Structured with headings/lists? → ✓/✗       │
│  4. Meaning not colour-dependent? → ✓/✗         │
│  5. Instructions clear & contextual? → ✓/✗      │
│  6. Language inclusive? → ✓/✗                    │
│  7. Reading level accessible? → ✓/✗             │
│                                                  │
│  HTML CHECKS (WCAG 1.4.3, 3.1.1, 2.4.2, 3.3.2):│
│  8. Contrast ratios met? → ✓/✗                  │
│  9. lang attribute present? → ✓/✗               │
│  10. Meaningful <title>? → ✓/✗                  │
│  11. Form inputs labelled? → ✓/✗                │
│  12. Links descriptive? → ✓/✗                   │
│                                                  │
│  Any ✗ → RETRY (regenerate with fix)            │
│  All ✓ → deliver output                         │
└──────────────────────────────────────────────────┘
        ↓
Accessible, WCAG-compliant output delivered
```

## File Structure

```
gr-L1-accessibility-standards/
├── config.yml                          # Rail configuration
├── prompts.yml                         # LLM evaluation prompt (7 criteria)
├── gr-L1-accessibility-standards.co    # LLM-only Colang flow (uses self_check_output)
├── accessibility_standards.co          # Python-hybrid Colang flow (calls actions.py)
├── actions.py                          # Deterministic Python (ableist terms, vague refs, colour patterns, img alt)
├── spec.yaml                           # Guardrail specification
└── README.md                           # This file
```

**Two modes:**
- **LLM-only** (`gr-L1-accessibility-standards.co`): Uses `execute self_check_output` — all validation done by the LLM via prompts.yml. No Python dependency.
- **Python-hybrid** (`accessibility_standards.co`): Calls Python actions from `actions.py` for deterministic regex checks (ableist terms, missing alt text) + LLM for semantic checks (reading level, structure quality).

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

Tests whether the LLM can correctly evaluate output against accessibility rules. Validates the **LLM's judgement accuracy** — not the guardrail flow itself.

**Valid output (expected: "yes"):**

```
The payment initiation process involves three steps:

1. **Enter beneficiary details** — Provide the recipient's name and IBAN (International Bank Account Number).
2. **Confirm amount** — Enter the transfer amount and select the currency.
3. **Authenticate** — Complete Strong Customer Authentication (SCA) using your registered device.

Note: All fields marked with an asterisk (*) and labelled "Required" must be completed before submission.
```

**Invalid output (expected: "no"):**

```
Click here to see the red items which are the errors. The crazy thing is the system is totally lame at handling edge cases. See the diagram above for details. If you're not blind you can see the button on the right side of the screen.
```

Issues: "click here", colour-only ("red items are errors"), ableist ("crazy", "lame", "blind"), vague reference ("above", "right side"), no alt text for diagram.

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Clear structured output | None | "yes" |
| Contains "click here" | Vague reference | "no" |
| Colour-only meaning | "red items are errors" without label | "no" |
| Ableist language | "blind spot in the design" | "no" |
| Image without alt text | `<img src="diagram.png">` (no alt) | "no" |
| Dense unstructured paragraph | 500 words, no headings or lists | "no" |
| Jargon without explanation | "Configure the BFF via the CDN's WAF rules" | "no" |
| Accessible with technical terms | "Configure the Backend-for-Frontend (BFF)..." | "yes" |
| Image with alt text | `<img src="diagram.png" alt="Payment flow diagram">` | "yes" |
| Inclusive language | "The team lead reviews the output" | "yes" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

Tests the actual Colang flow as it would execute at runtime:

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L1-accessibility-standards")
rails = LLMRails(config)

# Test: accessible output should pass
response = await rails.generate_async(
    messages=[{"role": "user", "content": "Explain the payment process"}]
)
assert "blocked" not in response["content"].lower()
print("✅ Accessible output passed")

# Test: inaccessible output should be blocked
response = await rails.generate_async(
    messages=[{"role": "user", "content": "click here to see the red errors above"}]
)
assert "blocked" in response["content"].lower() or "flagged" in response["content"].lower()
print("✅ Inaccessible output blocked")
```

### Option 3: Python Unit Testing (standalone actions.py)

```python
from actions import check_accessibility

# Should detect ableist language
result = await check_accessibility("This is a blind spot in the design")
assert result == True

# Should detect missing alt text
result = await check_accessibility('<img src="flow.png">')
assert result == True

# Should pass clean text
result = await check_accessibility("The payment process has three steps: 1. Enter details 2. Confirm 3. Authenticate")
assert result == False
```
