# 📚 API 文档

> Auto-Novel 的 Python API 接口。

---

## 快速开始

```python
from auto_novel import (
    get_skill_dir, get_protocols_dir,
    get_kb_templates_dir, get_scripts_dir
)

# 获取路径
skill_dir = get_skill_dir()
protocols_dir = get_protocols_dir()

print(f"Skill 目录: {skill_dir}")
print(f"协议目录: {protocols_dir}")
```

---

## 命令行

```bash
auto-novel init <project_dir> [--genre <genre>]
auto-novel score <chapter>
auto-novel web
```

---

## Python API

### 项目管理

```python
from scripts.kb_manager import init_templates, status, validate

# 初始化项目（创建 5 件知识库）
init_templates("~/my-novel", "/path/to/templates", genre="玄幻仙侠")

# 查看状态
status("~/my-novel")

# 验证完整性
validate("~/my-novel")
```

### 评分章节

```python
from scripts.chapter_scorer import ChapterScorer

scorer = ChapterScorer(project_dir="~/my-novel")
result = scorer.score_chapter(chapter_text, "chapter_001.md")

print(f"总评: {result.overall}")
print(f"状态: {result.status}")
```

### LLM 增强评分

```python
from scripts.chapter_scorer_llm import LLMEnhancedScorer

scorer = LLMEnhancedScorer(project_dir="~/my-novel", use_llm=True)
result = scorer.score_chapter(chapter_text, "chapter_001.md")
```

### 事实提取

```python
from scripts.fact_extractor import FactExtractor

extractor = FactExtractor(project_dir="~/my-novel")
facts = extractor.extract_from_chapter(Path("chapter_001.md"))

for fact in facts:
    print(f"{fact.id}: {fact.content} ({fact.category})")
```

### LLM 调用

```python
from scripts.llm_client import LLMClient

client = LLMClient()
response = client.call(
    prompt="写一段玄幻开篇",
    system="你是网文作者",
    max_tokens=1000,
    temperature=0.7
)
print(response)
```

---

## 📖 协议文件

协议文件是 markdown 格式，frontmatter 包含：

```yaml
---
ID: protocol.topic_selection
SCOPE: protocol
LOAD: both
PRIORITY: 8
TRIGGER: 「novel:new」/ 「novel:topic」/ 「选题」
PHASE: process
VERSION: v1.0.0
UPDATED: 2026-08-20
---
```

读取协议：

```python
from pathlib import Path

protocol_file = Path("protocols/topic-selection.md")
content = protocol_file.read_text(encoding="utf-8")

# 解析 frontmatter
import re
match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
frontmatter, body = match.groups()

# 解析 YAML
import yaml
meta = yaml.safe_load(frontmatter)

print(f"ID: {meta['ID']}")
print(f"触发词: {meta['TRIGGER']}")
```

---

## 🔧 完整示例

```python
"""完整的小说生成流程示例"""

from pathlib import Path
from scripts.kb_manager import init_templates
from scripts.context_assembler import ContextAssembler
from scripts.chapter_scorer import ChapterScorer
from scripts.fact_extractor import FactExtractor
from scripts.llm_client import LLMClient

# 1. 创建项目
project_dir = Path.home() / "my-novel"
init_templates(str(project_dir), "/path/to/templates", genre="玄幻仙侠")
print(f"✅ 项目创建: {project_dir}")

# 2. 组装上下文（喂给 LLM）
assembler = ContextAssembler(str(project_dir))
context = assembler.assemble(chapter_no=1, target_words=3500)
print(f"📋 上下文组装: {len(context)} tokens")

# 3. 调用 LLM 生成章节
client = LLMClient()
chapter_text = client.call(
    prompt=f"{context}\n\n请写第 1 章",
    max_tokens=7000
)

# 4. 保存章节
chapter_file = project_dir / "chapter_001.md"
chapter_file.write_text(chapter_text, encoding="utf-8")
print(f"💾 章节保存: {chapter_file}")

# 5. 提取事实
extractor = FactExtractor(str(project_dir))
facts = extractor.extract_from_chapter(chapter_file)
print(f"📌 提取事实: {len(facts)} 条")

# 6. 5 维评分
scorer = ChapterScorer(str(project_dir))
result = scorer.score_chapter(chapter_text, "chapter_001.md")
print(f"📊 评分: {result.overall} {result.status}")
```

---

## 📖 参见

- [QUICKSTART.md](QUICKSTART.md) — 5 分钟上手
- [LLM_SETUP.md](LLM_SETUP.md) — LLM 配置
- [README.md](../README.md) — 项目概览