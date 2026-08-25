# 绒宝跨设计 Skill 组合路由

## 路由边界

本 Skill 有两个互不混淆的执行面：

| 用户意图 | 执行方式 |
| --- | --- |
| 中文文章、帖子或方法论正文配图；或明确要求 16:9 正文插图 | 本 Skill 原生模式，使用白底极简手绘规则 |
| 普通横版封面、竖版海报或方图，没有 Baoyu 显式要求 | 路由到现有 `dongfang-cover-design`；无 Rongbao IP 信号时为 `direct-target`，不注入角色 |
| 同时提到“绒宝”“牙仔”“阿龅”或其别名、“这个IP”“该IP”“带IP”等身份信号，或显式调用 `$rongbao-illustrations`，以及封面、封面 KV、竖版海报、portrait poster、方图、正方形或 1:1 | 组合路由到已注册的目标设计 Skill |
| `$rongbao-illustrations`/角色/IP 信号 + 萌粒、角色锚点、转面、3:4 信息图或 3:4 贴纸页 | 组合路由到可选 `ip-illustration-character-system` |
| 只有萌粒、角色锚点、转面、3:4 信息图或 3:4 贴纸页，没有角色/IP 信号 | 生成 `ip-illustration-character-system` 的 `direct-target` 计划，不注入 Rongbao 图片 |
| 显式调用 `baoyu-*`，或“Baoyu/宝玉 + 文章配图、封面、信息图、知识漫画、漫画、小红书图片、图片卡片、幻灯片/slide deck” | 优先路由到对应 Baoyu Skill；有 Rongbao IP 信号时注入已选角色，否则为 `direct-target` |
| 显式调用 `guizang-social-card-skill`、写“归藏”、瑞士风社交卡、电子杂志社交卡、公众号封面对或 Live Photo | 路由到 `guizang-social-card-skill` 的对应能力；有 Rongbao IP 信号时注入已选角色，否则为 `direct-target` |
| 显式调用 `gbro`、`gbro-cover-design`、写“gbro 封面”“三轮提问封面”或“10 种构图风格封面” | 路由到 `gbro-cover-design` / `cover-prompt-3x4`；有 Rongbao IP 信号时注入已选角色，否则为 `direct-target`；始终只输出 3:4 提示词包 |
| 泛指小红书图文/图片但未选择视觉系统 | 返回 `style_selection_required: true`，候选为归藏瑞士风、归藏电子杂志风和 Baoyu `xhs-images`；不自动抢占任一目标 |
| 只有知识漫画、漫画、小红书图片、图片卡片或幻灯片/slide deck，没有 Rongbao IP 信号 | 路由到对应 Baoyu Skill 的 `direct-target`，不注入 Rongbao 图片 |
| 只有 `$dongfang-cover-design`，但没有绒宝/牙仔/阿龅/IP 身份信号 | 仅执行用户明确点名的目标 Skill，不注入任何角色参考图，不由本 adapter 组合 |
| 只有 `$ip-illustration-character-system`，但没有绒宝/牙仔/阿龅/IP 身份信号 | 允许用户直接使用上游 Skill，但不注入任何角色参考图 |
| 只有封面/海报/方图，但没有角色或 IP 身份信号 | 不由本 Skill 擅自接管；请用户明确目标设计 Skill 或补充角色身份要求 |

“绒宝”“牙仔”“阿龅”或其别名、“这个IP”或“带IP”等身份信号、显式调用 `$rongbao-illustrations`，以及目标画幅信号，是组合路由的触发条件：显式调用 `$rongbao-illustrations` 时，与封面/海报/方图同时出现即可组合；没有任何角色/IP 信号时，单独的 `$dongfang-cover-design` 不得注入角色参考图。用户明确点名目标 Skill 时，尊重该明确调用。

