# 附件：13 份 frontmatter 修复与补全

> 配套主文档：[design-curator 实施设计文档 v2](../IMPLEMENTATION-SPEC.md)  
> 来源版本：`VoltAgent/awesome-design-md@8147538b4226ae41e2487a9179e3bcc1f68e8554`  
> 目的：给实现 AI 可直接导入、可验证、可追溯的修订参考，而不是让它重新猜测缺失 tokens。

## 1. 本附件交付了什么

- `upstream/`：主 README、完整 MIT LICENSE、74 份原始 DESIGN.md 的锁定裁剪快照。
- `frontmatter/<slug>.yaml`：13 份完整的有效 YAML 内容，**不含 `---` 边界**。
- `normalized/<slug>/DESIGN.md`：13 份可直接使用的完整修订文件，含 frontmatter 边界与完整源正文。
- `patches/<slug>.patch`：13 份针对固定源版本的 unified diff，可用于审查和独立回放。
- `sources/<slug>.json`：每份修改的来源行号、映射、未定字段与已知冲突。
- `source-lock.json`：原始/修订/YAML 哈希、全部74条清单、overlay路径。
- `validation-report.json`：本次真实执行过的机器检查及其边界。

**实现推荐使用完整 normalized 文件作为 overlay，不要手工从本文复制一小段 YAML 后漏掉其它字段。**

13 份修订分为：3份最小语法修复、10份从正文保守补全。其余61份原始文件不重写。74份有效规范由“原始快照 + 按slug覆盖的13份修订”组成。

本附件不是一份可直接安装的Skill；主文档规定的脚本、工作流与测试仍需实现。

## 2. 导入、校验与优先级

### 2.1 正确导入步骤

1. 先确认源文件SHA与source-lock中的source_sha256相同。
2. 对有overlay的slug使用完整normalized文件，并确认normalized_sha256。
3. 对其余61份使用原始文件，不添加空壳frontmatter、不统一改名。
4. 合并后仍要读取正文。frontmatter只结构化其中可确定部分，不替代Layout、状态、阴影、响应式、图片、禁用项等信息。
5. source-notes随Skill分发；某候选被选入时必须读取对应notes，不能只加载YAML。

不能把本附件patch应用到不同提交的同名文件。遇到SHA不匹配要重新审查，不要“尽量套上”。

### 2.2 数据表示原则

- `version: alpha` 与结构化token命名由本次整理添加，不是品牌官方发布物。
- 缺失文件的`description`逐字摘录该文件Visual Theme & Atmosphere首个完整段落，不采用可能过时的README风格简述，不混入新审美判断。
- 颜色值取源文明确字面量，补充语义名称时记录为`semantic-alias-of-literal`。例如Mastercard的primary取实际营销CTA Ink Black，而不是Logo红黄。
- `rounded.px-12`、`spacing.px-16`等为保守的“按值命名”，不推定它们等价于其它品牌的md/lg，也不表示该值可用于所有角色。
- typography按原层级表逐行录入。确定的字号/字重/行高/字距才写入；`normal`、范围、约数、缺值留在正文及omitted_properties里。
- 字体字段沿用表格/字体章节中的原名字；正文仍保留fallback与许可说明。没有擅自把所有专有字体改成Inter。
- components只录该具体段落明确的属性。不臆造hover值，不把minHeight改成height，不自动继承并补全不确定的组件字段。
- 50%圆形、复合圆角、椭圆、阴影、渐变、motion等未强塞入不适合的alpha类型；保留正文几何/表现规则。
- 相同hex的角色不强行合并；不同角色的命名可有相同值。
- 未给确切值的黄色/粉色/橙色等描述不转换成随意hex。

**“未写进 frontmatter”不等于“可以自创”或“原文不重要”。必须继续读完整正文。**

### 2.3 不做的事情

本次没有：

- 校正所有原文内部冲突；这些是候选复核时必须处理的已知风险。
- 证明所有原规范符合WCAG或所有字体都能取得授权。
- 把可变/响应式属性锁成一个全局默认值。
- 建设统一品牌token schema，让74份规范都必须有相同键。
- 生成缺乏源文依据的组件系统、营销图片或品牌标识。

## 3. 13 份文件导航

