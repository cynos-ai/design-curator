# Changes

## Audit revision — current draft, not confirmed

- Request: repair the fixture's internal specification/sample inconsistencies, not invent a new style.
- On Primary prose: stale #ffffff → #141413, matching the existing token and HTML.
- Font roles: proprietary source stacks → actual local display/body/monospace stacks in typography and Typography; no font-loading claim added.
- Current h1: source 64px/1.05 (mobile 32px) → actual clamp(46px, 5.5vw, 72px)/1.03 and 44px at ≤430px. Section heading maximum 48px → actual 50px/1.12. UI weights and button line-height synchronized.
- Buttons: 40px source height and 12px padding → min-height 44px, 11px vertical padding; secondary border/background and nav CTA weight scoped explicitly.
- Main Layout/Components/Responsive sections now document actual sample geometry, 820/430 breakpoints, hidden navigation links (no invented hamburger), static product shadow and cream footer. These larger source-style exceptions need fresh review; they are no longer silently treated as unchanged source rules.
- This is a new audit run. Its baseline is an exact copy of the unchanged project root from the previous committed run (SHA 932ab9fad6b58f4d3125d6f25a46b217b23d8ae19dcfbd373486e4640ef37b88), not a fresh upstream copy. sample.html is unchanged; no historical browser evidence is copied into this candidate's evidence/.
- The old committed run, root, confirmation and receipt remain intact. New root_design_before is fixed to that root SHA; the revised candidate has a different SHA. Historical consistency claims are withdrawn by the audit note, not by rewriting committed session history. Original-record copies are retained in ../evidence-before-audit/.
- Verification: bundled structure/reference checks rerun; full consistency and browser acceptance pending. The previous pass cannot certify this revision; no user confirmation exists for the new run. No new commit receipt or user feedback fabricated.

## Historical implementation notes (superseded where contradicted above)

- Request: adapt the Claude-inspired system for a Chinese SaaS sample and preserve readability.
- `colors.on-primary`: `#ffffff` → `#141413`; synchronized On Primary, primary button, coral callout/badge and CTA-band prose.
- `colors.primary-active`: `#a9583e` → `#bf6b50`; synchronized state prose so deep-ink text remains above the normal-text contrast target.
- Added explicit CJK display/body fallback and 44px project touch target in Project Application & Provenance.
- Source baseline remains unchanged. Browser evidence and final hashes are recorded in review.json.
