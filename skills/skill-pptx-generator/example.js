/**
 * Example: Generate an Ascendion presentation
 * 
 * This demonstrates how to use the template to create a full deck.
 * Copy and modify this file for each new presentation.
 */

const path = require('path');
const {
  createPresentation,
  createTitleSlide,
  createSlide,
  createGridSlide,
  createClosingSlide,
  addKeyTakeaway,
  addBadge,
  addArrow,
  addDarkCard,
  addCard,
  addFlowBar,
  addBulletList,
  COLORS,
  FONTS,
  SIZES,
} = require('./template');

// ── Create presentation ──────────────────────────────────────
const prs = createPresentation();

// ── Slide 1: Title ───────────────────────────────────────────
createTitleSlide(
  prs,
  'Ascendion Presentation',  // Main title
  'Technical Methodology',                      // Subtitle
  'How [Customer] built an AI-augmented SDLC for their platform',  // Description
  '[Customer]  |  Ascendion'                          // Attribution
);

// ── Slide 2: The Problem (Grid Cards) ────────────────────────
createGridSlide(prs, 2, 'The Problem', 'Why AI-DLC was needed', [
  { heading: 'Inconsistent Requirements', body: 'Requirements captured across emails, chats, and multiple meetings with no single structured process' },
  { heading: 'Time-Poor Stakeholders', body: 'Business experts too valuable to spend days in requirements workshops — engineering builds from incomplete specs' },
  { heading: 'Late Infrastructure Decisions', body: 'Security, deployment, and infrastructure decisions surface after code is written — costly rework' },
  { heading: 'Manual Testing Burden', body: 'Testing largely manual, consuming weeks per release cycle with limited automation' },
  { heading: 'NFRs as Afterthoughts', body: 'Observability, performance, and security treated as bolt-on requirements discovered late' },
  { heading: 'Slow Incident Resolution', body: 'Major incidents take hours to resolve with multiple teams on bridge calls across data sources' },
  { heading: 'Key-Person Dependency', body: 'Expertise concentrated in key individuals — single points of failure across critical systems' },
  { heading: 'Inconsistent Maturity', body: 'Some teams cloud-native and automated, others still largely manual — inconsistent maturity' },
], { keyTakeaway: 'Result: Costly rework, slow time to revenue, and growing key-person risk' });

// ── Slide 3: Framework Overview ──────────────────────────────
const slide3 = createSlide(prs, 3, 'AI-DLC Framework Overview', 'Three phases, three continuous flows, one core principle');

// Three phase cards
const phaseW = 3.3;
const phases = [
  { num: '01', title: 'Inception Phase', desc: 'AI-augmented MOB sessions produce validated spec + clickable prototype before code is written', color: COLORS.accentBlue },
  { num: '02', title: 'Construction Phase', desc: 'Engineers orchestrate AI agents to generate production-ready code against enterprise standards', color: COLORS.green },
  { num: '03', title: 'Operations Phase', desc: 'Automated deployment with AI-assisted incident detection, triage, and remediation', color: COLORS.coral },
];

phases.forEach((phase, i) => {
  const x = SIZES.margin + i * (phaseW + 0.15);
  const y = 1.3;
  addDarkCard(slide3, x, y, phaseW, 2.2, phase.title, phase.desc, { accentColor: phase.color });
  addBadge(slide3, x + 0.15, y + 0.15, phase.num, { color: phase.color });

  if (i < 2) {
    addArrow(slide3, x + phaseW + 0.02, y + 0.9);
  }
});

// Flow bars
addFlowBar(slide3, 3.8, 'AI Steering Knowledge Feed', { accentColor: COLORS.accentBlue });
addFlowBar(slide3, 4.4, 'Architecture Blueprint Flow', { accentColor: COLORS.bodyDark });
addFlowBar(slide3, 5.0, 'Security & Engineering Standards Flow', { accentColor: COLORS.coral });

addKeyTakeaway(slide3, 'Core Principle:  AI augments, humans decide');

// ── Slide 4: Phase 1 Detail ─────────────────────────────────
const slide4 = createSlide(prs, 4, 'Phase 1: Inception', 'The MOB Elaboration Process');

// Left section - description box
addCard(slide4, 0.5, 1.15, 5.3, 1.1, 'What is a MOB Session?',
  'A structured 30–60 minute collaborative requirements capture session where business, product, and engineering collaborate. The conversation is transcribed and fed to Kiro.'
);

// Right section - CAST Framework
slide4.addText('The CAST Framework', {
  x: 6.1, y: 1.15, w: 5.3, h: 0.35,
  fontSize: 14, fontFace: FONTS.heading,
  color: COLORS.headingDark, bold: true
});

const castItems = [
  { letter: 'C', label: 'Context', desc: 'What does the system already know?', color: COLORS.accentBlue },
  { letter: 'A', label: 'Action', desc: 'What is the exact trigger?', color: COLORS.green },
  { letter: 'S', label: 'State', desc: 'What has changed after success?', color: COLORS.coral },
  { letter: 'T', label: 'Transition', desc: 'Where does the user go next?', color: COLORS.bodyDark },
];

castItems.forEach((item, i) => {
  const y = 1.7 + i * 0.7;
  // Badge
  slide4.addShape('ellipse', {
    x: 6.1, y, w: 0.45, h: 0.45,
    fill: { color: item.color },
    line: { type: 'none' }
  });
  slide4.addText(item.letter, {
    x: 6.1, y, w: 0.45, h: 0.45,
    fontSize: 18, fontFace: FONTS.heading,
    color: COLORS.white, bold: true,
    align: 'center', valign: 'middle'
  });
  // Label + description
  slide4.addText(item.label, {
    x: 6.7, y, w: 4.5, h: 0.25,
    fontSize: 12, fontFace: FONTS.heading,
    color: COLORS.headingDark, bold: true
  });
  slide4.addText(item.desc, {
    x: 6.7, y: y + 0.25, w: 4.5, h: 0.25,
    fontSize: 10, fontFace: FONTS.body,
    color: COLORS.bodyDark
  });
});

addKeyTakeaway(slide4, 'Ground Rules:  "If you are not talking, you are challenging"  |  Flag what you don\'t know', { fillColor: COLORS.accentBlue });

// ── Slide 5: Closing ─────────────────────────────────────────
createClosingSlide(
  prs, 5,
  'Human-AI Boundary',
  'Clear delineation: AI augments and accelerates, humans own every decision',
  'The AI cannot override a steering file constraint  •  No agent executes without human validation  •  Existing process is always the fallback'
);

// ── Save ─────────────────────────────────────────────────────
const outputPath = path.join(WORKSPACE_DIR, 'artifacts', 'example-output.pptx');
prs.writeFile({ fileName: outputPath })
  .then(() => console.log(`✅ Presentation saved: ${outputPath}`))
  .catch(err => console.error('Error:', err));

