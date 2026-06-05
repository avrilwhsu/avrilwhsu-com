# Decision: GSAP-Pinned Scroll Choreography for Section 1

**Context**: After researching how Anthropic's Project Deal page implements its "first block pinned, subsequent blocks reveal one by one" effect, decided to implement Option 1 (GSAP ScrollTrigger pin pattern) on the `/human-AI-collaboration-creativity` article page. See [anthropic-project-deal-effects.md](anthropic-project-deal-effects.md) Section 10 for the full pattern analysis.

**Decided**: 2026-06 (research + implementation session)
**Scope**: This article page only. Other pages remain zero-dependency.

---

## The decision in one sentence

Use GSAP ScrollTrigger (self-hosted) to pin section 1 of the article page in the viewport while user scrolls, scrubbing through a timeline of fade-in reveals for 6 content blocks.

## Why this approach over alternatives

| Option | Why not |
|---|---|
| Pure `position: sticky` (what we had before) | Other content scrolls UP past the sticky block. Doesn't match Anthropic's "stack-up" visual. |
| Vanilla JS pinned scroll (~80 lines) | More code to write/maintain. Harder to get smooth easing. |
| Stacking sticky (~10 lines CSS) | Stair-step look, not the smooth choreography of Anthropic. |
| **GSAP ScrollTrigger** ← chosen | Faithful Anthropic experience. Industry-standard for this pattern (Apple, Stripe, Linear). |

**Trade-off accepted**: ~115KB JS dependency on ONE page. Mitigated by self-hosting (no CDN reliance) and scoping to this page only via Flask template block.

---

## Implementation summary

### Files involved

| File | Role |
|---|---|
| [static/js/gsap.min.js](../static/js/gsap.min.js) | Core GSAP library, 72KB, self-hosted |
| [static/js/ScrollTrigger.min.js](../static/js/ScrollTrigger.min.js) | ScrollTrigger plugin, 43KB, self-hosted |
| [templates/base.html](../templates/base.html) | Added `{% block extra_scripts %}{% endblock %}` before `</body>` |
| [templates/human_ai_collaboration_creativity.html](../templates/human_ai_collaboration_creativity.html) | Restructured section 1 markup; overrode `extra_scripts` block with GSAP code; kept the existing section/TOC IntersectionObserver for non-pinned sections |
| [static/style.css](../static/style.css) | Added `.pinned-section`, `.pinned-content`, `.pinned-intro`, `.reveal-block` rules. Removed `html:has(.process) { scroll-snap-type }` to prevent snap-vs-GSAP conflict. |

### How scoping works (dependency only loads on one page)

In `base.html`:
```html
{% block extra_scripts %}{% endblock %}
```

In `human_ai_collaboration_creativity.html`:
```html
{% block extra_scripts %}
<script src="{{ url_for('static', filename='js/gsap.min.js') }}"></script>
<script src="{{ url_for('static', filename='js/ScrollTrigger.min.js') }}"></script>
<script>
    /* GSAP setup */
</script>
{% endblock %}
```

Other pages don't override `extra_scripts` → they get nothing → GSAP doesn't load there. Home page, substack, contact all stay zero-dependency.

---

## Section 1 markup labels

```html
<section id="step-1" class="process-section pinned-section">
    <div class="pinned-content">
        <div class="pinned-intro">           ← Always visible, NOT animated
            <h2>Hi, I'm Avril.</h2>
            <p>📍Silicon Valley<br>💼 Human-centered AI at Dell's Chief AI Office.</p>
        </div>
        <p class="reveal-block">...</p>      ← Block index 0
        <p class="reveal-block">...</p>      ← Block index 1
        <p class="reveal-block">...</p>      ← Block index 2
        <p class="reveal-block">...</p>      ← Block index 3
        <p class="reveal-block">...</p>      ← Block index 4
        <p class="reveal-block">...</p>      ← Block index 5
    </div>
</section>
```

