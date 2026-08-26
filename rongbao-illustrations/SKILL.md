---
name: rongbao-illustrations
description: 生成可按名称选择已注册 IP（默认牙仔；含绒宝、阿龅和确认注册的个人角色）的中文正文配图；当用户同时提到角色、这个IP、显式调用 $rongbao-illustrations 或带IP，以及封面、竖版海报、方图、萌粒/角色锚点/转面/3:4 信息图/贴纸，Baoyu/宝玉 的内容能力，或真人照片个人 IP、本人/博主卡通形象、照片转卡通、人物表情包/动作包时，按注册依赖组合调用目标设计 Skill。用于正文配图、文章插图、配图建议、shot list、去标题/改图和 create|prompt 透传；未指定角色时默认牙仔，正文原生模式使用牙仔黑白身份协议、纯白手绘、少量红橙蓝批注、简洁清爽但天马行空的视觉风格。
---

# 绒宝怪诞正文配图与跨设计组合路由

## 核心定位

本 Skill 的原生模式为中文文章设计和生成 16:9 横版正文配图。目标不是做商业插画、PPT 信息图或可爱卡通，而是把文章里的关键判断、流程、结构、状态或隐喻，变成一张清爽、怪诞、有创意、可读但不说明书的手绘解释图。

默认视觉 IP 是“牙仔”：以 `assets/yazai.webp` 和 `references/yazai-identity.md` 为身份参考，保留黑白拟人猫、黑色尖耳、头顶毛块、半眯的竖瞳大眼、宽扁脸、两颗小门牙、胡须、长卷尾、白衬衫、黑马甲或黑领结和围裙；在本 Skill 中转译成简洁的黑色手绘线稿与克制平涂色块。牙仔认真做一件荒诞但成立的事，必须参与画面的核心动作，不能只是站在旁边当装饰。绒宝仍保留为显式角色，并遵循 `references/rongbao-identity.md` 的身份协议。

当用户同时提到具体角色名（绒宝/牙仔/阿龅及其别名）、“这个IP”“该IP”“带IP”等身份信号，或显式调用 `$rongbao-illustrations`，以及封面、竖版海报、方图，或已注册的萌粒/角色锚点/转面/3:4 信息图/贴纸能力时，进入跨设计组合模式：按 `references/design-routing.md` 路由到已注册目标设计 Skill。目标 Skill 决定画幅、构图、材质、光线、文字和输出；本 Skill 只提供已选择角色的身份锚点与角色参考图，不能把正文的白底手绘默认强加给目标 Skill。

## 执行面与优先级

