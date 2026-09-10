# design-curator

> **语言：** [English](./README.md) · 简体中文

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/cynos-ai/design-curator.svg)](https://github.com/cynos-ai/design-curator/releases)

面向编码代理的独立 Agent Skill：从 74 份锁定的品牌灵感 `DESIGN.md` 中语义选择一套，用真实产品内容生成 HTML 样张，经验证和当前版本确认后，安全交付项目根 `DESIGN.md`。

它不是自动评分器、网页模板库、品牌官方规范或 WCAG 认证工具。默认采用单一现成系统，不做跨系统混搭，也不在确认前覆盖项目文件。

## 目录

- [环境](#环境)
- [安装](#安装)
- [使用](#使用)
- [工作流程](#工作流程)
- [仓库结构](#仓库结构)
- [轻量打包](#轻量打包)
- [安全与恢复](#安全与恢复)
- [测试与证据](#测试与证据)
- [来源与许可](#来源与许可)
- [已知边界](#已知边界)

## 环境

- Python 3.11+
- `PyYAML==6.0.2`
- 建议具备真实浏览器能力，用于响应式、字体、交互和对比验证

```bash
python -m pip install -r requirements.txt
python scripts/build-library.py --skill-root .
python scripts/build-library.py --skill-root . --check
```

构建完全离线，固定到 [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md/tree/8147538b4226ae41e2487a9179e3bcc1f68e8554) 提交 `8147538b4226ae41e2487a9179e3bcc1f68e8554`。`--check` 在 Skill 内临时目录重建并逐字节比较，不修改发布产物。

## 安装

从 [Releases](https://github.com/cynos-ai/design-curator/releases) 下载打包好的 Skill 并解压，或直接使用本仓库，并保持 `SKILL.md`、`scripts/`、`references/`、`assets/` 同目录。

将整个 `design-curator/` 目录放入宿主支持的 skills 目录：

- pi 全局：`~/.pi/agent/skills/design-curator/`
- pi 项目（受信任）：`.pi/skills/design-curator/`
- 显式加载：`--skill /absolute/path/to/design-curator`

首次安装后运行一次构建命令。不要只复制 `SKILL.md` 或只复制 13 份 overlay。

## 使用

示例请求：

- “给这个中文 SaaS 落地页选两套风格，先出真实内容样张。”
- “参考 Linear，但先别改根 DESIGN.md。”
- “重新选择项目设计规范；我确认样张后再替换。”

Agent 会读取 `INDEX.md` 中的 74 条完整描述，再完整读取入围候选的规范与 source notes，并在目标项目的 `.design-samples/<run-id>/` 内工作。只有在用户确认当前版本并授权替换后，才会调用提交脚本：

```bash
python scripts/commit-design.py \
  --project-root /path/to/project \
  --session .design-samples/<run-id>/session.json
```

结构检查：

```bash
python scripts/validate-design.py /path/to/candidate/DESIGN.md \
  --baseline /path/to/candidate/baseline.DESIGN.md
```

退出码 0 仅表示没有结构阻断，不代表浏览器与无障碍检查已通过。

## 工作流程

1. **检查项目**：记录根 `DESIGN.md` 是否存在、是否普通文件及其 SHA-256。已有系统优先，除非用户明确要求替换。
2. **建立最小 brief**：产品、页面类型、受众、语言、视口、偏好、排斥条件、素材与内容状态。
3. **语义推荐**：不打分、不做标签权重、不做向量排名。分类仅供浏览，用户明确约束优先于品牌行业。
4. **全文复核**：入围候选必须完整读取规范与 source notes，之后才生成样张。
5. **真实内容样张**：候选共用同一内容清单，但不共用同一布局。摄影型规范体现摄影比例，文档型规范体现阅读层级。
6. **在候选内调整**：所有适配先写回候选 `DESIGN.md`，再重渲染并重新检查样张。
7. **如实验证**：结构、正文一致性、字体、响应式、交互和对比逐项记录 `pass` / `fail` / `not-checked` / `not-applicable`。
8. **确认与安全落定**：只有在当前版本确认、候选与样张 bundle 哈希绑定、备份可校验时，才替换根文件。

## 仓库结构

- `SKILL.md`：短而完整的 Agent 执行协议。
- `INDEX.md` / `assets/catalog.json`：构建生成的描述目录，不含分数和标签。
- `assets/upstream/`：只读的 74 份原始裁剪快照。
- `assets/overlays/`：13 份完整修订文件。
- `assets/source-notes/`：修订来源、遗漏和已知冲突。
- `assets/audit/`：13 份独立 frontmatter YAML 与 unified patches，供审计，不参与运行时叠加。
- `assets/design-md/`：构建后的 74 份有效运行时规范。
- `assets/build-receipt.json`：当前发布产物哈希完成标记。
- `scripts/build-library.py`：固定哈希门禁、overlay、目录和回执构建。
- `scripts/validate-design.py`：严格 YAML、重复键、已知类型、引用、正文引用和 baseline diff。
- `scripts/commit-design.py`：候选/review/确认/bundle 哈希门禁、备份及原子根文件落定。
- `scripts/package-skill.py`：按运行时白名单生成确定性轻量 ZIP，并验证包内清单和校验和。
- `IMPLEMENTATION-SPEC.md`：完整实施设计文档。

## 轻量打包

开发仓库保留 tests、examples 与验收证据；安装包不携带这些文件：

```bash
python scripts/package-skill.py --skill-root . --version 1.0.0
```

默认输出 `dist/design-curator-skill-1.0.0.zip`。压缩包排除 `examples/`、`tests/`、`attachments/`、`assets/audit/` 和开发报告，保留 74 份运行规范、可重建来源、脚本与工作流参考。ZIP 内的 `PACKAGE-MANIFEST.json` 和 `PACKAGE-CHECKSUMS.sha256` 用于独立校验。相同输入和版本会生成字节一致的 ZIP。

## 安全与恢复

提交器拒绝符号链接、路径越界、过期证据、缺少必要检查、根文件外部变化和未授权替换。已有规范备份到运行目录的 `backup/DESIGN.before.md`，回执写入 `commit-receipt.json`。

根文件写入前会在运行目录保存 `commit-intent.json`。若根文件已写入但回执或 session 写入失败，可保持候选、review 和确认不变，重跑同一提交命令：脚本核对 intent、根 SHA 与原备份后只补记录，不再次覆盖。若最后清理失败，`already-committed` 分支会先核对遗留 intent 与回执、session 是否匹配，再清除；不匹配则保留并报错。

构建发布失败时尝试恢复旧产物；恢复也失败则保留 `.build-backup-*` 并输出位置，同时移除完成标记，避免残缺库被当成可用。

恢复旧规范同样需要用户确认。仅当当前根 SHA 等于回执 `after_sha` 且备份 SHA 等于 `before_sha` 时才安全；根已被后续编辑时先展示差异，不自动覆盖。锁只协调本工具，提交期间应避免外部编辑。

## 测试与证据

```bash
python -m unittest discover -s tests -v
```

自动测试覆盖：74 条构建、Slack 补项、raw/overlay/source-note 哈希门禁、构建锁与回执；重复键、缺失与循环引用、代码围栏、类型检查和 baseline diff；新建与替换根规范、备份权限、幂等重跑、过期候选、外部编辑、符号链接、提交锁、崩溃恢复与 review 门禁。

`tests/scenarios.md` 列出 10 个 Agent/浏览器场景及其真实执行状态。`examples/saas-demo/` 是隔离演练夹具：此前的 committed run 保留其规范、review、确认与回执字节，修订在新运行 `20260910T062049Z-audit02` 中完成，以旧根规范为不可变 baseline，并最终经真实脚本确认落定。发布时已把 `session.json` 与 `validate-design.json` 内的本机绝对路径替换为中性的 `/srv/projects/zhilan-demo` 前缀，规范、样张、review、回执和确认的哈希均未受影响。夹具与故障注入测试均明确标注，绝不当成真实用户或浏览器验收。

## 来源与许可

本项目以 MIT 许可发布，见 [`LICENSE`](LICENSE)。

- 上游数据：[VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md)，固定提交 `8147538b4226ae41e2487a9179e3bcc1f68e8554`，MIT 许可。完整通知保存在 [`assets/UPSTREAM-LICENSE.txt`](assets/UPSTREAM-LICENSE.txt)，并逐字节保留在 [`assets/upstream/LICENSE`](assets/upstream/LICENSE)。
- 依赖：PyYAML 6.0.2，MIT 许可。
- 详见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。

上游内容是非官方品牌灵感分析。MIT 许可不覆盖商标、品牌标识、产品图片或专有字体权利，分发与商用前需独立确认。

## 已知边界

- AI 语义选型由 Agent 阅读完成，不由脚本自动打分。
- 颜色基础检查支持 3/4/6/8 位 hex、传统逗号 rgb/rgba、hsl/hsla 数值语法（两组均为别名且 alpha 可选；Hue 接受无单位数或 deg/grad/rad/turn，拒绝百分比），以及 transparent/currentColor。现代空格或 slash 语法、var/calc、命名色等明确标记为 `color-not-checked`，不代替浏览器复核。
- 引用检查识别完整 token 路径，`component.*` 作为源文 `components.*` 别名；frontmatter 断裂引用与整组引用阻断，正文未知形式给出人工复核 finding。components 可引用一个复合 typography token，不可引用整个 typography 组。
- 正文语义一致性、实际字体字形、透明或图片背景对比和布局必须结合人工或浏览器检查。
- 无浏览器时只能走明确的用户人工检查路径，脚本不会自动放行。
- v1 不提供全量 HTML 风格浏览器，不支持默认混搭，也不做原生移动端自动转换。
