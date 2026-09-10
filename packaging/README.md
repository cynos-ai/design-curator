# design-curator — 轻量运行包

这是可直接安装的 Agent Skill 运行包，包含 74 份设计规范、索引、来源锁、构建/校验/安全提交脚本及工作流参考。开发测试、演练截图和审计附件未包含在本 ZIP 中。

## 安装

需要 Python 3.11+ 和 `PyYAML==6.0.2`：

```bash
python -m pip install -r requirements.txt
python scripts/build-library.py --skill-root . --check
```

将解压后的整个 `design-curator/` 目录复制到宿主 skills 目录。pi 可使用：

```bash
pi --skill /absolute/path/to/design-curator
```

也可放入 `~/.pi/agent/skills/design-curator/` 或受信任项目的 `.pi/skills/design-curator/`。

## 使用原则

- 从 `INDEX.md` 中已有规范语义选型，不评分、不默认混搭。
- 候选必须全文读取其 DESIGN.md 和对应 source notes。
- 先在目标项目 `.design-samples/<run-id>/` 生成真实内容样张。
- 所有适配先写回候选规范，再重渲染和验证。
- 用户确认当前版本并明确授权替换后，才能运行安全提交脚本。

完整执行协议见 `SKILL.md` 和 `references/`。

## 完整性

- `PACKAGE-MANIFEST.json`：版本、来源提交和所有运行文件哈希。
- `PACKAGE-CHECKSUMS.sha256`：ZIP 内文件校验和；不包含自身。
- `assets/build-receipt.json`：74 份有效规范、INDEX 和 catalog 的构建回执。

解压后可运行：

```bash
sha256sum -c PACKAGE-CHECKSUMS.sha256
python scripts/build-library.py --skill-root . --check
```

## 来源与限制

规范固定来源于 `VoltAgent/awesome-design-md@8147538b4226ae41e2487a9179e3bcc1f68e8554`，属于非官方品牌灵感分析。MIT 通知见 `assets/UPSTREAM-LICENSE.txt`；商标、图片和专有字体权利需独立确认。

结构校验通过不等于浏览器、字体、可用性或完整 WCAG 认证。无浏览器能力时必须走明确的用户人工检查路径。