**Naming convention**:
- `.pinned-section` — the entire section (what GSAP pins)
- `.pinned-content` — inner wrapper for layout
- `.pinned-intro` — the always-visible intro block (h2 + location/role)
- `.reveal-block` — each of the 6 fading-in blocks (selected in JS by `document.querySelectorAll('.reveal-block')`, order matches DOM order)

In JavaScript: accessed as `revealBlocks[0]`, `revealBlocks[1]`, etc.

---

## Block content + exact scroll timing

Pin range: `'+=200%'` → user scrolls 2 viewport heights (~100rem on typical desktop) through the pinned section. Total timeline length: 8.5 units. Each `<p>` block animates `opacity: 0 → 1` and `y: 20 → 0` over `duration: 1` timeline unit.

| Block | Content | Timeline start–end | % of pin range | Scroll position |
|---|---|---|---|---|
| **Intro** | "Hi, I'm Avril." + 📍/💼 | — | 0%–100% always visible | always visible |
| **Block 0** | 🚀 My Journey: 4 tech waves. Each one, pioneer work. 5 shapes of 🎯 | 1.5 → 2.5 | 17.6%–29.4% | 35%–59% of first viewport scroll |
| **Block 1** | 1. Physical → Digital: 18 international awards · bringing emerging tech into connected products | 2.7 → 3.7 | 31.8%–43.5% | 64%–87% of first viewport scroll |
| **Block 2** | 2. Mobile: helped grow an early-stage startup to acquisition | 3.9 → 4.9 | 45.9%–57.6% | 92% first viewport – 15% second viewport |
| **Block 3** | 3. Cloud: won a Fortune 50 innovation award · featured alongside the CEO | 5.1 → 6.1 | 60.0%–71.8% | 20%–44% of second viewport scroll |
| **Block 4** | 4. AI: inventor on first batch of generative AI patents granted by USPTO · commercialized | 6.3 → 7.3 | 74.1%–85.9% | 48%–72% of second viewport scroll |
| **Block 5** | One thing made all of this possible — and will keep working through whatever comes next: creativity. | 7.5 → 8.5 | 88.2%–100% | 76%–100% of second viewport scroll |

---

## How "scrub" creates the smooth feel

```js
scrollTrigger: {
    trigger: pinnedSection,
    start: 'top top',      // pin engages when section's top reaches viewport top
    end: '+=200%',         // pin holds for 200% of viewport scroll (~2 screens worth)
    pin: true,             // actually pin the section in viewport
    scrub: 1,              // 1 second smoothing — animation lags behind scroll by 1s
    anticipatePin: 1       // pre-render fix for smoother engagement
}
```

**`scrub: 1`**: as you scroll, GSAP smoothly catches up to your scroll position over 1 second. Fast scrolls don't snap instantly — they ease toward the destination over ~1 second. This is the "buttery" feel.

**Each block's animation definition**:
```js
tl.fromTo(block,
    { opacity: 0, y: 20 },              // initial state: invisible, 20px below
    { opacity: 1, y: 0, duration: 1 },  // target state: fully visible, in place
    1.5 + i * 1.2                       // when to START in the timeline
);
```

`1.5` = initial offset before any block reveals (so user sees intro for a bit before reveals start).
`1.2` = gap between each block's start.

---

## Full scroll journey through section 1

| Scroll position | What user sees |
|---|---|
| Hero | "You + AI →" cover with Georgetown credit |
| Hero ends, section 1 starts | Section 1 pins via GSAP. Only intro visible. TOC turns black on "1 Quick Intro". Topnav hides. |
| 0%–17% pin scroll | Pinned. Only intro visible. (User scrolls but page isn't moving — scroll input is "consumed" by pin) |
| 17%–29% | "🚀 My Journey" fades in & slides up |
| 31%–43% | "1. Physical → Digital" fades in & slides up |
| 45%–57% | "2. Mobile" fades in & slides up |
| 60%–71% | "3. Cloud" fades in & slides up |
| 74%–85% | "4. AI" fades in & slides up |
| 88%–100% | "One thing made all of this possible…" fades in & slides up |
| Pin releases | Section 1 unpins, scrolls out. Section 2 enters from below. TOC switches to "2". Topnav stays hidden (still not last section). |

---

## TOC active state + topnav visibility (during pin)

Standard IntersectionObserver doesn't fire reliably when a section is GSAP-pinned (the section's effective viewport position is decoupled from its DOM position). So we use GSAP's own callbacks for section 1:

