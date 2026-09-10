#!/usr/bin/env python3
"""Shared, dependency-light helpers for design-curator."""
from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import yaml

REF_RE = re.compile(r"\{([A-Za-z_][A-Za-z0-9_-]*(?:\.[A-Za-z0-9_-]+)*)\}")


def reference_path(value: str) -> str:
    # Upstream prose uses singular component.* for the components mapping.
    return "components." + value[len("component."):] if value.startswith("component.") else value
DIMENSION_RE = re.compile(r"^-?\d+(?:\.\d+)?(?:px|em|rem)$")
SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.-]*$")
KNOWN_GROUPS = ("colors", "typography", "rounded", "spacing", "components")


class DesignError(Exception):
    """Expected validation or safety failure."""


class UniqueSafeLoader(yaml.SafeLoader):
    pass


def _unique_mapping(loader: UniqueSafeLoader, node: yaml.Node, deep: bool = False) -> dict[Any, Any]:
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:  # type: ignore[attr-defined]
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            mark = getattr(key_node, "start_mark", None)
            where = f" at line {mark.line + 1}" if mark else ""
            raise DesignError(f"duplicate YAML key {key!r}{where}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueSafeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def json_dump(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def parse_frontmatter_bytes(data: bytes, source: str = "<bytes>") -> tuple[dict[str, Any], str, int]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DesignError(f"{source}: not UTF-8: {exc}") from exc
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise DesignError(f"{source}: missing opening frontmatter delimiter")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        raise DesignError(f"{source}: missing closing frontmatter delimiter")
    yaml_text = "".join(lines[1:end])
    try:
        value = yaml.load(yaml_text, Loader=UniqueSafeLoader)
    except DesignError:
        raise
    except yaml.YAMLError as exc:
        raise DesignError(f"{source}: invalid YAML: {exc}") from exc
    if not isinstance(value, dict):
        raise DesignError(f"{source}: frontmatter must be a mapping")
    return value, "".join(lines[end + 1 :]), end + 1


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str, int]:
    return parse_frontmatter_bytes(path.read_bytes(), str(path))


def lookup(root: Any, dotted: str) -> tuple[bool, Any]:
    value = root
    for segment in dotted.split("."):
        if not isinstance(value, dict) or segment not in value:
            return False, None
        value = value[segment]
    return True, value


