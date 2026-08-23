#!/usr/bin/env python3
"""Read-only diagnostic for Rongbao design Skill dependencies.

This script deliberately has no network or installation behavior.  It reads
the local registry and checks common Codex/agent/sibling-repository locations.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_DIR = SKILL_DIR.parent
REGISTRY_PATH = SKILL_DIR / "references" / "design-dependencies.json"


def _unique_paths(paths: list[Path]) -> list[Path]:
    result: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        resolved = path.expanduser().resolve(strict=False)
        key = os.path.normcase(str(resolved))
        if key not in seen:
            seen.add(key)
            result.append(resolved)
    return result


def _candidate_paths(dependency: dict[str, Any]) -> list[Path]:
    skill_id = str(dependency["skill_id"])
    skill_path = Path(str(dependency["path"]))
    repo = str(dependency["repo"])
    repo_name = repo.rsplit("/", 1)[-1]

    candidates: list[Path] = []
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        candidates.append(Path(codex_home) / "skills" / skill_id)
    candidates.append(Path.home() / ".codex" / "skills" / skill_id)
    candidates.append(Path.home() / ".agents" / "skills" / skill_id)
    candidates.append(REPO_DIR.parent / repo_name / skill_path)
    return _unique_paths(candidates)


def _frontmatter_name(skill_file: Path) -> str | None:
    """Read only the YAML frontmatter name without requiring PyYAML."""

    try:
        lines = skill_file.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError):
        return None
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, separator, value = line.partition(":")
        if separator and key.strip() == "name":
            return value.strip().strip("'\"")
    return None


def _load_registry() -> dict[str, Any]:
    with REGISTRY_PATH.open("r", encoding="utf-8") as handle:
        registry = json.load(handle)
    if not isinstance(registry, dict):
        raise ValueError("registry root must be an object")
    if registry.get("version") != 1:
        raise ValueError("registry version must be 1")
    dependencies = registry.get("dependencies")
    if not isinstance(dependencies, list):
        raise ValueError("registry dependencies must be a list")
    for dependency in dependencies:
        required = {"skill_id", "repo", "path", "ref", "capabilities"}
        if not isinstance(dependency, dict) or not required.issubset(dependency):
            raise ValueError("each dependency needs skill_id, repo, path, ref, capabilities")
        if not isinstance(dependency["ref"], str) or not dependency["ref"].strip():
            raise ValueError("dependency ref must be a non-empty string")
        if not isinstance(dependency["capabilities"], list):
            raise ValueError("dependency capabilities must be a list")
    return registry


def diagnose() -> dict[str, Any]:
    registry = _load_registry()
    dependencies: list[dict[str, Any]] = []
    for dependency in registry["dependencies"]:
        locations = []
        for candidate in _candidate_paths(dependency):
            skill_file = candidate / "SKILL.md"
            skill_name = _frontmatter_name(skill_file) if skill_file.is_file() else None
            locations.append(
                {
                    "path": str(candidate),
                    "exists": candidate.is_dir(),
                    "skill_md": skill_file.is_file(),
                    "name": skill_name,
                    "name_match": skill_name == dependency["skill_id"],
                }
            )
        available = any(location["skill_md"] and location["name_match"] for location in locations)
        dependencies.append(
            {
                "skill_id": dependency["skill_id"],
                "repo": dependency["repo"],
                "path": dependency["path"],
                "ref": dependency["ref"],
                "capabilities": dependency["capabilities"],
                "source": f"https://github.com/{dependency['repo']}/tree/{dependency['ref']}/{dependency['path']}",
                "available": available,
                "locations": locations,
            }
        )
    return {
        "registry": str(REGISTRY_PATH),
        "version": registry["version"],
        "dependencies": dependencies,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only Rongbao dependency doctor")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON")
    parser.add_argument("--strict", action="store_true", help="exit 1 when a dependency is missing")
    args = parser.parse_args(argv)

    try:
        report = diagnose()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"doctor error: {exc}", file=sys.stderr)
        return 2

    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for dependency in report["dependencies"]:
            state = "available" if dependency["available"] else "missing"
            print(f"{dependency['skill_id']}: {state} ({', '.join(dependency['capabilities'])})")

    if args.strict and any(not dependency["available"] for dependency in report["dependencies"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
