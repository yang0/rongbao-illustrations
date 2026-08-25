#!/usr/bin/env python3
"""Deterministic routing and reference-input assembly for design Skills.

This adapter never installs or copies a dependency. It chooses the native
Rongbao path or one registered design dependency, then emits a deterministic
ordered prompt package for the caller.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REGISTRY_PATH = SKILL_DIR / "references" / "design-dependencies.json"
UPSTREAM_SKILL_ID = "ip-illustration-character-system"
DONGFANG_SKILL_ID = "dongfang-cover-design"
GUIZANG_SKILL_ID = "guizang-social-card-skill"
GPT_IMAGE_2_STYLE_LIBRARY_ID = "gpt-image-2-style-library"
GBRO_SKILL_ID = "gbro-cover-design"
BAOYU_SKILL_IDS = {
    "baoyu-article-illustrator",
    "baoyu-comic",
    "baoyu-cover-image",
    "baoyu-infographic",
    "baoyu-slide-deck",
    "baoyu-xhs-images",
}
BAOYU_DEFAULT_CAPABILITIES = {
    "baoyu-article-illustrator": "article-illustration",
    "baoyu-comic": "comic",
    "baoyu-cover-image": "cover-image",
    "baoyu-infographic": "infographic",
    "baoyu-slide-deck": "slide-deck",
    "baoyu-xhs-images": "xhs-images",
}
BAOYU_UNIQUE_CAPABILITIES = {"comic", "slide-deck"}
GPT_IMAGE_2_LINKS = {
    "model": "https://developers.openai.com/api/docs/models/gpt-image-2",
    "guide": "https://developers.openai.com/api/docs/guides/image-generation",
}

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from character_router import (  # noqa: E402
    _alias_matches,
    _read_registry,
    resolve_character_inputs,
)
from dependency_utils import (  # noqa: E402
    DependencyRegistryError,
    inspect_dependency_location,
    inspect_dependency,
    load_dependency_registry,
)


CAPABILITY_ALIASES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "article-infographic-3x4",
        (
            "3:4",
            "3：4",
            "3x4",
            "3×4",
            "信息图",
            "知识卡",
            "知识卡片",
            "article infographic",
            "infographic",
        ),
    ),
    (
        "sticker-sheet-3x4",
        ("贴纸", "贴纸页", "异形贴纸", "模切贴纸", "sticker sheet", "sticker-sheet"),
    ),
    (
        "turnaround-sheet",
        ("转面图", "转面设定", "角色转面", "turnaround", "turnaround sheet"),
    ),
    (
        "character-anchor",
        ("角色锚点", "角色形象", "人物锚点", "character anchor", "character-anchor"),
    ),
    (
        "mini-article-illustration",
        ("萌粒", "mini pen-doodle", "mini illustration", "mini article illustration"),
    ),
)

BAOYU_CAPABILITY_ALIASES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "comic",
        ("知识漫画", "漫画", "知识漫画", "comic", "comics", "knowledge comic"),
    ),
    (
        "xhs-images",
        (
            "小红书图片",
            "小红书配图",
            "小红书图文",
            "小红书组图",
            "小红书轮播图文",
            "图片卡片",
            "图片卡",
            "xhs images",
            "xhs-images",
        ),
    ),
    (
        "slide-deck",
        ("幻灯片", "幻灯片组", "演示文稿", "slide deck", "slides", "presentation"),
    ),
    (
        "article-illustration",
        (
            "文章配图",
            "正文配图",
            "文章插图",
            "article illustration",
            "article illustrator",
            "baoyu article illustrator",
        ),
    ),
    (
        "cover-image",
        ("封面", "封面图", "cover image", "article cover"),
    ),
    (
        "infographic",
        ("信息图", "知识信息图", "infographic", "baoyu infographic"),
    ),
)

DONGFANG_CAPABILITY_ALIASES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "portrait-poster",
        ("竖版海报", "竖屏海报", "竖版封面", "portrait poster", "portrait cover"),
    ),
    (
        "square-graphic",
        ("方图", "正方形", "正方形传播图", "square graphic", "1:1 graphic"),
    ),
    (
        "landscape-cover",
        ("横版封面", "横屏封面", "封面 KV", "封面", "landscape cover", "cover"),
    ),
)

GUIZANG_CAPABILITY_ALIASES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "swiss-social-card",
        (
            "瑞士风社交卡",
            "归藏瑞士风",
            "瑞士国际主义",
            "瑞士风",
            "swiss social card",
            "swiss style",
            "swiss",
        ),
    ),
    (
        "editorial-social-card",
        (
            "电子杂志社交卡",
            "归藏电子杂志风",
            "电子杂志风",
            "杂志风社交卡",
            "editorial social card",
            "editorial style",
            "editorial",
        ),
    ),
    (
        "wechat-cover-pair",
        (
            "公众号封面对",
            "公众号封面一对",
            "公众号头图分享卡",
            "微信封面对",
            "21:9+1:1",
            "21:9 + 1:1",
            "wechat cover pair",
            "wechat cover",
        ),
    ),
    (
        "live-photo-card",
        (
            "live photo 卡片",
            "live photo",
            "livephoto",
            "动态卡",
            "实况卡",
            "实况拼图",
            "live photo card",
        ),
    ),
    (
        "xhs-social-cards",
        (
            "小红书图文组图",
            "小红书轮播图文",
            "小红书卡片组",
            "rednote carousel",
            "xiaohongshu carousel",
            "xhs social cards",
        ),
    ),
)

GUIZANG_GENERIC_XHS_ALIASES: tuple[str, ...] = (
    "小红书图文",
    "小红书图片",
    "小红书配图",
    "小红书组图",
    "小红书轮播",
    "rednote",
    "xiaohongshu",
    "xhs",
)

GBRO_CAPABILITY_ALIASES: tuple[str, ...] = (
    "gbro",
    "gbro-cover-design",
    "三轮提问封面",
    "三轮提问的封面",
    "三轮问答封面",
    "10种构图风格封面",
    "10 种构图风格封面",
    "十种构图风格封面",
)

PROMPT_ENHANCER_ALIASES: tuple[str, ...] = (
    "gpt-image-2-style-library",
    "freestylefly/awesome-gpt-image-2",
    "awesome-gpt-image-2",
    "gpt image 2 style library",
    "gpt image 2 风格库",
    "gpt image 2 模板库",
    "gpt image2 风格库",
    "gpt image2 模板库",
    "模板库增强提示词",
    "模板库增强",
    "按模板增强提示词",
    "风格库增强提示词",
    "prompt enhancement",
)

PROMPT_ENHANCER_OUTPUTS: tuple[str, ...] = (
    "template_name",
    "style_tags",
    "scene_tags",
    "case_ids",
    "structured_prompt",
    "negative_constraints",
)


class DesignRoutingError(ValueError):
    """Raised when the dependency registry cannot support routing."""


def _contains_ascii_token(alias: str, text: str) -> bool:
    pattern = rf"(?<![A-Za-z0-9_-]){re.escape(alias.casefold())}(?![A-Za-z0-9_-])"
    return re.search(pattern, text.casefold()) is not None


def _load_target_dependency() -> dict[str, Any]:
    return _load_dependencies_by_id()[UPSTREAM_SKILL_ID]


def _load_dependencies_by_id() -> dict[str, dict[str, Any]]:
    registry = load_dependency_registry(REGISTRY_PATH)
    return {str(dependency["skill_id"]): dependency for dependency in registry["dependencies"]}


def _registered_character_signal(request: str) -> dict[str, Any]:
    registry = _read_registry()
    text = request.casefold()
    aliases: list[str] = []
    for character in registry.get("characters", []):
        for alias in character.get("aliases", []):
            if isinstance(alias, str) and (
                _alias_matches(alias, text) if alias else False
            ):
                aliases.append(alias)
    ip_signal = bool(
        re.search(
            r"(?:这个|该|我的|本|自有|指定)\s*ip(?:形象|角色|素材|参考)?|"
            r"ip\s*(?:形象|角色|素材|参考)|带\s*ip",
            text,
            flags=re.IGNORECASE,
        )
    )
    adapter_signal = bool(
        aliases
        or ip_signal
        or "$rongbao-illustrations" in text
        or "rongbao-illustrations" in text
    )
    return {
        "registered_aliases": list(dict.fromkeys(aliases)),
        "ip_signal": ip_signal,
        "rongbao_skill_signal": "$rongbao-illustrations" in text
        or "rongbao-illustrations" in text,
        "adapter_signal": adapter_signal,
    }


def _target_skill_signal(request: str, dependency: Mapping[str, Any]) -> bool:
    text = request.casefold()
    aliases = {
        str(dependency["skill_id"]).casefold(),
        str(dependency.get("install_name", dependency["skill_id"])).casefold(),
    }
    if dependency.get("skill_id") == UPSTREAM_SKILL_ID:
        aliases.add("ip_illustration_for_yourself")
    if dependency.get("skill_id") == GBRO_SKILL_ID:
        aliases.update(GBRO_CAPABILITY_ALIASES)
    return any(_contains_ascii_token(alias, text) for alias in aliases)


def _gbro_signal(request: str) -> bool:
    """Detect explicit gbro invocation without claiming ordinary covers."""

    text = request.casefold()
    for alias in GBRO_CAPABILITY_ALIASES:
        if alias.isascii():
            if _contains_ascii_token(alias, text):
                return True
        elif alias.casefold() in text:
            return True
    return False


def _prompt_enhancer_signal(request: str) -> bool:
    """Detect an explicit GPT Image 2 style-library enhancement request.

    The enhancer is deliberately opt-in.  Generic words such as ``风格`` or
    ``模板`` do not activate it, so existing target Skill routing remains
    unchanged unless the user names this library or asks for template-based
    prompt enhancement.
    """

    text = request.casefold()
    for alias in PROMPT_ENHANCER_ALIASES:
        if alias.isascii():
            if _contains_ascii_token(alias, text):
                return True
        elif alias.casefold() in text:
            return True
    return bool(
        re.search(
            r"gpt\s*image\s*2[^。\n]{0,24}(?:风格库|模板库)[^。\n]{0,12}(?:增强|优化)",
            text,
            flags=re.IGNORECASE,
        )
    )


def _is_prompt_enhancer_dependency(dependency: Mapping[str, Any]) -> bool:
    return str(dependency.get("purpose", "")).casefold() == "prompt-enhancement" or str(
        dependency.get("skill_id", "")
    ) == GPT_IMAGE_2_STYLE_LIBRARY_ID


def _select_prompt_enhancer(
    request: str,
    dependencies: Mapping[str, Mapping[str, Any]],
) -> Mapping[str, Any] | None:
    """Select the opt-in prompt enhancer without replacing the base target."""

    if not _prompt_enhancer_signal(request):
        return None
    return dependencies.get(GPT_IMAGE_2_STYLE_LIBRARY_ID)


def _guizang_signal(request: str) -> bool:
    """Detect an explicit Guizang/social-card request without stealing Baoyu."""

    text = request.casefold()
    if _contains_ascii_token("guizang-social-card-skill", text):
        return True
    if _contains_ascii_token("op7418/guizang-social-card-skill", text):
        return True
    if any(alias.casefold() in text for alias in ("归藏", "social card", "social cards")):
        return True
    return detect_guizang_capability(request) is not None


def _baoyu_signal(request: str) -> bool:
    text = request.casefold()
    return bool(
        re.search(r"宝玉|\bbaoyu\b|baoyu-skills|jimliu/baoyu-skills", text, flags=re.IGNORECASE)
    )


def _detect_alias_capability(
    request: str,
    aliases: tuple[tuple[str, tuple[str, ...]], ...],
) -> str | None:
    text = request.casefold()
    for capability, capability_aliases in aliases:
        for alias in capability_aliases:
            if alias.isascii():
                if _contains_ascii_token(alias, text):
                    return capability
            elif alias.casefold() in text:
                return capability
    return None


def detect_baoyu_capability(request: str) -> str | None:
    """Detect a Baoyu-specific capability without changing native defaults."""

    return _detect_alias_capability(request, BAOYU_CAPABILITY_ALIASES)


def detect_dongfang_capability(request: str) -> str | None:
    """Detect the existing Dongfang cover/poster/square capability."""

    return _detect_alias_capability(request, DONGFANG_CAPABILITY_ALIASES)


def detect_guizang_capability(request: str) -> str | None:
    """Detect a Guizang Social Card capability from explicit style/platform terms."""

    return _detect_alias_capability(request, GUIZANG_CAPABILITY_ALIASES)


def detect_gbro_capability(request: str) -> str | None:
    """Return gbro's fixed 3:4 prompt capability when explicitly selected."""

    return "cover-prompt-3x4" if _gbro_signal(request) else None


