---
ID: protocol.entry_routing
SCOPE: protocol
LOAD: hot
PRIORITY: 10
TRIGGER: 用户首次进入 skill / 主菜单
PHASE: process
VERSION: v1.0.0
UPDATED: 2026-08-20
---

# 4 大门入口路由协议（Entry Routing Protocol）

[REF:protocol.entry_routing]

## 一、设计哲学

**核心原则**（借鉴 webnovel-skills）：**用户不用记 skill 名——路由是 skill 的活**

33+ 个 skill 让用户无从下手。本协议提供 **4 大门入口**，让用户按"我现在想做什么"选择，背后的 skill 路由自动完成。

---

## 二、4 大门入口

```
Auto-Novel Skill
├─ 🚪 门 1: 新建小说（从 0 开新书）
├─ 🚪 门 2: 继续写（接着之前的书）
├─ 🚪 门 3: 优化 / 修改（已有正文）
└─ 🚪 门 4: 投稿 / 分析（准备发布）
```

---

## 三、门 1：新建小说（New Novel）

### 3.1 触发词

```
用户说：
- "我想写小说"
- "帮我建一个新书"
- "从零开始"
- "新小说"
```

### 3.2 路由流程

```
入口 1：新建小说
   ↓
【第 1 步】选题（idea）
   ↓ 调用 protocol.outline 的「选题定位」
   ↓ 4 连问：频道 / 平台 / 题材 / 篇幅
   ↓ 输出：3 个差异化选题（含卖点 + 类型 + 金手指）
   ↓
【第 2 步】世界设定（world，可选）
   ↓ 仅"强设定"题材需要（修仙/科幻/玄幻）
   ↓ 输出：力量体系 + 经济体系 + 地理规则
   ↓
【第 3 步】金手指设计（goldfinger）
   ↓ 调用 protocol.outline 的「核心爽点链」
   ↓ 输出：主角特殊能力 + 升级台阶
   ↓
【第 4 步】人设（character）
   ↓ 调用 protocol.outline 的「主角设定」
   ↓ 输出：主角 + 重要配角 + 反派
   ↓
【第 5 步】大纲（planner）
   ↓ 调用 protocol.planner 的「全书战役总蓝图」
   ↓ 输出：核心矛盾 + 成长弧线 + 大爆点
   ↓
【第 6 步】目录（toc）
   ↓ 调用 protocol.toc 的「章节目录」
   ↓ 输出：30 章 / 批
   ↓
【第 7 步】开篇钩（hook）
   ↓ 调用 protocol.outline 的「黄金三章策略」
   ↓ 输出：前 3 章详细设计
   ↓
【第 8 步】第一篇正文（write）
   ↓ 调用 protocol.write + protocol.context_assembly
   ↓ 输出：第 1 章（3500-4000 字）
   ↓
【第 9 步】建立档案（archive）
   ↓ 调用 protocol.archive
   ↓ 输出：fact_locks/ + chapter_summaries/
   ↓
✅ 完成
```

### 3.3 入口 1 的快捷指令

```
/novel:new           # 完整流程
/novel:new quick     # 简化流程（跳过 world + hook）
/novel:new outline   # 只生成大纲
```

---

## 四、门 2：继续写（Continue Writing）

### 4.1 触发词

```
用户说：
- "继续写"
- "接着写下一章"
- "继续"
- "下一章"
```

### 4.2 路由流程

```
入口 2：继续写
   ↓
【第 1 步】读档（memory）
   ↓ 调用 protocol.archive 的「读档」
   ↓ 输出：当前状态（卷/章/进度/最近摘要）
   ↓
【第 2 步】上下文组装（context）
   ↓ 调用 protocol.context_assembly
   ↓ 输出：7 层上下文（详见 context-assembly.md）
   ↓
【第 3 步】生成章节契约（contract）
   ↓ 基于 Layer 3 当前 50 章规划
   ↓ 输出：本章 must_happen / must_not_happen / ending_hook
   ↓
【第 4 步】正文生成（write）
   ↓ 调用 protocol.write
   ↓ 输出：3500-4000 字正文
   ↓
【第 5 步】5 维评分（scoring）
   ↓ 调用 protocol.quality_scoring
   ↓ 输出：5 维评分报告
   ↓
【第 6 步】一致性检查（consistency）
   ↓ 调用 protocol.context_assembly 的事实锁检测
   ↓ 输出：连续性体检报告
   ↓
【第 7 步】回写档案（archive）
   ↓ 调用 protocol.archive
   ↓ 输出：fact_locks 更新 + chapter_summary
   ↓
✅ 完成
```

### 4.3 入口 2 的快捷指令

```
/novel:continue           # 完整流程
/novel:continue 12        # 跳到第 12 章
/novel:continue volume2   # 跳到第 2 卷
```

---

## 五、门 3：优化 / 修改（Optimize / Revise）

### 5.1 触发词

```
用户说：
- "优化这一章"
- "改写"
- "这一章不好看"
- "润色"
- "去 AI 味"
```

### 5.2 路由流程

