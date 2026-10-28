# W02-Orchestrator: API Code Generator Workflow
# ═══════════════════════════════════════════════════════════════
# Language/framework agnostic API code generator.
# Tech stack discovered from docs/KBs or defaults to Java/Spring Boot.
# ═══════════════════════════════════════════════════════════════

```yaml
workflow:
  name: api-code-generator
  version: "1.0"
  trigger: manual (developer provides epic/stories + optional codebase path)

pipeline:
  steps:
    - id: step1
      prompt: W02-step1-tech-discovery.md
      input: architecture docs + existing codebase (optional) + knowledge bases
      output_to: step2
      gate: tech_stack must be resolved (discovered or defaulted)
      on_fail: default to Java/Spring Boot and proceed

    - id: step2
      prompt: W02-step2-code-generator.md
      input: step1.tech_stack + stories + existing codebase + language KB
      output_to: github
      gate: all tests pass, no regression in existing code
      on_fail: RETRY once, then flag for developer review

  execution_order: step1 → step2

knowledge_bases_required:
  # Always attached (framework-agnostic)
  core:
    - kb-L0-agent-quality-standards        # B1-B10 grounding, citation, PII
    - kb-L0-api-coding-standards           # NEW — language-agnostic API patterns (REST, CQRS, error handling, testing)
    - kb-L1-enterprise-architecture        # EA1-EA20 (tech stack, patterns, security, data)
    - kb-L1-openapi-standards              # OA1-OA17 (API spec compliance)
    - kb-L1-microservices-architecture     # MS1-MS17 (service boundaries, communication, resilience, data, observability)

  # Attached based on Step 1 discovery (one set per language)
  language_specific:
    java_springboot:
      - kb-L1-java-springboot-standards    # Project structure, Spring patterns, Bean config, JPA, testing (JUnit/Mockito)
    csharp_dotnet:
      - kb-L1-csharp-dotnet-standards      # Clean Architecture, MediatR, EF Core, FluentValidation, xUnit
    nodejs_express:
      - kb-L1-nodejs-express-standards     # Express patterns, middleware, Prisma/Sequelize, Jest
    python_fastapi:
      - kb-L1-python-fastapi-standards     # FastAPI patterns, Pydantic, SQLAlchemy, pytest
    kotlin_ktor:
      - kb-L1-kotlin-ktor-standards        # Ktor patterns, Exposed ORM, kotest

  # Attached based on domain
  domain:
    - kb-L2-payments-domain                # PD1-PD25 (lending domain rules)
    - kb-L3-application-baseline           # Existing app state (brownfield)

data_contract:
  step1_output:
    required: [tech_stack, mode, project_structure, existing_code_analysis]
    tech_stack:
      language: "java | csharp | typescript | python | kotlin"
      framework: "springboot | dotnet | express | fastapi | ktor"
      build_tool: "maven | gradle | dotnet | npm | pip"
      test_framework: "junit | xunit | jest | pytest | kotest"
      orm: "jpa | efcore | prisma | sqlalchemy | exposed"
      db: "postgresql | sqlserver | mysql | mongodb"
    passed_to_step2: [tech_stack, mode, project_structure, existing_code_analysis, language_kb_id]

  step2_output:
    required: [files_created, files_modified, tests_created, test_results, github_storage]

evaluation_thresholds:
  gate:
    faithfulness: {threshold: 0.93}       # Code must match story ACs
    hallucination: {threshold: 0.07}      # No invented endpoints or logic
    correctness: {threshold: 0.92}        # Code must compile/run correctly
    consistency: {threshold: 0.93}        # Code consistent with existing codebase
  recommended:
    answer_correctness: {threshold: 0.90} # Technical accuracy
    context_recall: {threshold: 0.88}     # Must recall KB patterns
```

# ═══════════════════════════════════════════════════════════════
# ERROR HANDLING
# ═══════════════════════════════════════════════════════════════

error_handling:
  step1_failure:
    action: default to Java/Spring Boot and proceed to Step 2
    reasoning: "Discovery failure should not block code generation"

  step2_build_failure:
    action: retry once with error context, then flag for developer
    detail: "If generated code doesn't compile/lint, retry with the error message as additional context"

  step2_existing_tests_fail:
    action: STOP — do NOT push to GitHub
    detail: "If existing tests break after changes, the code has regression. Revert changes to modified files, report which tests failed and why, suggest fix."
    notification: "⚠️ Regression detected: {N} existing tests failed after changes. Code NOT pushed."

  step2_new_tests_fail:
    action: retry once with failure details, then push with warning
    detail: "New test failures may indicate incorrect test expectations. Retry with error context. If still failing, push code but flag tests as needing review."

  github_push_failure:
    action: retry once (likely auth/conflict), then save files locally
    fallback: "Write all generated files to local output directory with README"

  idempotency:
    branch_exists: force-push (overwrite previous attempt)
    pr_exists: update PR body and files, don't create duplicate

# ═══════════════════════════════════════════════════════════════
# EXECUTION SUMMARY
# ═══════════════════════════════════════════════════════════════

summary_template: |
  ═══════════════════════════════════════════════════════════
  API CODE GENERATOR — EXECUTION SUMMARY
  ═══════════════════════════════════════════════════════════
  Epic: {id} — {title}
  Mode: {greenfield | brownfield}

  STEP 1: TECH DISCOVERY
    Language: {language} {version}
    Framework: {framework} {version}
    Source: {codebase | documentation | default}
    Existing endpoints: {N}
    Existing tests: {N}

  STEP 2: CODE GENERATION
    Files created: {N}
    Files modified: {N}
    Files unchanged: {N}
    Tests created: {unit} unit + {contract} contract + {integration} integration
    Test results: {passed}/{total} passed
    Regression: {existing tests still pass: yes/no}

  GITHUB
    Branch: feature/{epic-id}-api-implementation
    PR: #{N} → {repo}
    Files committed: {N}

  ═══════════════════════════════════════════════════════════
