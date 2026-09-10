# Test Results

## Current audit revision

Scope: internal Skill contracts only. No external-security framework, CSS engine or evidence-authentication system was added.

Executed:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python scripts/build-library.py --skill-root . --check
```

- Unit tests: **26 passed, 0 failed** (previously 15); includes deterministic lightweight-package verification.
- Locked library consistency: **74 effective specifications passed**; source assets, overlays and generated library content were not modified.
- Revised demo structure/reference validation: passed.

New regression coverage:

- Required review checks cannot all be not-applicable; passing checks need nonempty method/evidence records.
- User-reviewed path may retain machine not-checked with explicit human-review scope and feedback; missing feedback rejects. These are fixtures, not actual user acceptance.
- Root written but receipt/session write fails: retry completes records for both new and replaced roots, preserving the original backup; later root edits are not overwritten.
- Build publish failure restores old outputs; rollback failure retains the remaining backup and removes the completion marker.
- Unknown/missing and whole-group references, singular component prose aliases, ambiguous prose placeholders.
- Invalid basic hex/rgb colors; explicit not-checked for unsupported modern CSS syntax.
- Color alias/optional-alpha/angle-unit regressions: rgb(1, 2, 3, 0.5) and hsl(120deg, 50%, 40%) accepted; percentage hue rejected; unsupported syntax remains not-checked.
- Failed intent cleanup retried after records are already committed; mismatched intent retained.
- Confirmed audit02 root equals the candidate; confirmation, review, receipt and bundle identities agree. Backup equals baseline and the true prior root SHA; before/after differ. Original run/session/receipt remain unchanged. These assertions do not prove full semantic consistency.
- Runtime packaging is deterministic for equal inputs/version, contains 74 effective designs and package-local checksums, and excludes examples/tests/audit/development material.

## Demo status: Agent/browser reviewed, user confirmed, committed

Audit found a stale on-primary literal and unsynchronized font/responsive rules in the formerly committed demo. The prior prose-consistency pass was withdrawn.

The original committed run `20260910T123000Z-demo01` keeps its specification, review, confirmation and receipt bytes. For publication, machine-specific absolute paths inside the two `session.json` files and the two `validate-design.json` evidence reports were replaced with the neutral prefix `/srv/projects/zhilan-demo`; no design, sample, review, receipt or confirmation hash changed. New run `20260910T062049Z-audit02` preserves the former root as immutable baseline and fixes root_design_before to that SHA. After scoped Agent/browser review and the user's explicit continuation confirmation following sample presentation, commit-design.py copied the unchanged confirmed candidate into the root and preserved the original bytes in backup/DESIGN.before.md. Session is committed, review is ready-machine-verified and the new receipt records distinct before/after hashes. The old consistency pass is withdrawn in audit documentation without rewriting commit history.

Original-record copies are retained under:

`examples/saas-demo/.design-samples/20260910T062049Z-audit02/evidence-before-audit/`

Historical viewport screenshots remain only in the old run. New candidate evidence/ now contains the fresh structural report, agent-review.md, browser-checks.json, 375/768/1440 screenshots and keyboard focus screenshot. Checks found and repaired insufficient focus/number contrast, an invalid email action and callout alignment. Real viewport overflow checks, text contrast pairs, Tab/Shift+Tab/Enter navigation, hover and active pointer state were rerun on the final HTML. All action targets are at least 44px high. Fonts were checked as readable local CJK fallback, not per-glyph identity proof. User acceptance was recorded separately after this scoped sample validation. Neither the checks nor user acceptance imply complete WCAG or cross-browser/native-touch/200%-zoom certification.

The other Agent/browser scenarios remain scoped as recorded in `tests/scenarios.md`; protocol checks and fault-injection tests are not browser evidence.
