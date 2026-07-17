# Directory / marketplace submissions

Where to list AppAtlas, and the exact submission each channel wants. Some accept PRs (done for you); the big ones are human-and-form-only (drafts below, paste them yourself).

## Done — PR opened

- **xiaolai/claude-plugin-marketplace** (community marketplace, accepts PRs):
  PR → https://github.com/xiaolai/claude-plugin-marketplace/pull/9
  Once merged, users can `/plugin marketplace add xiaolai/claude-plugin-marketplace` and find `appatlas`.

## Needs you to submit (form + human-only by their rules)

### awesome-claude-code (hesreallyhim/awesome-claude-code)
They reject PRs on purpose; submit via their "Submit a new resource" GitHub issue form, and their rules require a human to submit. Format rules: single-line, factual, no sales language, no emoji, don't address the reader.

- Submit at: the "Click here to submit a new resource" link in that repo's README (opens a GitHub issue template).
- **Name:** AppAtlas
- **Category:** Tooling (or Skills — pick the closest their form offers)
- **Primary link:** https://github.com/sleepyw33kday/appatlas
- **Description (paste verbatim, already rule-compliant):**
  ```
  Walks a web or mobile app end to end and produces a browsable atlas of every screen, with per-screen behavior specs, a faceted tag index, and a flow graph linking screens.
  ```

### Anthropic official plugin directory (anthropics/claude-plugins-official)
Vetted, form-based, review-gated. Submit via the plugin submission form.

- Submit at: `claude.ai/settings/plugins/submit` (or `platform.claude.com/plugins/submit`).
- Repo to submit: `https://github.com/sleepyw33kday/appatlas` (already a valid `.claude-plugin` marketplace + plugin, MIT-licensed, so it should pass the mechanical checks).
- Use the same one-line description as above.

## Passive / auto-indexed

Directories like claudemarketplaces.com, claudepluginhub.com, and the daily-updated community directories crawl GitHub for `.claude-plugin` manifests and plugin topics. The repo already has the manifests and topics (claude-code, claude-plugin, claude-skill, ...), so it should surface without action. If any offers a "submit" form, use the one-liner above.