def _is_generic_xhs_request(request: str) -> bool:
    """Return True for a generic Xiaohongshu request without a style choice."""

    text = request.casefold()
    has_xhs = any(
        (alias.casefold() in text if not alias.isascii() else _contains_ascii_token(alias, text))
        for alias in GUIZANG_GENERIC_XHS_ALIASES
    )
    return has_xhs and detect_guizang_capability(request) is None


def _explicit_dependency(request: str, dependencies: Mapping[str, Mapping[str, Any]]) -> Mapping[str, Any] | None:
    """Return an explicitly named registered dependency in registry order."""

    for dependency in dependencies.values():
        if _is_prompt_enhancer_dependency(dependency):
            continue
        if _target_skill_signal(request, dependency):
            return dependency
        if dependency.get("skill_id") == GUIZANG_SKILL_ID and _guizang_signal(request):
            return dependency
    return None


def _capability_for_dependency(request: str, dependency: Mapping[str, Any]) -> str | None:
    skill_id = str(dependency["skill_id"])
    if skill_id in BAOYU_SKILL_IDS:
        return detect_baoyu_capability(request) or BAOYU_DEFAULT_CAPABILITIES.get(skill_id)
    if skill_id == DONGFANG_SKILL_ID:
        return detect_dongfang_capability(request) or str(dependency["capabilities"][0])
    if skill_id == UPSTREAM_SKILL_ID:
        return detect_capability(request) or None
    if skill_id == GUIZANG_SKILL_ID:
        return detect_guizang_capability(request) or "xhs-social-cards"
    if skill_id == GBRO_SKILL_ID:
        return "cover-prompt-3x4"
    return str(dependency["capabilities"][0]) if dependency.get("capabilities") else None


