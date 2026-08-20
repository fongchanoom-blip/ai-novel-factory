---
ID: protocol.outline
SCOPE: protocol
LOAD: both
PRIORITY: 8
TRIGGER: 「novel:new」/ 「novel:outline」/ 「大纲」
PHASE: process
VERSION: v1.0.0
UPDATED: 2026-08-20
---

# 大纲协议（Outline Protocol）

[REF:protocol.outline]

## 一、设计哲学

**核心原则**：**"大纲 = 故事的骨架，没有骨架的故事会崩"**

大纲是长篇小说的"导航图"——有了大纲，写到第 100 章也知道要去哪里。

**为什么需要大纲协议？**
- 长篇小说没有大纲 = 写到第 50 章就开始漂移
- 大纲 = 防止"前后矛盾"的核心机制
- 大纲 = 团队协作的基础（如有编辑）

**核心策略**：
- ✅ **3 层大纲**：全书战役 → 卷战斗 → 章节任务
- ✅ **基于 Save the Cat 15 节拍**（影视行业验证）
- ✅ **每层都有爽点/钩子/反转**
- ✅ **支持大纲修改**（但要追溯影响）

---

## 二、3 层大纲架构

```
┌─────────────────────────────────────────────────┐
│  Layer 3: 章节任务大纲（每章 3500-5000 字）        │
│  - 本章核心事件（1 个 must_happen）               │
│  - 本章情绪曲线                                   │
│  - 本章钩子                                       │
│  - 本章长度                                       │
└─────────────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────────────┐
│  Layer 2: 卷战斗大纲（每卷 30-100 章）             │
│  - 卷核心冲突                                     │
│  - 卷成长弧线                                     │
│  - 卷高潮 / 卷结局                               │
│  - 卷伏笔（埋设 + 回收）                         │
└─────────────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────────────┐
│  Layer 1: 全书战役大纲（全书 100-500 章）         │
│  - 核心矛盾                                       │
│  - 主角成长弧线（全 4 段）                       │
│  - 终极高潮                                       │
│  - 4 大爆点（开篇/中期/高潮/结局）               │
└─────────────────────────────────────────────────┘
```

---

## 三、Layer 1：全书战役大纲

### 3.1 全书 4 段结构（基于 Save the Cat）

```
📚 全书战役大纲（示例：100 万字玄幻）

1️⃣ 开篇（第 1-25 章，10 万字）
   目标：建立主角 + 金手指 + 主线冲突
   核心事件：入门 → 获得金手指 → 第一次小胜利
   情绪基调：热血 + 期待
   关键爽点：废柴初露锋芒

2️⃣ 发展阶段（第 26-250 章，50 万字）
   目标：建立世界观 + 主角成长 + 多线剧情
   核心事件：加入宗门 → 参加大比 → 第一次大失败
   情绪基调：起伏 + 深度
   关键爽点：实力提升 + 情感发展

3️⃣ 高潮阶段（第 251-400 章，60 万字）
   目标：核心冲突爆发 + 身世揭秘 + 终极对决
   核心事件：身世揭秘 → 反派浮出水面 → 终极大战
   情绪基调：紧张 + 燃点
   关键爽点：扮猪吃虎 + 越级反杀

4️⃣ 结局阶段（第 401-500 章，40 万字）
   目标：回收所有伏笔 + 主角终极成就 + 情感收束
   核心事件：击败终极反派 → 飞升/圆满 → 尾声
   情绪基调：升华 + 圆满
   关键爽点：所有承诺的兑现
```

### 3.2 全书 4 大爆点

```yaml
爆点 1：开篇钩（第 5 章）
  目标：让读者继续看第 6 章
  建议：神秘事件 / 反转身份 / 第一次反杀

爆点 2：中期转折（第 100 章）
  目标：让读者追更
  建议：身世揭秘 / 实力突破 / 反派出场

爆点 3：高潮推进（第 300 章）
  目标：让读者付费
  建议：重大失败 / 情感冲击 / 终极反派浮出

爆点 4：终极高潮（第 450 章）
  目标：让读者强烈满足
  建议：终极对决 / 飞升 / 圆满
```

### 3.3 主角成长弧线（4 段）

```
第 1 段（开篇）：懵懂少年 → 有目标的探索者
第 2 段（发展）：探索者 → 有实力的挑战者
第 3 段（高潮）：挑战者 → 有担当的领袖
第 4 段（结局）：领袖 → 圆满的传奇
```

### 3.4 输出格式

