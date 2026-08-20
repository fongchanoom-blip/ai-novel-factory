# 📖 Auto-Novel · 让 AI 写小说变简单

> **你只需想故事，AI 帮你写到 100 万字不崩设定。**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.7-green.svg)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org)
[![Protocols](https://img.shields.io/badge/protocols-17-blue)](protocols/)
[![Genre Templates](https://img.shields.io/badge/genre_templates-5-orange)](kb-templates/genre/)
[![LLM Providers](https://img.shields.io/badge/llm_providers-4-purple)](scripts/llm_client.py)

---

## 📖 项目说明

> **Auto-Novel Skill** 是一个**开源的 AI 中文长篇创作工具**，整合 6 个主流 AI 写作 skill 的核心机制，提供从选题、大纲、章节生成到评分、修订单一站式工程化流程。

**核心定位**：
- 🎯 **不是 AI 替代作者**——是 AI **辅助**作者的工具
- 🏗️ **协议化**——17 个独立协议，可按需加载，节省 50-70% token
- 📦 **离线可用**——基础评分和事实提取基于规则，无需 API Key
- 🔌 **可扩展**——4 个 LLM provider + 5 套题材模板 + Web 界面

**适用读者**：
- ✅ 网文作者（玄幻/都市/言情/悬疑/科幻）
- ✅ 写作爱好者（想用 AI 辅助但担心一致性）
- ✅ AI 研究者（想研究 AI 在长篇创作中的应用）
- ✅ 工具开发者（想基于此 fork 自定义版本）

**授权协议**：MIT License（可商用、可修改、可分发）

---

## 这是什么？

**Auto-Novel** 是一个基于协议（protocol-based）的中文长篇 AI 创作 Skill。

它把小说创作拆解为 **9 个快捷入口** + **17 个独立协议** + **7 个自动化工具**，让你专注想故事，AI 帮你处理一致性问题。

---

## 🎯 核心特性

### 1️⃣ 9 个快捷入口（无需记命令）

| 入口 | 功能 |
|------|------|
| `/novel:demo` | 30 秒看 AI 能做什么 |
| `/novel:quick` | 快速试写（不需准备）|
| `/novel:new` | 从零开始正式创作 |
| `/novel:continue` | 继续写下一章 |
| `/novel:fix` | 优化/修改/去 AI 味 |
| `/novel:submit` | 投稿/分析/签约准备 |
| `/novel:stuck` | 卡文急救 |
| `/novel:daily` | 日更管理 |
| `/novel:cowrite` | AI 共写（你一句我一句）|

### 2️⃣ 17 个独立协议

每个协议是**可独立加载的 markdown 文档**——比"巨型 prompt"节省 50-70% 的 token。

- **核心层**（3）：boot / arbitration / session_state
- **核心创作流程**（5）：topic-selection / outline / toc / draft / write
- **一致性保证**（4）：knowledge-base-contract / context-assembly / fact-lock / quality-scoring
- **入口与路由**（6）：entry-routing / demo / quick / stuck / daily / cowrite
- **创新与体验**（2）：innovation-modules / friendly-errors

### 3️⃣ 5 大流派模板（v1.0.7 新增）

| 题材 | 平台 |
|------|------|
| 🏯 **玄幻仙侠** | 起点/番茄 |
| 🏙️ **都市现代** | 起点/番茄/晋江 |
| 💕 **言情古风** | 晋江/起点女生 |
| 🔍 **悬疑推理** | 知乎盐选/起点 |
| 🚀 **科幻未来** | 起点/番茄 |

### 4️⃣ 5 维评分体系

每章自动评分（无需 LLM 也可运行）：
- **人设一致性**（OOC，30%）
- **世界观一致性**（Lore，25%）
- **逻辑性**（20%）
- **文风一致性**（Style，15%）
- **非重复性**（Non-Repetition，10%）

### 5️⃣ LLM 接入（v1.0.6 新增）

支持 4 个 provider，**自动 fallback 到规则版**：

| Provider | 模型 | 价格 |
|----------|------|------|
| **DeepSeek**（推荐）| deepseek-chat | ¥0.001/1K |
| **Anthropic Claude** | claude-3-5-sonnet | $0.015/1K |
| **OpenAI** | gpt-4o-mini | $0.0006/1K |
| **智谱 GLM** | glm-4-flash | **免费** |

---

## 🚀 快速开始

### 安装

```bash
# 方式 1：作为 Hermes skill 安装（推荐）
git clone https://github.com/<your-org>/auto-novel.git
cp -r auto-novel/ ~/.hermes/profiles/cont/skills/auto-novel/

# 方式 2：作为 Python 包安装
pip install auto-novel
```

### 30 秒体验

```bash
cd examples/demo-novel
python3 -m auto_novel.demo
```

### 创建新项目

```bash
# 命令行
python3 scripts/kb_manager.py ~/my-novel init --genre 玄幻仙侠

# 或启动 Web 界面
cd web
python3 app.py
# 浏览器打开 http://localhost:7860
```

---

## 📦 项目结构

```
auto-novel/
├── core/             # 3 个核心协议
├── protocols/        # 17 个独立协议
├── constants/        # 全局常数
├── references/       # 13 模块方法论库
├── kb-templates/     # 11 个知识库模板（含 5 套题材）
├── scripts/          # 7 个自动化脚本
├── web/              # Gradio Web 界面
├── examples/         # 示例项目
├── docs/             # 详细文档
├── LICENSE           # MIT 许可证
├── CONTRIBUTING.md   # 贡献指南
└── ROADMAP.md        # 路线图
```

---

## 📚 文档导航

- 🚀 **新用户**：[docs/QUICKSTART.md](docs/QUICKSTART.md)
- 🎨 **题材模板**：[kb-templates/genre/README.md](kb-templates/genre/README.md)
- 🤖 **LLM 配置**：[docs/LLM_SETUP.md](docs/LLM_SETUP.md)
- 🔧 **API 文档**：[docs/API.md](docs/API.md)
- 🤝 **贡献**：[CONTRIBUTING.md](CONTRIBUTING.md)
- 🗗 **规划**：[ROADMAP.md](ROADMAP.md)

---

## 🌟 借鉴的开源项目

本项目的设计灵感来自以下优秀项目（按借鉴深度排序）：

- [tianming-skill](https://github.com/zy-zmc/tianming-skill) — 元标签体系 + 协议模式
- [chinese-longnovel-skill](https://github.com/xiaofeng-928/chinese-longnovel-skill) — 中文长篇 50 章规划
- [PhosAQy/novel-skills](https://github.com/PhosAQy/novel-skills) — 5 维评分 + 大纲权威性
- [chinese-webnovel-skills](https://github.com/tance-mang/chinese-webnovel-skills) — 4 大门入口 + 草稿模式
- [vibe-noveling](https://github.com/lbjjin/vibe-noveling) — 剧情爆破 / 掀桌模式
- [Distilled-Novel-Toolbox](https://github.com/dama-cyber/Distilled-Novel-Toolbox) — 13 模块方法论库

---

## 📊 状态

- ✅ **v1.0.7** 已发布
- ✅ 17 个协议 + 7 个脚本 + Web 界面
- ✅ 5 套题材模板
- ✅ 4 个 LLM provider
- ✅ CI/CD 自动化测试
- 🚧 **v1.1.0**：白嫖版（更多免费 LLM）+ 作家社区

---

## 🤝 贡献

欢迎贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

可以贡献的方向：
- 🆕 新题材模板（历史/军事/末世/校园/体育/游戏）
- 🔌 新 LLM provider 接入
- 🐛 Bug 修复
- 📚 文档改进
- 🌍 国际化（英文/日文/繁体）

---

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

---

## ⭐ Star History

如果这个项目对你有帮助，请给个 ⭐！你的支持是项目持续发展的动力。

[![Star History Chart](https://api.star-history.com/svg?repos=<your-org>/auto-novel&type=Date)](https://star-history.com/#<your-org>/auto-novel)