---
ID: protocol.innovation_modules
SCOPE: protocol
LOAD: hot
PRIORITY: 7
TRIGGER: 用户说"剧情太平" / "加戏" / "掀桌"
PHASE: process
VERSION: v1.0.0
UPDATED: 2026-08-20
---

# 创新模块协议（Innovation Modules）

[REF:protocol.innovation_modules]

## 一、设计哲学

**核心问题**（借鉴 vibe-noveling）：当 AI 写到某个阶段，剧情可能**太平、太套路、太乏味**——这是长篇最常见的"中期危机"。

**解决方案**：提供 2 个**创新模块**，打破套路：
1. **booming（剧情爆破）**——让剧情真正"炸"起来
2. **fuck-it（同终点加戏）**——不改本章目标，只让单章内部更戏剧

**与大纲权威性的平衡**：
- 创新模块**不破坏大纲权威**——爆破后的方向仍需经用户确认
- 加戏**不破坏本章目标**——只是强化表达，不改结果

---

## 二、模块 1：booming（剧情爆破）

### 2.1 设计目标

当用户觉得剧情"太平、不够炸、想强行掀桌"时使用——生成 10 套**高烈度爆破方向**，让用户挑选。

### 2.2 触发词

```
- "剧情太平"
- "不够炸"
- "想掀桌"
- "强行反转"
- "加猛料"
- "booming"
```

### 2.3 输入要求

```yaml
booming_input:
  current_state:        # 当前剧情状态
    current_chapter: 25
    current_arc: "第 1 卷中期"
    recent_summary: "张三在宗门立足，准备参加大比决赛"
    planned_next_5_chapters: [...]   # 接下来 5 章原计划

  user_pain_points:    # 用户的不满
    - "剧情太套路了"
    - "反派太弱"
    - "主角太强没张力"

  forbidden_changes:    # 用户不愿触碰的边界
    - "不要让张三提前暴露元婴"
    - "不要改变张三是宗门弟子"
```

### 2.4 输出：10 套爆破方向

```yaml
booming_output:
  directions:
    - id: "BOOM-01"
      title: "神秘长老突然降临，欲收张三为徒"
      intensity: 中  # 高 / 中 / 低
      ripple_radius: 中  # 影响范围：仅本章 / 数章 / 整卷
      conflict: "张三是否要背叛现有宗门"
      feasibility_check: ✓  # 是否符合大纲边界
      pitch: |
        在第 25 章比赛中，一位路过的元婴期大能看中了张三，
        当场要收他为徒。这让张三陷入两难：
        - 留在青云宗，按部就班成长
        - 跟随神秘长老，可能实力大增但背叛师门
      foreshadow_setup: "神秘长老是师父的旧识（第 8 章伏笔）"
      expected_impact: "改变主角成长轨迹，但符合世界观"

    - id: "BOOM-02"
      title: "师姐突然出现，已被敌方势力策反"
      intensity: 高
      ripple_radius: 大
      conflict: "主角是否要面对爱情与立场的冲突"
      feasibility_check: ✓
      pitch: |
        张三苦寻的师姐突然出现，但她已被敌方势力策反。
        她带来的不是温情，而是致命陷阱。
        - 主角的初恋 vs 宗门的安危
        - 师姐的"背叛"是否另有隐情
      foreshadow_setup: "师姐失踪（第 8 章）的真相"
      expected_impact: "卷级高潮，反派提前浮出水面"

    - id: "BOOM-03"
      ...
      （更多 7 套）

  selection_requirement: |
    必须从 10 套中**至少选 2 套"真正掀桌"**的（即 intensity=高 的至少 2 套）
    用户在确认后，调用 protocol.toc 更新目录
```

### 2.5 爆破方向筛选的硬约束

**至少 2 套掀桌**（intensity=高）—— 这是 vibe-noveling 的核心约束：
- 防止"假掀桌"（看似剧烈实际安全）
- 强制创新

