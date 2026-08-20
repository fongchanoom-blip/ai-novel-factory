---
ID: protocol.draft
SCOPE: protocol
LOAD: both
PRIORITY: 8
TRIGGER: 「novel:draft」「/novel:draft <章号>」「章节草案」「详细大纲」
PHASE: process
VERSION: v1.0.0
UPDATED: 2026-08-20
---

# 章节草案协议（Chapter Draft Protocol）

[REF:protocol.draft]

## 一、设计哲学

**核心原则**：**"写之前，先画好战斗地图"**

章节草案 = 单章的"作战地图"——告诉 AI 具体场景、对话、动作要怎么安排。

**为什么需要章节草案？**
- 直接生成 3500 字正文，AI 可能"自由发挥"导致漂移
- 草案 = 给 AI 一个"剧本"，但保留弹性
- 草案 = 用户最后审稿的机会（修改后 AI 按草案写）

**核心策略**：
- ✅ **场景分镜**：本章有几个场景，每个场景做什么
- ✅ **关键对话**：重要对话先拟好（不一定要 AI 100% 按）
- ✅ **情绪节奏**：本章的情绪曲线
- ✅ **伏笔标记**：本章要埋/收的伏笔

---

## 二、章节草案 vs 章节大纲 vs 章节正文

| 维度 | 大纲 | 草案 | 正文 |
|------|------|------|------|
| **长度** | 50-200 字 | 1000-3000 字 | 3500-5000 字 |
| **细节** | 核心事件 | 场景 + 对话 + 动作 | 完整叙述 |
| **灵活性** | 抽象 | 半具体 | 具体 |
| **生成时间** | 1 分钟 | 5 分钟 | 30-60 秒 |
| **用户审阅** | | **必要**（修改后再写） | 仅修改 |

**工作流**：
```
章节大纲（toc） → 章节草案（draft）→ 章节正文（write）
   ↓                    ↓                    ↓
   1 分钟              5 分钟              30-60 秒
```

---

## 三、章节草案的 6 大要素

### 3.1 要素 1：场景分镜

```yaml
scene_breakdown:
  - scene: 1
    location: 青云宗比武场
    characters: [张三, 对手（赵无极）, 主考官]
    duration: 30%                    # 占本章 30%
    summary: "张三走上比武台，对手轻蔑"

  - scene: 2
    location: 比武场（战斗）
    characters: [张三, 赵无极]
    duration: 50%                    # 占本章 50%
    summary: "透视符箓发动，张三看穿破绽"

  - scene: 3
    location: 比武场（赛后）
    characters: [张三, 王二]
    duration: 20%                    # 占本章 20%
    summary: "王二警告张三"
```

### 3.2 要素 2：关键对话

```yaml
key_dialogues:
  - character: 主考官
    scene: 1
    content: "张三，你确定要挑战赵师兄？"

  - character: 张三
    scene: 1
    content: "请师兄指教。"
    emotion: 冷静

  - character: 赵无极
    scene: 1
    content: "哼，不自量力。"
    emotion: 轻蔑

  - character: 张三
    scene: 2
    content: "[内心] 他的右肩有旧伤..."
    emotion: 专注
```

### 3.3 要素 3：关键动作

```yaml
key_actions:
  - scene: 2
    action: 张三的剑缓缓抬起
    detail: 慢动作，0.5 秒
    impact: 紧张感

  - scene: 2
    action: 张三透视符箓发动
    detail: 一道金光闪过
    impact: 揭示能力

  - scene: 2
    action: 张三击中对手右肩
    detail: 一剑命中
    impact: 战斗结束
```

### 3.4 要素 4：环境/氛围

```yaml
atmosphere:
  scene_1:
    mood: 紧张 + 压抑
    description: 比武场人山人海，张三走上台时感到无数目光
    sensory: 视觉（人群）+ 听觉（喧嚣）+ 触觉（汗水）

  scene_2:
    mood: 燃点
    description: 比武开始，空气凝固
    sensory: 视觉（剑光）+ 听觉（金属碰撞）+ 触觉（心跳）

  scene_3:
    mood: 期待 + 隐忧
    description: 王二的眼神严肃
    sensory: 视觉（王二表情）+ 听觉（低语）
```

### 3.5 要素 5：情绪曲线

```yaml
emotion_curve:
  chapter_emotion: 紧张 → 燃点 → 期待

  scene_1:
    emotion: 紧张
    intensity: 6/10
    reason: 张三面临强敌

  scene_2:
    emotion: 燃点
    intensity: 10/10
    reason: 战斗爆发，透视显威

  scene_3:
    emotion: 期待 + 隐忧
    intensity: 7/10
    reason: 王二的警告
```

### 3.6 要素 6：伏笔标记

```yaml
foreshadowing:
  plant:                                  # 本章埋设
    - id: FS-013
      scene: 3
      content: 王二提到"有人在针对你"
      hint: 神秘人物身份未明
      reveal_chapter: 50

  reveal:                                 # 本章回收
    - id: FS-005
      scene: 2
      content: 张三透视符箓首次显威
      planted_chapter: 5
      planted_content: 张三得到透视符箓
```

---

## 四、章节草案的完整模板

