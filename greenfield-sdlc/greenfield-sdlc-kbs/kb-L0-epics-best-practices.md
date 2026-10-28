Schreiber Foods Inc. Jira Epic Best Practices and Standard Operating Procedure

Document Owner: Agile Program Management Office (PMO) / Enterprise Solutions Architecture
 Applies To: All Product, Engineering, QA, and IT Delivery Teams
 Status: Approved, Mandatory Standard
 Version: 1.2
 Related Source Document: Standard Product Requirements Document (PRD) Template

1. Purpose of a Schreiber Foods Epic

A Jira Epic is a strategic container, not a technical execution document. Its primary function is to communicate two questions clearly to any reader, including plant leadership, product stakeholders, delivery teams, and new engineers:

What business or manufacturing capability are we delivering?
Why does it matter to Schreiber Foods in terms of cost, compliance, throughput, customer service, operational performance, or food safety?

An Epic must not prescribe detailed implementation. It may identify high-level operating or solution constraints when they materially affect scope, feasibility, compliance, food safety, or business value.

Detailed implementation belongs downstream in Features, Stories, Tasks, Sub-tasks, technical design documents, and Confluence engineering pages.

Guiding Principle: If a reader cannot understand the Epic’s business intent, value, and boundaries through a brief scan of its Summary and User Value Statement, the Epic has failed its purpose.

An Epic overloaded with implementation detail creates four organizational risks:

It becomes stale when implementation details change, reducing trust in Jira as a source of truth.
It obscures the business justification relied upon by Plant Operations, Finance, Compliance, Quality, and other stakeholders.
It duplicates information that should remain in the PRD, Confluence, or engineering documentation, creating conflicting versions of the truth.
It slows backlog grooming, refinement, planning, and portfolio reviews because Epics are no longer scannable.
2. Input Filtering Rules: What to Extract From the PRD

When converting an approved PRD into a Jira Epic, the author or AI-assisted drafting agent must extract only the information permitted below and maintain the required level of abstraction.

2.1 Executive Summary to Epic Summary and User Value Statement
Compress the Executive Summary into:
A single-sentence Epic Summary.
A three-to-five-sentence User Value Statement.
The Epic title must be derived from the core business capability, not copied directly from the Executive Summary.
The User Value Statement must identify:
Who benefits.
What capability changes.
Why the change matters.
What business, manufacturing, operational, compliance, customer, or food-safety outcome is expected.
Remove narrative background, project history, stakeholder quotations, meeting commentary, and implementation detail.
Retain only the distilled business intent and expected value.
When quantitative targets are available in the approved PRD, include them without alteration.
Do not invent targets, benefits, deadlines, or performance improvements that are not supported by the PRD.
2.2 Requirements to Macro Feature Pillars
Do not transcribe individual requirements into the Epic.
Consolidate requirements into three to six macro feature pillars representing major capability groupings.
Each pillar should generally be expressible in five to eight words.
A macro feature pillar may later be decomposed into one or more downstream Features, Stories, or linked Epics, according to the configured Jira hierarchy.
Pillars must describe capability areas rather than implementation tasks.
If a requirement cannot be shortened to a capability-level phrase without losing its meaning, defer it to the Feature or Story layer.
Do not create one pillar for every PRD requirement.
Preserve traceability to the source PRD without reproducing its detailed content.

Examples of appropriately scoped macro feature pillars:

Automated Lot Genealogy Capture
Batch Record Synchronization
Production Exception Monitoring
Quality Hold Management
Traceability Reporting and Evidence
2.3 Out of Scope to Strict Project Boundaries
Carry the PRD’s out-of-scope intent into the Epic as a concise bullet list.
Preserve the original boundary without changing its meaning.
Place the content under an Out of Scope subsection.
Limit the list to three to six bullets.
When the PRD contains a longer list, consolidate related exclusions into clear categories.
Do not introduce new exclusions that are not supported by the approved PRD.
Where appropriate, identify the separate initiative, Epic, or future phase in which excluded work is expected to be addressed.

The Out of Scope section is a boundary control intended to prevent scope creep. It must not become a discussion log or implementation backlog.

2.4 Constraints to High-Level Operating Constraints

Extract only constraints that materially limit or shape the Epic at a strategic level.

Appropriate constraints include:

Enterprise platform or module boundaries.
Plant infrastructure limitations.
Production calendar restrictions.
Supply chain timing restrictions.
Regulatory requirements.
Corporate policy boundaries.
Data residency or retention obligations.
Approved technology or hosting boundaries when they materially affect feasibility or scope.
Required deployment windows or blackout periods.
Operational continuity requirements.

Exclude implementation-specific constraints such as:

API rate limits.
Library or package versions.
Field-level schema restrictions.
Coding conventions.
Component-level design decisions.
Detailed interface behavior.
Test-case implementation details.

These belong in child work items or technical documentation.

2.5 PRD-to-Epic Cardinality Rule

Determine the number of Epics produced from a PRD before drafting Epic content.

Step 1: Evaluate the Executive Summary

If the Executive Summary describes one cohesive business capability serving one primary business outcome, default to one Epic.

Step 2: Consolidate Requirements

Roll the requirements into three to six macro feature pillars.

If the pillars fit within one cohesive capability and collectively support the same business outcome, confirm one Epic.

Step 3: Evaluate an Excessive Number of Pillars

If more than six pillars remain after reasonable consolidation:

Keep one Epic if all pillars support the same business outcome and stakeholder group.
Flag the Epic as potentially large during backlog grooming rather than splitting it artificially.
Split into multiple Epics when the pillars support genuinely distinct business outcomes, initiatives, or stakeholder groups.
Each resulting Epic must provide independently understandable business value.
Step 4: Identify Bundled, Unrelated Initiatives

If the Executive Summary combines unrelated initiatives, treat this as a PRD-scoping concern.

The Product Owner should request that the PRD be separated into independently governed PRDs.

If delivery must proceed from the existing PRD:

Create one Epic for each distinct initiative or outcome.
Apply every filtering, exclusion, acceptance, risk, and quality rule in this SOP independently to each Epic.
Maintain traceability from every resulting Epic to the same source PRD.
Record the scoping concern concisely in the User Value Statement or Summary context.
Recommend that future revisions be separated into appropriately scoped PRDs.
Step 5: Prohibit Requirement-Level Epics

Never create one Epic for each individual requirement.

Epic count must reflect the number of distinct business initiatives or independently valuable outcomes, not:

The number of requirements.
The number of PRD sections.
The number of macro feature pillars.
The number of systems involved.
The number of delivery teams.

Cardinality Test: Could this cluster of requirements ship independently and provide meaningful value to a distinct stakeholder group if the remainder of the PRD were never delivered? If yes for two different clusters, create separate Epics. If no, retain them within one Epic.

2.6 Acceptance Criteria to Epic-Level Outcomes

Every Epic must contain three to seven high-level acceptance criteria demonstrating that the intended business capability and required outcomes have been delivered.

Epic acceptance criteria must:

Describe measurable business, manufacturing, operational, quality, food-safety, governance, or compliance outcomes.
Focus on what must be true for the Epic to be accepted.
Remain independent of specific implementation choices.
Be objectively verifiable.
Align with the Epic Summary, User Value Statement, scope, and macro feature pillars.
Identify required evidence when evidence is necessary to demonstrate completion.
Reflect applicable obligations without reproducing detailed control implementation.
Be traceable to the source PRD.

Epic acceptance criteria must not contain:

Field-level validation.
Screen or button behavior.
API response formats.
Component-level logic.
Detailed workflow steps.
Detailed test cases.
Coding or design instructions.
Feature-level or Story-level scenarios.

Altitude Test: If an acceptance criterion describes how a component behaves rather than what business or operational outcome must be achieved, it is too detailed for the Epic.

Recommended Acceptance Criteria Pattern
Given [business, operational, or compliance context],

When [the Epic capability is available or used],

Then [a measurable outcome is achieved]

AND [required evidence is available, where applicable].

Appropriate Epic Acceptance Criteria
Authorized users can complete the intended business process across the approved operating scope.
Required traceability information can be retrieved within the target timeframe defined in the approved PRD.
Applicable quality, food-safety, security, and compliance reviews have been completed.
Required evidence is generated and retained according to the applicable policy.
Defined success measures can be captured through approved reporting or monitoring mechanisms.
Inappropriate Epic Acceptance Criteria
A specific field accepts a defined format.
A button displays a particular confirmation message.
An API returns a particular response code.
A component performs a specific validation sequence.
A user interface follows a detailed navigation flow.

