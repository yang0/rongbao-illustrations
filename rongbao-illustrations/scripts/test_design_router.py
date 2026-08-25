#!/usr/bin/env python3
"""Self-contained tests for optional dependency probing and design routing."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import doctor
from dependency_utils import (
    dependency_candidate_paths,
    dependency_source_url,
    inspect_dependency,
    load_dependency_registry,
)
from design_router import (
    assemble_reference_inputs,
    model_gate,
    route_request,
)


ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = ROOT / "rongbao-illustrations"
REGISTRY_PATH = SKILL_DIR / "references" / "design-dependencies.json"
DEPENDENCIES = load_dependency_registry(REGISTRY_PATH)["dependencies"]
DEPENDENCIES_BY_ID = {item["skill_id"]: item for item in DEPENDENCIES}
DONGFANG = DEPENDENCIES_BY_ID["dongfang-cover-design"]
UPSTREAM = DEPENDENCIES_BY_ID["ip-illustration-character-system"]
BAOYU_DEPENDENCIES = [
    item for item in DEPENDENCIES if str(item["skill_id"]).startswith("baoyu-")
]
GUIZANG = DEPENDENCIES_BY_ID["guizang-social-card-skill"]
GPT_IMAGE_2_STYLE_LIBRARY = DEPENDENCIES_BY_ID["gpt-image-2-style-library"]
GBRO = DEPENDENCIES_BY_ID["gbro-cover-design"]
PNG_BYTES = (SKILL_DIR / "assets" / "rongbao.png").read_bytes()


def write_upstream_fixture(root: Path, *, skill_name: str = "ip-illustration-character-system") -> None:
    (root / "SKILL.md").write_text(
        f"---\nname: {skill_name}\ndescription: fixture\n---\n",
        encoding="utf-8",
    )
    for relative_path in UPSTREAM["reference_inputs"]["style"] + UPSTREAM["reference_inputs"]["layout"]:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(PNG_BYTES)


def write_skill_fixture(root: Path, skill_name: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "SKILL.md").write_text(
        f"---\nname: {skill_name}\ndescription: fixture\n---\n",
        encoding="utf-8",
    )


def write_gbro_fixture(root: Path, *, include_references: bool = True) -> None:
    write_skill_fixture(root, GBRO["skill_id"])
    if include_references:
        (root / "references").mkdir(parents=True, exist_ok=True)


def test_dependency_probe() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        temp_root = Path(temporary)
        codex_home = temp_root / "codex"
        installed = codex_home / "skills" / UPSTREAM["install_name"]
        installed.mkdir(parents=True)
        write_upstream_fixture(installed)
        environment = {"CODEX_HOME": str(codex_home)}

        report = inspect_dependency(UPSTREAM, skill_root=SKILL_DIR, environment=environment, home=temp_root)
        assert report["status"] == "installed"
        assert report["installed"] is True
        assert report["install_name"] == "ip-illustration-character-system"
        assert report["root_path"] is True
        assert report["installed_location"] == str(installed.resolve())
        assert report["source"] == "https://github.com/EverettFish/ip_illustration_for_yourself/tree/main"
        assert "/." not in report["source"]
        assert report["install"]["args"] == [
            "--repo",
            "EverettFish/ip_illustration_for_yourself",
            "--path",
            ".",
            "--name",
            "ip-illustration-character-system",
            "--ref",
            "main",
        ]
        assert "--path ." in report["install"]["command"]
        assert "--name ip-illustration-character-system" in report["install"]["command"]

        missing = inspect_dependency(
            UPSTREAM,
            skill_root=SKILL_DIR,
            environment={"CODEX_HOME": str(temp_root / "missing-codex")},
            home=temp_root,
        )
        assert missing["status"] == "missing"
        assert missing["installed"] is False
        assert missing["optional"] is True

        (installed / "SKILL.md").write_text(
            "---\nname: wrong-skill-id\ndescription: fixture\n---\n", encoding="utf-8"
        )
        wrong = inspect_dependency(UPSTREAM, skill_root=SKILL_DIR, environment=environment, home=temp_root)
        assert wrong["status"] == "invalid"
        assert wrong["installed"] is False
        assert wrong["locations"][0]["name_match"] is False

        custom_registry = {"version": 1, "dependencies": [UPSTREAM]}
        installed_report = doctor.diagnose(
            registry=custom_registry,
            skill_dir=SKILL_DIR,
            environment=environment,
            home=temp_root,
        )
        assert installed_report["dependencies"][0]["status"] == "invalid"
        assert doctor.strict_dependency_failure(installed_report["dependencies"]) is True
        missing_report = doctor.diagnose(
            registry=custom_registry,
            skill_dir=SKILL_DIR,
            environment={"CODEX_HOME": str(temp_root / "missing-codex")},
            home=temp_root,
        )
        assert missing_report["dependencies"][0]["status"] == "missing"
        assert doctor.strict_dependency_failure(missing_report["dependencies"]) is False


def test_baoyu_dependency_probe() -> None:
    assert len(BAOYU_DEPENDENCIES) == 6
    assert all(dependency["repo"] == "JimLiu/baoyu-skills" for dependency in BAOYU_DEPENDENCIES)
    assert all(dependency["ref"] == "main" for dependency in BAOYU_DEPENDENCIES)
    assert all(dependency["install_name"] == dependency["skill_id"] for dependency in BAOYU_DEPENDENCIES)
    with tempfile.TemporaryDirectory() as temporary:
        temp_root = Path(temporary)
        isolated_skill_dir = temp_root / "isolated" / "rongbao-illustrations"
        codex_home = temp_root / "codex"
        for dependency in BAOYU_DEPENDENCIES:
            write_skill_fixture(
                codex_home / "skills" / dependency["install_name"],
                dependency["skill_id"],
            )
        report = doctor.diagnose(
            registry={"version": 1, "dependencies": BAOYU_DEPENDENCIES},
            skill_dir=isolated_skill_dir,
            environment={"CODEX_HOME": str(codex_home)},
            home=temp_root,
        )
        assert {item["status"] for item in report["dependencies"]} == {"installed"}
        for dependency, item in zip(BAOYU_DEPENDENCIES, report["dependencies"]):
            assert item["skill_id"] == dependency["skill_id"]
            assert item["optional"] is True
            assert item["source"] == (
                f"https://github.com/JimLiu/baoyu-skills/tree/main/{dependency['path']}"
            )
            assert item["capabilities"] == dependency["capabilities"]
            assert item["install"]["args"] == [
                "--repo",
                "JimLiu/baoyu-skills",
                "--path",
                dependency["path"],
                "--name",
                dependency["skill_id"],
                "--ref",
                "main",
            ]
            assert item["installed_location"] == str(
                (codex_home / "skills" / dependency["install_name"]).resolve()
            )
        assert doctor.strict_dependency_failure(report["dependencies"]) is False

        missing_report = doctor.diagnose(
            registry={"version": 1, "dependencies": BAOYU_DEPENDENCIES},
            skill_dir=isolated_skill_dir,
            environment={"CODEX_HOME": str(temp_root / "missing-codex")},
            home=temp_root,
        )
        assert {item["status"] for item in missing_report["dependencies"]} == {"missing"}
        assert doctor.strict_dependency_failure(missing_report["dependencies"]) is False

        invalid_root = codex_home / "skills" / BAOYU_DEPENDENCIES[0]["install_name"]
        (invalid_root / "SKILL.md").write_text(
            "---\nname: wrong-baoyu-skill\ndescription: fixture\n---\n",
            encoding="utf-8",
        )
        invalid_report = doctor.diagnose(
            registry={"version": 1, "dependencies": BAOYU_DEPENDENCIES},
            skill_dir=isolated_skill_dir,
            environment={"CODEX_HOME": str(codex_home)},
            home=temp_root,
        )
        assert invalid_report["dependencies"][0]["status"] == "invalid"
        assert doctor.strict_dependency_failure(invalid_report["dependencies"]) is True


def test_guizang_dependency_probe() -> None:
    assert GUIZANG["repo"] == "op7418/guizang-social-card-skill"
    assert GUIZANG["path"] == "."
    assert GUIZANG["install_name"] == "guizang-social-card-skill"
    assert GUIZANG["ref"] == "main"
    assert GUIZANG["optional"] is True
    assert GUIZANG["license"] == "AGPL-3.0"
    assert GUIZANG["capabilities"] == [
        "xhs-social-cards",
        "swiss-social-card",
        "editorial-social-card",
        "wechat-cover-pair",
        "live-photo-card",
    ]
    with tempfile.TemporaryDirectory() as temporary:
        temp_root = Path(temporary)
        codex_home = temp_root / "codex"
        installed = codex_home / "skills" / GUIZANG["install_name"]
        write_skill_fixture(installed, GUIZANG["skill_id"])
        report = inspect_dependency(
            GUIZANG,
            skill_root=SKILL_DIR,
            environment={"CODEX_HOME": str(codex_home)},
            home=temp_root,
        )
        assert report["status"] == "installed"
        assert report["root_path"] is True
        assert report["source"] == "https://github.com/op7418/guizang-social-card-skill/tree/main"
        assert report["license"] == "AGPL-3.0"
        assert report["install"]["args"] == [
            "--repo",
            "op7418/guizang-social-card-skill",
            "--path",
            ".",
            "--name",
            "guizang-social-card-skill",
            "--ref",
            "main",
        ]
        missing = inspect_dependency(
            GUIZANG,
            skill_root=SKILL_DIR,
            environment={"CODEX_HOME": str(temp_root / "missing-codex")},
            home=temp_root,
        )
        assert missing["status"] == "missing"
        assert missing["optional"] is True


def test_dependency_sibling_candidates() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        temp_root = Path(temporary)
        root_dependency_candidates = dependency_candidate_paths(
            UPSTREAM,
            skill_root=SKILL_DIR,
            environment={},
            home=temp_root,
        )
        nested_dependency_candidates = dependency_candidate_paths(
            DONGFANG,
            skill_root=SKILL_DIR,
            environment={},
            home=temp_root,
        )
        assert (ROOT.parent / "ip_illustration_for_yourself").resolve() in root_dependency_candidates
        assert (ROOT.parent / "dongfang" / "dongfang-cover-design").resolve() in nested_dependency_candidates

        enhancer_candidates = dependency_candidate_paths(
            GPT_IMAGE_2_STYLE_LIBRARY,
            skill_root=SKILL_DIR,
            environment={},
            home=temp_root,
        )
        assert (
            ROOT.parent
            / "awesome-gpt-image-2"
            / "agents"
            / "skills"
            / "gpt-image-2-style-library"
        ).resolve() in enhancer_candidates


def test_gpt_image_2_style_library_is_opt_in_prompt_enhancer() -> None:
    assert GPT_IMAGE_2_STYLE_LIBRARY["repo"] == "freestylefly/awesome-gpt-image-2"
    assert GPT_IMAGE_2_STYLE_LIBRARY["path"] == "agents/skills/gpt-image-2-style-library"
    assert GPT_IMAGE_2_STYLE_LIBRARY["install_name"] == "gpt-image-2-style-library"
    assert GPT_IMAGE_2_STYLE_LIBRARY["ref"] == "main"
    assert GPT_IMAGE_2_STYLE_LIBRARY["optional"] is True
    assert GPT_IMAGE_2_STYLE_LIBRARY["license"] == "MIT"
    assert GPT_IMAGE_2_STYLE_LIBRARY["purpose"] == "prompt-enhancement"
    with tempfile.TemporaryDirectory() as temporary:
        temp_root = Path(temporary)
        dongfang_root = temp_root / "dongfang"
        enhancer_root = temp_root / "gpt-image-2-style-library"
        write_skill_fixture(dongfang_root, DONGFANG["skill_id"])
        write_skill_fixture(enhancer_root, GPT_IMAGE_2_STYLE_LIBRARY["skill_id"])

        ordinary = route_request(
            "Use $rongbao-illustrations create 用牙仔做一张横版封面",
            dependency_root=dongfang_root,
            model="image_gen",
        )
        assert ordinary["target_skill_id"] == DONGFANG["skill_id"]
        assert ordinary["prompt_enhancer"] is None

        enhanced = route_request(
            "Use $rongbao-illustrations create 用牙仔做一张横版封面，并使用 GPT Image 2 风格库增强提示词",
            dependency_root=dongfang_root,
            prompt_enhancer_root=enhancer_root,
            model="image_gen",
        )
        assert enhanced["target_skill_id"] == DONGFANG["skill_id"]
        assert enhanced["target_capability"] == "landscape-cover"
        assert enhanced["prompt_enhancer"]["skill_id"] == GPT_IMAGE_2_STYLE_LIBRARY["skill_id"]
        assert enhanced["prompt_enhancer"]["status"] == "installed"
        assert enhanced["prompt_enhancement"]["base_target_unchanged"] is True
        assert enhanced["prompt_enhancement"]["output_fields"] == [
            "template_name",
            "style_tags",
            "scene_tags",
            "case_ids",
            "structured_prompt",
            "negative_constraints",
        ]
        assert enhanced["model_gate"]["required_by"] == [
            GPT_IMAGE_2_STYLE_LIBRARY["skill_id"]
        ]
        assert enhanced["model_gate"]["delivery"] == "prompt-package"
        assert enhanced["generation_ready"] is False

        confirmed = route_request(
            "Use $rongbao-illustrations create 用牙仔做一张横版封面，并使用 gpt-image-2-style-library 增强提示词",
            dependency_root=dongfang_root,
            prompt_enhancer_root=enhancer_root,
            model="gpt-image-2",
            model_confirmed=True,
        )
        assert confirmed["target_skill_id"] == DONGFANG["skill_id"]
        assert confirmed["prompt_enhancer"]["skill_id"] == GPT_IMAGE_2_STYLE_LIBRARY["skill_id"]
        assert confirmed["model_gate"]["direct_generation_allowed"] is True
        assert confirmed["generation_ready"] is True

        baoyu_enhanced = route_request(
            "Use $rongbao-illustrations prompt 用绒宝做 Baoyu 知识漫画，并按模板增强提示词",
            prompt_enhancer_root=enhancer_root,
            model="gpt-image-2",
            model_confirmed=True,
        )
        assert baoyu_enhanced["target_skill_id"] == "baoyu-comic"
        assert baoyu_enhanced["prompt_enhancer"]["skill_id"] == GPT_IMAGE_2_STYLE_LIBRARY["skill_id"]

        guizang_enhanced = route_request(
            "Use $rongbao-illustrations prompt 用阿龅做归藏瑞士风社交卡，并使用模板库增强提示词",
            prompt_enhancer_root=enhancer_root,
            model="gpt-image-2",
            model_confirmed=True,
        )
        assert guizang_enhanced["target_skill_id"] == GUIZANG["skill_id"]
        assert guizang_enhanced["prompt_enhancer"]["skill_id"] == GPT_IMAGE_2_STYLE_LIBRARY["skill_id"]

        missing = route_request(
            "Use $rongbao-illustrations prompt 用牙仔做一张方图，并使用 GPT Image 2 模板库增强提示词",
            environment={"CODEX_HOME": str(temp_root / "missing-codex")},
            home=temp_root,
        )
        assert missing["target_skill_id"] == DONGFANG["skill_id"]
        assert missing["prompt_enhancer"]["status"] == "missing"
        assert missing["prompt_enhancer"]["license"] == "MIT"
        assert "--path agents/skills/gpt-image-2-style-library" in missing["prompt_enhancer"]["install"]["command"]



def test_guizang_routing_and_style_selection() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        guizang_root = Path(temporary) / "guizang"
        write_skill_fixture(guizang_root, GUIZANG["skill_id"])

        swiss = route_request(
            "用归藏瑞士风做一套小红书图文",
            dependency_root=guizang_root,
        )
        assert swiss["mode"] == "direct-target"
        assert swiss["target_skill_id"] == GUIZANG["skill_id"]
        assert swiss["target_capability"] == "swiss-social-card"
        assert swiss["inject_character_references"] is False
        assert swiss["characters"] == []

        editorial = route_request(
            "Use guizang-social-card-skill create 电子杂志风社交卡",
            dependency_root=guizang_root,
        )
        assert editorial["target_capability"] == "editorial-social-card"
        assert editorial["mode"] == "direct-target"

        wechat = route_request(
            "用归藏做公众号封面对（21:9 + 1:1）",
            dependency_root=guizang_root,
        )
        assert wechat["target_capability"] == "wechat-cover-pair"

        live_photo = route_request(
            "用归藏做一张 Live Photo 卡片",
            dependency_root=guizang_root,
        )
        assert live_photo["target_capability"] == "live-photo-card"

        injected = route_request(
            "Use $rongbao-illustrations create 用牙仔做归藏瑞士风小红书图文",
            dependency_root=guizang_root,
        )
        assert injected["mode"] == "upstream"
        assert injected["target_skill_id"] == GUIZANG["skill_id"]
        assert injected["target_capability"] == "swiss-social-card"
        assert injected["characters"] == ["yazai"]
        assert [Path(path).name for path in injected["referenced_image_paths"]] == ["yazai.png"]
        assert injected["reference_inputs"][0]["identity_reference_path"].endswith(
            "yazai-identity.md"
        )

        generic = route_request("做一套小红书图文")
        assert generic["mode"] == "selection-required"
        assert generic["style_selection_required"] is True
        assert generic["generation_ready"] is False
        assert {item["target_capability"] for item in generic["style_candidates"]} == {
            "swiss-social-card",
            "editorial-social-card",
            "xhs-images",
        }

        explicit_baoyu = route_request("宝玉做一套小红书图文")
        assert explicit_baoyu["target_skill_id"] == "baoyu-xhs-images"
        assert explicit_baoyu["style_selection_required"] is False


def test_routing_and_input_order() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        upstream_root = Path(temporary) / "upstream"
        upstream_root.mkdir()
        write_upstream_fixture(upstream_root)
        dongfang_root = Path(temporary) / "dongfang"
        write_skill_fixture(dongfang_root, DONGFANG["skill_id"])
        baoyu_roots: dict[str, Path] = {}
        for dependency in BAOYU_DEPENDENCIES:
            root = Path(temporary) / dependency["skill_id"]
            write_skill_fixture(root, dependency["skill_id"])
            baoyu_roots[dependency["skill_id"]] = root
        missing_environment = {"CODEX_HOME": str(Path(temporary) / "missing-codex")}

        native = route_request("生成一张普通文章配图")
        assert native["mode"] == "native"
        assert native["target_skill_id"] is None
        assert native["characters"] == ["yazai"]
        assert [record["role"] for record in native["reference_inputs"]] == ["character_identity"]

        ordinary_cover = route_request(
            "做一张普通横版封面",
            dependency_root=dongfang_root,
            model="image_gen",
        )
        assert ordinary_cover["mode"] == "direct-target"
        assert ordinary_cover["target_skill_id"] == DONGFANG["skill_id"]
        assert ordinary_cover["target_capability"] == "landscape-cover"
        assert ordinary_cover["inject_character_references"] is False
        assert ordinary_cover["reference_inputs"] == []

        default_ip_cover = route_request(
            "这个IP做一张普通横版封面",
            dependency_root=dongfang_root,
            model="image_gen",
        )
        assert default_ip_cover["mode"] == "upstream"
        assert default_ip_cover["target_skill_id"] == DONGFANG["skill_id"]
        assert default_ip_cover["characters"] == ["yazai"]
        assert [Path(path).name for path in default_ip_cover["referenced_image_paths"]] == [
            "yazai.png"
        ]

        rongbao_cover = route_request(
            "Use $rongbao-illustrations create 用绒宝做一张横版封面",
            dependency_root=dongfang_root,
            model="image_gen",
        )
        assert rongbao_cover["mode"] == "upstream"
        assert rongbao_cover["target_skill_id"] == DONGFANG["skill_id"]
        assert rongbao_cover["characters"] == ["rongbao"]
        assert [item["role"] for item in rongbao_cover["reference_inputs"]] == ["character_identity"]

        baoyu_cases = (
            ("baoyu-article-illustrator", "宝玉做一张文章配图", "article-illustration"),
            ("baoyu-comic", "宝玉做一套知识漫画", "comic"),
            ("baoyu-cover-image", "宝玉做一张封面图", "cover-image"),
            ("baoyu-infographic", "宝玉做一张信息图", "infographic"),
            ("baoyu-slide-deck", "宝玉做一套幻灯片", "slide-deck"),
            ("baoyu-xhs-images", "宝玉做一套小红书图片", "xhs-images"),
        )
        for skill_id, request, capability in baoyu_cases:
            routed = route_request(
                f"Use $rongbao-illustrations create 用牙仔和绒宝{request}",
                dependency_root=baoyu_roots[skill_id],
                model="image_gen",
            )
            assert routed["mode"] == "upstream"
            assert routed["target_skill_id"] == skill_id
            assert routed["target_capability"] == capability
            assert routed["characters"] == ["rongbao", "yazai"]
            assert [Path(path).name for path in routed["referenced_image_paths"]] == [
                "rongbao.png",
                "yazai.png",
            ]
            if skill_id == "baoyu-comic":
                assert [item["role"] for item in routed["reference_inputs"]] == [
                    "character_setting",
                    "character_setting",
                ]
                assert all(item["original_asset_overrides_derived_sheet"] for item in routed["reference_inputs"])
            elif skill_id == "baoyu-slide-deck":
                assert [item["role"] for item in routed["reference_inputs"]] == [
                    "deck_identity",
                    "deck_identity",
                ]
                assert all(item["appearance_scope"] == "content-appropriate pages only" for item in routed["reference_inputs"])
            elif skill_id == "baoyu-xhs-images":
                assert all(item["chain_anchor"] is False for item in routed["reference_inputs"])
                assert all(item["chain_anchor_source"] is None for item in routed["reference_inputs"])
                assert all(
                    item["direct_reference_for"] == "first_generated_output"
                    for item in routed["reference_inputs"]
                )
                assert all(item["first_output_direct_reference"] is True for item in routed["reference_inputs"])
                assert routed["reference_contract"] == {
                    "policy": "xhs-chain-anchor",
                    "original_asset_direct_reference_for": "first_generated_output",
                    "first_generated_output_becomes_chain_anchor_for": "subsequent_outputs",
                    "all_selected_original_assets_required_for_first_output": True,
                    "original_assets_must_not_be_chain_anchors": True,
                }
            else:
                assert [item["role"] for item in routed["reference_inputs"]] == [
                    "character_identity",
                    "character_identity",
                ]
            assert routed["model_gate"]["direct_generation_allowed"] is True
            assert routed["model_gate"]["applies"] is False

        baoyu_direct = route_request(
            "$baoyu-comic create 做一套知识漫画",
            dependency_root=baoyu_roots["baoyu-comic"],
            model="unknown-tool",
        )
        assert baoyu_direct["mode"] == "direct-target"
        assert baoyu_direct["target_skill_id"] == "baoyu-comic"
        assert baoyu_direct["inject_character_references"] is False
        assert baoyu_direct["characters"] == []
        assert baoyu_direct["reference_inputs"] == []
        assert baoyu_direct["generation_ready"] is True

        unique_baoyu_without_signal = route_request(
            "做一套知识漫画",
            dependency_root=baoyu_roots["baoyu-comic"],
        )
        assert unique_baoyu_without_signal["mode"] == "direct-target"
        assert unique_baoyu_without_signal["target_skill_id"] == "baoyu-comic"
        assert unique_baoyu_without_signal["inject_character_references"] is False

        default_ip_baoyu = route_request(
            "该IP做一套知识漫画",
            dependency_root=baoyu_roots["baoyu-comic"],
        )
        assert default_ip_baoyu["mode"] == "upstream"
        assert default_ip_baoyu["target_skill_id"] == "baoyu-comic"
        assert default_ip_baoyu["characters"] == ["yazai"]
        assert [Path(path).name for path in default_ip_baoyu["referenced_image_paths"]] == [
            "yazai.png"
        ]

        ordinary_article = route_request("生成一张普通文章配图")
        assert ordinary_article["mode"] == "native"
        assert ordinary_article["target_skill_id"] is None
        ordinary_infographic = route_request("做一张普通 3:4 信息图")
        assert ordinary_infographic["target_skill_id"] == UPSTREAM["skill_id"]
        assert ordinary_infographic["target_capability"] == "article-infographic-3x4"

        missing_sticker = route_request(
            "Use $rongbao-illustrations prompt 用 yazai 做一套萌粒贴纸",
            environment=missing_environment,
            home=Path(temporary),
        )
        sticker_omissions = {
            Path(item["relative_path"]).name: item["reason"]
            for item in missing_sticker["reference_omissions"]
        }
        assert set(sticker_omissions) == {
            "style_ref_01_user_docs_reader.png",
            "style_ref_02_user_searcher.png",
            "style_ref_03_user_catgirl_anchor.png",
        }
        assert "identity-risk" in sticker_omissions["style_ref_03_user_catgirl_anchor.png"]
        assert not any("layout" in item["relative_path"] for item in missing_sticker["reference_omissions"])

        missing_infographic = route_request(
            "Use $rongbao-illustrations prompt 用绒宝做一张 3:4 信息图",
            environment=missing_environment,
            home=Path(temporary),
        )
        infographic_omissions = [item["relative_path"] for item in missing_infographic["reference_omissions"]]
        assert set(infographic_omissions) == set(
            UPSTREAM["reference_inputs"]["style"] + UPSTREAM["reference_inputs"]["layout"]
        )
        assert any("layout" in relative_path for relative_path in infographic_omissions)

        unique_without_signal = route_request("做一张萌粒风格的 3:4 信息图")
        assert unique_without_signal["mode"] == "direct-target"
        assert unique_without_signal["target_skill_id"] == "ip-illustration-character-system"
        assert unique_without_signal["inject_character_references"] is False
        assert unique_without_signal["characters"] == []
        assert unique_without_signal["reference_inputs"] == []
        assert unique_without_signal["reason"] == (
            "upstream capability requested without a Rongbao character/IP signal; do not inject an IP"
        )

        default_ip_upstream = route_request(
            "这个IP做一套萌粒贴纸",
            dependency_root=upstream_root,
        )
        assert default_ip_upstream["mode"] == "upstream"
        assert default_ip_upstream["target_skill_id"] == UPSTREAM["skill_id"]
        assert default_ip_upstream["characters"] == ["yazai"]
        assert Path(default_ip_upstream["referenced_image_paths"][0]).name == "yazai.png"

        upstream = route_request(
            "Use $rongbao-illustrations create 用绒宝和牙仔做萌粒风格 3:4 信息图",
            dependency_root=upstream_root,
            model="image_gen",
        )
        assert upstream["mode"] == "upstream"
        assert upstream["target_skill_id"] == "ip-illustration-character-system"
        assert upstream["target_capability"] == "article-infographic-3x4"
        assert upstream["characters"] == ["rongbao", "yazai"]
        roles = [record["role"] for record in upstream["reference_inputs"]]
        assert roles[:2] == ["character_identity", "character_identity"]
        assert roles[2:4] == ["style_reference", "style_reference"]
        assert roles[4:] == ["layout_reference", "layout_reference", "layout_reference"]
        assert "style_ref_03" in " ".join(item["relative_path"] for item in upstream["reference_omissions"])
        assert all(Path(path).is_absolute() for path in upstream["referenced_image_paths"])
        assert all(Path(path).is_file() for path in upstream["referenced_image_paths"])
        assert upstream["model_gate"]["delivery"] == "prompt-package"

        yazai = route_request(
            "Use $rongbao-illustrations prompt 用 yazai 做一套萌粒贴纸",
            dependency_root=upstream_root,
            model="gpt-image-2",
            model_confirmed=True,
        )
        assert yazai["mode"] == "upstream"
        assert yazai["characters"] == ["yazai"]
        assert "style_ref_03" in " ".join(item["relative_path"] for item in yazai["reference_omissions"])
        assert all("rongbao.png" not in path for path in yazai["referenced_image_paths"])
        assert yazai["model_gate"]["direct_generation_allowed"] is True
        assert yazai["operation"] == "prompt"

        direct_without_signal = route_request(
            "$ip-illustration-character-system create 做一张萌粒贴纸",
            dependency_root=upstream_root,
            model="gpt-image-2",
            model_confirmed=True,
        )
        assert direct_without_signal["mode"] == "direct-target"
        assert direct_without_signal["inject_character_references"] is False
        assert direct_without_signal["characters"] == []
        assert direct_without_signal["reference_inputs"] == []
        assert direct_without_signal["generation_ready"] is True

        assembled = assemble_reference_inputs(upstream, dependency_root=upstream_root)
        assert assembled["referenced_image_paths"] == upstream["referenced_image_paths"]
        assert [item["label"] for item in assembled["inputs"]] == upstream["image_input_contract"]["prompt_labels"]


def test_model_gate() -> None:
    assert model_gate("gpt-image-2", explicitly_confirmed=True)["direct_generation_allowed"] is True
    assert model_gate("image_gen", explicitly_confirmed=True)["direct_generation_allowed"] is False
    assert model_gate("unknown-tool", explicitly_confirmed=True)["delivery"] == "prompt-package"
    assert model_gate("gpt-image-2", request="请生成图片")["direct_generation_allowed"] is False
    assert model_gate(None, request="请使用 GPT Image 2 生成")["direct_generation_allowed"] is False
    assert model_gate("gpt-image-2", request="请使用 GPT Image 2 生成")["direct_generation_allowed"] is True


def test_gbro_dependency_probe_and_required_references() -> None:
    assert GBRO["repo"] == "pyang5166/gbro-cover-design"
    assert GBRO["path"] == "."
    assert GBRO["install_name"] == "gbro-cover-design"
    assert GBRO["ref"] == "main"
    assert GBRO["optional"] is True
    assert GBRO["license"] == "MIT"
    assert GBRO["reference_policy"] == "gbro-cover-prompt"
    assert GBRO["output_mode"] == "prompt-only"
    assert GBRO["fixed_aspect_ratio"] == "3:4"
    assert GBRO["required_paths"] == ["references"]
    with tempfile.TemporaryDirectory() as temporary:
        temp_root = Path(temporary)
        codex_home = temp_root / "codex"
        installed = codex_home / "skills" / GBRO["install_name"]
        write_gbro_fixture(installed)
        environment = {"CODEX_HOME": str(codex_home)}

        report = inspect_dependency(GBRO, skill_root=SKILL_DIR, environment=environment, home=temp_root)
        assert report["status"] == "installed"
        assert report["root_path"] is True
        assert report["required_paths"] == ["references"]
        assert report["locations"][0]["required_paths_present"] is True
        assert report["source"] == "https://github.com/pyang5166/gbro-cover-design/tree/main"
        assert report["install"]["args"] == [
            "--repo",
            "pyang5166/gbro-cover-design",
            "--path",
            ".",
            "--name",
            "gbro-cover-design",
            "--ref",
            "main",
        ]

        (installed / "references").rmdir()
        invalid = inspect_dependency(GBRO, skill_root=SKILL_DIR, environment=environment, home=temp_root)
        assert invalid["status"] == "invalid"
        assert invalid["installed"] is False
        assert invalid["locations"][0]["required_paths_present"] is False
        assert doctor.strict_dependency_failure([invalid]) is True

        missing = inspect_dependency(
            GBRO,
            skill_root=SKILL_DIR,
            environment={"CODEX_HOME": str(temp_root / "missing-codex")},
            home=temp_root,
        )
        assert missing["status"] == "missing"
        assert missing["optional"] is True
        assert doctor.strict_dependency_failure([missing]) is False


def test_gbro_explicit_prompt_routing_and_identity_order() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        temp_root = Path(temporary)
        gbro_root = temp_root / "gbro-cover-design"
        write_gbro_fixture(gbro_root)

        ordinary = route_request(
            "做一张普通横版封面",
            dependency_root=gbro_root,
            environment={"CODEX_HOME": str(temp_root / "missing-codex")},
            home=temp_root,
        )
        assert ordinary["target_skill_id"] == DONGFANG["skill_id"]
        assert ordinary["target_capability"] == "landscape-cover"

        direct = route_request(
            "Use gbro-cover-design prompt 做一张 3:4 竖版封面",
            dependency_root=gbro_root,
            environment={"CODEX_HOME": str(temp_root / "missing-codex")},
            home=temp_root,
        )
        assert direct["mode"] == "direct-target"
        assert direct["target_skill_id"] == GBRO["skill_id"]
        assert direct["target_capability"] == "cover-prompt-3x4"
        assert direct["inject_character_references"] is False
        assert direct["characters"] == []
        assert direct["delivery_mode"] == "prompt-package"
        assert direct["prompt_only"] is True
        assert direct["prompt_package"]["briefing_rounds"] == 3
        assert direct["prompt_package"]["layout_style_count"] == 10
        assert direct["generation_ready"] is False

        injected = route_request(
            "Use $rongbao-illustrations create 用绒宝和阿龅让 gbro 做一张三轮提问封面",
            dependency_root=gbro_root,
        )
        assert injected["mode"] == "upstream"
        assert injected["target_skill_id"] == GBRO["skill_id"]
        assert injected["target_capability"] == "cover-prompt-3x4"
        assert injected["characters"] == ["rongbao", "abao"]
        assert [Path(path).name for path in injected["referenced_image_paths"]] == [
            "rongbao.png",
            "abao.png",
        ]
        assert [item["role"] for item in injected["reference_inputs"]] == [
            "character_identity",
            "character_identity",
        ]
        assert all(item["face_reference"] is False for item in injected["reference_inputs"])
        assert injected["reference_contract"]["face_reference_semantics"] is False
        assert injected["generation_ready"] is False

        ten_styles = route_request(
            "用牙仔做一张 10 种构图风格封面",
            dependency_root=gbro_root,
        )
        assert ten_styles["target_skill_id"] == GBRO["skill_id"]
        assert ten_styles["characters"] == ["yazai"]

        incompatible = route_request(
            "Use gbro 封面 create 用牙仔做一张 16:9 横版封面",
            dependency_root=gbro_root,
        )
        assert incompatible["target_skill_id"] == GBRO["skill_id"]
        assert incompatible["aspect_ratio"]["compatible"] is False
        assert "固定 3:4" in incompatible["aspect_ratio"]["warning"]
        assert incompatible["generation_ready"] is False


test_dependency_probe()
test_baoyu_dependency_probe()
test_guizang_dependency_probe()
test_dependency_sibling_candidates()
test_guizang_routing_and_style_selection()
test_routing_and_input_order()
test_model_gate()
test_gbro_dependency_probe_and_required_references()
test_gbro_explicit_prompt_routing_and_identity_order()
print("design router tests passed")
