# Rongbao Illustrations / 绒宝配图

> 把中文文章里的判断、流程、状态和隐喻，变成一张张白底、手绘、怪诞但清爽的正文配图。
>
> 16:9 横版 | 绒宝 IP | 纯白手绘 | 少量红橙蓝中文批注 | Codex Skill

---

## 这个仓库是什么

Rongbao Illustrations 是一个 Codex Skill，用来指导 AI Agent 为中文文章、帖子、博客、Notion 文档和方法论内容生成正文配图，并在明确提出绒宝 IP 的封面、竖版海报或方图请求时，按需组合目标设计 Skill。

它不是通用插画 prompt，也不是 PPT 信息图模板。它的核心目标是：先理解文章里的认知锚点，再把其中一个判断、流程、结构、状态或隐喻，变成一张有记忆点的 16:9 手绘解释图。

默认视觉 IP 是“绒宝”：参考 `rongbao-illustrations/assets/rongbao.png` 的黄色圆形主体、青绿色叶耳、棕黑大眼、橙色腮红和橙色手脚，并转译成白底极简手绘角色。绒宝不是贴纸或站在角落里的装饰物，而是正在认真参与系统运转的荒诞工作者。

一句话：**让 AI 不只是“配一张图”，而是把文章里的一个关键认知动作画出来。**

---

## 适合谁用

特别适合：

- 写中文文章，需要正文配图和文章插图的人
- 做知识型内容、方法论内容、AI 工作流内容的人
- 想把抽象判断画成具体隐喻的人
- 想要一种比 PPT 信息图更轻、更怪、更有个人识别度的配图风格的人
- 用 Codex 做内容生产，希望稳定复用一套视觉语言的人

不适合：

- 想要商业插画、品牌 KV 或精致扁平插画的人
- 想要传统 PPT 信息图、复杂架构图或流程图的人
- 想要儿童卡通、可爱 IP、表情包风格的人
- 想把大量正文、长段解释或完整课程页塞进一张图里的人
- 需要严格可编辑矢量源文件的人

---

## 它会产出什么

默认输出：

- 16:9 横版正文配图
- 一篇文章的 4-8 张 shot list
- 每张图的主题、核心意思、结构类型、绒宝动作和中文标注建议
- 最终 PNG 图片，保存到 workspace 的 `assets/<article-slug>-illustrations/`

按需组合输出：

- 横版封面（`landscape-cover`）
- 竖版海报（`portrait-poster`）
- 方图（`square-graphic`）

组合输出的画幅、构图、材质、光线、文字、尺寸和保存方式由目标设计 Skill 决定。

原生模式默认不输出：

- PPTX / PDF / Keynote
- SVG / HTML / Canvas 可编辑图
- 商业海报或封面 KV
- 大段文字型信息图

---

## 视觉风格

这个 Skill 默认使用“绒宝怪诞正文配图”风格：

- 纯白背景，不要纸纹、米色、阴影、渐变
- 黑色手绘线稿，细线，轻微抖动
- 大量留白，主体只占画面约 40%-60%
- 少量红色、橙色、蓝色中文手写批注
- 一张图只表达一个核心动作、结构、状态或隐喻
- 绒宝必须参与核心动作，不能只是装饰
- 生成时读取 Skill 包内的 `assets/rongbao.png` 作为角色参考；只保留身份锚点，不复制参考图的 3D 绒毛、米色背景、渐变或阴影。
- 怪诞、有创意、清爽；友好灵动，但不幼儿化、不用可爱表情替代结构表达

以上是正文配图原生模式的默认值。跨到其他设计 Skill 时，绒宝只提供黄色圆身、青绿叶耳、大棕眼、橙色腮红和橙色四肢等身份锚点；目标 Skill 决定媒介表现。

组合图中角色要与场景共享媒介和光线，身份色默认保持鲜亮黄/青绿/橙；禁止综合色偏、统一降饱和或复古做旧伪装融合。若出现参考图材质残留或贴片感，只针对角色做一次融合迭代，保持构图、标题、配色和身份锚点不变。

---

## 跨设计 Skill 组合

这是一个轻量 adapter 架构，不依赖 `agent-reach`，也不复制目标 Skill 文件：