角色先按 [character-routing.md](character-routing.md) 解析：无角色名或只有“这个IP/该IP”时默认 `yazai`；出现任意两个或三个注册别名时选择对应的全部角色；明确未知名称返回支持列表，不猜测替代角色。

## 画幅到能力的映射

- 横版封面、封面 KV、landscape cover → `landscape-cover`
- 竖版海报、竖版封面、portrait poster → `portrait-poster`
- 方图、正方形、1:1 graphic、square graphic → `square-graphic`
- 萌粒、mini pen-doodle → `mini-article-illustration`
- 角色锚点、character anchor → `character-anchor`
- 转面图、turnaround sheet → `turnaround-sheet`
- 3:4 信息图、知识卡片 → `article-infographic-3x4`
- 3:4 贴纸页、异形贴纸、sticker sheet → `sticker-sheet-3x4`
- 文章配图、正文插图、article illustration → `baoyu-article-illustrator`（仅显式 Baoyu/宝玉 或 Skill id）
- 知识漫画、漫画、comic → `baoyu-comic`
- 小红书图片、图片卡片、xhs images → `baoyu-xhs-images`
- 归藏小红书图文组图 → `guizang-social-card-skill` / `xhs-social-cards`
- 归藏瑞士风社交卡 → `guizang-social-card-skill` / `swiss-social-card`
- 归藏电子杂志社交卡 → `guizang-social-card-skill` / `editorial-social-card`
- 归藏公众号 21:9 + 1:1 封面对 → `guizang-social-card-skill` / `wechat-cover-pair`
- 归藏 Live Photo 动态卡 → `guizang-social-card-skill` / `live-photo-card`
- gbro 三轮提问封面、10 种构图风格封面 → `gbro-cover-design` / `cover-prompt-3x4`
- gbro 的 3:4 固定画幅、10 种模板和三轮提问 → `ten-layout-styles` / `three-round-briefing` / `character-reference-prompt`
- 幻灯片、slide deck、演示文稿 → `baoyu-slide-deck`
- Baoyu 封面、Baoyu 信息图 → `baoyu-cover-image` / `baoyu-infographic`

目标能力必须出现在 [design-dependencies.json](design-dependencies.json) 的注册表中。注册表是声明性数据，不是目标 Skill 的副本。

## create / prompt 透传

- `create` 表示执行生成：原样透传用户的画幅、材质、光线、文字、尺寸、输出路径和目标 Skill 选项。
- `prompt` 表示生成或检查提示词/路由计划：保留目标 Skill 的提示词契约，不在用户未要求时生图。
- adapter 不吞掉、改写或替换 `create` / `prompt`；只在组合调用中附加角色注册表为每个选中角色声明的包内相对 `asset` 和 `identity_reference`。实际生图/改图时，先用 `character_router.py --json` 取得当前 Skill 根目录解析出的 `character_inputs[*].asset_path`，逐张 `view_image` 后，按注册表顺序全部放入目标设计 Skill 的 `referenced_image_paths`，并在提示词中标出 Image 与显示名映射；不能只靠文字描述或写死开发机绝对路径。
- 需要上游能力时，运行 `scripts/design_router.py --json "<request>"`；它会保留 `create|prompt` 语义，输出 `target_skill_id`、`target_capability`、`dependency.status`、`reference_inputs` 和同序 `referenced_image_paths`。能力词或显式上游名称即使没有角色/IP信号，也会输出 `direct-target` 计划；只有有角色/IP信号时才进入带角色输入的 `upstream` 模式。实际生图/改图还必须对每条 `reference_inputs` 调用 `view_image`，再把同一顺序的路径传给目标工具。
- Baoyu 的 `reference_policy` 决定原图输入策略：`direct-character` 用于文章配图、封面和信息图；`comic-character-sheet` 保证注册原图优先、衍生角色表仅作 secondary anchor；`deck-identity` 允许角色只出现在内容合适的页面；`xhs-chain-anchor` 将所有选中角色原图作为第一张生成的 direct references，并将第一张生成成品作为后续链式 anchor。Baoyu 不使用 Everett 的 GPT Image 2 门禁。
- 归藏使用 `social-card-character`：所有选中角色的原始 `asset_path` 位于全部输入最前，并保留对应 `identity_reference_path`；风格、版式、平台画幅和 Live Photo 处理服从归藏上游。角色应出现在封面及至少一个承担内容表达的页面，纯截图或数据页可不强制放入角色。

