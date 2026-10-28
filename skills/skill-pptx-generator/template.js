template.js
javascript
/**
 * PPTX Template
 * 
 * This is the reusable template for generating presentations in the
 * Ascendion design system. Import and use the helper functions
 * to build consistent slides.
 * 
 * Usage:
 *   const { createPresentation, COLORS, helpers } = require('./template');
 *   const prs = createPresentation();
 *   // ... add slides using helpers ...
 *   prs.writeFile({ fileName: 'output.pptx' });
 */

const pptxgen = require('pptxgenjs');

// ═══════════════════════════════════════════════════════════════
// DESIGN TOKENS
// ═══════════════════════════════════════════════════════════════

const COLORS = {
  darkBg: '0D1B2A',        // Odd slide backgrounds
  lightBg: 'E0E1DD',       // Even slide backgrounds
  accentBlue: '4DA8DA',    // Top bar, accents, highlights
  darkCard: '1B2838',      // Card fill on dark slides
  mutedText: '778DA9',     // Body text on dark backgrounds
  bodyDark: '415A77',      // Body text on light backgrounds
  headingLight: 'FFFFFF',  // Headings on dark backgrounds
  headingDark: '0D1B2A',   // Headings on light backgrounds
  green: '81B29A',         // Positive accents, numbered badges
  coral: 'E07A5F',         // Warnings, important callouts
  white: 'FFFFFF',         // Card fills on light slides
};

const FONTS = {
  heading: 'Calibri',
  body: 'Calibri',
};

const SIZES = {
  slideW: 13.33,
  slideH: 7.5,
  topBarH: 0.06,
  margin: 0.5,
  cardGap: 0.15,
  cardPad: 0.15,
};

// ═══════════════════════════════════════════════════════════════
// PRESENTATION FACTORY
// ═══════════════════════════════════════════════════════════════

function createPresentation() {
  const prs = new pptxgen();
  prs.defineLayout({ name: 'PPTX', width: SIZES.slideW, height: SIZES.slideH });
  prs.layout = 'AIDLC_WIDE';
  prs.author = 'Ascendion';
  prs.subject = 'Generated with PPTX Skill';
  return prs;
}

// ═══════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════

/**
 * Add the accent bar at the top of every slide
 */
function addTopBar(slide) {
  slide.addShape('rect', {
    x: 0, y: 0, w: SIZES.slideW, h: SIZES.topBarH,
    fill: { color: COLORS.accentBlue },
    line: { type: 'none' }
  });
}

/**
 * Add page number in bottom-right corner
 */
function addPageNumber(slide, num) {
  slide.addText(String(num), {
    x: 11.17, y: 6.25, w: 0.6, h: 0.3,
    fontSize: 10, fontFace: FONTS.body,
    color: COLORS.mutedText, align: 'center'
  });
}

/**
 * Add a bottom key-takeaway bar with text
 */
function addKeyTakeaway(slide, text, options = {}) {
  const { fillColor = COLORS.darkCard, y = 5.75, h = 0.5 } = options;
  slide.addShape('rect', {
    x: SIZES.margin, y, w: SIZES.slideW - (SIZES.margin * 2), h,
    fill: { color: fillColor },
    line: { type: 'none' },
    rectRadius: 0.02
  });
  slide.addText(text, {
    x: SIZES.margin + 0.15, y, w: SIZES.slideW - (SIZES.margin * 2) - 0.3, h,
    fontSize: 11, fontFace: FONTS.body,
    color: COLORS.white, valign: 'middle'
  });
}

/**
 * Create a dark slide (for odd-numbered slides)
 * @returns {object} slide object
 */
function createDarkSlide(prs, title, subtitle, slideNum) {
  const slide = prs.addSlide();
  slide.background = { fill: COLORS.darkBg };
  addTopBar(slide);

  slide.addText(title, {
    x: SIZES.margin, y: 0.25, w: 8, h: 0.6,
    fontSize: 30, fontFace: FONTS.heading,
    color: COLORS.headingLight, bold: false
  });

  if (subtitle) {
    slide.addText(subtitle, {
      x: SIZES.margin, y: 0.8, w: 8, h: 0.35,
      fontSize: 12, fontFace: FONTS.body,
      color: COLORS.mutedText
    });
  }

  if (slideNum) addPageNumber(slide, slideNum);
  return slide;
}

/**
 * Create a light slide (for even-numbered slides)
 * @returns {object} slide object
 */
function createLightSlide(prs, title, subtitle, slideNum) {
  const slide = prs.addSlide();
  slide.background = { fill: COLORS.lightBg };
  addTopBar(slide);

  slide.addText(title, {
    x: SIZES.margin, y: 0.25, w: 8, h: 0.55,
    fontSize: 28, fontFace: FONTS.heading,
    color: COLORS.headingDark, bold: false
  });

  if (subtitle) {
    slide.addText(subtitle, {
      x: SIZES.margin, y: 0.72, w: 8, h: 0.3,
      fontSize: 13, fontFace: FONTS.body,
      color: COLORS.accentBlue
    });
  }

  if (slideNum) addPageNumber(slide, slideNum);
  return slide;
}

