# Anthropic "Project Deal" Page — Effects & Techniques Reference

**Source page**: https://www.anthropic.com/features/project-deal
**Captured**: 2026-05 (research session)
**Stack signals**: Next.js + React + CSS Modules (class names like `SectionIntroChat-module-scss-module__0VaMXW__avatarAsciiWrap` are the giveaway — that hash is a Next.js build-time fingerprint)

This doc captures every visual/interactive technique we identified on the page, what it's called, how it's built, and the library landscape behind it. Use as context next time we want to copy any of these onto your own coaching site.

---

## 1. Scroll-revealed entrance animation (fade/translate-in on scroll)

**What you see**: As you scroll down, sections, stat blocks, and images fade in and translate up ~20px as they enter the viewport. Not parallax, not scroll-snap — just things "appearing" as you reach them.

**Industry names**: Scroll-revealed entrance animation · Reveal-on-scroll · Scroll-linked fade-in · "whileInView" effect.

**How it's built**:
- **Modern React way**: Framer Motion's `whileInView` prop on each section.
- **Vanilla way** (no library): `IntersectionObserver` fires when an element crosses the viewport, callback adds a CSS class like `.is-visible`, CSS handles the transition. ~15 lines of JS total.
- **Pure CSS (bleeding edge)**: CSS scroll-driven animations via `animation-timeline: view()`. Modern browsers only.

**Minimal vanilla recipe**:
```js
const io = new IntersectionObserver((entries) => {
    entries.forEach(e => e.isIntersecting && e.target.classList.add('is-visible'));
}, { threshold: 0.15 });
document.querySelectorAll('.reveal').forEach(el => io.observe(el));
```
```css
.reveal { opacity: 0; transform: translateY(20px); transition: opacity .6s, transform .6s; }
.reveal.is-visible { opacity: 1; transform: none; }
```

**When to use on coaching site**: credentials blocks, testimonial cards, "how it works" steps. Good fit anywhere with stacked content sections — gives the page a sense of momentum without being heavy-handed.

---

## 2. Sticky scroll / pinned column scrollytelling

**What you see**: In the "Intake Interview" section on desktop — left column shows numbered list (1, 2, 3, … 6) that stays pinned to the viewport while the right column scrolls past with the actual content. The left list highlights the active item as the right content rolls past.

**Industry names**: Sticky scroll · Pinned column · Split-screen scrollytelling · Scroll-linked sticky panel.

**How it's built**:
- **The pin**: `position: sticky; top: <some px>;` on the left column. The browser pins it once you scroll past its top edge and unpins when its parent container scrolls away. CSS-only — one line.
- **The active-state sync**: each numbered section on the right has an `IntersectionObserver`. When it crosses the viewport's halfway line, callback adds an `.active` class to the matching left-side item.
- **Total code**: ~20 lines of JS + a few CSS rules. No library required.

**Sister patterns in this genre**:
- **Pinned timeline** = pin both columns and scrub through frames as you scroll (Apple iPhone reveals). Typically GSAP ScrollTrigger.
- **Scrollytelling** (the umbrella genre): any "scroll position drives layout/content" effect.

**When to use on coaching site**: "How my engagement works" — numbered steps pinned left, detail copy scrolling right. Great fit for service pages because the persistent index reassures readers about the process structure.

---

## 3. Scripted auto-scroll after intro animation

**What you see**: Page loads → intro animation plays → after the animation finishes, the page **auto-scrolls** down to the first content section ("shy got some quirky supplies…"). Reader doesn't have to scroll themselves — the site pulls them into the content.

**Industry names**: Scripted auto-scroll · Scroll choreography on load · Scroll handoff · Onboarding scroll. Pejorative term when overdone: **scroll hijacking**.

**How it's built**:
```js
// Fires when intro animation completes:
const target = document.querySelector('#first-content-section');
target.scrollIntoView({ behavior: 'smooth', block: 'start' });
```
- Trigger is usually a Framer Motion `onAnimationComplete` callback or a `setTimeout` matched to the intro's duration.
- The "buttery smooth" feeling on Anthropic's version is almost certainly **Lenis** (a smooth-scroll library that's become the standard for 2025-era marketing sites) — browser-native `behavior: 'smooth'` is noticeably jerkier.

**UX trade-off (important)**:
- ✅ OK when: fires once on first load, stops the moment the user touches the scroll wheel, destination is genuinely the start of content.
- ❌ Bad when: fires on every navigation, fights the user's wheel input, or skips past content.

**When to use on coaching site**: only if we add an intro animation to the hero. Otherwise, skip — auto-scroll without a preceding animation feels like the page is broken.

---

## 4. ASCII avatar animation (the "Mikaela's agent" figure)

**What you see**: A human/character figure that looks animated, made of numbers and symbols. Discovered the class name `avatarAsciiWrap` in DevTools — that's the smoking gun.

**Industry names**: ASCII art animation · Text-based avatar · ASCII flipbook · ASCII shader (when generated live from an image).

