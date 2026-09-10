#!/usr/bin/env python3
"""Create a deterministic, runtime-only design-curator Skill ZIP."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import zipfile
from pathlib import Path

FIXED_TIME = (1980, 1, 1, 0, 0, 0)
ROOT_NAME = "design-curator"
DIRECT_FILES = (
    "SKILL.md",
    "INDEX.md",
    "requirements.txt",
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "assets/UPSTREAM-LICENSE.txt",
    "assets/source-lock.json",
    "assets/catalog.json",
    "assets/build-receipt.json",
    "scripts/build-library.py",
    "scripts/commit-design.py",
    "scripts/designlib.py",
    "scripts/validate-design.py",
)
DIRECTORIES = (
    "references",
    "assets/upstream",
    "assets/overlays",
    "assets/source-notes",
    "assets/design-md",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def validate_version(value: str) -> str:
    if not re.fullmatch(r"[0-9A-Za-z][0-9A-Za-z._-]{0,63}", value):
        raise ValueError("version must be 1-64 safe filename characters")
    return value


def add_file(files: dict[str, bytes], root: Path, source: Path, destination: str | None = None) -> None:
    if source.is_symlink() or not source.is_file():
        raise ValueError(f"regular non-symlink file required: {source}")
    relative = destination or source.relative_to(root).as_posix()
    if relative in files:
        raise ValueError(f"duplicate package path: {relative}")
    files[relative] = source.read_bytes()


def collect(root: Path) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    add_file(files, root, root / "packaging/README.md", "README.md")
    for relative in DIRECT_FILES:
        add_file(files, root, root / relative)
    for relative in DIRECTORIES:
        directory = root / relative
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError(f"real directory required: {directory}")
        for path in sorted(directory.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"symbolic links are forbidden in package: {path}")
            if path.is_file():
                add_file(files, root, path)
    designs = [name for name in files if re.fullmatch(r"assets/design-md/[^/]+/DESIGN\.md", name)]
    if len(designs) != 74:
        raise ValueError(f"runtime package must contain 74 effective designs, got {len(designs)}")
    forbidden = ("examples/", "tests/", "attachments/", "assets/audit/", ".git/")
    if any(name.startswith(forbidden) for name in files):
        raise ValueError("development-only content entered runtime package")
    return files


def checksum_text(files: dict[str, bytes]) -> bytes:
    return "".join(f"{sha256(files[name])}  {name}\n" for name in sorted(files)).encode("utf-8")


def zip_info(name: str, executable: bool = False) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(f"{ROOT_NAME}/{name}", FIXED_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    mode = 0o755 if executable else 0o644
    info.external_attr = (stat.S_IFREG | mode) << 16
    info.flag_bits |= 0x800
    return info


def write_zip(output: Path, files: dict[str, bytes], version: str, source_commit: str) -> None:
    payload_hashes = {name: sha256(data) for name, data in sorted(files.items())}
    manifest = {
        "schema_version": 1,
        "package": ROOT_NAME,
        "version": version,
        "source_commit": source_commit,
        "design_count": 74,
        "payload_file_count": len(files),
        "payload_bytes": sum(len(data) for data in files.values()),
        "files": payload_hashes,
        "excluded": ["examples", "tests", "attachments", "assets/audit", "IMPLEMENTATION-SPEC.md", "TEST-RESULTS.md", "RELEASE-VALIDATION.json"],
    }
    package_files = dict(files)
    package_files["PACKAGE-MANIFEST.json"] = json_bytes(manifest)
    package_files["PACKAGE-CHECKSUMS.sha256"] = checksum_text(package_files)
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_name(f".{output.name}.tmp-{os.getpid()}")
    temp.unlink(missing_ok=True)
    try:
        with zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name, data in sorted(package_files.items()):
                executable = name.startswith("scripts/") and name.endswith(".py")
                archive.writestr(zip_info(name, executable), data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        temp.replace(output)
    finally:
        temp.unlink(missing_ok=True)


def verify_zip(path: Path) -> dict[str, object]:
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError("ZIP CRC verification failed")
        names = archive.namelist()
        if len(names) != len(set(names)) or any(not name.startswith(f"{ROOT_NAME}/") for name in names):
            raise ValueError("invalid ZIP path inventory")
        raw = {name[len(ROOT_NAME) + 1 :]: archive.read(name) for name in names}
        manifest = json.loads(raw["PACKAGE-MANIFEST.json"])
        expected = raw["PACKAGE-CHECKSUMS.sha256"].decode("utf-8").splitlines()
        for line in expected:
            digest, name = line.split("  ", 1)
            if name not in raw or sha256(raw[name]) != digest:
                raise ValueError(f"inner checksum mismatch: {name}")
        if len([name for name in raw if re.fullmatch(r"assets/design-md/[^/]+/DESIGN\.md", name)]) != 74:
            raise ValueError("verified ZIP does not contain 74 designs")
    return {"file_count": len(names), "design_count": manifest["design_count"], "payload_file_count": manifest["payload_file_count"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", default=".")
    parser.add_argument("--version", required=True, type=validate_version)
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        root = Path(args.skill_root).resolve(strict=True)
        if not (root / "SKILL.md").is_file():
            raise ValueError(f"not a design-curator Skill root: {root}")
        check = subprocess.run(
            [sys.executable, str(root / "scripts/build-library.py"), "--skill-root", str(root), "--check"],
            text=True, capture_output=True,
        )
        if check.returncode:
            raise ValueError(f"library check failed: {check.stderr.strip()}")
        receipt = json.loads((root / "assets/build-receipt.json").read_text(encoding="utf-8"))
        files = collect(root)
        output = Path(args.output).expanduser() if args.output else root / "dist" / f"design-curator-skill-{args.version}.zip"
        if not output.is_absolute():
            output = Path.cwd() / output
        write_zip(output, files, args.version, receipt["source_commit"])
        verified = verify_zip(output)
        result = {
            "status": "packaged",
            "output": str(output.resolve()),
            "sha256": sha256(output.read_bytes()),
            "bytes": output.stat().st_size,
            "version": args.version,
            **verified,
        }
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