| slug | 类型 | 完整修订文件 | YAML | 来源说明 |
|---|---|---|---|---|
| elevenlabs | 语法修复 | [DESIGN.md](../assets/overlays/elevenlabs/DESIGN.md) | [YAML](../assets/audit/frontmatter/elevenlabs.yaml) | [sources](../assets/source-notes/elevenlabs.json) |
| raycast | 语法修复 | [DESIGN.md](../assets/overlays/raycast/DESIGN.md) | [YAML](../assets/audit/frontmatter/raycast.yaml) | [sources](../assets/source-notes/raycast.json) |
| supabase | 语法修复 | [DESIGN.md](../assets/overlays/supabase/DESIGN.md) | [YAML](../assets/audit/frontmatter/supabase.yaml) | [sources](../assets/source-notes/supabase.json) |
| kraken | 缺失补全 | [DESIGN.md](../assets/overlays/kraken/DESIGN.md) | [YAML](../assets/audit/frontmatter/kraken.yaml) | [sources](../assets/source-notes/kraken.json) |
| lamborghini | 缺失补全 | [DESIGN.md](../assets/overlays/lamborghini/DESIGN.md) | [YAML](../assets/audit/frontmatter/lamborghini.yaml) | [sources](../assets/source-notes/lamborghini.json) |
| lovable | 缺失补全 | [DESIGN.md](../assets/overlays/lovable/DESIGN.md) | [YAML](../assets/audit/frontmatter/lovable.yaml) | [sources](../assets/source-notes/lovable.json) |
| mastercard | 缺失补全 | [DESIGN.md](../assets/overlays/mastercard/DESIGN.md) | [YAML](../assets/audit/frontmatter/mastercard.yaml) | [sources](../assets/source-notes/mastercard.json) |
| runwayml | 缺失补全 | [DESIGN.md](../assets/overlays/runwayml/DESIGN.md) | [YAML](../assets/audit/frontmatter/runwayml.yaml) | [sources](../assets/source-notes/runwayml.json) |
| sanity | 缺失补全 | [DESIGN.md](../assets/overlays/sanity/DESIGN.md) | [YAML](../assets/audit/frontmatter/sanity.yaml) | [sources](../assets/source-notes/sanity.json) |
| spotify | 缺失补全 | [DESIGN.md](../assets/overlays/spotify/DESIGN.md) | [YAML](../assets/audit/frontmatter/spotify.yaml) | [sources](../assets/source-notes/spotify.json) |
| starbucks | 缺失补全 | [DESIGN.md](../assets/overlays/starbucks/DESIGN.md) | [YAML](../assets/audit/frontmatter/starbucks.yaml) | [sources](../assets/source-notes/starbucks.json) |
| tesla | 缺失补全 | [DESIGN.md](../assets/overlays/tesla/DESIGN.md) | [YAML](../assets/audit/frontmatter/tesla.yaml) | [sources](../assets/source-notes/tesla.json) |
| theverge | 缺失补全 | [DESIGN.md](../assets/overlays/theverge/DESIGN.md) | [YAML](../assets/audit/frontmatter/theverge.yaml) | [sources](../assets/source-notes/theverge.json) |

## 4. 三份语法修复：仅改错误纯量的写法

### 4.1 ElevenLabs

**错误原因**：description单行未引用字符串中出现`CTAs are subtle: ...`，冒号后空格破坏普通YAML纯量解析。

修复方式：

```diff
-description: [包含 CTAs are subtle: ... 的完整原始单行描述]
+description: >-
+  [同一段完整原始描述]
```

上面是解释示意，不是可应用patch。真实完整patch在[elevenlabs.patch](../assets/audit/patches/elevenlabs.patch)。

不改颜色、字体、组件、正文；解析后的description与原始行文字相同。

### 4.2 Supabase

**错误原因**：description中`quietly technical: ...`同类未转义冒号。

同样改为`description: >-`后缩进完整原文。真实patch：[supabase.patch](../assets/audit/patches/supabase.patch)。

保留原来的`name: Supabaze-Inspired-design-analysis`。这里的拼写不是YAML语法错误，不借此偷偷重写上游命名。Skill显示名称应由README中的Supabase确定。

### 4.3 Raycast：不要改错字段

Raycast文件开头实际为：

```yaml
---
version: alpha
name: Raycast-design-analysis
属于: [含 marketing page: ... 的额外单行长描述]
description: |
  [已有合法的原始description]
```

真正导致语法错误的是未知键`属于`的值，**已有description是合法块纯量**。

正确修复：

```diff
-属于: [额外单行长描述]
+属于: >-
+  [完全相同的额外长描述]
 description: |
   [现有description保持不变]
```

- 保留unknown字段符合保守消费策略。
- 不把`属于`重命名为description；否则产生重复键或覆盖已有描述。
- 不删除那段额外说明。
- 索引使用现有`description`，不是`属于`。

