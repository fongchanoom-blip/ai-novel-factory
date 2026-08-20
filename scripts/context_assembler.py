#!/usr/bin/env python3
"""
7 层上下文组装器（Context Assembler）

为章节生成组装 7 层上下文。
实现 [REF:protocol.context_assembly] 的核心功能。

7 层：
  Layer 7: 项目元数据
  Layer 6: 当前章节需要的文风样本
  Layer 5: 最近 20 章摘要 + 50 章阶段摘要
  Layer 4: 最近 3 章有效正文
  Layer 3: 当前 50 章规划
  Layer 2: 主角状态仓库
  Layer 1: 当前章节契约

用法：
    python3 context_assembler.py <project_dir> [--chapter N] [--output json]
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


# ==================== 数据结构 ====================


class ContextBundle:
    """7 层上下文包"""

    def __init__(self):
        self.layers = {
            "layer_1_chapter_contract": {},
            "layer_2_protagonist_state": {},
            "layer_3_phase_plan": {},
            "layer_4_recent_chapters": [],
            "layer_5_summaries": {},
            "layer_6_style_samples": "",
            "layer_7_project_metadata": {},
        }
        self.token_estimate = 0

    def to_dict(self):
        return {
            "layers": self.layers,
            "token_estimate": self.token_estimate,
            "generated_at": datetime.now().isoformat(),
        }

    def estimate_tokens(self):
        """估算 token 数"""
        total = 0
        for layer_data in self.layers.values():
            if isinstance(layer_data, list):
                for item in layer_data:
                    total += len(str(item)) // 2
            elif isinstance(layer_data, dict):
                total += len(json.dumps(layer_data, ensure_ascii=False)) // 2
            else:
                total += len(str(layer_data)) // 2
        self.token_estimate = total
        return total


# ==================== 7 层组装 ====================


class ContextAssembler:
    """7 层上下文组装器"""

    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)

    def assemble(self, chapter_number: int) -> ContextBundle:
        """组装完整上下文"""
        ctx = ContextBundle()

        # Layer 7: 项目元数据
        ctx.layers["layer_7_project_metadata"] = self._load_layer_7()

        # Layer 1: 章节契约
        ctx.layers["layer_1_chapter_contract"] = self._load_layer_1(chapter_number)

        # Layer 2: 主角状态
        ctx.layers["layer_2_protagonist_state"] = self._load_layer_2()

        # Layer 3: 阶段规划
        ctx.layers["layer_3_phase_plan"] = self._load_layer_3(chapter_number)

        # Layer 4: 最近 3 章正文
        ctx.layers["layer_4_recent_chapters"] = self._load_layer_4(chapter_number)

        # Layer 5: 摘要
        ctx.layers["layer_5_summaries"] = self._load_layer_5(chapter_number)

        # Layer 6: 文风样本
        ctx.layers["layer_6_style_samples"] = self._load_layer_6()

        ctx.estimate_tokens()
        return ctx

    def _load_layer_7(self) -> dict:
        """Layer 7: 项目元数据"""
        return {
            "title": self._load_meta("title") or "未命名小说",
            "author": self._load_meta("author") or "未知作者",
            "genre": self._load_meta("genre") or "未指定",
            "pov": self._load_meta("pov") or "第一人称",
            "total_words_target": int(self._load_meta("total_words_target") or "1000000"),
            "current_words": self._count_total_words(),
            "progress_pct": 0.0,
            "current_volume": 1,
            "current_chapter": self._get_last_chapter(),
            "min_words_per_chapter": 3000,
            "max_words_per_chapter": 4000,
        }

    def _load_layer_1(self, chapter: int) -> dict:
        """Layer 1: 章节契约"""
        toc_file = self.project_dir / "toc" / f"chapter_{chapter:03d}.md"
        contract = {
            "chapter_number": chapter,
            "chapter_title": self._get_chapter_title(chapter),
            "must_happen": [],
            "must_not_happen": [],
            "ending_hook": "",
            "continuity_risks": [],
            "target_words": 3500,
        }

        if toc_file.exists():
            text = toc_file.read_text(encoding="utf-8")
            # 简化解析
            for line in text.split("\n"):
                if "must_happen" in line.lower() or "必须" in line:
                    contract["must_happen"].append(line.strip())
                elif "must_not" in line.lower() or "禁止" in line:
                    contract["must_not_happen"].append(line.strip())
                elif "ending_hook" in line.lower() or "章末钩" in line:
                    contract["ending_hook"] = line.strip()
        else:
            contract["must_happen"] = ["[默认] 推动主线"]
            contract["must_not_happen"] = ["[默认] 不要 OOC"]
            contract["ending_hook"] = "[默认] 设置下一章悬念"

        return contract

    def _load_layer_2(self) -> dict:
        """Layer 2: 主角状态仓库"""
        foundation_file = self.project_dir / "世界基石.md"
        if foundation_file.exists():
            text = foundation_file.read_text(encoding="utf-8")
            # 简单解析（实际应该用 YAML 解析）
            return {
                "name": self._extract_value(text, "姓名") or "主角",
                "current_realm": self._extract_value(text, "修为") or "未指定",
                "resources": self._extract_value(text, "灵石") or "0",
                "location": self._extract_value(text, "位置") or "未指定",
                "injuries": self._extract_value(text, "伤势") or "无",
                "source": "世界基石.md",
            }
        return {
            "name": "主角",
            "current_realm": "未指定",
            "resources": "0",
            "location": "未指定",
            "injuries": "无",
            "source": "缺失（使用默认）",
        }

    def _load_layer_3(self, chapter: int) -> dict:
        """Layer 3: 当前 50 章规划"""
        return {
            "phase_number": (chapter - 1) // 50 + 1,
            "phase_theme": "第 1 阶段：宗门崛起" if chapter <= 50 else "后续阶段",
            "phase_chapters": "1-50",
            "current_progress_pct": ((chapter - 1) % 50) * 2,
            "planned_events": [],
            "phase_milestones": [],
            "pending_reveals": [],
        }

    def _load_layer_4(self, chapter: int) -> list:
        """Layer 4: 最近 3 章正文"""
        recent = []
        for i in range(max(1, chapter - 3), chapter):
            ch_file = self.project_dir / f"chapter_{i:03d}.md"
            if ch_file.exists():
                text = ch_file.read_text(encoding="utf-8")
                # 提取前 1000 字作为摘要
                summary = text[:1000] if len(text) > 1000 else text
                recent.append({
                    "chapter": i,
                    "title": self._get_chapter_title(i),
                    "summary": summary,
                    "word_count": len(re.findall(r"[\u4e00-\u9fff]", text)),
                })
            else:
                recent.append({
                    "chapter": i,
                    "title": f"第 {i} 章（未找到）",
                    "summary": "[未找到该章节]",
                    "word_count": 0,
                })
        return recent

    def _load_layer_5(self, chapter: int) -> dict:
        """Layer 5: 摘要"""
        return {
            "recent_20_chapters": [],
            "phase_summary": {
                "phase": "第 1 阶段",
                "arc_progress": f"已完成 {chapter - 1} 章",
                "key_reveals": [],
            },
        }

    def _load_layer_6(self) -> str:
        """Layer 6: 文风样本"""
        style_file = self.project_dir / "文风样本.md"
        if style_file.exists():
            text = style_file.read_text(encoding="utf-8")
            return text[:2000]  # 取前 2000 字符
        return "[默认] 古风仙侠，半文半白"

    # ----- 辅助方法 -----

    def _load_meta(self, key: str) -> str:
        """从项目元数据加载"""
        meta_file = self.project_dir / "project_meta.yaml"
        if meta_file.exists():
            text = meta_file.read_text(encoding="utf-8")
            for line in text.split("\n"):
                if line.startswith(f"{key}:"):
                    return line.split(":", 1)[1].strip()
        return ""

    def _extract_value(self, text: str, key: str) -> str:
        """从文本中提取 key 对应的值"""
        for line in text.split("\n"):
            if key in line and ":" in line:
                return line.split(":", 1)[1].strip()
        return ""

    def _get_chapter_title(self, chapter: int) -> str:
        """获取章节标题"""
        toc_file = self.project_dir / "toc" / f"chapter_{chapter:03d}.md"
        if toc_file.exists():
            text = toc_file.read_text(encoding="utf-8")
            first_line = text.split("\n")[0]
            if first_line.startswith("#"):
                return first_line.lstrip("#").strip()
        return f"第 {chapter} 章"

    def _count_total_words(self) -> int:
        """统计已写总字数"""
        total = 0
        for ch_file in self.project_dir.glob("chapter_*.md"):
            text = ch_file.read_text(encoding="utf-8")
            total += len(re.findall(r"[\u4e00-\u9fff]", text))
        return total

    def _get_last_chapter(self) -> int:
        """获取最后章节号"""
        chapters = list(self.project_dir.glob("chapter_*.md"))
        if not chapters:
            return 0
        max_n = 0
        for f in chapters:
            m = re.search(r"chapter_(\d+)", f.name)
            if m:
                max_n = max(max_n, int(m.group(1)))
        return max_n


# ==================== CLI 入口 ====================


def main():
    parser = argparse.ArgumentParser(description="7 层上下文组装器")
    parser.add_argument("project_dir", help="小说项目目录")
    parser.add_argument("--chapter", type=int, default=1,
                        help="章节号（默认 1）")
    parser.add_argument("--output", choices=["text", "json"],
                        default="text", help="输出格式")
    args = parser.parse_args()

    print("=" * 70)
    print("🧩 Auto-Novel · 7 层上下文组装器")
    print("=" * 70)
    print(f"📂 项目目录: {args.project_dir}")
    print(f"📖 目标章节: {args.chapter}")
    print()

    assembler = ContextAssembler(args.project_dir)
    ctx = assembler.assemble(args.chapter)

    if args.output == "json":
        print(json.dumps(ctx.to_dict(), ensure_ascii=False, indent=2))
    else:
        for layer_name, layer_data in ctx.layers.items():
            print(f"【{layer_name}】")
            if isinstance(layer_data, list):
                print(f"  项数: {len(layer_data)}")
                for item in layer_data[:3]:
                    print(f"  - {str(item)[:100]}...")
                if len(layer_data) > 3:
                    print(f"  ... 还有 {len(layer_data) - 3} 项")
            elif isinstance(layer_data, dict):
                print(f"  字段: {len(layer_data)}")
                for k, v in layer_data.items():
                    print(f"  - {k}: {str(v)[:80]}")
            else:
                print(f"  内容: {str(layer_data)[:200]}...")
            print()

        print(f"📊 总 Token 估算: {ctx.token_estimate}")

    print("=" * 70)


if __name__ == "__main__":
    main()