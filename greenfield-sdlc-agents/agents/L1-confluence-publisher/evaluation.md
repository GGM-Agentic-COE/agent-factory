# Evaluation — L1-confluence-publisher

## Quality Gates
- [ ] published_page.action correctly reflects created vs. updated
- [ ] No page was overwritten without update: true explicitly passed
- [ ] Published content matches the source artifact — no summarization, reformatting, or editing
- [ ] A missing artifact or empty content correctly returns INSUFFICIENT_CONTEXT rather than publishing something blank

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 1.00 | Published content is byte-for-byte the given artifact — no tolerance for drift, this agent transforms nothing |
| Consistency | 0.95 | action (created/updated) matches what tool-L1-confluence-create-page actually reported |
| Reasoning quality | 0.7 | execution_summary clearly states what was published and where |

Hallucination and citation-completeness scores are N/A for this agent — it
generates no content to hallucinate or cite.

## Reflection Checklist
- [ ] No silent overwrite occurred
- [ ] No content alteration occurred
- [ ] Tool invocation outcome is accurately reported, not assumed successful

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