```
入口 3：优化 / 修改
   ↓
【第 1 步】选择修改类型
   ↓ 选项 A: 整章重写
   ↓ 选项 B: 局部修改（指定段/句）
   ↓ 选项 C: AI 味检测与去 AI 化
   ↓ 选项 D: 节奏调整
   ↓
【第 2 步】选择修改原因
   ↓ 原因 1: AI 味太重（aidetect）
   ↓ 原因 2: 一致性问题（continuity）
   ↓ 原因 3: 节奏拖沓（pacing）
   ↓ 原因 4: 情绪不充分（emotion）
   ↓ 原因 5: 文风不符（style）
   ↓
【第 3 步】定位问题
   ↓ 自动扫描 → 输出问题清单（到段/句）
   ↓
【第 4 步】选择处理方式
   ↓ 选项 A: 自动修改（AI 直接重写）
   ↓ 选项 B: 提供修改建议（AI 给方案 + 用户拍板）
   ↓ 选项 C: 混合模式（AI 改一部分 + 用户改一部分）
   ↓
【第 5 步】执行修改
   ↓ 调用对应 skill
   ↓
【第 6 步】5 维重新评分
   ↓ 评分提升？ → 接受 / 重写
   ↓
✅ 完成
```

### 5.3 入口 3 的快捷指令

```
/novel:fix                      # 通用修复
/novel:fix aidetect            # 去 AI 味
/novel:fix continuity          # 修复一致性问题
/novel:fix pacing              # 调整节奏
/novel:fix emotion             # 强化情绪
```

---

## 六、门 4：投稿 / 分析（Submit / Analyze）

### 6.1 触发词

```
用户说：
- "我要投稿"
- "准备发了"
- "字数够了吗"
- "能签约吗"
```

### 6.2 路由流程

```
入口 4：投稿 / 分析
   ↓
【第 1 步】篇幅检查（length）
   ↓ 调 references/length-standards.md
   ↓ 输出：当前字数 vs 平台签约门槛
   ↓
【第 2 步】3 章签约体检（submission）
   ↓ 调 references/submission-checklist.md
   ↓ 输出：黄金三章质量体检
   ↓
【第 3 步】过审校对（proofread）
   ↓ 错别字 + 敏感词 + 平台规则
   ↓ 输出：校对报告
   ↓
【第 4 步】平台趋势分析（trends，可选）
   ↓ 当前题材热度 + 同类作品竞争
   ↓ 输出：趋势报告
   ↓
【第 5 步】书名简介打磨（title）
   ↓ 书名 + 简介 + 标签
   ↓ 输出：3 个备选方案
   ↓
✅ 完成
```

### 6.3 入口 4 的快捷指令

```
/novel:submit               # 完整投稿准备
/novel:submit length        # 篇幅检查
/novel:submit title         # 书名打磨
```

---

## 七、入口选择的智能引导

### 7.1 用户不清楚在哪一步时

**自动诊断问题**：

```
AI: "你现在在哪一步？
     ① 我想开始写新小说
     ② 我已经写了 X 章，想继续
     ③ 我对某章不满意，想改
     ④ 我准备投稿"

用户: "不知道"

AI: "几个问题帮你判断：
     - 你已经写过任何一章吗？
     - 你有完整的 5 件知识库吗？
     - 你正在为某章发愁吗？
     - 你的字数已超过 1 万吗？"
```

### 7.2 流程被打断时的恢复

```
AI: "我们上次停在了【第 5 步·金手指设计】。
     今天要从这里继续，还是重新走一遍？

     A. 继续（金手指设计）
     B. 重新走（从选题开始）"
```

---

## 八、入口路由的元数据

### 8.1 路由决策表

```python
def route_entry(user_input):
    """根据用户输入路由到对应入口"""

    triggers = {
        'new': ['新建', '新小说', '从零', '开始', '新书'],
        'continue': ['继续', '接着', '下一章', '续写'],
        'optimize': ['改', '优化', '润色', '去AI味', '难看'],
        'submit': ['投稿', '发布', '字数', '签约']
    }

    for entry, words in triggers.items():
        if any(w in user_input for w in words):
            return entry

    # 不明确时，引导用户
    return ask_for_clarification()
```

### 8.2 入口状态追踪

```yaml
entry_state:
  current_entry: new | continue | optimize | submit
  progress:
    new: 1/9     # 当前在第几步
    continue: 5/7
    optimize: 3/6
    submit: 2/5
  last_step: "金手指设计"
  last_active: "2026-08-20T15:30:00Z"
  pending_actions: []
```

---

## 九、与其他 skill 的差异

相比 webnovel-skills 的 start skill：
- webnovel：4 大门设计但分散在 references/
- 本 skill：**统一在 protocol.entry_routing** + **状态追踪** + **恢复机制**

相比 PhosAQy 的"项目初始化"：
- PhosAQy：仅初始化流程
- 本 skill：**4 大门入口** + **自动选择**

---

## 十、版本演进

| 版本 | 日期 | 关键变更 |
|------|------|----------|
| v1.0.0 | 2026-08-20 | 初始版本（基于 webnovel-skills 4 大门设计改进） |