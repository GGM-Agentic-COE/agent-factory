---
name: html-doc
description: Generates professional HTML documents following the Ascendion Agentic CoE visual design system. Use this whenever asked to create an HTML document, guide, standards doc, or technical write-up.
trigger: When the user asks to create an HTML document, guide, write-up, standards page, or any long-form HTML content that should follow the dark-navy design system.
---

# HTML Document Generator Skill

## Inputs
- `title`: Document title
- `subtitle`: Subtitle or description line
- `sections`: Content to structure into the document

## Design System

### Color Palette

| Role | Hex | CSS Variable | Usage |
|------|-----|-------------|-------|
| Dark Background | `#0D1B2A` | `--dark-bg` | Header, code blocks, callouts, card-dark |
| Light Background | `#E0E1DD` | `--light-bg` | Page body background |
| Accent Blue | `#4DA8DA` | `--accent` | Top bar, h4, links, badges, borders |
| Card Dark Fill | `#1B2838` | `--card-dark` | Flow steps, dark cards |
| Muted Text | `#778DA9` | `--muted` | Code text, secondary text on dark |
| Body Text | `#415A77` | `--body-light` | Main body text on light bg |
| Green Accent | `#81B29A` | `--green` | Secondary cards, highlighted flow steps |
| Coral Accent | `#E07A5F` | `--coral` | Warnings, anti-patterns |
| White | `#FFFFFF` | `--white` | Card backgrounds, text on dark |

### Typography

| Element | Font | Size | Color |
|---------|------|------|-------|
| Document Title (h1) | Trebuchet MS | 28pt | `#FFFFFF` (in header) |
| Section Title (h2) | Trebuchet MS | 20pt | `#0D1B2A` |
| Sub-heading (h3) | Trebuchet MS | 14pt | `#0D1B2A` |
| Label/Accent (h4) | Calibri | 12pt | `#4DA8DA` |
| Body text (p, li) | Calibri | 11pt | `#415A77` |
| Code (pre, code) | Courier New | 9.5pt | `#778DA9` (block) / `#4DA8DA` (inline) |
| Table cells | Calibri | 10.5pt | `#415A77` |

### Structural Elements

#### Header
- Full-width dark background (`#0D1B2A`)
- Top border: 5px solid `#4DA8DA`
- Contains: h1 title + subtitle paragraph
- Bottom border-radius: 4px
- Margin-bottom: 40px

#### Table of Contents
- White card background
- Ordered list with accent-colored links
- Placed immediately after header

#### Section Headings (h2)
- Border-bottom: 3px solid `#4DA8DA`
- Margin-top: 40px (clear separation between sections)

#### Cards
- **Light card**: white bg, 4px left border (accent blue), 3px border-radius
- **Dark card**: `#0D1B2A` bg, 4px left border (accent blue), muted text color
- **Green variant**: left border `#81B29A` — for secondary/alternative content
- **Coral variant**: left border `#E07A5F` — for warnings/anti-patterns

#### Grid Layout
- 2-column grid (`.grid`): `grid-template-columns: 1fr 1fr; gap: 14px`
- Use for side-by-side comparison cards

#### Callout
- Dark bg (`#0D1B2A`), 4px left border accent, white text
- Used for key principles, summary statements

#### Flow Diagrams
- Horizontal flex layout with flow-step boxes and `▶` arrows
- Steps: dark card bg, white text, accent left border
- Highlighted steps: green left border

#### Code Blocks (pre)
- Dark bg (`#0D1B2A`), muted text (`#778DA9`)
- Courier New, 9.5pt, 1.5 line-height
- 14px 18px padding

#### Tables
- Dark header row (`#0D1B2A`, white text)
- Alternating row bg (even rows: white)
- Full width, collapsed borders

#### Badges
- Circular, 28px, accent/green bg, bold Trebuchet MS, white text
- Used as inline labels before headings

### Prohibited Patterns
- ❌ No gradients
- ❌ No drop shadows
- ❌ No rounded corners > 4px
- ❌ No colors outside the palette
- ❌ No Arial, Helvetica, or sans-serif fallback for headings (must be Trebuchet MS)
- ❌ No pure black (`#000000`) anywhere
- ❌ No text smaller than 9pt

