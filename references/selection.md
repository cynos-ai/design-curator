# 语义选型与状态准备

## brief.json

```json
{
  "schema_version": 1,
  "product": "产品名或明确的暂定名",
  "page_type": "landing",
  "audience": null,
  "language": "zh-CN",
  "viewports": [375, 768, 1440],
  "style_preferences": ["用户原话或忠实概括"],
  "must_not": ["明确排斥条件"],
  "reference_brand": null,
  "available_assets": [],
  "content_status": "approved-draft",
  "assumptions": []
}
```

`page_type` 选 landing/dashboard/docs/commerce/editorial/app/other；`content_status` 选 provided/approved-draft/draft。未知值用 JSON null，不用字符串。

## 推荐顺序

1. 明确禁止条件和硬需求优先，例如不要暗色、必须中文、密集表格。
2. 比较整体气质、信息密度、内容主导方式和任务，而非行业标签。
3. 优先无需重做色板、字体角色或组件系统的规范。
4. 点名品牌时大小写不敏感匹配 display_name 或 slug；不存在则明确告知。
5. 默认两套，明确匹配一套，最多三套。不得凑数。

推荐说明必须引用真实 description，并指出代价，例如专有字体、摄影依赖、偏营销、状态缺失。然后读取全文和 source notes。README 只提供名称/分类，不是风格真相源。

## 全文复核

逐项检查：页面类型和原生布局、主题模式、当前任务所需组件、字体许可及中文覆盖、图片依赖、Responsive Behavior、源文内部冲突、关键交互及对比风险。

不能为了保住初选而现场发明完整组件系统。复核不合适就撤回候选；没有可靠匹配则报告覆盖不足。

## session.json 最低结构

```json
{
  "schema_version": 1,
  "run_id": "20260910T120000Z-a1b2c3",
  "phase": "sample-review",
  "project_root": "/absolute/project/path",
  "root_design_before": {"exists": false, "sha256": null},
  "candidates": [],
  "selected_candidate": null,
  "user_confirmation": null
}
```

phase 只能是 brief/candidates/sample-review/selected/committed/cancelled。每个 candidate 记录 id、slug、relative_path、baseline_sha256、current_design_sha256、sample_sha256、sample_bundle_sha256、review_path。

确认对象必须绑定 candidate_id、design_sha256、sample_bundle_sha256、replacement_approved 布尔值、confirmation_text 和 ISO8601 confirmed_at。确认不能由 Agent 代写。