def _select_target(
    request: str,
    dependencies: Mapping[str, Mapping[str, Any]],
) -> tuple[Mapping[str, Any] | None, str | None]:
    """Choose one target while preserving registered Everett and Dongfang routes."""

    explicit = _explicit_dependency(request, dependencies)
    if explicit is not None:
        return explicit, _capability_for_dependency(request, explicit)

    # A generic Xiaohongshu request is intentionally left unresolved until the
    # caller chooses a visual system.  This keeps Guizang from silently
    # taking over Baoyu's xhs-images route.
    if _is_generic_xhs_request(request) and not _baoyu_signal(request):
        return None, None

    baoyu_capability = detect_baoyu_capability(request)
    if baoyu_capability is not None:
        baoyu_skill = next(
            (
                dependency
                for dependency in dependencies.values()
                if BAOYU_DEFAULT_CAPABILITIES.get(str(dependency["skill_id"])) == baoyu_capability
            ),
            None,
        )
        if baoyu_skill is not None and (_baoyu_signal(request) or baoyu_capability in BAOYU_UNIQUE_CAPABILITIES):
            return baoyu_skill, baoyu_capability

    everett_capability = detect_capability(request)
    if everett_capability is not None:
        return dependencies.get(UPSTREAM_SKILL_ID), everett_capability

    dongfang_capability = detect_dongfang_capability(request)
    if dongfang_capability is not None:
        return dependencies.get(DONGFANG_SKILL_ID), dongfang_capability
    return None, None


