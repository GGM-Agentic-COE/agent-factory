# Early Childhood Education Domain Knowledge Base
### kb-L2-early-childhood-education-domain v1.0.0
### Domain knowledge for Singapore early childhood education (preschool/childcare). All agents creating epics, stories, or designs for NFC products MUST ground their decisions in this KB.

---

## EC1: Childcare Centre Lifecycle

### Parent Journey

1. **Discovery** — Parent searches for childcare centre (ECDA portal, word of mouth, NFC website). Centre availability, location, and programme type are key decision factors.
2. **Enquiry** — Parent contacts centre or submits online enquiry. Centre responds with availability, fees, and programme information.
3. **Waitlist** — If no vacancy, parent joins waitlist. ECDA vacancy management rules apply — centres must update vacancy portal within 3 working days.
4. **Registration** — Parent completes enrolment form (child details, parent details, emergency contacts, medical history, dietary requirements). Consent captured for subsidies, photo/video, outings.
5. **Subsidy Application** — Centre submits subsidy application to ECDA on parent's behalf. Basic subsidy (up to $600/month) and Additional subsidy (means-tested) processed via ECDA systems.
6. **Enrolment Confirmation** — Centre confirms placement. First month's fees invoiced. Registration deposit collected.
7. **Onboarding** — Child starts settling-in period (typically 1-2 weeks). Parent orientation conducted. Digital check-in/out system activated.
8. **Active Enrolment** — Daily attendance, learning activities, developmental observations, parent communications via app. Monthly fee billing and payment collection.
9. **Transition / Graduation** — Child transitions between levels (PG → N1 → N2 → K1 → K2) or graduates to primary school. Portfolio and developmental reports transferred.
10. **Withdrawal** — Parent submits notice (typically 1 month). Final billing reconciled. Subsidy cessation notified to ECDA.

### Centre Operations Journey

1. **Licensing** — Centre obtains ECDA licence (Early Childhood Development Centres Act 2017). Annual renewal with compliance checks.
2. **Capacity Planning** — Staff-to-child ratios mandated by ECDA (1:5 for infant, 1:8 for PG, 1:15 for N1-K2 with aide). Vacancy management.
3. **Staff Management** — Teacher qualifications (DPT/ACEY minimum), First Aid certification, mandatory training hours. Staff-to-child ratio compliance.
4. **Programme Delivery** — Curriculum aligned to ECDA Nurturing Early Learners (NEL) framework. Learning areas: Aesthetics & Creative Expression, Discovery of the World, Language & Literacy, Motor Skills, Numeracy, Social & Emotional Development.
5. **Daily Operations** — Attendance tracking, meal management, nap schedules, activity planning, incident reporting.
6. **Financial Management** — Fee collection (GIRO, PayNow), subsidy reconciliation with ECDA, financial reporting.
7. **Regulatory Compliance** — ECDA audits, SPARK certification (quality rating), fire safety, health & hygiene, child protection.
8. **Parent Engagement** — Portfolio updates, learning observations, parent-teacher conferences, event management.

---

## EC2: Key Entities & Data Model

### Child Profile
| Field | Type | Validation | Regulatory Basis |
|---|---|---|---|
| Full name | String | As per birth certificate | ECDA registration |
| Date of birth | Date | Age determines level placement | ECDA age-level rules |
| NRIC/FIN/Birth Cert No | String | Unique identifier | ECDA subsidy processing |
| Gender | Enum: Male, Female | Required | ECDA reporting |
| Race | Enum | Required for programme planning | MOE reporting |
| Citizenship | Enum: SC, PR, Foreigner | Determines subsidy eligibility | ECDA subsidy rules |
| Medical conditions | Array | Allergies, conditions, medication | Duty of care |
| Dietary requirements | Array | Halal, vegetarian, allergies | Meal planning |
| Immunisation records | Array | Required vaccines per age | HPB schedule |
| Emergency contacts | Array (min 2) | Name, relationship, phone | Safety requirement |

### Parent/Guardian Profile
| Field | Type | Validation |
|---|---|---|
| Full name | String | As per NRIC |
| NRIC/FIN | String | For subsidy processing |
| Relationship to child | Enum: Father, Mother, Guardian | Required |
| Contact: mobile | String | Singapore format (+65) |
| Contact: email | String | For portal access |
| Household income | Currency (SGD) | For Additional Subsidy means-testing |
| Marital status | Enum | Affects subsidy calculation |
| Working status | Boolean | Required for working mother subsidy |

### Centre Profile
| Field | Type | Notes |
|---|---|---|
| Centre name | String | Licensed name |
| ECDA licence number | String | Unique identifier |
| Operator type | Enum: Anchor, Partner, Premium | Determines fee caps and subsidies |
| Address | String | Physical location |
| Capacity | Object | By level (Infant, PG, N1, N2, K1, K2) |
| Current enrolment | Integer | Real-time from attendance system |
| Vacancy | Integer per level | Must report to ECDA within 3 days |
| Operating hours | String | Typically 7AM–7PM |
| Principal | Staff reference | Licensed person-in-charge |

