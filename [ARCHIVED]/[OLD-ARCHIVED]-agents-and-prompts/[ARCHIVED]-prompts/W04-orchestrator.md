# W04-Orchestrator: Mobile Code Generator Workflow
# ═══════════════════════════════════════════════════════════════
# Platform-agnostic mobile code generator.
# Tech stack discovered from codebase/KBs or defaults to Kotlin + Jetpack Compose.
# ═══════════════════════════════════════════════════════════════

```yaml
workflow:
  name: mobile-code-generator
  version: "1.0"
  trigger: manual (developer provides epic/stories + optional codebase path)

pipeline:
  steps:
    - id: step1
      prompt: W04-step1-mobile-tech-discovery.md
      input: design docs + existing codebase (optional) + knowledge bases
      output_to: step2
      gate: tech_stack must be resolved (discovered or defaulted)
      on_fail: default to Kotlin + Jetpack Compose and proceed

    - id: step2
      prompt: W04-step2-mobile-code-generator.md
      input: step1.tech_stack + stories + existing codebase + framework KB
      output_to: github
      gate: all tests pass, accessibility audit passes WCAG 2.1 AA, no regression
      on_fail: RETRY once, then flag for developer review

  execution_order: step1 → step2

knowledge_bases_required:
  core:
    - kb-L0-agent-quality-standards        # B1-B10 grounding, citation, PII
    - kb-L0-mobile-coding-standards        # Platform-agnostic mobile patterns (MVVM, a11y, offline, navigation)
    - kb-L1-enterprise-architecture        # EA1-EA20 (tech stack, patterns, security, data)

  framework_specific:
    kotlin-compose:
      - kb-L1-kotlin-compose-standards     # Jetpack Compose, Material3, ViewModel, Hilt, Navigation Compose
      - kb-L1-kotlin-compose-scaffold      # KF1-KF15 (production scaffold for greenfield projects)
    swiftui:
      - kb-L1-swiftui-standards            # SwiftUI views, MVVM, Combine, NavigationStack, testing
    flutter:
      - kb-L1-flutter-standards            # Widgets, BLoC/Riverpod, GoRouter, testing
    react-native:
      - kb-L1-react-native-standards       # React Native components, React Navigation, Redux/Zustand, testing

  domain:
    - kb-L2-payments-domain                # PD1-PD25 (lending domain rules)
    - kb-L3-application-baseline           # Existing app state (brownfield)

data_contract:
  step1_output:
    required: [tech_stack, design_system_analysis, screen_inventory, navigation_graph]
    tech_stack:
      platform: "android | ios | cross-platform"
      language: "kotlin | swift | dart | typescript"
      framework: "compose | swiftui | flutter | react-native"
      build_tool: "gradle | xcode | flutter-cli | metro"
      test_framework: "junit5 | xctest | flutter-test | jest"
      di_framework: "hilt | koin | manual | provider | none"
      navigation: "navigation-compose | navigationstack | go-router | react-navigation"
      state_management: "stateflow | combine | bloc | riverpod | redux | zustand"
      networking: "retrofit | alamofire | dio | axios"
      local_storage: "room | coredata | hive | async-storage"
      design_system: "material3 | cupertino | custom | none"
    design_system_analysis:
      required: [tokens, components, patterns]
    screen_inventory:
      required: [existing_screens, screen_types]
    navigation_graph:
      required: [routes, nav_type, deep_links]
    passed_to_step2: [tech_stack, mode, design_system_analysis, screen_inventory, navigation_graph, framework_kb_id]

  step2_output:
    required: [files_created, files_modified, tests_created, citations_summary, design_decisions]

evaluation_thresholds:
  gate:
    faithfulness: {threshold: 0.93}       # UI must match story ACs
    hallucination: {threshold: 0.07}      # No invented screens or routes
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
    action: default to Kotlin 2.0 + Jetpack Compose + Hilt and proceed to Step 2
    reasoning: "Discovery failure should not block mobile code generation"

  step2_build_failure:
    action: retry once with error context, then flag for developer
    detail: "If generated code doesn't compile/lint, retry with the error message as additional context"

  step2_test_failure:
    action: retry once with failure details, then push with warning
    detail: "New test failures may indicate incorrect test expectations. Retry with error context."

  step2_accessibility_failure:
    action: STOP — fix violations before push
    detail: "WCAG 2.1 AA compliance is mandatory. Fix all TalkBack/VoiceOver failures before pushing."
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
  MOBILE CODE GENERATOR — EXECUTION SUMMARY
  ═══════════════════════════════════════════════════════════
  Epic: {id} — {title}
  Mode: {greenfield | brownfield}

  STEP 1: MOBILE TECH DISCOVERY
    Platform: {android | ios | cross-platform}
    Language: {language} {version}
    Framework: {framework} {version}
    Build Tool: {build_tool}
    Source: {codebase | documentation | default}
    Design System: {design_system_name | custom | none}
    Existing Screens: {N}
    Navigation Routes: {N}

  STEP 2: MOBILE CODE GENERATION
    Files created: {N}
    Files modified: {N}
    Files unchanged: {N}
    Tests created: {unit} unit + {ui} UI + {accessibility} a11y
    Test results: {passed}/{total} passed
    Accessibility: WCAG 2.1 AA {pass/fail}
    Regression: {existing tests still pass: yes/no}

  GITHUB
    Branch: feature/{epic-id}-mobile-implementation
    PR: #{N} → {repo}
    Files committed: {N}

  ═══════════════════════════════════════════════════════════