- 正文文章插图、帖子配图、方法论配图或明确的 16:9 正文请求：走本 Skill 原生模式。
- “绒宝/牙仔/阿龅/这个IP/带IP”或显式调用 `$rongbao-illustrations`，并与封面、竖版海报、方图或 1:1 同时出现：走组合模式。
- 普通封面、竖版海报和方图仍路由到已注册的 `dongfang-cover-design`；普通 3:4 信息图、萌粒和贴纸仍路由到 Everett 的 `ip-illustration-character-system`。
- 显式调用任一 `baoyu-*` Skill，或写“Baoyu/宝玉 + 文章配图、封面、信息图、知识漫画、漫画、小红书图片、图片卡片、幻灯片/slide deck”：优先路由到对应 Baoyu Skill。知识漫画、小红书图片和幻灯片是 Baoyu 独有能力；带角色/IP信号时注入已选角色，没有信号时只透传给上游。
- 显式调用 `personal-ip-image-pack`，或请求真人照片个人 IP、本人/博主卡通形象、照片转卡通、人物表情包/动作包/贴纸套图：路由到个人 IP 上游；上游负责读取用户提供的 1-3 张照片，不注入默认牙仔，不把临时原型自动写入角色注册表。动物、吉祥物、虚构角色和现有牙仔/绒宝/阿龅请求不触发这条隐式路由。
- 只有 `$dongfang-cover-design`、没有绒宝/牙仔/阿龅/IP 身份信号时：不注入任何角色参考图，不由本 adapter 组合；只有补充角色/IP 信号后才组合。
- 只有封面/海报/方图但没有角色身份要求：不要由本 Skill 擅自接管，等待用户明确目标设计 Skill 或补充角色身份要求。
- 角色选择遵循 `references/character-routing.md`：解析完整请求时先解析当前 Skill 根目录，再运行 `python -X utf8 <skill-root>/scripts/character_router.py --json "<request>"`；没有角色名或别名时默认 `yazai`，“这个IP/该IP”不会切换角色。只有用户明确说“使用/切换到/指定某某 IP”时才在该命令末尾加 `--explicit` 对未知名称返回支持列表；普通正文里的陌生名词不报未知 IP 错误。
- 同一请求出现两个或更多注册角色时选择全部角色；每个角色分别保留身份锚点并共同参与核心动作，不把其中一个降为装饰，也不把角色融合成一个混合形象。
- 组合冲突按“用户明确要求 > 目标设计 Skill 契约 > 已选角色身份锚点 > adapter 默认”处理。
- `create` 与 `prompt` 必须透传：前者执行目标 Skill 的生成，后者生成/检查目标提示词或路由计划；不要吞掉用户的画幅、材质、光线、文字、尺寸、输出路径等选项。
- 需要封面、海报、方图、萌粒、角色锚点、转面图、3:4 信息图、3:4 贴纸页，或 Baoyu 的文章配图、知识漫画、小红书图片、幻灯片时，先运行 `scripts/design_router.py --json`。普通文章配图仍走本 Skill 原生模式；目标 Skill 有角色/IP信号时进入 `upstream` 并注入已选角色，没有信号时进入 `direct-target` 但不注入任何角色图片。
- 直接调用 `$ip-illustration-character-system` 而没有绒宝/牙仔/阿龅、IP 或 `$rongbao-illustrations` 信号时，不注入任何角色参考图；只透传用户对上游 Skill 的直接请求。
- 任何实际生图或改图都必须使用真实角色图片输入：先运行路由器读取 `character_inputs`，再对每个 `asset_path` 调用 `view_image`，并把所有已选图片按注册表顺序放入图像工具的 `referenced_image_paths`。提示词要用 `prompt_label` 明确 Image 1/2/3 与显示名的映射，并声明每张图仅作对应角色身份参考；只写文字身份描述不算完成。
- 只做 `prompt`、shot list 或路由计划时不要无谓加载图片，但要把运行时解析出的 `asset_path` 和角色映射写入计划；静态文档写 `assets/<id>.webp`，运行时不得使用开发机硬编码路径。

## 先读这些参考

按任务需要读取，不要一次塞满上下文：

- `references/style-dna.md`：风格 DNA、颜色、文字、禁忌。
- `references/rongbao-ip.md`：绒宝 IP 的身份锚点、性格、动作库和禁忌。
- `references/rongbao-identity.md`：跨媒介身份协议；组合到其他设计 Skill 时必须读取。
- `references/character-routing.md`：角色名称解析、默认角色、并行多角色、未知名称处理和生图图片输入契约。
- `references/character-registry.json`：角色注册表；公开字段为 id、display_name、aliases、asset、identity_reference。
- `references/yazai-identity.md`：牙仔身份协议；只在选择牙仔时读取。
- `references/abao-identity.md`：阿龅身份协议；只在选择阿龅时读取。
- `references/composition-patterns.md`：结构类型、原创隐喻方法和反复刻规则。
- `references/prompt-template.md`：单张生图提示词模板、Image 1/2/3 参考图映射和 `referenced_image_paths` 契约。
- `references/qa-checklist.md`：生成后检查和迭代规则。
- `references/design-routing.md`：意图路由、create|prompt 透传、缺失依赖确认和扩展方式。
- `references/design-dependencies.json`：v1 设计依赖注册表；先解析当前 Skill 根目录，再运行 `<skill-root>/scripts/doctor.py --json` 只读检查可用性。
- `scripts/design_router.py`：原生、Dongfang、Everett、Baoyu、Guizang 与 gbro 能力路由、`create|prompt` 识别、目标相关模型门禁和有序图片输入装配。
- `scripts/dependency_utils.py`：依赖注册表校验、`install_name`/根路径解析、安装信息和只读位置探测。
- `scripts/register_character.py`：用户明确确认后，将批准的个人 IP 图像无损转换为 WebP，连同身份协议和名称安全写入角色注册表；冲突只有 `--update` 才可覆盖。
- `assets/rongbao.webp`：绒宝角色参考图；只读取身份特征，不复制其 3D 绒毛材质、米色背景或原始姿态。
- `assets/yazai.webp`：牙仔角色参考图；只在选择牙仔时读取身份特征，媒介由目标 Skill 决定。
- `assets/abao.webp`：阿龅角色参考图；只在选择阿龅时读取身份特征，媒介由目标 Skill 决定。
- `assets/xiaomei.webp`：小美角色参考图；只在选择小美时读取身份特征，媒介由目标 Skill 决定。
- `assets/examples/`：只作低频视觉校准，不进入默认生成路径。不要照抄这些案例的构图、物件或标注。

