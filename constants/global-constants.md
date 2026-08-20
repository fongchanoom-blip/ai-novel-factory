---
ID: constant.global
SCOPE: constant
LOAD: both
PRIORITY: 10
VERSION: v1.0.0
UPDATED: 2026-08-20
---

# 全局常数表（Global Constants Table）

[REF:constant.global]

本文件定义 Auto-Novel Skill 的所有全局常量。所有协议文件中可使用 `[VAR:xxx]` 引用。

---

## 一、字数与篇幅

[VAR:short_story_word_min] = 8000
[VAR:short_story_word_max] = 30000
[VAR:short_story_draft_min] = 10000
[VAR:short_story_draft_max] = 20000
[VAR:long_novel_chapter_word_min] = 3000
[VAR:long_novel_chapter_word_max] = 4000
[VAR:long_novel_volume_word_min] = 250000
[VAR:long_novel_volume_word_max] = 350000
[VAR:long_novel_min_chapters] = 100
[VAR:long_novel_max_chapters] = 500

---

## 二、规划粒度

[VAR:planning_chapter_per_session] = 30  # 每次目录规划 30 章
[VAR:planning_volume_default_count] = 3  # 默认 3 卷
[VAR:planning_golden_three_chapters] = 3  # 黄金三章
[VAR:planning_min_outline_layers] = 3  # 大纲三层结构

---

## 三、质量评分

[VAR:quality_auto_pass_score] = 9.0  # 5 维评分 ≥9.0 自动通过
[VAR:quality_manual_review_score] = 7.0  # 7-0-8.9 人工复审
[VAR:quality_reject_score] = 7.0  # <7.0 触发重写

[VAR:quality_weight_ooc] = 30  # 人设一致性权重（%）
[VAR:quality_weight_lore] = 25  # 世界观一致性权重（%）
[VAR:quality_weight_logic] = 20  # 逻辑权重（%）
[VAR:quality_weight_style] = 15  # 文风一致性权重（%）
[VAR:quality_weight_repetition] = 10  # 非重复性权重（%）

---

## 四、AI 味阈值

[VAR:ai_smell_index_max] = 10  # AI 味指数范围 0-10
[VAR:ai_smell_human_like_max] = 3  # 0-3 像真人
[VAR:ai_smell_semi_finished_max] = 6  # 4-6 半成品
[VAR:ai_smell_metaphor_density_per_kchar] = 3  # 比喻密度 ≤3/千字
[VAR:ai_smell_consecutive_same_pattern_max] = 2  # 连续同句式 ≤2 句
[VAR:ai_smell_extreme_word_per_kchar] = 3  # 极端词 ≤3/千字
[VAR:ai_smell_high_freq_emotion_word_per_chapter] = 1  # 高频情绪词 ≤1/章

---

## 五、伏笔管理

[VAR:foreshadowing_max_unclaimed_chapters] = 30  # 伏笔超期 30 章触发警告
[VAR:foreshadowing_priority_layers] = 4  # 4 层追踪（细纲/总结/摘要/追踪表）

---

## 六、知识库契约

[VAR:knowledge_base_files_required] = 5  # 五件知识库
[VAR:knowledge_base_files_essential_for_write] = 5  # 五件全部必需才能写正文
[VAR:knowledge_base_files_essential_for_toc] = 4  # 4 件必需才能生成目录
[VAR:knowledge_base_files_essential_for_draft] = 3  # 3 件必需才能生成草案

---

## 七、安全与合规

[VAR:safety_no_harmful_content] = true  # 绝对禁止
[VAR:safety_compliance_required] = ["无色情", "无暴力恐怖", "无政治敏感", "无AI违规词"]
[VAR:safety_max_retries_on_block] = 3  # 触发安全拦截时最多重试次数

---

## 八、文件命名规范

[VAR:naming_draft_prefix] = "修改"  # 草稿文件名前缀
[VAR:naming_archive_prefix] = "存档"  # 存档文件名前缀
[VAR:naming_chapter_pattern] = "第{X}章"  # 章标题格式
[VAR:naming_volume_pattern] = "卷{X}"  # 卷标题格式

---

## 九、调度与节奏

[VAR:schedule_aggressive_targets_per_session] = 5  # 每会话高产目标章节数
[VAR:schedule_default_targets_per_session] = 2  # 每会话默认目标
[VAR:schedule_conservative_targets_per_session] = 1  # 每会话保守目标

---

## 十、引用关系表

```
协议文件清单：
├─ core.boot.sequence       → core/boot-sequence.md
├─ core.arbitration         → core/arbitration.md
├─ core.session_state       → core/session-state.md
├─ protocol.outline         → protocols/outline.md
├─ protocol.planner         → protocols/planner.md
├─ protocol.toc             → protocols/toc.md
├─ protocol.draft           → protocols/draft.md
├─ protocol.write           → protocols/write.md
├─ protocol.review          → protocols/review.md
├─ protocol.archive         → protocols/archive.md
├─ codex.consistency        → codex/consistency.md
├─ codex.narrative_structure → codex/narrative-structure.md
├─ codex.safety             → codex/safety.md
├─ constant.global          → constants/global-constants.md
└─ auto-novel.META_TAGS     → META_TAGS.md
```

---

## 十一、版本演进

| 版本 | 日期 | 关键变更 |
|------|------|----------|
| v1.0.0 | 2026-08-20 | 初始版本（基于 tianming-skill v2.0.0 + MyNovel + PhosAQy + webnovel-skills） |