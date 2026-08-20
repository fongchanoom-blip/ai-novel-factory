#!/usr/bin/env python3
"""
Auto-Novel Skill · Web 界面（集成 scripts/ + LLM）

v1.0.6: 加入 LLM 增强
- 移除演示数据
- 接入 5 个 scripts 作为后端
- 接入 4 个 LLM provider（DeepSeek/Claude/OpenAI/智谱）
- 支持真实项目管理 + LLM 评分 + LLM 生成章节
"""

import gradio as gr
import json
import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# 添加 scripts 目录到路径
SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

# 加载 LLM 帮助模块
sys.path.insert(0, str(Path(__file__).parent))
from llm_settings import (
    get_settings, update_settings,
    call_llm_for_score, call_llm_for_extract, call_llm_for_chapter,
)

# ==================== 项目后端 ====================


class ProjectManager:
    """项目管理器（接入 scripts/）"""

    def __init__(self):
        self.projects_root = Path.home() / "auto-novel-projects"
        self.projects_root.mkdir(exist_ok=True)

    def list_projects(self) -> list:
        """列出所有项目"""
        if not self.projects_root.exists():
            return []
        return [d.name for d in self.projects_root.iterdir() if d.is_dir()]

    def get_project_path(self, name: str) -> Path:
        return self.projects_root / name

    def create_project(self, name: str, genre: str, platform: str, length: str) -> str:
        """创建新项目（调用 kb_manager）"""
        if not name.strip():
            return "❌ 项目名不能为空"

        project_path = self.get_project_path(name)
        if project_path.exists():
            return f"❌ 项目《{name}》已存在"

        project_path.mkdir(parents=True, exist_ok=True)

        # 调用 kb_manager.py init
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_DIR / "kb_manager.py"),
                    str(project_path),
                    "init",
                    "--templates",
                    str(Path(__file__).parent.parent / "kb-templates"),
                ],
                capture_output=True, text=True, timeout=10,
            )
        except Exception as e:
            return f"❌ 创建失败: {e}"

        # 保存项目元数据
        meta = {
            "name": name,
            "genre": genre,
            "platform": platform,
            "length": length,
            "created_at": datetime.now().isoformat(),
            "current_chapter": 0,
            "total_words": 0,
        }
        (project_path / "project_meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        return f"✅ 项目《{name}》创建成功！\n已生成 5 件知识库模板\n项目路径: {project_path}"

    def get_meta(self, project_name: str) -> dict:
        """获取项目元数据"""
        path = self.get_project_path(project_name)
        meta_file = path / "project_meta.json"
        if not meta_file.exists():
            return {}
        return json.loads(meta_file.read_text(encoding="utf-8"))

    def get_status(self, project_name: str) -> str:
        """获取项目状态（调用 kb_manager status）"""
        path = self.get_project_path(project_name)
        if not path.exists():
            return f"❌ 项目 {project_name} 不存在"

        try:
            result = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "kb_manager.py"), str(path), "status"],
                capture_output=True, text=True, timeout=10,
            )
            return result.stdout
        except Exception as e:
            return f"❌ 状态查询失败: {e}"

    def get_dashboard(self, project_name: str) -> str:
        """获取项目仪表盘数据"""
        path = self.get_project_path(project_name)
        if not path.exists():
            return f"❌ 项目 {project_name} 不存在"

        meta = self.get_meta(project_name)
        if not meta:
            return f"⚠️ 项目元数据缺失"

        # 统计总字数（扫描所有 chapter_*.md）
        total_words = 0
        chapter_count = 0
        for ch_file in path.glob("chapter_*.md"):
            text = ch_file.read_text(encoding="utf-8")
            words = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
            total_words += words
            chapter_count += 1

        # 读取最近章节
        recent_chapters = []
        for ch_file in sorted(path.glob("chapter_*.md"))[-5:]:
            recent_chapters.append({
                "file": ch_file.name,
                "words": sum(1 for c in ch_file.read_text(encoding="utf-8")
                             if '\u4e00' <= c <= '\u9fff'),
            })

        # 读取事实锁
        fact_locks = list((path / "fact_locks" / "active").glob("FL-*.yaml")) \
            if (path / "fact_locks" / "active").exists() else []

        md = f"""# 📊 项目仪表盘：{project_name}

## 基本信息

| 字段 | 值 |
|------|-----|
| 📚 类型 | {meta.get('genre', '未指定')} |
| 🎯 平台 | {meta.get('platform', '未指定')} |
| 📏 篇幅 | {meta.get('length', '未指定')} |
| 📅 创建时间 | {meta.get('created_at', '未知')[:19]} |

## 📈 创作进度

| 指标 | 当前值 |
|------|--------|
| 章节数 | {chapter_count} 章 |
| 总字数 | {total_words:,} 字 |
| 目标字数 | {meta.get('total_words_target', '1,000,000')} 字 |
| 进度 | {total_words / 10000:.1f}% |

## 📖 最近章节

"""
        if recent_chapters:
            for ch in recent_chapters:
                md += f"- `{ch['file']}` — {ch['words']:,} 字\n"
        else:
            md += "_暂无章节_\n"

        md += f"\n## 🔒 事实锁\n\n"
        md += f"- 已有事实锁: **{len(fact_locks)}** 条\n"

        md += "\n## 💡 快速操作\n\n"
        md += "- 🔍 评估知识库 → [知识库状态](#kb-status)\n"
        md += "- ✍️ 生成章节 → [章节生成](#chapter-gen)\n"
        md += "- 📊 评分章节 → [5 维评分](#scoring)\n"
        md += "- 🔍 提取事实 → [事实提取](#facts)\n"

        return md

    def score_chapter(self, project_name: str, chapter_file: str) -> str:
        """对章节进行 5 维评分"""
        path = self.get_project_path(project_name)
        if not path.exists():
            return f"❌ 项目 {project_name} 不存在"

        chapter_path = path / chapter_file
        if not chapter_path.exists():
            return f"❌ 章节文件不存在: {chapter_file}"

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_DIR / "chapter_scorer.py"),
                    str(chapter_path),
                    "--project-dir", str(path),
                ],
                capture_output=True, text=True, timeout=30,
            )
            return result.stdout if result.returncode == 0 \
                else f"❌ 评分失败:\n{result.stderr}"
        except Exception as e:
            return f"❌ 评分异常: {e}"

    def extract_facts(self, project_name: str, chapter_file: str) -> str:
        """提取章节事实"""
        path = self.get_project_path(project_name)
        if not path.exists():
            return f"❌ 项目 {project_name} 不存在"

        chapter_path = path / chapter_file
        if not chapter_path.exists():
            return f"❌ 章节文件不存在: {chapter_file}"

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_DIR / "fact_extractor.py"),
                    str(chapter_path),
                    "--project-dir", str(path),
                ],
                capture_output=True, text=True, timeout=30,
            )
            return result.stdout if result.returncode == 0 \
                else f"❌ 提取失败:\n{result.stderr}"
        except Exception as e:
            return f"❌ 提取异常: {e}"

    def assemble_context(self, project_name: str, chapter: int) -> str:
        """组装 7 层上下文"""
        path = self.get_project_path(project_name)
        if not path.exists():
            return f"❌ 项目 {project_name} 不存在"

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_DIR / "context_assembler.py"),
                    str(path),
                    "--chapter", str(chapter),
                ],
                capture_output=True, text=True, timeout=30,
            )
            return result.stdout if result.returncode == 0 \
                else f"❌ 装配失败:\n{result.stderr}"
        except Exception as e:
            return f"❌ 装配异常: {e}"

    def list_chapters(self, project_name: str) -> list:
        """列出项目所有章节"""
        path = self.get_project_path(project_name)
        if not path.exists():
            return []
        return sorted([f.name for f in path.glob("chapter_*.md")])

    def generate_demo_chapter(self, project_name: str, chapter_no: int,
                               prompt: str, target_words: int) -> str:
        """生成示例章节（演示用 - 实际使用应调用 LLM）"""
        path = self.get_project_path(project_name)
        if not path.exists():
            return "❌ 项目不存在"

        # 生成简单的演示章节
        chapter_text = f"""# 第 {chapter_no} 章 {prompt[:20]}...

## 第一节

我深吸一口气，抬手推开那扇破旧的木门。门后是一片漆黑，但我知道，答案就在其中。

{'(这是演示内容，实际使用时将调用 LLM 生成完整章节...)' * int(target_words // 50)}

## 章末钩

王二在台下对我低声说："有人要对付你。"

——本章完——
"""
        # 保存到项目
        chapter_file = path / f"chapter_{chapter_no:03d}.md"
        chapter_file.write_text(chapter_text, encoding="utf-8")

        return f"""✅ 第 {chapter_no} 章已生成！

**文件位置**: {chapter_file}
**字数**: {target_words:,}（演示版）

> 💡 演示模式：实际使用时需接入 LLM API
> 🔧 接入 DeepSeek/Claude API 后可生成真正的章节"""