**可行性自动检查**（feasibility_check）：
- ✓ 符合世界观规则
- ✓ 不破坏主角人设
- ✓ 不与已有伏笔冲突
- ✓ 主角有能力应对
- ✗ 任何一项不满足 → 自动标记 ✗

**ripple_radius（影响范围）**：
- 仅本章：局部冲突
- 数章：卷内高潮
- 整卷：跨卷铺垫
- 全部：影响大纲骨架（需要重新规划）

### 2.6 选中后的处理

```
用户: "我选 BOOM-01 和 BOOM-02"
   ↓
检查影响范围
   ├─ 仅本章/数章 → 调用 protocol.toc 更新目录
   └─ 整卷/全部 → 调用 protocol.planner 重新规划 + 更新目录
   ↓
更新事实锁（标记新的剧情方向）
   ↓
更新 Layer 3 当前 50 章规划
   ↓
✅ 完成
```

---

## 三、模块 2：fuck-it（同终点加戏）

### 3.1 设计目标

**不改变本章的"结束目标"**，只让单章内部更戏剧、更夸张、更有**漫画感**。

**典型场景**：
- "张三这一章要进入 16 强"（结束目标固定）
- 但"如何进入 16 强"的过程太平淡 → 用 fuck-it 加戏

### 3.2 触发词

```
- "不够爽"
- "太直白"
- "加戏"
- "漫画感"
- "fuck-it"
- "过程不够戏剧"
```

### 3.3 输入要求

```yaml
fuckit_input:
  chapter_outcome:  # 本章不可变的目标
    "张三必须进入宗门大比 16 强"

  current_draft:    # 当前草稿（可选）
    current_chapter: 12
    chapter_draft: "..."

  style_preference:  # 加戏方向
    - "动作戏加强"
    - "心理刻画加强"
    - "反转加强"
```

### 3.4 输出：3 套加戏方案

**内置 15 种加戏方向**（AI 从中随机挑选 3 种）：

| 编号 | 方向 | 描述 |
|------|------|------|
| 1 | 战斗场面更精彩 | 镜头特写、慢动作、感官刺激 |
| 2 | 心理刻画更细腻 | 内心独白、矛盾挣扎 |
| 3 | 反转更剧烈 | 出人意料但合理 |
| 4 | 环境渲染更强烈 | 氛围营造、情绪传递 |
| 5 | 对话更有张力 | 短句交锋、潜台词 |
| 6 | 回忆穿插更巧妙 | 闪回、对比 |
| 7 | 时间压力更紧迫 | 倒计时、节拍 |
| 8 | 旁观者视角 | 切换视角增加戏剧 |
| 9 | 身体语言更丰富 | 微表情、肢体动作 |
| 10 | 多线叙事交错 | 多视角同时进行 |
| 11 | 反差萌 / 反差严肃 | 严肃中带轻松 |
| 12 | 装逼打脸四拍 | 铺垫→嘲讽→爆发→收束 |
| 13 | 扮猪吃虎 | 隐藏实力后反转 |
| 14 | 角色出场震撼 | 关键人物登场 |
| 15 | 道具/细节铺垫 | 伏笔与回收 |

### 3.5 加戏方案示例