def detect_capability(request: str) -> str | None:
    """Detect the most specific upstream capability in deterministic order."""

    text = request.casefold()
    for capability, aliases in CAPABILITY_ALIASES:
        for alias in aliases:
            if alias.isascii():
                if _contains_ascii_token(alias, text):
                    return capability
            elif alias.casefold() in text:
                return capability
    return None


def detect_operation(request: str) -> str:
    """Preserve ``create`` versus ``prompt`` semantics for downstream Skills."""

    text = request.casefold()
    if re.search(r"先不要生图|不要生图|只要提示词|只做提示词|路由计划|shot\s*list|\bprompt\b", text):
        return "prompt"
    if re.search(r"\bcreate\b|生成|生图|设计|做一张|做一套|改图|编辑图片|画一张", text):
        return "create"
    return "unspecified"


def _requested_aspect_ratio(request: str) -> str | None:
    """Extract an explicitly requested common aspect ratio, if present."""

    match = re.search(r"(?<!\d)(\d+)\s*[:：x×]\s*(\d+)(?!\d)", request.casefold())
    if match:
        return f"{match.group(1)}:{match.group(2)}"
    text = request.casefold()
    if re.search(r"横版|横屏|landscape", text):
        return "16:9"
    if re.search(r"方图|正方形|square", text):
        return "1:1"
    return None


def model_gate(
    model: str | None = None,
    *,
    explicitly_confirmed: bool = False,
    request: str = "",
) -> dict[str, Any]:
    """Allow direct generation only for an explicitly confirmed GPT Image 2."""

    normalized_model = (model or "").casefold().replace("_", "-").replace(" ", "-")
    recognized = normalized_model in {"gpt-image-2", "gptimage-2", "gptimage2"}
    phrase_confirmed = bool(re.search(r"gpt[\s_-]*image[\s_-]*2", request.casefold()))
    confirmed = explicitly_confirmed or phrase_confirmed
    direct_allowed = recognized and confirmed
    return {
        "requested_model": model,
        "recognized_gpt_image_2": recognized,
        "explicitly_confirmed": confirmed,
        "applies": True,
        "direct_generation_allowed": direct_allowed,
        "delivery": "direct-generation" if direct_allowed else "prompt-package",
        "required_model": "gpt-image-2",
        "official_docs": GPT_IMAGE_2_LINKS,
        "reason": (
            "GPT Image 2 is explicitly confirmed"
            if direct_allowed
            else "generic or unknown image tools are not accepted; prepare a prompt package"
        ),
    }


