# Presentation Design Guardrails

## Purpose
This steering file enforces the Ascendion visual design system for all generated PowerPoint presentations. It acts as an immutable constraint — the AI MUST follow these rules without deviation.

## Immutable Design Rules

### 1. Color Usage — NO EXCEPTIONS
- Dark backgrounds MUST be `#0D1B2A` — never use black (#000000) or generic dark grey
- Light backgrounds MUST be `#E0E1DD` — never use pure white (#FFFFFF) as a slide background
- Accent blue MUST be `#4DA8DA` — never use generic blue (#0000FF or #2196F3)
- Body text on dark MUST be `#778DA9` — never use pure white for body text
- Body text on light MUST be `#415A77` — never use black for body text

### 2. Typography — NO EXCEPTIONS
- ALL headings MUST use Trebuchet MS — never Arial, Helvetica, or Calibri for headings
- ALL body text MUST use Calibri — never use Trebuchet MS for body paragraphs
- Title slides: 36pt maximum
- Content slides: 28-32pt for section headers
- Body: 10.5-14pt range only

### 3. Background Alternation — NO EXCEPTIONS
- Slide 1, 3, 5, 7, 9, 11, 13... → Dark (#0D1B2A)
- Slide 2, 4, 6, 8, 10, 12, 14... → Light (#E0E1DD)
- This pattern MUST NOT be broken for any reason

### 4. Structural Elements — REQUIRED ON EVERY SLIDE
- Top accent bar (full-width, #4DA8DA, 0.06" height)
- Page number (bottom-right, Calibri 10pt, #778DA9)

### 5. Content Density Rules
- Maximum 8 cards per grid layout
- Maximum 5 bullet points per section
- Maximum 3 columns in a framework overview
- If content exceeds these limits, split across multiple slides

### 6. Prohibited Patterns
- ❌ Drop shadows on shapes
- ❌ Gradient fills (use solid colors only)
- ❌ Rounded corners with radius > 0.05"
- ❌ Clip art or stock photos
- ❌ WordArt or decorative text effects
- ❌ More than 3 font sizes on a single slide
- ❌ Text smaller than 9pt
- ❌ Pure black (#000000) anywhere in the presentation
- ❌ Using theme colors instead of explicit hex values

### 7. Spacing Standards
- Minimum margin from slide edge: 0.5" (all sides)
- Minimum gap between cards: 0.15"
- Text padding inside cards: 0.15" all sides
- Line spacing: 1.0-1.2 (never double-spaced)

## Validation
Before saving any generated PPTX, verify:
1. Every slide has the correct background colour for its position
2. Top bar is present on every slide
3. No prohibited patterns are used
4. Font family is correct for each text role
5. All hex colors match the palette exactly