These criteria belong in downstream Features, Stories, test cases, or technical documentation.

3. Exclusion Rules: What Is Forbidden in the Epic

The following PRD content must not be copied or described in detail within the Epic. It is either too granular, too volatile, or intended for another audience.

PRD Section	Why It Is Excluded From the Epic	Correct DestinationTraceability Matrix	Requirement-to-validation mapping is execution-level content that changes throughout delivery and reduces Epic scanability.	Linked Confluence page or approved test-management tool; detailed references belong in downstream work items.
Compound Requirement Split	This is a delivery decomposition artifact used to produce downstream work items.	Downstream Features, Stories, Tasks, or approved decomposition artifacts.
Detailed Open Questions	Detailed delivery questions are volatile and create confusion when placed in a strategic work item.	Linked decision log or open-items register; delivery-level questions remain with child work items.
Detailed Assumptions	Delivery assumptions can change quickly and should not be duplicated in the Epic.	Source PRD, decision log, or relevant child work items.
Glossary	Definitions are reference material rather than strategic Epic content.	Linked organization-wide or project-specific glossary.
Detailed Technical Design	Component behavior, architecture, schemas, and implementation decisions are outside the Epic’s strategic purpose.	Confluence engineering pages, architecture records, or technical design documents.
Detailed Test Scenarios	Test steps and expected component behavior operate below Epic altitude.	Test-management system, Feature or Story acceptance criteria, or QA documentation.
3.1 Material Open Decisions

An unresolved decision affecting any of the following must not be hidden:

Epic scope.
Business outcome.
Regulatory or food-safety viability.
Funding or sponsorship.
Operational feasibility.
Production continuity.
Approval readiness.

Such a decision must be resolved before Epic approval or represented through a clearly labeled link to the governing decision log.

3.2 Material Assumptions

A material assumption affecting business value, scope, feasibility, food safety, compliance, or approval may be represented as:

A concise operating constraint.
A dependency.
A critical risk.
A referenced decision.

Do not copy the detailed assumptions section from the PRD.

Rule of Thumb: If information primarily helps an engineer build or a QA analyst test, it does not belong in the Epic. If it helps stakeholders understand intent, value, boundaries, acceptance, or material risk, it may be included in condensed form.

4. Critical Business, Regulatory, and Food-Safety Risks

The PRD Risks section must be actively filtered. Do not copy or summarize the complete risk register into the Epic.

Only material risks meeting the criteria below belong in the Epic.

4.1 Risks That Must Be Included

Include a risk when it could:

Prevent delivery of the Epic’s intended business outcome.
Halt or materially disrupt production.
Trigger or increase the likelihood of a product recall.
Create a regulatory finding or missed compliance deadline.
Cause an audit failure.
Jeopardize certification status.
Create a material food-safety exposure.
Prevent required traceability or recall execution.
Create an operational continuity failure that invalidates the Epic’s intended value.

Relevant risk categories may include:

FDA requirements or compliance deadlines.
FSMA traceability obligations.
SQF audit or certification risks.
HACCP plan impacts.
Allergen control risks.
Recall-readiness gaps.
USDA or applicable state regulatory exposure.
Plant shutdown exposure.
Material production continuity risks.
Critical dependencies that could prevent the business capability from operating.

Each qualifying risk must be written as one concise bullet containing:

Risk category.
Clear risk statement.
Severity where supported by the source.
Relevant deadline where explicitly stated.
Business, regulatory, food-safety, or operational consequence.

Example:

- ⚠️ Regulatory: Delayed lot genealogy capability may affect readiness for an applicable traceability deadline identified in the approved PRD.


Do not invent a severity, deadline, probability, or impact that is not present in the approved source.

4.2 Risks That Must Be Excluded

Do not include routine delivery risks such as:

General defects or engineering bugs.
Routine developer training needs.
Routine end-user training needs.
Non-material vendor service concerns.
Day-to-day staffing issues.
Sprint-level scheduling issues.
Minor environmental readiness issues.
Ordinary delivery impediments.
Risks that do not materially affect the business outcome, production continuity, food safety, compliance, auditability, or certification.

These risks belong in:

The linked risk register.
Delivery plans.
Feature or Story blockers.
Team impediment logs.
Relevant operational or engineering documentation.

Risk Filtering Test: If the risk materializes, could it materially prevent the intended business outcome, expose Schreiber Foods to a regulatory finding, cause an audit failure, trigger a recall, jeopardize certification, or halt operations? If not, exclude it from the Epic.

