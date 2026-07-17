---
name: appatlas
description: Use when asked to walk/crawl/tear down/document an entire app end to end — every screen, sub-tab, setting, and flow — with screenshots, flow recordings, behavior specs, and a browsable index. Works for web apps (Chrome MCP) and iOS/Android apps (simulator/emulator). Triggers - "app walk", "document this app", "full walkthrough", "teardown", "crawl the app", "Mobbin-style index", competitor/product research on a live SaaS.
---

# AppAtlas — map every screen of any app

## Overview

You are the **orchestrator**: you resolve blockers, keep the index current, and dispatch Sonnet subagents to crawl and write. The product's UI surface (one Chrome tab group, one simulator) is a **single shared resource — crawl agents run strictly one at a time**; parallelism is for doc/review/fixer agents only. Read `references/playbook.md` in this skill directory before dispatching anything — it has the briefing template, capture workflows, recovery snippets, and index builder.

**Iron rule of parallelism:** at most ONE crawl agent per physical UI resource at a time. The Chrome tab group is one resource (Chrome MCP acts on the focused tab; parallel agents interleave clicks and freeze screenshot capture — "one tab per agent, 4–6 in parallel" does not work). Each simulator/emulator is its own resource. Distinct resources (e.g. the web lane and an iOS-simulator lane) MAY run as concurrent lanes, each with its own briefing; within a lane, strictly sequential.

## Phases

