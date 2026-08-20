---
ID: protocol.context_assembly
SCOPE: protocol
LOAD: hot
PRIORITY: 8
TRIGGER: 「novel：正文」/ 「novel：草案」/ 每章生成前
PHASE: process
VERSION: v1.0.0
UPDATED: 2026-08-20
---

# 7 层上下文组装协议（Context Assembly Protocol）

[REF:protocol.context_assembly]

## 一、设计哲学

**核心问题**：写到几十/几百章后，AI 仍能记得：
- 谁知道什么（信息传播边界）
- 资源还剩多少（资源追踪）
- 系统开放到哪一级（系统权限）
- 哪条因果债没偿还（伏笔）
- 哪个角色状态在何处（角色一致性）

**解决方案**：每章重新组装**有边界的 7 层上下文**，而非塞整本书。

**关键收益**：
- 上下文固定在合理大小（约 30-50K tokens）
- 长篇写到 500 章仍不漂移
- 上下文组装成本可控

---

## 二、7 层上下文架构

每章生成前，按以下 7 层顺序组装：

```
┌─────────────────────────────────────┐
│  Layer 7：项目元数据                  │  ← 项目配置 + 写作风格 + 整体进度
├─────────────────────────────────────┤
│  Layer 6：作者文风样本               │  ← 当前章节需要的文风参考
├─────────────────────────────────────┤
│  Layer 5：当前章节摘要 + 阶段摘要    │  ← 最近 20 章摘要 + 当前 50 章阶段总结
├─────────────────────────────────────┤
│  Layer 4：近场章节正文                │  ← 最近 3 章有效正文
├─────────────────────────────────────┤
│  Layer 3：当前 50 章规划             │  ← 系统阶段计划 + 当前进度 + 已发生事实
├─────────────────────────────────────┤
│  Layer 2：主角状态仓库                │  ← 主角 + 复杂系统文的独立系统状态
├─────────────────────────────────────┤
│  Layer 1：当前章节契约              │  ← 本章必须发生/禁止/章末钩
└─────────────────────────────────────┘
```

**总 token 预算**：30-50K（视章节复杂度可调）

---

## 三、逐层详细定义

### Layer 1：当前章节契约（Chapter Contract）

**职责**：明确"这一章必须做什么，不能做什么"——防止 AI 自由发挥漂移。

**内容**：
```yaml
chapter_contract:
  chapter_number: 12
  chapter_title: "宗门大比初战"

  must_happen:  # 必须发生
    - 张三首次使用透视符箓看穿对手破绽
    - 张三进入宗门大比 16 强

  must_not_happen:  # 禁止发生
    - 张三此时还不能暴露真实修为（应在第 25 章后）
    - 不能让师姐出现（师姐仍在失踪中）

  chapter_ending_hook:  # 章末钩
    - 王二在台下对张三说："有人要对付你"
    - 张三回头看到一个神秘身影

  continuity_risks:  # 连续性风险
    - 上一章张三的伤已恢复 80%（避免写"仍然剧痛"）
    - 师父仍在中毒治疗中（不要写"师父健康"）

  target_words: 3500
```

**token 预算**：~500 tokens

### Layer 2：主角状态仓库（Protagonist State）

**职责**：主角当前的"硬状态"——这些数字绝不能漂移。

**内容**：
```yaml
protagonist_state:
  basic:
    name: 张三
    age: 18
    realm: 筑基期三层

  resources:
    spirit_stones: 100        # 当前灵石数
    equipment:
      - 灵剑（普通品质）
      - 透视符箓（每日 3 次，已用 0 次）

  location: 青云宗比武场

  relationships:
    - target: 师姐（李清）
      relationship: 暗恋（单相思）
      status: 失踪中（第 8 章失踪，至今未找到）
      last_contact: 第 7 章
    - target: 师父（李青云）
      relationship: 敬重
      status: 右臂中毒（已治疗 50%）
      last_contact: 第 10 章

  knowledge_matrix:
    knows:
      - 师姐失踪的初步线索指向宗门内部
    does_not_know:
      - 师父的真实身份（元婴期大能）
      - 透视符箓的真正来源

  emotion_state:
    current: 紧张 + 警惕
    recent_changes: 第 11 章赢了初战，信心增加

  injuries:
    - 旧伤：第 9 章战斗中的轻伤（已恢复）
    - 状态：完全健康
```

**token 预算**：~800 tokens

**复杂系统文**：如系统流、修仙流、科幻流，可补充**独立系统状态仓库**：

```yaml
system_state:
  name: 透视符箓系统
  level: 1
  experience: 80/100
  next_unlock: 透视深度 +10%
  daily_uses: 0/3
  cooldown_until: 今日 00:00
```

### Layer 3：当前 50 章规划（System Phase Plan）