```yaml
book_outline:
  title: 逆天仙途
  total_words: 1000000
  total_chapters: 500

  # 4 大爆点
  mega_beats:
    - position: chapter 5
      title: 第一滴血
      type: 第一次反杀
    - position: chapter 100
      title: 身世揭秘
      type: 身份反转
    - position: chapter 300
      title: 终极对决前夜
      type: 重大失败
    - position: chapter 450
      title: 飞升
      type: 终极成就

  # 4 段结构
  arcs:
    - name: 开篇
      chapters: 1-25
      target_words: 100000
      key_event: 入门 + 金手指
      climax: chapter 5（开篇钩）

    - name: 发展
      chapters: 26-250
      target_words: 500000
      key_event: 宗门大比 + 第一次失败
      climax: chapter 100（中期转折）

    - name: 高潮
      chapters: 251-400
      target_words: 600000
      key_event: 身世揭秘 + 反派对决
      climax: chapter 300（高潮推进）

    - name: 结局
      chapters: 401-500
      target_words: 400000
      key_event: 飞升 + 圆满
      climax: chapter 450（终极高潮）

  # 核心矛盾
  main_conflict: "主角'天灵根'身份与宗门利益冲突"

  # 终极反派
  ultimate_antagonist: "幕后黑手（师父）"

  # 主题
  theme: "命运掌握在自己手中"
```

---

## 四、Layer 2：卷战斗大纲

### 4.1 卷 = 30-100 章的完整故事

```
第 1 卷：入门崛起（第 1-100 章）
   卷核心冲突：张三能否在宗门立足？
   卷成长弧线：废柴 → 外门弟子 → 内门弟子
   卷高潮：第 100 章身世揭秘
   卷伏笔：
      埋设：第 8 章 师姐失踪
      回收：第 95 章 师姐出现
```

### 4.2 卷大纲的 5 大要素

```yaml
volume_outline:
  volume_number: 1
  volume_title: 入门崛起
  chapters: 1-100

  # 卷核心冲突
  conflict: "张三能否在宗门立足？"

  # 卷成长弧线
  arc: "废柴 → 外门弟子 → 内门弟子"

  # 卷高潮
  climax:
    chapter: 100
    title: 身世揭秘
    description: 张三发现自己是天灵根，宗门震动

  # 卷伏笔
  foreshadows:
    - id: FS-001
      type: planted
      chapter: 8
      content: 师姐失踪
      reveal_chapter: 95
      reveal_content: 师姐被反派策反

    - id: FS-002
      type: planted
      chapter: 12
      content: 神秘符箓
      reveal_chapter: 80
      reveal_content: 符箓来自师父

  # 卷爽点
  pleasure_points:
    - chapter: 5
      type: 越级反杀
    - chapter: 30
      type: 装逼打脸
    - chapter: 60
      type: 扮猪吃虎

  # 卷失败
  failures:
    - chapter: 50
      type: 第一次大失败
      impact: 主角觉醒
```

---

## 五、Layer 3：章节任务大纲

### 5.1 每章都有完整契约

```yaml
chapter_outline:
  chapter: 12
  title: 大比初战

  # 本章必须发生
  must_happen:
    - "张三首次使用透视符箓看穿对手破绽"
    - "张三进入宗门大比 16 强"

  # 本章禁止发生
  must_not_happen:
    - "张三还不能暴露真实修为（应在第 25 章后）"
    - "不能让师姐出现（师姐仍在失踪中）"

  # 章末钩
  ending_hook:
    - type: 悬念
      content: "王二在台下对张三说：'有人要对付你'"

  # 情绪曲线
  emotion_curve:
    - phase: 紧张
      chapters: [前半]
    - phase: 燃点
      chapters: [战斗]
    - phase: 期待
      chapters: [后半]
    - phase: 钩子
      chapters: [末尾]

  # 目标字数
  target_words: 3500
```

### 5.2 章节大纲模板

```markdown
# 第 X 章 [标题]

## 核心事件
- [1 个 must_happen]

## 情绪曲线
[紧张 / 燃点 / 期待 / 钩子]

## 章末钩
[1 个强钩子]

## 字数
[目标字数]

## 与前后章的衔接
- 前章：[承接点]
- 后章：[铺设点]
```

---

## 六、大纲生成流程

### 6.1 输入：选题

```yaml
input:
  topic_id: TOPIC-1
  title: 逆天仙途
  genre: 玄幻 / 仙侠
  platform: 起点
  length: 长篇（100 万字）
  main_character: 张三
  golden_finger: 透视符箓
```

### 6.2 输出：完整 3 层大纲

```
生成 Layer 1：全书战役大纲
   ↓
生成 Layer 2：分卷大纲（默认 5 卷 × 100 章）
   ↓
生成 Layer 3：章节大纲（默认 100 章 + 占位后续）
```

### 6.3 大纲生成分 3 步

```python
def generate_outline(topic):
    # Step 1: 全书战役（基于 Save the Cat 15 节拍）
    book_outline = generate_book_outline(topic)  # 5 分钟

    # Step 2: 分卷大纲（每卷 100 章）
    volume_outlines = generate_volume_outlines(book_outline)  # 10 分钟

    # Step 3: 章节大纲（每卷前 30 章 + 后 70 章占位）
    chapter_outlines = generate_chapter_outlines(volume_outlines)  # 15 分钟

    return {
        'book_outline': book_outline,
        'volume_outlines': volume_outlines,
        'chapter_outlines': chapter_outlines
    }
```