真实patch：[raycast.patch](../assets/audit/patches/raycast.patch)。

### 4.4 三份修复的最小性检查

本次已验证：

- 对应修复键的解析后字符串与原行值一致。
- 从`colors:`开始到文件末尾字节不变，所有视觉tokens和完整正文保留。
- patch可以独立应用到锁定源文件，结果与normalized文件字节完全相同。

## 5. 十份缺失补全：逐份说明

以下摘要帮助实现AI定位风险，完整tokens以对应YAML为准。每个新增token/组件/字阶都在sources JSON中有来源区间；行号指向未修改的upstream原文件。

### 5.1 Kraken

补充：16个语义色、10个字阶、原spacing/radius集合、主按钮/轮廓/浅色/白色按钮与success badge的明确属性。

关键角色：

```yaml
colors:
  primary: '#7132f5'
  canvas: '#ffffff'
  ink: '#101114'
  on-primary: '#ffffff'
```

注意：

- White Button写10px圆角，全局Do要求所有按钮12px。附件保留该变体，项目使用前须明确例外或避开，不能声称无冲突。
- Button/Caption/Small的字重、行高有区间；未任选一个端点。
- Micro行把uppercase写在Letter Spacing列；没有把uppercase写成letterSpacing。
- 50%圆形留在正文，未转成9999px。

### 5.2 Lamborghini

补充：black/gold体系、明确hover与语义色、14个字阶、完整确定spacing/radius、7个明确按钮/状态条目。

关键角色：

```yaml
colors:
  primary: '#FFC000'
  primary-hover: '#917300'
  canvas: '#000000'
  ink: '#FFFFFF'
  on-primary: '#000000'
```

注意：

- 黑底/深灰字的Black Filled是源文自身的低对比问题，忠实录入不是认可其可用性。
- “只允许gold”与cyan/blue/teal的交互特例要按作用域区分。
- 0px按钮/卡片与20px toggle不能统一缩放。
- Body等行有400/700、0.14–0.2px等范围或候选值，未合成虚构默认值。
- 不造缺失表单系统；影像与原字体资源仍须审查。

### 5.3 Lovable

补充：暖中性色与alpha阶梯、12个字阶、间距与圆角集合、5个明确组件。

```yaml
colors:
  primary: '#1c1c1c'
  on-primary: '#fcfbf8'
  canvas: '#f7f4ed'
  hairline: '#eceae4'
```

注意：

- 普通按钮6px，pill仅用于指定icon/action toggle；不能按概述给所有按钮9999px。
- Hero表格行高1.00–1.10未写成单值；项目可依据后文具体示例选择1.10，但须记为应用配置。
- 关键inset shadow、active opacity、focus要继续按正文执行，不能只渲染颜色和圆角。
- 未给stop值的warm gradient没有被补成任意渐变token。

### 5.4 Mastercard

补充：实际CTA与Logo/consent/arc分离的颜色角色、9个字阶、确定的间距圆角、3种明确按钮。

```yaml
colors:
  primary: '#141413'
  on-primary: '#F3F0EE'
  canvas: '#F3F0EE'
  consent: '#CF4500'
  orbit: '#F37338'
```

注意：

- Logo红黄不是UI主色；consent orange不能当营销CTA。
- 字阶表Nav/Button tracking是-0.48px，具体primary段落是-0.32px。没有把按钮绑定到存在冲突的共用字阶；实现按具体用途明确。
- 50%圆形/轨道和卫星CTA几何留正文；未用大px圆角替代。
- “所有点击目标达44px”不能取代实际高度测量。
- 约数尺寸、whisper色和范围不被包装为精确值；shadow的blur/spread解释问题仍需复核。

### 5.5 Runway

补充：无彩色UI色板、9个字阶、确定spacing/radius、仅可确定的button-link圆角与mission暗色区。

```yaml
colors:
  primary: '#000000'
  canvas: '#000000'
  ink: '#ffffff'
  surface: '#1a1a1a'
```

**刻意不补 `on-primary` 或填充CTA。** 源按钮背景仅说`likely transparent or dark`，不足以编造一个黑色主按钮。

- `primary`对应源Primary里的Runway Black，不意味“背景=primary”的通用组件映射。
- Body/Button的weight、lineHeight、tracking未定值。
- imagery不是可有可无的装饰；没有高质量合法素材时不应承诺高保真。
- 不能因为其他品牌都有text-input就给Runway造一个。

