# 独立演练项目：知澜

这是 Skill 的隔离测试项目，不是生产网站。

## 历史提交：保留，不重写生命周期

- 项目根 `DESIGN.md` 保持上一轮已提交的原始字节。
- 原运行 `.design-samples/20260910T123000Z-demo01/` 保持 committed，原 session、root_design_before、确认和正式回执不变。
- 历史截图和 browser-checks.json 仍属于该旧运行，不会作为新候选证据。

**审核撤回的是旧版 prose-consistency 的通过结论，不是删除历史提交事实。** 审核发现旧规范存在 on-primary 正文旧值、字体和响应式规则未同步。旧 review 中的 pass 仅保留为历史记录，不应继续作为质量保证。

## 当前修订：新的 audit run，待复核

新运行：`.design-samples/20260910T062049Z-audit02/`。

- `claude-zh/baseline.DESIGN.md` 从当前项目根完整复制，SHA 为 `932ab9fad6b58f4d3125d6f25a46b217b23d8ae19dcfbd373486e4640ef37b88`。
- 新 session 的 root_design_before 创建时即固定为这个 SHA，不随候选变化。
- 修订只在 `claude-zh/DESIGN.md` 内；与根规范字节不同。
- session=sample-review，review=pending，user_confirmation=null；没有新 commit receipt。
- 新候选 evidence/ 仅包含本轮结构校验报告，无历史截图或浏览器检查记录。
- 原始记录副本保存在新运行的 evidence-before-audit/，用于追溯，不是本轮验收证据。

本次修订未重新进行浏览器验收。后续须复核规范及样张、刷新 review、取得当前版本确认与替换授权，才能通过提交脚本更新根规范并备份真正的上一版。
