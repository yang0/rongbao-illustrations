#!/usr/bin/env python3
"""Deterministic character registry validation and name resolution."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REGISTRY_PATH = SKILL_DIR / "references" / "character-registry.json"
ASCII_TOKEN_CHARS = r"A-Za-z0-9_-"


class CharacterRegistryError(ValueError):
    """Raised when the character registry cannot support deterministic routing."""


class UnknownCharacterError(CharacterRegistryError):
    """Raised when an explicit, unsupported character name is requested."""

    def __init__(self, requested: str, supported: list[dict[str, str]]) -> None:
        self.requested = requested
        self.supported = supported
        names = ", ".join(f"{item['display_name']} ({item['id']})" for item in supported)
        super().__init__(f"unknown character '{requested}'; supported: {names}")


def _read_registry() -> dict[str, Any]:
    with REGISTRY_PATH.open("r", encoding="utf-8") as handle:
        registry = json.load(handle)
    if not isinstance(registry, dict):
        raise CharacterRegistryError("character registry root must be an object")
    return registry


def _supported(items: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {"id": str(item.get("id", "")), "display_name": str(item.get("display_name", ""))}
        for item in items
        if isinstance(item, dict) and item.get("id") and item.get("display_name")
    ]


def _alias_matches(alias: str, text: str) -> bool:
    """Match Chinese aliases by containment and ASCII aliases as whole tokens."""

    normalized_alias = alias.casefold()
    if not alias.isascii():
        return normalized_alias in text
    pattern = rf"(?<![{ASCII_TOKEN_CHARS}]){re.escape(normalized_alias)}(?![{ASCII_TOKEN_CHARS}])"
    return re.search(pattern, text) is not None


def inspect_registry() -> dict[str, Any]:
    """Return a JSON-safe validation report without changing the filesystem."""

    report: dict[str, Any] = {
        "registry": str(REGISTRY_PATH),
        "version": None,
        "default_character": None,
        "valid": False,
        "errors": [],
        "items": [],
    }
    try:
        registry = _read_registry()
    except (OSError, UnicodeError, json.JSONDecodeError, CharacterRegistryError) as exc:
        report["errors"] = [str(exc)]
        return report

    report["version"] = registry.get("version")
    report["default_character"] = registry.get("default_character")
    errors: list[str] = []
    if registry.get("version") != 1:
        errors.append("character registry version must be 1")
    characters = registry.get("characters")
    if not isinstance(characters, list):
        errors.append("character registry characters must be a list")
        report["errors"] = errors
        return report
    if not isinstance(report["default_character"], str) or not report["default_character"].strip():
        errors.append("default_character must be a non-empty string")

    seen_ids: set[str] = set()
    seen_aliases: dict[str, str] = {}
    valid_ids: set[str] = set()
    for index, item in enumerate(characters):
        item_errors: list[str] = []
        if not isinstance(item, dict):
            errors.append(f"character[{index}] must be an object")
            continue
        required = {"id", "display_name", "aliases", "asset", "identity_reference"}
        missing = sorted(required.difference(item))
        if missing:
            item_errors.append(f"missing fields: {', '.join(missing)}")
        character_id = item.get("id")
        display_name = item.get("display_name")
        aliases = item.get("aliases")
        asset = item.get("asset")
        identity_reference = item.get("identity_reference")
        if not isinstance(character_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", character_id):
            item_errors.append("id must use lowercase letters, digits, and hyphens")
        elif character_id in seen_ids:
            item_errors.append(f"duplicate character id: {character_id}")
        else:
            seen_ids.add(character_id)
            valid_ids.add(character_id)
        if not isinstance(display_name, str) or not display_name.strip():
            item_errors.append("display_name must be a non-empty string")
        if not isinstance(aliases, list) or not aliases:
            item_errors.append("aliases must be a non-empty list")
            aliases = []
        else:
            if not any(isinstance(alias, str) and not alias.isascii() for alias in aliases):
                item_errors.append("aliases must include a non-English alias")
            if not any(isinstance(alias, str) and alias.isascii() for alias in aliases):
                item_errors.append("aliases must include an English alias")
            for alias in aliases:
                if not isinstance(alias, str) or not alias.strip():
                    item_errors.append("aliases must contain non-empty strings")
                    continue
                alias_key = alias.casefold()
                previous = seen_aliases.get(alias_key)
                if previous is not None:
                    item_errors.append(f"duplicate alias: {alias}")
                else:
                    seen_aliases[alias_key] = str(character_id)
        asset_path = SKILL_DIR / str(asset) if isinstance(asset, str) else None
        identity_path = SKILL_DIR / str(identity_reference) if isinstance(identity_reference, str) else None
        asset_exists = bool(asset_path and asset_path.is_file())
        identity_exists = bool(identity_path and identity_path.is_file())
        if not asset_exists:
            item_errors.append(f"asset missing: {asset}")
        if not identity_exists:
            item_errors.append(f"identity_reference missing: {identity_reference}")
        item_report = {
            "id": character_id,
            "display_name": display_name,
            "aliases": aliases,
            "asset": asset,
            "identity_reference": identity_reference,
            "asset_exists": asset_exists,
            "identity_reference_exists": identity_exists,
            "valid": not item_errors,
            "errors": item_errors,
        }
        report["items"].append(item_report)
        errors.extend(f"{character_id or index}: {message}" for message in item_errors)

    default_character = report["default_character"]
    if isinstance(default_character, str) and default_character not in valid_ids:
        errors.append(f"default_character is not registered: {default_character}")
    report["errors"] = errors
    report["valid"] = not errors and bool(report["items"])
    return report


def _load_validated_registry() -> dict[str, Any]:
    report = inspect_registry()
    if not report["valid"]:
        supported = [
            {"id": item["id"], "display_name": item["display_name"]}
            for item in report["items"]
            if item.get("valid")
        ]
        raise CharacterRegistryError("; ".join(report["errors"]) or "character registry is invalid")
    return _read_registry()


def resolve_characters(request: str | None = None, *, explicit: bool = False) -> list[str]:
    """Resolve aliases in request text, defaulting to Rongbao when unnamed."""

    registry = _load_validated_registry()
    characters = registry["characters"]
    text = (request or "").strip().casefold()
    if not text:
        return [registry["default_character"]]
    selected: list[str] = []
    for character in characters:
        aliases = character["aliases"]
        if any(_alias_matches(alias, text) for alias in aliases):
            selected.append(character["id"])
    if selected:
        return selected
    if explicit:
        supported = _supported(characters)
        raise UnknownCharacterError(request or "", supported)
    return [registry["default_character"]]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve Rongbao character names")
    parser.add_argument("request", nargs="?", default="", help="text containing character aliases")
    parser.add_argument(
        "--explicit",
        action="store_true",
        help="error when an explicitly requested character name is unmatched",
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON")
    args = parser.parse_args(argv)
    try:
        selected = resolve_characters(args.request, explicit=args.explicit)
    except UnknownCharacterError as exc:
        if args.as_json:
            print(json.dumps({"error": str(exc), "supported": exc.supported}, ensure_ascii=False, indent=2))
        else:
            print(f"error: {exc}")
        return 2
    except CharacterRegistryError as exc:
        print(f"error: {exc}")
        return 2
    result = {"request": args.request, "characters": selected}
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(", ".join(selected))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
