# Audit02：执行 Agent 复核记录

范围：当前中文静态演示样张；不等同于用户确认或全部源规范认证。

## 规范、正文与 HTML 对照

已读取候选 frontmatter 和完整正文，并对照 sample.html 的 CSS、DOM、锚点、baseline 差异复核。

| 项目 | 核对/修复 | 结果 |
|---|---|---|
| 主色及状态 | on-primary 正文、token、按钮均为深墨；hover/active 使用 #bf6b50 | 当前用途同步 |
| 字体与语言 | h1/h2 本地 serif/CJK 栈、正文 sans/CJK 栈、query 系统 monospace；同步 query line-height 1.55、正文表格 | 不声称专有字体已加载 |
| 字阶及布局 | h1 72 上限/46 compact/44 narrow，宽度 8em；section h2 50 上限；820/430 断点；组件 padding/radius、44px 目标高度 | 与当前渲染对照 |
| CTA 居中 | 原 .callout margin 覆盖 shell 的 auto margin 导致左偏；改为 0 auto 90px | 左边距 375→12、768→44、1440→130px |
| 对比 | 初检 teal 焦点约2.247:1、primary编号约2.712:1；改 ink 焦点、primary-active编号 | 重测达本样张目标 |
| 操作 | 去掉无效示例邮箱；按钮改成本地查看静态示例，目标可聚焦 | 无外发或真实提交 |
| 内容 | 演示标签、示例资料和项目说明可见；无客户logo、营收、证言、认证声明 | 产品能力为演示文案，不是已核实业务承诺 |
| 正文冲突 | 修正禁止hover、要求实际Claude chrome、强制dark-footer等与当前用途冲突的指令；移除 token.refs 占位形式 | 当前用途不再由旧指令覆盖 |
| 非当前用途 | 未使用的源组件/字阶、source layout reference 保留且标明作用域 | 未做未来组件的全量一致性认证 |

## 新浏览器证据

浏览器：隔离的 Linux Chromium 152，工具返回 UA 记录于 browser-checks.json。
方法：真实 viewport、DOM computed styles/尺寸、文本颜色配对、真实 Tab/Shift+Tab/Enter、hover、pointerdown、截图视觉检查。probe.js 仅为本样张采集数据，不是通用无障碍引擎。

- 375×900、768×1024、1440×1000：scrollWidth 等于视口宽；没有检测到横向溢出、文字颜色失败；截图中中文可读，无可见缺字方框或遮挡截断。
- 可见链接/按钮高度最低44px，按钮约45.6875px。
- 375：Tab 顺序 brand→nav CTA→primary；3px ink focus；Enter 到 #demo-answer 并聚焦该面板；Shift+Tab 到次操作；Enter 到 #workflow。
- 768：实际点击 callout “查看示例回答”进入并聚焦 #demo-answer。
- 1440：hover 与真实 pointerdown 时 :active 均实测为 #bf6b50，前景 #141413；点击到 #demo-answer。其余静态锚点存在性由 DOM 清单检查，不冒充每个链接都逐一点击过。
- 默认 CTA 5.625:1，hover/active 4.770:1；42px编号3.198:1（大号文本目标3:1）；普通正文最低颜色组合5.133:1；ink/cream焦点17.498:1，深色面板内on-dark焦点17.005:1。
- 无图片和远程字体/脚本资源；控制台无事件/异常记录。浏览器请求只有候选HTML、审计probe及一次本地证据保存POST。该POST由复核工具发起，不是sample.html行为。
- 先修改规范再渲染；最终补入非视觉复核说明后重新校验，HTML SHA 与新截图/浏览器报告一致。

## 诚实边界与待用户决定

未证明每个字形具体来自哪一个已安装字体；本地 fallback 在本次浏览器可读，不保证跨系统完全同形。
未检查全浏览器矩阵、原生设备触摸、200%浏览器缩放、屏幕阅读器或所有未使用组件；不宣称完整 WCAG。
当前是静态内容演示，不含真实知识库、试用申请或邮件服务。

执行 Agent 已完成上述范围复核。review 可标 ready-machine-verified，但 session 仍为 sample-review，selected_candidate=null、user_confirmation=null。必须向用户展示此版样张和适配，取得当前版本及替换授权后才能落定。根文件、旧运行、baseline 均未修改。
