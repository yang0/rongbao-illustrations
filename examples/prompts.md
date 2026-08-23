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
- 绒宝在图里做什么
- 建议元素
- 建议中文标注词

<粘贴文章>
```

## 文章正文配图

```text
Use $rongbao-illustrations 把下面这篇文章生成 4 张绒宝怪诞正文配图。
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

画面要怪诞但清爽，读取 `assets/rongbao.png` 作为绒宝角色参考，并让绒宝承担核心动作。
中文标注最多 5 个，短一点。
```

## 工作流主题

```text
Use $rongbao-illustrations 为“把一条原始素材加工成流量、信任、转化三种内容”生成一张图。
不要画正式流程图，不要复刻一鱼多吃旧案例。
请重新发明一个新的低科技隐喻，让绒宝参与核心动作。
```

## 改图：去掉标题

```text
Use $rongbao-illustrations 帮我编辑这张图。
去掉左上角的“Workflow / 流程图”标题和下划线，其他内容保持不变。
不要新增任何文字或物件。
```

## 改图：增强绒宝参与感

```text
Use $rongbao-illustrations 这张图方向对，但绒宝有点像装饰。
请保持核心意思不变，重生成一版：让绒宝成为真正推动结构运转的人。
画面更怪一点，但仍然纯白、清爽、少字。
```

## 生成一组风格样片

```text
Use $rongbao-illustrations 输出 5 个不同主题的绒宝正文配图效果。
主题分别覆盖：信息过载、产品验证、内容复利、一人公司、信任建立。
每张单独生成，不要拼成一张。
```

## 跨设计 Skill 组合

当请求同时包含“绒宝 / 这个IP / 带IP”和目标画幅时，`$rongbao-illustrations` 只负责意图路由与绒宝身份参考，目标设计 Skill 负责画幅、构图、材质、光线、文字和输出。组合请求会保留 `create|prompt` 语义，并将 Skill 内的 `assets/rongbao.png` 作为角色参考图传递；角色要与场景共享媒介和光线，身份色默认鲜亮，禁止综合色偏/统一降饱和/复古做旧；贴片感只做一次角色融合迭代；正文配图仍走本 Skill 原生白底手绘模式。

### 横版封面

```text
Use $rongbao-illustrations create 为这个绒宝 IP 做一张横版封面。
主题：把复杂观点变成一个可记忆的视觉入口。能力：landscape-cover。
```

### 竖版海报

```text
Use $rongbao-illustrations create 为这个 IP 做一张竖版海报。
主题：一条内容从想法到行动的转化。能力：portrait-poster。
```

### 方图

```text
Use $rongbao-illustrations prompt 为带绒宝 IP 的 1:1 方图设计一份提示词。
主题：信任由证据逐步累积。能力：square-graphic。不要直接生图。
```

### 依赖缺失时

首次使用组合能力时，先解析当前 Skill 根目录，再运行 `<skill-root>/scripts/doctor.py --json`；不要假设当前 cwd 是 Skill 目录。若目标 Skill 缺失，展示来源并只请求一次确认：

```text
来源：https://github.com/yang0/dongfang/tree/main/dongfang-cover-design
参数：repo `yang0/dongfang` / path `dongfang-cover-design` / ref `main`
是否使用系统 $skill-installer 从 GitHub 安装上述 repo/path/ref？
```

确认后由系统 `$skill-installer` 安装上述 repo/path/ref，下一轮 Codex 生命周期继续；拒绝则不改环境、不安装、不模仿目标能力。

### 扩展注册

新增目标设计 Skill 时，在 `rongbao-illustrations/references/design-dependencies.json` 增加 `skill_id`、`repo`、`path`、`ref` 和 `capabilities`，再增加对应的意图/画幅映射；不要复制目标 Skill 源码。