```js
scrollTrigger: {
    // ... pin config above
    onEnter: () => setStep1Active(true),
    onEnterBack: () => setStep1Active(true),
    onLeave: () => setStep1Active(false),
    onLeaveBack: () => setStep1Active(false)
}
```

Where `setStep1Active(active)`:
- Toggles `.active` class on TOC item 1
- Toggles `.topnav-hidden` on topnav (hides during section 1)

Sections 2–8 still use the original IntersectionObserver pattern (no GSAP needed for them).

---

## Where to tune things (cheat sheet)

| To change… | Edit this | In file |
|---|---|---|
| Block 0's start delay | `1.5` in `1.5 + i * 1.2` | [templates/human_ai_collaboration_creativity.html](../templates/human_ai_collaboration_creativity.html) |
| Gap between blocks | `1.2` in `1.5 + i * 1.2` | same |
| Fade-in duration of each block | `duration: 1` | same |
| Total pin scroll length | `'+=200%'` | same |
| Scrub smoothing | `scrub: 1` (higher = laggier; 2-3 = more dramatic slow follow) | same |
| Block content | The `<p class="reveal-block">…</p>` text | same |
| Initial vertical offset of blocks | `y: 20` in `fromTo` | same |

---

## Risks + mitigations

### Risk 1: GSAP library breaks or changes API
- **Mitigation**: self-hosted in [static/js/](../static/js/). The version (3.12.5) is frozen forever. No CDN dependency.

### Risk 2: Scroll-snap conflict broke other sections
- **Mitigation**: removed `html:has(.process) { scroll-snap-type }` rule. Sections 2-8 now scroll normally without snap. Behavior preserved via the existing IntersectionObserver-based reveal pattern.

### Risk 3: Mobile experience may degrade (GSAP pin on small screens)
- **To verify**: test on phone. If pin behavior is bad on mobile, can disable GSAP at small viewports and fall back to natural scroll.

### Risk 4: ~115KB extra JS on this page
- **Acceptable**: this is a one-shot experience page (Georgetown session), not a frequently-visited landing page. Page load is still fast.

### Risk 5: Page no longer works offline IF GSAP files fail to load
- **Mitigation**: files are self-hosted in static/. They only fail if user's connection drops mid-page-load AND the JS files weren't already cached. Browser usually caches them after first visit.

---

## Future considerations

### If we want this on other article pages (Cards 2, 3 destinations)
- Reuse the same `.pinned-section` markup pattern
- Reuse the same GSAP setup (just point at new `.pinned-section` and `.reveal-block` elements)
- No additional library loading — GSAP only loads per-page

### If we want to simplify back to sticky
- Remove the `extra_scripts` block on the article page
- Restore `position: sticky` on `.pinned-intro`
- Re-add the `html:has(.process) { scroll-snap-type }` rule
- ~20 minutes to revert

### If Anthropic-style reveals are desired site-wide
- Move GSAP loading to base.html (becomes a global dependency)
- Apply `.pinned-section` pattern to other sections
- Page weight goes up across the site — only worth it if multiple pages need this pattern

---

## Related research files

- [anthropic-project-deal-effects.md](anthropic-project-deal-effects.md) — full research on Anthropic's patterns (Section 10 covers the pinned scroll specifically)
- [mentimeter-research.md](mentimeter-research.md) — separate research on live-polling for the Georgetown session

---

## Quick verification commands

```bash
# Verify GSAP files are served
curl -sI http://127.0.0.1:5001/static/js/gsap.min.js | head -1
curl -sI http://127.0.0.1:5001/static/js/ScrollTrigger.min.js | head -1

# Verify the article page still loads
curl -sI http://127.0.0.1:5001/human-AI-collaboration-creativity | head -1
```

All should return `HTTP/1.1 200 OK`.