## 工作流

### 0. 先判定执行面

先按 `references/character-routing.md` 解析角色，再按 `references/design-routing.md` 识别身份信号和目标画幅/能力，决定原生或组合模式。需要可选上游能力时，再运行 `<skill-root>/scripts/design_router.py --json "<request>"`；解析后保留 `character_inputs` 的注册表顺序和绝对 `asset_path`。组合模式不要先套用正文模板；先解析当前 Skill 根目录，再运行 `<skill-root>/scripts/doctor.py --json` 检查角色注册表和目标 Skill 是否可用。缺失时只展示来源并请求一次确认，拒绝后不修改环境、不安装、不模拟目标能力。

如果本次是只规划 prompt/shot list，可只展示 `character_inputs` 中的路径而不加载图片；如果本次会生图或改图，必须先对每个已选 `asset_path` 调用 `view_image`，并将这些路径全部传给图像工具。

对于 Everett 路由，`design_router.py` 会按“角色参考图 → `style_ref_01` → `style_ref_02` →（未选牙仔时）`style_ref_03` →（仅 3:4 信息图）layout refs”装配路径，并要求明确确认 GPT Image 2。Dongfang 和 Baoyu 不套用这个模型门禁；Baoyu 各能力按其输入策略使用已选角色原图，通用/未知图像工具仍应遵循目标 Skill 的调用契约。

### 1. 消化正文

先读用户给的正文、链接、Notion 页面、Markdown 文件或截图内容。提炼：

- 核心观点是什么
- 哪些段落承担认知转折
- 哪些内容适合用图解释
- 哪些地方只适合文字，不需要图

不要平均配图。优先选择“认知锚点”，例如：核心判断、两个断点、输入输出闭环、分流、前后对比、一鱼多吃、承接路径、常见坑、角色状态变化。

### 2. 先出配图策略

如果用户只是说“分析怎么配图 / 思考哪些地方需要配图”，先给 shot list。每张图写清楚：

- 放在哪个段落后
- 图的主题
- 核心意思
- 结构类型
- 已选择角色在图里分别做什么
- 建议元素
- 建议中文标注词

默认 4-8 张。文章很短时 1-3 张；长文也不要轻易超过 9 张。够用就好，避免把正文做成画册。

### 3. 原生单张生成

如果用户明确要求“生成 / 输出 / 做图 / 帮我生成”，不要停下来等确认；用内置 `image_gen` 每张单独生成。不要把多张图拼在一张里。

每张图只讲一个核心结构。提示词必须包含：

