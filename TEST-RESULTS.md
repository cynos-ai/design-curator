# Test Results

Validation date: 2026-09-10

## Automated

Commands:

```bash
python -m py_compile scripts/*.py tests/*.py
python scripts/build-library.py --skill-root . --check
python -m unittest discover -s tests -v
```

Results:

- Python compilation: passed.
- Deterministic library check: passed, 74 effective specifications at locked commit.
- Unit tests: **15 passed, 0 failed**.
- Project audit: Skill frontmatter, authored local links, build receipt hashes and demo commit receipt passed.

Covered areas: source/overlay/note hash gates, 74-entry inventory, Slack supplement, deterministic receipt, active build lock, strict YAML and duplicate keys, missing/cyclic/prose references, type checks, baseline diff, candidate/sample/asset bundle identity, required review checks, confirmation and replacement authorization, backup permissions, external root changes, stale samples, symlinks, commit lock and idempotent rerun.

## Browser exercise

`examples/saas-demo` was rendered in an isolated browser at 375, 768 and 1440 CSS px.

- No horizontal overflow at the three target widths.
- Navigation collapsed at narrow widths; content remained readable.
- All rendered `.btn` controls measured about 45.69 CSS px high.
- Keyboard Tab produced a visible 3px teal outline with 3px offset.
- Computed primary colors matched deep ink on coral.
- Calculated opaque contrast ratios: coral/deep-ink 5.625:1; adjusted active coral/deep-ink 4.770:1; dark/cream 17.005:1.
- Final screenshots were regenerated after the last HTML change.

Evidence is in `examples/saas-demo/.design-samples/20260910T123000Z-demo01/claude-zh/evidence/`. This is scoped sample evidence, not full WCAG certification or validation of all 74 systems.

## Not executed as passing browser tests

The remaining cross-domain scenarios in `tests/scenarios.md` are explicitly marked as protocol/manual or not executed. They are not represented as successful browser runs.
