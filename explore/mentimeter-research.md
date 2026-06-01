# Mentimeter — Research & Implementation Notes

**Use case**: Live audience poll for a high-schooler presentation. Students scan a QR code on their phones, type open-ended answers, and see each other's responses appear anonymously and in real time on a webpage embedded in avrilwhsu.com.

**Captured**: research session, 2026-05.
**Sources**: mentimeter.com/features, mentimeter.com/plans (pricing tables JS-rendered — couldn't read directly; details marked "from baseline knowledge" should be re-verified on the live site before committing).

---

## What Mentimeter is

A SaaS live-polling tool. Presenter creates questions in a slide-deck UI; audience joins via menti.com with a 6-digit code or QR scan and types answers from their phone. Answers appear live on the presenter's screen in real time. Most popular question types for open-ended audience input: **Word Cloud** (answers visualized as a tag cloud, more frequent words grow larger) and **Open Ended** (answers stream in as a list).

Used heavily in education, conferences, and corporate training. Direct competitors: Slido, AhaSlides, Poll Everywhere, Wooclap, Vevox.

---

## Account requirements

| Role | Account needed? | What they do |
|---|---|---|
| **Presenter (Avril)** | Yes — free signup with email, no credit card | Builds the poll deck, runs the live session |
| **Students (audience)** | **No account needed** | Go to menti.com → type the 6-digit code (or scan QR) → type their answer → submit. Anonymous by default. No app, no email, no signup. |

This frictionless audience side is universal across all major live-polling tools (Slido, AhaSlides, Poll Everywhere). It's the entire point of the category.

---

## Free tier — what we know

**Confirmed from features page**:
- ✅ Word cloud question type available
- ✅ Open Q&A question type available
- ✅ Real-time anonymous responses
- ✅ AI grouping (clusters similar student responses into themes — useful for sorting open-ended answers)

**From baseline knowledge (verify before committing — pricing/limits change)**:
- 🟡 Free tier historically capped at ~**2 question slides per presentation** — very restrictive if your presentation has multiple polls
- 🟡 Free tier may show a Mentimeter logo/watermark on the presenter view
- 🟡 Paid Pro plan starts ~$12–15/month (USD)
- 🟡 No hard cap on simultaneous audience members on free tier last time I checked, but verify if your class is >50

**Verify these by**:
1. Signing up (free, no credit card) and trying to add a 3rd question slide to a presentation.
2. Looking at the "Plans" comparison table inside their app (more accurate than the public pricing page).

---

## The big embedding caveat ⚠️

**Mentimeter's free tier historically does NOT allow iframe embedding of the live presenter view into external websites.** Embedding has been a paid Pro feature.

What this means for the Flask site:
- ✅ You can always project the Mentimeter presenter view live during the event (just open mentimeter.com on your laptop).
- ❌ You may not be able to `<iframe>` the live results into a page on avrilwhsu.com on free tier.

**Three workarounds if embedding is paywalled:**
1. **Pay for one month of Pro** (~$12) just for the month of your event — cheapest if Mentimeter is non-negotiable.
2. **Switch to Slido or AhaSlides** — both include iframe embedding in their free tiers. Students don't know or care which platform is behind the QR — they just scan and type.
3. **Skip the embed entirely** — just project the Mentimeter presenter view directly during the presentation, and link to it from your site rather than embedding. Less integrated but free and simple.

**How to verify whether free tier embeds**: in your Mentimeter presentation, click Share/Embed. If you see iframe code copy-paste available, free tier works. If it's behind a Pro paywall prompt, you'll have to pick a workaround.

---

## Implementation on this Flask site (if embed works)

### Step 1 — Mentimeter setup (one-time, ~10 min)
1. Sign up at https://mentimeter.com.
2. Create a new presentation.
3. Add a question slide. For high-schoolers, **Word Cloud** is the most engaging visual; **Open Ended** is best for longer text answers.
4. Write the question (e.g., "What's the one thing about AI that scares you most?").
5. **Turn on moderation** in slide settings. Critical for anonymous teenagers — lets you approve answers before they appear on screen, prevents inappropriate responses from displaying live.
6. Click Present. Note the **6-digit code** on screen and the **presentation ID** in the URL: `https://www.mentimeter.com/app/presentation/[THIS-ID]/...`

### Step 2 — Flask route

Add to [app.py](../app.py):

```python
@app.route("/presentation")
def presentation():
    return render_template("presentation.html")
```

### Step 3 — Template

Create `templates/presentation.html`:

```html
{% extends "base.html" %}
{% block title %}Live Poll{% endblock %}
{% block content %}
<section class="presentation">
    <p class="join-instructions">
        Join at <strong>menti.com</strong> with code <strong>12 34 56</strong>
    </p>
    <iframe
        src="https://www.mentimeter.com/app/presentation/[YOUR-PRESENTATION-ID]/embed"
        width="100%"
        height="700"
        frameborder="0"
        allowfullscreen>
    </iframe>
</section>
{% endblock %}
```

### Step 4 — Minimal CSS

Append to [static/style.css](../static/style.css):

```css
.presentation {
    max-width: 1000px;
    margin: 2rem auto;
    padding: 2rem 1rem;
}
.join-instructions {
    text-align: center;
    font-size: 1.25rem;
    margin-bottom: 1.5rem;
}
```

### Step 5 — Test before the event
1. Visit `http://127.0.0.1:5001/presentation` in browser.
2. Open phone, go to menti.com, type the code, submit a test answer.
3. Watch the iframe update with the answer in real time.
4. If real-time sync works → ready for go-live.

That's the whole implementation on the Flask side. Mentimeter handles all the WebSocket / real-time complexity. Your site is just an iframe host.

---

## Gotchas — read before you commit

1. **Free tier embedding is the make-or-break issue** — verify FIRST. Everything else is secondary.
2. **Moderation must be turned on** for anonymous student input. Skipping this risks inappropriate answers appearing live on screen during your high schooler presentation. Non-negotiable.
3. **Free tier branding watermark** — Mentimeter logo may appear on the presenter view in free tier. Cosmetic but worth knowing for a polished feel.
4. **Audience cap** — free tier should handle typical classroom sizes (≤50), but verify if presenting to a large assembly.
5. **iframe + mobile** — embedded iframes can be janky on phones. Less critical here since students watch the projector, not their phones, after submitting answers.
6. **Real-time latency** — Mentimeter usually <2 seconds, but during peak event times can lag. Test with the actual venue WiFi if you can.
7. **Backup plan** — always have the direct Mentimeter URL ready in case the embed glitches during the event. Open it in another browser tab as a fallback.

---

## Alternatives if Mentimeter doesn't work out

Same use case (QR scan → type answer → anonymous live display), free embed:

| Tool | Free embed? | Free tier audience cap | Notes |
|---|---|---|---|
| **Slido** | ✅ Yes (first-class embed feature) | ~100 participants | Cisco-owned, most stable. Strong for Q&A. |
| **AhaSlides** | ✅ Yes | Most generous free tier in the category | Best zero-cost option. Educator-friendly. |
| **Poll Everywhere** | 🟡 Limited | ~40 free | Education-focused, K-12 plans exist. |
| **Mentimeter** | ❌ Pro tier required (verify) | Verify per-question limits | Cleanest UI; students recognize it. |

**My recommendation** (from research session):
- If brand-loyal to Mentimeter and OK paying ~$12 for one month: **Mentimeter Pro**.
- If avoiding any cost: **Slido** (most reliable) or **AhaSlides** (largest free tier).

---

## What I'd test next

When you're ready, the fastest path is:
1. Sign up for Mentimeter free.
2. Build a one-slide test poll.
3. Open the Share/Embed dialog and look at it.
4. If embed iframe is unlocked → proceed with the Flask implementation above.
5. If paywalled → spend 5 minutes on Slido instead (same flow), and only revisit Mentimeter if Slido doesn't meet a specific need.

15 minutes to a definitive answer.

---

## Related notes

- For the page-level scroll/animation choices on your high schooler presentation (above-the-fold hook, scroll choreography, etc.), see [anthropic-project-deal-effects.md](anthropic-project-deal-effects.md) in this same folder.
- The live poll section is one part of the broader presentation — typically lands mid-page after the hook, before the call-to-action.

---

## How to actually run Mentimeter on free tier with a webpage (the two-tab pattern)

**Context**: After running the research, the practical question became — if Mentimeter free tier blocks iframe embedding, how do you actually use Mentimeter alongside your webpage during a live event AND preserve the results afterward? The answer is the **two-tab pattern**, which is what experienced conference presenters do regardless of platform.

### During the event — two browser tabs on your laptop

| Tab | URL | What it shows | When to project |
|---|---|---|---|
| **Tab 1: Your webpage** | `http://127.0.0.1:5001/[poll-page-route]` | The poll question + big QR code + 6-digit join code. NOT the live results. | When asking the audience to vote |
| **Tab 2: Mentimeter presenter view** | `https://www.mentimeter.com/app/presentation/[ID]/...` | The live word cloud growing as votes come in | When showing results to the room |

You **toggle between the two tabs on the projector** at the right moments in your talk:
1. Open Tab 1 → audience scans QR, goes to menti.com, votes from their phones
2. After ~30 seconds of voting, switch to Tab 2 → audience sees the live word cloud
3. Optionally switch back to Tab 1 if you want more votes

### Why this is better than iframe embedding (even if you had Pro)

- **No iframe weirdness** at showtime — iframes can be flaky on venue Wi-Fi, have weird scroll behavior, or fail to load
- **You control the timing** — present the question first, let votes accumulate, THEN reveal results. Iframe embed shows everything at once.
- **Cleaner presenter experience** — Mentimeter's full-screen presenter view is designed for this, with controls for advancing slides
- **Universal across tools** — works the same on Slido, AhaSlides, Poll Everywhere, etc.

### After the event — three options for the permanent archive

To preserve the results on your webpage so future visitors can see what your audience said:

#### Option 1: Screenshot the final word cloud (5 min, recommended for one-off events)

1. With the final word cloud filled in on the Mentimeter tab, **Cmd+Shift+4** (Mac) → drag to select the word cloud area
2. Save the image to `static/` (e.g. `static/poll-results-2026-06.png`)
3. Add to your webpage:
   ```html
   <section>
       <h2>Audience word cloud</h2>
       <p>What scared the audience most about AI:</p>
       <img src="{{ url_for('static', filename='poll-results-2026-06.png') }}"
            alt="Word cloud of audience responses">
       <p class="meta">Live poll · Georgetown AI Academy Summer 2026 · 47 responses</p>
   </section>
   ```

**Pros**: Trivial. No JS, no library, no Mentimeter dependency after event ends. Matches Mentimeter's visual style exactly.
**Cons**: Static image (text not selectable, doesn't scale crisply on retina without a high-res screenshot).

#### Option 2: Rebuild as native HTML/CSS (30 min, recommended for portfolio polish)

Anthropic-style move (see [anthropic-project-deal-effects.md](anthropic-project-deal-effects.md) Section 8). Selectable text, on-brand styling, accessible.

1. In Mentimeter, **Export results** → CSV. Gives you word + count pairs.
2. Build the word cloud in HTML+CSS — each word's font-size set proportional to its count:
   ```html
   <div class="word-cloud">
     <span style="font-size: 3.5rem;">automation</span>
     <span style="font-size: 3rem;">jobs</span>
     <span style="font-size: 2.5rem;">misinformation</span>
     <!-- ... -->
   </div>
   ```
3. Style with `display: flex; flex-wrap: wrap; gap: 1rem; justify-content: center;` plus per-word color/weight variation.

**Pros**: Selectable text, SEO-friendly, scales crisply, on-brand styling, accessible to screen readers, no image dependencies.
**Cons**: 30 min vs. 5 min. Requires manual rebuild from CSV.

**JS alternative**: use `wordcloud2.js` (https://github.com/timdream/wordcloud2.js, ~30KB, no deps) — pass it the word/count array, it renders a canvas. More dynamic but adds a dependency.

#### Option 3: Mentimeter "shareable results" URL (if available on free tier)

1. In Mentimeter presentation, check **Share → Share results** for a public URL like `https://www.mentimeter.com/s/...`
2. If available, either:
   - **Link out**: button on your webpage that opens it in a new tab. Free, no embed.
   - **Iframe**: usually blocked on free tier by `X-Frame-Options`, but worth checking.

**Pros**: Auto-updates if you re-run the poll.
**Cons**: Depends on Mentimeter staying up and keeping your presentation live. Link could break if you delete the presentation.

### Recommended flow for the Georgetown session

```
Pre-event (1 day before):
  □  Build the Mentimeter poll with Word Cloud question type
  □  Turn on response moderation (CRITICAL for anonymous audience)
  □  Build the /live-poll Flask route with QR code + join code on the page
  □  Generate QR code for menti.com voting URL (free tools: qr-code-generator.com)
  □  Save QR as static/menti-qr.png

Day-of:
  □  Open Tab 1 (your webpage) and Tab 2 (Mentimeter presenter view) BEFORE going on stage
  □  Test both tabs work on venue Wi-Fi
  □  Have your phone hotspot ready as backup
  □  During talk: project Tab 1 → audience votes → switch to Tab 2 → reveal results

Post-event (within 24 hours):
  □  Screenshot the final word cloud from Mentimeter
  □  Save as static/poll-results-[date].png
  □  Add results section to the article page or create /event-archive
  □  Push to GitHub → permanent record viewable by future visitors
```

### Why the two-tab + screenshot pattern is the right call here

For a **one-off speaking engagement** (Georgetown session, ~30-50 audience members, single event), the two-tab pattern with a post-event screenshot:

- ✅ Costs $0 (no Mentimeter Pro needed)
- ✅ Is more reliable than iframe embeds at the venue
- ✅ Preserves a clean visual artifact for portfolio/archive
- ✅ Standard practice for conference speakers regardless of tool

You'd only want iframe embedding if you were running **recurring live polls on a public webpage with audience interaction expected from non-event visitors** (e.g. a continuous Q&A widget on a contact page). That's not the Georgetown use case.

---

## Business case analysis — should Avril pay for annual basic plan?

**Context**: Mentimeter's basic plan is annual-only (~$96–144/year, no monthly option). Before committing, this section maps out where Mentimeter genuinely earns its place for a solo coaching business — vs. where other tools win.

### Three zones of value for a coaching business

#### 🟢 HIGH value — Mentimeter shines here

**1. Speaking engagements (Georgetown + future events)**
- Direct application of current use case
- If Avril does 3-4 speaking gigs per year (conferences, panels, podcast guest appearances with live polls, corporate talks), annual basic plan pays for itself
- Why Mentimeter specifically: audiences recognize it from teachers, frictionless join via menti.com, anonymous responses encourage honesty

**2. Free intro webinars / lead-magnet events**
- The textbook coaching/consulting use of Mentimeter
- Format: 60-min "AI Career Planning Workshop" as free top-of-funnel event
  - **Opening poll**: "Where are you in your AI journey?" → segments audience for personalized talk
  - **Mid-event word cloud**: "What's your biggest blocker?" → makes audience feel heard
  - **Closing pulse**: "How confident do you feel now vs. when we started?" → measurable proof of value
- Probably the highest-ROI single application for Avril's business

**3. Group coaching cohorts (if launched)**
- 6-week AI Career Reinvention Cohort or similar
- Weekly session check-in pulse polls, word cloud reflections, retention quizzes, open Q&A queue
- Mentimeter is THE tool for cohort-based courses (Lambda School, Reforge, Maven all use it)

#### 🟡 MEDIUM value — works, but consider alternatives

**4. Newsletter reader polls**
- Use case: Quarterly "What should I write about next?" embedded in Substack issue
- Mentimeter limit: requires navigating away from email to menti.com — low response rates
- **Better tool**: Substack's native poll feature (single-click in-email, much higher response rate)

**5. Permanent embedded poll on website**
- Use case: Continuous "Audience pulse" word cloud on About page
- Mentimeter limit: iframe embed = Pro tier (not basic). Uncurated = spam risk
- **Better tool**: hardcoded HTML/CSS word cloud (see [anthropic-project-deal-effects.md](anthropic-project-deal-effects.md) Section 8) with curated themes. More polished, totally free.

#### 🔴 LOW value — wrong tool

**6. Lead capture / discovery call forms**
- Mentimeter is designed for anonymous group responses, not 1:1 lead capture
- **Right tool**: Typeform (~$25/mo), Tally (free, generous), or Google Forms (free)

**7. Detailed client feedback after sessions**
- Too lightweight, no analytics dashboard for tracking over time
- **Right tool**: Typeform, Tally, or direct email questions

### Creative use cases specifically for Avril's brand positioning

These fit the "industry SME + content creator + coach" positioning:

**8. "Voices from my talks" archive page on the site**
- A `/voices` or `/audience-voices` page collecting screenshots of word clouds from every event Avril speaks at
- Each entry: event name, date, the word cloud screenshot, maybe a one-line takeaway
- **Why it works**: powerful social proof. Anonymous, raw, in-the-moment audience sentiment feels more authentic than curated testimonials.
- **Cost**: $0 ongoing (static images, like Section 8 of project-deal-effects)

**9. "Pulse check" before a paid offering**
- Before launching a new paid program, run a free "30-min AI Career Reality Check" webinar with Mentimeter polls throughout
- The audience's poll responses double as **market research for product-market fit** — what blockers show up most? What language do people use? Pricing test: "What would you pay for help solving this?"
- **Why it works**: validates the offer before building it. The pulse data informs sales page copy and pricing.

**10. Conference speaker positioning loop**
- After each speaking gig:
  1. Tweet/LinkedIn-post the word cloud image: "Spoke at Georgetown today. Here's what students said scared them most about AI. Some patterns I noticed..."
  2. Link back to the `/voices` archive on the site
  3. Use the dataset to inform the next talk's hook
- **Why it works**: every speaking gig generates a viral-able artifact PLUS content for the audience PLUS positioning material for the next gig. Compounding flywheel.

### Cost/benefit decision matrix

| Annual event frequency | Verdict |
|---|---|
| 1 event/year (just Georgetown) | ❌ Don't buy. Use free tier (2-question limit is fine for one session). |
| 2-3 events/year | 🟡 Maybe. ~$50/event — reasonable. |
| 4+ events/year | ✅ Buy. Pays off via professional polish + smoother workflow. |
| Cohort coaching launch | ✅ Buy regardless. One of the highest-ROI tools for cohort programs. |
| Plans for free webinars | ✅ Buy. Webinars are where Mentimeter shines for solopreneur coaches. |

### Important alternative to evaluate first

Before committing to Mentimeter's annual basic plan, **try Slido** (same use cases, free embed in iframe, more generous free tier). If Slido covers needs at $0, save ~$120/year. The audience-side experience is nearly identical.

### Final recommendation

- **For just the Georgetown event**: use Mentimeter free tier (or Slido free). Don't pay for annual basic for one gig.
- **If planning more speaking + at least one free webinar in next 12 months**: annual basic plan is worth it. Bundle with use cases #1, #2, #8, #9, #10.
- **The single highest-leverage use case**: a quarterly free intro webinar with live Mentimeter polls as a lead-gen tactic. That alone justifies the cost AND fits the industry SME positioning.
