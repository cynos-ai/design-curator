# Test Results

## Current audit revision

Scope: internal Skill contracts only. No external-security framework, CSS engine or evidence-authentication system was added.

Executed:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python scripts/build-library.py --skill-root . --check
```

- Unit tests: **25 passed, 0 failed** (previously 15).
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
- New audit candidate removes known stale values and stays pending. Tests assert the original committed root/session/receipt remain unchanged, the new baseline matches that root, and no historical browser files enter new evidence/. These limited assertions do not prove full semantic consistency.

## Demo status: pending fresh acceptance

Audit found a stale on-primary literal and unsynchronized font/responsive rules in the formerly committed demo. The prior prose-consistency pass was withdrawn.

The project root and original committed run `20260910T123000Z-demo01` remain byte-identical to their original version, including confirmation and receipt. A new run `20260910T062049Z-audit02` copies that root as its immutable baseline and fixes root_design_before to the original SHA. Only its candidate contains the revised typography/component/responsive rules. New review is pending, user_confirmation is null and no new receipt exists. The old consistency pass is withdrawn in the audit documentation without rewriting commit history.

Original-record copies are retained under:

`examples/saas-demo/.design-samples/20260910T062049Z-audit02/evidence-before-audit/`

Historical viewport screenshots remain only in the old run. New candidate evidence/ contains only the freshly generated structural validation report. This revision did **not** rerun browser checks or claim fresh visual acceptance, per-glyph font proof, complete semantic consistency or WCAG certification.

The other Agent/browser scenarios remain scoped as recorded in `tests/scenarios.md`; protocol checks and fault-injection tests are not browser evidence.
