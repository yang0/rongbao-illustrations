# Prompt Examples

下面这些 prompt 可以直接复制到 Codex 里使用。

## 只做配图规划

```text
Use $rongbao-illustrations 先不要生图。
请分析下面这篇文章哪里值得配图，输出 5 张左右的 shot list。
每张图写清楚：
- 放在哪个段落后
- 图的主题
- 核心意思
- 结构类型
- 已选角色在图里做什么
- 建议元素
- 建议中文标注词

<粘贴文章>
```

## 文章正文配图

```text
Use $rongbao-illustrations 把下面这篇文章生成 4 张牙仔黑白怪诞正文配图。
要求：16:9 横版、纯白背景、黑色手绘线稿、少量红橙蓝中文手写批注。
每张图只讲一个核心结构，不要做 PPT 信息图，不要可爱卡通。

<粘贴文章>
```

## 长文配图策略

```text
Use $rongbao-illustrations 给这篇长文做配图策略。
不要平均配图，只挑认知锚点：核心判断、输入输出闭环、前后对比、常见坑、承接路径。
默认 6-8 张，先输出 shot list，不要生成图片。

<粘贴文章>
```

## 单个观点生成一张图

```text
Use $rongbao-illustrations 为这个观点生成一张 16:9 正文配图：

信任不是喊出来的，而是一块证据一块证据铺过去。

画面要怪诞但清爽；未指定角色时使用牙仔，读取 `assets/yazai.png` 和 `references/yazai-identity.md` 作为身份参考，并让牙仔承担核心动作。
中文标注最多 5 个，短一点。
```

## 按名称选择角色

没有写角色名时默认使用牙仔；“这个IP / 该IP”也不会切换默认角色。可显式写绒宝、牙仔或阿龅，也可同时写任意多个角色；英文别名不区分大小写。

```text
Use $rongbao-illustrations 为“证据如何累积”生成一张 16:9 正文配图。
请使用牙仔（YAZAI）作为核心动作角色，保留黑白拟人猫身份锚点，不复制参考图材质。
```

```text
Use $rongbao-illustrations 为这个主题生成一张正文配图。
请让绒宝和牙仔一起完成核心动作，分别保持各自身份，不要把其中一个画成背景装饰。
```

```text
Use $rongbao-illustrations 为这个主题生成一张正文配图。
请使用阿龅（abao）作为核心动作角色，读取 `assets/abao.png` 与 `references/abao-identity.md`，保留黑白拟人犬、下垂黑耳、长口鼻和深色工装身份，不复制参考图材质。
```

也可以直接写：`用阿龅为这篇文章生成正文配图`。

```text
Use $rongbao-illustrations 为这个主题生成一张方图。
请让绒宝、牙仔和阿龅共同完成核心动作，分别保持三个角色的身份，不要把任何一个角色画成背景装饰或混合角色。
```

明确写出未注册的 IP 名称时，Skill 会返回支持列表（绒宝、牙仔、阿龅），不会猜测替代角色。

## 生图时附加角色参考图

实际生成或编辑图片时，先解析当前 Skill 根目录下的注册表：

```bash
python -X utf8 rongbao-illustrations/scripts/character_router.py --json "用牙仔和阿龅设计一张横版封面"
```

读取 JSON 的 `character_inputs`，对其中每个 `asset_path` 调用 `view_image`，再按 `input_order` 将全部路径传入图像工具的 `referenced_image_paths`。提示词明确写出：`Image 1 — 牙仔：identity reference only`、`Image 2 — 阿龅：identity reference only`。只做规划或 prompt 时不必加载图片，但要把返回的绝对路径与角色映射列在计划中；不要依赖文字描述、附加未选角色，或写死开发机路径。

## 工作流主题

```text
Use $rongbao-illustrations 为“把一条原始素材加工成流量、信任、转化三种内容”生成一张图。
不要画正式流程图，不要复刻一鱼多吃旧案例。
请重新发明一个新的低科技隐喻，让已选角色参与核心动作。
```

## 改图：去掉标题

```text
Use $rongbao-illustrations 帮我编辑这张图。
去掉左上角的“Workflow / 流程图”标题和下划线，其他内容保持不变。
不要新增任何文字或物件。
```

## 改图：增强角色参与感

```text
Use $rongbao-illustrations 这张图方向对，但角色有点像装饰。
请保持核心意思不变，重生成一版：让已选角色成为真正推动结构运转的人。
画面更怪一点，但仍然纯白、清爽、少字。
```

## 生成一组风格样片

```text
Use $rongbao-illustrations 输出 5 个不同主题的牙仔黑白正文配图效果。
主题分别覆盖：信息过载、产品验证、内容复利、一人公司、信任建立。
每张单独生成，不要拼成一张。
```

## 跨设计 Skill 组合

当请求同时包含角色/IP信号和目标画幅时，`$rongbao-illustrations` 只负责意图路由与已选角色身份参考，目标设计 Skill 负责画幅、构图、材质、光线、文字和输出。组合请求会保留 `create|prompt` 语义，并将注册表中每个选中角色的参考图传递；角色要与场景共享媒介和光线，绒宝身份色默认鲜亮，牙仔与阿龅遵循各自黑白协议，禁止综合色偏/统一降饱和/复古做旧；贴片感只做一次角色融合迭代；多个角色要分别保持身份并共同参与核心动作，不得融合；正文配图仍走本 Skill 原生白底手绘模式。

### 可选萌粒/角色锚点/信息图能力

以下请求带有绒宝、牙仔、阿龅、IP 或 `$rongbao-illustrations` 信号时，由 adapter 路由到可选的 `ip-illustration-character-system` 并注入已选角色；没有这些信号时，能力词或显式上游调用也只生成 `direct-target` 计划，不注入角色图片：

