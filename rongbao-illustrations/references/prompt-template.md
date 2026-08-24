# 生图提示词模板

以下模板只适用于本 Skill 的正文配图原生模式。先按 `character-routing.md` 解析角色；未指定时默认牙仔。组合到其他设计 Skill 时，不要套用本模板的白底手绘默认值；改为透传目标 Skill 契约，并附带角色注册表中每个选中角色的 `asset` 和 `identity_reference`。组合透传时补充：绒宝身份色默认保持鲜亮黄、鲜亮青绿和鲜亮橙，只有环境或用户明确要求时才局部变化；牙仔和阿龅遵循各自身份协议；禁止综合色偏、统一降饱和或复古做旧伪装融合。

## 强制图片输入契约

凡是实际生图或改图，必须先执行：

```text
python -X utf8 <skill-root>/scripts/character_router.py --json "<request>"
```

从 JSON 的 `character_inputs` 读取每个已选角色的 `asset_path`，按 `input_order` 对每个路径调用 `view_image`，并将全部这些绝对路径按同样顺序传给图像工具的 `referenced_image_paths`。提示词必须显式写出：

```text
Image 1 — {display_name}: identity reference only; preserve this character's identity.
Image 2 — {display_name}: identity reference only; preserve this character's identity.
```

多角色时只传本次 `character_inputs` 中的图片，不能附加未选角色，也不能把文字身份锚点当作图片输入的替代品。`prompt`、shot list 或路由计划不实际生图时不必加载图片，但要把 JSON 返回的 `asset_path` 与 `prompt_label` 展示在计划里。静态 prompt 使用 `assets/<id>.png`；运行时绝不使用开发机硬编码路径。

## 可选上游 prompt package

需要萌粒、角色锚点、转面图、3:4 信息图或 3:4 贴纸页时，先运行：

```text
python -X utf8 <skill-root>/scripts/design_router.py --json "<request>"
```

能力词或显式上游名称都可以使 `target_skill_id` 为 `ip-illustration-character-system`；只有请求含注册角色、IP 或 `$rongbao-illustrations` 信号时才注入角色。无信号时返回 `direct-target` prompt package，不附加任何角色图片。带角色输入时，`reference_inputs` 的顺序固定为：已选角色图片、`style_ref_01`、`style_ref_02`、未选牙仔时的 `style_ref_03`，以及仅信息图追加的 layout 图片。每一条实际使用的路径先 `view_image`，再把同一顺序传入 `referenced_image_paths`；提示词用返回的 `label` 逐条写出 `Image N` 和角色/用途。

该上游只接受 GPT Image 2 直接生图。若运行时没有显式确认 GPT Image 2，交付完整 prompt package、绝对参考图路径和以下官方链接，不静默改用通用图像工具：

