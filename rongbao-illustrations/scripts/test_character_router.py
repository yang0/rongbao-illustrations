#!/usr/bin/env python3
"""Deterministic smoke tests for character routing and image inputs."""

import io
import json
from contextlib import redirect_stdout
from pathlib import Path

from character_router import (
    SKILL_DIR,
    UnknownCharacterError,
    main,
    resolve_character_inputs,
    resolve_characters,
)


def assert_inputs(request: str | None, expected: list[str]) -> None:
    inputs = resolve_character_inputs(request)
    assert [item["id"] for item in inputs] == expected
    assert len(inputs) == len(expected)
    selected_asset_paths = {Path(item["asset_path"]).resolve() for item in inputs}
    expected_asset_paths: set[Path] = set()
    for index, item in enumerate(inputs, start=1):
        asset_path = Path(item["asset_path"])
        identity_path = Path(item["identity_reference_path"])
        assert asset_path.is_absolute(), item
        assert identity_path.is_absolute(), item
        assert asset_path.is_file(), item
        assert identity_path.is_file(), item
        assert asset_path == (SKILL_DIR / item["asset"]).resolve()
        assert identity_path == (SKILL_DIR / item["identity_reference"]).resolve()
        assert item["input_order"] == index
        assert item["prompt_label"].startswith(f"Image {index}: {item['display_name']}")
        expected_asset_paths.add(asset_path)
    assert selected_asset_paths == expected_asset_paths
    skill_root = SKILL_DIR.resolve()
    assert all(skill_root == path or skill_root in path.parents for path in selected_asset_paths)


def assert_json_inputs(request: str, expected: list[str]) -> None:
    output = io.StringIO()
    with redirect_stdout(output):
        assert main(["--json", request]) == 0
    result = json.loads(output.getvalue())
    assert result["characters"] == expected
    assert [item["id"] for item in result["character_inputs"]] == expected
    assert all(Path(item["asset_path"]).is_absolute() for item in result["character_inputs"])


assert_inputs(None, ["yazai"])
assert_inputs("", ["yazai"])
assert_inputs("这个IP", ["yazai"])
assert_inputs("该IP", ["yazai"])
assert_inputs("普通默认请求", ["yazai"])
assert_inputs("用牙仔做一张海报", ["yazai"])
assert_inputs("绒宝、牙仔和阿龅共同完成", ["rongbao", "yazai", "abao"])
assert_json_inputs("绒宝、牙仔和阿龅共同完成", ["rongbao", "yazai", "abao"])
assert_json_inputs("该IP", ["yazai"])


assert resolve_characters() == ["yazai"]
assert resolve_characters("") == ["yazai"]
assert resolve_characters("普通默认请求") == ["yazai"]
assert resolve_characters("这个IP") == ["yazai"]
assert resolve_characters("该IP") == ["yazai"]
assert resolve_characters("绒宝") == ["rongbao"]
assert resolve_characters("rongbao") == ["rongbao"]
assert resolve_characters("牙仔") == ["yazai"]
assert resolve_characters("用牙仔") == ["yazai"]
assert resolve_characters("YAZAI") == ["yazai"]
assert resolve_characters("yazai") == ["yazai"]
assert resolve_characters("阿龅") == ["abao"]
assert resolve_characters("ABAO") == ["abao"]
assert resolve_characters("绒宝+牙仔") == ["rongbao", "yazai"]
assert resolve_characters("绒宝+阿龅") == ["rongbao", "abao"]
assert resolve_characters("牙仔和阿龅") == ["yazai", "abao"]
assert resolve_characters("绒宝、牙仔和阿龅") == ["rongbao", "yazai", "abao"]
for request in ("prongbao", "yazaix", "abaox"):
    try:
        resolve_characters(request, explicit=True)
    except UnknownCharacterError:
        pass
    else:
        raise AssertionError(f"longer token should not activate a character: {request}")
try:
    resolve_characters("章鱼", explicit=True)
except UnknownCharacterError as exc:
    assert all(name in str(exc) for name in ("绒宝", "牙仔", "阿龅"))
else:
    raise AssertionError("unknown explicit character should fail")

print("character router tests passed")
