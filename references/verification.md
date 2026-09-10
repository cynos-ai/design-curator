# 验证、证据与 review 状态

## 四层检查

1. **结构**：YAML、重复键、类型、引用、文件可读。
2. **规范一致性**：受影响 token/组件/正文/状态/响应式同步，scope 明确，无丢失章节。
3. **渲染**：真实视口、实际字体/图片、溢出、操作和状态。
4. **可用性/无障碍**：文本对比、键盘焦点、label、触控、缩放和移动可读。

结构脚本退出 0 只代表无结构阻断。正文一致性由 Agent 审阅 diff 与源文；浏览器结论需要真实截图/检查输出。

## 对比与交互

正常文本目标 4.5:1；符合大号文本定义时 3:1。检查 default/hover/focus/active 及实际状态。透明色结合真实底色合成；图片背景看局部。移动主要点击目标按项目目标 44×44 CSS px 检查。不能因品牌色而保留已确认不可读的关键操作。

## 无浏览器路径

仍生成可打开样张，并给用户逐项清单。只有用户明确反馈检查了对应视口、交互、字体/图片和可读性范围后，才设 `ready-user-reviewed`；保留机器未检查项。仅“选 A”仍为 pending。

## review.json

```json
{
  "schema_version": 1,
  "candidate_id": "claude",
  "design_sha256": "...",
  "sample_sha256": "...",
  "asset_hashes": {},
  "sample_bundle_sha256": "...",
  "external_assets": [],
  "status": "pending",
  "checks": [],
  "blocking_findings": [],
  "accepted_limitations": []
}
```

checks 至少分别记录 structure、references、prose-consistency、fonts、responsive、interaction、contrast、content-authenticity；id 不重复。每项写 method、evidence、findings，pass 必须有非空证据路径或具体检查说明。

最小放行表：

| 路径 | 结构、引用、正文一致性、内容真实性 | 字体、响应式、交互、对比 |
|---|---|---|
| ready-machine-verified | 全部 pass | 全部 pass，记录实际浏览器/检查证据 |
| ready-user-reviewed | 全部 pass | 可保留机器 not-checked，但须有下面的人工检查反馈 |

八个必检项不能用 not-applicable 绕过；额外检查项可使用该状态并说明原因。无表单等局部不适用范围写在检查说明中，不代表整个 interaction 不适用。

人工路径另加：

```json
"human_review": {
  "checked_ids": ["fonts", "responsive", "interaction", "contrast"],
  "feedback": "摘录用户对具体视口、字体/图片、操作和可读性检查的反馈；不是简单选A"
}
```

反馈对应当前 review 的 DESIGN/bundle，仍须取得当前版本的 session.user_confirmation。脚本只检查记录完整性，不认证证据真伪；Agent 不得编造反馈。

bundle 映射含 `sample.html` 和 assets/ 下每个普通文件。按 POSIX 相对路径排序，用：

```python
json.dumps(mapping, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
```

对 UTF-8 字节做 SHA-256。evidence/review 不进入 bundle。远程资源记录 URL、版本/加载证据和许可限制；优先使用可合法固化的本地资源。

## 放行

阻断：结构错误、断裂引用、当前用途冲突、关键交互不可用/不可读、证据 SHA 过期、当前版本未确认或替换授权不足。

有真实浏览器证据且关键项完成可为 `ready-machine-verified`；无浏览器但用户完成具体人工检查可为 `ready-user-reviewed`。二者都不是完整 WCAG 认证。
