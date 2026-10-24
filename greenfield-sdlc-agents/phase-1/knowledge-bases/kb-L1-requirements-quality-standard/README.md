# kb-L1-requirements-quality-standard

**Domain covered:** None specific — a cross-domain method for judging
whether a functional requirement is Unambiguous, Complete, Singular,
Feasible, Verifiable, Correct, and Traceable (ISO/IEC/IEEE 29148).

**Why it exists:** `L1-requirements-elicitor` is a generic L1 agent, reused
across every domain. Two of the seven characteristics it must satisfy —
Singular (no compound "and") and Traceable (every FR cites a vision.md
clause) — were already enforced directly in `requirements.template.md`
before this KB existed. The other five had no systematic method behind
them. Same role as `kb-L1-nfr-classification-taxonomy`: a small, reusable,
cross-domain method, not a domain fact set.

**What it deliberately does NOT do:** supply a feasibility or correctness
verdict for any specific requirement. Those two characteristics are
judgment calls that need domain/architecture knowledge this KB doesn't
have — it states the question to ask, never asserts the answer.

**Who uses it?**
- `L1-requirements-elicitor` — mechanical self-check only: vague-term scan
  (Unambiguous), compound-clause scan (Singular). Cheap, deterministic,
  no judgment required.
- `L1-requirements-elicitor-evaluator` — the full rubric as source of
  truth: Complete's coverage check, Verifiable's testability check,
  Consistent's contradiction check, and the Feasible/Correct *questions*
  (never verdicts this KB itself supplies).

**Sources:** ISO/IEC/IEEE 29148 (requirement quality characteristics);
RFC 2119 (shall/should/may obligation keywords).

**Update frequency:** Annually, or when the underlying standard revises.

**Quality bar:** Every characteristic must give either a mechanically
checkable rule (with a form, not a verdict) or an explicit judgment
question — a characteristic stated as vague advice ("write good
requirements") would fail this bar the same way a vague requirement itself
would.

**Owner:** Agentic-AI CoE

**Consumers:** `L1-requirements-elicitor`, `L1-requirements-elicitor-evaluator`