```text
Use $rongbao-illustrations create 用牙仔做一张萌粒风格的 mini 文章配图。
```

```text
Use $rongbao-illustrations prompt 用绒宝和阿龅做一套 3:4 信息图。
```

```text
Use $rongbao-illustrations create 用阿龅做一套 3:4 主题贴纸页。
```

直接调用 `$ip-illustration-character-system` 但不点名 Rongbao IP 时，路由为 `direct-target`，不注入绒宝、牙仔或阿龅图片。普通“生成文章配图”也保持本 Skill 原生白底手绘模式。

路由命令：

```bash
python -X utf8 rongbao-illustrations/scripts/design_router.py --json 'Use $rongbao-illustrations prompt 用牙仔做一张 3:4 信息图'
```

实际生图/改图时，按 JSON 的 `reference_inputs` 顺序逐张 `view_image`，再把同序路径传入 `referenced_image_paths`。只有 Everett 上游要求明确确认 GPT Image 2；未确认时交付 prompt package，不静默使用通用图像工具。

### Baoyu 可选组合

显式调用 Baoyu Skill，或写“Baoyu/宝玉 + 能力”时，优先路由到对应上游：

```text
Use $rongbao-illustrations create 用牙仔做一套知识漫画。
请把牙仔原图作为 Image 1 的角色设定参考；若上游生成角色表，只能作为二级锚点，不能覆盖注册原图。
```

```text
Use $rongbao-illustrations create 用绒宝和阿龅做一套小红书图片卡片。
将两张选中角色原图按注册表顺序作为第 1 张生成的 direct references；第 1 张生成成品才是后续链式图片的 anchor，不带入未选角色。
```

```text
Use $baoyu-slide-deck create 用绒宝做一套幻灯片。
绒宝可以只出现在内容合适的页面，但出现时必须保持原图身份；不要强迫每页出现角色。
```

Baoyu 直接调用但没有绒宝、牙仔、阿龅、IP 或 `$rongbao-illustrations` 信号时，返回 `direct-target`，不注入角色图片；Baoyu 不套用 Everett 的 GPT Image 2 门禁。

### 横版封面

```text
Use $rongbao-illustrations create 为这个绒宝 IP 做一张横版封面。
主题：把复杂观点变成一个可记忆的视觉入口。能力：landscape-cover。
```

```text
Use $rongbao-illustrations create 为阿龅（abao）IP 做一张横版封面。
主题：把复杂观点变成一个可记忆的视觉入口。能力：landscape-cover。读取阿龅参考图并保持其黑白拟人犬身份。
```

英文别名示例：`Use $rongbao-illustrations create 用 yazai 做一张横版封面。`

### 竖版海报

```text
Use $rongbao-illustrations create 为这个 IP 做一张竖版海报。
主题：一条内容从想法到行动的转化。能力：portrait-poster。
未指定其他角色时，使用默认牙仔黑白身份协议。
```

### 方图

```text
Use $rongbao-illustrations prompt 为带绒宝 IP 的 1:1 方图设计一份提示词。
主题：信任由证据逐步累积。能力：square-graphic。不要直接生图。
```

多角色方图示例：`用绒宝和牙仔设计一张方图`。

### 依赖缺失时

首次使用组合能力时，先解析当前 Skill 根目录，再运行 `<skill-root>/scripts/doctor.py --json`；不要假设当前 cwd 是 Skill 目录。若目标 Skill 缺失，展示来源并只请求一次确认：

```text
来源：https://github.com/yang0/dongfang/tree/main/dongfang-cover-design
参数：repo `yang0/dongfang` / path `dongfang-cover-design` / ref `main`
是否使用系统 $skill-installer 从 GitHub 安装上述 repo/path/ref？
```

可选 IP Illustration 依赖缺失时：

```text
来源：https://github.com/EverettFish/ip_illustration_for_yourself
参数：repo `EverettFish/ip_illustration_for_yourself` / path `.` / name `ip-illustration-character-system` / ref `main`
能力：character-anchor / turnaround-sheet / mini-article-illustration / article-infographic-3x4 / sticker-sheet-3x4
是否使用系统 $skill-installer 安装上述依赖？
```

确认后：`$skill-installer install --repo EverettFish/ip_illustration_for_yourself --path . --name ip-illustration-character-system --ref main`。该依赖不随本项目打包，不复制上游代码或图片；上游仓库未在本项目声明额外许可证。

Baoyu 依赖缺失时，一次确认可安装一个或多个已选路径：

```text
来源：https://github.com/JimLiu/baoyu-skills
路径：skills/baoyu-article-illustrator skills/baoyu-comic skills/baoyu-cover-image skills/baoyu-infographic skills/baoyu-slide-deck skills/baoyu-xhs-images
ref：main；上游仓库声明 MIT
是否使用系统 $skill-installer 安装选中的 Baoyu Skill？
```

确认后：`$skill-installer install --repo JimLiu/baoyu-skills --path skills/baoyu-article-illustrator skills/baoyu-comic skills/baoyu-cover-image skills/baoyu-infographic skills/baoyu-slide-deck skills/baoyu-xhs-images --ref main`。本项目不复制上游代码或素材。

确认后由系统 `$skill-installer` 安装上述 repo/path/ref，下一轮 Codex 生命周期继续；拒绝则不改环境、不安装、不模仿目标能力。

### 扩展注册

新增目标设计 Skill 时，在 `rongbao-illustrations/references/design-dependencies.json` 增加 `skill_id`、可选 `install_name`、`repo`、`path`、`ref`、`optional`、`reference_policy` 和 `capabilities`，需要时声明 `requires_gpt_image_2`，再增加对应的意图/画幅映射；根仓库用 `path: "."`，不要复制目标 Skill 源码或图片。