- [GPT Image 2 model](https://developers.openai.com/api/docs/models/gpt-image-2)
- [Image generation API guide](https://developers.openai.com/api/docs/guides/image-generation)

## Baoyu 目标的图片输入策略

Baoyu 不使用 Everett 的 GPT Image 2 门禁。实际生图/改图仍必须先对所有选中的角色原图 `view_image`，再按 JSON 的 `referenced_image_paths` 原序传入，并用 Image 标签绑定显示名：

- `baoyu-article-illustrator`、`baoyu-cover-image`、`baoyu-infographic`：原图是 direct identity reference。
- `baoyu-comic`：原图是 primary character-setting reference；上游生成的 character sheet 只能是 secondary anchor，永远不能覆盖注册表原图。
- `baoyu-slide-deck`：原图是 deck identity reference；角色只在内容合适的页面出现，不强迫每页出现。
- `baoyu-xhs-images`：所有选中角色原图都是第 1 张生成的 direct references；第 1 张生成成品才是后续链式生成的 anchor；后续提示词保留身份约束并对照注册原图 QA，不附加未选角色。

没有角色/IP信号时，Baoyu 请求为 `direct-target`，不附加任何角色图片；显式 `$rongbao-illustrations`、“这个IP/该IP”或具体角色名才允许注入对应注册角色。

组合媒介适配约束（附加到目标 Skill 提示词）：

```text
Adapt each selected character's material, stroke, edge, grain, ambient light, and cast shadow to the target medium so every character and the scene share one visual medium and lighting logic. Keep Rongbao's identity colors bright yellow, teal green, and orange by default; allow only local changes required by the environment or an explicit user request, and follow the selected character's identity protocol for other colors and anchors. Keep Yazai and Abao as separate black-and-white identities unless their own protocols or the user specify otherwise. Do not preserve studio 3D fur, a hard cutout edge, isolated highlights, global color grading, uniform desaturation, or faux vintage aging. If a character still looks pasted on, make one targeted character-media integration pass only; lock composition, title, palette, and all selected identity anchors. Never blend two selected characters into one hybrid character.
```

每张图单独生成。根据正文内容替换变量，不要把多张图拼在一起。

下面的原生模板以牙仔为默认示例，并遵循 `yazai-identity.md`。若角色解析结果是显式选择的绒宝或阿龅，替换角色段为对应身份协议（`rongbao-identity.md` 或 `abao-identity.md`）；若同时选择两个或三个角色，则分别保留每段身份描述，让所有选中角色共同承担核心动作，同时避免角色融合。

```text
Generate one standalone 16:9 horizontal Chinese article illustration.

Visual DNA:
Pure white background. Minimalist black hand-drawn line art. Slightly wobbly pen lines. Lots of empty white space. Sparse red/orange/blue handwritten Chinese annotations. Clean absurd product-sketch feeling. No gradients, no shadows, no paper texture, no complex background, no commercial vector style, no PPT infographic look, no cute mascot poster, no children's illustration, no realistic UI.

Recurring selected IP character required:
Use every selected character input image in registry order. `Image 1`, `Image 2`, and `Image 3` are the actual `referenced_image_paths` passed to the image tool; each image is an identity reference only for the corresponding named character, not a style or composition reference. If no name was selected, use 牙仔 based on `assets/yazai.png` and its identity protocol: a black-and-white anthropomorphic cat with black pointed ears, a distinct head tuft, half-lidded vertical pupils, a broad flat face, two buck teeth, whiskers, a long curled tail, white shirt, black vest or bow tie, and apron. If 绒宝 was explicitly selected, use `assets/rongbao.png` and preserve its yellow round body, two teal leaf-like ears, large brown-black eyes with white sclera, orange cheeks, and orange hands and feet. If 阿龅 was selected, use `assets/abao.png` and preserve its black-and-white anthropomorphic dog, floppy black ears, head tufts, long muzzle and black nose, half-lidded eyes, two small front teeth, white collared shirt and dark workwear overalls/apron. Translate each reference into sparse black line art and restrained flat color without copying photography or rendered material. Every selected character must perform a core conceptual action, not decorate the scene; keep each identity separate and do not create a hybrid character.

Theme:
{正文配图主题}

Structure type:
{结构类型：Workflow / 系统局部 / 前后对比 / 角色状态 / 概念隐喻 / 方法分层 / 地图路线 / 小漫画分镜}

Core idea:
{这张图要表达的核心意思}

Composition:
{具体画面：每个已选角色在哪里、分别正在做什么、主要物件是什么、信息如何流动}

Suggested elements:
{元素1} / {元素2} / {元素3} / {元素4}

Chinese handwritten labels:
{标注词1} / {标注词2} / {标注词3} / {标注词4} / {可选标注词5}

Color use:
Black for main line art and structure. Keep 牙仔 and 阿龅's black-and-white identities unless the selected protocol or user asks for a deliberate change. If 绒宝 is explicitly selected, keep its identity colors bright yellow, teal green, and orange; restrain their area, not their saturation. Orange for main flow/path/arrows. Red only for key warnings/problems/results. Blue only for secondary notes or feedback/system state.

Constraints:
One image explains only one core structure. Keep the main subject around 40%-60% of the canvas. Preserve at least 35% blank white space. Use at most 5-8 short handwritten Chinese labels. Do not write a title in the top-left corner. Do not write the structure type on the image. Do not make it a formal diagram, course slide, or dense explainer. Do not copy prior examples or reuse known case compositions unless explicitly requested; invent a fresh visual metaphor for this specific article. It should be clear but not instructional, interesting but not childish, strange but clean.
```

## 图像编辑提示

去掉左上角标题：

```text
Edit the provided image. Remove only the handwritten title "{要删除的文字}" and its underline from the top-left corner. Fill that area with the same clean white background, matching the surrounding blank paper. Preserve everything else exactly: characters, labels, paths, line style, composition, aspect ratio, and image quality. Do not add any new text or objects.
```

增强怪诞感：

```text
Regenerate this illustration with the same core meaning and simple layout, but make every selected character central to the conceptual action. Each selected character should do a distinct part of the strange work that explains the idea, not stand beside the diagram. Keep each character's identity protocol recognizable, while keeping the result clean, sparse, hand-drawn, and not an over-cute mascot. Do not merge selected characters into one hybrid.
```