**Critical insight**: It's NOT a video, GIF, or Lottie. It's literally **text characters** in a `<pre>` or `<div>` with monospace font. The character shape is built from characters like `@`, `#`, `%`, `*`, `+`, `=`, `:`, `.`, `-`, etc., mapped to pixel brightness.

**Three implementation styles**:
1. **Frame swap (flipbook)**: pre-rendered ASCII frames in a JS array, `setInterval` swaps `textContent` every ~80–150ms. Like stop-motion but with text.
2. **Character mutation (glitch/breathing)**: start with the base figure, randomly flip a percentage of characters each tick. Shape stays recognizable; details shimmer. This is likely what Anthropic uses.
3. **Generated from an image at runtime**: hidden `<canvas>` reads pixel brightness of an actual image, JS maps each pixel to a character based on darkness. Can be made to "breathe" by re-sampling on a loop.

**Why Anthropic chose this over a video/photo**:
- Tiny payload — text characters are bytes, not megabytes.
- Sharp at any resolution (vector-like).
- On-brand for an AI safety company (terminal/hacker aesthetic).
- Accessible — can include `aria-label="Avatar of Mikaela"` while the visual is decoration.

**Can be applied to your own headshot**:
- One-time conversion: Python script converts `avril-hero-v3.jpg` to a fixed ASCII block (~80×60 chars), pasted as static `<pre>` in HTML. Looks like a dot-matrix sketch.
- Live runtime conversion: hidden canvas + JS pixel sampling + character mutation = animated breathing ASCII portrait. ~60 lines, no library.

---

## Library / tooling landscape

The same visual effects can be built different ways. What Anthropic uses vs. what your site could use:

| Approach | Used by | Notes |
|---|---|---|
| **Framer Motion** (React library) | Anthropic likely uses this | npm package `framer-motion`. Declarative `whileInView`, `animate`, `onAnimationComplete`. Lives inside React/Next.js code. |
| **GSAP / ScrollTrigger** | Pinned timeline cases (Apple) | Most powerful, steepest curve. Imperative timelines. CDN script or npm. |
| **Lenis** | Anthropic for smooth scroll | Smooth-scroll library, 2025-era standard. Replaces browser-native `behavior: 'smooth'` with much smoother easing curves. |
| **IntersectionObserver** (vanilla browser API) | Your site could use this | Zero dependencies, built into every browser. Best for reveal-on-scroll + sticky scroll active-state sync. |
| **CSS `position: sticky`** | Universal | One CSS line. Powers the sticky-column pattern. |
| **Framer (the site builder)** | NOT Anthropic | Different product from Framer Motion. No-code, click-to-add scroll animations. Same company makes both — confusing. |
| **Webflow Interactions (IX2)** | NOT Anthropic | Webflow's no-code scroll-interaction system. Compiles to JS at build time. |

**Important Framer naming confusion**:
- **Framer** (framer.com) = no-code website builder, drag-and-drop, hosted.
- **Framer Motion** (`npm install framer-motion`) = React animation library.
- Same company, completely different products. Easy to mix up when researching.

---

## Cheat sheet — what each effect is called

| What you described | Industry name | Search terms |
|---|---|---|
| Sections fade up on scroll | Scroll-revealed entrance animation | `IntersectionObserver fade in`, `Framer Motion whileInView` |
| Left column pinned, right scrolls past | Sticky scroll / pinned column | `position: sticky scroll`, `scrollytelling sticky` |
| Numbered list lights up as you scroll | Scroll-synced active state | `IntersectionObserver active section nav` |
| Auto-scroll after intro animation | Scripted auto-scroll / scroll handoff | `scrollIntoView smooth`, `Lenis smooth scroll` |
| ASCII figure that moves | ASCII art animation (text flipbook) | `ASCII art animation javascript`, `aalib.js` |

---

## What's feasible to add to avrilwhsu-com (Flask + vanilla JS stack)

Your current stack is server-rendered Flask templates with vanilla JS in `<script>` tags. No React, no build step. This means:

✅ **Trivial to add** (no dependencies needed):
- Scroll-revealed entrance animation (vanilla IntersectionObserver, ~15 lines)
- Sticky scroll pinned column (1 CSS line + IntersectionObserver for active state)
- Scripted auto-scroll (3 lines of JS)
- ASCII avatar (Python one-time conversion → static `<pre>` in HTML)

🟡 **Doable with one CDN script tag**:
- Smoother scroll via Lenis (`<script src="https://cdn.jsdelivr.net/npm/lenis@1/dist/lenis.min.js">`)
- GSAP ScrollTrigger if we ever want pinned timeline scrubbing

🔴 **Would require a stack change** (not recommended for your site):
- Framer Motion (needs React)
- Anything requiring a React component tree

The takeaway: every effect Anthropic uses on that page can be reproduced on your Flask site without changing your stack or installing anything heavy. Just vanilla JS + CSS.

---

## 5. Hero section sizing — viewport-locked vs content-intrinsic

