# 适配、补足和漂移控制

默认不改系统。任何调整只发生在项目候选副本；Skill 资产、上游快照与 baseline 永不修改。

## 每次调整事务

1. 归类：内容变化、受约束适配、源文纠错或整体换风格。
2. 列影响清单：token 路径、组件/变体、正文表格、Do/Don't、响应式、字体/图片、样张区域。
3. 超出用户请求先说明；整体换风格回到推荐。
4. 保存 before SHA；不覆盖 baseline。
5. 对工作 DESIGN 做最小编辑，保留 unknown 字段、注释和正文。
6. 同步所有受影响数值和解释；相同 hex 可能有不同角色，禁止盲目全局替换。
7. 更新 changes.md，结构校验和人工正文一致性检查。
8. 从新 DESIGN 重出样张，重查状态和视口。
9. 刷新 review 的 DESIGN/HTML/asset/bundle SHA；旧截图和确认作废。
10. 只提交用户确认的当前版本。

## 常见请求

- 亮/暗：同步相关表面、前景、边框和状态，不只改 canvas/ink。
- 主色：先确认真正语义角色，再查 hover/active/focus/disabled、on-color、图表和正文。Sanity 原生红 CTA→蓝 hover 不应机械改成深红。
- 密度：调目标区域间距和组件 padding，不同比例缩放全部 spacing。
- 字号：按语义字阶同步 line-height/tracking/换行/移动规则。
- 圆角：区分普通圆角、pill、circle 和 0px；不得统一倍乘。
- 字体/中文：写回角色、可加载字体、fallback 和度量调整。
- 页面重排：遵守同一系统布局原则，不借另一品牌排版。

## 缺失、区间和冲突

先找同规范中更具体的场景规则；范围可针对当前用途选一个并标“项目选定值”；语义冲突或必需状态缺失时提出最小项目适配；无法可靠补足就换候选或阻止落定。

不要把 normal、近似值或范围擅自写成 1.5、400 或中点。Starbucks 的展示字号 rem/px 冲突必须明确选择尺度与 root 策略。50% 圆形保留几何含义；未知 hover 不用“加深10%”冒充上游事实。

## 最终规范

最终 DESIGN 必须单独可用。项目修订应同步实际 token、组件状态、正文、表格和响应式，而非只在末尾写“已调整”。末尾只保留一个 `Project Application & Provenance` 章节，含 Scope、Source、Applied Adaptations、Verification & Limits、Attribution；写入候选后再验证和确认。

完整 MIT 通知需包含，且不得解释为品牌字体、图片或商标授权。