**职责**：当前章节在 50 章规划中的位置 + 已发生 vs 计划目标。

**内容**：
```yaml
phase_plan:
  phase_number: 1     # 第 1 个 50 章阶段
  phase_theme: "宗门崛起·初入江湖"
  phase_chapters: "1-50"

  current_progress:
    planned_to_chapter: 12
    actual_completed_chapter: 11
    on_track: true

  planned_events:
    - chapter: 5
      event: 张三获得透视符箓
      status: 已发生 ✓
    - chapter: 10
      event: 师父受伤
      status: 已发生 ✓
    - chapter: 15
      event: 张三进入宗门大比决赛
      status: 未发生 ⏳
    - chapter: 25
      event: 张三首次暴露真实修为
      status: 锁定（不可提前）🔒

  phase_milestones:
    - chapter: 30
      milestone: 第一卷结尾，主角进入内门
    - chapter: 50
      milestone: 第二卷开场，主角首次下山

  pending_reveals:
    - 张三身世秘密（应在第 30 章揭晓）
    - 师姐失踪真相（应在第 40 章揭晓）
```

**token 预算**：~1000 tokens

**硬约束**：细纲**不能**擅自新增总纲之外的主线事件、角色、能力或伏笔。

### Layer 4：近场章节正文（Recent Chapters）

**职责**：最近 3 章的**有效正文**——保证叙事连续性。

**内容**：
```yaml
recent_chapters:
  - chapter: 11
    title: "宗门大比初战"
    summary: 张三在宗门大比中初战告捷，引起关注
    key_events:
      - 张三首次公开使用透视符箓（不露痕迹）
      - 神秘观众开始注意张三
    ending: 张三回到宿舍，王二来访
    word_count: 3500

  - chapter: 10
    title: "师父的伤"
    summary: 师父中毒事件，张三开始怀疑宗门内部
    key_events:
      - 师父右臂中毒，张三目睹
      - 张三查阅宗门典籍发现异常
    ending: 张三决定参加宗门大比以接近真相
    word_count: 3500

  - chapter: 9
    title: "秘境探险"
    summary: 张三在秘境中探索，遇到妖兽
    key_events:
      - 张三首次使用透视符箓对付妖兽
      - 张三获得一块神秘矿石
    ending: 张三带着矿石回到宗门
    word_count: 3500
```

**token 预算**：~3000 tokens（3 章 × 1000 字 = 3000 tokens）

**注**：复杂伏笔回收时，自动补读"埋设原章"——见 [REF:protocol.foreshadowing] 的伏笔追踪。

### Layer 5：当前章节摘要 + 阶段摘要（Chapter Summary）

**职责**：最近 20 章的摘要 + 当前 50 章阶段的总结——保持长篇一致性。

**内容**：
```yaml
chapter_summaries:
  recent_20_chapters:
    - chapter: 11 → "宗门大比初战，张三告捷，引起注意"
    - chapter: 10 → "师父中毒，张三开始调查"
    - ...
    - chapter: 1 → "张三入门测试，意外通过"

phase_summary:
  phase: "第 1 个 50 章"
  theme: 宗门崛起·初入江湖
  arc_progress: "前 11 章已完成张三在宗门立足、获得金手指、卷入师父中毒事件"
  key_reveals_so_far: "透视符箓能力、师父中毒与宗门内部关联"
  character_development: "张三从懵懂少年成长为有目标的调查者"
  world_state_changes: "宗门大比开启，张三进入内门考核期"
```

**token 预算**：~2000 tokens

### Layer 6：作者文风样本（Style Reference）

**职责**：当前章节需要的**具体文风参考**——根据场景选择最相似的样本。

**内容**：
```yaml
style_samples_for_this_chapter:
  chapter_type: 战斗 + 心理
  matching_samples:
    - source: "文风样本.md · 第 5 段"
      content: |
        我深吸一口气，抬手推开那扇破旧的木门。门后是一片漆黑，
        但我知道，答案就在其中。这一刻，我等了很久。
      style_features:
        - 第一人称视角
        - 古风词汇"深吸一口气""罢了"
        - 短段节奏（约 40 字）

    - source: "文风样本.md · 第 8 段"
      content: |
        剑光一闪，对手的眉心已现红点。
        我收剑入鞘，心中并无得意——这只是开始。
      style_features:
        - 战斗描写简洁
        - 心理活动通过动作呈现（show > tell）
```

**token 预算**：~1000 tokens

### Layer 7：项目元数据（Project Metadata）

**职责**：项目级固定信息——支持上下文组装。

