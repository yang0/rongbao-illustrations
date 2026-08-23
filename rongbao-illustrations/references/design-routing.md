# 绒宝跨设计 Skill 组合路由

## 路由边界

本 Skill 有两个互不混淆的执行面：

| 用户意图 | 执行方式 |
| --- | --- |
| 中文文章、帖子或方法论正文配图；或明确要求 16:9 正文插图 | 本 Skill 原生模式，使用白底极简手绘规则 |
| 同时提到“绒宝”“这个IP”“该IP”“带IP”等身份信号，或显式调用 `$rongbao-illustrations`，以及封面、封面 KV、竖版海报、portrait poster、方图、正方形或 1:1 | 组合路由到已注册的目标设计 Skill |
| 只有 `$dongfang-cover-design`，但没有绒宝/IP 身份信号 | 仅执行用户明确点名的目标 Skill，不注入 `assets/rongbao.png`，不由本 adapter 组合 |
| 只有封面/海报/方图，但没有绒宝或 IP 身份信号 | 不由本 Skill 擅自接管；请用户明确目标设计 Skill 或补充绒宝身份要求 |

“绒宝”“这个IP”或“带IP”等身份信号、显式调用 `$rongbao-illustrations`，以及目标画幅信号，是组合路由的触发条件：显式调用 `$rongbao-illustrations` 时，与封面/海报/方图同时出现即可组合；没有任何绒宝/IP 信号时，单独的 `$dongfang-cover-design` 不得注入绒宝参考图。用户明确点名目标 Skill 时，尊重该明确调用。

## 画幅到能力的映射

- 横版封面、封面 KV、landscape cover → `landscape-cover`
- 竖版海报、竖版封面、portrait poster → `portrait-poster`
- 方图、正方形、1:1 graphic、square graphic → `square-graphic`

目标能力必须出现在 [design-dependencies.json](design-dependencies.json) 的注册表中。注册表是声明性数据，不是目标 Skill 的副本。

## create / prompt 透传

- `create` 表示执行生成：原样透传用户的画幅、材质、光线、文字、尺寸、输出路径和目标 Skill 选项。
- `prompt` 表示生成或检查提示词/路由计划：保留目标 Skill 的提示词契约，不在用户未要求时生图。
- adapter 不吞掉、改写或替换 `create` / `prompt`；只在组合调用中附加 `assets/rongbao.png` 这一角色参考图，并把最终输出交给目标设计 Skill。

## 组合执行

1. 识别身份信号和目标画幅，选出一个注册能力。
2. 先解析当前 Skill 根目录，再运行 `<skill-root>/scripts/doctor.py --json`，确认目标 Skill 是否可用；不要假设当前 cwd 是 Skill 目录。
3. 目标 Skill 可用时，使用本 Skill 的 `assets/rongbao.png` 作为角色参考图，调用目标 Skill；最终画幅、构图、材质、光线、文字和输出服从目标 Skill，且角色与场景共享媒介、笔触、边缘、颗粒、环境光和投影逻辑。
4. 不在本仓库复制、改写或模拟 `dongfang-cover-design` 的文件和能力。

## 组合验收与定向修正

组合图必须检查角色是否与场景共享媒介和光线。若出现参考图材质残留、抠图感或贴片感，只做一次针对角色媒介融合的定向迭代，保持构图、标题、色彩和身份锚点不变；不要借此重做目标设计 Skill 的整体画面。

## 缺失依赖

目标 Skill 缺失时，只展示一次来源和能力，并请求一次确认：

```text
缺少组合依赖：dongfang-cover-design
来源：https://github.com/yang0/dongfang/tree/main/dongfang-cover-design
参数：repo `yang0/dongfang` / path `dongfang-cover-design` / ref `main`
能力：landscape-cover / portrait-poster / square-graphic
是否使用系统 $skill-installer 从 GitHub 安装上述 repo/path/ref？
```

用户确认后，交给系统 `$skill-installer` 执行 GitHub 安装（repo `yang0/dongfang`，path `dongfang-cover-design`，ref `main`），不要自行实现下载器或修改安装环境；告知用户该 Skill 按 Codex 生命周期在下一轮可用，下一轮再继续组合请求。用户拒绝时立即停止，不安装、不修改环境，也不模仿目标 Skill 的封面/海报/方图能力。

## 扩展注册

新增目标设计 Skill 时，只需在注册表增加 `skill_id`、GitHub `repo`、Skill `path`、Git ref `ref` 和 `capabilities`，并在本文件增加明确的身份信号与能力映射。不要把目标 Skill 的源码复制到本仓库。