def walk_strings(value: Any, path: str = "") -> Iterator[tuple[str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk_strings(child, f"{path}.{key}" if path else str(key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_strings(child, f"{path}[{index}]")
    elif isinstance(value, str):
        yield path, value


def validate_references(frontmatter: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    graph: dict[str, set[str]] = {}
    for location, value in walk_strings(frontmatter):
        refs = [reference_path(ref) for ref in REF_RE.findall(value)]
        if refs:
            graph.setdefault(location, set()).update(refs)
        for ref in refs:
            exists, target = lookup(frontmatter, ref)
            if not exists:
                findings.append({"code": "missing-reference", "severity": "error", "path": location, "reference": ref})
            elif isinstance(target, dict) and not (
                location.startswith("components.") and ref.startswith("typography.") and ref.count(".") == 1
            ):
                findings.append({"code": "invalid-group-reference", "severity": "error", "path": location, "reference": ref})
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, trail: list[str]) -> None:
        if node in visiting:
            start = trail.index(node) if node in trail else 0
            findings.append({"code": "reference-cycle", "severity": "error", "path": node, "cycle": trail[start:] + [node]})
            return
        if node in visited:
            return
        visiting.add(node)
        for target in graph.get(node, set()):
            if target in graph:
                visit(target, trail + [node])
        visiting.remove(node)
        visited.add(node)

    for node in sorted(graph):
        visit(node, [])
    unique = {json.dumps(item, sort_keys=True): item for item in findings}
    return list(unique.values())


def validate_types(frontmatter: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for group in KNOWN_GROUPS:
        if group in frontmatter and not isinstance(frontmatter[group], dict):
            findings.append({"code": "invalid-group-type", "severity": "error", "path": group, "expected": "mapping"})
    for required in ("name", "description"):
        value = frontmatter.get(required)
        if not isinstance(value, str) or not value.strip():
            findings.append({"code": "missing-required", "severity": "error", "path": required})
    typography = frontmatter.get("typography", {})
    if isinstance(typography, dict):
        for name, token in typography.items():
            path = f"typography.{name}"
            if not isinstance(token, dict):
                findings.append({"code": "invalid-token-type", "severity": "error", "path": path, "expected": "mapping"})
                continue
            for prop in ("fontSize", "letterSpacing"):
                value = token.get(prop)
                unitless_zero = prop == "letterSpacing" and value == 0 and not isinstance(value, bool)
                if prop in token and not unitless_zero and not (isinstance(value, str) and DIMENSION_RE.fullmatch(value)):
                    findings.append({"code": "invalid-dimension", "severity": "error", "path": f"{path}.{prop}", "value": value})
            if "fontWeight" in token and (isinstance(token["fontWeight"], bool) or not isinstance(token["fontWeight"], (int, float))):
                findings.append({"code": "invalid-font-weight", "severity": "error", "path": f"{path}.fontWeight"})
            if "lineHeight" in token and not (isinstance(token["lineHeight"], (int, float)) and not isinstance(token["lineHeight"], bool)) and not (isinstance(token["lineHeight"], str) and DIMENSION_RE.fullmatch(token["lineHeight"])):
                findings.append({"code": "invalid-line-height", "severity": "error", "path": f"{path}.lineHeight", "value": token["lineHeight"]})
            for prop in ("fontSize", "fontWeight", "lineHeight", "letterSpacing"):
                if prop not in token:
                    findings.append({"code": "unresolved-property", "severity": "warning", "path": f"{path}.{prop}"})
    for group in ("spacing", "rounded"):
        values = frontmatter.get(group, {})
        if isinstance(values, dict):
            for name, value in values.items():
                if not ((isinstance(value, (int, float)) and not isinstance(value, bool)) or (isinstance(value, str) and DIMENSION_RE.fullmatch(value))):
                    findings.append({"code": "invalid-dimension", "severity": "error", "path": f"{group}.{name}", "value": value})
    for key in frontmatter:
        if key not in {"version", "name", "description", *KNOWN_GROUPS}:
            findings.append({"code": "unknown-top-level-key", "severity": "warning", "path": str(key)})
    return findings


def validate_colors(frontmatter: dict[str, Any]) -> list[dict[str, Any]]:
    """Check hex and legacy comma rgb/hsl; leave other CSS syntax explicit."""
    findings = []
    colors = frontmatter.get("colors", {})
    if not isinstance(colors, dict):
        return findings
    number = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
    for name, value in colors.items():
        code, severity = "color-not-checked", "warning"
        if isinstance(value, str):
            text = value.strip()
            if REF_RE.fullmatch(text) or text in {"transparent", "currentColor"}:
                continue
            if text.startswith("#"):
                if re.fullmatch(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})", text):
                    continue
                code, severity = "invalid-color", "error"
            else:
                match = re.fullmatch(r"(rgba?|hsla?)\((.*)\)", text, re.IGNORECASE)
                if match:
                    function, args = match.groups()
                    function, args = function.lower(), args.strip()
                    # Nested CSS functions, relative colors and space/slash syntax
                    # are outside this small checker, not necessarily invalid.
                    unsupported = "(" in args or "/" in args or args.lower().startswith("from ")
                    if "," in args and not unsupported:
                        parts = [x.strip().lower() for x in args.split(",")]
                        # rgb/rgba and hsl/hsla are aliases; alpha is optional for both.
                        valid = len(parts) in (3, 4)
                        for i, part in enumerate(parts):
                            if function.startswith("hsl") and i == 0:
                                pattern = number + r"(?:deg|grad|rad|turn)?"
                            elif function.startswith("hsl") and i in (1, 2):
                                pattern = number + "%"
                            else:
                                pattern = number + "%?"
                            valid = valid and bool(re.fullmatch(pattern, part))
                        if function.startswith("rgb") and len(parts) >= 3:
                            # Legacy comma channels must all be numbers or all percentages.
                            valid = valid and len({p.endswith("%") for p in parts[:3]}) == 1
                        if valid:
                            continue
                        code, severity = "invalid-color", "error"
                    elif not unsupported and re.fullmatch(r"[A-Za-z_-]+", args) and args.lower() != "none":
                        code, severity = "invalid-color", "error"
        else:
            code, severity = "invalid-color", "error"
        findings.append({"code": code, "severity": severity, "path": f"colors.{name}", "value": value})
    return findings


def strip_code_fences(markdown: str) -> str:
    output: list[str] = []
    in_fence = False
    marker = ""
    for line in markdown.splitlines():
        match = re.match(r"^\s*(```+|~~~+)", line)
        if match:
            token = match.group(1)
            if not in_fence:
                in_fence, marker = True, token[0]
            elif token[0] == marker:
                in_fence = False
            continue
        if not in_fence:
            output.append(line)
    return "\n".join(output)


def validate_prose_references(frontmatter: dict[str, Any], body: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for line_no, line in enumerate(strip_code_fences(body).splitlines(), 1):
        for raw_ref in REF_RE.findall(line):
            ref = reference_path(raw_ref)
            if ref.split(".")[0] not in KNOWN_GROUPS:
                findings.append({"code": "ambiguous-prose-reference", "severity": "warning", "line": line_no, "reference": raw_ref})
            elif not lookup(frontmatter, ref)[0]:
                findings.append({"code": "missing-prose-reference", "severity": "error", "line": line_no, "reference": raw_ref})
            elif ref in KNOWN_GROUPS:
                findings.append({"code": "invalid-group-reference", "severity": "error", "line": line_no, "reference": ref})
    return findings


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    output: dict[str, Any] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            output.update(flatten(child, f"{prefix}.{key}" if prefix else str(key)))
    else:
        output[prefix] = value
    return output


def heading_list(markdown: str) -> list[str]:
    return [line.strip() for line in strip_code_fences(markdown).splitlines() if re.match(r"^#{1,6}\s+", line)]


def resolve_within(root: Path, relative: str | Path, *, must_exist: bool = True) -> Path:
    root = root.resolve(strict=True)
    candidate = root / relative
    resolved = candidate.resolve(strict=must_exist)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise DesignError(f"path escapes root: {relative}") from exc
    return resolved


def ensure_regular_no_symlink(path: Path) -> None:
    if path.is_symlink():
        raise DesignError(f"symbolic link is not allowed: {path}")
    info = path.stat()
    if not stat.S_ISREG(info.st_mode):
        raise DesignError(f"regular file required: {path}")


@contextmanager
def exclusive_lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    try:
        fd = os.open(path, flags, 0o600)
    except FileExistsError as exc:
        raise DesignError(f"active lock exists: {path}") from exc
    try:
        os.write(fd, f"pid={os.getpid()}\n".encode())
        os.fsync(fd)
        os.close(fd)
        fd = -1
        yield
    finally:
        if fd >= 0:
            os.close(fd)
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def atomic_write(path: Path, data: bytes, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(temp, flags, mode if mode is not None else 0o666)
    try:
        with os.fdopen(fd, "wb", closefd=False) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        if mode is not None:
            os.chmod(temp, mode)
        os.replace(temp, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        try:
            os.close(fd)
        except OSError:
            pass
        temp.unlink(missing_ok=True)