### 5.6 Sanity

补充：确定sRGB色、16个字阶、已确定间距/圆角、8个按钮与输入条目。

```yaml
colors:
  primary: '#f36458'
  on-primary: '#ffffff'
  canvas: '#0b0b0b'
  interactive: '#0052ef'
components:
  button-primary-hover:
    backgroundColor: '{colors.interactive}'
    textColor: '{colors.ink}'
```

- 保留红CTA→蓝hover，不机械派生深红hover。
- `space-12=96–120px`没有定值；4–5px radius没有合成md，已知5px来自Ghost。
- P3 green仅采用源文明示的sRGB fallback #19d600，其它P3色留正文，没有自己算近似。
- 48px表格tracking -1.68px与Do泛化范围不一致，项目应明确具体字阶优先与例外。
- 红底白字对比需要实际检查，不因引用有效而放行。

### 5.7 Spotify

补充：播放器色板、14个紧凑字阶、确定spacing/radius、5个明确组件。

```yaml
colors:
  primary: '#1ed760'
  canvas: '#121212'
  surface: '#181818'
  surface-interactive: '#1f1f1f'
  ink: '#ffffff'
```

- 不添加通用on-primary：源文同时存在dark circular play与Prompt中的green circular play，不将两者不加区分地合成一个默认。
- search组件保留具体段落padding `12px 96px 12px 48px`；后文简写并非无差别替代。
- normal行高/字距留正文；不全替成1.5/0。
- 大写按钮tracking是范围，不能用第一端点覆盖全部按钮。
- 50%圆形需要等宽高，不仅是大圆角。
- 这是实际播放器App规范，选型时不能把它当Spotify营销站。

### 5.8 Starbucks：本附件最重要的未决项

补充：四级green及Rewards角色、10个部分结构化字阶、确定spacing/radius、9个明确按钮与卡片条目。

```yaml
colors:
  primary: '#00754A'
  brand-green: '#006241'
  house-green: '#1E3932'
  canvas: '#f2f0eb'
  on-primary: '#ffffff'
```

**源文存在不能无损消解的单位冲突：**

| 原字阶行 | 表格写法 | 与正文 `1rem=10px` 的关系 | 本次处理 |
|---|---|---|---|
| Display | 5.0rem / 80px | 按root应为50px，与80px冲突 | 不写fontSize |
| Jumbo | 3.6rem / 58px | 按root应为36px，与58px冲突 | 不写fontSize |
| Hero Large | 2.8rem / 45px | 按root应为28px，与45px冲突 | 不写fontSize |
| Body | 1.6rem / 16px | 一致 | 写16px，记录单位归一 |
| Small / Micro | 1.4rem / 约14px、1.3rem / 约13px | 明确root可得14/13px | 按root归一，保留来源 |

没有采用80/58/45，也没有擅自“纠正”为50/36/28。需要使用这些展示字阶的项目必须明确选择尺度/root策略，并同步正文后才能落定。

其它注意：

- spacing专门表格的rem与px一致，按px列补录，不被上面的字号冲突连带阻断。
- `-0.16px`与`-0.01em`只在16px时相等，不能全局替换。
- Green Accent主CTA、Starbucks Green标题、House Green深带、Rewards Gold各有独立语义。
- 圆形Frap/复合feedback圆角/椭圆几何不伪装为单个rounded token。
- Rewards渐变示例与全局禁渐变矛盾、移动触控、字体许可仍是候选复核事项。

### 5.9 Tesla

补充：单蓝色CTA+中性层级、8个字阶、少量确定spacing/radius、4个明确组件。

```yaml
colors:
  primary: '#3E6AE1'
  on-primary: '#FFFFFF'
  canvas: '#FFFFFF'
  ink: '#171A20'
```

- `minHeight:40px`没有改成`height:40px`；原文精确最小高度继续保留在正文。
- 原文40px超过44px的说法错误，不当作触控通过依据。
- `Category Label 16px est.`、约12px卡片圆角没有转成确定token。
- hover仅描述略变暗，没有编造一个hex。
- Secondary“same dimensions”与响应式宽度不同，附件没有擅自套200px等继承值。
- 展示/正文两字体角色保留；fallback选择需要写进项目最终规范。

### 5.10 The Verge

补充：mint/purple/状态色等明确值、21个字阶、确定spacing/radius、7个明确组件状态。

```yaml
colors:
  primary: '#3cffd0'
  on-primary: '#000000'
  secondary: '#5200ff'
  canvas: '#131313'
  ink: '#ffffff'
```

