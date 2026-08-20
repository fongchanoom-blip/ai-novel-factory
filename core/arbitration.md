---
ID: core.arbitration
SCOPE: core
LOAD: both
PRIORITY: 10
PHASE: process
VERSION: v1.0.0
UPDATED: 2026-08-20
---

# 双层真理仲裁协议（Two-Layer Truth Arbitration）

[REF:core.arbitration]

## 触发时机

每条用户指令处理前必须执行本协议。

---

## 第一阶段：内殿铸魂（仅冷启动）

### 1.1 加载所有核心协议

冷启动时，按以下顺序加载：

1. [REF:core.boot.sequence]（启动序列）
2. [REF:core.session_state]（会话状态）
3. [REF:constant.global]（全局常数）
4. [REF:META_TAGS]（元标签体系）
5. [REF:codex.safety]（安全法典）

### 1.2 编译内在地址映射表

遍历所有 `[ID:xxx]` 标记，建立【内在地址映射表】：

```
内在地址映射表：
├─ core.boot.sequence → core/boot-sequence.md
├─ core.arbitration → core/arbitration.md
├─ core.session_state → core/session-state.md
├─ protocol.outline → protocols/outline.md
├─ ...（所有 14 个 ID）
```

### 1.3 创建 REF 直接链接

遍历所有 `[REF:xxx]` 引用，建立从引用点到目标法则的【直接内存链接】。

### 1.4 编译全局常数表

读取 [REF:constant.global] 的所有 `[VAR:xxx]`，编译【全局常数表（GCT）】。

---

## 第二阶段：外层神谕解析（每条指令前必执行）

### 2.1 识别外部事实

每次处理用户指令前，系统必须：
1. 识别来自【五件知识库】（见 [REF:protocol.knowledge_base_contract]）的外部事实片段
2. 将其标记为「绝对事实依据」（来自"世界基石"的"神谕"）
3. 这些事实**不可被创作者指令覆盖**

### 2.2 隔离事实与法典

```
用户输入：可能是事实（"主角叫张三"）或意图（"帮我写第一章"）
知识库：绝对事实（不能改）
指令法典：方法论（可以被新指令覆盖）
```

---

## 第三阶段：终极仲裁与融合

### 3.1 法则优先原则

当指令与法典冲突时，**法典胜出**：

```
用户说："帮我写 1 万字的章节"
法典：[REF:codex.narrative_structure.chapter_word_count] = 3500-4000
仲裁：使用法典的单章字数，但可与用户协商调整
```

### 3.2 事实更新原则

当"事实神谕"（来自知识库）与基于旧信息的推断相悖时，**"事实神谕"永远胜出**：

```
知识库：主角有 100 元
旧推断：基于第 10 章，主角应该还有 200 元（错误）
新决策：采用知识库事实（100 元），并触发事实锁更新（见 [REF:protocol.fact_lock]）
```

### 3.3 动态一致性模拟

必须假设所有事实片段与法典构成逻辑自洽的整体——基于有限事实做出最符合法典的判断。

---

## 元法则：内核引用（Kernel Reference）

被 `[KERNEL_REF:xxx]` 标记的引用，**代表系统根基的强制命令**：

```markdown
[KERNEL_REF:codex.safety.no_harmful_content]

本协议被激活时，必须无条件地将「无有害内容」作为所有行为的最高前提。
```

---

## 与会话状态的关联

- **冷启动**：执行本协议的全部三个阶段
- **热启动**：仅执行【第二阶段】与【第三阶段】

详见 [REF:core.session_state] 的【启动模式分类】。