- 16:9 横版中文正文配图
- 纯白背景
- 黑色手绘线稿
- 少量红色/橙色/蓝色中文手写批注
- 大量留白
- 已选择角色作为核心动作主体；未指定时为牙仔
- 先按角色注册表读取选中的角色参考图和身份协议：牙仔默认保留黑白拟人猫、黑色尖耳/头顶毛块、半眯竖瞳、宽扁脸、两颗门牙、胡须、长卷尾、白衬衫、黑马甲或黑领结和围裙；显式选择绒宝时保留黄色圆身、青绿色叶耳、棕黑大眼、橙色腮红和橙色手脚；阿龅遵循自己的黑白犬身份协议。实际生图时，按 `character_inputs` 将每张 `asset_path` 作为对应 `Image 1/2/3` 的 `referenced_image_paths`，并在提示词中声明“identity reference only”。画面必须转译为白底极简手绘，不得复制参考图的摄影棚 3D 材质、米色背景、渐变、阴影或商业吉祥物质感。多角色时每个角色都要参与核心动作，不能融合成混合角色。
- 禁止 PPT、商业插画、幼稚可爱、复杂架构、左上角类型标题

不要复刻过往案例。案例只提供风格密度和牙仔参与方式，不能直接复用“传送带断点 / 绒宝拉线 / 素材鱼 / 盖章工具箱 / 常见坑路径”等已有构图，除非用户明确要求复刻某张图。每次都要从当前文章重新发明一个奇怪但成立的隐喻。

### 4. 组合生成

如果组合请求使用 `create`，或用户明确要求生成图片，并触发组合路由：

- 读取 `character_inputs` 中每个选中角色的绝对 `asset_path`，先逐张 `view_image`，再把全部路径按顺序传给目标设计 Skill 的 `referenced_image_paths`；提示词用 `prompt_label` 标明 Image 与显示名映射，并声明每张图仅作身份参考。不能依赖文字描述、附加未选图片或使用开发机硬编码路径。
- 将用户指定的画幅、构图、材质、光线、文字、尺寸、输出路径和其他目标选项原样透传；最终输出服从目标 Skill 契约。
- 不复制 `dongfang-cover-design` 文件，不用本 Skill 的白底手绘提示词模拟封面、竖版海报或方图能力。

### 可选 IP Illustration Character System