### 6.4 总耗时

- Layer 1：5-10 分钟
- Layer 2：10-15 分钟
- Layer 3：15-20 分钟
- **总计**：30-45 分钟

---

## 七、大纲修改与追溯

### 7.1 大纲修改的影响

```
修改第 12 章大纲
   ↓
自动检测影响：
  - 是否影响 Layer 3 其他章节？
  - 是否影响 Layer 2 卷大纲？
  - 是否影响 Layer 1 全书战役？
   ↓
如果影响：
  - 提示用户「此修改将影响 X 个章节大纲」
  - 询问「是否同步更新？」
```

### 7.2 大纲版本管理

```
大纲文件存储：
  book_outline_v1.json  # 当前
  book_outline_v2.json  # 修改后
  book_outline_diff.json # 差异

用户可随时回滚到任意版本。
```

### 7.3 大纲权威性原则

**细纲若与已发生事实冲突 → 流程停止，不偷偷改写历史。**

参考 [REF:protocol.fact_lock] 的冲突处理流程。

---

## 八、与其他协议的协同

### 8.1 outline → toc

```
大纲生成完成：
   ↓
调用 protocol.toc
   ↓
基于大纲生成完整章节目录
```

### 8.2 outline → character-design

```
大纲中的角色：
   ↓
调用 protocol.topic_selection 的角色细化
   ↓
生成完整角色档案
```

### 8.3 outline → world-building

```
大纲中的世界观设定：
   ↓
调用 protocol.knowledge_base_contract
   ↓
生成完整的 5 件知识库
```

---

## 九、Save the Cat 15 节拍（影视行业标准）

借鉴电影行业的经典节拍，确保大纲有节奏：

| # | 节拍 | 位置 | 目标 |
|---|------|------|------|
| 1 | Opening Image | 第 1 章 | 立人设 |
| 2 | Theme Stated | 第 5 章 | 主旨暗示 |
| 3 | Setup | 第 1-10 章 | 建立冲突 |
| 4 | Catalyst | 第 12 章 | 第一次转折 |
| 5 | Debate | 第 13-25 章 | 内心挣扎 |
| 6 | Break into Two | 第 25 章 | 进入第二幕 |
| 7 | B Story | 第 30 章 | 副线（情感） |
| 8 | Fun and Games | 第 30-75 章 | 爽点密集 |
| 9 | Midpoint | 第 75 章 | 中点转折 |
| 10 | Bad Guys Close In | 第 80-100 章 | 反派发力 |
| 11 | All Is Lost | 第 100 章 | 最低点 |
| 12 | Dark Night of the Soul | 第 101-110 章 | 反思 |
| 13 | Break into Three | 第 110 章 | 觉醒 |
| 14 | Finale | 第 110-125 章 | 终极对决 |
| 15 | Final Image | 第 125 章 | 尾声 |

**网络小说通常为 4-5 个完整节拍**（一部长篇 = 多部电影）

---

## 十、错误处理

### 10.1 大纲生成失败

```
😅 抱歉，AI 这会儿想不出好的大纲，让我重新试试...

（10 秒后重试，或）
   ↓
AI: 这次我换一个思路：
- 改变核心冲突
- 调整主角设定
- 简化世界观

你想要哪个方向？
```

### 10.2 大纲太复杂

```
😊 你想要的大纲很丰富！但我想确保质量。

让我先聚焦核心：
1. 主角是谁？
2. 核心冲突是什么？
3. 期望的结局？

其他的我后续补充。
```

### 10.3 用户对大纲不满意

```
用户: "这个大纲太平了"
   ↓
AI: 让我用 protocol.innovation_modules 的 booming 模式重新生成
   ↓
生成 10 套高烈度方向
   ↓
用户选 1 套 → 更新大纲
```

---

## 十一、性能要求

- **响应时间**：
 - Layer 1：≤ 5 分钟
 - Layer 2：≤ 15 分钟
 - Layer 3：≤ 20 分钟
 - **总计**：≤ 45 分钟
- **大纲可读性**：每层都有人话描述 + YAML 结构

---

## 十二、与其他 skill 的差异

相比其他 skill 的"大纲"：
- tianming：有大纲但仅文字描述，无 3 层结构
- MyNovel：分阶段（每 50 章）但无 Save the Cat
- webnovel：分散在多个 references/

**本协议创新**：**"3 层大纲 + Save the Cat 15 节拍 + 修改追溯"**——专业影视编剧方法论。

---

## 十三、版本演进

| 版本 | 日期 | 关键变更 |
|------|------|----------|
| v1.0.0 | 2026-08-20 | 初始版本：3 层大纲 + Save the Cat |