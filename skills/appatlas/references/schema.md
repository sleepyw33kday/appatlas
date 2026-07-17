# Atlas data model — the per-screen record

Every captured screen gets one structured record. Records are the backbone of the tree, the tag index, the structure panel, and the flow graph. Crawl agents emit them; a semantic pass normalizes tags and resolves cross-page links.

## Where records live

Each section writes `<section>/screens.json` — a JSON array of records for that section's screens. The viewer generator merges all `*/screens.json` at build time. One record per screenshot file.

## Record shape

```jsonc
{
  "id": "07-monitoring/monitor-detail--responses-tab",   // REQUIRED, stable = "<section>/<screenshot-stem>"
  "section": "07-monitoring",                             // REQUIRED, folder name
  "sectionTitle": "Monitoring",                           // human label
  "screenshot": "monitor-detail--responses-tab.jpg",      // REQUIRED, file in <section>/screenshots/

  // hierarchy → drives the auto tree (section → page → subtab → modal)
  "page": "Monitor Detail",        // the page this screen belongs to
  "subtab": "Responses",           // sub-tab within the page, or null
  "modal": null,                   // modal/dialog name if this screen IS a modal, else null

  "title": "Monitor detail — Responses tab",  // one-line human title
  "route": "/{org}/{proj}/monitors/{id}/responses",  // URL/route if known, else null

  // the "read on structure" (requirement 3)
  "pageType": "data-table",        // ONE value from taxonomy.md → PAGE TYPES
  "flows": ["monitoring"],         // 0..n from taxonomy.md → FLOWS (which product journeys this belongs to)
  "features": ["filtering","export","row-detail-modal","sorting"],  // capability-level, free-ish but prefer taxonomy
  "elements": [                    // element inventory (the observable controls)
    {"type":"filter","label":"Models","behavior":"multi-select dropdown"},
    {"type":"button","label":"Export","behavior":"downloads CSV of the response table"},
    {"type":"row","label":"response row","behavior":"opens the Response Details modal"}
  ],
  "states": ["populated"],         // 0..n: empty | populated | sample | gated | loading | error (see taxonomy)

  // semantic tagging (requirements 2 + 4) → the Mobbin layer
  "tags": ["data-table","filters","export","ai-response"],  // from taxonomy.md → PATTERN TAGS (controlled)

  // semantic linking (requirement 4) → typed edges to other screens = the graph
  "links": [
    {"to":"07-monitoring/monitor-detail--response-details-modal","via":"response row","type":"opens-modal"}
  ],

  "summary": "The monitor's per-response table: one row per AI answer captured, filterable by model/type/citations, each row opening a full response-detail modal."  // 1-2 sentence read
}
```

## Field rules

- **id / section / screenshot** are required and must be internally consistent (`id === section + "/" + stem(screenshot)`).
- **pageType** is exactly one value from the taxonomy. If nothing fits, use `other` and note why in `summary` (a recurring `other` means the taxonomy needs a new type — flag it).
- **tags / flows / states** draw from the controlled vocab in `taxonomy.md`. Free tags are allowed but every free tag must be justified; the semantic pass folds near-duplicates into the controlled set so the global index stays clean (this is what makes tags *indexable across many apps* — requirement 2).
- **elements**: capture the load-bearing controls, not every pixel. `type` from ELEMENT TYPES; `behavior` is a short verb phrase of what it does.
- **links.to** must be a valid `id` of another record. **links.type** from LINK TYPES. `via` names the control that creates the edge (a button, a row, a tab, a nav item). Links are what turn the flat gallery into a navigable graph.
- **summary** is the human "read" — what this screen is and does, in the user's terms.

## Who fills what (two-phase)

1. **Crawl agent (per section, has the browser):** emits records with everything it can observe directly — hierarchy, pageType, features, elements, states, a first-pass tags, summary. It knows its own section's internal links (tab→tab, button→modal within the section).
2. **Semantic pass (one agent, reads ALL sections' records + specs, no browser):** normalizes `tags`/`flows`/`pageType` against the taxonomy, assigns `flows` membership consistently, and resolves **cross-section links** (e.g. a dashboard CTA that jumps into another section) — these need the global view, so no single crawl agent can author them. Output overwrites/augments each `screens.json`.

## Validation before render

`build_atlas.py` should reject/repair: dangling `links.to` (drop with a warning), `pageType`/`tags` outside the taxonomy (keep but flag), `id` mismatches. Log dropped/flagged items; never silently swallow.
