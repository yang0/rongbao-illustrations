#!/usr/bin/env python3
"""Deterministic smoke tests for character alias resolution."""

from character_router import UnknownCharacterError, resolve_characters


assert resolve_characters() == ["rongbao"]
assert resolve_characters("牙仔") == ["yazai"]
assert resolve_characters("用牙仔") == ["yazai"]
assert resolve_characters("YAZAI") == ["yazai"]
assert resolve_characters("绒宝+牙仔") == ["rongbao", "yazai"]
for request in ("prongbao", "yazaix"):
    try:
        resolve_characters(request, explicit=True)
    except UnknownCharacterError:
        pass
    else:
        raise AssertionError(f"longer token should not activate a character: {request}")
try:
    resolve_characters("章鱼", explicit=True)
except UnknownCharacterError as exc:
    assert "绒宝" in str(exc) and "牙仔" in str(exc)
else:
    raise AssertionError("unknown explicit character should fail")

print("character router tests passed")
