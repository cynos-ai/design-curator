# 确认、安全落定与恢复

## 落定前话术必须包含

- 待落定系统与 slug。
- 全部重要项目适配及限制。
- 当前候选 DESIGN 和样张 bundle 的身份。
- 目标 `<project>/DESIGN.md`。
- 根规范已存在时，明确询问是否替换。

用户确认必须针对当前版本；任何规范、HTML 或本地资源变化都会使其失效。

## 提交

使用 `scripts/commit-design.py`，不得手工绕过。脚本拒绝符号链接/越界、状态或哈希不一致、未 ready review、外部修改过的根规范及未授权替换；已有根文件先备份，再同目录原子替换并回读。

成功后交付：根 DESIGN 路径、选定样张、验证摘要、accepted limitations、commit receipt 和备份位置。不要自动开发页面或安装其它工具。

## 异常恢复

若输出 `root_changed=true` 且 `recovery_required=true`，先比较根文件 SHA、候选 SHA 和备份 SHA；根已等于候选时只补全记录，不再次覆盖。若根文件已被后续编辑，停止并展示差异。

恢复旧规范也要用户确认。仅当当前根 SHA 等于 receipt 的 after_sha，且 backup SHA 等于 before_sha 时，才将备份按与提交相同的安全方式恢复；否则不得自动覆盖。

工具锁只协调本工具，提交期间应避免外部编辑。不要强删疑似活跃锁；确认无进程占用后由人工处理遗留锁。

## 后续修改

从当前根 DESIGN 创建新 run、新 baseline 和新确认，不从上游覆盖。资源库更新不会自动升级已落定项目规范。
