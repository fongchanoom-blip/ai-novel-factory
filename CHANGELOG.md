# Changelog

所有项目的版本变更都会记录在此文件。

格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，
版本遵循 [Semantic Versioning](https://semver.org/spec/v2.0.0.html)。

---

## [1.0.7] - 2026-08-20 — 题材模板版

### 新增

- 5 套题材专用模板（kb-templates/genre/）
  - 玄幻仙侠（8.6 KB）
  - 都市现代（6.9 KB）
  - 言情古风（7.1 KB）
  - 悬疑推理（7.8 KB）
  - 科幻未来（7.9 KB）
- 题材总览 README，含题材选择指南 + 爽点速查表
- `kb_manager.py --genre` 参数支持

### 修改

- `scripts/kb_manager.py`：`init_templates()` 新增 `genre` 参数 + CLI `--genre` 选项
- `scripts/kb_manager.py`：自动创建项目目录

---

## [1.0.6] - 2026-08-20 — LLM 增强版

### 新增

- 统一 LLM 客户端（`scripts/llm_client.py`），支持 4 个 provider：
  - DeepSeek（推荐，性价比高）
  - Anthropic Claude
  - OpenAI
  - 智谱 GLM（有免费模型）
- LLM 增强评分器（`scripts/chapter_scorer_llm.py`）
- LLM 增强事实提取器（`scripts/fact_extractor_llm.py`）
- Web 界面新增"🤖 LLM 配置"标签页（5 标签页）

### 修改

- Web 界面集成 LLM 辅助函数（`web/llm_settings.py`）

---

## [1.0.5] - 2026-08-20 — Web 集成 scripts 版

### 新增

- Web 界面与 scripts/ 自动化脚本深度集成
- 真实项目管理 UI（移除演示数据 `ProjectStore`）

---

## [1.0.4] - 2026-08-20 — 自动化脚本版

### 新增

- 5 个自动化脚本：
  - `metadata_validator.py` — 验证协议元数据
  - `kb_manager.py` — 5 件知识库管理
  - `fact_extractor.py` — 事实提取（规则版）
  - `chapter_scorer.py` — 5 维评分（规则版）
  - `context_assembler.py` — 7 层上下文组装

---

## [1.0.3] - 2026-08-20 — Web 界面版

### 新增

- Gradio Web 界面
- 4 大功能页面：项目仪表盘 / 章节生成 / 5 维评分 / 创作辅助

---

## [1.0.2] - 2026-08-20 — 核心创作流程版

### 新增

- 5 个核心创作协议：
  - `topic-selection`（选题）
  - `outline`（大纲）
  - `toc`（章节目录）
  - `draft`（章节草案）
  - `write`（正文写作）

---

## [1.0.1] - 2026-08-20 — 小白友好性增强版

### 新增

- 5 个快捷入口：demo / quick / stuck / daily / cowrite
- 友好错误信息协议
- README 重写加电梯演讲 + 5 分钟上手教程

---

## [1.0.0] - 2026-08-20 — 初始版本

### 新增

- 整合 6 个主流 skill 的核心机制：
  - tianming-skill（元标签体系）
  - MyNovel（事实锁 + SHA-256）
  - PhosAQy（5 维评分）
  - chinese-webnovel-skills（4 大门入口）
  - vibe-noveling（剧情爆破）
  - Distilled-Novel-Toolbox（13 模块方法论）

[1.0.7]: https://github.com/<your-org>/auto-novel/releases/tag/v1.0.7
[1.0.6]: https://github.com/<your-org>/auto-novel/releases/tag/v1.0.6
[1.0.5]: https://github.com/<your-org>/auto-novel/releases/tag/v1.0.5
[1.0.4]: https://github.com/<your-org>/auto-novel/releases/tag/v1.0.4
[1.0.3]: https://github.com/<your-org>/auto-novel/releases/tag/v1.0.3
[1.0.2]: https://github.com/<your-org>/auto-novel/releases/tag/v1.0.2
[1.0.1]: https://github.com/<your-org>/auto-novel/releases/tag/v1.0.1
[1.0.0]: https://github.com/<your-org>/auto-novel/releases/tag/v1.0.0