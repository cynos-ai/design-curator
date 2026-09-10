# 独立演练项目：知澜

这是 Skill 的隔离演练项目，不是生产网站。

## 当前状态：audit02 已确认并落定

- 生效规范：项目根 `DESIGN.md`，与 audit02 候选逐字节一致。
- 当前运行：`.design-samples/20260910T062049Z-audit02/`。
- 用户查看样张路径后回复“可以，继续”；当前版本确认和替换授权记录在 session.json。
- session=committed，review=ready-machine-verified，正式回执为 commit-receipt.json。
- 旧版备份：新运行的 `backup/DESIGN.before.md`，与本轮 baseline 字节一致。

SHA：
- 提交前：`932ab9fad6b58f4d3125d6f25a46b217b23d8ae19dcfbd373486e4640ef37b88`
- 提交后：`d962edd85b3781e9dbc7cca32ff3e71af906e456d53fc8f6f61bfd0ed006cb48`
- 样张 bundle：`da1b553f5506ea1029770fe76063c6bf1e202bd23674dcb11c0c641f916a345c`

## 复核范围

执行 Agent 已完成规范/CSS/DOM对照和真实375/768/1440视口复核，修复低对比焦点与编号、无效邮箱操作、callout居中等问题。证据在当前候选 `claude-zh/evidence/`；样张为 `claude-zh/sample.html`。

中文fallback在本次浏览器可读，但不保证每个字形的具体字体来源。不声称完整WCAG、跨浏览器、原生触控或200%浏览器缩放认证。该样张只有本地静态示例操作，没有真实知识库或试用服务。

候选规范及复核证据中的“等待确认”描述是提交前复核快照。提交脚本严格复制用户已确认字节，不在落定时追加文字；当前生命周期以 session 和 commit receipt 为准。

## 历史与恢复

原运行 `.design-samples/20260910T123000Z-demo01/` 的规范、review、确认与回执保留原始字节。旧版一致性通过结论已被审核撤回，但历史提交事实不被重写。

为公开发布，两个 `session.json` 和两份 `validate-design.json` 证据中的本机绝对路径已替换为中性前缀 `/srv/projects/zhilan-demo`；规范、样张、review、回执和确认的哈希均未改变，审计链依然成立。

新 baseline 与 root_design_before 固定指向旧版 SHA。只有用户确认后，根规范才由提交脚本更新；旧版完整保存在 backup/，前后 SHA 不同。

恢复旧版也需要用户确认。仅当当前根 SHA 仍等于本次回执 after_sha 且备份 SHA 等于 before_sha 时，才可按安全落定流程恢复；后续已编辑的根规范不得直接覆盖。