## Document Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
:root {
  --dark-bg: #0D1B2A;
  --light-bg: #E0E1DD;
  --accent: #4DA8DA;
  --card-dark: #1B2838;
  --muted: #778DA9;
  --body-light: #415A77;
  --green: #81B29A;
  --coral: #E07A5F;
  --white: #FFFFFF;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: Calibri, sans-serif; background: var(--light-bg); color: var(--body-light); line-height: 1.6; }
.container { max-width: 100%; margin: 0 auto; padding: 48px 60px; }
.header {
  background: var(--dark-bg); padding: 48px 40px; border-top: 5px solid var(--accent);
  margin-bottom: 40px; border-radius: 0 0 4px 4px;
}
.header h1 { font-family: 'Trebuchet MS', sans-serif; color: var(--white); font-size: 28pt; font-weight: normal; margin-bottom: 8px; }
.header p { color: var(--muted); font-size: 13pt; }
h2 {
  font-family: 'Trebuchet MS', sans-serif; color: var(--dark-bg); font-size: 20pt;
  font-weight: normal; margin: 40px 0 6px; padding-bottom: 6px;
  border-bottom: 3px solid var(--accent);
}
h3 { font-family: 'Trebuchet MS', sans-serif; color: var(--dark-bg); font-size: 14pt; margin: 20px 0 8px; }
h4 { font-size: 12pt; color: var(--accent); margin: 14px 0 6px; }
p { margin-bottom: 10px; font-size: 11pt; }
ul, ol { padding-left: 20px; margin-bottom: 12px; }
li { margin-bottom: 4px; font-size: 11pt; }
.card {
  background: var(--white); border-left: 4px solid var(--accent); border-radius: 3px;
  padding: 16px 20px; margin: 12px 0;
}
.card-dark {
  background: var(--dark-bg); border-left: 4px solid var(--accent); border-radius: 3px;
  padding: 16px 20px; margin: 12px 0; color: var(--muted);
}
.card-dark h3, .card-dark h4 { color: var(--white); }
.card-green { border-left-color: var(--green); }
.card-coral { border-left-color: var(--coral); }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 14px 0; }
.badge {
  display: inline-flex; align-items: center; justify-content: center;
  width: 28px; height: 28px; border-radius: 50%; font-family: 'Trebuchet MS';
  font-size: 11pt; font-weight: bold; color: var(--white); background: var(--accent);
  margin-right: 8px; vertical-align: middle;
}
.badge-green { background: var(--green); }
.flow { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin: 10px 0; }
.flow-step {
  background: var(--card-dark); color: var(--white); padding: 6px 12px;
  border-radius: 3px; font-size: 10pt; border-left: 3px solid var(--accent);
}
.flow-step.hl { border-left-color: var(--green); }
.flow-arrow { color: var(--accent); font-size: 13pt; }
pre {
  background: var(--dark-bg); color: var(--muted); padding: 14px 18px;
  border-radius: 3px; font-family: 'Courier New', monospace; font-size: 9.5pt;
  line-height: 1.5; overflow-x: auto; margin: 10px 0;
}
code { font-family: 'Courier New', monospace; font-size: 9.5pt; color: var(--accent); }
.callout {
  background: var(--dark-bg); border-left: 4px solid var(--accent); border-radius: 3px;
  padding: 12px 18px; margin: 16px 0; color: var(--white); font-size: 11pt;
}
.toc { background: var(--white); padding: 20px 24px; border-radius: 3px; margin-bottom: 32px; }
.toc a { color: var(--accent); text-decoration: none; font-size: 11pt; }
.toc li { margin-bottom: 6px; }
table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 10.5pt; }
th { background: var(--dark-bg); color: var(--white); padding: 8px 12px; text-align: left; }
td { padding: 8px 12px; border-bottom: 1px solid var(--light-bg); }
tr:nth-child(even) td { background: var(--white); }
</style>
</head>
<body>
<div class="container">

<div class="header">
  <h1>{title}</h1>
  <p>{subtitle}</p>
</div>

<div class="toc">
  <h3 style="margin-top:0;">Contents</h3>
  <ol>
    <li><a href="#section-1">{Section 1 title}</a></li>
    <!-- ... -->
  </ol>
</div>

<h2 id="section-1">1. {Section Title}</h2>
<p>{Content}</p>

<!-- Use components as needed: -->
<!-- .card, .card-dark, .card-green, .card-coral -->
<!-- .grid for 2-column layouts -->
<!-- .callout for key statements -->
<!-- .flow + .flow-step + .flow-arrow for diagrams -->
<!-- pre for code blocks -->
<!-- table for structured data -->
<!-- .badge for inline numbered/lettered markers -->

</div>
</body>
</html>
```

## Quality Checklist
- [ ] All colors match palette exactly (no approximations)
- [ ] Headings use Trebuchet MS, body uses Calibri
- [ ] Header has dark bg with 5px accent top border
- [ ] Section h2 has 3px accent bottom border
- [ ] Cards have 4px left border (accent, green, or coral)
- [ ] Code blocks use dark bg with muted text
- [ ] Tables have dark header row
- [ ] No prohibited patterns (shadows, gradients, off-palette colors)
- [ ] TOC present with anchor links for all sections
- [ ] Container is full-width with 60px horizontal padding
