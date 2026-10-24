# W03-Orchestrator: UI Code Generator Workflow
# ═══════════════════════════════════════════════════════════════
# Framework-agnostic UI code generator.
# Tech stack discovered from codebase/KBs or defaults to React + TypeScript + Vite.
# ═══════════════════════════════════════════════════════════════

```yaml
workflow:
  name: ui-code-generator
  version: "1.0"
  trigger: manual (developer provides epic/stories + optional codebase path)

pipeline:
  steps:
    - id: step1
      prompt: W03-step1-ui-tech-discovery.md
      input: design docs + existing codebase (optional) + knowledge bases
      output_to: step2
      gate: tech_stack must be resolved (discovered or defaulted)
      on_fail: default to React + TypeScript + Vite and proceed

    - id: step2
      prompt: W03-step2-ui-code-generator.md
      input: step1.tech_stack + stories + existing codebase + framework KB
      output_to: github
      gate: all tests pass, accessibility audit passes WCAG 2.1 AA, no regression
      on_fail: RETRY once, then flag for developer review

  execution_order: step1 → step2

knowledge_bases_required:
  core:
    - kb-L0-agent-quality-standards        # B1-B10 grounding, citation, PII
    - kb-L0-ui-coding-standards            # Framework-agnostic UI patterns (components, a11y, responsive, i18n)
    - kb-L1-enterprise-architecture        # EA1-EA20 (tech stack, patterns, security, data)

  framework_specific:
    react:
      - kb-L1-react-standards              # Hooks, functional components, Context/Redux, React Router, testing
    angular:
      - kb-L1-angular-standards            # Modules, services, RxJS, Angular Router, testing
    vue:
      - kb-L1-vue-standards                # Composition API, Pinia, Vue Router, testing
    nextjs:
      - kb-L1-nextjs-standards             # App Router, SSR/SSG, server components, testing
    compose:
      - kb-L1-compose-standards            # Jetpack Compose, Material3, ViewModel, testing
    swiftui:
      - kb-L1-swiftui-standards            # SwiftUI views, MVVM, Combine, testing

  domain:
    - kb-L2-payments-domain                # PD1-PD25 (lending domain rules)
    - kb-L3-application-baseline           # Existing app state (brownfield)

data_contract:
  step1_output:
    required: [tech_stack, design_system_analysis, component_inventory]
    tech_stack:
      framework: "react | angular | vue | nextjs | compose | swiftui"
      language: "typescript | javascript | kotlin | swift"
      build_tool: "vite | webpack | angular-cli | vue-cli | gradle | xcode"
      test_framework: "vitest | jest | karma | vue-test-utils | compose-test | xctest"
      state_management: "context | redux | zustand | ngrx | pinia | viewmodel | observable"
      styling: "css-modules | tailwind | styled-components | scss | material | swiftui-native"
      component_library: "custom | mui | ant-design | shadcn | angular-material | vuetify"
    design_system_analysis:
      required: [tokens, components, patterns]
    component_inventory:
      required: [existing_components, routes, stores]
    passed_to_step2: [tech_stack, mode, design_system_analysis, component_inventory, framework_kb_id]

  step2_output:
    required: [files_created, files_modified, tests_created, citations_summary, design_decisions]

evaluation_thresholds:
  gate:
    faithfulness: {threshold: 0.93}       # UI must match story ACs
    hallucination: {threshold: 0.07}      # No invented components or routes
    correctness: {threshold: 0.92}        # Code must build and render correctly
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
    action: default to React 18 + TypeScript 5 + Vite and proceed to Step 2
    reasoning: "Discovery failure should not block UI code generation"

  step2_build_failure:
    action: retry once with error context, then flag for developer
    detail: "If generated code doesn't compile/lint, retry with the error message as additional context"

  step2_test_failure:
    action: retry once with failure details, then push with warning
    detail: "New test failures may indicate incorrect test expectations. Retry with error context."

  step2_accessibility_failure:
    action: STOP — fix violations before push
    detail: "WCAG 2.1 AA compliance is mandatory. Fix all critical/serious axe-core violations before pushing."
    notification: "⚠️ Accessibility violations: {N} WCAG 2.1 AA failures. Code NOT pushed until resolved."

  step2_existing_tests_fail:
    action: STOP — do NOT push to GitHub
    detail: "If existing tests break after changes, revert changes to modified files, report failures, suggest fix."
    notification: "⚠️ Regression detected: {N} existing tests failed after changes. Code NOT pushed."

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
  UI CODE GENERATOR — EXECUTION SUMMARY
  ═══════════════════════════════════════════════════════════
  Epic: {id} — {title}
  Mode: {greenfield | brownfield}

  STEP 1: UI TECH DISCOVERY
    Framework: {framework} {version}
    Language: {language} {version}
    Build Tool: {build_tool}
    Source: {codebase | documentation | default}
    Design System: {design_system_name | custom | none}
    Existing Components: {N}
    Existing Routes: {N}

  STEP 2: UI CODE GENERATION
    Files created: {N}
    Files modified: {N}
    Files unchanged: {N}
    Tests created: {unit} unit + {integration} integration + {accessibility} a11y
    Test results: {passed}/{total} passed
    Accessibility: WCAG 2.1 AA {pass/fail}
    Regression: {existing tests still pass: yes/no}

  GITHUB
    Branch: feature/{epic-id}-ui-implementation
    PR: #{N} → {repo}
    Files committed: {N}

  ═══════════════════════════════════════════════════════════