1. **意图路由**：识别“绒宝 / 这个IP / 带IP”或显式调用 `$rongbao-illustrations`，以及封面、竖版海报或方图画幅。
2. **身份协议**：从本 Skill 的 `rongbao-illustrations/assets/rongbao.png` 提供绒宝身份参考。
3. **目标设计 Skill**：根据注册表选择能力，负责画幅、构图、材质、光线、文字和输出。
4. **交付**：`create` 透传生成请求，`prompt` 透传提示词/路由计划；不把正文白底手绘默认强加给目标 Skill。

v1 注册表位于 [`rongbao-illustrations/references/design-dependencies.json`](rongbao-illustrations/references/design-dependencies.json)，当前登记：

`dongfang-cover-design` → `yang0/dongfang` 的 `dongfang-cover-design`（ref `main`），能力为 `landscape-cover`、`portrait-poster`、`square-graphic`。

### 按需安装依赖

首次触发组合路由时，Skill 会先运行只读 doctor 并展示来源；依赖缺失时只请求一次确认，不会自动改环境：

```text
来源：https://github.com/yang0/dongfang/tree/main/dongfang-cover-design
参数：repo `yang0/dongfang` / path `dongfang-cover-design` / ref `main`
是否使用系统 $skill-installer 从 GitHub 安装上述 repo/path/ref？
```

确认后交给系统 `$skill-installer` 安装上述 repo/path/ref，提示用户该 Skill 将按 Codex 生命周期在下一轮可用；拒绝则不安装、不修改环境，也不模仿目标设计能力。新增设计依赖时，只需在注册表添加 `skill_id`、`repo`、`path`、`ref` 和 `capabilities`，再补充对应的意图映射，不要复制目标 Skill 源码。

只读诊断命令：

```bash
python rongbao-illustrations/scripts/doctor.py --json
```

上面的命令从本仓库根目录执行；Skill 安装后，先解析当前 Skill 根目录，再运行 `<skill-root>/scripts/doctor.py --json`，不要假设当前 cwd 是 Skill 目录。

---

## 示例效果

### 两个断点

![两个断点](examples/images/01-two-breakpoints.png)

### 按目的分拣

![按目的分拣](examples/images/02-sort-by-purpose.png)

### 一鱼多吃

![一鱼多吃](examples/images/03-one-fish-many-uses.png)

### 承接路径

![承接路径](examples/images/04-handoff-path.png)

### 信息井

![信息井](examples/images/05-information-well.png)

### 想法压机

![想法压机](examples/images/06-idea-press.png)

### 内容发酵

![内容发酵](examples/images/07-content-fermentation.png)

### 信任桥

![信任桥](examples/images/08-trust-bridge.png)

这些图片是风格校准样例，不是构图模板。使用时应该从当前文章重新发明隐喻，不要照抄旧案例的物件和构图。

---

## 安装

克隆仓库：

```bash
git clone https://github.com/yang0/rongbao-illustrations.git
cd rongbao-illustrations
```

复制 skill 到 Codex skills 目录：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R ./rongbao-illustrations "${CODEX_HOME:-$HOME/.codex}/skills/"
```

安装后，在 Codex 里使用：

```text
Use $rongbao-illustrations 为这篇中文文章设计并生成 5 张绒宝怪诞正文配图。
```

---

## 怎么用

### 只做配图规划

```text
Use $rongbao-illustrations 先不要生图。
请分析下面这篇文章哪里值得配图，输出 5 张左右的 shot list。
每张图写清楚：放在哪段后、主题、核心意思、结构类型、绒宝在做什么、建议中文标注词。

<粘贴文章>
```

### 直接生成正文配图

```text
Use $rongbao-illustrations 把下面这篇文章生成 4 张绒宝怪诞正文配图。
要求：16:9 横版、纯白背景、黑色手绘线稿、少量红橙蓝中文手写批注。