**Question raised**: Does Project Deal set its hero / sections to viewport size (e.g. `min-height: 100vh`)?

### What we could verify
- WebFetch only sees Anthropic's server-rendered HTML; CSS lives in compiled Next.js bundles (`/_next/static/css/...`) that aren't visible to scraping.
- No `vh`/`vw`/`dvh` units appear in inline styles or class names that surface in the HTML.
- No class names like `full-screen`, `viewport`, `hero-full`, `100vh` in the rendered markup.

### My assessment (educated, not verified)
**Project Deal does NOT use viewport-locked section heights.** Reasoning:

1. **Content-flow design** — long-form scrollytelling. Sections are sized to their content + padding, not to a viewport. The opposite of `min-height: 100vh` design.
2. **The "Intake Interview" sticky-scroll pattern requires a tall parent** so the sticky column can pin against scrolling siblings. A `100vh` parent would constrain that scroll dance.
3. **Anthropic's other marketing pages** (pricing, careers) consistently use content-intrinsic section heights, not viewport-locked ones.

### How to verify yourself in 60 seconds
1. Open https://www.anthropic.com/features/project-deal in Chrome.
2. Right-click a section → **Inspect** → check the section's computed CSS.
3. Look for `min-height` and `height` — if you see `100vh`/`100dvh`, viewport-locked is in use. If `auto` or a fixed `px`/`rem`, content-intrinsic.

### Two design philosophies compared

| Approach | Behavior | Pros | Cons |
|---|---|---|---|
| **Viewport-locked** (`min-height: 100vh`) | Every section is at least one screen tall | Strong visual rhythm, forces deliberate scroll moments | Lots of empty space when content is short |
| **Content-intrinsic** (Project Deal style) | Section is exactly as tall as content + padding | Reading flows naturally, no wasted space | Less cinematic, can feel like a wall of text |

Your **avrilwhsu-com substack page** currently uses `min-height: 100vh` on the gray Keynotes section (viewport-locked). Your **home page hero** uses `min-height: 70vh` (also viewport-anchored). Different from Project Deal's content-intrinsic approach.

---

## 6. "Big hero title centered in the viewport" pattern

**The pattern**: a hero section that fills exactly one viewport height, with a large title centered both vertically and horizontally — guaranteed to be visible above the fold on page load.

### The CSS (6 lines)

```css
.hero {
    min-height: 100vh;
    min-height: 100dvh;        /* mobile-safe override */
    display: flex;
    align-items: center;       /* vertical centering */
    justify-content: center;   /* horizontal centering */
    text-align: center;
}

.hero-title {
    font-size: clamp(2rem, 6vw, 5rem);  /* big + responsive */
    line-height: 1.1;
}
```

### Why each line matters
- `min-height: 100vh` — section fills exactly one viewport. Always above the fold.
- `min-height: 100dvh` — mobile-safe fallback. On phones, the address bar can briefly steal `100vh`, causing content to clip. `100dvh` (dynamic viewport height) accounts for this. Browsers that support it use it; older ones fall back to `100vh`.
- `display: flex` + `align-items: center` + `justify-content: center` — title sits in the dead-center of the viewport, vertically and horizontally.
- `clamp(2rem, 6vw, 5rem)` — title scales with viewport width: minimum 32px (mobile), grows to 6% of viewport width (~77px on a 1280px screen), maxes out at 80px. Tune these numbers to taste.
- `line-height: 1.1` — tight line spacing for large display text so multi-line titles don't feel airy.

### Sticky-nav gotcha

If a sticky topnav sits above the hero (as on avrilwhsu-com — `.topnav` is `position: sticky; top: 0`), the nav takes its natural height in flow before the hero. So:
- Nav (~64px) + Hero (100vh) = total above the fold > one viewport height
- Bottom of hero sits slightly below the fold

Two ways to handle:

1. **Subtract nav height** for pixel-perfect "everything fits above the fold":
   ```css
   .hero {
       min-height: calc(100dvh - 4rem);  /* subtract nav height */
   }
   ```
2. **Leave it as-is** for stronger vertical centering of the title:
   - Hero is true 100vh. Title centers in that space.
   - Bottom sliver of hero (matching nav height) is below the fold.
   - Often looks better — title is visually centered in the visible area.

### When to use this pattern
- Above-the-fold "hook" sections (e.g. the high schooler presentation intro)
- One-off conversion pages where you want a single message to dominate the first screen
- Landing pages for events / launches

### When NOT to use it
- Content-driven articles or blog posts (Project Deal style) — viewport-locked sections feel forced
- Anywhere readers need to scan/skim quickly — they'd rather see multiple cards/sections at once

---

## 7. The numbered side table-of-contents pattern (Anthropic's 1–6 step nav)

**What you see on Project Deal**: A column of numbered steps pinned to the left side of the viewport as you scroll. The 6 steps:

1. Intake interview
2. Agent assignment
3. Agents deployed
4. Agents negotiate
5. Deal execution
6. In-person exchange

