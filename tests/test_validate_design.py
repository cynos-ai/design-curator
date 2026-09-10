from __future__ import annotations

import json
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