<粘贴文章>
```

### 为单个概念生成一张图

```text
Use $rongbao-illustrations 为“信任不是喊出来的，而是一块证据一块证据铺过去”生成一张正文配图。
画面要怪诞但清爽，读取 `assets/rongbao.png` 作为绒宝角色参考，并让绒宝承担核心动作。
```

### 组合生成横版封面

```text
Use $rongbao-illustrations create 为这个绒宝 IP 做一张横版封面。
主题：把复杂观点变成一个可记忆的视觉入口。请把绒宝作为角色参考，画幅使用 landscape-cover。
```

显式调用 `$rongbao-illustrations` 与封面/海报/方图同时出现即可触发组合；单独调用 `$dongfang-cover-design` 且没有绒宝/IP 信号时，不会注入绒宝参考图。

### 组合生成竖版海报

```text
Use $rongbao-illustrations create 为这个 IP 做一张竖版海报。
主题：一条内容从想法到行动的转化。请保留绒宝身份锚点，画幅使用 portrait-poster。
```

### 组合生成方图

```text
Use $rongbao-illustrations prompt 为带绒宝 IP 的 1:1 方图设计一份提示词。
主题：信任由证据逐步累积。请保留绒宝身份锚点，画幅使用 square-graphic，不要直接生图。
```

### 去掉图里的标题或错误文字

```text
Use $rongbao-illustrations 帮我编辑这张图，去掉左上角的“流程图”标题，其他内容保持不变。
```

更多示例见 [examples/prompts.md](examples/prompts.md)。

---

## 工作流程

这个 skill 的流程是：

1. 读取文章、Markdown、Notion 内容、截图或用户给的主题
2. 判断是正文原生模式，还是“绒宝/IP + 封面/海报/方图”的组合模式
3. 提炼核心观点、认知转折、流程结构和适合视觉化的段落
4. 先输出 shot list：每张图只选一个认知锚点
5. 为每张图选择结构类型：Workflow、系统局部、前后对比、角色状态、概念隐喻、方法分层、地图路线或小漫画分镜
6. 重新发明一个低科技、怪诞但成立的物理隐喻
7. 让绒宝承担核心动作，或将 `assets/rongbao.png` 作为角色参考传给目标设计 Skill
8. 每张图单独调用图像模型生成；组合请求服从目标 Skill 的输出契约
9. 按 QA checklist 检查原生正文图；组合图按目标 Skill 的检查标准验收
10. 原生模式保存到 `assets/<article-slug>-illustrations/`；组合模式遵循目标设计 Skill 的输出路径、格式和交付契约

---

## 目录结构

```text
.
├── README.md
├── LICENSE
├── NOTICE.md
├── assets/
│   └── rongbao.png
├── examples/
│   ├── images/
│   │   ├── 01-two-breakpoints.png
│   │   ├── 02-sort-by-purpose.png
│   │   └── ...
│   └── prompts.md
└── rongbao-illustrations/
    ├── SKILL.md
    ├── agents/
    │   └── openai.yaml
    ├── assets/
    │   ├── rongbao.png
    │   └── examples/
    ├── references/
        ├── style-dna.md
        ├── rongbao-ip.md
        ├── rongbao-identity.md
        ├── composition-patterns.md
        ├── prompt-template.md
        ├── qa-checklist.md
        ├── design-routing.md
        └── design-dependencies.json
    └── scripts/
        └── doctor.py
```

真正需要安装到 Codex 的是子目录：

```text
rongbao-illustrations/
```

根目录的 README、LICENSE、NOTICE 和 examples 是 GitHub 分享文档。

为兼容已有安装和调用，Skill id、安装目录和 `$rongbao-illustrations` 调用方式保持不变；本仓库使用独立的 `rongbao-illustrations` GitHub 地址，用户可见的角色名称和内容统一使用“绒宝”。

---

## 注意事项

- 图片里的中文文字越短越稳定。
- 每张图只讲一个核心结构，不要把文章做成说明书。
- 绒宝必须承担核心动作；如果去掉绒宝画面仍然完全成立，说明绒宝太装饰了。
- 示例图只用于校准线条密度、留白、颜色克制和绒宝参与方式，不要复刻构图。
- AI 图像模型可能出现错字、幻觉标签、风格漂移或多余标题，生成后需要检查。
- 如果中文错字严重，优先减少标注词并重生成。

---

## 上游来源

本项目由 yang0 独立维护。维护者 X / Twitter：[https://x.com/yang02010](https://x.com/yang02010)。绒宝角色设计源自上游项目作者创作的“小黑”IP，本项目在这一视觉基础上进行独立改编，并保留原有 Skill id、安装目录和调用方式以兼容既有使用习惯。感谢上游项目作者的创作与原始项目基础。

- 上游仓库：[上游仓库](https://github.com/helloianneo/ian-xiaohei-illustrations)

---

## License

MIT License. See [LICENSE](LICENSE).
