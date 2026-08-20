---
ID: protocol.write
SCOPE: protocol
LOAD: both
PRIORITY: 9
TRIGGER: 「novel:continue」/ 「novel:write」/ 「写正文」/ 「下一章」
PHASE: process
VERSION: v1.0.0
UPDATED: 2026-08-20
---

# 正文写作协议（Chapter Writing Protocol）

[REF:protocol.write]

## 一、设计哲学

**核心原则**：**"基于完整草案 + 7 层上下文 + 文风样本，生成 3500-5000 字正文"**

这是 Auto-Novel 的核心协议——所有其他协议都为它服务。

**为什么需要专门的写作协议？**
- 直接让 AI 写 = "自由发挥" = 容易漂移
- 写作协议 = 标准化流程 = 一致性 + 质量可控
- 协议 = 集成所有上下文（知识库 / 事实锁 / 上下文组装）

**核心策略**：
- ✅ **基于章节草案**（不自由发挥）
- ✅ **基于 7 层上下文**（保证一致性）
- ✅ **自动 5 维评分**（保证质量）
- ✅ **自动生成事实锁**（保证不漂移）

---

## 二、写作协议的完整流程

### 2.1 9 步流程

```
入口：用户说"写第 X 章" / "继续写"
   ↓
【第 1 步】加载上下文
   ↓ 调用 protocol.context_assembly
   ↓ 输出：7 层上下文（30-50K tokens）
   ↓
【第 2 步】加载章节草案
   ↓ 调用 protocol.draft
   ↓ 输出：本章的 6 大要素（场景 + 对话 + 动作 + 氛围 + 情绪 + 伏笔）
   ↓
【第 3 步】加载章节大纲
   ↓ 调用 protocol.toc
   ↓ 输出：本章在全书中的位置
   ↓
【第 4 步】生成正文
   ↓ 基于 7 层上下文 + 章节草案 + 章节大纲
   ↓ 输出：3500-5000 字正文
   ↓ 时间：30-60 秒
   ↓
【第 5 步】自动 5 维评分
   ↓ 调用 protocol.quality_scoring
   ↓ 输出：评分报告
   ↓
【第 6 步】一致性检查
   ↓ 调用 protocol.fact_lock
   ↓ 输出：是否与已有事实冲突
   ↓
【第 7 步】如果评分 < 7.0 → 重写
   ↓ 自动重写 1-3 次（最多 3 次）
   ↓
【第 8 步】如果评分 7.0-8.9 → 人工复审
   ↓ 等待用户决策
   ↓
【第 9 步】如果评分 ≥ 9.0 → 自动通过
   ↓ 更新事实锁 + 章节摘要 + 世界基石
   ↓ 输出：完整章节
```

---

## 三、上下文组装（7 层）

详细见 [REF:protocol.context_assembly]。

```
Layer 7: 项目元数据（进度/风格/总字数）
Layer 6: 当前章节需要的文风样本
Layer 5: 最近 20 章摘要 + 50 章阶段摘要
Layer 4: 最近 3 章有效正文
Layer 3: 当前 50 章规划
Layer 2: 主角状态仓库 + 系统状态
Layer 1: 当前章节契约
```

**token 预算**：30-50K tokens

---

## 四、写作的硬约束（必须遵守）

### 4.1 必须遵守的 8 条硬规则

```
1. 字数：3500-5000 字（用户可配置）
2. 视角：第一人称 / 第三人称（用户设定）
4. 文风：参照文风样本（不允许偏离）
5. 设定：遵守世界观规则（力量体系/经济/地理）
6. 一致性：与已有事实锁 100% 一致
7. 钩子：章末必须有钩子（参考 toc 设定）
8. 伏笔：按 draft 埋设/回收
```

### 4.2 禁止的 5 类内容

```
1. ❌ 不允许与已有事实锁冲突
2. ❌ 不允许使用禁用表达（来自文风样本）
3. ❌ 不允许 OOC（角色行为与人设不一致）
4. ❌ 不允许 AI 味重（连续 3 句同句式等）
5. ❌ 不允许超出章节大纲范围
```

---

## 五、写作生成的参数

### 5.1 字数控制

```yaml
default_words: 3500
min_words: 3000
max_words: 5000

platform_adjustments:
  起点: 4000-5000
  番茄: 1500-2500
  晋江: 3000-5000
  七猫: 1500-2500
  知乎: 8000-30000
```

### 5.2 温度参数

```yaml
temperature:
  默认: 0.7
  战斗场景: 0.6      # 严谨
  情感场景: 0.85     # 多样
  对话: 0.75
  描写: 0.7
```

### 5.3 多模型策略

```yaml
默认: Claude 4 / DeepSeek V3
- Claude: 适合情感细腻
- DeepSeek: 适合剧情推进
- GPT-4: 适合英文
```

---

## 六、生成策略

### 6.1 一次性生成

```
优点：速度快（30-60 秒）
缺点：可能不如分段细致
适用：章节大纲清晰 + 草案完整
```

