#!/usr/bin/env python3
"""Explicitly register a user-approved IP in the Rongbao character registry.

This helper is intentionally opt-in.  It copies one approved PNG into the
installed Skill package, creates or accepts an identity protocol, and updates
the local registry only after ``--confirm`` has been supplied.  It never
downloads a character, installs a dependency, or overwrites an existing
character unless ``--update`` is also supplied.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ID_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]*\Z")
CJK_PATTERN = re.compile(r"[\u3400-\u9fff]")

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from character_router import _png_read_error  # noqa: E402


class CharacterRegistrationError(ValueError):
    """Raised when an explicit character registration is unsafe or invalid."""


def _read_registry(registry_path: Path) -> dict[str, Any]:
    try:
        with registry_path.open("r", encoding="utf-8") as handle:
            registry = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CharacterRegistrationError(f"cannot read character registry: {exc}") from exc
    if not isinstance(registry, dict) or registry.get("version") != 1:
        raise CharacterRegistrationError("character registry must be a version 1 object")
    if not isinstance(registry.get("characters"), list):
        raise CharacterRegistrationError("character registry characters must be a list")
    return registry


def _normalise_aliases(character_id: str, display_name: str, aliases: Iterable[str]) -> list[str]:
    values = [alias.strip() for alias in aliases if isinstance(alias, str) and alias.strip()]
    if display_name not in values:
        values.insert(0, display_name)
    if character_id not in {value.casefold() for value in values if value.isascii()}:
        values.append(character_id)

    result: list[str] = []
    seen: set[str] = set()
    for alias in values:
        key = alias.casefold()
        if key not in seen:
            seen.add(key)
            result.append(alias)
    return result


def _validate_metadata(character_id: str, display_name: str, aliases: list[str]) -> None:
    if not ID_PATTERN.fullmatch(character_id):
        raise CharacterRegistrationError("id must use lowercase letters, digits, and hyphens")
    if not display_name.strip() or not CJK_PATTERN.search(display_name):
        raise CharacterRegistrationError("display_name must contain a Chinese name")
    if len(aliases) < 2:
        raise CharacterRegistrationError("aliases must include at least Chinese and English aliases")
    if len({alias.casefold() for alias in aliases}) != len(aliases):
        raise CharacterRegistrationError("aliases must be unique")
    if not any(not alias.isascii() for alias in aliases):
        raise CharacterRegistrationError("aliases must include a Chinese alias")
    if not any(alias.isascii() for alias in aliases):
        raise CharacterRegistrationError("aliases must include an English alias")


def _validate_prototype(path: Path) -> None:
    if not path.is_file():
        raise CharacterRegistrationError(f"approved prototype does not exist: {path}")
    if path.suffix.casefold() != ".png":
        raise CharacterRegistrationError("approved prototype must be a PNG file")
    error = _png_read_error(path)
    if error:
        raise CharacterRegistrationError(f"approved prototype is invalid: {error}")


def _identity_protocol(
    *,
    display_name: str,
    asset_relative_path: str,
    identity_text: str | None,
    identity_file: Path | None,
) -> str:
    if identity_text is not None and identity_file is not None:
        raise CharacterRegistrationError("use either --identity-text or --identity-file, not both")
    if identity_file is not None:
        try:
            identity_text = identity_file.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as exc:
            raise CharacterRegistrationError(f"cannot read identity protocol: {exc}") from exc
    if identity_text is not None and not identity_text.strip():
        raise CharacterRegistrationError("identity protocol cannot be empty")
    if identity_text is not None:
        return identity_text.rstrip() + "\n"
    return (
        f"# {display_name} IP identity protocol\n\n"
        f"- Approved primary reference: `{asset_relative_path}`.\n"
        "- Preserve the approved character's silhouette, face, proportions, expression range, "
        "signature clothing or marks, and stable identity colors.\n"
        "- The target design Skill may redraw the character in its own medium, but must not "
        "replace the character with an unrelated person, mascot, or mixed character.\n"
        "- This character was registered only after explicit user confirmation; do not update "
        "the identity anchor without a new confirmation.\n"
    )


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def _write_registry(path: Path, registry: dict[str, Any]) -> None:
    data = json.dumps(registry, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    _atomic_write(path, data)


def _conflicts(
    characters: list[dict[str, Any]],
    *,
    character_id: str,
    aliases: list[str],
    update: bool,
) -> tuple[int | None, list[str]]:
    same_id_index: int | None = None
    conflicts: list[str] = []
    alias_map: dict[str, tuple[str, int]] = {}
    for index, item in enumerate(characters):
        if not isinstance(item, dict):
            continue
        item_id = str(item.get("id", ""))
        if item_id == character_id:
            same_id_index = index
        for alias in item.get("aliases", []):
            if isinstance(alias, str):
                alias_map.setdefault(alias.casefold(), (item_id, index))

    if same_id_index is not None and not update:
        conflicts.append(f"character id already exists: {character_id}")
    for alias in aliases:
        previous = alias_map.get(alias.casefold())
        if previous is None:
            continue
        previous_id, previous_index = previous
        if previous_id != character_id or previous_index != same_id_index:
            conflicts.append(f"alias already belongs to {previous_id}: {alias}")
    return same_id_index, conflicts


def register_character(
    character_id: str,
    display_name: str,
    aliases: Iterable[str],
    prototype: Path,
    *,
    skill_dir: Path = SKILL_DIR,
    identity_text: str | None = None,
    identity_file: Path | None = None,
    confirm: bool = False,
    update: bool = False,
) -> dict[str, Any]:
    """Register one approved PNG and return its machine-readable result."""

    if not confirm:
        raise CharacterRegistrationError(
            "registration requires explicit confirmation; pass --confirm only after the user approves the prototype"
        )
    character_id = character_id.strip()
    display_name = display_name.strip()
    supplied_aliases = [alias.strip() for alias in aliases if isinstance(alias, str) and alias.strip()]
    _validate_metadata(character_id, display_name, supplied_aliases)
    normalised_aliases = _normalise_aliases(character_id, display_name, supplied_aliases)
    prototype = prototype.expanduser().resolve(strict=False)
    _validate_prototype(prototype)

    skill_dir = skill_dir.expanduser().resolve(strict=False)
    registry_path = skill_dir / "references" / "character-registry.json"
    registry = _read_registry(registry_path)
    characters = registry["characters"]
    same_id_index, conflicts = _conflicts(
        characters,
        character_id=character_id,
        aliases=normalised_aliases,
        update=update,
    )
    asset_path = skill_dir / "assets" / f"{character_id}.png"
    identity_path = skill_dir / "references" / f"{character_id}-identity.md"
    if not update or same_id_index is None:
        for path, label in ((asset_path, "asset"), (identity_path, "identity protocol")):
            if path.exists():
                conflicts.append(f"{label} already exists: {path}")
    if conflicts:
        raise CharacterRegistrationError("; ".join(dict.fromkeys(conflicts)))

    asset_relative = f"assets/{character_id}.png"
    identity_relative = f"references/{character_id}-identity.md"
    identity_content = _identity_protocol(
        display_name=display_name,
        asset_relative_path=asset_relative,
        identity_text=identity_text,
        identity_file=identity_file,
    )
    character_record = {
        "id": character_id,
        "display_name": display_name,
        "aliases": normalised_aliases,
        "asset": asset_relative,
        "identity_reference": identity_relative,
    }

    old_registry = registry_path.read_bytes()
    old_asset = asset_path.read_bytes() if asset_path.is_file() else None
    old_identity = identity_path.read_bytes() if identity_path.is_file() else None
    try:
        if same_id_index is None:
            characters.append(character_record)
            updated = False
        else:
            characters[same_id_index] = character_record
            updated = True
        _atomic_write(asset_path, prototype.read_bytes())
        _atomic_write(identity_path, identity_content.encode("utf-8"))
        _write_registry(registry_path, registry)
    except Exception:
        _atomic_write(registry_path, old_registry)
        if old_asset is None:
            asset_path.unlink(missing_ok=True)
        else:
            _atomic_write(asset_path, old_asset)
        if old_identity is None:
            identity_path.unlink(missing_ok=True)
        else:
            _atomic_write(identity_path, old_identity)
        raise

    return {
        "registered": True,
        "updated": updated,
        "character": character_record,
        "asset_path": str(asset_path),
        "identity_reference_path": str(identity_path),
        "confirmed": True,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Register a user-approved IP in Rongbao")
    parser.add_argument("--id", required=True, dest="character_id", help="lowercase English character id")
    parser.add_argument("--display-name", required=True, help="Chinese display name")
    parser.add_argument(
        "--alias",
        action="append",
        dest="aliases",
        default=[],
        help="character alias; repeat for Chinese and English aliases",
    )
    parser.add_argument("--prototype", "--asset", required=True, type=Path, help="approved PNG prototype")
    parser.add_argument("--identity-file", type=Path, help="approved identity protocol Markdown")
    parser.add_argument("--identity-text", help="identity protocol Markdown text")
    parser.add_argument("--skill-dir", type=Path, default=SKILL_DIR, help="installed Rongbao Skill root")
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="confirm the user explicitly approved this prototype for registration",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="allow replacing an existing character with the same id; aliases owned by another id still fail",
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON")
    args = parser.parse_args(argv)
    try:
        result = register_character(
            args.character_id,
            args.display_name,
            args.aliases,
            args.prototype,
            skill_dir=args.skill_dir,
            identity_text=args.identity_text,
            identity_file=args.identity_file,
            confirm=args.confirm,
            update=args.update,
        )
    except (CharacterRegistrationError, OSError, UnicodeError) as exc:
        if args.as_json:
            print(json.dumps({"registered": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{'updated' if result['updated'] else 'registered'}: {result['character']['display_name']} ({args.character_id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
