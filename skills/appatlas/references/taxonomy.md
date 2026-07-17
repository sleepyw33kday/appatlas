# Atlas taxonomy — the controlled vocabulary

Mobbin-informed. This is what makes tags **indexable and consistent across many apps** (requirement 2): if every atlas draws page types, flows, and pattern tags from the same vocabulary, a future meta-index can answer "show me every paywall screen" or "every onboarding flow" across all crawled apps. Free values are allowed but the semantic pass folds them toward these; a value that recurs across apps earns a place here.

Keep this file the single source of truth. When you add a value, add it here so the next crawl reuses it instead of inventing a synonym.

## PAGE TYPES (exactly one per screen)

`landing` · `auth` · `onboarding-step` · `dashboard` · `list` · `data-table` · `detail` · `form` · `wizard-step` · `editor` · `settings` · `pricing` · `checkout` · `empty-state` · `gated` · `modal` · `drawer` · `gallery` · `docs` · `analytics` · `search-results` · `feed` · `profile` · `notifications` · `command-palette` · `error` · `confirmation` · `other`

Guidance: `gated` = the screen the free/locked user sees (upgrade wall). `modal`/`drawer` = the screen IS an overlay. `data-table` beats `list` when rows have many columns/sortable cells. `analytics` = chart-heavy read-only dashboards; `dashboard` = the app's home/overview.

## FLOWS (0..n per screen — the product journeys)

Common (reuse across apps): `onboarding` · `sign-in` · `sign-up` · `checkout` · `subscription-management` · `cancellation` · `settings` · `team-management` · `api-keys` · `integrations` · `search` · `sharing` · `export` · `notifications` · `referral` · `content-creation` · `analytics`

App-specific flows are fine (e.g. `monitoring`, `citations`, `sitemap-sync`) — name them after the product's own journey. Keep them lowercase-kebab.

## PATTERN TAGS (0..n per screen — the Mobbin UI-pattern layer)

Navigation: `sidebar-nav` · `top-nav` · `tabs` · `breadcrumb` · `command-palette` · `global-search` · `mega-menu` · `bottom-nav`

Filtering / data control: `filters` · `sort` · `date-range-picker` · `multi-select` · `dropdown` · `pill-filter` · `chips` · `search`

Data display: `data-table` · `card-grid` · `bento` · `list-detail` · `master-detail` · `kanban-board` · `chart` · `bar-chart` · `line-chart` · `donut-chart` · `sparkline` · `heatmap` · `stat-cards` · `map` · `timeline` · `feed` · `activity-log` · `leaderboard` · `comparison` · `feature-matrix`

Overlays / structure: `modal` · `dialog` · `drawer` · `bottom-sheet` · `popover` · `tooltip` · `accordion` · `disclosure`

Input / forms: `form` · `inline-edit` · `toggle` · `segmented-control` · `slider` · `stepper` · `wizard` · `file-upload` · `drag-drop` · `rich-text-editor` · `code-block` · `copy-button`

Commerce / growth: `pricing-table` · `paywall` · `upgrade-nag` · `trial-banner` · `retention-funnel` · `checkout-form` · `plan-toggle`

Content / social: `image-gallery` · `lightbox` · `carousel` · `marquee` · `testimonial` · `logo-wall` · `avatar` · `rating` · `comment`

Status / feedback: `empty-state` · `skeleton-loader` · `toast` · `banner` · `status-pill` · `badge` · `progress` · `notification-list`

System / dev: `api-key` · `webhook` · `settings-list` · `kbd-shortcut` · `syntax-highlight` · `docs-nav`

Marketing surfaces: `hero` · `cta` · `footer` · `faq`

## ELEMENT TYPES (for `elements[].type`)

`button` · `icon-button` · `link` · `input` · `textarea` · `select` · `dropdown` · `toggle` · `checkbox` · `radio` · `tab` · `filter` · `search` · `chip` · `card` · `row` · `cell` · `chart` · `menu` · `modal-trigger` · `upload` · `slider` · `stepper` · `nav-item`

## LINK / EDGE TYPES (for `links[].type` — the graph edges)

- `navigates` — a nav item / link that goes to another page (different route).
- `tab-switch` — switching a sub-tab within the same page.
- `opens-modal` — a control that opens a modal/dialog screen.
- `opens-drawer` — opens a side drawer / bottom sheet.
- `opens-menu` — opens a menu/popover that itself is a captured screen.
- `expands` — inline expand-in-place (an accordion/chevron row that reveals more on the SAME screen), or a same-screen state transition after an action (a form submit that swaps the panel content). Not a true overlay, so distinct from `opens-modal`/`opens-drawer`. Rendered dashed and ignored for graph layout.
- `cta` — a primary call-to-action that jumps into another flow (e.g. dashboard "Generate Report" → report dialog).
- `back` — returns to a parent/previous screen.
- `sub-page` — a hierarchical child (page → its detail/settings sub-page).
- `related` — semantically related, no direct control (same data seen elsewhere).
- `external` — leaves the app (docs site, OAuth, Stripe).

Edge direction is source → target. The flow graph groups nodes by `flows` (or `section` when a screen has no flow) and draws these edges; `navigates`/`cta`/`sub-page` shape the tree-like flow, `related` shows cross-links.

## Extending the taxonomy

If ≥3 screens across a crawl need a value that isn't here, add it (don't ship 3 synonyms). If it recurs across *apps*, it belongs in the "common" tiers so the cross-app index stays coherent. Record additions in the crawl's `README` so the taxonomy evolution is auditable.