```yaml
fuckit_output:
  plans:
    - id: "FUCKIT-01"
      title: "方案 1：战斗慢镜头 + 心理独白"
      used_directions: [1, 2]  # 战斗 + 心理
      modifications:
        - position: "第 3 段"
          original: "张三挥剑向对手"
          suggestion: |
            改为：张三的剑缓缓抬起（慢动作），眼神冰冷。
            内独白：这一剑，等了三个月。
          expected_impact: "紧张感 + 漫画感"
      preserve_outcome: ✓  # 保持"进入 16 强"
      word_count_change: "+50 字"

    - id: "FUCKIT-02"
      title: "方案 2：装逼打脸四拍"
      used_directions: [12, 13]  # 装逼打脸 + 扮猪吃虎
      modifications:
        - position: "第 5 段"
          original: "对手轻视张三"
          suggestion: |
            改为：对手出言嘲讽（第一拍铺垫）→
            张三隐藏实力让对手 3 招（第二拍嘲讽）→
            张三突然爆发（第三拍爆发）→
            对手跪地认输（第四拍收束）。
          expected_impact: "读者爽感 + 10 倍"
      preserve_outcome: ✓
      word_count_change: "+150 字"

    - id: "FUCKIT-03"
      title: "方案 3：旁观者视角"
      used_directions: [8, 9]
      modifications:
        - position: "全章穿插"
          original: "第三人称全知视角"
          suggestion: |
            改为：插入 2 段旁观者视角（王二 + 神秘长老）
            描述张三的招式在他们眼中的震撼程度。
          expected_impact: "提升读者代入感 + 增强'被人关注'的爽感"
      preserve_outcome: ✓
      word_count_change: "+200 字"

  selection_requirement: |
    用户必须从 3 套中**至少选 1 套**
    选中后调用 protocol.write 修改本章
    **硬约束**：本章结束目标必须保持不变
```

### 3.6 硬约束

**本章结束目标不可变**：
- 这是与"剧情爆破（booming）"的核心区别
- booming 改变剧情方向，fuck-it 只强化表达

**如果用户想改结束目标**：
- 系统提示："您想改变本章的结束目标，请改用 `booming` 模块"
- 自动切换到 booming 流程

---

## 四、与其他 skill 的差异

相比 vibe-noveling 的同名模块：
- vibe：基于 Claude Code 私有约定
- 本 skill：**协议文档化** + **硬约束明确**

相比 webnovel-skills 的 expand skill：
- webnovel：通用扩写
- 本 skill：**3 套备选 + 用户选择** + **15 种加戏方向**

---

## 五、与其他协议的协同

### 5.1 booming → planner / toc

```
booming 选中后
   ↓
影响范围 = 整卷 → 调用 protocol.planner 重新规划
影响范围 = 仅本章/数章 → 调用 protocol.toc 更新目录
   ↓
更新事实锁
   ↓
更新 Layer 3 当前 50 章规划
```

### 5.2 fuck-it → write

```
fuck-it 选中后
   ↓
调用 protocol.write 修改本章正文
   ↓
调用 protocol.quality_scoring 重新评分
   ↓
✅ 完成
```

---

## 六、使用流程示例

### 6.1 booming 示例

```
用户: "剧情太平了，第 12 章张三太顺了"

AI: "我理解。让我生成 10 套剧情爆破方向：
     【10 套方案的完整内容】
     请选择您喜欢的 1-3 套。"

用户: "BOOM-01 和 BOOM-02 都很有趣"

AI: "好的。我会调用 protocol.planner 重新规划（因为 BOOM-02 影响范围 = 整卷）。
     请确认是否接受重新规划？"

用户: "接受"

AI: "好的。我已经：
     1. 重新规划了第 1 卷后续 25 章
     2. 更新了当前 50 章规划
     3. 新增了 8 个事实锁
     4. 生成了新的目录（30 章/批）
     请查看新的规划。"
```

### 6.2 fuck-it 示例

```
用户: "第 12 章太平淡，进入 16 强没什么爽感"

AI: "本章结束目标是'张三进入 16 强'，不可变。
     我会用 fuck-it 模块加戏，生成 3 套加戏方案：
     【3 套方案的完整内容】
     请选择您喜欢的方案。"

用户: "方案 2"

AI: "好的。我会：
     1. 修改第 12 章正文（加入装逼打脸四拍）
     2. 新增 200 字左右
     3. 重新评分
     请查看修改后的版本。"
```

---

## 七、版本演进

| 版本 | 日期 | 关键变更 |
|------|------|----------|
| v1.0.0 | 2026-08-20 | 初始版本（基于 vibe-noveling booming/fuck-it 模块改进） |