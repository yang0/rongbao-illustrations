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
DONGFANG = DEPENDENCIES[0]
UPSTREAM = DEPENDENCIES[1]
BAOYU_DEPENDENCIES = DEPENDENCIES[2:]
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


test_dependency_probe()
test_baoyu_dependency_probe()
test_dependency_sibling_candidates()
test_routing_and_input_order()
test_model_gate()
print("design router tests passed")
