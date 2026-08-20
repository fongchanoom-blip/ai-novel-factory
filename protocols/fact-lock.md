---
ID: protocol.fact_lock
SCOPE: protocol
LOAD: hot
PRIORITY: 9
TRIGGER: 每条事实生成后
PHASE: process
VERSION: v1.0.0
UPDATED: 2026-08-20
---

# 事实锁协议（Fact Lock Protocol）

[REF:protocol.fact_lock]

## 一、设计哲学

**核心问题**：AI 写长篇时最危险的失误是"看起来合理的胡写"——基于旧信息推断新内容，导致前后不一致。

**解决方案**：每条事实绑定**来源路径 + 锚点 + SHA-256 哈希**，构成**不可篡改的证据链**。

**硬约束**：细纲若与已发生事实冲突 → 流程停止，不偷偷改写历史。

---

## 二、事实锁结构

```yaml
fact_lock:
  # 唯一标识
  id: "FL-001"

  # 事实内容
  content: "张三当前拥有 100 灵石"
  category:  # 8 大类
    - 资源
    - 时间
    - 地点
    - 角色认知
    - 信息传播
    - 能力
    - 身份
    - 伤势
    - 关系
    - 伏笔

  # 证据链
  source:
    file: "世界基石.md"           # 知识库来源
    line: 5                       # 行号
    content_hash: "abc123..."      # 原文 SHA-256
  anchor:
    chapter: 11                   # 锚定章节
    paragraph: 3                  # 段号
    sentence_hash: "def456..."     # 原文 SHA-256

  # 元数据
  created_at: "2026-08-20T10:30:00Z"
  created_by: "system"             # system | user | initial
  confidence: 100%                 # 100% / 80% / < 80%

  # 状态
  status:  # 4 种状态
    - active      # 当前生效
    - superseded  # 被新事实替代
    - retired     # 已不适用（事件过期）
    - contested   # 有争议

  # 关联
  related_facts:
    - "FL-002"
    - "FL-005"
```

---

## 三、8 大事实类别

每条事实锁必须归入以下类别之一：

### 3.1 资源（Resources）

**示例**：
```yaml
- content: "张三拥有 100 灵石"
  category: resources
- content: "张三装备：灵剑（普通品质）、透视符箓（每日 3 次）"
  category: resources
```

### 3.2 时间（Time）

**示例**：
```yaml
- content: "宗门大比开始于第 10 章开始日，第 30 章结束"
  category: time
- content: "师父中毒发生在第 10 章傍晚"
  category: time
```

### 3.3 地点（Location）

**示例**：
```yaml
- content: "第 11 章比武场位于青云宗东广场"
  category: location
- content: "张三当前位于比武场"
  category: location
```

### 3.4 角色认知（Character Knowledge）

**示例**：
```yaml
- content: "张三知道师姐失踪初步线索指向宗门内部"
  category: character_knowledge
- content: "张三不知道师父真实身份是元婴期大能"
  category: character_knowledge
```

### 3.5 信息传播（Information Propagation）

**示例**：
```yaml
- content: "王二不知道张三有透视符箓"
  category: information_propagation
- content: "师父知道张三获得透视符箓（但不知道具体能力）"
  category: information_propagation
```

### 3.6 能力（Powers）

**示例**：
```yaml
- content: "张三的透视符箓每日最多使用 3 次"
  category: powers
- content: "张三在筑基期三层（不可使用御剑飞行）"
  category: powers
```

### 3.7 身份（Identity）

**示例**：
```yaml
- content: "张三当前身份：青云宗外门弟子"
  category: identity
- content: "张三真实身份：前朝遗孤（仅张三本人知道）"
  category: identity
```

### 3.8 伤势（Injuries）

**示例**：
yaml
- content: "张三在第 9 章战斗中受轻伤，已恢复"
  category: injuries
- content: "师父右臂中毒，已治疗 50%"
  category: injuries
```

---

## 四、SHA-256 证据链

### 4.1 哈希计算

```python
import hashlib

