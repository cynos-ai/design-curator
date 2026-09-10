#!/usr/bin/env python3
"""Safely commit a reviewed candidate DESIGN.md into a project root."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import sys
from pathlib import Path
from typing import Any

from designlib import (
    DesignError, atomic_write, canonical_json, exclusive_lock, json_dump,
    parse_frontmatter, resolve_within, sha256_bytes, sha256_file,
    validate_prose_references, validate_references, validate_types,
)

READY = {"ready-machine-verified", "ready-user-reviewed"}


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DesignError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise DesignError(f"JSON object required: {path}")
    return value


def reject_symlink_chain(root: Path, path: Path) -> None:
    relative = path.absolute().relative_to(root.absolute())
    cursor = root.absolute()
    for part in relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise DesignError(f"symbolic link is not allowed: {cursor}")


def bundle(candidate_dir: Path) -> tuple[str, str, dict[str, str]]:
    sample = candidate_dir / "sample.html"
    if sample.is_symlink() or not sample.is_file():
        raise DesignError("candidate sample.html must be a regular file")
    mapping = {"sample.html": sha256_file(sample)}
    assets = candidate_dir / "assets"
    if assets.exists():
        if assets.is_symlink() or not assets.is_dir():
            raise DesignError("candidate assets must be a real directory")
        for path in sorted(assets.rglob("*")):
            if path.is_symlink():
                raise DesignError(f"symbolic links are not allowed in candidate assets: {path}")
            if path.is_file():
                mapping[path.relative_to(candidate_dir).as_posix()] = sha256_file(path)
    return mapping["sample.html"], sha256_bytes(canonical_json(mapping)), {k: v for k, v in mapping.items() if k != "sample.html"}


def candidate_from(session: dict[str, Any]) -> dict[str, Any]:
    selected = session.get("selected_candidate")
    candidates = session.get("candidates")
    if not isinstance(selected, str) or not isinstance(candidates, list):
        raise DesignError("selected_candidate and candidates are required")
    matches = [item for item in candidates if isinstance(item, dict) and item.get("id") == selected]
    if len(matches) != 1:
        raise DesignError("selected candidate not found or duplicated")
    return matches[0]


def current_root_state(root_file: Path) -> dict[str, Any]:
    if root_file.is_symlink():
        raise DesignError("project DESIGN.md may not be a symbolic link")
    if not root_file.exists():
        return {"exists": False, "sha256": None}
    if not root_file.is_file():
        raise DesignError("project DESIGN.md must be a regular file")
    return {"exists": True, "sha256": sha256_file(root_file)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--session", required=True)
    args = parser.parse_args()
    root_changed = False
    backup_path: str | None = None
    before_sha: str | None = None
    after_sha: str | None = None
    try:
        root = Path(args.project_root).resolve(strict=True)
        if not root.is_dir():
            raise DesignError("project root must be a directory")
        session_path = Path(args.session)
        if not session_path.is_absolute():
            session_path = root / session_path
        try:
            session_relative = session_path.absolute().relative_to(root)
        except ValueError as exc:
            raise DesignError("session path escapes project root") from exc
        reject_symlink_chain(root, session_path.absolute())
        session_path = resolve_within(root, session_relative)
        if ".design-samples" not in session_path.relative_to(root).parts:
            raise DesignError("session must be inside project/.design-samples")
        lock_path = root / ".design-curator-commit.lock"
        with exclusive_lock(lock_path):
            session = load_json(session_path)
            if Path(session.get("project_root", "")).resolve() != root:
                raise DesignError("session project_root mismatch")
            if session.get("phase") == "committed":
                receipt_path = session_path.parent / "commit-receipt.json"
                receipt = load_json(receipt_path)
                root_file = root / "DESIGN.md"
                if root_file.is_file() and sha256_file(root_file) == receipt.get("after_sha"):
                    print(json.dumps({**receipt, "status": "already-committed"}, ensure_ascii=False, sort_keys=True))
                    return 0
                raise DesignError("session says committed but receipt/root do not agree")
            if session.get("phase") != "selected":
                raise DesignError("session phase must be selected")
            candidate = candidate_from(session)
            relative = candidate.get("relative_path")
            if not isinstance(relative, str):
                raise DesignError("candidate relative_path missing")
            candidate_unresolved = session_path.parent / relative
            reject_symlink_chain(root, candidate_unresolved.absolute())
            candidate_dir = resolve_within(session_path.parent, relative)
            if candidate_dir.parent != session_path.parent:
                raise DesignError("candidate directory must be directly inside run directory")
            if session.get("run_id") != session_path.parent.name or session_path.parent.parent.name != ".design-samples":
                raise DesignError("session run_id/path mismatch")
            if candidate.get("review_path") != f"{relative}/review.json":
                raise DesignError("candidate review_path mismatch")
            design = candidate_dir / "DESIGN.md"
            review_path = candidate_dir / "review.json"
            for path in (design, review_path):
                if path.is_symlink() or not path.is_file():
                    raise DesignError(f"regular candidate file required: {path.name}")
            design_sha = sha256_file(design)
            sample_sha, bundle_sha, asset_hashes = bundle(candidate_dir)
            review = load_json(review_path)
            confirmation = session.get("user_confirmation")
            if not isinstance(confirmation, dict):
                raise DesignError("current user confirmation is required")
            expected = [candidate.get("current_design_sha256"), review.get("design_sha256"), confirmation.get("design_sha256")]
            if any(value != design_sha for value in expected):
                raise DesignError("candidate DESIGN hash does not match session, review and confirmation")
            if candidate.get("sample_sha256") != sample_sha or review.get("sample_sha256") != sample_sha:
                raise DesignError("sample hash mismatch")
            if any(value != bundle_sha for value in (candidate.get("sample_bundle_sha256"), review.get("sample_bundle_sha256"), confirmation.get("sample_bundle_sha256"))):
                raise DesignError("sample bundle hash mismatch")
            if review.get("asset_hashes") != asset_hashes:
                raise DesignError("review asset hash inventory mismatch")
            if confirmation.get("candidate_id") != candidate.get("id") or not isinstance(confirmation.get("confirmation_text"), str) or not confirmation["confirmation_text"].strip():
                raise DesignError("confirmation identity/text missing")
            required_checks = {"structure", "references", "prose-consistency", "fonts", "responsive", "interaction", "contrast", "content-authenticity"}
            checks = review.get("checks")
            check_ids = {item.get("id") for item in checks if isinstance(item, dict)} if isinstance(checks, list) else set()
            checks_by_id = {item.get("id"): item for item in checks if isinstance(item, dict)} if isinstance(checks, list) else {}
            bad_check_states = {key: checks_by_id.get(key, {}).get("status") for key in required_checks if checks_by_id.get(key, {}).get("status") not in {"pass", "not-applicable"}}
            if review.get("candidate_id") != candidate.get("id") or review.get("status") not in READY or review.get("blocking_findings") or not required_checks.issubset(check_ids) or bad_check_states:
                raise DesignError("review is not ready or lacks passing required checks")
            if not isinstance(review.get("accepted_limitations"), list) or not isinstance(review.get("external_assets"), list):
                raise DesignError("review limitations/external_assets must be lists")
            if not isinstance(confirmation.get("confirmed_at"), str) or "T" not in confirmation["confirmed_at"]:
                raise DesignError("confirmation timestamp missing")
            frontmatter, body, _ = parse_frontmatter(design)
            blocking = [item for item in validate_types(frontmatter) + validate_references(frontmatter) + validate_prose_references(frontmatter, body) if item.get("severity") == "error"]
            if blocking:
                raise DesignError(f"candidate failed structural validation: {blocking[:3]}")
            root_file = root / "DESIGN.md"
            actual_before = current_root_state(root_file)
            expected_before = session.get("root_design_before")
            if actual_before != expected_before:
                raise DesignError("project DESIGN.md changed since session started")
            if actual_before["exists"] and confirmation.get("replacement_approved") is not True:
                raise DesignError("explicit replacement approval is required")
            before_sha = actual_before["sha256"]
            backup = session_path.parent / "backup" / "DESIGN.before.md"
            if actual_before["exists"]:
                backup.parent.mkdir(parents=True, exist_ok=True)
                if backup.exists():
                    if backup.is_symlink() or sha256_file(backup) != before_sha:
                        raise DesignError("existing backup does not match original root DESIGN")
                else:
                    shutil.copyfile(root_file, backup)
                    os.chmod(backup, stat.S_IMODE(root_file.stat().st_mode))
                backup_path = backup.relative_to(root).as_posix()
            mode = stat.S_IMODE(root_file.stat().st_mode) if root_file.exists() else None
            # Last pre-write guard; the advisory lock only coordinates this tool.
            if current_root_state(root_file) != expected_before:
                raise DesignError("project DESIGN.md changed immediately before commit")
            atomic_write(root_file, design.read_bytes(), mode)
            root_changed = True
            after_sha = sha256_file(root_file)
            if after_sha != design_sha:
                raise OSError("root DESIGN hash mismatch after atomic replacement")
            receipt = {
                "schema_version": 1, "status": "committed", "root_changed": True,
                "project_design": "DESIGN.md", "backup_path": backup_path,
                "before_sha": before_sha, "after_sha": after_sha,
                "candidate_id": candidate["id"], "sample_bundle_sha256": bundle_sha,
                "recovery_required": False,
            }
            atomic_write(session_path.parent / "commit-receipt.json", json_dump(receipt), 0o600)
            session["phase"] = "committed"
            atomic_write(session_path, json_dump(session), stat.S_IMODE(session_path.stat().st_mode))
            print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
            return 0
    except DesignError as exc:
        print(json.dumps({"status": "rejected", "error": str(exc), "root_changed": root_changed, "backup_path": backup_path, "before_sha": before_sha, "after_sha": after_sha, "recovery_required": root_changed}, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "io-error", "error": str(exc), "root_changed": root_changed, "backup_path": backup_path, "before_sha": before_sha, "after_sha": after_sha, "recovery_required": root_changed}, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
