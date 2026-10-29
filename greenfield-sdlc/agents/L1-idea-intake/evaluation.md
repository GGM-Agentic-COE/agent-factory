# Evaluation — L1-vision-idea-intake

## Quality Gates
- [ ] All required fields present: problem_statement, target_users (≥1), value_proposition, candidate_success_metrics, open_questions
- [ ] Every item's `traced_to` is an actual substring/paraphrase of the input, not fabricated
- [ ] Every `candidate_success_metrics[].status` is correctly "stated" (explicit in input) vs. "suggested" (inferred) — no mislabeling
- [ ] IDs sequential per category (TU-01, TU-02...; SM-01...; OQ-01...), no gaps or duplicates
- [ ] If input was insufficient, status is "failed" with items empty and execution_summary states INSUFFICIENT_CONTEXT — not a hallucinated partial brief

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every item traces to input via `traced_to` |
| Hallucination | ≤ 0.10 | No invented users, problems, or metrics |
| Consistency | 0.90 | Target users and value proposition don't contradict problem statement |
| Relevance | 0.85 | Output is usable as-is by market-analyzer/regulatory-checker/vision-generator |
| Reasoning quality | 0.80 | Every `reasoning` field explains the extraction/inference, not just restates it |
| Citation completeness | N/A | This agent grounds against input text, not a KB — `traced_to` substitutes for citation |

## Reflection Checklist
- [ ] No field left as placeholder or vague filler text
- [ ] Every "suggested" metric is phrased so a reader can't mistake it for stated fact
- [ ] Open questions list is non-empty unless the input was genuinely complete (rare)

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