def compute_hash(text):
    """计算文本 SHA-256 哈希"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]

# 示例
content = "张三当前拥有 100 灵石"
hash_value = compute_hash(content)
# → "abc123def456"
```

### 4.2 哈希的作用

**每次正文生成后，重新计算哈希**：

```python
def verify_fact_lock(fact_lock_id):
    """验证事实锁的当前状态"""
    lock = get_fact_lock(fact_lock_id)

    # 验证来源文件未变更
    source_content = read_file(lock.source.file, lock.source.line)
    if compute_hash(source_content) != lock.source.content_hash:
        return "STALE", "来源文件已变更，需重新生成事实锁"

    # 验证锚点章节正文未变更
    anchor_text = read_chapter_paragraph(lock.anchor.chapter, lock.anchor.paragraph)
    if compute_hash(anchor_text) != lock.anchor.sentence_hash:
        return "ANCHOR_DRIFT", "锚点章节已变更，需重新生成事实锁"

    return "VALID", "事实锁有效"
```

### 4.3 状态自动更新

**当源头或锚点变更时**：
```
原事实锁状态：active → superseded
新事实锁自动生成：基于当前最新内容
旧事实锁归档至：archive/fact_locks/<chapter>/
```

---

## 五、事实锁的生成时机

### 5.1 自动生成时机

| 时机 | 触发条件 | 示例 |
|---|---|---|
| **章节生成完成** | 每章正文生成后自动提取事实 | 张三在第 12 章获得 50 灵石 → 自动生成 FL-001 |
| **状态变更** | 系统检测到状态变化 | 师父中毒治疗 50% → 70% → 自动更新 FL-002 |
| **用户手动修正** | 用户在知识库中手动修正事实 | 用户修正"张三有 100 灵石"为"张三有 150 灵石" |

### 5.2 自动提取算法

```python
def extract_facts_from_chapter(chapter_text, previous_facts):
    """从新章节中提取事实，与已有事实对比"""

    # 1. 数字类事实（灵石、修为、年龄、物品数量）
    new_facts = extract_numeric_facts(chapter_text)

    # 2. 状态类事实（位置、健康、关系）
    new_facts += extract_state_facts(chapter_text)

    # 3. 知识类事实（谁知道了什么）
    new_facts += extract_knowledge_facts(chapter_text)

    # 4. 与已有事实比对
    for new_fact in new_facts:
        existing = find_matching_fact(new_fact, previous_facts)
        if existing:
            # 更新现有事实锁
            update_fact_lock(existing.id, new_fact)
        else:
            # 生成新事实锁
            create_fact_lock(new_fact)

    # 5. 检测矛盾
    contradictions = detect_contradictions(new_facts, previous_facts)
    if contradictions:
        raise FactLockViolation(contradictions)
```

---

## 六、事实锁冲突处理

### 6.1 冲突类型

| 冲突类型 | 描述 | 处理 |
|---|---|---|
| **数字冲突** | "张三有 100 灵石" vs "张三有 200 灵石" | 以**最近章节**事实为准，旧事实锁 superseded |
| **状态冲突** | "师父健康" vs "师父中毒" | 以**最近章节**事实为准 |
| **位置冲突** | "张三在 A 地" vs "张三在 B 地" | 必须有时间/事件衔接 |
| **知识冲突** | "张三知道 X" vs "张三不知道 X" | 严重错误，触发人工复核 |

### 6.2 冲突解决流程

```
发现冲突
   ↓
自动判定：硬冲突（数字/状态/位置）vs 软冲突（知识/认知）
   ↓
【硬冲突】
  - 以最近章节事实为准
  - 旧事实锁自动 superseded
  - 重新生成事实锁
  - 写入日志

【软冲突】
  - 触发人工复核
  - 输出【事实冲突报告】
  - 等待用户裁决
```

### 6.3 冲突报告示例

```
【事实冲突报告 · 第 15 章】

⚠️ 检测到 1 处软冲突：

事实 A（FL-008）：
  内容："张三不知道师父真实身份是元婴期大能"
  来源：世界基石.md · 第 12 行
  锚点：第 8 章 · 第 4 段

事实 B（推测）：
  内容："张三在第 14 章从宗门典籍中查阅到师父信息"
  来源：第 14 章 · 第 5 段
  置信度：60%（推测）

【冲突类型】
知识认知冲突——推测与既成事实矛盾

【建议】
1. 修改本章内容：删除张三查阅典籍的细节
2. 修改世界基石：删除"张三不知道师父真实身份"
3. 添加伏笔：第 14 章只查到部分信息

请选择处理方式：
A. 修改本章（推荐）
B. 修改知识库
C. 添加伏笔说明
```

---

## 七、事实锁的查询 API

### 7.1 查询当前所有事实

```python
def get_active_facts(category=None):
    """获取所有当前生效的事实锁"""
    locks = read_all_fact_locks(status='active')
    if category:
        locks = [l for l in locks if l.category == category]
    return locks
```

### 7.2 查询特定时间窗口内的事实

```python
def get_facts_in_range(start_chapter, end_chapter):
    """获取指定章节范围内的事实"""
    locks = read_all_fact_locks(status='active')
    return [l for l in locks
            if start_chapter <= l.anchor.chapter <= end_chapter]
```

### 7.3 查询矛盾事实

```python
def get_contested_facts():
    """获取有争议的事实"""
    return read_all_fact_locks(status='contested')
```

---

## 八、事实锁的存储

### 8.1 文件结构

```
用户小说项目/
├── 世界基石.md              ← 当前事实快照（人类可读）
├── fact_locks/
│   ├── active/
│   │   ├── FL-001.yaml      ← 当前生效事实
│   │   ├── FL-002.yaml
│   │   └── ...
│   ├── superseded/          ← 已被替代
│   │   └── FL-XXX.yaml
│   └── contested/           ← 有争议
│       └── FL-XXX.yaml
└── archives/
    └── <chapter>/
        └── fact_locks.yaml  ← 章节生成时的事实快照
```

### 8.2 与世界基石的同步

**世界基石.md = 人类可读的当前事实**。
**fact_locks/ = 机器可读的事实锁 + 证据链**。

每次世界基石更新 → 自动同步更新 fact_locks。

---

## 九、与其他 skill 的差异

相比 MyNovel（chinese-longnovel-skill）的 fact_lock：
- MyNovel：仅在 Python 脚本中实现，不暴露给用户
- 本 skill：**协议文档化** + **冲突报告** + **API 查询**

相比 webnovel-skills 的 memory skill：
- webnovel：通用 memory，无 SHA-256 哈希
- 本 skill：**SHA-256 哈希证据链** + **冲突检测**

---

## 十、版本演进

| 版本 | 日期 | 关键变更 |
|------|------|----------|
| v1.0.0 | 2026-08-20 | 初始版本（基于 MyNovel fact_lock 改进） |