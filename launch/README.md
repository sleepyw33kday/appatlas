# AppAtlas launch kit

Ready-to-post drafts. All lead with the live demo, because the artifact sells better than any description. Post from your own accounts (these are drafts, not auto-posted).

**Canonical links**
- Live atlas demo: https://sleepyw33kday.github.io/appatlas/example/
- Landing: https://sleepyw33kday.github.io/appatlas/
- Repo: https://github.com/sleepyw33kday/appatlas
- Demo GIF: `assets/appatlas-demo.gif`

**Suggested order (one morning)**
1. Show HN + X thread + r/ClaudeAI, same 2-hour window.
2. Reply to every comment for the first few hours (this is what carries HN/Reddit).
3. Same afternoon: submit to the awesome-lists (see `../` PR).
4. LinkedIn a day later for the UX-research/PM crowd.
5. Product Hunt once there's a small star base.

---

## Show HN

**Title** (80 char max, no emoji):
```
Show HN: AppAtlas – map every screen of any app with one Claude Code command
```

**URL:** `https://sleepyw33kday.github.io/appatlas/`

**First comment** (post immediately after submitting):
```
I kept doing the same tedious thing by hand: click through an entire product,
screenshot every screen, and write up what each one does — for competitive
teardowns, onboarding new teammates, and QA baselines. It goes stale the week
after you finish.

AppAtlas is a Claude Code skill that does the whole thing. You point it at an
app you have access to and it walks the product end to end: signs in, completes
onboarding, opens every sub-tab, dialog and setting, and produces:

- screenshots of every screen
- a plain-language behavior spec per screen (what each control does, empty vs
  gated states, etc.)
- a single self-contained HTML "atlas" you can browse: an auto-built tree, a
  Mobbin-style tag rail (page types / flows / UI patterns) that filters across
  the whole app, a structure panel per screen, and a Flows graph that wires
  screens together by what opens what.

Live example (a real SaaS, 350 screens, 344 links between them):
https://sleepyw33kday.github.io/appatlas/example/ — try the tag chips, open a
screen, then hit "Flows".

It works on web (via the Claude-in-Chrome tools) and iOS/Android (simulator or
emulator). Under the hood it's an orchestrator that fans out one subagent per
section, then a review + coverage-audit pass, then a generator builds the atlas
from structured per-screen records.

Design constraints I cared about: it never enters payment details, never does
destructive actions, and hands any paid checkout back to you. Trials it starts,
it can cancel.

It's MIT, and the repo is its own Claude Code plugin marketplace:
  /plugin marketplace add sleepyw33kday/appatlas
  /plugin install appatlas@appatlas

Repo: https://github.com/sleepyw33kday/appatlas

Happy to answer anything about the orchestration, the tagging taxonomy, or how
it handles paywalls and quota.
```

---

## X / Twitter thread

**1/** (attach `assets/appatlas-demo.gif`)
```
I built a Claude Code skill that maps every screen of any app with one command.

Point it at a product, it walks the whole thing and hands you a browsable atlas:
every screen, tagged, linked, and searchable.

Live demo (350 real screens) 👇
https://sleepyw33kday.github.io/appatlas/example/
```

**2/**
```
It's not just a screenshot dump.

Every screen gets a structured record: page type, the flows it belongs to, its
UI patterns, an element inventory, and typed links to other screens.

So the whole app becomes a graph you can filter and walk.
```

**3/**
```
Four ways into the same atlas:

• an auto-built tree (section → page → sub-tab → modal)
• a Mobbin-style tag rail that filters across the app
• a structure panel on every screen
• a Flows graph, screens wired by what opens what
```

**4/**
```
Under the hood: an orchestrator fans out one subagent per section, runs a review
+ coverage audit, then a generator builds the atlas from structured records.

Web via Claude-in-Chrome, plus iOS/Android via the simulator.
```

**5/**
```
Safe on live accounts by design: no payment details entered, nothing destructive,
paid checkouts handed back to you. Trials it starts, it can cancel.
```

**6/** (CTA)
```
MIT. The repo is its own Claude Code plugin marketplace:

/plugin marketplace add sleepyw33kday/appatlas
/plugin install appatlas@appatlas

https://github.com/sleepyw33kday/appatlas
```

---

## r/ClaudeAI (or r/ClaudeCode)

**Title:**
```
I made a Claude Code skill that walks an entire app and builds a browsable, tagged atlas of every screen
```

**Body:**
```
Sharing a skill I built and just open-sourced: AppAtlas.

You give it an app you have access to and it does the walkthrough you'd otherwise
do by hand — signs in, completes onboarding, opens every sub-tab, dialog and
little setting — and produces screenshots + a behavior spec per screen + a single
self-contained HTML atlas.

The atlas is the fun part. Every screen is a structured record (page type, flows,
UI-pattern tags, element inventory, links to other screens), so you get:
- an auto-built app tree
- a faceted tag rail (page types / flows / patterns) that filters the whole app,
  Mobbin-style
- a structure panel on each screen
- a Flows graph that lays out each journey as a node graph, wired by what opens what

Live example, a real SaaS with 350 screens and 344 links:
https://sleepyw33kday.github.io/appatlas/example/

How it runs: it's an orchestrator that dispatches one Sonnet subagent per section
(sequential per browser tab / simulator, since they'd fight over the UI), then a
review + coverage-audit pass, then a generator builds the atlas from the records.
Works on web via the Claude-in-Chrome tools and on iOS/Android via the simulator.

It's careful on live accounts: no payment details, no destructive actions, paid
checkouts handed back to you.

Install (the repo is its own plugin marketplace):
/plugin marketplace add sleepyw33kday/appatlas
/plugin install appatlas@appatlas

Repo (MIT): https://github.com/sleepyw33kday/appatlas

Curious what people would point it at first. Happy to go into the orchestration
or the tagging taxonomy if useful.
```

---

## LinkedIn

```
Competitive teardowns and UX-research walkthroughs are one of those jobs that eat
a day and go stale the next week: click every screen, screenshot it, write up what
it does, keep it organized.

I open-sourced a Claude Code skill that does the whole thing. Point it at a
product you have access to and it walks the app end to end, then produces a
browsable "atlas": every screen, a plain-language spec of what each one does, and
a tagged, linked map you can filter by page type, flow, or UI pattern — plus a
graph view of how the screens connect.

Live example, a real SaaS with 350 screens:
https://sleepyw33kday.github.io/appatlas/example/

It runs on web and on iOS/Android, and it's careful on live accounts: no payment
details, nothing destructive, paid checkouts handed back to you.

Useful if you do product research, competitive analysis, design audits, or need a
regression baseline of a product's UI. It's MIT-licensed.

Repo: https://github.com/sleepyw33kday/appatlas
```

---

## Notes on claims (keep these honest)

- "350 screens, 344 links" is the real count from the bundled example. Keep it accurate if you regenerate.
- Don't claim it works with zero setup on mobile: it needs Xcode+simulator (idb) or Android emulator (adb).
- Don't imply it bypasses paywalls: it removes a *client-side nag overlay* on an account you own to document pages the server already returns; genuinely gated features stay gated and are documented as such.