### GPT Image 2 风格库增强层

只有请求明确点名 `gpt-image-2-style-library`、GPT Image 2 风格库或“模板库增强提示词”时，才在现有目标旁设置 `prompt_enhancer`；普通请求不会触发。增强层只提供 `template_name`、`style_tags`、`scene_tags`、`case_ids`、`structured_prompt` 和 `negative_constraints`，不改变 `target_skill_id`、画幅、版式、角色身份或参考图顺序。角色原图始终是身份输入，不得作为风格参考。

缺失依赖时使用：

```text
$skill-installer install --repo freestylefly/awesome-gpt-image-2 --path agents/skills/gpt-image-2-style-library --name gpt-image-2-style-library --ref main
```

该上游要求 GPT Image 2 才可将增强结果直接用于 `create`；模型未明确确认时只交付完整 prompt package、角色协议路径和同序参考图路径。

### gbro 3:4 封面提示词

只有显式出现 `gbro`、`gbro-cover-design`、“gbro 封面”、“三轮提问封面”或“10 种构图风格封面”时，才选择 `gbro-cover-design`；普通封面保持 Dongfang/Baoyu 路由。gbro 固定 3:4 竖版，目标 Skill 保留三轮提问、10 种构图模板、标题建议、空间关系和安全区定义，Rongbao adapter 不把它当作图像生成器。

组合模式的角色输入固定为：已选角色原始 `asset_path` →（无额外风格图）目标 Skill 的身份提示词。角色图在提示词中标为每个 IP 的 `identity reference only`，不是 gbro 上游所说的真人脸部参考；不得改变角色五官、体型、服饰、身份色或尾巴等锚点，多角色必须分别保持身份并共同参与封面叙事。没有角色/IP信号时不注入默认牙仔。

`prompt` 和 `create` 对 gbro 都返回完整 `prompt-package`，不直接生图。用户明确要求 16:9、4:3 或 1:1 时，返回固定 3:4 的不兼容警告并建议切换 Dongfang/Baoyu，不静默裁切。上游 `references/` 是必需运行资源，doctor 会把缺少它的安装判为 invalid。

## 组合执行

1. 识别身份信号和目标画幅，选出一个注册能力。
2. 先解析当前 Skill 根目录，再运行 `<skill-root>/scripts/doctor.py --json`，确认目标 Skill 是否可用；不要假设当前 cwd 是 Skill 目录。
3. 目标 Skill 可用时，使用 `character_inputs` 中每个选中角色的绝对 `asset_path`；实际生图/改图前逐张 `view_image`，再按 `input_order` 将所有路径传入目标 Skill 的 `referenced_image_paths`，并用 `prompt_label` 标记 Image 1/2/3 与显示名。只做 `prompt`/路由计划时不加载图片，但展示这些路径。多角色时只传选中的图片，分别保持身份且共同参与核心动作，不能将它们融合为一个混合角色。最终画幅、构图、材质、光线、文字和输出服从目标 Skill，且每个角色与场景共享媒介、笔触、边缘、颗粒、环境光和投影逻辑。
4. 不在本仓库复制、改写或模拟 `dongfang-cover-design` 的文件和能力。

可选上游的输入顺序固定为：已选角色参考图 → `style_ref_01` → `style_ref_02` → 仅在未选牙仔时的 `style_ref_03` → 仅在 `article-infographic-3x4` 时的 layout refs。风格参考只约束笔触、构图和线面关系，不覆盖角色身份；原始注册资产仍是身份主锚点，不能被衍生锚点覆盖。

