from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-design.py"


def run(text: str, baseline: str | None = None):
    temp = tempfile.TemporaryDirectory()
    path = Path(temp.name) / "DESIGN.md"
    path.write_text(text)
    cmd = [sys.executable, str(SCRIPT), str(path)]
    if baseline is not None:
        old = Path(temp.name) / "baseline.md"
        old.write_text(baseline)
        cmd += ["--baseline", str(old)]
    result = subprocess.run(cmd, text=True, capture_output=True)
    payload = json.loads(result.stdout or result.stderr)
    temp.cleanup()
    return result, payload


VALID = """---
version: alpha
name: Fixture
description: Fixture design
colors:
  primary: '#123456'
  ink: '#ffffff'
typography:
  body:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: 0
spacing:
  sm: 8px
rounded:
  sm: 4px
components:
  button:
    backgroundColor: '{colors.primary}'
    typography: '{typography.body}'
---
# Rules
Use `{colors.primary}`.
"""


class ValidateTests(unittest.TestCase):
    def test_valid_and_composite_typography_reference(self):
        result, payload = run(VALID)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(payload["status"], "structurally-valid")

    def test_reference_namespaces_groups_and_prose_alias(self):
        for ref in ("{missing.token}", "{typography}", "{spacing.sm}"):
            text = VALID.replace("{typography.body}", ref)
            if ref == "{spacing.sm}":
                # A scalar token is still a valid reference (semantic use is reviewed separately).
                self.assertEqual(run(text)[0].returncode, 0)
            else:
                self.assertEqual(run(text)[0].returncode, 1)
        self.assertEqual(run(VALID + "Use `{component.button}`.\n")[0].returncode, 0)
        self.assertEqual(run(VALID + "Use `{component.missing}`.\n")[0].returncode, 1)
        result, payload = run(VALID + "Example `{token.refs}`.\n")
        self.assertEqual(result.returncode, 0)
        self.assertIn("ambiguous-prose-reference", {f["code"] for f in payload["findings"]})

    def test_basic_colors_and_explicit_unsupported_syntax(self):
        for color in ("#12345", "#12", "rgb(nonsense)", "rgb(1, nope, 3)"):
            with self.subTest(color=color):
                result, payload = run(VALID.replace("#123456", color))
                self.assertEqual(result.returncode, 1)
                self.assertIn("invalid-color", {f["code"] for f in payload["findings"]})
        for color in ("#abc", "#abcd", "#12345678", "rgba(1, 2, 3, 0.5)", "hsl(120, 50%, 40%)"):
            self.assertEqual(run(VALID.replace("#123456", color))[0].returncode, 0)
        for color in ("oklch(60% 0.2 30)", "rgb(1 2 3 / 50%)"):
            result, payload = run(VALID.replace("#123456", color))
            self.assertEqual(result.returncode, 0)
            self.assertIn("color-not-checked", {f["code"] for f in payload["findings"]})

    def test_color_alias_alpha_and_hue_units(self):
        for color in ("rgb(1, 2, 3, 0.5)", "rgba(1, 2, 3)",
                      "hsl(120deg, 50%, 40%)", "hsl(0.5turn, 50%, 40%, 50%)",
                      "hsla(1rad, 50%, 40%)", "HSL(100grad, 50%, 40%)"):
            with self.subTest(color=color):
                result, payload = run(VALID.replace("#123456", color))
                self.assertEqual(result.returncode, 0, payload)
                self.assertFalse(any(f["path"] == "colors.primary" for f in payload["findings"]))
        for color in ("hsl(10%, 50%, 40%)", "hsla(10%, 50%, 40%, .5)"):
            result, payload = run(VALID.replace("#123456", color))
            self.assertEqual(result.returncode, 1)
            self.assertIn("invalid-color", {f["code"] for f in payload["findings"]})
        for color in ("hsl(calc(1turn / 2), 50%, 40%)", "rgb(from red r g b)",
                      "rgb(var(--channels))", "rgb(1 2 3 / .5)"):
            result, payload = run(VALID.replace("#123456", color))
            self.assertEqual(result.returncode, 0)
            self.assertIn("color-not-checked", {f["code"] for f in payload["findings"]})

    def test_audit_candidate_removes_known_stale_values_and_is_pending(self):
        project = ROOT / "examples/saas-demo"
        run_dir = project / ".design-samples/20260910T062049Z-audit02"
        candidate = run_dir / "claude-zh"
        design = (candidate / "DESIGN.md").read_text()
        self.assertNotEqual((project / "DESIGN.md").read_bytes(), (candidate / "DESIGN.md").read_bytes())
        self.assertEqual((project / "DESIGN.md").read_bytes(), (candidate / "baseline.DESIGN.md").read_bytes())
        self.assertIn('**On Primary** (`{colors.on-primary}` — #141413)', design)
        self.assertNotIn('fontFamily: "Copernicus', design)
        self.assertNotIn('hero h1 64→32px', design)
        self.assertIn('h1 44px', design)
        report = json.loads((candidate / "review.json").read_text())
        session = json.loads((run_dir / "session.json").read_text())
        self.assertEqual(report["design_sha256"], hashlib.sha256((candidate / "DESIGN.md").read_bytes()).hexdigest())
        self.assertEqual(report["status"], "pending")
        self.assertIsNone(session["user_confirmation"])
        self.assertEqual(session["phase"], "sample-review")
        self.assertFalse((run_dir / "commit-receipt.json").exists())
        self.assertEqual(set(p.name for p in (candidate / "evidence").iterdir()), {"validate-design.json"})
        root_sha = hashlib.sha256((project / "DESIGN.md").read_bytes()).hexdigest()
        self.assertEqual(session["root_design_before"], {"exists": True, "sha256": root_sha})
        self.assertEqual(session["candidates"][0]["baseline_sha256"], root_sha)
        self.assertNotEqual(root_sha, report["design_sha256"])
        old = project / ".design-samples/20260910T123000Z-demo01"
        old_session = json.loads((old / "session.json").read_text())
        self.assertEqual(old_session["phase"], "committed")
        self.assertEqual(old_session["root_design_before"], {"exists": False, "sha256": None})
        self.assertIsNotNone(old_session["user_confirmation"])
        self.assertEqual(json.loads((old / "commit-receipt.json").read_text())["after_sha"], root_sha)
        self.assertEqual(root_sha, "932ab9fad6b58f4d3125d6f25a46b217b23d8ae19dcfbd373486e4640ef37b88")
        self.assertEqual(run(design)[0].returncode, 0)

    def test_duplicate_key_is_rejected(self):
        result, payload = run(VALID.replace("  ink: '#ffffff'", "  ink: '#ffffff'\n  ink: '#000000'"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate", payload["error"])

    def test_missing_reference_and_cycle(self):
        missing = VALID.replace("{colors.primary}", "{colors.absent}", 1)
        result, payload = run(missing)
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing-reference", {x["code"] for x in payload["blocking_findings"]})
        cycle = VALID.replace("  primary: '#123456'", "  primary: '{colors.ink}'").replace("  ink: '#ffffff'", "  ink: '{colors.primary}'")
        result, payload = run(cycle)
        self.assertEqual(result.returncode, 1)
        self.assertIn("reference-cycle", {x["code"] for x in payload["blocking_findings"]})

    def test_prose_code_fence_is_ignored_but_real_reference_is_not(self):
        fenced = VALID.replace("Use `{colors.primary}`.", "```css\n.x { color: {colors.unknown}; }\n```")
        self.assertEqual(run(fenced)[0].returncode, 0)
        real = VALID.replace("Use `{colors.primary}`.", "Use `{colors.unknown}`.")
        result, payload = run(real)
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing-prose-reference", {x["code"] for x in payload["blocking_findings"]})

    def test_types_unknowns_and_baseline_diff(self):
        changed = VALID.replace("fontSize: 16px", "fontSize: normal").replace("description: Fixture design", "description: Fixture design\ncustom: keep-me")
        result, payload = run(changed, VALID)
        self.assertEqual(result.returncode, 1)
        codes = {x["code"] for x in payload["findings"]}
        self.assertIn("invalid-dimension", codes)
        self.assertIn("unknown-top-level-key", codes)
        self.assertTrue(payload["baseline_diff"]["body_changed"] is False)
        self.assertIn("typography.body.fontSize", payload["baseline_diff"]["tokens"]["changed"])


if __name__ == "__main__":
    unittest.main()