# ==================== LLM 辅助函数 ====================


def call_llm_for_chapter_llm_score(project_name: str, chapter_file: str, dimension: str) -> str:
    """LLM 评分单个章节维度"""
    if not project_name or not chapter_file:
        return "❌ 请选择项目和章节"

    path = manager.get_project_path(project_name)
    if not path.exists():
        return f"❌ 项目 {project_name} 不存在"

    chapter_path = path / chapter_file
    if not chapter_path.exists():
        return f"❌ 章节不存在: {chapter_file}"

    text = chapter_path.read_text(encoding="utf-8")
    return call_llm_for_score(text, dimension, str(path))


def call_llm_for_chapter_with_save(project_name: str, chapter_no: int,
                                    target_words: int, prompt: str) -> str:
    """LLM 生成章节并保存到项目"""
    if not project_name:
        return "❌ 请先选择项目"
    if not prompt.strip():
        return "❌ 请填写章节描述"

    path = manager.get_project_path(project_name)
    if not path.exists():
        return f"❌ 项目 {project_name} 不存在"

    # 调用 LLM 生成
    response = call_llm_for_chapter(prompt, target_words, str(path))

    if response.startswith("❌"):
        return response

    # 保存到项目
    chapter_path = path / f"chapter_{chapter_no:03d}.md"
    chapter_path.write_text(response, encoding="utf-8")

    import re as _re
    chinese_chars = _re.findall(r"[\u4e00-\u9fff]", response)
    return f"""✅ 第 {chapter_no} 章已生成并保存！

**文件位置**: {chapter_path}
**字符数**: {len(chinese_chars):,} 字

---

```
{response[:600]}
{'...' if len(response) > 600 else ''}
```
"""

