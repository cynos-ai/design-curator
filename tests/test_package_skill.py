from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/package-skill.py"


class PackageTests(unittest.TestCase):
    def test_runtime_package_is_deterministic_complete_and_light(self):
        with tempfile.TemporaryDirectory() as temp:
            first = Path(temp) / "first.zip"
            second = Path(temp) / "second.zip"
            results = []
            for output in (first, second):
                run = subprocess.run(
                    [sys.executable, str(SCRIPT), "--skill-root", str(ROOT), "--version", "1.0.0-test", "--output", str(output)],
                    text=True, capture_output=True,
                )
                self.assertEqual(run.returncode, 0, run.stderr)
                results.append(json.loads(run.stdout))
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(results[0]["sha256"], hashlib.sha256(first.read_bytes()).hexdigest())
            with zipfile.ZipFile(first) as archive:
                self.assertIsNone(archive.testzip())
                names = set(archive.namelist())
                prefix = "design-curator/"
                self.assertIn(prefix + "SKILL.md", names)
                self.assertIn(prefix + "README.md", names)
                self.assertIn(prefix + "PACKAGE-MANIFEST.json", names)
                self.assertIn(prefix + "PACKAGE-CHECKSUMS.sha256", names)
                designs = [name for name in names if name.startswith(prefix + "assets/design-md/") and name.endswith("/DESIGN.md")]
                self.assertEqual(len(designs), 74)
                for forbidden in ("examples/", "tests/", "attachments/", "assets/audit/", "IMPLEMENTATION-SPEC.md", "TEST-RESULTS.md", "RELEASE-VALIDATION.json", "scripts/package-skill.py"):
                    self.assertFalse(any(name.startswith(prefix + forbidden) for name in names), forbidden)
                manifest = json.loads(archive.read(prefix + "PACKAGE-MANIFEST.json"))
                self.assertEqual(manifest["design_count"], 74)
                self.assertEqual(manifest["version"], "1.0.0-test")
                checksum_lines = archive.read(prefix + "PACKAGE-CHECKSUMS.sha256").decode().splitlines()
                for line in checksum_lines:
                    digest, relative = line.split("  ", 1)
                    self.assertEqual(hashlib.sha256(archive.read(prefix + relative)).hexdigest(), digest)


if __name__ == "__main__":
    unittest.main()