Everett 可选上游要求 GPT Image 2。只有运行时明确确认 GPT Image 2 才允许直接生成；通用或未知图像工具必须停止在 prompt package，并附官方链接：

- [GPT Image 2 model](https://developers.openai.com/api/docs/models/gpt-image-2)
- [Image generation API guide](https://developers.openai.com/api/docs/guides/image-generation)

## 组合验收与定向修正

### 身份检查

- 对每个选中角色逐一核对其 `identity_reference`：绒宝的黄色圆身、青绿色叶耳、大棕黑眼睛、橙色腮红和橙色手脚，牙仔的黑白拟人猫、尖耳/头顶毛块、竖瞳、宽扁脸、门牙、胡须、卷尾和服饰锚点，以及阿龅的黑白拟人犬、下垂黑耳、头顶毛、长口鼻/黑鼻头、门牙和白衬衫加深色工装锚点都应可辨识。
- 绒宝身份色默认保持鲜亮黄、鲜亮青绿和鲜亮橙；只有环境或用户明确要求时才做局部变化。其他角色遵循各自身份协议的颜色约束。
- 不接受综合色偏、统一降饱和或复古做旧造成的身份色漂移。

### 媒介检查

- 每个角色与场景共享目标媒介的材质、笔触、边缘、颗粒、环境光和投影；多角色之间仍保持各自身份，不出现混合脸型、耳朵、服装或配色。
- 不残留参考图的摄影棚 3D 绒毛、硬抠边缘、独立高光、抠图感或贴片感。
- 媒介融合应通过角色重绘适配目标媒介完成，不用全局滤镜伪装统一。

### 一次定向修正

如果媒介检查失败，只做一次针对角色媒介融合的定向迭代，锁定构图、标题、配色和所有已选角色的身份锚点，只重绘角色媒介；不要借此重做目标设计 Skill 的整体画面。

## 缺失依赖

目标 Skill 缺失时，只展示一次来源、能力和安装参数，并请求一次确认。`dongfang-cover-design` 仍按原有路径注册；可选上游使用以下信息：

```text
缺少组合依赖：dongfang-cover-design
来源：https://github.com/yang0/dongfang/tree/main/dongfang-cover-design
参数：repo `yang0/dongfang` / path `dongfang-cover-design` / ref `main`
能力：landscape-cover / portrait-poster / square-graphic
是否使用系统 $skill-installer 从 GitHub 安装上述 repo/path/ref？
```

用户确认后，交给系统 `$skill-installer` 执行 GitHub 安装（repo `yang0/dongfang`，path `dongfang-cover-design`，ref `main`），不要自行实现下载器或修改安装环境；告知用户该 Skill 按 Codex 生命周期在下一轮可用，下一轮再继续组合请求。用户拒绝时立即停止，不安装、不修改环境，也不模仿目标 Skill 的封面/海报/方图能力。

```text
缺少组合依赖：ip-illustration-character-system
来源：https://github.com/EverettFish/ip_illustration_for_yourself
参数：repo `EverettFish/ip_illustration_for_yourself` / path `.` / name `ip-illustration-character-system` / ref `main`
能力：character-anchor / turnaround-sheet / mini-article-illustration / article-infographic-3x4 / sticker-sheet-3x4
是否使用系统 $skill-installer 从 GitHub 安装上述 repo/path/ref/name？
```

确认后交给系统 `$skill-installer` 使用：

```text
$skill-installer install --repo EverettFish/ip_illustration_for_yourself --path . --name ip-illustration-character-system --ref main
```

该上游依赖不随本仓库打包，不复制其代码或图片；上游仓库未在本项目声明额外许可证。用户拒绝时不安装、不修改环境、不伪造上游能力。可选依赖缺失属于正常状态，doctor strict 不因此失败；但存在错误 Skill id 或其他 invalid 状态仍应失败。

Baoyu 可选依赖缺失时只展示一次来源、能力和选中的路径，并请求一次确认。6 个注册项均来自 [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills)，使用 `main`，仓库声明 MIT；不要将其源码或素材复制到本项目。需要多个 Baoyu Skill 时，使用系统 installer 的多路径参数一次安装：

```text
来源：https://github.com/JimLiu/baoyu-skills
选中路径：skills/baoyu-article-illustrator、skills/baoyu-comic、skills/baoyu-cover-image、skills/baoyu-infographic、skills/baoyu-slide-deck、skills/baoyu-xhs-images
能力：article-illustration / comic / cover-image / infographic / slide-deck / xhs-images
是否使用系统 $skill-installer 安装选中的 Baoyu Skill？
```

确认后交给系统 `$skill-installer`：

```text
$skill-installer install --repo JimLiu/baoyu-skills --path skills/baoyu-article-illustrator skills/baoyu-comic skills/baoyu-cover-image skills/baoyu-infographic skills/baoyu-slide-deck skills/baoyu-xhs-images --ref main
```

如果只需要一个能力，只传对应的一个 `--path`；不要自行下载、复制或修改安装目录。用户直接调用 Baoyu 且没有 Rongbao IP 信号时保持上游原生行为，不附加角色参考图。

归藏可选依赖缺失时只展示一次来源、能力和安装参数，并请求一次确认：

```text
缺少组合依赖：guizang-social-card-skill
来源：https://github.com/op7418/guizang-social-card-skill
参数：repo `op7418/guizang-social-card-skill` / path `.` / name `guizang-social-card-skill` / ref `main`
能力：xhs-social-cards / swiss-social-card / editorial-social-card / wechat-cover-pair / live-photo-card
许可证：AGPL-3.0（以上游仓库声明为准）
是否使用系统 $skill-installer 从 GitHub 安装上述依赖？
```

确认后交给系统 `$skill-installer`：

```text
$skill-installer install --repo op7418/guizang-social-card-skill --path . --name guizang-social-card-skill --ref main
```

不要复制上游源码、模板或素材。用户拒绝时不安装、不修改环境，也不模拟归藏的版式能力。

gbro 可选依赖缺失时只展示一次来源、MIT、固定画幅和完整仓库安装参数，并请求一次确认：

```text
缺少组合依赖：gbro-cover-design
来源：https://github.com/pyang5166/gbro-cover-design
参数：repo `pyang5166/gbro-cover-design` / path `.` / name `gbro-cover-design` / ref `main`
能力：cover-prompt-3x4 / ten-layout-styles / three-round-briefing / character-reference-prompt
输出：prompt-only，固定 3:4 竖版；完整仓库必须包含 `references/`
许可证：MIT（以上游仓库声明为准）
是否使用系统 $skill-installer 从 GitHub 安装上述依赖？
```

确认后交给系统 `$skill-installer`：

```text
$skill-installer install --repo pyang5166/gbro-cover-design --path . --name gbro-cover-design --ref main
```

不要复制 gbro 的源码、`references/`、模板、示例或素材；用户拒绝时不安装、不修改环境，也不把 Rongbao 的原生正文规则伪装成 gbro 封面提示词。

## 扩展注册

新增目标设计 Skill 时，只需在注册表增加 `skill_id`、可选 `install_name`、GitHub `repo`、Skill `path`、Git ref `ref`、`optional`、`reference_policy` 和 `capabilities`，并在本文件增加明确的身份信号与能力映射。需要 GPT Image 2 的目标才声明 `requires_gpt_image_2: true`；若上游要求额外目录（如 gbro 的 `references/`），声明 `required_paths`，doctor 会将缺少目录的安装判为 invalid；根路径用 `path: "."`，doctor 与安装信息会保留仓库根位置，不生成 `/.`。不要把目标 Skill 的源码或图片复制到本仓库。