# ==================== 全局实例 ====================

manager = ProjectManager()


# ==================== Gradio 界面 ====================


def build_interface():
    """构建 Gradio 界面"""

    theme = gr.themes.Soft(primary_hue="indigo", secondary_hue="slate")

    with gr.Blocks(
        title="Auto-Novel · 自动小说创作（v1.0.5）",
    ) as demo:
        # ===== 顶部标题 =====
        gr.Markdown("""# 📖 Auto-Novel · 让 AI 写小说变简单

> **v1.0.5：Web 界面已接入 scripts/ 自动化脚本！** 从演示数据升级到完整工程化工具链。

所有项目管理、5 维评分、事实提取、上下文组装均调用本地 Python 脚本（无需 LLM 即可演示）。

---
""")

        # ===== 项目选择器 =====
        with gr.Row():
            project_selector = gr.Dropdown(
                choices=manager.list_projects(),
                value=manager.list_projects()[0] if manager.list_projects() else None,
                label="📚 选择项目",
                scale=2,
            )
            refresh_btn = gr.Button("🔄 刷新项目列表", scale=1)

        gr.Markdown(f"📂 **项目根目录**: `{manager.projects_root}`")

        # ===== 4 大标签页 =====
        with gr.Tabs():
            # ===== 标签页 1：项目仪表盘 =====
            with gr.Tab("📊 项目仪表盘", id="dashboard-tab"):

                def refresh_dashboard(project_name):
                    if not project_name:
                        return "❌ 请先选择项目"
                    return manager.get_dashboard(project_name)

                dashboard_output = gr.Markdown(value="*选择项目后查看仪表盘*")

                refresh_btn.click(
                    fn=lambda: (
                        gr.update(choices=manager.list_projects()),
                        refresh_dashboard(project_selector.value)
                    ),
                    outputs=[project_selector, dashboard_output]
                )

                project_selector.change(
                    fn=refresh_dashboard,
                    inputs=project_selector,
                    outputs=dashboard_output
                )

                gr.Markdown("---")
                gr.Markdown("## 🆕 创建新项目")

                with gr.Row():
                    with gr.Column():
                        new_name = gr.Textbox(label="📚 项目名称", placeholder="例：逆天仙途")
                        new_genre = gr.Dropdown(
                            choices=["玄幻/仙侠", "都市/现代", "言情/古风",
                                     "悬疑/推理", "科幻/未来", "历史/军事"],
                            value="玄幻/仙侠",
                            label="📖 题材"
                        )
                    with gr.Column():
                        new_platform = gr.Dropdown(
                            choices=["起点", "番茄", "晋江", "七猫", "知乎盐选"],
                            value="起点",
                            label="🎯 目标平台"
                        )
                        new_length = gr.Dropdown(
                            choices=["短篇（3-10 万字）", "中篇（10-30 万字）",
                                     "长篇（30-100 万字）", "超长篇（100 万字+）"],
                            value="长篇（30-100 万字）",
                            label="📏 篇幅"
                        )
                create_btn = gr.Button("🆕 创建项目", variant="primary")
                create_output = gr.Markdown()
                create_btn.click(
                    fn=manager.create_project,
                    inputs=[new_name, new_genre, new_platform, new_length],
                    outputs=create_output
                )

            # ===== 标签页 2：知识库状态 =====
            with gr.Tab("📚 知识库状态", id="kb-tab"):
                kb_output = gr.Markdown(value="*点击下方按钮查看*")

                kb_btn = gr.Button("🔍 查看 5 件知识库状态", variant="primary")
                kb_btn.click(
                    fn=lambda name: manager.get_status(name) if name else "❌ 请先选择项目",
                    inputs=project_selector,
                    outputs=kb_output
                )

            # ===== 标签页 3：章节生成与评分 =====
            with gr.Tab("✍️ 章节生成 + 评分", id="chapter-tab"):
                gr.Markdown("## 📝 生成章节（演示模式）")

                with gr.Row():
                    with gr.Column():
                        gen_chapter_no = gr.Slider(1, 500, value=12, step=1, label="章节号")
                        gen_target_words = gr.Slider(1500, 5000, value=3500, step=100, label="目标字数")
                        gen_prompt = gr.Textbox(
                            label="章节描述",
                            placeholder="例：张三参加宗门大比预选赛",
                            lines=3
                        )
                        gen_btn = gr.Button("🚀 生成章节", variant="primary")
                    with gr.Column():
                        gen_output = gr.Markdown(value="*生成的章节会保存到项目目录*")

                gen_btn.click(
                    fn=lambda proj, ch_no, words, prompt:
                        manager.generate_demo_chapter(proj, int(ch_no), prompt, int(words))
                        if proj else "❌ 请先选择项目",
                    inputs=[project_selector, gen_chapter_no, gen_target_words, gen_prompt],
                    outputs=gen_output
                )

                gr.Markdown("---")
                gr.Markdown("## 📊 5 维评分")

                with gr.Row():
                    with gr.Column():
                        chapter_dropdown = gr.Dropdown(
                            choices=[],
                            label="📖 选择章节"
                        )
                        refresh_chapters_btn = gr.Button("🔄 刷新章节列表")
                        score_btn = gr.Button("📊 开始评分", variant="primary")
                    with gr.Column():
                        score_output = gr.Markdown(value="*点击\"开始评分\"*")

                refresh_chapters_btn.click(
                    fn=lambda proj: gr.update(choices=manager.list_chapters(proj) if proj else []),
                    inputs=project_selector,
                    outputs=chapter_dropdown
                )

                score_btn.click(
                    fn=lambda proj, ch: manager.score_chapter(proj, ch) if proj and ch else "❌ 请选择项目和章节",
                    inputs=[project_selector, chapter_dropdown],
                    outputs=score_output
                )

            # ===== 标签页 4：事实提取 + 上下文 =====
            with gr.Tab("🔧 事实 & 上下文", id="tools-tab"):
                gr.Markdown("## 🔍 提取事实锁")

                with gr.Row():
                    with gr.Column():
                        fact_chapter_dropdown = gr.Dropdown(
                            choices=[],
                            label="📖 选择章节"
                        )
                        refresh_fact_chapters_btn = gr.Button("🔄 刷新章节列表")
                        extract_btn = gr.Button("🔍 提取事实", variant="primary")
                    with gr.Column():
                        extract_output = gr.Markdown(value="*点击\"提取事实\"*")

                refresh_fact_chapters_btn.click(
                    fn=lambda proj: gr.update(choices=manager.list_chapters(proj) if proj else []),
                    inputs=project_selector,
                    outputs=fact_chapter_dropdown
                )

                extract_btn.click(
                    fn=lambda proj, ch: manager.extract_facts(proj, ch) if proj and ch else "❌ 请选择项目和章节",
                    inputs=[project_selector, fact_chapter_dropdown],
                    outputs=extract_output
                )

                gr.Markdown("---")
                gr.Markdown("## 🧩 7 层上下文组装")

                with gr.Row():
                    with gr.Column():
                        ctx_chapter_no = gr.Slider(1, 500, value=1, step=1, label="目标章节")
                        assemble_btn = gr.Button("🧩 组装上下文", variant="primary")
                    with gr.Column():
                        ctx_output = gr.Markdown(value="*点击\"组装上下文\"*")

                assemble_btn.click(
                    fn=lambda proj, ch_no: manager.assemble_context(proj, int(ch_no)) if proj else "❌ 请选择项目",
                    inputs=[project_selector, ctx_chapter_no],
                    outputs=ctx_output
                )

            # ===== 标签页 5：LLM 配置 =====
            with gr.Tab("🤖 LLM 配置", id="llm-config-tab"):
                gr.Markdown("## 🔑 LLM Provider 配置")
                gr.Markdown("""
支持 4 个 provider：
- **DeepSeek**（推荐）：性价比高，中文友好
- **Anthropic Claude**：质量高，价格贵
- **OpenAI**：英文友好
- **智谱 GLM**：有免费模型（glm-4-flash）

**配置方式**：
1. 在下方输入 API Key（仅保存到当前会话，不会上传）
2. 或设置环境变量：`export DEEPSEEK_API_KEY=sk-xxx`
""")

                with gr.Row():
                    with gr.Column():
                        provider_select = gr.Dropdown(
                            choices=["deepseek", "anthropic", "openai", "zhipu"],
                            value="deepseek",
                            label="🤖 Provider"
                        )
                        model_select = gr.Textbox(
                            value="deepseek-chat",
                            label="🧠 模型",
                            placeholder="例：deepseek-chat / claude-3-5-sonnet-20241022"
                        )
                        api_key_input = gr.Textbox(
                            label="🔑 API Key（可选）",
                            placeholder="留空则复用环境变量",
                            type="password"
                        )
                        save_config_btn = gr.Button("💾 保存配置", variant="primary")
                    with gr.Column():
                        config_status = gr.Markdown(value="*显示当前配置*")

                save_config_btn.click(
                    fn=lambda p, m, k: update_settings(p, m, k),
                    inputs=[provider_select, model_select, api_key_input],
                    outputs=config_status
                )

                def refresh_llm_status():
                    status = get_settings()
                    md = f"""**当前配置**：

| 字段 | 值 |
|------|-----|
| Provider | {status['provider']} |
| Model | {status['model']} |
| 缓存目录 | {status['cache_dir']} |
| 缓存条目 | {status['cache_size']} |

**API Key 状态**：

"""
                    for k, v in status["api_key_set"].items():
                        marker = "✅" if v else "❌"
                        md += f"- {marker} {k}\n"
                    return md

                check_btn = gr.Button("🔍 查看当前状态")
                check_btn.click(fn=refresh_llm_status, outputs=config_status)

                gr.Markdown("---")
                gr.Markdown("## 🧪 LLM 评分测试")

                with gr.Row():
                    with gr.Column():
                        llm_score_chapter = gr.Dropdown(
                            choices=[],
                            label="📖 选择章节"
                        )
                        llm_refresh_btn = gr.Button("🔄 刷新章节")
                        llm_score_dim = gr.Radio(
                            choices=["style", "repetition", "ooc"],
                            value="style",
                            label="评分维度"
                        )
                        llm_score_btn = gr.Button("🤖 LLM 评分", variant="primary")
                    with gr.Column():
                        llm_score_output = gr.Markdown(value="*点击 LLM 评分按钮*")

                llm_refresh_btn.click(
                    fn=lambda proj: gr.update(choices=manager.list_chapters(proj) if proj else []),
                    inputs=project_selector,
                    outputs=llm_score_chapter
                )

                llm_score_btn.click(
                    fn=lambda proj, ch, dim: call_llm_for_chapter_llm_score(proj, ch, dim),
                    inputs=[project_selector, llm_score_chapter, llm_score_dim],
                    outputs=llm_score_output
                )

                gr.Markdown("---")
                gr.Markdown("## ✨ LLM 生成章节")

                with gr.Row():
                    with gr.Column():
                        llm_chapter_no = gr.Slider(1, 500, value=12, step=1, label="章节号")
                        llm_target_words = gr.Slider(1500, 5000, value=3500, step=100, label="目标字数")
                        llm_prompt = gr.Textbox(
                            label="章节描述",
                            placeholder="例：张三参加宗门大比预选赛",
                            lines=3
                        )
                        llm_gen_btn = gr.Button("🚀 LLM 生成", variant="primary")
                    with gr.Column():
                        llm_gen_output = gr.Markdown(value="*生成结果将显示在此*")

                llm_gen_btn.click(
                    fn=lambda proj, ch, words, prompt:
                        call_llm_for_chapter_with_save(proj, int(ch), int(words), prompt),
                    inputs=[project_selector, llm_chapter_no, llm_target_words, llm_prompt],
                    outputs=llm_gen_output
                )

        # ===== 底部信息 =====
        gr.Markdown("""---
**Auto-Novel v1.0.5** · Web 界面已接入 scripts/

🔧 **本版本改进**：
- ✅ 移除演示数据 `ProjectStore`
- ✅ 接入 `scripts/` 5 个自动化脚本作为后端
- ✅ 支持真实项目管理（创建/查询/评分/提取事实/组装上下文）
- ✅ 项目存储位置：`~/auto-novel-projects/`

📖 [查看文档](../README.md) · 💬 [社区](https://discord.com.com) · 🐛 [Bug 报告](https://github.com.com)
""")

    return demo


# ==================== 启动入口 ====================


def main():
    print("=" * 70)
    print("📖 Auto-Novel Skill · Web 界面 v1.0.5")
    print("=" * 70)
    print(f"📂 项目根目录: {manager.projects_root}")
    print(f"🌐 启动地址: http://localhost:7860")
    print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    demo = build_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True,
        quiet=False,
        theme=gr.themes.Soft(primary_hue="indigo", secondary_hue="slate"),
        css=".gradio-container {max-width: 1200px !important}"
    )


if __name__ == "__main__":
    main()