/**
 * Automatically create the right slide type based on number
 */
function createSlide(prs, slideNum, title, subtitle) {
  if (slideNum % 2 === 1) {
    return createDarkSlide(prs, title, subtitle, slideNum);
  } else {
    return createLightSlide(prs, title, subtitle, slideNum);
  }
}

/**
 * Add a white card with left accent bar (best on light backgrounds)
 */
function addCard(slide, x, y, w, h, heading, body, options = {}) {
  const { accentColor = COLORS.accentBlue } = options;

  // Card background
  slide.addShape('rect', {
    x, y, w, h,
    fill: { color: COLORS.white },
    line: { type: 'none' },
    rectRadius: 0.02
  });

  // Left accent bar
  slide.addShape('rect', {
    x, y: y + 0.05, w: 0.04, h: h - 0.1,
    fill: { color: accentColor },
    line: { type: 'none' }
  });

  // Heading
  slide.addText(heading, {
    x: x + SIZES.cardPad, y: y + 0.05, w: w - (SIZES.cardPad * 2), h: 0.35,
    fontSize: 12, fontFace: FONTS.heading,
    color: COLORS.headingDark, bold: true
  });

  // Body
  slide.addText(body, {
    x: x + SIZES.cardPad, y: y + 0.4, w: w - (SIZES.cardPad * 2), h: h - 0.5,
    fontSize: 10.5, fontFace: FONTS.body,
    color: COLORS.bodyDark, valign: 'top'
  });
}

/**
 * Add a dark card (best on dark backgrounds)
 */
function addDarkCard(slide, x, y, w, h, heading, body, options = {}) {
  const { accentColor = COLORS.accentBlue } = options;

  slide.addShape('rect', {
    x, y, w, h,
    fill: { color: COLORS.darkCard },
    line: { type: 'none' },
    rectRadius: 0.02
  });

  // Left accent bar
  slide.addShape('rect', {
    x, y: y + 0.05, w: 0.04, h: h - 0.1,
    fill: { color: accentColor },
    line: { type: 'none' }
  });

  // Heading
  slide.addText(heading, {
    x: x + SIZES.cardPad, y: y + 0.1, w: w - (SIZES.cardPad * 2), h: 0.4,
    fontSize: 13, fontFace: FONTS.heading,
    color: COLORS.headingLight, bold: false
  });

  // Body
  slide.addText(body, {
    x: x + SIZES.cardPad, y: y + 0.5, w: w - (SIZES.cardPad * 2), h: h - 0.6,
    fontSize: 11.5, fontFace: FONTS.body,
    color: COLORS.mutedText, valign: 'top'
  });
}

/**
 * Add a numbered badge/circle
 */
function addBadge(slide, x, y, number, options = {}) {
  const { color = COLORS.accentBlue, size = 0.45, fontSize = 14 } = options;

  slide.addShape('ellipse', {
    x, y, w: size, h: size,
    fill: { color },
    line: { type: 'none' }
  });

  slide.addText(String(number).padStart(2, '0'), {
    x, y, w: size, h: size,
    fontSize, fontFace: FONTS.heading,
    color: COLORS.white, bold: true,
    align: 'center', valign: 'middle'
  });
}

/**
 * Add a flow arrow connector between elements
 */
function addArrow(slide, x, y) {
  slide.addText('▶', {
    x, y, w: 0.3, h: 0.3,
    fontSize: 16, fontFace: FONTS.body,
    color: COLORS.accentBlue, align: 'center', valign: 'middle'
  });
}

/**
 * Add a horizontal flow bar (used for continuous flows)
 */
function addFlowBar(slide, y, text, options = {}) {
  const { accentColor = COLORS.accentBlue } = options;
  const x = SIZES.margin;
  const w = SIZES.slideW - (SIZES.margin * 2);
  const h = 0.5;

  slide.addShape('rect', {
    x, y, w, h,
    fill: { color: COLORS.darkCard },
    line: { type: 'none' },
    rectRadius: 0.02
  });

  // Left dot accent
  slide.addShape('rect', {
    x, y: y + 0.07, w: 0.04, h: h - 0.14,
    fill: { color: accentColor },
    line: { type: 'none' }
  });

  slide.addText(text, {
    x: x + 0.2, y, w: w - 0.8, h,
    fontSize: 12, fontFace: FONTS.body,
    color: COLORS.white, valign: 'middle'
  });

  // Right arrow
  slide.addText('→', {
    x: x + w - 0.6, y, w: 0.5, h,
    fontSize: 16, fontFace: FONTS.body,
    color: accentColor, align: 'center', valign: 'middle'
  });
}

/**
 * Add a bullet list to a slide
 */