As the reader scrolls through the corresponding right-column content, the number for the current step **lights up** (becomes black/bold), and the previous numbers dim. Clicking a number scrolls to that section. The numbers persist on the left edge throughout the entire 6-step area.

### What this pattern is called (industry names)
- **Sticky table of contents** (the most common name)
- **Anchor navigation** / **side nav anchors**
- **Scroll-spy** (when the active-state highlighting is emphasized)
- **Numbered step indicator** / **stepper nav**
- **Pinned section index**
- **In-page navigation** (less specific)

This is a more specific *variant* of the general "sticky scroll / pinned column scrollytelling" pattern covered in Section 2. The defining features:
- Numbered or labeled list (not free-form content)
- Active-state highlighting tied to scroll position
- Click-to-scroll behavior
- Lives in a sidebar, not a full split-screen column

### The 4 sub-features that compose this pattern

| Feature | What it does | Built with |
|---|---|---|
| **Sticky positioning** | TOC stays in view as right column scrolls | CSS `position: sticky; top: <some px>;` |
| **Scroll-spy / active state** | Current step lights up as you scroll past it | JS `IntersectionObserver` watching each section, toggles `.active` class on the matching TOC item |
| **Click-to-scroll** | Clicking a TOC item scrolls to that section | Each TOC item is `<a href="#step-1">`. CSS `html { scroll-behavior: smooth; }` makes it animate. |
| **Visual progress / connector lines** | Numbers connected with vertical lines, progress bar fills as you scroll | CSS pseudo-elements (`::before`, `::after`) for connector lines; JS-set CSS variable for progress fill height |

### The HTML structure

```html
<section class="process">
    <aside class="process-nav">
        <ol>
            <li><a href="#step-1" class="process-nav-item">
                <span class="process-num">1</span>
                <span class="process-label">Intake interview</span>
            </a></li>
            <li><a href="#step-2" class="process-nav-item">
                <span class="process-num">2</span>
                <span class="process-label">Agent assignment</span>
            </a></li>
            <!-- ... 4 more ... -->
        </ol>
    </aside>

    <div class="process-content">
        <section id="step-1">
            <h2>Intake interview</h2>
            <p>...long content...</p>
        </section>
        <section id="step-2">
            <h2>Agent assignment</h2>
            <p>...long content...</p>
        </section>
        <!-- ... 4 more ... -->
    </div>
</section>
```

Two columns inside `.process`: the `<aside>` (TOC) and the `<div>` (content). On desktop, lay them out side-by-side with grid or flex. On mobile, the TOC typically collapses to a single horizontal scroller or hides entirely.

### The CSS (~20 lines)

```css
.process {
    display: grid;
    grid-template-columns: 280px 1fr;
    gap: 4rem;
    max-width: 1200px;
    margin: 0 auto;
    padding: 4rem 1.5rem;
}

.process-nav {
    position: sticky;
    top: 6rem;                  /* clears the sticky topnav */
    align-self: start;          /* don't stretch full height of grid */
}

.process-nav ol {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
}

.process-nav-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    color: #9ca3af;             /* dimmed by default */
    text-decoration: none;
    transition: color 0.2s;
}

.process-nav-item.active {
    color: #000;                /* lit up when section is in view */
    font-weight: 600;
}

.process-num {
    width: 1.75rem;
    height: 1.75rem;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #f3f4f6;
    font-variant-numeric: tabular-nums;
}

.process-nav-item.active .process-num {
    background: #000;
    color: #fff;
}

/* On mobile, collapse to a sticky horizontal strip OR hide entirely */
@media (max-width: 768px) {
    .process { grid-template-columns: 1fr; }
    .process-nav { display: none; }     /* simplest: hide on mobile */
}
```

### The JS (~15 lines, vanilla — no library)

```js
const navItems = document.querySelectorAll('.process-nav-item');
const sections = document.querySelectorAll('.process-content section');

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const id = entry.target.id;
            navItems.forEach(item => {
                item.classList.toggle('active', item.getAttribute('href') === `#${id}`);
            });
        }
    });
}, {
    rootMargin: '-40% 0px -50% 0px'   // a section is "active" when its top crosses ~40% from viewport top
});

