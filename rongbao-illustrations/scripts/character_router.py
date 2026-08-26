#!/usr/bin/env python3
"""Deterministic character registry validation and name resolution."""

from __future__ import annotations

import argparse
import json
import re
import struct
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REGISTRY_PATH = SKILL_DIR / "references" / "character-registry.json"
ASCII_TOKEN_CHARS = r"A-Za-z0-9_-"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
WEBP_RIFF_SIGNATURE = b"RIFF"
WEBP_SIGNATURE = b"WEBP"


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


def _resolve_skill_path(relative_path: str) -> Path:
    """Resolve a registry path from this installed Skill's root, never cwd."""

    return (SKILL_DIR / relative_path).resolve(strict=False)


def _png_read_error(path: Path) -> str | None:
    """Return a concise error when *path* is not a readable PNG file.

    This deliberately uses only the PNG signature and IHDR header.  It catches
    missing/truncated/wrong-format assets without adding an image dependency;
    the image generation tool remains responsible for full decoding.
    """

    try:
        with path.open("rb") as handle:
            header = handle.read(33)
    except OSError as exc:
        return f"asset unreadable: {exc}"
    if len(header) < 33 or header[:8] != PNG_SIGNATURE:
        return "asset is not a readable PNG"
    try:
        ihdr_length = struct.unpack(">I", header[8:12])[0]
        width, height = struct.unpack(">II", header[16:24])
    except struct.error:
        return "asset has an incomplete PNG header"
    if header[12:16] != b"IHDR" or ihdr_length < 13:
        return "asset has no valid PNG IHDR header"
    if width <= 0 or height <= 0:
        return "asset has invalid PNG dimensions"
    return None


def _webp_read_error(path: Path) -> str | None:
    """Return a concise error when *path* is not a readable WebP file."""

    try:
        file_size = path.stat().st_size
        with path.open("rb") as handle:
            header = handle.read(20)
    except OSError as exc:
        return f"asset unreadable: {exc}"
    if len(header) < 20 or header[:4] != WEBP_RIFF_SIGNATURE or header[8:12] != WEBP_SIGNATURE:
        return "asset is not a readable WebP"
    try:
        riff_size = struct.unpack("<I", header[4:8])[0]
        chunk_size = struct.unpack("<I", header[16:20])[0]
    except struct.error:
        return "asset has an incomplete WebP header"
    if riff_size + 8 > file_size:
        return "asset has a truncated WebP RIFF payload"
    if header[12:16] not in {b"VP8 ", b"VP8L", b"VP8X"}:
        return "asset has no supported WebP image chunk"
    padded_chunk_end = 20 + chunk_size + (chunk_size & 1)
    if chunk_size <= 0 or padded_chunk_end > file_size:
        return "asset has an invalid WebP image chunk"
    return None


def _image_read_error(path: Path) -> str | None:
    """Validate a registered raster image without requiring Pillow."""

    suffix = path.suffix.casefold()
    if suffix == ".webp":
        return _webp_read_error(path)
    if suffix == ".png":
        return _png_read_error(path)
    return f"unsupported registered asset format: {suffix or '<none>'}"


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
        asset_path = _resolve_skill_path(asset) if isinstance(asset, str) else None
        identity_path = _resolve_skill_path(identity_reference) if isinstance(identity_reference, str) else None
        asset_exists = bool(asset_path and asset_path.is_file())
        identity_exists = bool(identity_path and identity_path.is_file())
        asset_error = None
        if not asset_exists:
            item_errors.append(f"asset missing: {asset}")
        else:
            asset_error = _image_read_error(asset_path)
            if asset_error:
                item_errors.append(f"asset invalid: {asset} ({asset_error})")
        if not identity_exists:
            item_errors.append(f"identity_reference missing: {identity_reference}")
        item_report = {
            "id": character_id,
            "display_name": display_name,
            "aliases": aliases,
            "asset": asset,
            "identity_reference": identity_reference,
            "asset_path": str(asset_path) if asset_path else None,
            "identity_reference_path": str(identity_path) if identity_path else None,
            "asset_exists": asset_exists,
            "asset_readable": asset_exists and asset_error is None,
            "asset_error": asset_error,
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
    """Resolve aliases in request text, defaulting to Yazai when unnamed."""

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


def resolve_character_inputs(
    request: str | None = None, *, explicit: bool = False
) -> list[dict[str, Any]]:
    """Resolve selected characters and their installed image/protocol paths.

    The order follows the registry, making ``Image 1``, ``Image 2`` mappings
    deterministic for downstream image generation.  Paths are always resolved
    from this script's Skill root rather than the caller's current directory.
    """

    registry = _load_validated_registry()
    selected_ids = resolve_characters(request, explicit=explicit)
    by_id = {item["id"]: item for item in registry["characters"]}
    inputs: list[dict[str, Any]] = []
    for index, character_id in enumerate(selected_ids, start=1):
        item = by_id[character_id]
        asset_path = _resolve_skill_path(item["asset"])
        identity_reference_path = _resolve_skill_path(item["identity_reference"])
        inputs.append(
            {
                "id": item["id"],
                "display_name": item["display_name"],
                "asset": item["asset"],
                "identity_reference": item["identity_reference"],
                "asset_path": str(asset_path),
                "identity_reference_path": str(identity_reference_path),
                "input_order": index,
                "prompt_label": f"Image {index}: {item['display_name']} identity reference only",
            }
        )
    return inputs


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
    result = {
        "request": args.request,
        "characters": selected,
        "character_inputs": resolve_character_inputs(args.request, explicit=args.explicit),
    }
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(", ".join(selected))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
