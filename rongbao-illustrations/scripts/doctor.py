#!/usr/bin/env python3
"""Read-only diagnostic for Rongbao design Skill dependencies.

This script deliberately has no network or installation behavior.  It reads
the local registry and checks common Codex/agent/sibling-repository locations.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_DIR = SKILL_DIR.parent
REGISTRY_PATH = SKILL_DIR / "references" / "design-dependencies.json"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from character_router import inspect_registry as inspect_character_registry
from dependency_utils import (
    dependency_candidate_paths,
    frontmatter_name,
    inspect_dependency,
    load_dependency_registry,
)


# Keep these wrappers for callers that used the original read-only helpers.
def _candidate_paths(dependency: dict[str, Any]) -> list[Path]:
    return dependency_candidate_paths(dependency, skill_root=SKILL_DIR)


def _frontmatter_name(skill_file: Path) -> str | None:
    return frontmatter_name(skill_file)


def _load_registry() -> dict[str, Any]:
    return load_dependency_registry(REGISTRY_PATH)


def diagnose(
    *,
    registry: dict[str, Any] | None = None,
    skill_dir: Path = SKILL_DIR,
    environment: dict[str, str] | None = None,
    home: Path | None = None,
) -> dict[str, Any]:
    registry = _load_registry() if registry is None else registry
    characters = inspect_character_registry()
    dependencies = [
        inspect_dependency(
            dependency,
            skill_root=skill_dir,
            environment=environment,
            home=home,
        )
        for dependency in registry["dependencies"]
    ]
    return {
        "registry": str(REGISTRY_PATH),
        "version": registry["version"],
        "dependencies": dependencies,
        "characters": characters,
    }


def strict_dependency_failure(dependencies: list[dict[str, Any]]) -> bool:
    """Required missing and every invalid dependency block strict mode.

    Optional dependencies may be missing by design, but a present dependency
    with a wrong Skill id or malformed installation remains an error.
    """

    return any(
        dependency["status"] == "invalid"
        or (dependency["status"] == "missing" and not dependency["optional"])
        for dependency in dependencies
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only Rongbao dependency doctor")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 when a dependency or character registration is invalid",
    )
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
            state = dependency["status"]
            optional = ", optional" if dependency["optional"] else ""
            print(f"{dependency['skill_id']}: {state}{optional} ({', '.join(dependency['capabilities'])})")
        character_state = "valid" if report["characters"]["valid"] else "invalid"
        default_character = report["characters"].get("default_character")
        print(f"characters: {character_state} (default={default_character})")

    if args.strict and (
        strict_dependency_failure(report["dependencies"]) or not report["characters"]["valid"]
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