5. The Link, Do Not Copy Rule

Jira Epics must remain lightweight, scannable, and durable.

Content that is inherently detailed, visual, matrix-based, or frequently updated must be stored in the appropriate source system and linked from the Epic.

5.1 Content That Must Be Externalized
Full PRDs.
Detailed impact assessments.
Plant dependency graphs.
Network diagrams.
Full compliance matrices.
Traceability matrices.
Requirement decomposition spreadsheets.
Architecture diagrams.
Data-flow diagrams.
Technical design documents.
Detailed test plans.
Decision logs.
Complete risk registers.
Detailed implementation plans.
5.2 Required Linking Format

Use clean, descriptive labels rather than unlabeled URLs.

📎 Impact Assessment: URL

📎 Compliance Matrix: URL

📎 Detailed Requirements: URL

📎 Decision Log: URL


Every Epic must include a Reference Links subsection at the bottom of its description.

Reference links must:

Use a meaningful label.
Point to the authoritative source.
Avoid duplicating linked content inside the Epic.
Remain accessible to the intended audience.
Be checked during backlog grooming.

Broken, inaccessible, or missing required links are Epic quality defects and must be corrected before approval.

6. Writing and Formatting Standards
6.1 Epic Naming Convention

Epic titles must be:

Three to five words where practical.
Written in Title Case.
Focused on the business or manufacturing capability.
Understandable without technical translation.
Free of ticket-number-style prefixes unless required by Jira configuration.
Free of conversational history or meeting references.
Free of unnecessary platform names unless the platform itself materially defines the business capability.

Recommended pattern:

[Capability] + [Business Object] + [Optional Qualifier]

Good Examples
Automated Lot Genealogy Capture
Batch Record Synchronization
Plant Allergen Control Upgrade
Production Exception Monitoring
Quality Hold Management
Avoid
Epic for the New Traceability Work
Update Stuff in SAP
Build Traceability Microservice
Q3 Plant Operations Work
Create New Database Tables

When a specific platform is an approved constraint but does not define the business value, record it under Key Constraints rather than in the title.

6.2 Mandatory Epic Description Structure

Every Epic description must follow this structure:

## Summary
[One sentence describing the business or manufacturing capability]

## User Value Statement
[Three to five concise sentences describing who benefits, what changes, why it matters, and the expected outcome]

## Macro Feature Pillars
- Pillar 1
- Pillar 2
- Pillar 3

## Epic Acceptance Criteria
- Measurable business outcome 1
- Measurable operational or quality outcome 2
- Applicable governance, food-safety, or compliance outcome 3

## Out of Scope
- Excluded item 1
- Excluded item 2

## Key Constraints
- Strategic constraint 1
- Strategic constraint 2

## Critical Business, Regulatory, and Food-Safety Risks
- ⚠️ Material risk 1, including severity or deadline only when supported by the approved source

## Reference Links
📎 URL
📎 URL


If no qualifying risk exists, use:

## Critical Business, Regulatory, and Food-Safety Risks
- No qualifying material risks identified in the approved PRD.


Do not omit the section.

6.3 General Formatting Rules
Use concise bullets wherever possible.
Use bold text sparingly.
Use bold text only for material labels, risk severity flags, or required emphasis.
Avoid paragraphs longer than two sentences.
Do not use nested bullets deeper than one level.
Do not embed detailed tables, diagrams, matrices, or images.
Do not reproduce technical design content.
Do not copy detailed requirements from the PRD.
Do not use unexplained acronyms.
Preserve terminology from the approved PRD where it affects traceability.
Do not introduce claims, targets, deadlines, names, systems, or obligations unsupported by the approved source.
Review every Epic against this SOP before marking it Ready for Refinement.
7. Epic Definition of Done

An Epic may be marked complete only when the conditions applicable to its approved scope have been satisfied.

The Epic Definition of Done must be outcome-focused and must not replace the detailed Definition of Done used by Features, Stories, engineering teams, or QA teams.

