#!/usr/bin/env python3
"""Read-only structural validation and baseline diff for DESIGN.md."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from designlib import (
    DesignError, flatten, heading_list, parse_frontmatter, sha256_file,
    validate_prose_references, validate_references, validate_types,
)

COLOR_RE = re.compile(r"^(?:#[0-9A-Fa-f]{3,8}|rgba?\([^\n]+\)|hsla?\([^\n]+\)|transparent|currentColor)$")


def validate(path: Path) -> tuple[dict[str, Any], dict[str, Any], str]:
    if path.is_symlink() or not path.is_file():
        raise DesignError(f"regular non-symlink file required: {path}")
    frontmatter, body, _ = parse_frontmatter(path)
    findings = validate_types(frontmatter) + validate_references(frontmatter) + validate_prose_references(frontmatter, body)
    colors = frontmatter.get("colors", {})
    if isinstance(colors, dict):
        for name, value in colors.items():
            if isinstance(value, str) and value.startswith("{"):
                continue
            if not isinstance(value, str) or not COLOR_RE.fullmatch(value.strip()):
                findings.append({"code": "color-not-checked", "severity": "warning", "path": f"colors.{name}", "value": value})
    blocking = [item for item in findings if item.get("severity") == "error"]
    report = {
        "schema_version": 1,
        "file": str(path),
        "sha256": sha256_file(path),
        "status": "blocked" if blocking else "structurally-valid",
        "scope": "structure, known token types and references only; not visual/WCAG certification",
        "findings": findings,
        "blocking_findings": blocking,
    }
    return report, frontmatter, body


def baseline_diff(current_frontmatter: dict[str, Any], current_body: str, baseline: Path) -> dict[str, Any]:
    if baseline.is_symlink() or not baseline.is_file():
        raise DesignError(f"regular non-symlink baseline required: {baseline}")
    old, old_body, _ = parse_frontmatter(baseline)
    before, after = flatten(old), flatten(current_frontmatter)
    return {
        "baseline": str(baseline),
        "baseline_sha256": sha256_file(baseline),
        "tokens": {
            "added": {key: after[key] for key in sorted(after.keys() - before.keys())},
            "removed": {key: before[key] for key in sorted(before.keys() - after.keys())},
            "changed": {key: {"before": before[key], "after": after[key]} for key in sorted(before.keys() & after.keys()) if before[key] != after[key]},
        },
        "headings": {"before": heading_list(old_body), "after": heading_list(current_body)},
        "body_changed": old_body != current_body,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("design")
    parser.add_argument("--baseline")
    args = parser.parse_args()
    try:
        path = Path(args.design).resolve(strict=True)
        report, frontmatter, body = validate(path)
        if args.baseline:
            report["baseline_diff"] = baseline_diff(frontmatter, body, Path(args.baseline).resolve(strict=True))
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
        return 1 if report["blocking_findings"] else 0
    except DesignError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
