# design-curator — portable agent skill

> English below · 中文见下一节

An independent agent skill that picks one design system from 74 pinned brand-inspired `DESIGN.md`
specifications, renders a real-content HTML sample for confirmation, and safely delivers a complete
project-root `DESIGN.md`.

This archive contains the runtime skill only: the 74 effective specifications, the rebuildable
sources, the index, the scripts and the workflow references. Development tests, drill evidence and
audit material are not included.

## Install

Requires Python 3.11+ and `PyYAML==6.0.2`:

```bash
python -m pip install -r requirements.txt
python scripts/build-library.py --skill-root . --check
```

Copy the whole extracted `design-curator/` directory into a skills location supported by your host
(for pi: `~/.pi/agent/skills/design-curator/`, or `.pi/skills/design-curator/` in a trusted project),
or load it explicitly with `pi --skill /absolute/path/to/design-curator`.

## Usage principles

- Select semantically from existing specifications in `INDEX.md`; no scoring, no default mixing.
- Read a shortlisted specification and its source notes in full before generating anything.
- Work inside the target project's `.design-samples/<run-id>/` and render a real-content sample.
- Write every adaptation back into the candidate specification first, then re-render and re-verify.
- Replace the root `DESIGN.md` only after confirming the current version and authorizing replacement.

The complete execution protocol lives in `SKILL.md` and `references/`.

## Integrity

- `PACKAGE-MANIFEST.json` — version, upstream commit and hashes of every runtime file.
- `PACKAGE-CHECKSUMS.sha256` — inner checksums for all files except itself.
- `assets/build-receipt.json` — completion marker for the 74 specifications, index and catalog.

Verify after extracting:

```bash
sha256sum -c PACKAGE-CHECKSUMS.sha256
python scripts/build-library.py --skill-root . --check
```

## Source and license

Released under the MIT license, see `LICENSE`. The specifications come from
[VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md/tree/8147538b4226ae41e2487a9179e3bcc1f68e8554)
commit `8147538b4226ae41e2487a9179e3bcc1f68e8554`, also MIT licensed; the complete notice is in
`assets/UPSTREAM-LICENSE.txt`, and dependency notices are in `THIRD_PARTY_NOTICES.md`.

The upstream content is unofficial inspiration analysis. The MIT license does not cover trademarks,
product imagery or proprietary fonts.

Passing structural validation is not browser, font, usability or full WCAG certification. Without a
browser, only the explicit human-review path is allowed.

---

# design-curator — 可移植 Agent Skill

面向编码代理的独立 Agent Skill：从 74 份锁定的品牌灵感 `DESIGN.md` 中语义选择一套，用真实产品内容
生成 HTML 样张供确认，并安全交付完整的项目根 `DESIGN.md`。

本压缩包只包含运行时 Skill：74 份有效规范、可重建来源、索引、脚本与工作流参考。开发测试、演练证据和
审计材料不在包内。

## 安装

需要 Python 3.11+ 与 `PyYAML==6.0.2`：

```bash
python -m pip install -r requirements.txt
python scripts/build-library.py --skill-root . --check
```

将解压后的整个 `design-curator/` 目录复制到宿主支持的 skills 目录（pi 可用
`~/.pi/agent/skills/design-curator/`，或受信任项目的 `.pi/skills/design-curator/`），也可用
`pi --skill /absolute/path/to/design-curator` 显式加载。

## 使用原则

- 从 `INDEX.md` 已有规范中语义选型；不评分、不默认混搭。
- 入围候选必须完整读取规范与 source notes，之后才生成样张。
- 在目标项目 `.design-samples/<run-id>/` 内工作并生成真实内容样张。
- 所有适配先写回候选规范，再重渲染、重新验证。
- 只有确认当前版本并授权替换后，才更新项目根 `DESIGN.md`。

完整执行协议见 `SKILL.md` 与 `references/`。

## 完整性

- `PACKAGE-MANIFEST.json`：版本、上游提交及所有运行时文件哈希。
- `PACKAGE-CHECKSUMS.sha256`：包内文件校验和（不含自身）。
- `assets/build-receipt.json`：74 份规范、索引与目录的构建完成标记。

解压后可运行：

```bash
sha256sum -c PACKAGE-CHECKSUMS.sha256
python scripts/build-library.py --skill-root . --check
```

## 来源与许可

本项目以 MIT 许可发布，见 `LICENSE`。规范来源于
[VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md/tree/8147538b4226ae41e2487a9179e3bcc1f68e8554)
提交 `8147538b4226ae41e2487a9179e3bcc1f68e8554`，同为 MIT 许可；完整通知见
`assets/UPSTREAM-LICENSE.txt`，依赖说明见 `THIRD_PARTY_NOTICES.md`。

上游内容属于非官方品牌灵感分析；MIT 许可不覆盖商标、产品图片或专有字体权利。

结构校验通过不等于浏览器、字体、可用性或完整 WCAG 认证；无浏览器时必须走明确的用户人工检查路径。