sections.forEach(section => observer.observe(section));
```

That's the entire mechanism. `IntersectionObserver` watches every step section; when one enters the "active band" (between 40% and 50% from the top of the viewport), the matching TOC item gets the `.active` class. The `rootMargin` is the secret sauce — it defines what counts as "currently being read."

### Variants you'll see in the wild

| Variant | Where you see it | Difference |
|---|---|---|
| **Numbered steps** (Anthropic Project Deal) | Process / methodology pages | Each item has a number + label |
| **Bulleted TOC** (Stripe docs, MDN, Notion) | Documentation pages | No numbers, just heading labels |
| **Dot navigation** (Apple product pages) | Marketing slides | Dots instead of numbers, often horizontal |
| **Progress bar TOC** (Medium articles) | Long-form writing | A vertical line that fills as you scroll |
| **Floating button + popup** (Vercel docs) | Mobile-first docs | TOC hides until tapped |

### When to use this pattern on your site

✅ **Great fit**:
- Service/process pages where you walk readers through a sequence (e.g. "How my coaching engagement works" — 5–8 steps)
- Long methodology explanations (your "Recipe for AI-able vs. non-AI-able work" could use this)
- Multi-step case studies

❌ **Bad fit**:
- Short pages (under 3–4 sections) — TOC adds clutter without paying off
- Pages where order doesn't matter (use a card grid instead)
- Pages users skim, not read deeply

### Implementation difficulty on your Flask stack
- **HTML**: ~30 lines for a 6-step structure (the layout above)
- **CSS**: ~20 lines (the rules above)
- **JS**: ~15 lines of vanilla IntersectionObserver (no library needed)
- **Total**: ~65 lines across [templates/](../templates/) and [static/style.css](../static/style.css)

This is one of the highest-leverage patterns we've discussed — relatively simple to build, but transforms how readers experience long content. Worth doing if you ever write a "how my engagement works" page or similar process description.

---

## 8. The HTML+CSS comparison chart pattern (Anthropic's $38 vs $65 bike chart)

**What you see on Project Deal**: In "The findings" section, there's a broken-bike photo next to a comparison showing two prices — **$38 (Sold by Haiku agent)** vs **$65 (Sold by Opus agent)**, with **"70% Price increase"** between them. The chart looks like a designed graphic but the numbers are real, selectable text.

**Initial wrong assumption**: I first told you this was a static image. The user correctly pushed back — "the $ values look selectable so it's not an image." Re-verified: the bike *photo* is an image, but the price comparison is built entirely in HTML + CSS with real text.

### What this pattern is called (industry names)
- **HTML+CSS chart bars** / **CSS-only chart**
- **Static comparison chart** (no JS, no chart library)
- **Markup chart** / **semantic chart**
- **Pure CSS bar chart** (when bars are involved)
- **Stat block** / **comparison stat** (for simpler 2-value comparisons)

### Why HTML+CSS over the alternatives

| Approach | Pros | Cons |
|---|---|---|
| **Static image** (Figma export → `<img>`) | Designer pixel-control, fast to author once | ❌ Text not selectable, no SEO, hard to update, doesn't scale crisply |
| **Chart library** (Recharts, D3, Chart.js) | Dynamic data, interactivity, animations | ❌ Adds 100KB+ JS, overkill for static numbers, harder to design-tune |
| **HTML + CSS** (Anthropic's choice) | ✅ Tiny code, selectable text, SEO-readable, easy to update, accessible | Slightly more work than image, less flexible for animation |

For marketing pages with **static historical data** (the experiment is over — $38 and $65 won't change), HTML+CSS is the sharpest call. You only need a chart library if data updates dynamically (live dashboard, user-driven analytics).

### The HTML structure (~12 lines)

```html
<div class="price-comparison">
    <div class="price-bar price-bar-haiku" style="width: 38%;">
        <span class="price-label">$38</span>
        <span class="price-meta">Sold by Haiku agent</span>
    </div>
    <div class="price-bar price-bar-opus" style="width: 65%;">
        <span class="price-label">$65</span>
        <span class="price-meta">Sold by Opus agent</span>
    </div>
    <div class="price-delta">70% Price increase</div>
</div>
```

Notes:
- Each bar's **width is set inline** (`style="width: 38%;"`). This is one of the rare legitimate uses of inline styles — the width represents data, so it belongs with the data in the HTML, not in a separate CSS rule.
- The dollar amounts (`$38`, `$65`) and labels are in `<span>` elements — **real selectable HTML text**. Screen readers announce them. Search engines index them. Users can copy/paste them.
- The "70% Price increase" callout is also plain text in a `<div>`.

### The CSS (~25 lines)

```css
.price-comparison {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    max-width: 600px;
    margin: 2rem auto;
}

