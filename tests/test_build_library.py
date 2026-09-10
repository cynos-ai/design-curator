from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build-library.py"


def command(root: Path, check: bool = False):
    args = [sys.executable, str(root / "scripts" / "build-library.py"), "--skill-root", str(root)]
    if check:
        args.append("--check")
    return subprocess.run(args, text=True, capture_output=True)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class BuildTests(unittest.TestCase):
    def clone(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        temp = tempfile.TemporaryDirectory()
        target = Path(temp.name) / "skill"
        shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(".git", "__pycache__", ".tmp-*", ".build-backup-*"))
        return temp, target

    def test_current_build_is_deterministic_and_complete(self):
        before = (digest(ROOT / "INDEX.md"), digest(ROOT / "assets/catalog.json"), digest(ROOT / "assets/build-receipt.json"))
        result = command(ROOT, check=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, (digest(ROOT / "INDEX.md"), digest(ROOT / "assets/catalog.json"), digest(ROOT / "assets/build-receipt.json")))
        catalog = json.loads((ROOT / "assets/catalog.json").read_text())
        self.assertEqual(catalog["count"], 74)
        self.assertEqual(len({x["slug"] for x in catalog["entries"]}), 74)
        slack = next(x for x in catalog["entries"] if x["slug"] == "slack")
        self.assertIsNone(slack["category"])
        self.assertEqual(slack["display_name"], "Slack")
        self.assertEqual(next(x for x in catalog["entries"] if x["slug"] == "linear.app")["slug"], "linear.app")

    def test_raw_hash_mutation_fails_without_replacing_old_outputs(self):
        temp, root = self.clone()
        try:
            old = digest(root / "INDEX.md")
            path = root / "assets/upstream/design-md/airbnb/DESIGN.md"
            path.write_bytes(path.read_bytes() + b"\n")
            result = command(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("raw hash mismatch", result.stderr)
            self.assertEqual(digest(root / "INDEX.md"), old)
        finally:
            temp.cleanup()

    def test_overlay_and_note_mutations_fail(self):
        for relative, message in [("assets/overlays/kraken/DESIGN.md", "overlay hash mismatch"), ("assets/source-notes/kraken.json", "source note hash mismatch")]:
            with self.subTest(relative=relative):
                temp, root = self.clone()
                try:
                    path = root / relative
                    path.write_bytes(path.read_bytes() + b" ")
                    result = command(root)
                    self.assertEqual(result.returncode, 1)
                    self.assertIn(message, result.stderr)
                finally:
                    temp.cleanup()

    def test_inventory_extra_and_active_lock_fail_safely(self):
        temp, root = self.clone()
        try:
            extra = root / "assets/upstream/design-md/not-real"
            extra.mkdir()
            (extra / "DESIGN.md").write_text("x")
            result = command(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("inventory mismatch", result.stderr)
        finally:
            temp.cleanup()
        (ROOT / ".build-library.lock").write_text("test")
        try:
            result = command(ROOT, check=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn("active lock", result.stderr)
        finally:
            (ROOT / ".build-library.lock").unlink()

    def test_receipt_covers_catalog_index_and_74_designs(self):
        receipt = json.loads((ROOT / "assets/build-receipt.json").read_text())
        self.assertEqual(receipt["count"], 74)
        self.assertEqual(len([p for p in receipt["files"] if p.startswith("assets/design-md/")]), 74)
        self.assertNotIn("assets/build-receipt.json", receipt["files"])
        for relative, expected in receipt["files"].items():
            self.assertEqual(digest(ROOT / relative), expected)


if __name__ == "__main__":
    unittest.main()