7.1 Standard Epic Completion Conditions
All required downstream Features or Stories have been completed or formally dispositioned.
The business capability described in the Epic Summary is available within the approved scope.
Epic acceptance criteria have been satisfied.
Required business, quality, security, food-safety, regulatory, and operational reviews have been completed.
Required approvals and sign-offs have been obtained.
Critical defects or findings preventing acceptance have been resolved or formally accepted through an authorized process.
Required evidence has been generated and retained.
Operational ownership, monitoring, support, and escalation paths are established where applicable.
Required documentation and reference links are current.
Success measures can be captured using approved reporting or monitoring mechanisms.
Any remaining follow-up work has an identified owner and an approved tracking location.
7.2 Definition of Done Principles
Completion must be objectively verifiable.
Evidence must support required validations.
Quality, compliance, and food-safety obligations must not be deferred without authorized disposition.
Epic completion must reflect delivered capability, not merely completed development activity.
Deployment alone does not prove Epic acceptance.
Acceptance must be evaluated against the approved scope and Epic acceptance criteria.
8. Quick-Reference Quality and Compliance Checklist

Before publishing or approving an Epic, confirm:

Business Purpose and Naming
 The title is concise, capability-focused, and understandable to business stakeholders.
 The title avoids unnecessary technical implementation language.
 The Summary clearly states the business or manufacturing capability.
 The User Value Statement identifies who benefits, what changes, and why it matters.
 Any quantitative claim is supported by the approved PRD.
Cardinality and Decomposition
 Epic count reflects distinct business initiatives or outcomes.
 The PRD was not split into one Epic per requirement.
 Requirements are consolidated into three to six macro feature pillars where practical.
 Macro feature pillars represent capabilities rather than implementation tasks.
 Any PRD-scoping concern has been identified appropriately.
Acceptance Criteria
 The Epic contains three to seven high-level acceptance criteria.
 Acceptance criteria are measurable and objectively verifiable.
 Acceptance criteria focus on outcomes rather than implementation.
 Acceptance criteria align with the Summary, value, scope, and pillars.
 Detailed Feature, Story, interface, validation, and test behavior is excluded.
 Required evidence is identified where applicable.
Scope and Constraints
 Out-of-scope boundaries are stated clearly.
 Out-of-scope content preserves the intent of the approved PRD.
 Only high-level operating or solution constraints are listed.
 Technical implementation constraints have been deferred to downstream artifacts.
Risks
 Only material business, regulatory, food-safety, audit, certification, recall, production continuity, or plant shutdown risks are included.
 Routine delivery risks are excluded.
 Severity and deadlines are included only when supported by the source.
 No risk details were invented or inferred.
Excluded Content
 No detailed Traceability Matrix content appears in the Epic.
 No Compound Requirement Split content appears in the Epic.
 No detailed Open Questions section appears in the Epic.
 No detailed Assumptions section appears in the Epic.
 No Glossary content appears in the Epic.
 No detailed technical design or test scenarios appear in the Epic.
 Material unresolved decisions are resolved or linked through an approved decision log.
Links and Formatting
 Detailed matrices, diagrams, plans, and assessments are linked rather than pasted.
 The Reference Links subsection is present.
 Required links are labeled, accessible, and current.
 The mandatory Epic description structure is followed.
 The Epic is concise and scannable.
 No paragraph exceeds two sentences where a bullet can communicate the same information.
 No nested bullets exceed one level.
 The Epic has been reviewed against this SOP before being marked Ready for Refinement.
9. Minimum Epic Template
# [Epic Title]

## Summary
[One sentence describing the business or manufacturing capability]

## User Value Statement
[Three to five concise sentences describing who benefits, what changes, why it matters, and the expected outcome]

## Macro Feature Pillars
- [Capability pillar 1]
- [Capability pillar 2]
- [Capability pillar 3]

## Epic Acceptance Criteria
- [Measurable business outcome]
- [Measurable operational or quality outcome]
- [Applicable governance, food-safety, or compliance outcome]

## Out of Scope
- [Excluded item 1]
- [Excluded item 2]

## Key Constraints
- [Strategic constraint 1]
- [Strategic constraint 2]

## Critical Business, Regulatory, and Food-Safety Risks
- [Material qualifying risk or statement that no qualifying risks were identified]

## Reference Links
📎 URL
📎 URL




Main corrections made: added Epic-level acceptance criteria and Definition of Done, softened absolute “no how” and “one screen” language, preserved material assumptions and decisions through controlled linking, expanded risks to include outcome-threatening operational risks, clarified the Epic hierarchy, and removed solution-oriented naming where it did not represent business capability.
