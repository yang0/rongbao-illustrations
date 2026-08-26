#!/usr/bin/env python3
"""Tests for the personal-photo IP dependency and explicit registration flow."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from PIL import Image


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import doctor  # noqa: E402
from dependency_utils import inspect_dependency, load_dependency_registry  # noqa: E402
from design_router import PERSONAL_IP_SKILL_ID, SKILL_DIR, route_request  # noqa: E402
from register_character import CharacterRegistrationError, register_character  # noqa: E402


PERSONAL_DEPENDENCY = next(
    item
    for item in load_dependency_registry(SKILL_DIR / "references" / "design-dependencies.json")["dependencies"]
    if item["skill_id"] == PERSONAL_IP_SKILL_ID
)




def _write_png(path: Path, size: tuple[int, int]) -> None:
    Image.new("RGBA", size, (42, 118, 164, 255)).save(path, format="PNG")


def _skill_fixture(tmp_path: Path) -> Path:
    skill_dir = tmp_path / "skill"
    (skill_dir / "assets").mkdir(parents=True)
    (skill_dir / "references").mkdir(parents=True)
    (skill_dir / "references" / "character-registry.json").write_text(
        json.dumps(
            {
                "version": 1,
                "default_character": "yazai",
                "characters": [
                    {
                        "id": "yazai",
                        "display_name": "牙仔",
                        "aliases": ["牙仔", "yazai"],
                        "asset": "assets/yazai.webp",
                        "identity_reference": "references/yazai-identity.md",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return skill_dir


def test_personal_photo_routes_without_injecting_default_yazai() -> None:
    route = route_request("用我的真人照片设计一个个人卡通形象")
    assert route["target_skill_id"] == PERSONAL_IP_SKILL_ID
    assert route["target_capability"] == "personal-ip-prototype"
    assert route["mode"] == "direct-target"
    assert route["characters"] == []
    assert route["inject_character_references"] is False
    assert route["dependency"]["root_path"] is True
    assert route["dependency"]["purpose"] == "personal-photo-ip-creation"


def test_personal_dependency_probe_root_install_and_missing_status(tmp_path: Path) -> None:
    codex_home = tmp_path / "codex"
    installed = codex_home / "skills" / PERSONAL_IP_SKILL_ID
    (installed / "references").mkdir(parents=True)
    (installed / "assets").mkdir()
    (installed / "scripts").mkdir()
    (installed / "SKILL.md").write_text(
        f"---\nname: {PERSONAL_IP_SKILL_ID}\ndescription: fixture\n---\n",
        encoding="utf-8",
    )
    report = inspect_dependency(
        PERSONAL_DEPENDENCY,
        skill_root=SKILL_DIR,
        environment={"CODEX_HOME": str(codex_home)},
        home=tmp_path,
    )
    assert report["status"] == "installed"
    assert report["root_path"] is True
    assert report["required_paths"] == ["references", "assets", "scripts"]
    assert report["source"] == "https://github.com/DoraRabbitYan/personal-ip-image-pack/tree/main"
    assert report["install"]["args"] == [
        "--repo",
        "DoraRabbitYan/personal-ip-image-pack",
        "--path",
        ".",
        "--name",
        PERSONAL_IP_SKILL_ID,
        "--ref",
        "main",
    ]
    routed = route_request(
        "Use personal-ip-image-pack create 生成个人卡通原型",
        dependency_root=installed,
        environment={"CODEX_HOME": str(codex_home)},
        home=tmp_path,
    )
    assert routed["target_skill_id"] == PERSONAL_IP_SKILL_ID
    assert routed["mode"] == "direct-target"
    assert routed["generation_ready"] is True
    missing = inspect_dependency(
        PERSONAL_DEPENDENCY,
        skill_root=SKILL_DIR,
        environment={"CODEX_HOME": str(tmp_path / "missing-codex")},
        home=tmp_path,
    )
    assert missing["status"] == "missing"
    assert missing["optional"] is True
    assert doctor.strict_dependency_failure([missing]) is False


def test_personal_pack_explicit_and_expression_capability() -> None:
    route = route_request("Use personal-ip-image-pack create 做一套人物表情包")
    assert route["target_skill_id"] == PERSONAL_IP_SKILL_ID
    assert route["target_capability"] == "expression-pack"
    assert route["mode"] == "direct-target"
    assert route["characters"] == []


def test_existing_ip_and_mascot_requests_do_not_route_to_personal_pack() -> None:
    existing = route_request("用牙仔做一套人物表情包")
    assert existing["target_skill_id"] != PERSONAL_IP_SKILL_ID
    mascot = route_request("设计一个动物吉祥物")
    assert mascot["target_skill_id"] != PERSONAL_IP_SKILL_ID


def test_registration_requires_confirmation_and_writes_protocol(tmp_path: Path) -> None:
    skill_dir = _skill_fixture(tmp_path)
    prototype = tmp_path / "approved.png"
    _write_png(prototype, (64, 64))

    with pytest.raises(CharacterRegistrationError, match="English aliases"):
        register_character(
            "momo",
            "墨墨",
            ["墨墨"],
            prototype,
            skill_dir=skill_dir,
            confirm=True,
        )

    with pytest.raises(CharacterRegistrationError, match="explicit confirmation"):
        register_character(
            "momo",
            "墨墨",
            ["墨墨", "momo"],
            prototype,
            skill_dir=skill_dir,
        )
    assert not (skill_dir / "assets" / "momo.webp").exists()

    result = register_character(
        "momo",
        "墨墨",
        ["墨墨", "momo"],
        prototype,
        skill_dir=skill_dir,
        identity_text="# 墨墨身份协议\n\n保留圆眼和红围巾。",
        confirm=True,
    )
    assert result["registered"] is True
    assert result["updated"] is False
    registered_asset = skill_dir / "assets" / "momo.webp"
    with Image.open(registered_asset) as image:
        assert image.format == "WEBP"
        assert image.size == (64, 64)
    assert "红围巾" in (skill_dir / "references" / "momo-identity.md").read_text(encoding="utf-8")
    registry = json.loads((skill_dir / "references" / "character-registry.json").read_text(encoding="utf-8"))
    assert registry["default_character"] == "yazai"
    assert registry["characters"][-1]["aliases"] == ["墨墨", "momo"]


def test_registration_conflict_requires_update_and_update_preserves_default(tmp_path: Path) -> None:
    skill_dir = _skill_fixture(tmp_path)
    first = tmp_path / "first.png"
    second = tmp_path / "second.png"
    _write_png(first, (64, 64))
    _write_png(second, (128, 128))
    register_character("momo", "墨墨", ["墨墨", "momo"], first, skill_dir=skill_dir, confirm=True)

    with pytest.raises(CharacterRegistrationError, match="already exists"):
        register_character("momo", "墨墨二代", ["墨墨二代", "momo"], second, skill_dir=skill_dir, confirm=True)

    updated = register_character(
        "momo",
        "墨墨二代",
        ["墨墨二代", "momo-v2"],
        second,
        skill_dir=skill_dir,
        confirm=True,
        update=True,
    )
    assert updated["updated"] is True
    with Image.open(skill_dir / "assets" / "momo.webp") as image:
        assert image.format == "WEBP"
        assert image.size == (128, 128)
    registry = json.loads((skill_dir / "references" / "character-registry.json").read_text(encoding="utf-8"))
    assert registry["default_character"] == "yazai"
    assert registry["characters"][-1]["display_name"] == "墨墨二代"
