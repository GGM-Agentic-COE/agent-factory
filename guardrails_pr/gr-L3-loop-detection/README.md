# gr-L3-loop-detection

**Layer:** L3
**Triggers on:** input (input rail, checked on every iteration)
**On fail:** Block
**Implementation:** LLM-driven (Colang) + Python-hybrid mode available

## What does it do?

Detects and kills runaway agent execution — infinite loops, stuck processes, and recursion spirals that would otherwise run forever, consuming tokens and time. An agent stuck in a retry loop could run indefinitely without this guardrail, blocking an entire workflow and driving costs up.

**What it catches:**
- Iteration count exceeding the configured maximum iterations (default: 50)
- Elapsed time exceeding the configured timeout in seconds (default: 300)
- Recursion depth exceeding the configured maximum recursion (default: 10)

**What it allows:**
- Execution state at or below all configured limits, including values exactly at the boundary (e.g. iteration 50, elapsed 300s, recursion depth 10)

## How It Works

```
EXECUTION STATE (checked on every iteration)
    │
    ▼
[LLM: Iteration / timeout / recursion limit exceeded?] ──── Yes? ──► BLOCK (kill)
    │ No
    ▼
[CONTINUE EXECUTION]
```

## File Structure

```
gr-L3-loop-detection/
├── gr-L3-loop-detection.co   # input rail definitions
├── config.yml                 # NeMo config + self-check prompt
└── README.md                  # This file
```

## Testing

### Prompt-Based Testing (LLM Judgement)

**Should pass (answer: "yes" = safe):**
- "Iteration: 5, elapsed: 30s, recursion: 2"
- "Iteration: 50, elapsed: 300s, recursion: 10" (boundary — still within limits)

**Should block (answer: "no" = kill):**
- "Iteration: 55, elapsed: 350s, recursion: 12"

### Test Cases Matrix

| # | Test | Expected | Category | Severity |
|---|------|----------|----------|----------|
| 1 | Iteration count exceeds max_iterations | BLOCK | loop_detection | High |
| 2 | Elapsed time exceeds timeout_seconds | BLOCK | loop_detection | High |
| 3 | Recursion depth exceeds max_recursion | BLOCK | loop_detection | High |
| 4 | Execution well within all configured limits | PASS | — | — |
| 5 | Execution exactly at boundary limits (iter 50, time 300s, depth 10) | PASS | — | — |

## Testing Note

NeMo's built-in `self_check_input` flow only populates `{{ user_input }}` — it has no access to custom fields like `iteration_count` or `elapsed_seconds` directly. To test or run this guardrail, encode the execution state as a single descriptive string (e.g. `"Iteration: 55, elapsed: 350s, recursion: 12"`) and pass that as the input, exactly as shown above.
