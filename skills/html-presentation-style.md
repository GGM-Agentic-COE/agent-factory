---
name: html-presentation-style
description: Standard HTML presentation template with dark theme, card-based layout, and Ascendion branding. Use this whenever asked to create an HTML presentation — apply this exact CSS, structure, and component patterns.
---

# HTML Presentation Style Guide

## Base Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>[TITLE]</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Calibri,'Segoe UI',sans-serif;background:#0f172a;color:#e2e8f0}
.slide{min-height:100vh;padding:50px 60px;display:flex;flex-direction:column;justify-content:center;border-bottom:1px solid #1e293b;position:relative}
.slide::after{content:'CONFIDENTIAL — Ascendion';position:absolute;bottom:16px;right:40px;font-size:10px;color:#475569}
h1{font-size:2.6em;font-weight:700;color:#fff;margin-bottom:6px}
h2{font-size:1.8em;font-weight:600;color:#fff;margin-bottom:8px}
h3{font-size:1.05em;font-weight:600;color:#e2e8f0;margin:14px 0 6px}
h4{font-size:.88em;font-weight:700;color:#f1f5f9;margin:6px 0 4px}
p{font-size:.88em;color:#94a3b8;max-width:1000px;margin-bottom:8px;line-height:1.6}
.subtitle{font-size:1em;color:#94a3b8;margin-bottom:20px}
.grid{display:grid;gap:12px;margin:12px 0}
.grid-2{grid-template-columns:1fr 1fr}
.grid-3{grid-template-columns:1fr 1fr 1fr}
.grid-4{grid-template-columns:1fr 1fr 1fr 1fr}
.card{background:#1e293b;border:1px solid #334155;border-radius:10px;padding:16px}
.card h4{margin-top:0;color:#f1f5f9}
.card p{font-size:.82em;color:#94a3b8;margin:0}
.tag{display:inline-block;padding:2px 8px;border-radius:10px;font-size:.68em;font-weight:600;margin:2px}
.t-purple{background:#2d1b69;color:#c4b5fd}
.t-teal{background:#0f3d3e;color:#5eead4}
.t-green{background:#14532d;color:#86efac}
.t-amber{background:#451a03;color:#fbbf24}
.t-blue{background:#1e3a5f;color:#93c5fd}
.t-red{background:#450a0a;color:#fca5a5}
table{width:100%;border-collapse:collapse;margin:10px 0;font-size:.8em}
th{background:#334155;color:#e2e8f0;padding:8px 10px;text-align:left;font-weight:600;font-size:.75em}
td{padding:8px 10px;border-bottom:1px solid #1e293b;color:#cbd5e1}
tr:hover td{background:#263445}
.highlight{background:#1e293b;border:1px solid #334155;border-radius:10px;padding:14px;margin:12px 0}
.key-point{display:flex;align-items:flex-start;gap:8px;margin:6px 0}
.key-point::before{content:'→';color:#7c3aed;font-weight:700;flex-shrink:0}
.key-point p{margin:0;font-size:.85em;color:#cbd5e1}
ul{margin:4px 0 4px 14px}
li{margin:3px 0;color:#94a3b8;font-size:.82em}
.flow{display:flex;gap:32px;margin:14px 0;flex-wrap:wrap;align-items:center}
.flow-step{flex:1;min-width:80px;padding:10px 8px;text-align:center;border-radius:8px;background:#334155;position:relative}
.flow-step::after{content:'→';position:absolute;top:50%;left:100%;transform:translateY(-50%);width:32px;text-align:center;font-size:1.3em;color:#94a3b8}
.flow-step:last-child::after{content:none}
.no-arrows .flow-step::after{content:none}
.flow-step h5{font-size:.68em;color:#c4b5fd;text-transform:uppercase;letter-spacing:.4px;margin-bottom:3px}
.flow-step p{font-size:.68em;color:#94a3b8;margin:0}
.section-label{font-size:.7em;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:6px}
.role-card{background:#334155;border-radius:10px;padding:14px;margin:6px 0}
.role-card h4{color:#38bdf8;margin:0 0 6px;font-size:.88em}
.role-card p{font-size:.78em;color:#94a3b8;margin:2px 0}
.nav-bar{display:flex;gap:0;margin-bottom:24px}
.nav-pill{font-size:.78em;font-weight:600;padding:8px 18px;border-radius:20px;text-decoration:none;color:#94a3b8}
.nav-pill.active{background:#7c3aed;color:#fff}
.nav-pill:not(.active){background:#1e293b;color:#94a3b8}
.phase-pill{display:inline-block;padding:6px 16px;border-radius:20px;font-size:.75em;font-weight:700;color:#fff}
.pill-purple{background:#7c3aed}
.pill-teal{background:#06b6d4}
.pill-green{background:#10b981}
code{background:#334155;color:#c4b5fd;padding:1px 5px;border-radius:3px;font-size:.85em}
.code-block{background:#0f172a;border:1px solid #334155;color:#e2e8f0;border-radius:8px;padding:20px;font-family:'JetBrains Mono',monospace;font-size:.82em;overflow-x:auto;margin:12px 0;line-height:1.7;white-space:pre-wrap;word-wrap:break-word}
.code-block .k{color:#93c5fd}.code-block .s{color:#fbbf24}.code-block .c{color:#64748b;font-style:italic}
.artifact{background:#0f172a;border:2px solid #334155;border-radius:8px;padding:20px;margin:12px 0}
.artifact-title{font-size:.85em;font-weight:700;color:#c4b5fd;margin-bottom:6px;display:flex;align-items:center;gap:6px}
.artifact-title::before{content:'📄';font-size:1em}
.signoff{background:#14532d;border:1px solid #166534;border-radius:8px;padding:12px 16px;margin:12px 0;display:flex;align-items:center;gap:10px}
.signoff::before{content:'✅';font-size:1.2em}
.signoff p{margin:0;font-size:.85em;color:#86efac}
.handover{background:#451a03;border:1px solid #92400e;border-radius:8px;padding:12px 16px;margin:12px 0;display:flex;align-items:center;gap:10px}
.handover::before{content:'🔄';font-size:1.2em}
.handover p{margin:0;font-size:.85em;color:#fbbf24}
.phase-banner{background:linear-gradient(135deg,#1e293b,#334155);border:1px solid #475569;color:#fff;border-radius:10px;padding:14px 20px;margin-bottom:14px}
.phase-banner h2{color:#fff;margin:0;font-size:1.3em}
.phase-banner p{color:#94a3b8;margin:2px 0 0;font-size:.82em}
.fc-banner{background:linear-gradient(135deg,#1e293b,#334155);border:1px solid #475569;border-radius:10px;padding:14px 20px;margin-bottom:14px}
.fc-banner h3{color:#fff;margin:0;font-size:1.1em}
.fc-banner p{color:#94a3b8;margin:2px 0 0;font-size:.82em}
.count-box{font-size:2.2em;font-weight:800;color:#38bdf8;text-align:center}
.total-box{background:linear-gradient(135deg,#1e293b,#334155);border:1px solid #475569;color:#fff;border-radius:12px;padding:24px 32px;text-align:center;margin:20px 0}
.total-box .num{font-size:3em;font-weight:800;color:#38bdf8}
.total-box p{color:#94a3b8;margin:0}
.key-point{display:flex;align-items:flex-start;gap:8px;margin:6px 0}
.key-point::before{content:'→';color:#7c3aed;font-weight:700;flex-shrink:0}
.key-point p{margin:0;font-size:.85em;color:#cbd5e1}
.comparison td:nth-child(2){color:#64748b}
.comparison td:nth-child(3){color:#86efac;font-weight:600}
</style>
</head>
<body>
<!-- SLIDES GO HERE -->
</body>
</html>
```

## Color Palette

| Purpose | Color | Hex |
|---------|-------|-----|
| Background | Dark navy | `#0f172a` |
| Card background | Slate | `#1e293b` |
| Card border | Dark slate | `#334155` |
| Heading text | White | `#fff` |
| Subheading text | Light grey | `#e2e8f0` |
| Body text | Muted grey | `#94a3b8` |
| Table cell text | Light slate | `#cbd5e1` |
| Accent purple | Violet | `#7c3aed` / `#c4b5fd` (light) |
| Accent teal | Cyan | `#06b6d4` / `#5eead4` (light) |
| Accent green | Emerald | `#10b981` / `#86efac` (light) |
| Accent amber | Orange | `#f59e0b` / `#fbbf24` (light) |
| Accent red | Red | `#ef4444` / `#fca5a5` (light) |

## Component Patterns

### Card with colored top border
```html
<div class="card" style="border-top:3px solid #7c3aed">
  <h4>Title</h4>
  <p>Description</p>
</div>
```

### Card with left border (callout)
```html
<div class="card" style="border-left:4px solid #7c3aed">
  <h4>Callout Title</h4>
  <p>Important content here</p>
</div>
```

### Phase pills
```html
<span class="phase-pill pill-purple">INCEPTION</span>
<span class="phase-pill pill-teal">CONSTRUCTION</span>
<span class="phase-pill pill-green">PRODUCTION</span>
```

### Tags
```html
<span class="tag t-purple">Label</span>
<span class="tag t-teal">Label</span>
<span class="tag t-green">Label</span>
```

### Flow visualization (horizontal steps)
```html
<div class="flow">
  <div class="flow-step"><h5>Step 1</h5><p>Description</p></div>
  <div class="flow-step"><h5>Step 2</h5><p>Description</p></div>
</div>
```

### Key points (arrow bullets)
```html
<div class="key-point"><p>Important point with arrow prefix</p></div>
```

### Section label
```html
<div class="section-label">SECTION 1 — TITLE</div>
```

### Role card
```html
<div class="role-card">
  <h4>Role Name</h4>
  <p>→ Responsibility one</p>
  <p>→ Responsibility two</p>
</div>
```

### Navigation pills
```html
<div class="nav-bar">
  <a href="#section1" class="nav-pill active">Section 1</a>
  <a href="#section2" class="nav-pill">Section 2</a>
</div>
```

### Sticky section nav (top of page)
Every presentation MUST include a sticky navigation bar at the top linking to all sections/slides. Add the CSS and HTML immediately after `<body>`:

```css
.nav{position:sticky;top:0;background:#1e293b;padding:10px 40px;z-index:100;display:flex;gap:16px;align-items:center;flex-wrap:wrap;border-bottom:1px solid #334155}
.nav a{color:rgba(255,255,255,.7);text-decoration:none;font-size:11px;font-weight:600}
.nav a:hover{color:#fff}
.nav .brand{color:#fff;font-weight:800;font-size:13px;margin-right:auto}
```

```html
<div class="nav">
  <span class="brand">Presentation Title</span>
  <a href="#section-id-1">Section 1</a>
  <a href="#section-id-2">Section 2</a>
  <a href="#section-id-3">Section 3</a>
</div>
```

Each slide/section `<div>` must have a corresponding `id` attribute matching the nav `href`. Use kebab-case for IDs.

### Navigation button (top-right, links to another page)
```html
<div style="position:fixed;top:20px;right:40px;z-index:1000">
  <a href="other.html" style="padding:8px 16px;font-size:.8em;font-weight:600;border:1px solid #334155;border-radius:20px;background:#1e293b;color:#c4b5fd;text-decoration:none;font-family:Calibri,sans-serif">Link Text →</a>
</div>
```

### Banner slide (slimmer than full page, no min-height)
```html
<div style="padding:60px 80px 50px;border-bottom:1px solid #1e293b;position:relative">
  <div style="position:absolute;bottom:16px;right:40px;font-size:10px;color:#475569">CONFIDENTIAL — Ascendion</div>
  <h1>Title</h1>
  <p class="subtitle">Subtitle</p>
  <!-- Content cards etc -->
</div>
```
**Slide 1 (title slide) MUST always use this banner pattern** — never a full-viewport `.slide` div. This keeps the first slide compact with minimal whitespace, acting as a header/banner before the content slides begin.

### Parallel workflow (fan-out / fan-in)
```html
<div style="display:flex;gap:0;align-items:center;margin:14px 0">
  <div class="flow-step" style="flex:none;width:110px"><h5>Trigger</h5></div>
  <div style="display:flex;flex-direction:column;padding:0 8px;gap:2px">
    <span style="color:#94a3b8;font-size:.9em">→</span>
    <span style="color:#94a3b8;font-size:.9em">→</span>
  </div>
  <div class="no-arrows" style="display:flex;flex-direction:column;gap:8px;flex:1">
    <div class="flow-step">Agent A</div>
    <div class="flow-step">Agent B</div>
  </div>
  <div style="display:flex;flex-direction:column;padding:0 8px;gap:2px">
    <span style="color:#94a3b8;font-size:.9em">→</span>
    <span style="color:#94a3b8;font-size:.9em">→</span>
  </div>
  <div class="flow-step" style="flex:none;width:110px"><h5>Merge</h5></div>
</div>
```
Use `.no-arrows` on the parallel container to suppress `::after` arrows on inner flow-steps.

### Code block (for artifacts, configs, examples)
```html
<div class="code-block">
<span class="k">key:</span> <span class="s">value</span>
<span class="c"># comment</span>
</div>
```

### Artifact container
```html
<div class="artifact">
  <div class="artifact-title">Artifact Name</div>
  <div class="code-block">content here</div>
</div>
```

### Sign-off gate
```html
<div class="signoff"><p><strong>Sign-off:</strong> Description of gate. → Status: <span class="tag t-green">APPROVED</span></p></div>
```

### Handover
```html
<div class="handover"><p><strong>Handover:</strong> What is handed over and to whom.</p></div>
```

### Phase/Feature Cycle banner
```html
<div class="phase-banner"><h2>Phase Name</h2><p>Subtitle — who and when</p></div>
<div class="fc-banner"><h3>FC-01: Feature Name</h3><p>Epic | Depends on: FC-XX</p></div>
```

### Count box (large number display)
```html
<div class="count-box">9–10</div>
```

### Comparison table
```html
<table class="comparison">
<tr><th>Dimension</th><th>Traditional</th><th>New Model</th></tr>
<tr><td>Row</td><td>Old way (grey)</td><td>New way (green)</td></tr>
</table>
```

## Rules
- Font: Calibri (always, both themes)
- **Presentations** (slide-based): Use DARK theme (`#0f172a` background)
- **Deep dives & examples** (section-based, long-form): Use LIGHT theme (`#fff` background)
- Every slide/section has Ascendion footer
- Cards for all grouped content (never bare lists)

### When to use Dark Theme
- Slide-based presentations (one topic per viewport)
- Delivery models, team structures, feature cycles, metrics overviews
- Client-facing decks

### When to use Light Theme
- Long-form documents with detailed technical content
- Deep dives, implementation guides, development guides
- Content with JSON blocks, diagrams, code examples that benefit from light background
- Documents that will be printed or read for extended periods

## Dark Theme Colors (Presentations)
- Background: Dark navy `#0f172a`
- Every slide is `min-height:100vh` (full viewport)
- Footer: "CONFIDENTIAL — Ascendion" on every slide (via CSS ::after)
- Cards for all grouped content (never bare lists on the page)
- Tables have dark header row (`#334155`)
- Use `.grid-2` or `.grid-3` for layouts
- Use `.flow` for sequential/timeline visualizations (gap:20px between steps, `⟶` arrows)
- Use `.key-point` for important bullet points with arrows
- Use `.section-label` for section identifiers
- Use `.tag` for inline labels/badges
- Use `.phase-pill` for phase indicators
- Use `.code-block` for artifacts, configs, and code examples (pre-wrap, larger font)
- Use `.artifact` wrapper with `.artifact-title` for named deliverables
- Use `.signoff` for gate approvals (green) and `.handover` for handover points (amber)
- Use `.phase-banner` or `.fc-banner` for section headers within slides
- Use `.count-box` for large number displays
- Use `.comparison` class on tables for traditional-vs-new comparisons (grey vs green)
- Accent colors: purple for primary, teal for secondary, green for success/production
- Dark backgrounds for flow-step inline styles: purple `#2d1b69`, amber `#451a03`, green `#14532d`, red `#450a0a`, blue `#1e3a5f`, teal `#0f3d3e`, grey `#334155`
- Never use light backgrounds (`#f8f9fc`, `#e3e8f0`, `#fff`) — always dark variants

## Light Theme Colors (Deep Dives & Examples)

| Purpose | Color | Hex |
|---------|-------|-----|
| Background | White | `#ffffff` |
| Card background | Light grey | `#F4F5F7` |
| Card border | Mid grey | `#E0E3E8` |
| Heading text | Navy | `#1B2A4A` |
| Subheading text | Teal | `#0A7E8C` |
| Body text | Grey | `#666` |
| Table header | Navy bg, white text | `#1B2A4A` |
| Accent teal | Teal | `#0A7E8C` |
| Accent green | Green | `#1B8C3A` |
| Accent amber | Amber | `#D4880F` |
| Accent purple | Purple | `#5E35B1` |
| JSON blocks | Dark bg (always) | `#1e1e1e` |

### Light Theme Structure
- Use `<div class="section">` instead of `<div class="slide">`
- Use `<div class="phase-header">` for section banners (dark navy)
- Use `.card` with `.card-teal`, `.card-green`, etc. for colored left borders
- JSON/code blocks stay dark (`#1e1e1e`) for readability
- Footer via `.section::after` CSS