注册表中的 `ip-illustration-character-system` 指向 [EverettFish/ip_illustration_for_yourself](https://github.com/EverettFish/ip_illustration_for_yourself)，默认不随本 Skill 打包。它提供 `character-anchor`、`turnaround-sheet`、`mini-article-illustration`、`article-infographic-3x4` 和 `sticker-sheet-3x4`。普通文章配图不因安装它而改变；有注册角色/IP信号时由 adapter 路由并注入已选角色；没有信号时能力词或直接上游调用仍交给上游，但不注入角色。

首次触发且 doctor 显示缺失时，只请求一次确认。确认后交给系统 `$skill-installer`，使用注册表里的完整参数：

```text
$skill-installer install --repo EverettFish/ip_illustration_for_yourself --path . --name ip-illustration-character-system --ref main
```

不要复制上游代码或图片，也不要安装到仓库或用户正式 Skill 目录之外的临时位置。若用户直接调用上游 Skill 且没有角色/IP信号，保持上游原生行为，不附加任何已注册 Rongbao IP 图片。

如果用户使用 `prompt`，只输出目标 Skill 可执行的提示词/路由计划，不在用户未要求时生图；保留 `create|prompt` 语义和全部选项。

### 可选 Baoyu Skills

注册表中的 6 个 Baoyu Skill 均来自 [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills)，固定使用 `main`，不随本 Skill 打包：`baoyu-article-illustrator`、`baoyu-comic`、`baoyu-cover-image`、`baoyu-infographic`、`baoyu-slide-deck` 和 `baoyu-xhs-images`。显式点名 Skill，或写“Baoyu/宝玉 + 能力”时优先选择对应目标；知识漫画、漫画、小红书图片、图片卡片和幻灯片/slide deck 在带 Rongbao IP 信号时也会自动组合。

实际生图时，Baoyu 目标只接收当前请求选中的原始角色图片：文章配图、封面和信息图将原图作为 direct reference；漫画把原图作为 primary character-setting reference，目标 Skill 生成的衍生角色表只能作为 secondary anchor，不能覆盖注册表原图；slide deck 把原图作为 deck identity reference，角色只出现在内容合适的页面；xhs-images 将所有选中角色原图按注册表顺序作为第一张生成的 direct references，第一张生成成品才作为后续链式生成的 anchor。每种策略都必须先 `view_image` 再传 `referenced_image_paths`，并在提示词中标注 Image 与角色映射。

Baoyu 没有 Everett 的 GPT Image 2 门禁；只保留目标 Skill 自己的生成契约。缺失时只请求一次确认，可按需一次安装一个或多个路径：

```text
$skill-installer install --repo JimLiu/baoyu-skills --path skills/baoyu-article-illustrator skills/baoyu-comic skills/baoyu-cover-image skills/baoyu-infographic skills/baoyu-slide-deck skills/baoyu-xhs-images --ref main
```

不要复制 Baoyu 源码或素材，也不要把可选依赖安装到仓库或临时目录；用户直接调用 Baoyu 且没有角色/IP信号时，保持上游行为，不附加任何已注册 Rongbao IP 图片。

依赖缺失时，按 `references/design-routing.md` 展示 `yang0/dongfang`、`dongfang-cover-design`、`main` 的来源和能力并请求一次确认。确认后交给系统 `$skill-installer` 从 GitHub 安装 repo `yang0/dongfang`、path `dongfang-cover-design`、ref `main`，告知下一轮 Codex 生命周期继续；拒绝则立即结束该组合路径。

### 可选 Guizang Social Card Skill

注册表中的 `guizang-social-card-skill` 指向 [op7418/guizang-social-card-skill](https://github.com/op7418/guizang-social-card-skill)，固定使用仓库根目录、`main` ref 和同名安装目录。它提供小红书图文组图（3:4）、瑞士风卡片、电子杂志风卡片、公众号 21:9 + 1:1 封面对和 Live Photo 动态卡。它不随本 Skill 打包，不复制上游源码、模板或素材；上游许可证以其仓库声明的 AGPL-3.0 为准。

显式写“归藏 / Guizang / 瑞士风社交卡 / 电子杂志社交卡 / 公众号封面对 / Live Photo”时，`design_router.py` 路由到对应能力。泛指“小红书图文 / 小红书图片”但未指定视觉系统时，路由器返回 `style_selection_required: true` 以及“归藏瑞士风、归藏电子杂志风、Baoyu 小红书图文”候选，不擅自抢占 Baoyu；明确写“宝玉 / Baoyu”仍路由 Baoyu。

组合请求带有角色/IP信号时，先解析 `character_router.py`，把所有选中角色的原始 `asset_path` 和 `identity_reference_path` 按注册表顺序传给归藏；原图优先，多个角色分别保持身份并共同参与内容表达，不能融合成混合角色。无角色/IP信号时保持归藏上游原生行为，不注入牙仔、绒宝或阿龅。

归藏缺失时只展示来源、能力和完整安装参数，并请求一次确认；确认后交给系统 `$skill-installer`：

```text
$skill-installer install --repo op7418/guizang-social-card-skill --path . --name guizang-social-card-skill --ref main
```

### 可选 GPT Image 2 Style Library 提示词增强层

注册表中的 `gpt-image-2-style-library` 指向 [freestylefly/awesome-gpt-image-2](https://github.com/freestylefly/awesome-gpt-image-2) 的 `agents/skills/gpt-image-2-style-library`，固定使用 `main`，上游声明 MIT。它是按需提示词增强层，不是独立版式 Skill，也不替换 Rongbao、Dongfang、Everett、Baoyu 或 Guizang 的基础目标。

只有用户明确写“GPT Image 2 风格库 / 模板库增强 / 按模板增强提示词”或点名 `gpt-image-2-style-library` 时，才在既有 `target_skill_id` 旁设置 `prompt_enhancer`。增强层输出模板名、风格/场景标签、案例 ID、结构化提示词和负面约束；目标 Skill 继续决定画幅、版式和交付路径，角色原图与身份协议继续控制牙仔、绒宝和阿龅的身份，不能被当作风格参考。

缺失时只展示来源、MIT 许可证、能力和安装参数，并请求一次确认：

```text
$skill-installer install --repo freestylefly/awesome-gpt-image-2 --path agents/skills/gpt-image-2-style-library --name gpt-image-2-style-library --ref main
```

使用 `create` 时，只有运行环境明确确认 GPT Image 2 才允许直接使用增强结果生图；否则交付完整增强 prompt package、角色身份协议路径和参考图顺序。普通请求没有显式增强信号时维持原有路由，不被模板库改写。

### 可选 gbro Cover Design 3:4 封面提示词 Skill

注册表中的 `gbro-cover-design` 指向 [pyang5166/gbro-cover-design](https://github.com/pyang5166/gbro-cover-design)，使用仓库根目录和 `main`，上游声明 MIT。它固定输出 3:4 竖版封面提示词，保留三轮提问流程、10 种构图模板、标题建议和安全区约束；它只产出提示词包，不直接调用图像模型，也不替换 Dongfang 或 Baoyu 的普通封面路由。

只有用户显式写出 `gbro`、`gbro-cover-design`、“gbro 封面”、“三轮提问封面”或“10 种构图风格封面”时才路由到它。普通“做一张封面”、横版封面和显式 Baoyu 封面继续交给原有目标 Skill。gbro 请求固定 3:4；用户明确要求 16:9、4:3 或 1:1 时，保留 gbro 的选择但返回画幅不兼容警告，建议改用 Dongfang/Baoyu，不静默裁切。

有牙仔、绒宝、阿龅、`这个IP`、`带IP` 或 `$rongbao-illustrations` 信号时，先运行角色路由器，将所有选中角色的原始 `asset_path` 按注册表顺序放在输入最前；每张图在提示词中标成对应 IP 的 `identity reference only`，明确不是上游所说的真人脸部参考，不改变五官、体型、服饰、身份色和尾巴等身份锚点。多角色分别保持身份并共同参与封面叙事，不能融合成一个角色。没有 Rongbao IP 信号时保持 gbro 的 `direct-target` 原生行为，不注入牙仔。

gbro 的执行结果始终是 `prompt-package`：`prompt` 和 `create` 都只交付完整提示词、标题建议、选定构图风格、空间关系、参考图映射和中文文字复核提醒；Rongbao 不替上游直接生图。实际生成若由用户自行执行，按 gbro 上游契约完整使用其 `references/`，不可只复制 `SKILL.md`。

缺失时只展示来源、MIT、能力和一次性安装确认；确认后交给系统 `$skill-installer`：

```text
$skill-installer install --repo pyang5166/gbro-cover-design --path . --name gbro-cover-design --ref main
```

doctor 会同时检查安装目录的 `SKILL.md` 与必需的 `references/`；本项目不复制 gbro 源码、模板、示例或素材。

### 可选 Personal IP Image Pack

注册表中的 `personal-ip-image-pack` 指向 [DoraRabbitYan/personal-ip-image-pack](https://github.com/DoraRabbitYan/personal-ip-image-pack)，使用仓库根目录和 `main`，上游当前未声明许可证。它适合“真人照片 → 个人卡通 IP → 表情包/动作包/贴纸套图”；普通动物 IP、品牌吉祥物、虚构角色和已注册 Rongbao 角色继续走原有路由。

只有显式点名 `personal-ip-image-pack`，或出现真人照片个人 IP、本人/博主卡通形象、照片转卡通、人物表情包/动作包等信号时才路由到它。用户照片由上游 Skill 读取；Rongbao 不把牙仔作为默认参考，也不把用户照片复制到本仓库。缺失时只展示一次来源、能力和完整根目录安装参数，并请求确认：

```text
$skill-installer install --repo DoraRabbitYan/personal-ip-image-pack --path . --name personal-ip-image-pack --ref main
```

完整安装必须保留 `SKILL.md`、`references/`、`assets/` 和 `scripts/`。上游完成的原型默认只是当前任务产物；只有用户明确说“加入 Rongbao / 设为正式 IP”，并提供中文 `display_name`、英文 `id`、中英文 `aliases` 和批准原型图（PNG/JPEG/WebP）后，才执行：

```text
python -X utf8 <skill-root>/scripts/register_character.py --confirm \
  --id <english-id> --display-name <中文名> \
  --alias <中文名> --alias <english-id> \
  --prototype <approved-prototype>
```

已有 id 或别名默认失败；只有再次明确授权并附 `--update` 才更新已有角色。注册后新角色才会像牙仔、绒宝和阿龅一样按名称解析，并作为目标设计 Skill 的身份参考图。

### 5. 原生检查与迭代

仅原生正文模式检查 `references/qa-checklist.md` 的白底手绘规则。如果出现以下问题，优先重生成或局部编辑：

- 任一已选角色只是装饰，或多个角色被融合为一个混合形象
- 画面太满
- 太像流程图/PPT
- 中文太多或错字严重
- 左上角出现“常见坑/流程图/系统架构图”等标题
- 画风太可爱、幼稚、死板
- 背景不是干净白底

### 6. 组合验收与迭代

仅组合模式使用目标设计 Skill 的 QA、输出路径和交付契约，不套用本 Skill 的白底、16:9、`assets/<article-slug>-illustrations/` 或 `qa-checklist.md` 默认值。

#### 身份检查

- 对每个选中角色逐一确认其身份协议锚点仍可辨识；绒宝检查黄色圆身、青绿色叶耳、大棕黑眼睛、橙色腮红和橙色手脚，牙仔检查黑白拟人猫、尖耳/头顶毛块、竖瞳、宽扁脸、门牙、胡须、卷尾及服饰锚点，阿龅检查黑白拟人犬、下垂黑耳、头顶毛、长口鼻/黑鼻头、门牙、犬尾及白衬衫和深色工装锚点。
- 绒宝身份色默认保持鲜亮黄、鲜亮青绿和鲜亮橙；只有环境或用户明确要求时才做局部变化。其他角色遵循各自身份协议的颜色约束。
- 禁止综合色偏、统一降饱和或复古做旧造成身份色漂移；如用户明确改变锚点，按用户要求记录该偏差。

#### 媒介检查

- 确认角色与场景共享目标媒介的材质、笔触、边缘、颗粒、环境光和投影。
- 排除参考图摄影棚 3D 绒毛、硬抠边缘、独立高光、抠图感或贴片感，不用全局滤镜伪装融合。

#### 一次定向修正

若媒介检查失败，只做一次针对角色媒介融合的定向迭代，锁定构图、标题、配色和身份锚点，只重绘角色媒介；不要重做目标设计 Skill 的整体画面。

### 7. 原生保存交付

仅原生正文模式且用户在 workspace 内工作时，把最终图复制到：

```text
assets/<article-slug>-illustrations/
```

按顺序命名：

```text
01-topic-name.webp
02-topic-name.webp
```

保留原始生成文件，不要覆盖已有资产，除非用户明确要求替换。

### 8. 组合保存交付

仅组合模式按目标设计 Skill 的输出路径、文件命名、格式、尺寸和交付说明执行；不要自动复制到 `assets/<article-slug>-illustrations/`，不要覆盖目标 Skill 的输出约定。

## 输出口径

### 原生模式

生成前的策略输出要短而准。生成后的交付要包含：

- 生成了几张
- 每张图的用途
- 保存路径
- 哪些图最稳，哪些图是可选

### 组合模式

组合请求的交付遵循目标设计 Skill 契约，说明实际使用的画幅/能力、目标输出路径和文件格式，并额外报告每个选中角色的身份锚点检查结果。不要输出原生正文模式的白底 QA 结论或默认保存路径，除非目标 Skill 自己要求。

不要长篇解释风格理论；让图自己说话。
