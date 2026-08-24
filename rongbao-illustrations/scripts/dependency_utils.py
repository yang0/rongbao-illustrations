#!/usr/bin/env python3
"""Shared dependency registry validation and installation probing helpers.

The helpers are deliberately read-only.  They describe where an optional
dependency would be installed and never download, copy, or modify a Skill.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Mapping


ROOT_PATH_MARKERS = {"", ".", "./", ".\\"}
SKILL_ID_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]*\Z")
REPO_PATTERN = re.compile(r"[^/\s]+/[^/\s]+\Z")


class DependencyRegistryError(ValueError):
    """Raised when the design dependency registry is malformed."""


def is_root_path(path: str) -> bool:
    """Return whether a dependency path means the repository root."""

    return path.strip() in ROOT_PATH_MARKERS


def dependency_install_name(dependency: Mapping[str, Any]) -> str:
    """Return the destination Skill name, preserving old entries."""

    install_name = dependency.get("install_name") or dependency.get("skill_id")
    return str(install_name)


def dependency_source_url(dependency: Mapping[str, Any]) -> str:
    """Build a clean GitHub source URL, omitting ``/.`` for root installs."""

    repo = str(dependency["repo"])
    ref = str(dependency["ref"])
    path = str(dependency.get("path", ""))
    if is_root_path(path):
        return f"https://github.com/{repo}/tree/{ref}"
    normalized_path = path.replace("\\", "/").strip("/")
    return f"https://github.com/{repo}/tree/{ref}/{normalized_path}"


def dependency_install_info(dependency: Mapping[str, Any]) -> dict[str, Any]:
    """Return machine-readable and copyable system skill-installer data."""

    repo = str(dependency["repo"])
    path = str(dependency["path"])
    install_name = dependency_install_name(dependency)
    ref = str(dependency["ref"])
    args = [
        "--repo",
        repo,
        "--path",
        path,
        "--name",
        install_name,
        "--ref",
        ref,
    ]
    command = "$skill-installer install " + " ".join(
        [f"--repo {repo}", f"--path {path}", f"--name {install_name}", f"--ref {ref}"]
    )
    return {
        "repo": repo,
        "path": path,
        "name": install_name,
        "ref": ref,
        "args": args,
        "command": command,
    }


def validate_dependency(dependency: Any, index: int = 0) -> list[str]:
    """Return schema errors for one dependency record."""

    if not isinstance(dependency, dict):
        return [f"dependency[{index}] must be an object"]
    required = {"skill_id", "repo", "path", "ref", "capabilities"}
    errors: list[str] = []
    missing = sorted(required.difference(dependency))
    if missing:
        errors.append(f"missing fields: {', '.join(missing)}")

    skill_id = dependency.get("skill_id")
    if not isinstance(skill_id, str) or not SKILL_ID_PATTERN.fullmatch(skill_id):
        errors.append("skill_id must use lowercase letters, digits, and hyphens")

    install_name = dependency.get("install_name", skill_id)
    if not isinstance(install_name, str) or not SKILL_ID_PATTERN.fullmatch(install_name):
        errors.append("install_name must use lowercase letters, digits, and hyphens")

    repo = dependency.get("repo")
    if not isinstance(repo, str) or not REPO_PATTERN.fullmatch(repo):
        errors.append("repo must use owner/repository form")

    path = dependency.get("path")
    if not isinstance(path, str) or not path.strip():
        errors.append("path must be a non-empty string")

    ref = dependency.get("ref")
    if not isinstance(ref, str) or not ref.strip():
        errors.append("ref must be a non-empty string")

    capabilities = dependency.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities or not all(
        isinstance(capability, str) and capability.strip() for capability in capabilities
    ):
        errors.append("capabilities must be a non-empty list of strings")

    optional = dependency.get("optional", False)
    if not isinstance(optional, bool):
        errors.append("optional must be a boolean when provided")

    reference_inputs = dependency.get("reference_inputs")
    if reference_inputs is not None:
        if not isinstance(reference_inputs, dict):
            errors.append("reference_inputs must be an object when provided")
        else:
            for role, paths in reference_inputs.items():
                if not isinstance(role, str) or not isinstance(paths, list) or not all(
                    isinstance(path_item, str) and path_item.strip() for path_item in paths
                ):
                    errors.append("reference_inputs values must be lists of non-empty strings")
    return errors


def load_dependency_registry(registry_path: Path) -> dict[str, Any]:
    """Load and validate the shared dependency registry."""

    with registry_path.open("r", encoding="utf-8") as handle:
        registry = json.load(handle)
    if not isinstance(registry, dict):
        raise DependencyRegistryError("registry root must be an object")
    if registry.get("version") != 1:
        raise DependencyRegistryError("registry version must be 1")
    dependencies = registry.get("dependencies")
    if not isinstance(dependencies, list):
        raise DependencyRegistryError("registry dependencies must be a list")
    errors: list[str] = []
    for index, dependency in enumerate(dependencies):
        errors.extend(f"dependency[{index}]: {error}" for error in validate_dependency(dependency, index))
    if errors:
        raise DependencyRegistryError("; ".join(errors))
    return registry


def dependency_candidate_paths(
    dependency: Mapping[str, Any],
    *,
    skill_root: Path,
    environment: Mapping[str, str] | None = None,
    home: Path | None = None,
) -> list[Path]:
    """Return deterministic installed locations for a dependency."""

    env = os.environ if environment is None else environment
    home_path = Path.home() if home is None else home
    install_name = dependency_install_name(dependency)
    skill_path = str(dependency["path"])
    repo_name = str(dependency["repo"]).rsplit("/", 1)[-1]
    candidates: list[Path] = []
    codex_home = env.get("CODEX_HOME")
    if codex_home:
        candidates.append(Path(codex_home) / "skills" / install_name)
    candidates.append(home_path / ".codex" / "skills" / install_name)
    candidates.append(home_path / ".agents" / "skills" / install_name)
    sibling_root = skill_root.parent.parent / repo_name
    candidates.append(sibling_root if is_root_path(skill_path) else sibling_root / skill_path)

    result: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        resolved = candidate.expanduser().resolve(strict=False)
        key = os.path.normcase(str(resolved))
        if key not in seen:
            seen.add(key)
            result.append(resolved)
    return result


def frontmatter_name(skill_file: Path) -> str | None:
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


def inspect_dependency(
    dependency: Mapping[str, Any],
    *,
    skill_root: Path,
    environment: Mapping[str, str] | None = None,
    home: Path | None = None,
) -> dict[str, Any]:
    """Inspect one dependency without installing or mutating anything."""

    skill_id = str(dependency["skill_id"])
    install_name = dependency_install_name(dependency)
    locations: list[dict[str, Any]] = []
    for candidate in dependency_candidate_paths(
        dependency, skill_root=skill_root, environment=environment, home=home
    ):
        skill_file = candidate / "SKILL.md"
        skill_name = frontmatter_name(skill_file) if skill_file.is_file() else None
        exists = candidate.is_dir()
        name_match = skill_name == skill_id
        valid = exists and skill_file.is_file() and name_match
        locations.append(
            {
                "path": str(candidate),
                "exists": exists,
                "skill_md": skill_file.is_file(),
                "name": skill_name,
                "name_match": name_match,
                "valid": valid,
            }
        )
    valid_locations = [location for location in locations if location["valid"]]
    any_present = any(location["exists"] or location["skill_md"] for location in locations)
    installed = bool(valid_locations)
    status = "installed" if installed else ("invalid" if any_present else "missing")
    return {
        "skill_id": skill_id,
        "install_name": install_name,
        "repo": dependency["repo"],
        "path": dependency["path"],
        "root_path": is_root_path(str(dependency["path"])),
        "ref": dependency["ref"],
        "capabilities": dependency["capabilities"],
        "license": dependency.get("license"),
        "maintainer": dependency.get("maintainer"),
        "reference_policy": dependency.get("reference_policy", "direct-character"),
        "requires_gpt_image_2": bool(dependency.get("requires_gpt_image_2", False)),
        "optional": bool(dependency.get("optional", False)),
        "source": dependency_source_url(dependency),
        "install": dependency_install_info(dependency),
        "reference_inputs": dependency.get("reference_inputs", {}),
        "installed": installed,
        "available": installed,
        "status": status,
        "installed_location": valid_locations[0]["path"] if valid_locations else None,
        "locations": locations,
    }
