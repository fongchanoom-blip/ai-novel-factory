# 🤖 LLM 配置指南

> 让 scripts 从"基础规则"升级到"LLM 增强"。

---

## 📊 支持的 Provider

| Provider | 模型 | 1K tokens 价格 | 推荐度 |
|----------|------|----------------|--------|
| **DeepSeek** | deepseek-chat | ¥0.001 | ⭐⭐⭐⭐⭐ |
| **智谱 GLM** | glm-4-flash | **免费** | ⭐⭐⭐⭐⭐ |
| **OpenAI** | gpt-4o-mini | $0.0006 | ⭐⭐⭐⭐ |
| **Anthropic Claude** | claude-3-5-haiku | $0.0008 | ⭐⭐⭐⭐ |
| **Anthropic Claude** | claude-3-5-sonnet | $0.015 | ⭐⭐⭐（贵但质量高）|

---

## 🚀 30 秒配置

### 方式 1：环境变量（推荐）

```bash
# DeepSeek（推荐，性价比最高）
export DEEPSEEK_API_KEY=sk-xxx

# 智谱 GLM（有免费模型）
export ZHIPU_API_KEY=your-key

# Anthropic Claude
export ANTHROPIC_API_KEY=sk-ant-xxx

# OpenAI
export OPENAI_API_KEY=sk-xxx
```

### 方式 2：Web 界面

```bash
python3 web/app.py
# 浏览器打开 http://localhost:7860
# 切换到"🤖 LLM 配置"标签页
```

在界面输入 API Key（仅保存在内存中）。

---

## 🧪 验证配置

```bash
python3 scripts/llm_client.py
```

输出：

```
🤖 Auto-Novel · LLM 客户端

当前配置：
  Provider: deepseek
  Model: deepseek-chat

API Key 状态：
  ✅ deepseek
  ❌ anthropic
  ❌ openai
  ✅ zhipu

测试调用：
  响应: 你好
```

---

## 💡 使用 LLM 增强

### 5 维评分（LLM 增强版）

```bash
python3 scripts/chapter_scorer_llm.py chapter_001.md --mode hybrid
```

3 种模式：

| 模式 | 说明 | 需要 API Key |
|------|------|-------------|
| `--mode rule` | 纯规则评分 | ❌ |
| `--mode hybrid` | 规则 + LLM 综合 | ✅ |
| `--mode llm` | 纯 LLM 评分 | ✅ |

### 事实提取（LLM 增强版）

```bash
python3 scripts/fact_extractor_llm.py chapter_001.md --project-dir ~/my-novel --mode hybrid
```

---

## 🔧 切换 Provider

```python
from scripts.llm_client import LLMClient

client = LLMClient()
client.set_provider("anthropic", "claude-3-5-haiku-20241022")
response = client.call("写一段玄幻开篇")
```

---

## 🔒 隐私

- ✅ API Key 仅存在环境变量或 Web 内存中
- ✅ LLM 缓存存在本地（`~/.auto-novel/llm_cache/`）
- ✅ LLM 调用日志存在 `/tmp/auto-novel-logs/`（**不提交到 Git**）
- ❌ Auto-Novel **不会**上传你的项目内容

---

## 💰 成本估算

假设一个中篇（30 万字，10 万章）：

| Provider | 总成本 |
|----------|--------|
| 智谱 GLM-4-Flash | **免费** |
| DeepSeek | ¥20-50 |
| GPT-4o-mini | $5-10 |
| Claude Haiku | $10-20 |
| Claude Sonnet | $50-150 |

**推荐**：开始用 GLM-4-Flash（免费），质量不够时切换到 DeepSeek。

---

## ❓ 常见问题

### Q: 没有 API Key 能用吗？

**A: 能！** 所有 scripts 都基于规则运行，只是 LLM 增强版无法工作。

### Q: 哪个 provider 最好？

**A: 看场景**：

- 中文长篇 → **DeepSeek**（性价比之王）
- 英文质量 → **Claude Sonnet**（质量最高）
- 完全免费 → **智谱 GLM-4-Flash**
- 综合最佳 → **GPT-4o-mini**

### Q: API Key 会泄露吗？

**A: 不会**。Auto-Novel 不上传任何内容，API Key 仅本地使用。

### Q: 如何重置？

```bash
unset DEEPSEEK_API_KEY
unset ANTHROPIC_API_KEY
unset OPENAI_API_KEY
unset ZHIPU_API_KEY
```

---

## 📚 参考

- DeepSeek API 文档：https://platform.deepseek.com/docs
- 智谱 GLM 文档：https://open.bigmodel.cn/dev/api
- Anthropic API 文档：https://docs.anthropic.com
- OpenAI API 文档：https://platform.openai.com/docs