- Manuka“只允许≥60px”与移动hero 48–54px、移动wordmark 24–32px相冲突；没有篡改源文，项目必须明确角色例外。
- hover的透明白背景仍配黑字，在暗底合成可能不可读；附件按源文录入并标风险，不能直接宣布验证通过。
- 黄/粉/橙tile没给确切值，不编hex。
- mono timestamp的500/600与tracking范围不被选成单值。
- 原文明确允许字体替代并调整行高；本附件仍保留原Manuka的0.80，不把替代度量作为原品牌token。

## 6. 来源映射 JSON 如何阅读

以`sources/kraken.json`为例：

```json
{
  "slug": "kraken",
  "operation": "prepend-frontmatter",
  "source_repo": "https://github.com/VoltAgent/awesome-design-md",
  "source_commit": "8147538b4226ae41e2487a9179e3bcc1f68e8554",
  "source_path": "design-md/kraken/DESIGN.md",
  "source_sha256": "[实际文件内为完整SHA]",
  "mappings": [],
  "omitted_properties": [],
  "known_issues": [],
  "body_policy": "original body byte-preserved; ambiguities not silently resolved"
}
```

mappings中的类型：

| kind | 含义 |
|---|---|
| `metadata-added` | 本次整理新增的格式/名称元数据 |
| `verbatim-excerpt` | 从正文逐字摘取的description |
| `semantic-alias-of-literal` | 原文已有色值，新增token语义名称；角色须结合正文 |
| `table-transcription` | 原字阶表逐行摘录；fontFamily如来自公共定义，另附章节证据 |
| `scale-transcription` | 已明确spacing/radius集合；按值命名 |
| `component-transcription` | 具体组件段落明确的属性；未写属性不代表自动继承全部 |
| `syntax-only` | 块纯量包装，值语义/视觉tokens/正文不变 |

source_lines为原始文件1起始的闭区间。区间可以是一行表格，也可以是原组件/布局段落；这是来源证据，不是对该来源绝对正确的保证。

omitted_properties列出未结构化的字阶字段及原始内容。当前十份补全共记录125个未写入的属性，其中包括正常的CSS normal、省略号/破折号、范围和真正冲突，**不能把125都解读成严重错误**。源文对它们的语义仍然有效。

未穷举的组件/几何/阴影等保留正文，因此omitted_properties不是所有未结构化信息的总清单。

## 7. 本次真实执行的验证

### 已执行并通过

1. 全74份有效文件以安全YAML加载并拒绝重复键。
2. 74份description均非空。
3. frontmatter中识别到的colors/typography/spacing/rounded/components引用均能定位到已定义路径。
4. 十份补全文件中的已声明fontSize、letterSpacing为允许维度；fontWeight为数值；lineHeight为数值或维度。
5. 十份新增frontmatter后的原始正文逐字节保留。
6. 三份语法修复从colors开始直至末尾逐字节不变；修复键解析后字符串与原值相同。
7. 13个patch在独立原始快照上成功回放，结果与normalized文件字节一致。
8. source-lock记录全部原始和修订哈希，供实现AI重验。

### 未执行/不能据此声称

- 未运行全部文件的官方Google CLI lint。
- 未证明所有现代CSS颜色、alpha合成、字体/图片都可靠。
- 未解决全部源文语义冲突。
- 未验证所有正文token引用、全部类型和引用循环。
- 未生成真实产品HTML、未进行浏览器渲染/键盘/响应式测试。
- 未进行完整WCAG合规评估。

因此，本附件的状态是**“可解析、可追溯、可供实现的保守修订参考”**，不是“74套无需复核就可直接上线的设计系统”。

## 8. 实现时最容易犯的错误

- 只复制13份normalized，漏掉其它61份。
- 把Raycast的`属于`覆盖成description。
- 从README重新生成风格标签，把深色错误简述重新带回来。
- 给Runway/Spotify硬补on-primary，让所有主按钮走同一生成逻辑。
- 把Starbucks有争议的字号随便补齐，或把root全局设10px来掩盖矛盾。
- 遇到normal/范围就在YAML中填1.5、400或区间中点。
- 认为frontmatter覆盖全部表现，丢掉原body、阴影、字形、响应式与Do/Don’t。
- 为消除linter警告删除源文限制、unknown字段或改掉有意的状态色。
- 把“原样保留但已标风险”的组件当作“验证通过”。

**所有最终项目调整应回到主文档第7～9章执行：具体解释、完整写回、当前版本验证、用户确认。**
