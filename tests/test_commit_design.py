from __future__ import annotations

import hashlib
import importlib.util
from unittest.mock import patch
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "commit-design.py"
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("commit_design", SCRIPT)
commit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(commit)
DESIGN = (ROOT / "assets/design-md/claude/DESIGN.md").read_bytes()
CHECK_IDS = ["structure", "references", "prose-consistency", "fonts", "responsive", "interaction", "contrast", "content-authenticity"]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


class CommitTests(unittest.TestCase):
    def make_project(self, existing: bytes | None = None, approved: bool = True):
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name).resolve()
        root_design = project / "DESIGN.md"
        if existing is not None:
            root_design.write_bytes(existing)
            os.chmod(root_design, 0o640)
        run = project / ".design-samples/run-1"
        candidate = run / "claude"
        candidate.mkdir(parents=True)
        (candidate / "DESIGN.md").write_bytes(DESIGN)
        (candidate / "sample.html").write_text("<!doctype html><title>Sample</title><button>Start</button>")
        (candidate / "assets").mkdir()
        (candidate / "assets/local.txt").write_text("asset")
        design_sha = sha(DESIGN)
        sample_sha = sha((candidate / "sample.html").read_bytes())
        asset_hashes = {"assets/local.txt": sha((candidate / "assets/local.txt").read_bytes())}
        bundle = sha(canonical({"sample.html": sample_sha, **asset_hashes}))
        review = {
            "schema_version": 1, "candidate_id": "claude", "design_sha256": design_sha,
            "sample_sha256": sample_sha, "asset_hashes": asset_hashes,
            "sample_bundle_sha256": bundle, "external_assets": [],
            "status": "ready-machine-verified",
            "checks": [{"id": key, "status": "pass", "method": "fixture (not browser acceptance)", "evidence": ["unit-test fixture"], "findings": []} for key in CHECK_IDS],
            "blocking_findings": [], "accepted_limitations": [],
        }
        (candidate / "review.json").write_text(json.dumps(review))
        session = {
            "schema_version": 1, "run_id": "run-1", "phase": "selected", "project_root": str(project),
            "root_design_before": {"exists": existing is not None, "sha256": sha(existing) if existing is not None else None},
            "candidates": [{"id": "claude", "slug": "claude", "relative_path": "claude", "baseline_sha256": design_sha, "current_design_sha256": design_sha, "sample_sha256": sample_sha, "sample_bundle_sha256": bundle, "review_path": "claude/review.json"}],
            "selected_candidate": "claude",
            "user_confirmation": {"candidate_id": "claude", "design_sha256": design_sha, "sample_bundle_sha256": bundle, "replacement_approved": approved, "confirmation_text": "确认采用当前版本", "confirmed_at": "2026-09-10T12:00:00Z"},
        }
        session_path = run / "session.json"
        session_path.write_text(json.dumps(session))
        return temp, project, session_path, candidate

    def invoke(self, project: Path, session: Path):
        return subprocess.run([sys.executable, str(SCRIPT), "--project-root", str(project), "--session", str(session.relative_to(project))], text=True, capture_output=True)

    def test_review_paths(self):
        for kind in ("all-na", "empty-evidence", "manual-missing-feedback", "manual-complete"):
            with self.subTest(kind=kind):
                temp, project, session, candidate = self.make_project()
                try:
                    path = candidate / "review.json"
                    review = json.loads(path.read_text())
                    if kind == "all-na":
                        for check in review["checks"]: check["status"] = "not-applicable"
                    elif kind == "empty-evidence":
                        review["checks"][0]["evidence"] = []
                    else:
                        review["status"] = "ready-user-reviewed"
                        for check in review["checks"]:
                            if check["id"] in {"fonts", "responsive", "interaction", "contrast"}:
                                check["status"] = "not-checked"
                                check["method"] = "No browser; see human_review"
                                check["evidence"] = []
                        if kind == "manual-complete":
                            review["human_review"] = {"checked_ids": ["fonts", "responsive", "interaction", "contrast"], "feedback": "Fixture: inspected 375/768/1440, font readability, buttons and focus; accepted this scope."}
                    path.write_text(json.dumps(review))
                    result = self.invoke(project, session)
                    self.assertEqual(result.returncode, 0 if kind == "manual-complete" else 1, result.stderr)
                finally:
                    temp.cleanup()

    def test_recover_after_record_write_failure(self):
        for original in (None, b"original\\n"):
            for failed_name in ("commit-receipt.json", "session.json"):
                with self.subTest(original=original, failed_name=failed_name):
                    temp, project, session, candidate = self.make_project(original)
                    try:
                        real_write = commit.atomic_write
                        def fail(path, *args, **kwargs):
                            if path.name == failed_name:
                                raise OSError("injected record failure")
                            return real_write(path, *args, **kwargs)
                        with patch.object(commit, "atomic_write", side_effect=fail), patch.object(sys, "argv", [str(SCRIPT), "--project-root", str(project), "--session", str(session)]):
                            self.assertEqual(commit.main(), 2)
                        self.assertEqual((project / "DESIGN.md").read_bytes(), DESIGN)
                        result = self.invoke(project, session)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertEqual(json.loads(session.read_text())["phase"], "committed")
                        if original is not None:
                            self.assertEqual((session.parent / "backup/DESIGN.before.md").read_bytes(), original)
                    finally:
                        temp.cleanup()

    def test_recovery_does_not_overwrite_later_edit(self):
        temp, project, session, candidate = self.make_project(b"original")
        try:
            real_write = commit.atomic_write
            def fail(path, *args, **kwargs):
                if path.name == "commit-receipt.json": raise OSError("injected")
                return real_write(path, *args, **kwargs)
            with patch.object(commit, "atomic_write", side_effect=fail), patch.object(sys, "argv", [str(SCRIPT), "--project-root", str(project), "--session", str(session)]):
                self.assertEqual(commit.main(), 2)
            (project / "DESIGN.md").write_bytes(b"later edit")
            self.assertEqual(self.invoke(project, session).returncode, 1)
            self.assertEqual((project / "DESIGN.md").read_bytes(), b"later edit")
        finally:
            temp.cleanup()

    def test_retry_cleans_intent_after_cleanup_failure(self):
        temp, project, session, _ = self.make_project(b"old root")
        try:
            unlink = Path.unlink
            def fail(path, *args, **kwargs):
                if path.name == "commit-intent.json":
                    raise OSError("injected intent cleanup failure")
                return unlink(path, *args, **kwargs)
            with patch.object(Path, "unlink", fail), patch.object(sys, "argv", [str(SCRIPT), "--project-root", str(project), "--session", str(session)]):
                self.assertEqual(commit.main(), 2)
            self.assertEqual(json.loads(session.read_text())["phase"], "committed")
            intent = session.parent / "commit-intent.json"
            self.assertTrue(intent.exists())
            receipt_before = (session.parent / "commit-receipt.json").read_bytes()
            result = self.invoke(project, session)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("already-committed", result.stdout)
            self.assertFalse(intent.exists())
            self.assertEqual((session.parent / "commit-receipt.json").read_bytes(), receipt_before)
            self.assertEqual((project / "DESIGN.md").read_bytes(), DESIGN)
            self.assertEqual((session.parent / "backup/DESIGN.before.md").read_bytes(), b"old root")
        finally:
            temp.cleanup()

    def test_completed_commit_retains_mismatched_intent(self):
        temp, project, session, _ = self.make_project()
        try:
            self.assertEqual(self.invoke(project, session).returncode, 0)
            intent = session.parent / "commit-intent.json"
            intent.write_text('{"after_sha": "unrelated"}')
            result = self.invoke(project, session)
            self.assertEqual(result.returncode, 1)
            self.assertTrue(intent.exists())
            self.assertEqual((project / "DESIGN.md").read_bytes(), DESIGN)
        finally:
            temp.cleanup()

    def test_create_root_and_idempotent_rerun(self):
        temp, project, session, _ = self.make_project()
        try:
            result = self.invoke(project, session)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((project / "DESIGN.md").read_bytes(), DESIGN)
            receipt = json.loads((session.parent / "commit-receipt.json").read_text())
            self.assertTrue(receipt["root_changed"])
            self.assertIsNone(receipt["backup_path"])
            again = self.invoke(project, session)
            self.assertEqual(again.returncode, 0, again.stderr)
            self.assertIn("already-committed", again.stdout)
        finally:
            temp.cleanup()

    def test_existing_root_requires_permission_and_is_backed_up_with_mode(self):
        original = b"old design\n"
        temp, project, session, _ = self.make_project(original, approved=False)
        try:
            rejected = self.invoke(project, session)
            self.assertEqual(rejected.returncode, 1)
            self.assertEqual((project / "DESIGN.md").read_bytes(), original)
            data = json.loads(session.read_text())
            data["user_confirmation"]["replacement_approved"] = True
            session.write_text(json.dumps(data))
            accepted = self.invoke(project, session)
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            backup = session.parent / "backup/DESIGN.before.md"
            self.assertEqual(backup.read_bytes(), original)
            self.assertEqual(backup.stat().st_mode & 0o777, 0o640)
            self.assertEqual((project / "DESIGN.md").stat().st_mode & 0o777, 0o640)
        finally:
            temp.cleanup()

    def test_external_root_change_and_stale_candidate_are_rejected(self):
        original = b"old\n"
        temp, project, session, candidate = self.make_project(original)
        try:
            (project / "DESIGN.md").write_bytes(b"external edit\n")
            result = self.invoke(project, session)
            self.assertEqual(result.returncode, 1)
            self.assertIn("changed since", result.stderr)
            self.assertEqual((project / "DESIGN.md").read_bytes(), b"external edit\n")
        finally:
            temp.cleanup()
        temp, project, session, candidate = self.make_project()
        try:
            (candidate / "sample.html").write_text("changed")
            result = self.invoke(project, session)
            self.assertEqual(result.returncode, 1)
            self.assertIn("sample hash mismatch", result.stderr)
            self.assertFalse((project / "DESIGN.md").exists())
        finally:
            temp.cleanup()

    def test_symlink_candidate_and_root_are_rejected(self):
        temp, project, session, candidate = self.make_project()
        try:
            real = candidate.with_name("real-candidate")
            candidate.rename(real)
            candidate.symlink_to(real, target_is_directory=True)
            result = self.invoke(project, session)
            self.assertEqual(result.returncode, 1)
            self.assertIn("symbolic link", result.stderr)
        finally:
            temp.cleanup()
        temp, project, session, _ = self.make_project(b"old\n")
        try:
            outside = project / "outside.md"
            outside.write_text("outside")
            (project / "DESIGN.md").unlink()
            (project / "DESIGN.md").symlink_to(outside)
            result = self.invoke(project, session)
            self.assertEqual(result.returncode, 1)
            self.assertIn("symbolic link", result.stderr)
            self.assertEqual(outside.read_text(), "outside")
        finally:
            temp.cleanup()

    def test_active_lock_and_incomplete_review_reject(self):
        temp, project, session, candidate = self.make_project()
        try:
            (project / ".design-curator-commit.lock").write_text("active")
            result = self.invoke(project, session)
            self.assertEqual(result.returncode, 1)
            self.assertIn("active lock", result.stderr)
            (project / ".design-curator-commit.lock").unlink()
            review = json.loads((candidate / "review.json").read_text())
            review["checks"] = review["checks"][:-1]
            (candidate / "review.json").write_text(json.dumps(review))
            result = self.invoke(project, session)
            self.assertEqual(result.returncode, 1)
            self.assertIn("lacks passing required checks", result.stderr)
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