### 6.2 分段生成

```
策略：每个场景单独生成
   场景 1 → 场景 2 → 场景 3
   ↓          ↓          ↓
   1000 字   2000 字    500 字

优点：每段都可调整
缺点：时间长（2-3 分钟）
适用：复杂章节
```

### 6.3 选择策略

```python
def choose_strategy(chapter_outline):
    if chapter_outline.complexity == 'simple':
        return 'one_shot'       # 一次性
    elif chapter_outline.complexity == 'medium':
        return 'scene_by_scene' # 分场景
    else:  # complex
        return 'hybrid'         # 混合（先大纲后细化）
```

---

## 七、5 维自动评分（强制）

### 7.1 评分流程

```
生成正文
   ↓
自动评分（不展示给用户，仅系统内部）
   ↓
如果 ≥ 9.0 → 自动通过
如果 7.0-8.9 → 标记"需复审"
如果 < 7.0 → 自动重写（最多 3 次）

（重写 3 次仍未通过 → 人工介入）
```

### 7.2 评分权重

| 维度 | 权重 |
|------|------|
| 人设一致性 | 30% |
| 世界观一致性 | 25% |
| 逻辑性 | 20% |
| 文风一致性 | 15% |
| 非重复性 | 10% |

---

## 八、事实锁自动生成

### 8.1 提取事实

```python
def extract_facts_from_chapter(chapter_text):
    """从新章节中提取事实"""
    facts = []

    # 1. 数字类（灵石/修为/年龄/物品数量）
    facts += extract_numeric_facts(chapter_text)

    # 2. 状态类（位置/健康/关系）
    facts += extract_state_facts(chapter_text)

    # 3. 知识类（谁知道了什么）
    facts += extract_knowledge_facts(chapter_text)

    # 4. 物品变化（得到/失去）
    facts += extract_item_facts(chapter_text)

    return facts
```

### 8.2 冲突检测

```
新事实 vs 已有事实锁
   ↓
如果冲突 → 提示用户
   ↓
用户决策：
   - 接受新事实（更新事实锁）
   - 保持旧事实（重写正文）
```

---

## 九、与其他协议的协同

### 9.1 完整协同图

```
用户: "写第 12 章"
   ↓
[REF:protocol.context_assembly]  加载 7 层上下文
   ↓
[REF:protocol.draft]            加载章节草案
   ↓
[REF:protocol.toc]              加载章节大纲
   ↓
[REF:protocol.knowledge_base_contract]  加载 5 件知识库
   ↓
[REF:protocol.write] ← 当前协议
   ↓
[REF:protocol.quality_scoring]   自动 5 维评分
   ↓
[REF:protocol.fact_lock]         生成事实锁
   ↓
[REF:protocol.context_assembly]  更新主角状态仓库
   ↓
输出：完整章节
```

---

## 十、用户可配置的参数

```yaml
# user-config.yaml
writing:
  default_words: 3500
  temperature: 0.7
  model: claude-4-sonnet

  quality_threshold:
    auto_pass: 9.0
    review_needed: 7.0
    rewrite_needed: 0.0

  fact_extraction:
    enabled: true
    auto_resolve_conflicts: false

  style_constraints:
    disable_ai_smell: true
    disable_tells: true
    show_don_t_tell_ratio: 0.6  # 60% show, 40% tell
```

---

## 十一、错误处理

### 11.1 评分 < 7.0 自动重写 3 次

```
第 1 次评分 6.5 → 重写
第 2 次评分 7.2 → 通过（7.0-8.9 = 复审）
   ↓
提示用户：本次评分 7.2（需复审）
   ↓
用户决策：
A. 接受（写入）
B. 重写
```

### 11.2 评分一直 < 7.0

```
重写 3 次仍 < 7.0
   ↓
提示用户：AI 多次尝试未达预期
   ↓
建议：
A. 检查章节草案是否合理
B. 检查 5 件知识库是否完整
C. 手动修改草案后再写
```

### 11.3 事实冲突

```
新事实 vs 已有事实锁
   ↓
提示用户：发现 [X] 处冲突
   ↓
用户决策：
A. 接受新事实
B. 保持旧事实
C. 人工调整
```

---

## 十二、性能要求

- **生成时间**：30-60 秒（一次性）
- **重写时间**：每个循环 30-60 秒
- **总时间**：≤ 3 分钟（含最多 3 次重写）

---

## 十三、与其他 skill 的差异

相比其他 skill 的"正文写作"：
- tianming：手写流程，无强制评分
- MyNovel：Python 脚本，但无评分
- PhosAQy：评分为主，写作为辅

**本协议创新**：**"基于草案 + 7 层上下文 + 自动评分 + 事实锁"**——完整工程化写作流程。

---

## 十四、版本演进

| 版本 | 日期 | 关键变更 |
|------|------|----------|
| v1.0.0 | 2026-08-20 | 初始版本：9 步流程 + 自动评分 + 事实锁 |