1. **Recon (orchestrator, inline)** — sign in/up, complete onboarding *capturing every step as spec material* (fields, defaults, dropdown options, validation, side effects). Fill realistic demo data (a real brand/site you own beats lorem — features populate). Map the full nav → write the section list, folder tree `NN-section/{spec.md,screenshots/}`, `README.md` index with a status table + post-crawl checklist, and `AGENT-BRIEFING.md` from the playbook template.
2. **Crawl (one Sonnet agent per section, sequential)** — each agent reads the briefing, owns one section, saves screenshots + writes `spec.md`, AND emits a structured record per screen into `<section>/screens.json` (`references/schema.md`) using the controlled tags in `references/taxonomy.md`. Reports a 5–10 line summary. Update the README row as each returns; dispatch the next.
3. **Review (parallel, no browser)** — 2+ QA agents split the sections: verify spec↔screenshot consistency (they must `Read` the image files), coverage vs the nav map, stale claims in README. Then one fixer agent applies findings and logs what it changed.
3c. **Enrich — semantic tagging + linking (one agent, no browser)** — normalizes every `screens.json` against the taxonomy (page types, flows, pattern tags) so the tag index is consistent, and resolves **cross-section links** (a dashboard CTA that jumps into another section, a menu item that opens a settings page) — these need the whole-atlas view, so no single crawl agent can author them. This is what turns the flat gallery into a navigable graph. See `references/schema.md` (two-phase authoring) + `references/taxonomy.md`.
3b. **Coverage audit (feature level)** — sections done ≠ features done. Run two probes together: (a) an audit agent (files only) builds a feature inventory from every control/CTA/tab the specs *mention* and verdicts each as WALKED / SHALLOW (visible but never opened) / INTENTIONALLY-SKIPPED (reason) / MISSED; (b) the orchestrator live-sweeps the app-chrome paths section agents structurally miss: the avatar/account menu (often the ONLY route to some pages), notification panel, command-palette results, per-widget config dialogs (report/export builders), "Manage X" managers inside filter dropdowns, setup-checklist popovers, and project-vs-org scoped duplicates of settings pages. Fill fillable gaps, fold into specs, rebuild the index. Also recheck data-latency: widgets "empty" during the crawl often populate hours later — recapture the populated dashboard before shipping.
4. **Index — the enhanced viewer** — run `references/build_atlas.py`, which consumes the `screens.json` records + thumbnails + specs and emits a self-contained HTML with FOUR surfaces, all data-driven (no hand-authoring): an **auto-built tree** (section → page → sub-tab → modal), a **Mobbin-style faceted tag rail** (page types / flows / patterns / states, with counts, filters across the whole atlas so it scales to many apps), a **per-screen structure panel** (page type, features, element inventory, states, tags) opened from any card, and a **Flows graph** (screens as nodes, the semantic `links` as typed edges, laid out left-to-right per flow). Compress thumbs first (~700px JPEG q50 → the builder base64-inlines them). Publish as an Artifact / GitHub Pages (private by default) when the user asked for a browsable index; smoke-test locally first (`python3 -m http.server`, real browser, read console). Generator + pitfalls in the playbook; a plain gallery-only builder is the fallback if `screens.json` wasn't produced.
5. **Close-out** — run the post-crawl checklist: cancel trials the user asked to stop (screenshot the cancellation funnel — it's spec material), undo accidental mutations, send key artifacts to the user.

## Hard rules (give these to every crawl agent)

- Load all Chrome MCP tools in ONE ToolSearch call. Use only the tab ID in the briefing; never create tabs.
- Screenshot with `save_to_disk: true`, then `cp` the returned temp path into the section folder as `page--state.jpg`. A screenshot not copied to the tree is lost.
- Never: destructive controls, sending invites/messages, OAuth connects, plan/billing buttons, entering payment credentials (hand checkouts to the user — see playbook), actions that consume metered quota unless the orchestrator's dispatch prompt explicitly authorizes that one action.
- Open create-wizards, fill demo values, screenshot every step, then **cancel without submitting** — unless explicitly authorized to submit one.
- Gated/locked/upgrade states are spec material: capture the exact wording, don't treat as failure.
- Flow recordings for **key product moments only** (one per section at most); ordinary page tours get stills. Web: `gif_creator`. Mobile: `simctl io recordVideo` / `adb screenrecord`.
- Emit one `screens.json` record per screenshot as you go (`references/schema.md`): id/hierarchy/pageType/flows/features/elements/states/tags/summary + the intra-section `links` you can observe directly (tab→tab, button→modal, list→detail). Cross-section links are the enrich pass's job, not yours.

## Blocker playbook (orchestrator jobs)

| Blocker | Move |
|---|---|
| Paywall modal blocks pages | Often client-side only — remove overlay via JS and keep crawling; the server still serves data (playbook snippet) |
| Trial/checkout needs a card | Open checkout in a SECOND tab for the user, tell them, keep crawling the free tier meanwhile; re-verify gated sections after they complete it |
| Blank unhydrated shell after client-side nav | `location.reload()` + small scroll, wait 5–8s |
| Screenshot CDP timeout "renderer frozen" | New tab; if it spreads to all tabs, ask the user to restart Chrome, then re-verify capture before dispatching |
| Subagent dies mid-section (session limits) | Check what files it saved, write raw-notes of your own inline continuation, dispatch a finisher agent pointing at both |
| Product quota burning in background (crons) | Note the meter in the briefing; forbid prompt-run/refresh actions by default |

## Common mistakes

- Parallel browser agents (see iron rule). | Screenshots viewed but never saved to disk. | Onboarding rushed through instead of captured. | README/index left stale as sections finish. | Specs claiming "not captured" after a retake happened — reviewers catch this only if they Read images. | Recording GIFs for everything. | Embedding raw specs/HTML in the index without escaping `</script>` and forcing ASCII-safe payloads (`json.dumps` default) — one stray sequence kills the whole page script.

## Mobile lane (differences only)

iOS: `xcrun simctl boot/install/launch`, screenshots `xcrun simctl io booted screenshot`, video `recordVideo`, deep links `simctl openurl`; taps need `idb ui tap x y` (simctl can't inject touches) — verify idb early or flag setup blocker. Android: `adb shell input tap/swipe`, `adb exec-out screencap -p`, `adb shell screenrecord`. One simulator/emulator at a time; keep a per-screen done-checklist file so crashes resume, not restart. Everything else (phases, folder tree, specs, review, index) is identical.
