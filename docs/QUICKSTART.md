# 🚀 快速开始指南

> 5 分钟跑通 Auto-Novel。

---

## 30 秒体验

```bash
cd examples/demo-novel
python3 -m auto_novel.demo
```

---

## 完整流程（5 分钟）

### Step 1：安装（30 秒）

```bash
# 方式 1：从 GitHub 克隆
git clone https://github.com/<your-org>/auto-novel.git
cd auto-novel
pip install -e .

# 方式 2：仅使用脚本（无需安装）
git clone https://github.com/<your-org>/auto-novel.git
cd auto-novel
pip install pyyaml gradio
```

### Step 2：创建项目（1 分钟）

```bash
# 创建项目（自动生成 5 件知识库 + 题材模板）
auto-novel init ~/my-novel --genre 玄幻仙侠

# 或手动
python3 scripts/kb_manager.py ~/my-novel init --genre 玄幻仙侠
```

会生成：

```
~/my-novel/
├── 世界基石.md        ← 主角状态
├── 世界观规则.md      ← 力量体系
├── 角色档案.md        ← 人物设定
├── 档案事件.md        ← 事件追踪
├── 文风样本.md        ← 文风参考
└── 题材设定.md        ← 玄幻仙侠专用设定
```

### Step 3：填写知识库（2 分钟）

打开 `角色档案.md`，修改：

```yaml
主角:
  姓名: 张三
  年龄: 17
  修为: 练气期
  ...
```

### Step 4：生成章节（1 分钟）

```bash
# 命令行
python3 scripts/chapter_scorer.py ~/my-novel/chapter_001.md

# 或 Web 界面
auto-novel web
# 浏览器打开 http://localhost:7860
```

### Step 5：查看结果

评分报告：

```
总评: 8.82 ⚠️ review
  人设一致性 (30%): 10.0/10 ✅
  世界观一致性 (25%): 10.0/10 ✅
  逻辑性 (20%): 6.0/10 ❌
  文风一致性 (15%): 9.0/10 ✅
  非重复性 (10%): 9.0/10 ✅
```

---

## 🎯 常用命令

```bash
# 验证协议元数据
python3 scripts/metadata_validator.py .

# 启动 Web 界面
python3 web/app.py

# 评分章节
python3 scripts/chapter_scorer.py chapter.md

# 提取事实
python3 scripts/fact_extractor.py chapter.md --project-dir ~/my-novel

# 组装 7 层上下文
python3 scripts/context_assembler.py ~/my-novel --chapter 5

# LLM 增强评分（需要 API Key）
python3 scripts/chapter_scorer_llm.py chapter.md --mode hybrid
```

---

## ⚙️ 配置 LLM

```bash
# 设置环境变量（推荐）
export DEEPSEEK_API_KEY=sk-xxx
export ANTHROPIC_API_KEY=sk-ant-xxx

# 或在 Web 界面配置
auto-novel web
# 切换到"🤖 LLM 配置"标签页
```

详见 [LLM_SETUP.md](LLM_SETUP.md)。

---

## 🎨 选择题材

```bash
# 玄幻仙侠
auto-novel init ~/my-xuanhuan --genre 玄幻仙侠

# 都市现代
auto-novel init ~/my-dushi --genre 都市现代

# 言情古风
auto-novel init ~/my-yanqing --genre 言情古风

# 悬疑推理
auto-novel init ~/my-xuanyi --genre 悬疑推理

# 科幻未来
auto-novel init ~/my-keji --genre 科幻未来
```

详见 [kb-templates/genre/README.md](../kb-templates/genre/README.md)。

---

## ❓ 常见问题

### Q: 没有 API Key 能用吗？

**A: 能！** 所有 scripts 都基于规则，无需 LLM。

LLM 增强是可选的，用于更准确的事实提取和评分。

### Q: 在哪里找 API Key？

- DeepSeek：https://platform.deepseek.com
- 智谱 GLM：https://open.bigmodel.cn（**有免费模型**）
- Claude：https://console.anthropic.com
- OpenAI：https://platform.openai.com

### Q: 项目文件在哪？

默认在 `~/auto-novel-projects/<项目名>/`。

---

## 🚀 下一步

- 阅读 [README.md](../README.md) 了解完整功能
- 查看 [ROADMAP.md](../ROADMAP.md) 了解未来计划
- 加入社区参与贡献