```markdown
# 第 X 章：[标题]

## 一、章节契约（来自章节大纲）
- 核心事件：
  - [event 1]
  - [event 2]
- 情绪曲线：[紧张 → 燃点 → 期待]
- 钩子：[具体描述]
- 目标字数：[X] 字

## 二、场景分镜

### 场景 1：[地点]（占本章 [X]%）
**人物**：[角色列表]
**氛围**：[紧张 + 描述]
**关键动作**：
- [动作 1]
- [动作 2]

**关键对话**：
- [角色 A]：[对话内容]
- [角色 B]：[对话内容]

### 场景 2：[地点]（占本章 [X]%）
[同上结构]

### 场景 3：[地点]（占本章 [X]%）
[同上结构]

## 三、伏笔处理

### 埋设（plant）
- FS-XXX: [内容]

### 回收（reveal）
- FS-XXX: [内容]（原埋于第 X章）

## 四、事实锁预生成
- 张三进入 16 强
- 张三首次使用透视符箓（在战斗中）
- 王二警告张三

## 五、特殊注意事项
- [注意事项 1]
- [注意事项 2]
```

---

## 五、章节草案生成流程

### 5.1 输入：章节大纲 + 上下文

```yaml
input:
  chapter_outline: ...    # 来自 toc
  context_layers: ...     # 7 层上下文
  recent_chapters: [...]  # 最近 3 章
  foreshadows_to_reveal: [...]  # 待回收伏笔
```

### 5.2 输出：完整章节草案

```python
def generate_chapter_draft(chapter_outline, context):
    draft = {
        'scene_breakdown': generate_scene_breakdown(chapter_outline),
        'key_dialogues': generate_key_dialogues(chapter_outline),
        'key_actions': generate_key_actions(chapter_outline),
        'atmosphere': generate_atmosphere(chapter_outline),
        'emotion_curve': calculate_emotion_curve(chapter_outline),
        'foreshadowing': link_foreshadows(chapter_outline),
    }

    # 输出为 Markdown 格式
    return render_draft_markdown(draft)
```

### 5.3 时间分配

- 场景分镜：1 分钟
- 关键对话：1 分钟
- 关键动作：1 分钟
- 环境氛围：1 分钟
- 情绪曲线：30 秒
- 伏笔标记：30 秒
- **总计**：5 分钟

---

## 六、用户审阅与修改

### 6.1 审阅界面

```
📝 第 12 章《大比初战·透视显威》草案

## 场景 1：比武台入场（30%）
[场景描述...]

## 场景 2：战斗爆发（50%）
[场景描述...]

## 场景 3：王二警告（20%）
[场景描述...]

你想：
A. 接受，开始写正文
B. 修改某个场景（告诉我哪个）
D. 调整对话风格（更口语/更古风）
E. 增加/删除某个场景
```

### 6.2 常见修改类型

| 修改类型 | 示例 |
|----------|------|
| 修改对话 | "张三的话改成更冷静的" |
| 修改动作 | "战斗场景慢一点" |
| 修改氛围 | "增加紧张感" |
| 修改伏笔 | "把 FS-013 移到第 30 章" |
| 修改情绪 | "场景 3 应该更紧张" |

### 6.3 修改流程

```
用户提出修改
   ↓
应用修改
   ↓
重新生成草案
   ↓
用户审阅
   ↓
接受 → 进入正文生成
```

---

## 七、与其他协议的协同

### 7.1 draft → write

```
用户接受草案：
   ↓
调用 protocol.write
   ↓
基于完整草案生成正文
```

### 7.2 draft → fact_lock

```
草案中的事实锁预生成：
   ↓
调用 protocol.fact_lock
   ↓
自动生成 fact_locks
```

### 7.3 draft → 上下文

```
草案需要 7 层上下文：
   ↓
调用 protocol.context_assembly
   ↓
加载上下文
```

---

## 八、特殊场景

### 8.1 用户跳过草案直接写

```
用户: "跳过草案，直接写"
   ↓
AI: 好的，我会按章节大纲直接生成正文。
   风险：可能与你的想法有偏差。

确认跳过？
A. 确认跳过
B. 我还是先看草案
```

### 8.2 章节是过渡章

```
章节大纲标注：过渡章
   ↓
AI: 这是过渡章（约 1500-2000 字，不需要详细草案）
   ↓
生成简化版草案（仅核心事件 + 1 个场景）
```

### 8.3 章节是高潮章

```
章节大纲标注：高潮章
   ↓
AI: 这是高潮章，需要更详细的草案
   ↓
生成增强版草案（所有要素扩展 + 备用对话）
```

---

## 九、性能要求

- **响应时间**：≤ 5 分钟
- **场景数**：3-5 个场景
- **关键对话**：10-15 句
- **关键动作**：5-10 个

---

## 十、错误处理

### 10.1 草案生成失败

```
😅 抱歉，让我重新生成...

或者你想：
A. 跳过这章，写下一章
B. 手动提供草案
C. 调整章节大纲
```

### 10.2 草案与上下文冲突

```
⚠️ 我注意到草案与最近章节有些不一致：
  - 草案：张三今日首次使用透视符箓
  - 第 11 章末尾：张三已用过透视符箓

修正方案：
A. 调整草案
B. 调整第 11 章末尾
C. 添加说明（"虽然用过，但战斗场景中再次使用"）
```

---

## 十一、与其他 skill 的差异

相比其他 skill 的"章节草案"：
- tianming：仅文字描述，无结构化
- MyNovel：用纯文本大纲，无场景分镜
- webnovel：分散在 references/

**本协议创新**：**"6 大要素结构化 + 用户审阅 + 与上下文冲突检测"**——专业编剧工作流。

---

## 十二、版本演进

| 版本 | 日期 | 关键变更 |
|------|------|----------|
| v1.0.0 | 2026-08-20 | 初始版本：6 大要素 + 用户审阅机制 |