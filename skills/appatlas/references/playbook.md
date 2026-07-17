# Appwalk playbook — templates, workflows, snippets

Battle-tested on a full crawl of a live SaaS (Promptwatch, 2026-07: 13 sections, 280+ screenshots, 12 subagents). Adapt names, keep the mechanics.

## AGENT-BRIEFING.md template

Write this file at the crawl root during recon; every crawl agent reads it FIRST. Contents:

1. **Environment**: app + one-line description; account/org/project slugs; base URLs (project pages vs org settings often differ — settings areas are frequently exempt from paywalls); the ONE Chrome tab ID to use ("do NOT create tabs; never touch tab <other> — user is using it"); the single ToolSearch line loading navigate, computer, read_page, get_page_text, javascript_tool, find, browser_batch (+ gif_creator only if that section has a key moment).
2. **Plan/quota status**: current tier, metered budgets (e.g. "responses 21/6,000"), what's gated, whether a trial is active, "do NOT touch billing/plan controls".
3. **Recovery**: paywall-overlay removal snippet (below) + when to use; blank-shell recovery (`location.reload()` + scroll, 5–8s hydration waits); "if frozen after 2–3 retries, note it in spec and move on — orchestrator resolves".
4. **Capture workflow** (below), hard rules (from SKILL.md), GIF policy (key moments only).
5. **Deliverable**: spec.md format (below) + "final message = 5–10 line summary: what the section does, real vs empty/gated data, surprises, files written".

## Per-page capture workflow

1. `navigate` → wait 3–5s (SPAs hydrate lazily) → recovery snippet if needed.
2. Screenshot `save_to_disk: true` → `cp` temp path → `<section>/screenshots/<page>--<state>.jpg` (kebab-case; prefix by page so the index tree can filter by prefix).
3. `get_page_text` for content; `read_page` filter=interactive to enumerate controls. CAUTION: response-heavy pages can dump 50K+ chars — skip full page text there, rely on screenshots.
4. Scroll the whole page in steps, screenshot each new viewport of content.
5. Exercise reversible UI: every sub-tab, dropdown (screenshot open, Escape), filter, date-range, expander, row-detail modal. Toggled settings get reverted immediately.
6. Batch actions with `browser_batch` (click→wait→screenshot sequences); coordinates refer to the screenshot BEFORE the batch.

## spec.md format

```
# <Section>
Route(s): <URLs>
Purpose: <paragraph>

## Page: <name> (<route>)
Layout: <regions, widgets>
Controls & behavior: <every control: what it does, options observed>
States: <empty/sample/gated/error — quote gate wording verbatim>
Screenshots: <filename — one-line what it shows>
Notes: <quirks, API calls, surprises>
```

Modals/wizards that matter get their own `## Modal:` block. Mark inferences `[unverified]`.

## Paywall overlay removal (client-side gate, server still serves data)

Run via javascript_tool after navigation; re-run after client-side route changes. Do NOT run while a modal you're inspecting is open (it removes big modals indiscriminately):

```js
document.querySelectorAll('[role="dialog"]').forEach(e=>e.remove());
document.querySelectorAll('div').forEach(e=>{const s=getComputedStyle(e);
  if(s.position==='fixed'&&parseFloat(s.zIndex)>10&&e.offsetWidth>1000&&e.offsetHeight>500)e.remove()});
document.body.style.overflow='auto';document.body.style.pointerEvents='auto';
```

Ethics/scope: this is cosmetic removal of a nag overlay on an account the user owns, to document pages the server willingly returns. It does not bypass server-side authorization — genuinely gated features stay gated; document those.

## Trial/checkout handoff

Never enter card/payment data. When a trial unlocks real documentation depth: open the checkout in a SECOND tab, tell the user "complete this if you want full depth; $X verification, $Y/mo after trial — I'll keep crawling meanwhile", and continue on the free tier. When it activates (banner/quota flips), update the briefing (limits, gates) and re-verify previously gated sections. If the user says "cancel it after", add it to the README post-crawl checklist IMMEDIATELY — then do it via the app's Billing (screenshot every step of the retention funnel; it's spec material) and verify "will not renew / access until <date>" state.

## Demo data policy

Use a real brand/site the user owns as the monitored/imported subject — AI-analysis and data features populate meaningfully where lorem stays empty. Authorize consuming actions individually: "you MAY run exactly ONE <generation> with topic X" — never blanket permission. Onboarding auto-runs may start consuming metered quota with zero confirmation; note the meter reading in the briefing and after each section.

## Review + fix loop

- Reviewers get NO browser. Each: read spec.md fully; script-verify every referenced screenshot exists and every file is referenced; `Read` 3–5 images to verify the spec's claims (labels, counts, states); check format; flag cross-section contradictions. Output: findings file with severity (high=wrong info, medium=broken ref, low=style) + per-section coverage verdict.
- One fixer agent applies HIGH+MEDIUM (+cheap LOW) fixes and appends a "Fixes applied" log to each findings file. Orchestrator spot-checks the top findings landed, then rebuilds the index.
- Orchestrator resolves conflicts reviewers can't (e.g. you know a dropdown was changed after the screenshot — you are the ground truth; correct the spec yourself).

