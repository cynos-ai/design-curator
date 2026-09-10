# design-curator

独立 Agent Skill：从 74 份锁定的品牌灵感 DESIGN.md 中语义选择一套，用用户真实产品内容生成 HTML 样张，经验证和当前版本确认后，安全交付项目根 `DESIGN.md`。

它不是自动评分器、网页模板库、品牌官方规范或 WCAG 认证工具。默认不混搭，不在确认前覆盖项目文件。

## 环境

- Python 3.11+
- `PyYAML==6.0.2`
- 建议具备真实浏览器能力，用于响应式、字体、交互和对比验证

```bash
python -m pip install -r requirements.txt
python scripts/build-library.py --skill-root .
python scripts/build-library.py --skill-root . --check
python -m unittest discover -s tests -v
```

构建完全离线，固定到 `VoltAgent/awesome-design-md@8147538b4226ae41e2487a9179e3bcc1f68e8554`。`--check` 在 Skill 内临时目录重建并逐字节比较，不修改发布产物。

## 安装

将整个 `design-curator/` 目录复制到宿主支持的 skills 目录，保留 `SKILL.md`、scripts、references 和 assets。以 pi 为例，可放在 `~/.pi/agent/skills/design-curator/`，或受信任项目的 `.pi/skills/design-curator/`；也可通过 `--skill <path>` 加载。

首次安装运行一次构建命令；日常使用前由 Skill 执行 `--check`。不要只复制 SKILL.md 或 13 份 overlays。

## 使用

示例请求：

- “给这个中文 SaaS 落地页选两套风格，先出真实内容样张。”
- “参考 Linear，但先别改根 DESIGN.md。”
- “重新选择项目设计规范；我确认样张后再替换。”

Agent 会读取 `INDEX.md` 的 74 条完整 description，全文复核入围规范和 source notes，在目标项目 `.design-samples/<run-id>/` 工作。它只在用户确认当前候选和覆盖授权后调用：

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

退出 0 仅表示没有结构阻断，不代表浏览器和无障碍全部合格。

## 文件职责

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

完整实施依据保存在 `IMPLEMENTATION-SPEC.md`。

## 安全与恢复

提交器拒绝符号链接、路径越界、过期证据、缺少必要检查、根文件外部变化和未授权替换。已有规范备份到运行目录的 `backup/DESIGN.before.md`，回执写入 `commit-receipt.json`。

恢复也需要用户确认。只有当前根 SHA 等于回执 `after_sha` 且备份 SHA 等于 `before_sha` 时，才可用同样的临时文件+原子替换方式恢复；根已被后续编辑时先展示差异，不自动覆盖。工具锁只协调本工具，运行提交时应避免外部编辑。

## 测试与证据

```bash
python -m unittest discover -s tests -v
```

自动测试覆盖：74 条构建、Slack 补项、哈希/overlay/source-note 门禁、构建锁、回执；重复键、缺失引用、引用循环、代码围栏、类型和 baseline diff；新建/替换根规范、备份权限、幂等重跑、过期候选、外部编辑、符号链接和提交锁。

`tests/scenarios.md` 列出 10 个 Agent/浏览器场景及当前执行状态。`examples/saas-demo/` 是独立演练项目，包含最终规范、候选样张、review、截图与 commit receipt。

## 已知边界

- AI 语义选型由 Agent 阅读完成，不由脚本自动打分。
- 校验器只支持文档声明的已知类型和基础颜色语法；现代颜色可标 not-checked。
- 正文语义一致性、实际字体字形、透明/图片背景对比和布局必须结合人工/浏览器检查。
- 无浏览器时只能走明确的用户人工检查路径，不能自动标 ready。
- 上游是非官方品牌灵感分析；MIT 通知见 `assets/UPSTREAM-LICENSE.txt`。商标、图片和字体权利需独立确认。
- v1 不提供全量 HTML 风格浏览器、不支持默认混搭和原生移动端自动转换。
