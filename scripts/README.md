# Auto-Novel Skill · 自动化脚本

> 让所有协议从"文档描述"变"实际运行"。

---

## 📦 5 个核心脚本

| 脚本 | 功能 | 大小 |
|------|------|------|
| `metadata_validator.py` | 验证协议文件元数据完整性 | 4.2 KB |
| `kb_manager.py` | 管理 5 件知识库 + 能力降级 | 6.5 KB |
| `fact_extractor.py` | 从章节提取事实锁 | 13.7 KB |
| `chapter_scorer.py` | 5 维评分（无需 LLM）| 14.8 KB |
| `context_assembler.py` | 组装 7 层上下文 | 11.6 KB |

---

## 🚀 快速开始

### 安装依赖

所有脚本**仅用 Python 标准库**，无需安装第三方包。

```bash
# Python 3.8+
python3 --version
```

### 验证 skill 元数据

```bash
cd ~/.hermes/profiles/cont/skills/auto-novel/scripts
python3 metadata_validator.py ~/.hermes/profiles/cont/skills/auto-novel
```

**输出**：
```
✅ 所有协议文件元数据完整
协议文件总数: 17
完整 (宽松): 17
缺少必填字段: 0
```

### 管理 5 件知识库

```bash
# 初始化（从模板复制 5 件）
python3 kb_manager.py ~/my-novel init

# 检查状态
python3 kb_manager.py ~/my-novel status

# 验证完整性
python3 kb_manager.py ~/my-novel validate

# 列出缺失
python3 kb_manager.py ~/my-novel missing
```

### 提取事实锁

```bash
python3 fact_extractor.py ~/my-novel/chapter_001.md \
  --project-dir ~/my-novel
```

**输出**：
```
✅ 提取到 4 条事实
新增事实: 4
冲突事实: 0

📁 输出位置：
   active/    ← 当前事实
   superseded/  ← 已替代
   contested/  ← 有冲突
```

### 5 维评分

```bash
python3 chapter_scorer.py ~/my-novel/chapter_001.md \
  --project-dir ~/my-novel
```

**输出**：
```
【5 维评分结果】
总评: 8.82 ⚠️ review

人设一致性 (30%): 10.0/10
  ✅ 对话长度合理
  ...
世界观一致性 (25%): 10.0/10
  ...
逻辑性 (20%): 6.0/10
  ❌ 因果连接词不足
  ...
```

### 组装 7 层上下文

```bash
python3 context_assembler.py ~/my-novel --chapter 5
```

**输出**：完整的 7 层 JSON（项目元数据 + 章节契约 + 主角状态 + 阶段规划 + 最近 3 章 + 摘要 + 文风样本）

---

## 🧪 测试项目

```bash
# 测试场景
mkdir -p /tmp/test-project
python3 kb_manager.py /tmp/test-project init
```

输出应该显示 5 个文件创建成功。

---

## 📋 详细说明

### metadata_validator.py

**输入**：skill 目录
**输出**：每个协议文件的元数据完整度

**检查字段**：
- 必填：`ID`, `SCOPE`, `LOAD`
- 推荐：`PRIORITY`, `TRIGGER`, `PHASE`, `VERSION`

**用法**：
```bash
python3 metadata_validator.py <skill_dir>
python3 metadata_validator.py <skill_dir> --strict  # 严格模式
```

### kb_manager.py

**5 件知识库清单**：

| 文件 | 内容 | 自动必填 |
|------|------|----------|
| 世界基石.md | 主角当前状态 + 主线进度 | 否（系统自动维护）|
| 世界观规则.md | 力量体系 + 经济 + 地理 + 社会 | 是 |
| 角色档案.md | 主角 + 配角 + 反派 | 是 |
| 档案事件.md | 已发生事件（用于一致性核查）| 是 |
| 文风样本.md | 写作风格样本 | 是 |

**能力降级表**：

| 能力 | 必需文件 | 缺失时 |
|------|----------|--------|
| 选题 | 无 | ✅ 仍可用 |
| 大纲 | 世界观规则 | ⚠️ 降级 |
| 目录 | 4 件 | ❌ 禁止 |
| 草案 | 3 件 | ❌ 禁止 |
| 正文 | **5 件全** | ❌ 任一缺失禁止 |

**子命令**：
- `init` —— 从模板复制 5 件
- `status` —— 检查状态 + 能力评估
- `validate` —— 验证完整性
- `missing` —— 列出缺失

### fact_extractor.py

**8 大事实类别**：

| 类别 | 示例 |
|------|------|
| resources（资源）| "100 灵石" |
| time（时间）| "凌晨"、"3 天后" |
| location（地点）| "青云宗" |
| character_knowledge（角色认知）| "张三发现真相" |
| information_propagation（信息传播）| "师父告诉张三" |
| powers（能力）| "筑基期三层"、"每日 3 次" |
| identity（身份）| "天灵根" |
| injuries（伤势）| "右臂中毒" |

**冲突检测**：
- 数字冲突 → 标记 `contested`
- 状态冲突 → 标记 `contested`
- 知识冲突 → 标记 `contested`

**输出**：YAML 格式的事实锁文件，含 SHA-256 哈希

### chapter_scorer.py

**5 维评分（基于规则，无需 LLM）**：

| 维度 | 权重 | 检查项 |
|------|------|--------|
| 人设一致性 | 30% | 对话长度 / 心理活动 / 情绪铺垫 |
| 世界观一致性 | 25% | 力量等级 / 资源数字 / 地理距离 |
| 逻辑性 | 20% | 因果连接 / 时间线 / 动机 |
| 文风一致性 | 15% | AI 味信号 / 禁用表达 / 段落长度 |
| 非重复性 | 10% | 句式变化 / 形容词 / 爽点密度 |

**阈值**：
- ≥ 9.0：自动通过
- 7.0-8.9：人工复审
- < 7.0：触发重写

**注意**：当前为基于规则的简化版（不调用 LLM）。生产环境应接入 LLM 做深度评分。

### context_assembler.py

**7 层上下文**：

| Layer | 内容 |
|-------|------|
| 1 | 当前章节契约（must_happen / must_not_happen / ending_hook） |
| 2 | 主角状态仓库（name / realm / resources / location）|
| 3 | 当前 50 章规划（phase / progress / events）|
| 4 | 最近 3 章有效正文 |
| 5 | 摘要（最近 20 章 + 50 章阶段）|
| 6 | 当前章节需要的文风样本 |
| 7 | 项目元数据（title / genre / progress）|

**输出**：JSON 格式的上下文包，可直接喂给 LLM

---

## 🔗 与协议的关系

| 脚本 | 实现的协议 |
|------|----------|
| metadata_validator.py | `protocol.*` 元数据要求 |
| kb_manager.py | `protocol.knowledge_base_contract` |
| fact_extractor.py | `protocol.fact_lock` |
| chapter_scorer.py | `protocol.quality_scoring` |
| context_assembler.py | `protocol.context_assembly` |

---

## 🚧 未来工作

- [ ] LLM 接入（deep_score 模式）
- [ ] Web UI 集成（用脚本作为后端）
- [ ] 自动化测试套件
- [ ] CI/CD 集成
- [ ] 性能基准

---

## 📜 版本

**v1.0.0**（2026-08-20）—— 初始版本

所有脚本基于 Python 标准库（无第三方依赖），可在任何 Python 3.8+ 环境运行。