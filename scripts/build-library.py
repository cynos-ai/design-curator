#!/usr/bin/env python3
"""Build the deterministic 74-document design library and descriptive index."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

from designlib import (
    DesignError, exclusive_lock, json_dump, parse_frontmatter_bytes,
    resolve_within, sha256_bytes, sha256_file, validate_references, validate_types,
)

REPO = "https://github.com/VoltAgent/awesome-design-md"
COMMIT = "8147538b4226ae41e2487a9179e3bcc1f68e8554"
ENTRY_RE = re.compile(r"^- \[\*\*(.+?)\*\*\]\(https://getdesign\.md/([^/]+)/design-md\)")
SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.-]*$")


def sha(path: Path) -> str:
    return sha256_file(path)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DesignError(f"cannot read JSON {path}: {exc}") from exc


def parse_readme(path: Path) -> dict[str, dict[str, str | None]]:
    records: dict[str, dict[str, str | None]] = {}
    in_collection = False
    category: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() == "## Collection":
            in_collection = True
            continue
        if not in_collection:
            continue
        if line.startswith("## "):
            break
        if line.startswith("### "):
            category = line[4:].strip()
            continue
        match = ENTRY_RE.match(line)
        if match:
            name, slug = match.groups()
            if slug in records:
                raise DesignError(f"duplicate README slug: {slug}")
            records[slug] = {"display_name": name, "category": category}
    return records


def raw_format(path: Path) -> str:
    data = path.read_bytes()
    if not data.startswith(b"---"):
        return "prose-only"
    try:
        parse_frontmatter_bytes(data, str(path))
        return "yaml"
    except DesignError:
        return "invalid-yaml"


def source_origin(slug: str, overlay: dict[str, Any] | None, note: dict[str, Any] | None, source_path: str) -> dict[str, Any]:
    if overlay and overlay["kind"] == "prepend-frontmatter" and note:
        mapping = next((item for item in note.get("mappings", []) if item.get("path") == "description"), {})
        return {"kind": "source-prose-excerpt", "source_path": source_path, "source_lines": mapping.get("source_lines")}
    return {"kind": "upstream-frontmatter", "source_path": source_path, "source_lines": None}


def create_outputs(root: Path, staging: Path) -> tuple[dict[str, bytes], dict[str, Any]]:
    assets = root / "assets"
    lock = load_json(assets / "source-lock.json")
    if lock.get("schema_version") != 1 or lock.get("repo") != REPO or lock.get("commit") != COMMIT:
        raise DesignError("source-lock schema/repository/commit mismatch")
    files = lock.get("files")
    overlays = lock.get("overlays")
    if not isinstance(files, list) or len(files) != 74 or not isinstance(overlays, list) or len(overlays) != 13:
        raise DesignError("source-lock must contain 74 files and 13 overlays")
    slugs = [item.get("slug") for item in files]
    if len(set(slugs)) != 74 or any(not isinstance(s, str) or not SLUG_RE.fullmatch(s) or ".." in s for s in slugs):
        raise DesignError("invalid or duplicate slug in source-lock")
    upstream_dir = assets / "upstream" / "design-md"
    if upstream_dir.is_symlink() or not upstream_dir.is_dir():
        raise DesignError("upstream design-md must be a real directory")
    actual: set[str] = set()
    unsafe: list[str] = []
    for child in upstream_dir.iterdir():
        design = child / "DESIGN.md"
        if child.is_symlink() or not child.is_dir() or design.is_symlink() or not design.is_file():
            unsafe.append(child.name)
        else:
            actual.add(child.name)
    expected = set(slugs)
    if actual != expected or unsafe:
        raise DesignError(f"source inventory mismatch: missing={sorted(expected-actual)}, extra={sorted(actual-expected)}, unsafe={sorted(unsafe)}")
    metadata = {item["path"]: item["sha256"] for item in lock.get("metadata_files", [])}
    if set(metadata) != {"README.md", "LICENSE"}:
        raise DesignError("source-lock metadata must contain README.md and LICENSE")
    for relative, expected_sha in metadata.items():
        lexical = assets / "upstream" / relative
        if lexical.is_symlink():
            raise DesignError(f"metadata symbolic link is not allowed: {relative}")
        path = resolve_within(assets / "upstream", relative)
        if sha(path) != expected_sha:
            raise DesignError(f"metadata hash mismatch: {relative}")
    readme = parse_readme(assets / "upstream" / "README.md")
    if len(readme) != 73:
        raise DesignError(f"expected 73 README entries, got {len(readme)}")
    overlay_by_slug = {item.get("slug"): item for item in overlays}
    if len(overlay_by_slug) != 13 or not set(overlay_by_slug).issubset(expected):
        raise DesignError("invalid overlay inventory")
    design_out = staging / "assets" / "design-md"
    entries: list[dict[str, Any]] = []
    output_bytes: dict[str, bytes] = {}
    for item in sorted(files, key=lambda value: value["slug"]):
        slug = item["slug"]
        source_rel = item["path"]
        if source_rel != f"design-md/{slug}/DESIGN.md":
            raise DesignError(f"unexpected source path for {slug}: {source_rel}")
        raw = resolve_within(assets / "upstream", source_rel)
        if sha(raw) != item["sha256"]:
            raise DesignError(f"raw hash mismatch: {slug}")
        overlay = overlay_by_slug.get(slug)
        notes_path: str | None = None
        note: dict[str, Any] | None = None
        effective = raw
        normalization = "none"
        if overlay:
            if overlay.get("source_sha256") != item["sha256"]:
                raise DesignError(f"overlay source hash mismatch: {slug}")
            overlay_lexical = assets / "overlays" / slug / "DESIGN.md"
            note_lexical = assets / "source-notes" / f"{slug}.json"
            if overlay_lexical.parent.is_symlink() or overlay_lexical.is_symlink() or note_lexical.is_symlink():
                raise DesignError(f"overlay/source note symbolic link is not allowed: {slug}")
            effective = resolve_within(assets / "overlays", Path(slug) / "DESIGN.md")
            if sha(effective) != overlay.get("normalized_sha256"):
                raise DesignError(f"overlay hash mismatch: {slug}")
            note_file = resolve_within(assets / "source-notes", f"{slug}.json")
            if sha(note_file) != overlay.get("source_map_sha256"): 
                raise DesignError(f"source note hash mismatch: {slug}")
            note = load_json(note_file)
            if note.get("slug") != slug or note.get("source_sha256") != item["sha256"]:
                raise DesignError(f"source note identity mismatch: {slug}")
            notes_path = f"assets/source-notes/{slug}.json"
            normalization = overlay["kind"]
        data = effective.read_bytes()
        frontmatter, _body, _ = parse_frontmatter_bytes(data, str(effective))
        findings = validate_types(frontmatter) + validate_references(frontmatter)
        blocking = [f for f in findings if f.get("severity") == "error"]
        if blocking:
            raise DesignError(f"effective document invalid: {slug}: {blocking[:3]}")
        info = readme.get(slug)
        if slug == "slack":
            info = {"display_name": "Slack", "category": None}
        if info is None:
            raise DesignError(f"slug absent from README without explicit supplement: {slug}")
        destination = design_out / slug / "DESIGN.md"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        relative_output = f"assets/design-md/{slug}/DESIGN.md"
        output_bytes[relative_output] = data
        entries.append({
            "slug": slug,
            "display_name": info["display_name"],
            "aliases": list(dict.fromkeys([info["display_name"], slug])),
            "category": info["category"],
            "design_path": relative_output,
            "source_path": source_rel,
            "source_sha256": item["sha256"],
            "effective_sha256": sha256_bytes(data),
            "raw_format": raw_format(raw),
            "normalization": normalization,
            "description": frontmatter["description"],
            "description_origin": source_origin(slug, overlay, note, source_rel),
            "source_notes_path": notes_path,
            "reference_findings": [f for f in findings if f.get("severity") != "error"],
        })
    if set(readme) - expected:
        raise DesignError(f"README contains unknown entries: {sorted(set(readme)-expected)}")
    catalog = {"schema_version": 1, "source_repo": REPO, "source_commit": COMMIT, "count": len(entries), "entries": entries}
    catalog_bytes = json_dump(catalog)
    output_bytes["assets/catalog.json"] = catalog_bytes
    index_lines = [
        "# Design Curator Index", "", f"> Source: `{REPO}@{COMMIT}`", "> This is a descriptive catalog, not a ranking. Read each shortlisted DESIGN.md and its source notes in full before use.", "",
    ]
    categories: dict[str, int] = {}
    for entry in entries:
        name = entry["category"] or "Uncategorized"
        categories[name] = categories.get(name, 0) + 1
    index_lines += ["## Categories", ""] + [f"- {name}: {count}" for name, count in sorted(categories.items())] + ["", "## Designs", ""]
    for entry in entries:
        origin = "original frontmatter.description" if entry["description_origin"]["kind"] == "upstream-frontmatter" else "verbatim source prose excerpt"
        index_lines += [
            f"### {entry['display_name']} (`{entry['slug']}`)", "",
            f"Category: {entry['category'] or 'Uncategorized'}  ",
            f"Specification: `{entry['design_path']}`  ",
            f"Description source: {origin}", "",
            "> " + str(entry["description"]).replace("\n", "\n> "), "",
            f"Source notes: `{entry['source_notes_path']}`" if entry["source_notes_path"] else "Source notes: no overlay; full-text review still required", "",
        ]
    index_bytes = ("\n".join(index_lines).rstrip() + "\n").encode("utf-8")
    output_bytes["INDEX.md"] = index_bytes
    receipt_files = {key: sha256_bytes(value) for key, value in sorted(output_bytes.items())}
    receipt = {"schema_version": 1, "source_repo": REPO, "source_commit": COMMIT, "count": 74, "files": receipt_files}
    receipt_bytes = json_dump(receipt)
    output_bytes["assets/build-receipt.json"] = receipt_bytes
    (staging / "assets").mkdir(parents=True, exist_ok=True)
    (staging / "assets" / "catalog.json").write_bytes(catalog_bytes)
    (staging / "INDEX.md").write_bytes(index_bytes)
    (staging / "assets" / "build-receipt.json").write_bytes(receipt_bytes)
    return output_bytes, receipt


def check_outputs(root: Path, expected: dict[str, bytes]) -> None:
    mismatches: list[str] = []
    for relative, data in expected.items():
        path = root / relative
        if not path.is_file() or path.is_symlink() or path.read_bytes() != data:
            mismatches.append(relative)
    expected_designs = {p for p in expected if p.startswith("assets/design-md/")}
    design_root = root / "assets" / "design-md"
    actual_designs: set[str] = set()
    unsafe_entries: list[str] = []
    if design_root.exists():
        for path in design_root.rglob("*"):
            if path.is_symlink():
                unsafe_entries.append(path.relative_to(root).as_posix())
            elif path.is_file():
                actual_designs.add(path.relative_to(root).as_posix())
    if actual_designs != expected_designs or unsafe_entries:
        mismatches.append("assets/design-md inventory")
    if mismatches:
        raise DesignError(f"built outputs differ: {mismatches[:10]}")


def publish(root: Path, staging: Path) -> None:
    targets = [root / "assets" / "design-md", root / "assets" / "catalog.json", root / "INDEX.md", root / "assets" / "build-receipt.json"]
    staged = [staging / "assets" / "design-md", staging / "assets" / "catalog.json", staging / "INDEX.md", staging / "assets" / "build-receipt.json"]
    backup = root / f".build-backup-{os.getpid()}"
    backup.mkdir()
    moved: list[tuple[Path, Path]] = []
    installed: list[Path] = []
    try:
        for target in targets:
            if target.exists() or target.is_symlink():
                saved = backup / target.relative_to(root)
                saved.parent.mkdir(parents=True, exist_ok=True)
                os.replace(target, saved)
                moved.append((saved, target))
        for source, target in zip(staged, targets):
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(source, target)
            installed.append(target)
    except Exception:
        for target in reversed(installed):
            if target.is_dir(): shutil.rmtree(target, ignore_errors=True)
            else: target.unlink(missing_ok=True)
        for saved, target in reversed(moved):
            if saved.exists(): os.replace(saved, target)
        raise
    finally:
        shutil.rmtree(backup, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-root", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        root = Path(args.skill_root).resolve(strict=True)
        if not (root / "SKILL.md").is_file():
            raise DesignError(f"not a skill root: {root}")
        lock = root / ".build-library.lock"
        with exclusive_lock(lock):
            with tempfile.TemporaryDirectory(prefix=".tmp-build-", dir=root) as temp:
                staging = Path(temp)
                outputs, receipt = create_outputs(root, staging)
                if args.check:
                    check_outputs(root, outputs)
                else:
                    publish(root, staging)
                    check_outputs(root, outputs)
        print(json.dumps({"status": "consistent" if args.check else "built", "count": 74, "source_commit": receipt["source_commit"]}, sort_keys=True))
        return 0
    except DesignError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
