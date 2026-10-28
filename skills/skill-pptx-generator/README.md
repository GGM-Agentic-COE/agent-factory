# PPTX Generator

A reusable skill for generating professional PowerPoint presentations in the provided visual design system.

## 📁 File Structure

```
skill-pptx-generator/
├── SKILL.md          → Main skill definition (design system + instructions)
├── steering.md       → Immutable design guardrails (place in .kiro/steering/)
├── template.js       → Reusable pptxgenjs helper library
├── example.js        → Working example that generates a 5-slide deck
└── README.md         → This file
```

## 🚀 Installation in Kiro

### Option 1: As a Skill
1. Copy `SKILL.md` to your workspace `.kiro/skills/pptx-methodology/SKILL.md`
2. Copy `template.js` to your project root or a shared utils folder
3. The skill will be available when Kiro detects presentation generation tasks

### Option 2: As a Power (recommended for team-wide use)
1. Create a new Power in your workspace:
   ```
   .kiro/powers/pptx-methodology/
   ├── SKILL.md
   ├── steering.md
   └── template.js
   ```
2. Add to your `powers.json` or configure keyword activation (e.g., "generate deck", "create presentation", "AI-DLC slides")

### Option 3: Steering File Only
For lightweight enforcement without the full skill:
1. Copy `steering.md` to `.kiro/steering/pptx-design-system.md`
2. Kiro will enforce the design rules whenever generating PPTX content

## 🎨 Design System Summary

| Element | Value |
|---------|-------|
| Format | 16:9 Widescreen (13.33" × 7.5") |
| Heading Font | Trebuchet MS |
| Body Font | Calibri |
| Dark Background | `#0D1B2A` (odd slides) |
| Light Background | `#E0E1DD` (even slides) |
| Primary Accent | `#4DA8DA` |
| Green Accent | `#81B29A` |
| Coral Accent | `#E07A5F` |

## 🔧 Usage

```javascript
const { createPresentation, createTitleSlide, createGridSlide, createClosingSlide } = require('./template');

const prs = createPresentation();

createTitleSlide(prs, 'My Title', 'Subtitle', 'Description', 'Company | AWS');

createGridSlide(prs, 2, 'Challenges', 'Why we need this', [
  { heading: 'Problem 1', body: 'Description of the problem' },
  { heading: 'Problem 2', body: 'Description of the problem' },
], { keyTakeaway: 'Summary statement' });

createClosingSlide(prs, 3, 'Key Principle', 'Supporting text', 'Bottom bar statement');

prs.writeFile({ fileName: 'output.pptx' });
```

## 📐 Available Layout Helpers

| Function | Purpose |
|----------|---------|
| `createPresentation()` | Initialize a new deck with correct dimensions |
| `createTitleSlide()` | Slide 1 with decorative elements |
| `createSlide()` | Auto-picks dark/light based on slide number |
| `createDarkSlide()` | Force dark background |
| `createLightSlide()` | Force light background |
| `createGridSlide()` | Card grid (up to 4×2) |
| `createClosingSlide()` | Centered principle/closing |
| `addCard()` | White card with accent bar |
| `addDarkCard()` | Dark card for dark slides |
| `addBadge()` | Numbered circle badge |
| `addArrow()` | Flow arrow connector |
| `addFlowBar()` | Horizontal flow bar |
| `addBulletList()` | Formatted bullet points |
| `addKeyTakeaway()` | Bottom summary bar |
| `addTopBar()` | Top accent bar |
| `addPageNumber()` | Page number |

## ✅ Quality Checklist

Before sharing any generated deck:
- [ ] Background alternation is correct (odd=dark, even=light)
- [ ] Top accent bar on every slide
- [ ] Page numbers bottom-right
- [ ] Headings in Trebuchet MS, body in Calibri
- [ ] All colours from the approved palette
- [ ] No drop shadows, gradients, or clip art
- [ ] Maximum 8 cards per grid
- [ ] Closing slide has principle statement

