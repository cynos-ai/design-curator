# design-curator

> **Language:** English · [简体中文](./README-zh-CN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/cynos-ai/design-curator.svg)](https://github.com/cynos-ai/design-curator/releases)

An independent agent skill that picks one design system from 74 pinned brand-inspired `DESIGN.md` specifications, renders a real-content HTML sample for confirmation, and safely delivers a complete project-root `DESIGN.md`.

It is **not** an automatic scorer, a page-template library, an official brand system, or a WCAG certification tool. It adopts one existing system by default, never mixes systems without an explicit decision, and never overwrites project files before confirmation.

## Contents

- [Requirements](#requirements)
- [Install](#install)
- [Usage](#usage)
- [How it works](#how-it-works)
- [Repository layout](#repository-layout)
- [Lightweight packaging](#lightweight-packaging)
- [Safety and recovery](#safety-and-recovery)
- [Testing and evidence](#testing-and-evidence)
- [Source and license](#source-and-license)
- [Known limits](#known-limits)

## Requirements

- Python 3.11+
- `PyYAML==6.0.2`
- A real browser capability is recommended for responsive, font, interaction and contrast verification

```bash
python -m pip install -r requirements.txt
python scripts/build-library.py --skill-root .
python scripts/build-library.py --skill-root . --check
```

Builds are fully offline and pinned to [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md/tree/8147538b4226ae41e2487a9179e3bcc1f68e8554) commit `8147538b4226ae41e2487a9179e3bcc1f68e8554`. `--check` rebuilds in a temporary directory inside the skill and compares byte-for-byte without touching published artifacts.

## Install

Download the packaged skill from [Releases](https://github.com/cynos-ai/design-curator/releases) and unzip it, or copy this repository and keep `SKILL.md`, `scripts/`, `references/` and `assets/` together.

Then place the whole `design-curator/` directory in a skills location supported by your host:

- pi global: `~/.pi/agent/skills/design-curator/`
- pi project (trusted): `.pi/skills/design-curator/`
- explicit: `--skill /absolute/path/to/design-curator`

Run the build once after installing. Do not copy only `SKILL.md` or only the 13 overlay files.

## Usage

Example requests:

- "Pick two styles for this Chinese SaaS landing page and show me real-content samples first."
- "Something like Linear, but don't touch the root DESIGN.md yet."
- "Re-select the project's design system; replace it after I confirm the sample."

The agent reads all 74 descriptions in `INDEX.md`, then reads the full specification and source notes of each shortlisted candidate, and works inside the target project's `.design-samples/<run-id>/`. It only calls the commit script after the user confirms the current version and authorizes replacement:

```bash
python scripts/commit-design.py \
  --project-root /path/to/project \
  --session .design-samples/<run-id>/session.json
```

Structural validation:

```bash
python scripts/validate-design.py /path/to/candidate/DESIGN.md \
  --baseline /path/to/candidate/baseline.DESIGN.md
```

Exit code 0 means "no structural blockers" only. It does not mean the browser and accessibility checks passed.

## How it works

1. **Inspect the project** — record whether a root `DESIGN.md` exists, its SHA-256 and whether it is a regular file. Existing systems win unless the user asks to replace them.
2. **Build a minimal brief** — product, page type, audience, language, viewports, preferences, exclusions, assets and content status.
3. **Recommend semantically** — no scores, no tag weights, no vector ranking. Categories are for browsing only; explicit user constraints beat brand industry.
4. **Full-text review** — shortlisted candidates are read in full, together with their source notes, before any sample is generated.
5. **Real-content sample** — candidates share one content inventory but not one layout. Photography-driven systems show photography; docs systems show reading hierarchy.
6. **Adjust inside the candidate** — every adaptation is written back into the candidate `DESIGN.md` first, then the sample is re-rendered and re-checked.
7. **Verify honestly** — structure, prose consistency, fonts, responsive behaviour, interaction and contrast are recorded per check with `pass` / `fail` / `not-checked` / `not-applicable`.
8. **Confirm and commit safely** — the root file is replaced only with a current-version confirmation, a hash-bound candidate/sample bundle and a verified backup.

## Repository layout

- `SKILL.md` — short, complete execution protocol for the agent.
- `INDEX.md` / `assets/catalog.json` — generated description index; no scores or tags.
- `assets/upstream/` — read-only pinned snapshot of the 74 original files.
- `assets/overlays/` — 13 complete corrected documents.
- `assets/source-notes/` — provenance, omitted properties and known conflicts per overlay.
- `assets/audit/` — 13 standalone frontmatter YAML files and unified patches for auditing; not applied at runtime.
- `assets/design-md/` — the 74 effective runtime specifications produced by the build.
- `assets/build-receipt.json` — completion marker with artifact hashes.
- `scripts/build-library.py` — hash gates, overlay application, catalog and index generation.
- `scripts/validate-design.py` — strict YAML, duplicate keys, known token types, reference and baseline diff checks.
- `scripts/commit-design.py` — candidate/review/confirmation/bundle hash gates, backup and atomic root commit.
- `scripts/package-skill.py` — deterministic runtime-only ZIP with manifest and inner checksums.
- `IMPLEMENTATION-SPEC.md` — the full implementation specification (Chinese).

## Lightweight packaging

The development repository keeps tests, examples and acceptance evidence. Install packages deliberately exclude them:

```bash
python scripts/package-skill.py --skill-root . --version 1.0.0
```

Default output: `dist/design-curator-skill-1.0.0.zip`. The archive excludes `examples/`, `tests/`, `attachments/`, `assets/audit/` and development reports, while keeping the 74 runtime specifications, the rebuildable sources, scripts and workflow references. `PACKAGE-MANIFEST.json` and `PACKAGE-CHECKSUMS.sha256` inside the archive allow independent verification. Identical inputs and version produce a byte-identical ZIP.

## Safety and recovery

The committer rejects symbolic links, path escapes, stale evidence, missing required checks, external changes to the root file and unauthorized replacement. An existing specification is backed up to `backup/DESIGN.before.md` in the run directory, and the receipt is written to `commit-receipt.json`.

Before writing the root file, `commit-intent.json` is stored in the run directory. If the root file is written but the receipt or session write fails, keep the candidate, review and confirmation unchanged and re-run the same command: the script verifies the intent, root SHA and original backup, then only completes the records without overwriting again. If the final cleanup fails, the `already-committed` branch verifies the leftover intent against the receipt and session before removing it; a mismatch is preserved and reported.

If publishing the built library fails, the previous artifacts are restored; if the rollback also fails, the remaining `.build-backup-*` directory is retained and reported, and the completion marker is removed so an incomplete library is never treated as usable.

Restoring an older specification also requires user confirmation. It is only safe when the current root SHA equals the receipt's `after_sha` and the backup SHA equals `before_sha`; if the root has been edited since, the difference is shown instead of being overwritten. The lock only coordinates this tool, so avoid external editing during a commit.

## Testing and evidence

```bash
python -m unittest discover -s tests -v
```

Automated coverage includes: 74-entry build, the Slack supplement, raw/overlay/source-note hash gates, build lock and receipt; duplicate keys, missing and cyclic references, code fences, type checks and baseline diff; root creation and replacement, backup permissions, idempotent re-runs, stale candidates, external edits, symbolic links, commit lock, crash recovery and review gating.

`tests/scenarios.md` lists ten agent/browser scenarios with their real execution status. `examples/saas-demo/` is an isolated drill fixture: the earlier committed run keeps its specification, review, confirmation and receipt bytes, and the revision was completed in run `20260910T062049Z-audit02` with the previous root as its immutable baseline, then confirmed and committed through the real script. Machine-specific absolute paths inside the published `session.json` and `validate-design.json` records were replaced with the neutral prefix `/srv/projects/zhilan-demo`; no specification, sample, review, receipt or confirmation hash was affected. Fixture and fault-injection tests are labelled as such and are never presented as real user or browser acceptance.

## Source and license

Released under the MIT license, see [`LICENSE`](LICENSE).

- Upstream data: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md), pinned commit `8147538b4226ae41e2487a9179e3bcc1f68e8554`, MIT licensed. The complete notice is preserved in [`assets/UPSTREAM-LICENSE.txt`](assets/UPSTREAM-LICENSE.txt) and byte-identically in [`assets/upstream/LICENSE`](assets/upstream/LICENSE).
- Dependency: PyYAML 6.0.2, MIT licensed.
- Details: [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

The upstream content is unofficial inspiration analysis. The MIT license does not cover trademarks, brand marks, product imagery or proprietary fonts; confirm those rights independently before redistribution or commercial use.

## Known limits

- Semantic selection is performed by the agent reading the specifications; nothing is auto-scored.
- Color checking covers 3/4/6/8-digit hex, legacy comma `rgb()`/`rgba()` and numeric `hsl()`/`hsla()` (both pairs are aliases and alpha is optional; hue accepts a unitless number or `deg`/`grad`/`rad`/`turn`, and rejects percentages), plus `transparent`/`currentColor`. Modern space or slash syntax, `var()`/`calc()` and named colors are explicitly reported as `color-not-checked` rather than judged; real colors still need browser verification.
- Reference checking understands full token paths and treats `component.*` as an alias for the upstream `components.*`. Broken and whole-group references block; unknown prose forms are reported for human review. A component may reference one composite typography token but not the whole typography group.
- Prose consistency, actual glyph provenance, transparency or image-backed contrast and layout require human or browser checks.
- Without a browser, only the explicit human-review path is allowed; the tool never auto-approves.
- v1 has no full HTML style browser, no default mixing of systems, and no automatic native mobile conversion.
