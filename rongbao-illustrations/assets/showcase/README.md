# Showcase map

This directory is the source-of-truth map for the IP and capability gallery in the repository root [`README.md`](../../../README.md). It contains the declarative map plus project-generated showcase previews; it never vendors upstream source code or upstream reference assets.

## Source boundary

- `gallery-map.json` records the three registered IPs, every native or registered design capability, the copyable invocation, the target Skill, the expected aspect ratio, dependency-install status, and the image status.
- `gallery-map.json` also records `style_variant_gallery`, which contains colorful cross-Skill examples so the gallery does not imply that every mounted Skill shares the native white-background sketch style.
- `image_path` values point only to files already present in this repository. The comic and sticker previews are project-generated examples, not copied upstream material.
- Every registered capability now has a local project-generated preview. These previews prove the intended capability and aspect ratio; they are not official outputs or copied assets from optional upstream Skills.
- Optional dependencies remain optional: this folder does not vendor Dongfang, Everett, or Baoyu source code, style references, or assets.

## IP gallery

| IP | Asset | Identity protocol | Default |
| --- | --- | --- | --- |
| 绒宝 / `rongbao` | [`rongbao.png`](../rongbao.png) | [`rongbao-identity.md`](../../references/rongbao-identity.md) | No |
| 牙仔 / `yazai` | [`yazai.png`](../yazai.png) | [`yazai-identity.md`](../../references/yazai-identity.md) | **Yes** |
| 阿龅 / `abao` | [`abao.png`](../abao.png) | [`abao-identity.md`](../../references/abao-identity.md) | No |

The root README displays these three original project reference files directly. The default route is Yazai when no IP name is supplied; explicit names and multi-IP requests are documented there.

## Capability gallery records

The JSON is intentionally declarative. Use it to keep the README table, local showcase paths, and later imagegen handoff aligned without changing Skill IDs, dependency registration, or routing logic.

| Group | Capability | Target Skill | Aspect | Install dependency | Current image |
| --- | --- | --- | --- | --- | --- |
| Rongbao 原生 | `article-illustration` | `rongbao-illustrations` | 16:9 | No | [`01-two-breakpoints.png`](../examples/01-two-breakpoints.png) |
| Dongfang | `landscape-cover` | `dongfang-cover-design` | 16:9 | Yes | [`dongfang-landscape-cover.png`](dongfang-landscape-cover.png) |
| Dongfang | `portrait-poster` | `dongfang-cover-design` | 3:4 | Yes | [`dongfang-portrait-poster.png`](dongfang-portrait-poster.png) |
| Dongfang | `square-graphic` | `dongfang-cover-design` | 1:1 | Yes | [`dongfang-square-graphic.png`](dongfang-square-graphic.png) |
| Everett | `character-anchor` | `ip-illustration-character-system` | 3:4 | Yes | [`everett-character-anchor.png`](everett-character-anchor.png) |
| Everett | `turnaround-sheet` | `ip-illustration-character-system` | 3:4 | Yes | [`everett-turnaround-sheet.png`](everett-turnaround-sheet.png) |
| Everett | `mini-article-illustration` | `ip-illustration-character-system` | 3:4 | Yes | [`everett-mini-article-illustration.png`](everett-mini-article-illustration.png) |
| Everett | `article-infographic-3x4` | `ip-illustration-character-system` | 3:4 | Yes | [`everett-article-infographic-3x4.png`](everett-article-infographic-3x4.png) |
| Everett | `sticker-sheet-3x4` | `ip-illustration-character-system` | 3:4 | Yes | [`abao-sticker-preview.png`](../../../comic/abao-sticker-preview/abao-sticker-preview.png) |
| Baoyu | `article-illustration` | `baoyu-article-illustrator` | 16:9 | Yes | [`baoyu-article-illustration.png`](baoyu-article-illustration.png) |
| Baoyu | `comic` | `baoyu-comic` | 4:3 | Yes | [`01-page-positioning-bio.png`](../../../comic/weichen-x-growth-sop/01-page-positioning-bio.png) |
| Baoyu | `cover-image` | `baoyu-cover-image` | 4:3 | Yes | [`00-cover-weichen-x-growth-sop.png`](../../../comic/weichen-x-growth-sop/00-cover-weichen-x-growth-sop.png) |
| Baoyu | `infographic` | `baoyu-infographic` | 4:3 | Yes | [`baoyu-infographic.png`](baoyu-infographic.png) |
| Baoyu | `slide-deck` | `baoyu-slide-deck` | 16:9 | Yes | [`baoyu-slide-deck.png`](baoyu-slide-deck.png) |
| Baoyu | `xhs-images` | `baoyu-xhs-images` | 3:4 | Yes | [`baoyu-xhs-images.png`](baoyu-xhs-images.png) |

## Style variant previews

These additional previews are project-generated derivatives. They demonstrate that Rongbao supplies identity references while the mounted Skill controls the medium, palette, layout, and output ratio.

| Group | Style | Target Skill | Aspect | Preview |
| --- | --- | --- | --- | --- |
| Guizang | Swiss International | `guizang-social-card-skill` | 3:4 | [`guizang-swiss-social-card.png`](guizang-swiss-social-card.png) |
| Guizang | Editorial Magazine | `guizang-social-card-skill` | 3:4 | [`guizang-editorial-social-card.png`](guizang-editorial-social-card.png) |
| Dongfang | 彩色水墨 Editorial Cover | `dongfang-cover-design` | 16:9 | [`dongfang-color-ink-cover.png`](dongfang-color-ink-cover.png) |
| Everett | 彩色角色锚点 | `ip-illustration-character-system` | 3:4 | [`everett-color-character-anchor.png`](everett-color-character-anchor.png) |
| Baoyu | 彩色知识漫画 | `baoyu-comic` | 4:3 | [`baoyu-color-comic.png`](baoyu-color-comic.png) |

The available comic and sticker files are evidence of local project output only. They are not claims that the optional target Skill is installed in this checkout or that its output contract has been independently re-run.
