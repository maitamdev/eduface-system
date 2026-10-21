# AuraAttend interface refresh

## Second revision

The user rejected the first visual direction as too recognizably AI-generated. The current direction is a working attendance ledger: white surfaces, neutral navigation, 4px control corners, one unboxed metric strip, session rows, searchable records and a small daily bar chart. Marketing callouts, slogans, pastel cards and decorative avatars have been removed. Login is now a single purpose form. Brand wordmark and routes remain unchanged. Visual settings: variance 3, motion 1, density 6. Current screenshots are named `dashboard-v2-*`.

## Audit

- Current frontend: React 18, TypeScript, Vite, Tailwind 3, Lucide, Recharts. The working tree already contains a frontend rewrite; build on that version.
- Brand: AuraAttend wordmark and ScanFace icon, indigo accent, Plus Jakarta Sans / Inter, rounded controls. Preserve wordmark, routes, role restrictions, bilingual support, camera workflows and form field order.
- Information architecture: overview, scanner, sessions, records; admin-only people, enrollment, reports and system tools.
- Problems: competing indigo/cyan gradients, undersized secondary text, equal emphasis across panels, infrastructure copy in the toolbar, silent dashboard failures and no disconnected design preview.
- Existing visual settings: design variance 4, motion intensity 3, visual density 6. New direction: 5 / 3 / 5, operational hierarchy and restrained motion.
- This is an application dashboard. The frontend taste skill's marketing patterns do not apply; use existing React components, native CSS, Lucide and Recharts rather than adding another component system.
- SEO baseline: retain title, description and authenticated route slugs. No public content migration.

## Design decisions

- Light neutral workspace, indigo actions, semantic green/amber/red for status. Dark theme uses the same hierarchy.
- Self-host Be Vietnam Pro for Vietnamese, consistent spacing and tabular numerals.
- Cards: 18px corners; controls: 10px; status pills: fully rounded. Borders carry hierarchy; subtle shadows.
- Desktop navigation, accessible mobile drawer with Escape, focus containment/return, skip link, explicit icon labels.
- Refreshes keep data visible; disconnected panels expose retry rather than displaying missing values as zero. Independent requests retain successful panels.
- `/design-preview` is development-only, labels fictional data and does not authenticate a user or grant API privileges. Operational links use guarded routes.

## Verification

`npm run build` passed. Vietnamese/English, light/dark, desktop/mobile, keyboard drawer behavior, preview roles, empty panels and login labels were inspected in browser. Backend authentication and recognition were unavailable locally. Generated concept art illustrates the direction; browser screenshots document implementation. See [deliverables and verification](ui-demo/README.md).