function addBulletList(slide, x, y, w, bullets, options = {}) {
  const { fontSize = 11, color = COLORS.mutedText, lineSpacing = 22 } = options;

  const textItems = bullets.map(bullet => ({
    text: `▸  ${bullet}`,
    options: {
      fontSize, fontFace: FONTS.body, color,
      bullet: false, breakLine: true,
      lineSpacingMultiple: 1.3
    }
  }));

  slide.addText(textItems, {
    x, y, w, h: bullets.length * (fontSize * lineSpacing / 72),
    valign: 'top'
  });
}

/**
 * Create a title slide (always slide 1 — dark)
 */
function createTitleSlide(prs, mainTitle, subtitle, description) {
  const slide = prs.addSlide();
  slide.background = { fill: COLORS.darkBg };
  addTopBar(slide);

  // Left accent bar
  slide.addShape('rect', {
    x: 0.5, y: 1.37, w: 0.04, h: 3.2,
    fill: { color: COLORS.accentBlue },
    line: { type: 'none' }
  });

  // Main title
  slide.addText(mainTitle, {
    x: 0.65, y: 1.4, w: 7.8, h: 1.1,
    fontSize: 36, fontFace: FONTS.heading,
    color: COLORS.headingLight
  });

  // Subtitle
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.65, y: 2.55, w: 7.8, h: 0.55,
      fontSize: 22, fontFace: FONTS.body,
      color: COLORS.accentBlue
    });
  }

  // Description
  if (description) {
    slide.addText(description, {
      x: 0.65, y: 3.15, w: 7.8, h: 0.45,
      fontSize: 14, fontFace: FONTS.body,
      color: COLORS.mutedText
    });
  }

  // Decorative shapes (right side)
  slide.addShape('rect', {
    x: 9.0, y: 1.6, w: 2.0, h: 1.1,
    fill: { color: COLORS.darkCard },
    line: { type: 'none' }, rectRadius: 0.02
  });
  slide.addShape('rect', {
    x: 9.3, y: 2.85, w: 2.0, h: 1.1,
    fill: { color: COLORS.bodyDark },
    line: { type: 'none' }, rectRadius: 0.02
  });
  slide.addShape('rect', {
    x: 8.85, y: 4.1, w: 2.0, h: 0.9,
    fill: { color: COLORS.accentBlue },
    line: { type: 'none' }, rectRadius: 0.02
  });

  addPageNumber(slide, 1);
  return slide;
}

/**
 * Create a grid of cards (for problem/challenge slides)
 * @param {Array} cards - Array of {heading, body} objects (max 8)
 * @param {number} cols - Number of columns (3 or 4)
 */
function createGridSlide(prs, slideNum, title, subtitle, cards, options = {}) {
  const { cols = 4, keyTakeaway = '' } = options;
  const slide = createSlide(prs, slideNum, title, subtitle);

  const startY = 1.3;
  const cardW = (SIZES.slideW - (SIZES.margin * 2) - (SIZES.cardGap * (cols - 1))) / cols;
  const cardH = 1.6;
  const rows = Math.ceil(cards.length / cols);

  cards.forEach((card, i) => {
    const col = i % cols;
    const row = Math.floor(i / cols);
    const x = SIZES.margin + (col * (cardW + SIZES.cardGap));
    const y = startY + (row * (cardH + SIZES.cardGap));

    if (slideNum % 2 === 1) {
      addDarkCard(slide, x, y, cardW, cardH, card.heading, card.body);
    } else {
      addCard(slide, x, y, cardW, cardH, card.heading, card.body);
    }
  });

  if (keyTakeaway) {
    addKeyTakeaway(slide, keyTakeaway);
  }

  return slide;
}

/**
 * Create a closing/principle slide
 */
function createClosingSlide(prs, slideNum, title, subtitle, principle) {
  const slide = prs.addSlide();
  slide.background = { fill: COLORS.darkBg };
  addTopBar(slide);

  slide.addText(title, {
    x: 1.5, y: 2.5, w: SIZES.slideW - 3, h: 1.0,
    fontSize: 36, fontFace: FONTS.heading,
    color: COLORS.headingLight, align: 'center'
  });

  if (subtitle) {
    slide.addText(subtitle, {
      x: 1.5, y: 3.5, w: SIZES.slideW - 3, h: 0.6,
      fontSize: 14, fontFace: FONTS.body,
      color: COLORS.mutedText, align: 'center'
    });
  }

  if (principle) {
    addKeyTakeaway(slide, principle, { fillColor: COLORS.darkCard });
  }

  addPageNumber(slide, slideNum);
  return slide;
}

// ═══════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════

module.exports = {
  COLORS,
  FONTS,
  SIZES,
  createPresentation,
  createTitleSlide,
  createSlide,
  createDarkSlide,
  createLightSlide,
  createGridSlide,
  createClosingSlide,
  addTopBar,
  addPageNumber,
  addKeyTakeaway,
  addCard,
  addDarkCard,
  addBadge,
  addArrow,
  addFlowBar,
  addBulletList,
};