---

## EC3: Regulatory Framework

### ECDA (Early Childhood Development Agency)

| Regulation | Requirement | Impact on System |
|---|---|---|
| ECDCA 2017 | Licensing of all childcare centres | Centre must maintain licence data, renewal tracking |
| Child Care Centres Regulations | Staff-to-child ratios | System must track ratios in real-time per classroom |
| Subsidy framework | Basic + Additional + KiFAS subsidies | Automated subsidy calculation and ECDA submission |
| SPARK certification | Quality rating system (4 levels) | Portfolio evidence collection, developmental milestones |
| Vacancy reporting | Update within 3 working days | Automated vacancy sync to ECDA portal |
| Attendance reporting | Monthly submission to ECDA | Digital attendance records with check-in/out times |
| Staff qualifications | Minimum DPT/ACEY, teacher-to-trained ratio | Staff credential management and expiry tracking |

### Fee & Subsidy Structure

| Subsidy Type | Eligibility | Amount | System Requirement |
|---|---|---|---|
| Basic Subsidy | Singapore Citizen, working mothers | Up to $600/month (anchor operator) | Auto-apply on enrolment |
| Additional Subsidy | Income-based means test | $40–$467/month depending on income tier | Income verification, recalculation on change |
| KiFAS (Kindergarten Fee Assistance) | Kindergarten level only | Variable | Separate application process |
| CFAC (Child Development Account) | CDA holders | Direct debit from CDA | Payment integration |

### Key Compliance Rules
- **Staff ratios**: Must be maintained at ALL times (not just on average). System must alert if ratio breached.
- **Attendance**: Children not collected by 7PM must follow late-pickup protocol. Emergency contacts notified.
- **Medication**: Written parent consent required before administering. Logged with timestamp and witness.
- **Incident reporting**: Serious incidents reported to ECDA within 24 hours. All incidents logged with details and parent notification.
- **Child protection**: Signs of abuse reported to MSF (Ministry of Social and Family Development). Staff trained on recognition.

---

## EC4: Fee Management

### Fee Structure (NFC — Anchor Operator)
| Level | Age | Monthly Fee (Before Subsidy) | With Max Subsidy |
|---|---|---|---|
| Infant Care | 2–17 months | ~$1,340 | ~$740 |
| Playgroup (PG) | 18 months–2 years | ~$978 | ~$378 |
| Nursery 1 (N1) | 3 years | ~$778 | ~$178 |
| Nursery 2 (N2) | 4 years | ~$778 | ~$178 |
| Kindergarten 1 (K1) | 5 years | ~$720 | ~$120 |
| Kindergarten 2 (K2) | 6 years | ~$720 | ~$120 |

### Payment Methods
- GIRO (monthly auto-deduction)
- PayNow (QR or UEN)
- NETS
- Child Development Account (CDA) — government-matched savings
- Cash/Cheque (declining, centres moving to cashless)

### Billing Cycle
- Fees invoiced 1st of month
- Payment due by 7th of month
- Late payment: reminder at day 10, warning at day 20, suspension notice at day 30
- Subsidy credited: ECDA processes monthly, offset against invoice

---

## EC5: Attendance & Safety

### Check-In/Out System
| Event | Data Captured | Validation |
|---|---|---|
| Check-in | Time, authorised person ID (parent/guardian), temperature | Person must be in authorised list |
| Check-out | Time, authorised person ID, signature/biometric | Same validation as check-in |
| Late pickup | Trigger at closing time | Auto-notify emergency contacts |
| Absent | No check-in by 10AM | System marks absent, notifies parent for confirmation |
| Unauthorised pickup | Person not in system | BLOCK — do not release child, alert principal |

### Safety Protocols (System Requirements)
- Real-time headcount per classroom (matched against check-in records)
- Staff-to-child ratio monitoring with alerts on breach
- Incident report form (digital) with photo attachment, parent notification, ECDA submission
- Emergency evacuation checklist (digital) with roll-call verification
- Medical information accessible by staff during emergencies (allergies, conditions)

---

## EC6: Learning & Development

### NEL Framework (Nurturing Early Learners)
| Learning Area | Description | System Support |
|---|---|---|
| Aesthetics & Creative Expression | Art, music, dance, drama | Activity templates, portfolio capture |
| Discovery of the World | Science, nature, social studies | Observation recording |
| Language & Literacy | English + Mother Tongue | Milestone tracking, parent communication |
| Motor Skills Development | Gross and fine motor | Developmental checklists |
| Numeracy | Numbers, patterns, spatial awareness | Progress tracking |
| Social & Emotional Development | Self-awareness, relationships, resilience | Behaviour observations |

