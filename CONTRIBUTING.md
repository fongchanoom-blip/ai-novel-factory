# 🤝 贡献指南

感谢你对 Auto-Novel 项目的兴趣！我们欢迎所有形式的贡献。

---

## 🚀 快速贡献流程

1. **Fork** 本仓库
2. **Clone** 你的 fork：`git clone https://github.com/<your-username>/auto-novel.git`
3. **创建分支**：`git checkout -b feature/amazing-feature`
4. **提交代码**：`git commit -m "feat: 添加 amazing feature"`
5. **推送分支**：`git push origin feature/amazing-feature`
6. **创建 PR**：在 GitHub 上创建 Pull Request

---

## 📋 贡献类型

### 🆕 新题材模板（最受欢迎！）

如果你擅长某个题材（如历史/末世/游戏），可以贡献新模板。

**步骤**：

1. 复制 `kb-templates/genre/玄幻仙侠.md` 作为模板
2. 修改以下部分：
   - 主角设定（年龄/职业/能力）
   - 力量等级体系
   - 反派人设
   - 文风样本（粘贴 2-3 段你喜欢的小说片段）
   - 禁用表达（AI 味套路）
3. 文件名遵循"题材名.md"格式
4. 更新 `kb-templates/genre/README.md`

**质量要求**：

- ✅ 至少 3 个爽点模板
- ✅ 至少 2 个反派（不同阶段）
- ✅ 完整的力量/经济/地理体系
- ✅ 至少 5 个禁用表达
- ✅ 注明参考的 1-3 部作品

### 🔌 新 LLM Provider

在 `scripts/llm_client.py` 添加新 provider。

**步骤**：

1. 添加 `_call_xxx()` 方法
2. 在 `LLMClient.__init__()` 中添加配置项
3. 更新 `PRICING` 表
4. 测试：`python3 scripts/llm_client.py`

### 🐛 Bug 修复

1. 在 Issues 中找到对应的 bug（或创建一个）
2. Fork + 修复 + 测试
3. PR 时关联 Issue 编号

### 📚 文档改进

- 修正错别字
- 补充例子
- 翻译成其他语言

---

## 🔧 开发环境

### 依赖

- Python 3.9+
- PyYAML（知识库 YAML 解析）
- Gradio（Web 界面）

### 本地设置

```bash
# 克隆仓库
git clone https://github.com/<your-org>/auto-novel.git
cd auto-novel

# 安装依赖
pip install pyyaml gradio

# 运行测试
python3 scripts/metadata_validator.py .

# 启动 Web 界面
cd web
python3 app.py
```

---

## 📐 代码规范

### Python

- 遵循 PEP 8
- 函数和类加 docstring
- 关键逻辑加注释
- 新脚本要有 `argparse` CLI 入口

### Markdown

- 协议文件 frontmatter 包含：
  ```yaml
  ---
  ID: protocol.xxx
  SCOPE: protocol
  LOAD: hot | cold | both
  PRIORITY: 1-10
  TRIGGER: 「触发词」
  PHASE: boot | process | entry | error_handling | assist
  VERSION: v1.0.0
  UPDATED: YYYY-MM-DD
  ---
  ```
- 文件名：小写 + 连字符
- 章节使用 `##` `###` 而非 `**` 加粗

### 提交信息

使用 [Conventional Commits](https://www.conventionalcommits.org/)：

```
feat: 新增 xxx
fix: 修复 xxx
docs: 文档更新 xxx
style: 格式化（不影响代码）
refactor: 重构
test: 测试
chore: 构建/工具变更
```

---

## 🧪 测试要求

PR 必须包含：

1. **新功能**：手动测试 + 截图/日志
2. **Bug 修复**：原 bug 复现 + 修复后结果
3. **协议修改**：更新 `metadata_validator.py` 验证通过

CI 会自动运行：

- 语法检查（所有 .py 文件）
- `--help` 输出（所有 scripts）
- Web 界面导入测试
- 元数据验证

---

## 📜 行为准则

请阅读 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

核心原则：

- 友善、尊重、专业
- 假设对方出于善意
- 接受建设性批评
- 关注对社区最有利的事

---

## ❓ 提问

- 💬 **Discussion**：在 [GitHub Discussions](https://github.com/<your-org>/auto-novel/discussions) 提问
- 🐛 **Bug**：在 [GitHub Issues](https://github.com/<your-org>/auto-novel/issues) 创建 bug report
- 💡 **功能建议**：在 Issues 中用 `feature_request` 模板
- 📧 **私人联系**：参见 GitHub 主页

---

## 🙏 致谢

每个贡献者都会被记录在 [CONTRIBUTORS.md](CONTRIBUTORS.md)。

---

**再次感谢你的贡献！** 🎉