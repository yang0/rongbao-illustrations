# Showcase map

This directory is the source-of-truth map for the IP and capability gallery in the repository root [`README.md`](../../../README.md). It contains the declarative map plus project-generated showcase previews; it never vendors upstream source code or upstream reference assets.

## Source boundary

- `gallery-map.json` records the four registered IPs, every native or registered design capability, the copyable invocation, the target Skill, the expected aspect ratio, dependency-install status, and the image status.
- `gallery-map.json` also records `style_variant_gallery`, which contains colorful cross-Skill examples so the gallery does not imply that every mounted Skill shares the native white-background sketch style.
- `image_path` values point only to files already present in this repository. The comic and sticker previews are project-generated examples, not copied upstream material.
- Every registered capability now has a local project-generated preview. These previews prove the intended capability and aspect ratio; they are not official outputs or copied assets from optional upstream Skills.
- Optional dependencies remain optional: this folder does not vendor Dongfang, Everett, or Baoyu source code, style references, or assets.

## IP gallery

| IP | Asset | Identity protocol | Default |
| --- | --- | --- | --- |
| 绒宝 / `rongbao` | [`rongbao.webp`](../rongbao.webp) | [`rongbao-identity.md`](../../references/rongbao-identity.md) | No |
| 牙仔 / `yazai` | [`yazai.webp`](../yazai.webp) | [`yazai-identity.md`](../../references/yazai-identity.md) | **Yes** |
| 阿龅 / `abao` | [`abao.webp`](../abao.webp) | [`abao-identity.md`](../../references/abao-identity.md) | No |
| 小美 / `xiaomei` | [`xiaomei.webp`](../xiaomei.webp) | [`xiaomei-identity.md`](../../references/xiaomei-identity.md) | No |

The root README displays these four original project reference files directly. The default route is Yazai when no IP name is supplied; explicit names and multi-IP requests are documented there.

## Capability gallery records

The JSON is intentionally declarative. Use it to keep the README table, local showcase paths, and later imagegen handoff aligned without changing Skill IDs, dependency registration, or routing logic.

| Group | Capability | Target Skill | Aspect | Install dependency | Current image |
| --- | --- | --- | --- | --- | --- |
| Rongbao 原生 | `article-illustration` | `rongbao-illustrations` | 16:9 | No | [`01-two-breakpoints.webp`](../examples/01-two-breakpoints.webp) |
| Dongfang | `landscape-cover`（AI 工作流实验室高密度缩略图） | `dongfang-cover-design` | 16:9 | Yes | [`dongfang-landscape-cover.webp`](dongfang-landscape-cover.webp) |
| Dongfang | `portrait-poster` | `dongfang-cover-design` | 3:4 | Yes | [`dongfang-portrait-poster.webp`](dongfang-portrait-poster.webp) |
| Dongfang | `square-graphic` | `dongfang-cover-design` | 1:1 | Yes | [`dongfang-square-graphic.webp`](dongfang-square-graphic.webp) |
| Everett | `character-anchor` | `ip-illustration-character-system` | 3:4 | Yes | [`everett-character-anchor.webp`](everett-character-anchor.webp) |
| Everett | `turnaround-sheet` | `ip-illustration-character-system` | 3:4 | Yes | [`everett-turnaround-sheet.webp`](everett-turnaround-sheet.webp) |
| Everett | `mini-article-illustration` | `ip-illustration-character-system` | 3:4 | Yes | [`everett-mini-article-illustration.webp`](everett-mini-article-illustration.webp) |
| Everett | `article-infographic-3x4` | `ip-illustration-character-system` | 3:4 | Yes | [`everett-article-infographic-3x4.webp`](everett-article-infographic-3x4.webp) |
| Everett | `sticker-sheet-3x4` | `ip-illustration-character-system` | 3:4 | Yes | [`abao-sticker-preview.webp`](../../../comic/abao-sticker-preview/abao-sticker-preview.webp) |
| Baoyu | `article-illustration` | `baoyu-article-illustrator` | 16:9 | Yes | [`baoyu-article-illustration.webp`](baoyu-article-illustration.webp) |
| Baoyu | `comic` | `baoyu-comic` | 4:3 | Yes | [`01-page-positioning-bio.webp`](../../../comic/weichen-x-growth-sop/01-page-positioning-bio.webp) |
| Baoyu | `cover-image` | `baoyu-cover-image` | 4:3 | Yes | [`00-cover-weichen-x-growth-sop.webp`](../../../comic/weichen-x-growth-sop/00-cover-weichen-x-growth-sop.webp) |
| Baoyu | `infographic` | `baoyu-infographic` | 4:3 | Yes | [`baoyu-infographic.webp`](baoyu-infographic.webp) |
| Baoyu | `slide-deck` | `baoyu-slide-deck` | 16:9 | Yes | [`baoyu-slide-deck.webp`](baoyu-slide-deck.webp) |
| Baoyu | `xhs-images` | `baoyu-xhs-images` | 3:4 | Yes | [`baoyu-xhs-images.webp`](baoyu-xhs-images.webp) |
| gbro | `cover-prompt-3x4` | `gbro-cover-design` | 3:4 | Yes | [`gbro-abao-robot-price.webp`](gbro-abao-robot-price.webp) |

## Style variant previews

These additional previews are project-generated derivatives. They demonstrate that Rongbao supplies identity references while the mounted Skill controls the medium, palette, layout, and output ratio.

| Group | Style | Target Skill | Aspect | Preview |
| --- | --- | --- | --- | --- |
| Guizang | Swiss International | `guizang-social-card-skill` | 3:4 | [`guizang-swiss-social-card.webp`](guizang-swiss-social-card.webp) |
| Guizang | Editorial Magazine | `guizang-social-card-skill` | 3:4 | [`guizang-editorial-social-card.webp`](guizang-editorial-social-card.webp) |
| Dongfang | 彩色水墨 Editorial Cover | `dongfang-cover-design` | 16:9 | [`dongfang-color-ink-cover.webp`](dongfang-color-ink-cover.webp) |
| Dongfang | Non-Chinese high-density color poster | `dongfang-cover-design` | 3:4 | [`dongfang-non-chinese-color-poster.webp`](dongfang-non-chinese-color-poster.webp) |
| Everett | 彩色角色锚点 | `ip-illustration-character-system` | 3:4 | [`everett-color-character-anchor.webp`](everett-color-character-anchor.webp) |
| Baoyu | 彩色知识漫画 | `baoyu-comic` | 4:3 | [`baoyu-color-comic.webp`](baoyu-color-comic.webp) |
| gbro | 阿龅机器人降价封面 | `gbro-cover-design` | 3:4 | [`gbro-abao-robot-price.webp`](gbro-abao-robot-price.webp) |
| Rongbao composition | 真实场景 + 手绘牙仔 | `rongbao-illustrations` | 4:3 | [`real-scene-handdrawn-yazai.webp`](real-scene-handdrawn-yazai.webp) |
| Rongbao composition | 3D 动画电影感封面 | `rongbao-illustrations` | 16:9 | [`yazai-3d-animated-cover.webp`](yazai-3d-animated-cover.webp) |
| Personal IP | IP-05 → IP-03 个人 IP 制作流程 | `personal-ip-image-pack` | 16:9 | [`xiaomei-process-collage.webp`](xiaomei-process-collage.webp) |

The available comic and sticker files are evidence of local project output only. They are not claims that the optional target Skill is installed in this checkout or that its output contract has been independently re-run.