### Developmental Milestones
- Tracked per child against age-appropriate benchmarks
- Recorded as observations (text + photo/video evidence)
- Compiled into child portfolio (shared with parents termly)
- Used for SPARK certification evidence
- Transition reports generated on level-up or graduation

### Teacher Observations
| Field | Type | Purpose |
|---|---|---|
| Child | Reference | Who was observed |
| Date | DateTime | When |
| Learning area | Enum (NEL areas) | What domain |
| Observation | Text + media | What was observed |
| Milestone reference | Optional | Which milestone this evidences |
| Teacher | Reference | Who observed |
| Shared with parent | Boolean | Parent visibility |

---

## EC7: Integration Landscape

### External Systems
| System | Integration | Purpose |
|---|---|---|
| ECDA Portal | API / file submission | Subsidy applications, attendance reporting, vacancy updates |
| PayNow/NETS | Payment gateway | Fee collection |
| CDA (CPFB) | Payment integration | Child Development Account deductions |
| Firebase Cloud Messaging | Push service | Mobile notifications to parents |
| Freshchat | Live chat | External parent support channel (SN2-related queries) |
| Twilio / SendGrid | SMS / Email | Transactional notifications |
| Google Workspace | Directory / Auth | Staff identity and collaboration |
| ServiceNow | ITSM | Support ticket management |
| HubSpot | CRM | Marketing and parent engagement |
| SuccessFactors | HR | Staff lifecycle management |

### Internal Systems (NFC)
| System | Role | Technology |
|---|---|---|
| SkoolNet 2 (SN2) | Core preschool management | Go backend, React/React Native frontend |
| Middle Stage | CRM integration middleware | Custom |
| UiPath RPA | Process automation (25 use cases) | Attended + Developer bots |
| BigQuery | Analytics and reporting | Data warehouse |

---

## EC8: User Personas

| Persona | Count | Primary Needs | Pain Points |
|---|---|---|---|
| Parents | ~44,000 | Registration, payments, child progress, communication | App UX, payment reminders, understanding subsidies |
| Guardians | ~29,000 | Check-in/out, attendance | Simple and fast process |
| Teachers | ~5,000 (40% Chinese-speaking) | Classroom management, observations, attendance | Manual processes, language barriers |
| Principals | ~180 | Centre admin, enrolment, events, compliance | Data accuracy, reporting burden |
| HQ Staff | ~200 | Strategy, financials, analytics, compliance | Fragmented data, manual reporting |

---

## EC9: Business Rules

### Enrolment Rules
- Child age determines level: Infant (<18m), PG (18m-3y), N1 (3y), N2 (4y), K1 (5y), K2 (6y)
- Age calculated as at 1 January of enrolment year
- Sibling priority for waitlist
- Maximum capacity per centre enforced (never exceed licensed capacity)
- Transfer between NFC centres: enrolment preserved, subsidy notified to ECDA

### Fee Calculation Rules
- Base fee per level (set by NFC, within ECDA fee cap for anchor operators)
- Minus Basic Subsidy (auto-applied if eligible)
- Minus Additional Subsidy (means-tested, recalculated annually)
- Plus optional enrichment programme fees
- Plus ad-hoc charges (field trips, uniform, etc.)
- Pro-rated for mid-month starts/withdrawals

### Notification Rules
| Event | Channel | Timing | Recipient |
|---|---|---|---|
| Fee invoice generated | App + Email | 1st of month | Parent |
| Payment overdue | Push + SMS | Day 10 | Parent |
| Child absent (unconfirmed) | Push | 10AM | Parent |
| Incident report filed | Push + Email | Immediately | Parent |
| Learning observation shared | Push | When teacher publishes | Parent |
| Subsidy status change | Email | When processed | Parent |
| Vacancy opened | System | Within 3 days | ECDA portal |

---

## EC10: Terminology

| Term | Definition |
|---|---|
| ECDA | Early Childhood Development Agency — regulator |
| NEL | Nurturing Early Learners — national curriculum framework |
| SPARK | Singapore Preschool Accreditation Framework — quality rating |
| MFS | MyFirstSkool — NFC's anchor operator brand (160+ centres) |
| LSH | Little Skool House — NFC's partner operator brand (14 centres) |
| CME | ChangeMakers Explorer — NFC's premium brand (6 centres) |
| SEED | SEED Institute — NFC's enrichment arm (afterschool care, enrichment, outdoor camps) |
| SN2 | SkoolNet 2 — NFC's core preschool management system |
| PG | Playgroup — age 18 months to 3 years |
| N1/N2 | Nursery 1/2 — ages 3-4 |
| K1/K2 | Kindergarten 1/2 — ages 5-6 |
| KiFAS | Kindergarten Fee Assistance Scheme |
| CDA | Child Development Account — government savings account for children |
| DPT | Diploma in Pre-school Teaching |
| ACEY | Advanced Certificate in Early Years |
| GIRO | General Interbank Recurring Order — auto-payment |
| MSF | Ministry of Social and Family Development |
| HPB | Health Promotion Board |
