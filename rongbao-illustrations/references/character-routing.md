# 角色选择规则

角色选择由 [character-registry.json](character-registry.json) 驱动，默认角色是 `yazai`（牙仔）。当前注册角色包含绒宝、牙仔、阿龅和已确认的个人 IP 小美；个人照片生成的临时原型不会自动进入这个注册表。角色选择与正文/组合画幅路由分开：先解析角色，再把选中的角色资产和身份参考传给当前执行面。

## 选择顺序

1. 没有识别到角色名称或别名：使用默认牙仔。
2. 识别到中文或英文别名：选择对应角色；英文别名不区分大小写，例如 `yazai`、`YAZAI`、`YaZaI` 都选择牙仔，`abao` 和 `ABAO` 都选择阿龅。
3. 同一请求识别到两个或更多已注册角色：所有角色都保留各自身份并参与核心动作，可以同图出现；不能把多个角色融合为一个混合角色。
4. “这个IP”“该IP”是泛指，不切换角色；没有具体识别名时仍使用默认牙仔。
5. 只有用户明确使用“使用/切换到/指定某某 IP”等语义点名一个未注册名称时，才返回当前支持列表（绒宝、牙仔、阿龅）并请求用户改用支持名称；普通正文中的陌生名词不触发该错误。

真人照片个人 IP 是另一条设计路由，不会因为“人物表情包”或“个人卡通形象”把牙仔自动注入。只有原型经用户明确确认，并同时提供中文显示名、英文 `id`、中英文别名和批准的 PNG 后，才可运行受控注册脚本；注册前的原型只属于当前任务。

## 确定性解析入口

解析完整用户请求时，先解析当前 Skill 根目录，再运行：

```text
python -X utf8 <skill-root>/scripts/character_router.py --json "<request>"
```

JSON 中保留向后兼容的 `characters` ID 列表，并额外返回按注册表顺序排列的
`character_inputs`。每条记录包含 `id`、`display_name`、包内相对路径
`asset`/`identity_reference`，以及从当前安装 Skill 根目录解析出的运行时绝对路径
`asset_path`/`identity_reference_path`；`prompt_label` 明确了 `Image 1/2/3` 与角色的对应关系。
不要从调用方 cwd、开发机路径或手写路径推断角色图片。

普通文章正文中出现陌生名词时，不加 `--explicit`；没有已知别名就按默认角色处理，不把普通名词误报为未知 IP。只有用户明确使用“使用/切换到/指定某某 IP”等语义点名角色时，才在上述命令末尾加 `--explicit`，让未注册名称返回支持列表和错误。

## 透传与资产

每个选中角色都读取其注册的 `asset` 和 `identity_reference`。原生正文模式将角色身份套入正文规则；组合模式将每个角色的参考图传给目标设计 Skill，目标 Skill 决定媒介表现。若同时选择两名或三名角色，不能只传一张参考图、只保留一名角色的身份，或把角色画成一个混合形象；所有选中角色都要参与核心动作。

### 生图/改图的原生图片输入契约

只要请求会实际生成或编辑图片，文字身份描述都不能替代参考图输入，必须按以下顺序执行：

1. 运行 `character_router.py --json`，读取 `character_inputs`，保留注册表顺序。
2. 对每条记录的运行时 `asset_path` 调用 `view_image`，逐张查看已选角色的实际 PNG；不要查看或附加未选角色。
3. 调用图像生成/编辑工具时，把每条记录的 `asset_path` 全部放入 `referenced_image_paths`。单角色也必须传 1 张，多角色按顺序传 2/3 张。
4. 在提示词中明确标注 `Image 1 — 绒宝`、`Image 2 — 牙仔`、`Image 3 — 阿龅`（以本次返回的 `prompt_label` 为准），并说明“每张图仅作为对应角色的身份参考”；同时保留对应的身份协议作为文字约束。

`prompt` 或只做 shot list/路由计划时不生成图片，可以不调用 `view_image`，但输出中必须展示解析得到的 `asset_path` 和对应角色映射，方便下一步原样传入。静态文档只写包内路径 `assets/<id>.png`；运行时永远使用 JSON 返回的绝对 `asset_path`，不要写死某台开发机路径。

角色资产、身份参考或注册项缺失时，doctor 报告角色状态；strict 模式失败，不能静默退回牙仔。

## 确认后注册个人 IP

个人照片 IP 上游只负责从真人照片生成原型、表情和动作包。用户明确说“加入 Rongbao”或“设为正式 IP”后，才执行：

```text
python -X utf8 <skill-root>/scripts/register_character.py --confirm \
  --id <english-id> --display-name <中文名> \
  --alias <中文名> --alias <english-id> \
  --prototype <approved-prototype.png>
```

脚本会把批准的 PNG 复制为 `assets/<id>.png`，创建 `references/<id>-identity.md`，并更新注册表。已有 `id` 或别名默认失败；只有用户再次明确授权并附 `--update` 时才更新已有角色。脚本不安装依赖，也不下载或复制上游个人 IP Skill。