## Mobbin-style index (self-contained HTML)

Python builder pattern: walk `*/screenshots/*.jpg` → thumbnail via `sips -Z 700 -s format jpeg -s formatOptions 50` (≈25KB each; 280 thumbs ≈ 6–7MB, base64 ≈ +33%) → emit single HTML with:
- Hand-authored app-hierarchy tree (nav group → page → sub-tab → modal), each node = `{label, section, filename-prefix}` so it filters the gallery by prefix.
- Card grid (data-URI imgs, `loading="lazy"`), search box, section chips, click→lightbox, per-section spec text in a `<details>` panel (via embedded JSON).
- Token-level light/dark theming (`:root` vars + `prefers-color-scheme` + `data-theme` overrides).

Pitfalls that WILL bite:
- Specs quoted into a `<script>` block: escape `</` as `<\/` in every JSON payload or an embedded `</script>` (e.g. a setup snippet in a spec) kills the page script.
- Keep the template pure ASCII (json.dumps default escaping handles payloads; use `&mdash;`-style entities and CSS `\25B8` escapes in static text) — served-without-charset previews mojibake otherwise.
- `<details><summary><button>` trees: a button's click handler with stopPropagation blocks expansion — explicitly set `details.open = true` when selecting a group node.
- Smoke-test via `python3 -m http.server --directory <dir>` + real browser + console read BEFORE publishing. `node --check` the extracted script.
- Big GIFs: don't embed; keep in tree and send the best one directly to the user.

## Orchestrator bookkeeping

- README.md at crawl root = live index: status table (section | routes | ✅/🔄/⬜ + screenshot count), "what the app is" paragraph, known gates, post-crawl checklist (trial cancellation, accidental-mutation cleanup, publish, skill/report tasks). Update it on EVERY agent return — context compaction will eat your memory; the README is what survives.
- When a crawl agent dies mid-section (platform session limits): `ls` its section folder to see what survived, continue inline yourself, write `raw-notes-orchestrator.md` describing exactly what's done/remaining, then dispatch a finisher agent pointing at notes + existing screenshots (it can `Read` them) to complete and write the unified spec.
- Send agents corrections mid-run via SendMessage instead of respawning.

## Mobile lane specifics

- iOS: `xcrun simctl list`, `boot <udid>`, `install booted <path>.app`, `launch booted <bundle-id>`; screenshots `xcrun simctl io booted screenshot <p>.png`; video `xcrun simctl io booted recordVideo <p>.mov` (SIGINT to stop; `ffmpeg -vf "fps=10,scale=480:-1"` → gif); deep links `simctl openurl booted <scheme://…>`. Taps/swipes/text need **idb** (`idb ui tap x y`, `idb ui text "…"`) — verify installed during recon or flag setup blocker. Coordinates are POINTS; screenshots are PIXELS — divide by the device scale factor (2x/3x) before tapping.
- Android: `emulator -avd <name>`, `adb shell input tap x y` / `input text` / `input swipe`, `adb exec-out screencap -p > s.png`, `adb shell screenrecord /sdcard/f.mp4` (pull after).
- Sequential agents, same as web. Keep a `done-screens.md` checklist per section; on simulator crash: `simctl shutdown/boot`, reinstall, resume from checklist. Capture BOTH light/dark and notch/dynamic-island states only where the app itself changes behavior.

## Coverage audit (phase 3b) — how the gaps actually hide

Observed on the reference crawl: section agents covered 13/13 sections yet still missed a whole Reports page (PDF/CSV/Scheduled exports), the dashboard's Export-Report builder dialog, project-scoped API-key/Search-Console pages (duplicates of org-settings pages with different scope), the 9-step setup checklist contents, and the "Manage Topics" manager. Pattern: **gaps cluster in app chrome and nested dialogs, not in nav sections.**

Audit agent prompt core: build a deduplicated feature inventory from (1) nav + sub-tabs, (2) every button/CTA/toggle/filter the specs mention, (3) the pricing feature matrix (each row is a product feature), (4) API/MCP docs. Verdict each: WALKED (exercised + evidenced) / SHALLOW (exists in a screenshot, own UI never opened) / INTENTIONALLY SKIPPED (destructive/payment/OAuth/quota — note reason) / MISSED. "The spec says the button exists" = SHALLOW, not WALKED. Output: coverage-matrix.md + top-10 fillable gaps.

Orchestrator sweep checklist (browser): avatar menu (read hrefs via read_page — items often point to pages in NO sidebar), bell panel, ⌘K palette with a real query (note result grouping), every header action button's dialog (Generate/Export/Schedule), "Manage …" links inside filter dropdowns, setup/progress checklist popover, chat-widget launcher (open, don't message), and org-vs-project scoped route twins. Recapture formerly-empty dashboards (data latency).