def _model_gate_for_dependency(
    dependency: Mapping[str, Any] | None,
    model: str | None,
    *,
    explicitly_confirmed: bool,
    request: str,
) -> dict[str, Any]:
    """Apply the GPT Image 2 gate to a target dependency when required."""

    if dependency is not None and dependency.get("requires_gpt_image_2", False):
        return model_gate(model, explicitly_confirmed=explicitly_confirmed, request=request)
    return {
        "requested_model": model,
        "recognized_gpt_image_2": None,
        "explicitly_confirmed": explicitly_confirmed,
        "applies": False,
        "direct_generation_allowed": True,
        "delivery": "direct-generation",
        "required_model": None,
        "official_docs": {},
        "applies": False,
        "reason": "target dependency has no GPT Image 2 gate",
    }


def _model_gate_for_route(
    dependency: Mapping[str, Any] | None,
    prompt_enhancer: Mapping[str, Any] | None,
    model: str | None,
    *,
    explicitly_confirmed: bool,
    request: str,
) -> dict[str, Any]:
    """Apply the model gate when either the target or enhancer requires it."""

    required_by: list[str] = []
    for candidate in (dependency, prompt_enhancer):
        if candidate is not None and candidate.get("requires_gpt_image_2", False):
            required_by.append(str(candidate["skill_id"]))
    if required_by:
        gate = model_gate(model, explicitly_confirmed=explicitly_confirmed, request=request)
        gate["required_by"] = required_by
        return gate
    gate = _model_gate_for_dependency(
        dependency,
        model,
        explicitly_confirmed=explicitly_confirmed,
        request=request,
    )
    gate["required_by"] = []
    return gate


def _dependency_report(
    dependency: Mapping[str, Any],
    *,
    dependency_root: Path | None,
    environment: Mapping[str, str] | None,
    home: Path | None,
) -> dict[str, Any]:
    from dependency_utils import dependency_install_info, dependency_source_url, is_root_path

    report = inspect_dependency(
        dependency,
        skill_root=SKILL_DIR,
        environment=environment,
        home=home,
    )
    if dependency_root is None:
        return report
    root = dependency_root.expanduser().resolve(strict=False)
    location = inspect_dependency_location(dependency, root)
    valid = bool(location["valid"])
    report["installed"] = valid
    report["available"] = valid
    report["status"] = "installed" if valid else ("invalid" if root.exists() else "missing")
    report["installed_location"] = str(root) if valid else None
    report["locations"] = [location]
    report["source"] = dependency_source_url(dependency)
    report["install"] = dependency_install_info(dependency)
    report["root_path"] = is_root_path(str(dependency["path"]))
    return report