**内容**：
```yaml
project_metadata:
  title: "天命剑仙"
  author: "用户"
  genre: 仙侠 / 玄幻
  tone: 热血 / 阴谋
  pov: 第一人称（"我"）

  total_words_target: 1000000  # 100 万字目标
  current_words: 38500       # 已写 3.85 万字
  progress: 3.85%

  current_phase: 第 1 卷前期（宗门篇）
  current_volume: 1
  current_chapter: 12

  writing_constraints:
    min_words_per_chapter: 3000
    max_words_per_chapter: 4000
    golden_three_chapters_completed: true

  style_baseline:
    avg_paragraph_length: 100 字
    dialogue_ratio: 35%
    description_ratio: 25%
    action_ratio: 30%
    psychology_ratio: 10%
```

**token 预算**：~500 tokens

---

## 四、组装算法

### 4.1 顺序加载

```python
def assemble_context(chapter_number):
    context = {}

    # Layer 7：项目元数据（最先加载，决定后续选择）
    context['layer_7'] = load_layer_7()

    # Layer 1：当前章节契约（决定后续内容）
    context['layer_1'] = load_chapter_contract(chapter_number)

    # Layer 2：主角状态仓库
    context['layer_2'] = load_protagonist_state()

    # 复杂系统文：加载系统状态仓库
    if has_system_state():
        context['layer_2_system'] = load_system_state()

    # Layer 3：当前 50 章规划
    context['layer_3'] = load_phase_plan()

    # Layer 4：近场章节正文（最近 3 章）
    context['layer_4'] = load_recent_chapters(n=3)

    # Layer 5：摘要（最近 20 章 + 阶段摘要）
    context['layer_5'] = load_summaries()

    # Layer 6：文风样本（根据 Layer 1 场景类型选最相似样本）
    context['layer_6'] = load_style_samples_for(context['layer_1'].scene_type)

    return context
```

### 4.2 伏笔补读

如果 Layer 1 标注本章需回收某伏笔，自动补读该伏笔的**埋设原章**：

```python
def maybe_reload_foreshadowing(context, chapter_number):
    contracts = context['layer_1'].continuity_risks
    for risk in contracts:
        if risk.type == 'foreshadowing_payoff':
            planted_chapter = risk.planted_chapter
            context['layer_4_extra'] = load_chapter(planted_chapter)
```

### 4.3 token 预算监控

```python
def check_token_budget(context):
    total = sum(count_tokens(layer) for layer in context.values())
    if total > 60000:
        # 触发警告：上下文过大
        log_warning(f"Context exceeds 60K tokens: {total}")
        # 自动压缩方案：减少 Layer 4 章数（3 → 2）
        context['layer_4'] = load_recent_chapters(n=2)
```

---

## 五、组装后的"事实锁"标记

每条从上下文提取的"硬事实"，必须打上**事实锁标记**（详见 [REF:protocol.fact_lock]）：

```yaml
fact_locks:
  - content: "张三当前拥有 100 灵石"
    source: "世界基石.md · 第 5 行"
    anchored_chapter: 11
    anchored_paragraph: 3
    sha256: "abc123..."
    confidence: 100%  # 来自知识库

  - content: "张三已使用透视符箓 0 次"
    source: "世界基石.md · 第 8 行"
    anchored_chapter: 11
    anchored_paragraph: 5
    sha256: "def456..."
    confidence: 100%
```

**硬约束**：细纲若与已发生事实冲突 → 流程停止，不偷偷改写历史。

---

## 六、组装报告输出

每次组装完成后，输出【上下文组装报告】给用户：

```
【上下文组装报告 · 第 12 章】

Layer 1 章节契约：must_happen=2, must_not_happen=2, ending_hook=2
Layer 2 主角状态：灵石=100, 修为=筑基三层, 健康=完全健康
Layer 3 阶段规划：第 1 阶段 11/50 (22%), on_track=true
Layer 4 近场正文：第 9-11 章（11,500 字）
Layer 5 摘要：20 章 + 第 1 阶段摘要
Layer 6 文风样本：战斗场景 2 段 + 心理场景 1 段
Layer 7 元数据：第 1 卷第 12 章, 进度 3.85%

【事实锁总数】：23 条
【token 总计】：约 38,500 tokens ✓

【补读触发】：无（本章无伏笔回收）

【风险预警】：⚠️ 师父仍在中毒治疗中（已治疗 50%）——本章不能写"师父完全康复"
```

---

## 七、与其他 skill 的差异

相比 MyNovel（chinese-longnovel-skill）的 7 层：
- MyNovel：固定 7 层，但代码隐藏在 Python 脚本中
- 本 skill：**7 层在协议文档中明确说明**，便于审查与扩展

相比 webnovel-skills 的 memory skill：
- webnovel：用单一 memory 技能管理所有状态
- 本 skill：**7 层独立组装**，按需加载，节省 token

---

## 八、版本演进

| 版本 | 日期 | 关键变更 |
|------|------|----------|
| v1.0.0 | 2026-08-20 | 初始版本（基于 MyNovel 7 层上下文改进） |