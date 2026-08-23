# 生图提示词模板

以下模板只适用于本 Skill 的正文配图原生模式。组合到其他设计 Skill 时，不要套用本模板的白底手绘默认值；改为透传目标 Skill 契约，并附带 `assets/rongbao.png` 作为角色参考图。组合透传时补充：身份色默认保持鲜亮黄、鲜亮青绿和鲜亮橙，只有环境或用户明确要求时才局部变化；禁止综合色偏、统一降饱和或复古做旧伪装融合。

组合媒介适配约束（附加到目标 Skill 提示词）：

```text
Adapt the character's material, stroke, edge, grain, ambient light, and cast shadow to the target medium so the character and scene share one visual medium and lighting logic. Keep Rongbao's identity colors bright yellow, teal green, and orange by default; allow only local changes required by the environment or an explicit user request. Do not preserve studio 3D fur, a hard cutout edge, isolated highlights, global color grading, uniform desaturation, or faux vintage aging. If the character still looks pasted on, make one targeted character-media integration pass only; lock composition, title, palette, and identity anchors.
```

每张图单独生成。根据正文内容替换变量，不要把多张图拼在一起。

```text
Generate one standalone 16:9 horizontal Chinese article illustration.

Visual DNA:
Pure white background. Minimalist black hand-drawn line art. Slightly wobbly pen lines. Lots of empty white space. Sparse red/orange/blue handwritten Chinese annotations. Clean absurd product-sketch feeling. No gradients, no shadows, no paper texture, no complex background, no commercial vector style, no PPT infographic look, no cute mascot poster, no children's illustration, no realistic UI.

Recurring IP character required:
绒宝, a simplified hand-drawn character based on the reference image `assets/rongbao.png`: yellow round body, two teal leaf-like ears, large brown-black eyes with white sclera, orange cheeks, orange hands and feet. Preserve these identity anchors while translating the 3D furry reference into sparse black line art and restrained flat color. 绒宝 must perform the core conceptual action, not decorate the scene. Keep the expression focused and lively, not an over-cute mascot.

Theme:
{正文配图主题}

Structure type:
{结构类型：Workflow / 系统局部 / 前后对比 / 角色状态 / 概念隐喻 / 方法分层 / 地图路线 / 小漫画分镜}

Core idea:
{这张图要表达的核心意思}

Composition:
{具体画面：绒宝在哪里、正在做什么、主要物件是什么、信息如何流动}

Suggested elements:
{元素1} / {元素2} / {元素3} / {元素4}

Chinese handwritten labels:
{标注词1} / {标注词2} / {标注词3} / {标注词4} / {可选标注词5}

Color use:
Black for main line art and structure. Keep 绒宝's identity colors bright yellow, teal green, and orange; restrain their area, not their saturation. Orange for main flow/path/arrows. Red only for key warnings/problems/results. Blue only for secondary notes or feedback/system state.

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
Regenerate this illustration with the same core meaning and simple layout, but make 绒宝 more central to the conceptual action. 绒宝 should be doing the strange work that explains the idea, not standing beside the diagram. Keep the yellow body, teal leaf ears, brown-black eyes, orange cheeks and hands/feet recognizable, while keeping the result clean, sparse, hand-drawn, and not an over-cute mascot.
```