def _reference_record(
    path: Path,
    *,
    label: str,
    role: str,
    relative_path: str,
    identity_reference_only: bool = False,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    resolved = path.expanduser().resolve(strict=False)
    record = {
        "path": str(resolved),
        "relative_path": relative_path,
        "label": label,
        "role": role,
        "identity_reference_only": identity_reference_only,
        "exists": resolved.is_file(),
        "view_before_attach": True,
    }
    if extra:
        record.update(extra)
    return record


def _character_reference_contract(
    dependency: Mapping[str, Any] | None,
    index: int,
) -> tuple[str, str, dict[str, Any]]:
    """Return role, label suffix, and strategy metadata for one IP input."""

    policy = str((dependency or {}).get("reference_policy", "direct-character"))
    if policy == "comic-character-sheet":
        return (
            "character_setting",
            "character setting reference only",
            {
                "character_reference_stage": "primary",
                "derived_sheet_role": "secondary_anchor_only",
                "original_asset_overrides_derived_sheet": True,
            },
        )
    if policy == "deck-identity":
        return (
            "deck_identity",
            "deck identity reference only",
            {
                "deck_identity_reference": True,
                "appearance_scope": "content-appropriate pages only",
            },
        )
    if policy == "xhs-chain-anchor":
        return (
            "character_identity",
            "identity reference only",
            {
                # Every selected original is attached to the first generated
                # image.  The first output, not any original asset, becomes
                # the chain anchor for later cards.
                "direct_reference_for": "first_generated_output",
                "first_output_direct_reference": True,
                "chain_anchor": False,
                "chain_anchor_source": None,
                "chain_anchor_order": None,
            },
        )
    if policy == "gbro-cover-prompt":
        return (
            "character_identity",
            "identity reference only; not a human-face reference",
            {
                "character_reference_stage": "primary",
                "face_reference": False,
                "prompt_identity_injection": True,
                "character_identity_must_not_be_reinterpreted_as_real_person": True,
            },
        )
    return (
        "character_identity",
        "identity reference only",
        {"character_reference_stage": "primary"},
    )


def _reference_contract(dependency: Mapping[str, Any] | None) -> dict[str, Any]:
    """Describe how a selected dependency consumes the resolved inputs."""

    policy = str((dependency or {}).get("reference_policy", "native"))
    if policy == "xhs-chain-anchor":
        return {
            "policy": policy,
            "original_asset_direct_reference_for": "first_generated_output",
            "first_generated_output_becomes_chain_anchor_for": "subsequent_outputs",
            "all_selected_original_assets_required_for_first_output": True,
            "original_assets_must_not_be_chain_anchors": True,
        }
    if policy == "gbro-cover-prompt":
        return {
            "policy": policy,
            "asset_order": "selected_original_character_assets_first",
            "identity_reference_only": True,
            "face_reference_semantics": False,
            "preserve_identity_fields": [
                "facial features",
                "body proportions",
                "clothing",
                "identity colors",
                "tail or other registered silhouette anchors",
            ],
            "upstream_reference_semantics": (
                "do not call Rongbao character assets human-face references; keep each IP separate"
            ),
        }
    return {"policy": policy}


def assemble_reference_inputs(
    route: Mapping[str, Any],
    *,
    dependency_root: Path | None = None,
) -> dict[str, Any]:
    """Build stable ordered image inputs without loading or copying files."""

    records: list[dict[str, Any]] = []
    omissions: list[dict[str, str]] = []
    dependency = route.get("dependency") or {}
    character_dependency = dependency if route.get("mode") == "upstream" else None
    for character in route.get("character_inputs", []):
        index = len(records) + 1
        role, label_suffix, strategy_metadata = _character_reference_contract(character_dependency, index)
        records.append(
            _reference_record(
                Path(str(character["asset_path"])),
                label=f"Image {index} — {character['display_name']} {label_suffix}",
                role=role,
                relative_path=str(character["asset"]),
                identity_reference_only=True,
                extra={
                    **strategy_metadata,
                    "character_id": character["id"],
                    "identity_reference_path": character.get("identity_reference_path"),
                },
            )
        )

    if route.get("mode") != "upstream" or not route.get("inject_character_references"):
        return {
            "inputs": records,
            "referenced_image_paths": [record["path"] for record in records],
            "omissions": omissions,
            "view_each_before_attach": True,
            "prompt_only_no_view_image": True,
        }

    reference_inputs = dependency.get("reference_inputs", {})
    style_paths = list(reference_inputs.get("style", []))
    selected_ids = {character["id"] for character in route.get("character_inputs", [])}
    style_limit = 2 if "yazai" in selected_ids else len(style_paths)
    root_value = dependency_root or dependency.get("installed_location")
    if not root_value:
        for relative_path in style_paths[:style_limit]:
            omissions.append(
                {
                    "relative_path": str(relative_path),
                    "reason": "optional dependency is not installed",
                }
            )
        if "yazai" in selected_ids and len(style_paths) > 2:
            omissions.append(
                {
                    "relative_path": str(style_paths[2]),
                    "reason": "style_ref_03 is omitted by the identity-risk rule when Yazai is selected",
                }
            )
        if route.get("target_capability") == "article-infographic-3x4":
            for relative_path in reference_inputs.get("layout", []):
                omissions.append(
                    {
                        "relative_path": str(relative_path),
                        "reason": "optional dependency is not installed",
                    }
                )
        return {
            "inputs": records,
            "referenced_image_paths": [record["path"] for record in records],
            "omissions": omissions,
            "view_each_before_attach": True,
            "prompt_only_no_view_image": True,
        }

    root = Path(str(root_value)).expanduser().resolve(strict=False)
    for style_number, relative_path in enumerate(style_paths[:style_limit], start=1):
        index = len(records) + 1
        records.append(
            _reference_record(
                root / relative_path,
                label=f"Image {index} — style reference {style_number}",
                role="style_reference",
                relative_path=str(relative_path),
            )
        )
    if "yazai" in selected_ids and len(style_paths) > 2:
        omissions.append(
            {
                "relative_path": str(style_paths[2]),
                "reason": "style_ref_03 is omitted by the identity-risk rule when Yazai is selected",
            }
        )

    if route.get("target_capability") == "article-infographic-3x4":
        for layout_number, relative_path in enumerate(reference_inputs.get("layout", []), start=1):
            index = len(records) + 1
            records.append(
                _reference_record(
                    root / relative_path,
                    label=f"Image {index} — infographic layout reference {layout_number}",
                    role="layout_reference",
                    relative_path=str(relative_path),
                )
            )

    return {
        "inputs": records,
        "referenced_image_paths": [record["path"] for record in records],
        "omissions": omissions,
        "view_each_before_attach": True,
        "prompt_only_no_view_image": True,
    }


def route_request(
    request: str,
    *,
    model: str | None = None,
    model_confirmed: bool = False,
    dependency_root: Path | None = None,
    prompt_enhancer_root: Path | None = None,
    environment: Mapping[str, str] | None = None,
    home: Path | None = None,
) -> dict[str, Any]:
    """Return a deterministic native/upstream route and its input plan."""

    dependencies = _load_dependencies_by_id()
    signal = _registered_character_signal(request)
    dependency, capability = _select_target(request, dependencies)
    prompt_enhancer = _select_prompt_enhancer(request, dependencies)
    operation = detect_operation(request)
    requested_aspect_ratio = _requested_aspect_ratio(request)
    gbro_selected = dependency is not None and str(dependency["skill_id"]) == GBRO_SKILL_ID
    gbro_aspect_compatible = (
        not gbro_selected
        or requested_aspect_ratio is None
        or requested_aspect_ratio == "3:4"
    )
    adapter_signal = bool(signal["adapter_signal"])
    style_selection_required = (
        dependency is None
        and _is_generic_xhs_request(request)
        and not _baoyu_signal(request)
    )

    if style_selection_required:
        mode = "selection-required"
        target_skill = None
        inject = True
        reason = (
            "generic Xiaohongshu request needs a style choice; choose Guizang Swiss, "
            "Guizang Editorial, or Baoyu xhs-images"
        )
    elif dependency is not None:
        target_skill = str(dependency["skill_id"])
        if adapter_signal:
            mode = "upstream"
            inject = True
            reason = "registered character/IP signal authorizes the selected design Skill"
        else:
            mode = "direct-target"
            inject = False
            reason = (
                "upstream capability requested without a Rongbao character/IP signal; do not inject an IP"
                if target_skill == UPSTREAM_SKILL_ID
                else "design Skill requested without a Rongbao character/IP signal; do not inject an IP"
            )
    else:
        mode = "native"
        target_skill = None
        inject = True
        reason = "ordinary article illustration remains native"

    if prompt_enhancer is not None:
        reason = (
            f"{reason}; explicit GPT Image 2 style-library request attaches a prompt enhancer "
            "without replacing the base target"
        )

    character_inputs = resolve_character_inputs(request) if inject else []
    if dependency is None:
        dependency_report = {
            "skill_id": None,
            "status": "native",
            "installed": True,
            "available": True,
            "optional": False,
            "capabilities": [],
            "reference_inputs": {},
            "reference_policy": "native",
            "requires_gpt_image_2": False,
        }
    else:
        dependency_report = _dependency_report(
            dependency,
            dependency_root=dependency_root,
            environment=environment,
            home=home,
        )
    prompt_enhancer_report = None
    if prompt_enhancer is not None:
        enhancer_root = prompt_enhancer_root
        if enhancer_root is None and dependency is None:
            enhancer_root = dependency_root
        prompt_enhancer_report = _dependency_report(
            prompt_enhancer,
            dependency_root=enhancer_root,
            environment=environment,
            home=home,
        )
        prompt_enhancer_report["selected"] = True
        prompt_enhancer_report["base_target_skill_id"] = (
            str(dependency["skill_id"]) if dependency is not None else None
        )
        prompt_enhancer_report["output_fields"] = list(PROMPT_ENHANCER_OUTPUTS)
        prompt_enhancer_report["identity_policy"] = (
            "character references remain identity-only inputs; never use them as style references"
        )
    dependency_report["reference_requirements"] = (dependency or {}).get("reference_inputs", {})
    selected_model_gate = _model_gate_for_route(
        dependency,
        prompt_enhancer,
        model,
        explicitly_confirmed=model_confirmed,
        request=request,
    )
    route: dict[str, Any] = {
        "request": request,
        "operation": operation,
        "mode": mode,
        "target_skill_id": target_skill,
        "target_capability": capability,
        "delivery_mode": (
            "prompt-package"
            if dependency is not None and dependency.get("output_mode") == "prompt-only"
            else "target-skill"
        ),
        "prompt_only": bool(
            dependency is not None and dependency.get("output_mode") == "prompt-only"
        ),
        "aspect_ratio": {
            "requested": requested_aspect_ratio,
            "required": (
                str(dependency.get("fixed_aspect_ratio"))
                if gbro_selected and dependency is not None
                else None
            ),
            "compatible": gbro_aspect_compatible,
            "warning": (
                "gbro-cover-design 固定 3:4 竖版；请移除当前画幅要求，或改用 Dongfang/Baoyu 生成其他画幅。"
                if gbro_selected and not gbro_aspect_compatible
                else None
            ),
        },
        "prompt_package": (
            {
                "output_mode": "prompt-only",
                "fixed_aspect_ratio": "3:4",
                "safe_area": "关键元素距四边至少约 10%",
                "briefing_rounds": 3,
                "layout_style_count": 10,
                "title_suggestions": "target Skill derives 1-3 concise title candidates from the source content",
                "reference_semantics": (
                    "selected original IP images come first and are identity-only; never treat them as a human-face reference"
                ),
                "required_sections": [
                    "3:4 vertical composition",
                    "selected layout style",
                    "title and text hierarchy",
                    "foreground/midground/background spatial relations",
                    "reference-image mapping",
                    "Chinese text verification reminder",
                ],
            }
            if gbro_selected
            else None
        ),
        "style_selection_required": style_selection_required,
        "style_candidates": (
            [
                {
                    "label": "归藏瑞士风",
                    "target_skill_id": GUIZANG_SKILL_ID,
                    "target_capability": "swiss-social-card",
                },
                {
                    "label": "归藏电子杂志风",
                    "target_skill_id": GUIZANG_SKILL_ID,
                    "target_capability": "editorial-social-card",
                },
                {
                    "label": "Baoyu 小红书图文",
                    "target_skill_id": "baoyu-xhs-images",
                    "target_capability": "xhs-images",
                },
            ]
            if style_selection_required
            else []
        ),
        "inject_character_references": inject,
        "reason": reason,
        "signals": signal,
        "characters": [item["id"] for item in character_inputs],
        "character_inputs": character_inputs,
        "reference_policy": (dependency or {}).get("reference_policy", "native"),
        "reference_contract": _reference_contract(dependency),
        "dependency": dependency_report,
        "prompt_enhancer": prompt_enhancer_report,
        "prompt_enhancement": {
            "enabled": prompt_enhancer_report is not None,
            "skill_id": (
                str(prompt_enhancer["skill_id"]) if prompt_enhancer is not None else None
            ),
            "base_target_unchanged": True,
            "output_fields": list(PROMPT_ENHANCER_OUTPUTS),
            "role": "prompt_enhancer",
            "style_library_controls": [
                "visual medium",
                "information hierarchy",
                "text constraints",
                "prompt controllability",
            ],
            "target_skill_controls": [
                "canvas and aspect ratio",
                "layout and delivery path",
                "target-specific generation contract",
            ],
            "character_identity_controls": [
                "selected original reference images",
                "identity protocols",
                "character clothing and colors",
            ],
        },
        "model_gate": selected_model_gate,
    }
    references = assemble_reference_inputs(route, dependency_root=dependency_root)
    route["reference_inputs"] = references["inputs"]
    route["referenced_image_paths"] = references["referenced_image_paths"]
    route["reference_omissions"] = references["omissions"]
    route["image_input_contract"] = {
        "view_each_before_attach": references["view_each_before_attach"],
        "pass_same_order_to_referenced_image_paths": True,
        "prompt_only_returns_paths_without_loading": references["prompt_only_no_view_image"],
        "prompt_labels": [record["label"] for record in references["inputs"]],
    }
    model_ready = (
        operation != "create"
        or not bool(
            (dependency or {}).get("requires_gpt_image_2", False)
            or (prompt_enhancer or {}).get("requires_gpt_image_2", False)
        )
        or route["model_gate"]["direct_generation_allowed"]
    )
    enhancer_ready = prompt_enhancer_report is None or bool(prompt_enhancer_report["installed"])
    route["generation_ready"] = bool(
        not style_selection_required
        and not (gbro_selected and not gbro_aspect_compatible)
        and not (gbro_selected and dependency.get("output_mode") == "prompt-only")
        and (
            enhancer_ready
            and model_ready
            and (
                target_skill is None
                or (
                    dependency_report["installed"]
                    and (
                        not inject
                        or all(record["exists"] for record in references["inputs"])
                    )
                )
            )
        )
    )
    return route


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Route Rongbao requests to native or optional design Skills")
    parser.add_argument("request", help="full user request")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON")
    parser.add_argument("--model", default=None, help="runtime model/tool name")
    parser.add_argument(
        "--confirm-gpt-image-2",
        action="store_true",
        help="explicitly confirm that the callable model is GPT Image 2",
    )
    args = parser.parse_args(argv)
    try:
        result = route_request(
            args.request,
            model=args.model,
            model_confirmed=args.confirm_gpt_image_2,
        )
    except (DesignRoutingError, DependencyRegistryError, OSError, ValueError) as exc:
        if args.as_json:
            print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        else:
            print(f"error: {exc}")
        return 2
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{result['mode']}: {result['target_skill_id'] or 'native'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