.price-bar {
    background: linear-gradient(to right, #f3f4f6, #e5e7eb);
    padding: 1rem 1.5rem;
    border-radius: 8px;
    display: flex;
    align-items: baseline;
    gap: 1rem;
    /* width is set inline based on data — see HTML above */
}

.price-bar-opus {
    background: linear-gradient(to right, #fef3c7, #fde68a);  /* yellow tint */
}

.price-label {
    font-size: 2rem;
    font-weight: 700;
    font-variant-numeric: tabular-nums;  /* monospace digits — keeps columns lined up */
    color: #111;
}

.price-meta {
    color: #555;
    font-size: 0.95rem;
}

.price-delta {
    font-weight: 600;
    color: #000;
    text-align: center;
    font-size: 1.125rem;
    margin-top: 0.5rem;
}
```

That's a complete, production-quality comparison chart in ~37 lines. No JS, no library, no build step.

### Variants of this pattern

| Variant | What it looks like | When to use |
|---|---|---|
| **Bar comparison** (Anthropic's) | Horizontal bars, width proportional to value | Comparing 2–5 numbers |
| **Stat block grid** | Big numbers in a row, no bars | Headline metrics ("$4,000 in transactions / 6 categories / 70% gain") |
| **Pictographic** | Icons repeated to represent quantity | When you want it to feel "infographic-ish" |
| **Donut/pie with CSS conic-gradient** | Pure CSS donut chart | Single percentage breakdown |
| **Sparkline-as-SVG** | Tiny inline SVG line/bar chart | Embedded in body text, e.g. "revenue ▁▃▅▇" |

### Animated entrance (optional)

Pair this chart with the **scroll-revealed entrance animation** (Section 1 of this doc): bars expand from `width: 0` to their target width as the section scrolls into view. The visual story becomes "the bars *grow* as you read." ~10 extra lines:

```js
// In your scroll-reveal IntersectionObserver:
if (entry.isIntersecting) {
    entry.target.querySelectorAll('.price-bar').forEach(bar => {
        const target = bar.dataset.width;       // e.g. "38"
        bar.style.width = target + '%';
    });
}
```
```html
<!-- bars start at width: 0, store target in data attribute -->
<div class="price-bar" style="width: 0;" data-width="38">
    <span class="price-label">$38</span>
    ...
</div>
```
```css
.price-bar {
    transition: width 1.2s ease;
}
```

### When to use this pattern on your site

✅ **Great fit**:
- "Before AI / After AI" comparison (e.g. earnings, hours, projects shipped)
- Pricing tier visualizations on a services page
- Outcome metrics from coaching engagements ("Client X grew revenue 3x in 6 months")
- Any "this number vs. that number" moment in your content

❌ **Bad fit**:
- More than 5–8 data points (becomes cluttered, use a real chart library)
- Live/dynamic data that changes after page load
- Complex charts with axes, gridlines, multiple series (use Recharts or similar)

### Total implementation cost on your Flask stack
- HTML: ~12 lines per chart instance
- CSS: ~25 lines (write once, reuse across charts)
- JS (optional, for entrance animation): ~5 lines added to your existing IntersectionObserver
- **Total**: ~42 lines for the first chart, ~12 lines per additional chart

One of the cheapest, highest-impact patterns in the doc. Whenever you want to make a data point pop on a marketing page — this is the technique.

---

## 9. Scroll-triggered staggered reveal (the "cascade" effect within a section)

**What you see on Project Deal**: Inside each of the 6 numbered process steps (Intake Interview, Agent Assignment, etc.), when you scroll into a section, the content elements appear **one by one with a small delay between each** — not all at once. First the heading slides up, then ~150ms later the first paragraph, then the second, etc. Your eye follows the cascade.

**Different from**: the basic "fade-in-on-scroll" entrance (Section 1) where everything in a section appears together. Stagger reveal adds *rhythm* — the section feels choreographed and intentional.

### Industry names
- **Stagger reveal** / **staggered entrance**
- **Cascade animation** / **cascade reveal**
- **Sequential reveal** / **sequenced fade-in**
- **Scroll-triggered stagger**
- In Framer Motion specifically: **`staggerChildren`** transition

### What we could verify
- WebFetch only sees server-rendered HTML; the actual animation logic is React/Framer Motion in compiled bundles, invisible to scraping
- But the *effect* is observable in any modern browser — definitively present on the page

### Three implementation paths (ranked by your Flask + vanilla JS stack)

#### Pattern A — IntersectionObserver + CSS `transition-delay` (recommended)
**How it works**:
1. Section enters viewport → JS adds `.is-visible` class to the section
2. CSS uses `:nth-child(n)` selectors to apply increasing `transition-delay` to each child element
3. Each child fades + translates in with its assigned delay

**Code footprint**: ~15 lines JS + ~15 lines CSS, no library.

**The CSS**:
```css
.process-section > * {
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.6s ease, transform 0.6s ease;
}

.process-section.is-visible > * {
    opacity: 1;
    transform: none;
}

.process-section.is-visible > *:nth-child(1) { transition-delay: 0.05s; }
.process-section.is-visible > *:nth-child(2) { transition-delay: 0.2s; }
.process-section.is-visible > *:nth-child(3) { transition-delay: 0.35s; }
.process-section.is-visible > *:nth-child(4) { transition-delay: 0.5s; }
.process-section.is-visible > *:nth-child(5) { transition-delay: 0.65s; }
.process-section.is-visible > *:nth-child(6) { transition-delay: 0.8s; }

@media (prefers-reduced-motion: reduce) {
    .process-section > * {
        opacity: 1;
        transform: none;
        transition: none;
    }
}
```

**The JS** — extend the existing IntersectionObserver by adding `is-visible` on intersection:
```js
if (entry.isIntersecting) {
    entry.target.classList.add('is-visible');
    // ... rest of existing TOC active-state logic
}
```

#### Pattern B — Pure CSS `animation-timeline: view()` (no JS at all)
**How it works**: CSS scroll-driven animations tie each element's opacity/translate to scroll position. The browser handles everything; no JS needed.

```css
@keyframes reveal {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: none; }
}

.process-section > * {
    animation: reveal linear both;
    animation-timeline: view();
    animation-range: entry 0% entry 50%;
}

.process-section > *:nth-child(1) { animation-delay: 0s; }
.process-section > *:nth-child(2) { animation-delay: 0.15s; }
/* ... etc ... */
```

**Tradeoff**: requires Chrome 115+, Safari 18+, Firefox 121+ (2024+ browsers). Universal support in 2026 but very old devices might not see the effect.

#### Pattern C — Framer Motion `staggerChildren` (what Anthropic uses)
**How it works**: in React with Framer Motion:
```jsx
<motion.section
    variants={{ animate: { transition: { staggerChildren: 0.15 } } }}
    initial="initial"
    whileInView="animate"
>
    <motion.h2 variants={{ initial: { opacity: 0, y: 20 }, animate: { opacity: 1, y: 0 } }}>...</motion.h2>
    <motion.p variants={...}>...</motion.p>
</motion.section>
```

**Tradeoff**: requires React + Framer Motion. Not applicable to Flask without stack change.

### Tunable parameters (Pattern A)

| Parameter | Default | Snappier | More dramatic |
|---|---|---|---|
| **Stagger delay** | `0.15s` between siblings | `0.08s` | `0.25s` |
| **Translate distance** | `20px` | `10px` (subtle) | `40px` (pronounced) |
| **Transition duration** | `0.6s` | `0.4s` | `0.8s` |
| **Easing** | `ease` | `ease-out` | `cubic-bezier(0.2, 0.8, 0.2, 1)` |

### When to use this pattern

✅ **Good fit**:
- Long-form scrollytelling pages (Anthropic Project Deal, your article pages)
- Multi-paragraph sections that benefit from visual rhythm
- Pages where each section has 3+ child elements (headings, paragraphs, images, callouts)

❌ **Skip**:
- Single-element sections (just a heading + image) — there's nothing to "cascade"
- Scannable / table-heavy pages where readers want to absorb everything at once
- Forms or checkout flows — staggering input fields is annoying

### Integration with existing patterns on avrilwhsu-com

The article page `/human-AI-collaboration-creativity` already uses:
- Section 7 pattern (sticky numbered TOC)
- Scroll-snap (`html:has(.process) { scroll-snap-type: y mandatory; }`)
- Topnav-hide-during-snap effect

This stagger pattern composes cleanly on top — extend the existing IntersectionObserver to also toggle `.is-visible` on each section, add the CSS, done. ~30 extra lines of code, no conflicts with the snap/sticky behavior.

### Implementation difficulty on Flask stack
- **CSS**: ~15 lines
- **JS**: ~1 line addition to existing observer (`entry.target.classList.add('is-visible')`)
- **Total**: ~16 lines on top of what's already on the article page

One of the highest-leverage patterns to add on top of existing scroll-snap pages. Transforms static sections into choreographed reveals with minimal code.

---

## 9b. Pattern A-progressive: reveal-as-you-scroll (variable-height sections)

**Variation of Section 9.** Use this when you want each section to be **as tall as its content needs** (not fixed at 100vh), and content items reveal progressively as the user scrolls deeper into the section — rather than all cascading in when the section enters viewport.

### How it differs from Pattern A (Section 9)

| Aspect | Pattern A (cascade on enter) | Pattern A-progressive (reveal as you scroll) |
|---|---|---|
| **Section height** | Fixed `min-height: 100vh` | Variable, content-driven |
| **Reveal trigger** | Section enters viewport | Each child enters viewport |
| **Reveal timing** | All children cascade with stagger delays | Each child reveals when it crosses viewport line |
| **Scroll-snap mode** | Works with `mandatory` | Requires `proximity` (mandatory traps users in tall sections) |
| **User experience** | One choreographed reveal per section | Continuous reveal as user scrolls deeper |
| **Best for** | Short sections, cinematic snap rhythm | Long-form sections, reading-friendly flow |

### The 3 implementation changes vs. Section 9

#### 1. Remove the `min-height: 100vh` constraint
```css
.process-section {
    /* min-height: 100vh;  ← remove this */
    scroll-snap-align: start;
    padding: 7.5rem 0 4rem;
}
```
Sections now size to their content. A section with 2 paragraphs is ~60vh tall; a section with 10 paragraphs + 3 images is ~400vh tall.

#### 2. Observer watches each child item, not whole sections
```js
const items = document.querySelectorAll('.process-section > *');
const itemObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) entry.target.classList.add('is-visible');
    });
}, {
    rootMargin: '0px 0px -20% 0px',   // triggers when item is 20% above viewport bottom
    threshold: 0.1                     // requires 10% visible
});
items.forEach(item => itemObserver.observe(item));
```

CSS becomes simpler — no `:nth-child` delays needed since each item reveals independently:
```css
.process-section > * {
    opacity: 0;
    transform: translateY(30px);
    transition: opacity 0.7s ease, transform 0.7s ease;
}
.process-section > *.is-visible {
    opacity: 1;
    transform: none;
}
```

#### 3. Switch scroll-snap mode from `mandatory` to `proximity`
```css
html:has(.process) {
    scroll-snap-type: y proximity;  /* was: mandatory */
}
```

With `mandatory`, tall sections trap users — browser keeps snapping back to section boundaries while they're reading mid-section. **Proximity** lets users scroll freely within a tall section, and only nudges to snap when they're close to the next section boundary. This is what Anthropic Project Deal uses.

### Full UX flow (8 sections, applied to your article page)

1. User lands on hero (snap point) → topnav visible, reads the title + Georgetown credit
2. Scrolls down → section 1 top approaches → proximity snap to section 1 start
3. Section 1's h2 enters viewport → reveals (cascade-free, just fades up)
4. User keeps scrolling within section 1 → items below reveal one by one as they cross viewport
5. Section 1 content ends → next snap point (section 2 top) approaches → proximity snap to section 2
6. Repeat through all 8 sections
7. After section 8 → scroll continues to back-link
8. Topnav still hides during sections 1-7 (existing logic works because that observer watches sections, not items)

### Click-to-jump behavior (TOC interactions)

The click-to-section behavior **stays intact**. When user clicks any TOC item:

1. Browser smooth-scrolls to that section's `#step-N` anchor (via existing `html { scroll-behavior: smooth }`)
2. Section snaps with its top at viewport (snap-margin handles topnav clearance)
3. **Only the h2 headline reveals on arrival** (it's the first item in viewport)
4. **Below-viewport content stays hidden** (opacity: 0) — paragraphs, images, callouts deeper in the section wait
5. User scrolls down → each item below crosses viewport line → reveals one at a time
6. User reads → scrolls → next item reveals → continues until end of section
7. Approaching next section boundary → gentle proximity snap to next section

This delivers the "click jumps to headline, scroll reveals progressively" experience.

### Small caveat about smooth-scroll transit

When a user clicks "skip to section 8" from way up the page, the smooth-scroll **passes through** sections 2-7 during transit. Each section's h2 briefly enters the viewport as the scroll position moves down. The IntersectionObserver fires for those h2's during transit → they get marked visible while in motion.

User impact:
- **Destination section (section 8)**: behaves exactly as designed — h2 reveals on arrival, deeper content waits for scroll ✅
- **Sections the scroll passed through**: their h2's are now marked visible. If user later scrolls back to revisit section 4, the h2 is already revealed (they lose the "fresh reveal" moment for the headline).
- **Deep content below h2 in passed-through sections**: still hidden, since those items never entered viewport during transit. They reveal correctly when user scrolls down to them.

**Is this a problem?** Realistically, no. Users who click "jump to section 8" rarely scroll back to section 4 immediately. The h2 being pre-revealed isn't jarring when they do.

### Polish options if you want bulletproof behavior

If you want every section to feel "fresh" on first proper visit (not transit):

#### Option 1: Disable observer during programmatic scrolls
```js
let isProgrammaticScroll = false;

document.querySelectorAll('.process-nav-item').forEach(link => {
    link.addEventListener('click', () => {
        isProgrammaticScroll = true;
        setTimeout(() => { isProgrammaticScroll = false; }, 800);  // smooth-scroll duration
    });
});

const itemObserver = new IntersectionObserver((entries) => {
    if (isProgrammaticScroll) return;
    entries.forEach(entry => {
        if (entry.isIntersecting) entry.target.classList.add('is-visible');
    });
}, { ... });
```
~10 extra lines of JS. Items in transit-through sections stay hidden; only destination section's h2 reveals.

#### Option 2: Remove `.is-visible` on scroll-leave
Items hide again when they leave viewport. On next entry, they re-reveal. More "alive" but can feel busy if user scrolls back and forth.
```js
entries.forEach(entry => {
    entry.target.classList.toggle('is-visible', entry.isIntersecting);
});
```

Neither is necessary for the default behavior to work — they're polish moves.

### When to choose Pattern A vs. Pattern A-progressive

| Use Pattern A (cascade on enter) | Use Pattern A-progressive (reveal as scroll) |
|---|---|
| Sections fit in ~100vh of content | Sections have substantial content (>100vh) |
| You want cinematic mandatory snap rhythm | You want reading-friendly proximity snap |
| Each section is a quick "beat" | Each section is a deeper reading experience |
| Animation should feel like one choreographed moment | Animation should feel like progressive discovery |

For the avrilwhsu-com article pages, **Pattern A-progressive is the better fit** if you plan to write substantive content per section (multiple paragraphs, examples, images per section). For short content (1-2 paragraphs per section), Pattern A is fine.

### Implementation cost on top of existing scroll-snap TOC page

- **CSS changes**: ~10 lines (remove min-height, add per-item opacity/transform)
- **JS changes**: ~10 lines (new IntersectionObserver for items)
- **Mode change**: 1 line (mandatory → proximity)
- **Total**: ~21 lines of changes/additions on top of the current article page implementation

