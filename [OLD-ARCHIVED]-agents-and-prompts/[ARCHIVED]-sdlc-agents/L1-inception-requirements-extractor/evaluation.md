# Evaluation — L1-inception-requirements-extractor

## Quality Gates

- [ ] IDs sequential per category (FR-01, FR-02... / NFR-01... / CON-01...)
- [ ] No duplicate IDs across categories
- [ ] Every FR and NFR has MoSCoW priority
- [ ] Categories 1-3 have citation (source_reference + source_location)
- [ ] All items across 10 categories have reasoning field
- [ ] No empty required fields (id, title/description per schema)
- [ ] Every requirement traces to input text (no hallucination)
- [ ] Confidence calibrated: explicit = 0.9+, inferred = 0.7-0.8
- [ ] Data requirements with personal attributes have pii=true
- [ ] Risk likelihood/impact: only High/Medium/Low
- [ ] PRD generated and uploaded to blob with valid URL
- [ ] PRD follows kb-L1-prd-document-template structure

## Scores (≥ threshold to pass)

| Dimension | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every requirement traces to input phrase |
| Hallucination | ≤ 0.10 | No invented capabilities/features |
| Consistency | 0.90 | Requirements don't contradict each other |
| Relevance | 0.85 | Requirements are actionable, not vague |
| Completeness | 0.85 | Input's capabilities adequately captured |
| Citation quality | 0.95 | Every cat 1-3 item cites exact input phrase |

## Reflection Checklist

- [ ] All stated capabilities → FR (split on "and")
- [ ] NFRs measurable (time, %, uptime)
- [ ] Constraints are decisions, not capabilities
- [ ] Gaps have impact + suggested question
- [ ] Dependencies only from explicit mentions
- [ ] Success metrics only from explicit targets; vague → GAP
- [ ] PII flagged correctly (name/email/phone/DOB/financial)
- [ ] No requirement contradicts another
- [ ] PRD sections populated from extracted requirements
- [ ] PRD uploaded to correct path
- [ ] execution_summary includes all 10 category counts
