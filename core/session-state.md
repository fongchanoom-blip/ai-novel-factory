---
ID: core.session_state
SCOPE: core
LOAD: both
PRIORITY: 9
PHASE: process
VERSION: v1.0.0
UPDATED: 2026-08-20
---

# 会话状态维持协议（Session State Protocol）

[REF:core.session_state]

## 状态烙印机制

### 初始化烙印

当系统首次成功执行「初始化」指令后，在内部创建：

```
[状态: 已唤醒 | Auto-Novel v1.0 | 宪章版本: v1.0.0]
[知识库: <已绑定 N 件 / 待补 M 件>]
[能力状态: <根据知识库缺失输出>]
```

代表系统核心人格和操作系统已成功加载并内化。

### 状态自检

每条指令处理前，必须先进行一次快速的内部状态自检。

---

## 启动模式分类

### 热启动（Hot Start）

**触发场景**：用户在同一会话中下达连续指令时。

**跳过内容**：
- [REF:core.boot.sequence] 的【第一阶段：元标签解析】
- [REF:core.boot.sequence] 的【第二阶段：知识库契约确认】（仅检查变更）

**保留执行**：
- [REF:core.arbitration] 的【第二阶段：外层神谕解析】
- [REF:core.arbitration] 的【第三阶段：终极仲裁与融合】
- 按 `TRIGGER` 路由加载相应的 `protocols/` 文件

### 冷启动 / 重载（Cold Start / Reload）

**触发场景**：
1. 用户首次说"开始创作"或"初始化"
2. 新会话开启且无状态烙印
3. 用户说"重置"或"重新初始化"
4. 检测不到状态烙印

**执行内容**：完整重新执行 [REF:core.boot.sequence] 与 [REF:core.arbitration] 的全部阶段。

---

## 状态变更触发条件

| 触发事件 | 状态变化 | 后续行为 |
|---|---|---|
| 首次「初始化」 | 无 → 已唤醒 | 完成完整冷启动后转入热启动 |
| 「重置」 | 已唤醒 → 重启 | 强制冷启动 |
| 「重新初始化」 | 已唤醒 → 重启 | 强制冷启动 + 重新读取知识库 |
| 知识库版本变更 | 已唤醒 → 重启 | 自动冷启动并更新烙印版本号 |
| 触发 FATAL_ERROR | 已唤醒 → 冻结 | 暂停所有创作型指令 |

---

## 状态信息存储

### 当前会话状态

```yaml
status:
  state: 已唤醒 | 重启 | 冻结
  novel_version: v1.0.0
  charter_version: v1.0.0
  knowledge_base:
    world_foundation: 已绑定 | 缺失
    world_rules: 已绑定 | 缺失
    character_profiles: 已绑定 | 缺失
    event_archive: 已绑定 | 缺失
    style_samples: 已绑定 | 缺失
  capabilities:
    topic: 可用
    outline: 可用 | 降级
    toc: 可用 | 禁止
    draft: 可用 | 禁止
    write: 可用 | 禁止
    review: 可用 | 降级
    archive: 可用
  progress:
    current_phase: 选题 | 大纲 | 目录 | 草案 | 正文 | 质检 | 存档
    current_volume: 0
    current_chapter: 0
    total_words: 0
```

---

## 与仲裁协议的依赖关系

本协议是 [REF:core.arbitration] 的**前置开关**：
- 仅当本协议判定为「冷启动」时，仲裁协议的【第一阶段】才被激活
- 「热启动」状态下，仲裁协议从【第二阶段】开始执行