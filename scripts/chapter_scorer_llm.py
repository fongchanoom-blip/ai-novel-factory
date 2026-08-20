#!/usr/bin/env python3
"""
5 维评分器 - LLM 增强版（Chapter Scorer LLM-Enhanced）

v1.0.6 新增：可选 LLM 增强评分

相比基础版（chapter_scorer.py）：
- ✅ 文风一致性：调用 LLM 深度分析（替代正则匹配）
- ✅ 非重复性：调用 LLM 检测语义重复
- ✅ 人设一致性：调用 LLM 检查角色 OOC

兼容模式：
- 默认：仍使用规则版（无需 API Key）
- --mode llm：使用 LLM 增强（需要 API Key）
- --mode hybrid：规则 + LLM 综合判断

用法：
    python3 chapter_scorer_llm.py <chapter_file> --mode llm
    python3 chapter_scorer_llm.py <chapter_file> --mode hybrid
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

# 复用基础版
sys.path.insert(0, str(Path(__file__).parent))
from chapter_scorer import (
    DimensionScore, OverallScore, ChapterScorer
)

# 复用 LLM 客户端
from llm_client import LLMClient


# ==================== LLM 评分 prompt 模板 ====================


PROMPTS = {
    "style": """你是一位资深网文编辑，正在评估章节的**文风一致性**。

【章节正文】
{text}

【文风样本】（参考）
{style_sample}

请评估：
1. 词汇是否与样本一致（古代用词 vs 现代网络用语）
2. 句式是否符合（长短句分布）
3. 镜头语言是否符合（人物视角 vs 全知视角）
4. 总体文风氛围（热血/阴谋/轻松）

输出严格按以下格式（0-10 分，保留 1 位小数）：

```
SCORE: 8.5
ISSUES:
- [问题 1]
- [问题 2]
PASSES:
- [优点 1]
```""",

    "repetition": """你是一位资深网文编辑，正在评估章节的**非重复性**。

【章节正文】
{text}

请评估：
1. 是否有相似的句式连续出现（≥3 次）
2. 是否有相同的形容词/动词过度使用
3. 是否有"眼睛微眯/瞳孔一缩"等 AI 味套路
4. 爽点是否多样化（避免单一模式）

输出严格按以下格式（0-10 分，保留 1 位小数）：

```
SCORE: 8.5
ISSUES:
- [问题 1]
PASSES:
- [优点 1]
```""",

    "ooc": """你是一位资深网文编辑，正在评估章节的**人设一致性（OOC）**。

【章节正文】
{text}

【角色设定】
{character_profiles}

请评估：
1. 主角言行是否符合人设（性格、动机、语气）
2. 配角是否 OOC（角色弧光是否一致）
3. 角色成长是否铺垫合理
4. 是否有"突然性格变化"等不自然描写

输出严格按以下格式（0-10 分，保留 1 位小数）：

```
SCORE: 8.5
ISSUES:
- [问题 1]
PASSES:
- [优点 1]
```""",
}


# ==================== LLM 增强评分器 ====================


class LLMEnhancedScorer(ChapterScorer):
    """LLM 增强版评分器（继承自基础版）"""

    def __init__(self, project_dir: str = ".", use_llm: bool = True):
        super().__init__(project_dir)
        self.use_llm = use_llm
        self.llm_client = LLMClient() if use_llm else None

    def score_chapter(self, chapter_text: str, chapter_file: str = "") -> OverallScore:
        """对章节进行 5 维评分（LLM 增强版）"""
        # 1. 基础规则评分（无需 LLM 也能跑）
        scores = {
            "人设一致性": self._score_ooc(chapter_text),
            "世界观一致性": self._score_lore(chapter_text),
            "逻辑性": self._score_logic(chapter_text),
            "文风一致性": self._score_style(chapter_text),
            "非重复性": self._score_repetition(chapter_text),
        }

        # 2. LLM 增强（如果有 API Key）
        if self.use_llm and self.llm_client:
            # 检查 API Key
            status = self.llm_client.get_status()
            if any(status["api_key_set"].values()):
                # 增强文风一致性
                style_score = self._llm_score_style(chapter_text)
                if style_score:
                    scores["文风一致性"] = style_score

                # 增强非重复性
                rep_score = self._llm_score_repetition(chapter_text)
                if rep_score:
                    scores["非重复性"] = rep_score

                # 增强人设一致性
                ooc_score = self._llm_score_ooc(chapter_text)
                if ooc_score:
                    scores["人设一致性"] = ooc_score

        # 3. 加权计算总分
        overall = sum(
            s.score * self.WEIGHTS[name]
            for name, s in scores.items()
        )

        # 4. 状态判断
        if overall >= 9.0:
            status = "✅ auto_pass"
        elif overall >= 7.0:
            status = "⚠️ review"
        else:
            status = "❌ rewrite"

        from datetime import datetime
        word_count = len(re.findall(r"[\u4e00-\u9fff]", chapter_text))

        return OverallScore(
            overall=round(overall, 2),
            status=status,
            dimensions={k: s.to_dict() for k, s in scores.items()},
            timestamp=datetime.now().isoformat(),
            chapter_file=chapter_file,
            word_count=word_count,
        )

    def _llm_score_style(self, text: str) -> Optional[DimensionScore]:
        """LLM 评估文风一致性"""
        # 读取文风样本
        style_sample = ""
        style_file = self.project_dir / "文风样本.md"
        if style_file.exists():
            style_sample = style_file.read_text(encoding="utf-8")[:1000]

        prompt = PROMPTS["style"].format(
            text=text[:3000],  # 截断避免超长
            style_sample=style_sample or "（无）"
        )

        response = self.llm_client.call(prompt, max_tokens=800)
        return self._parse_llm_response("文风一致性", response)

    def _llm_score_repetition(self, text: str) -> Optional[DimensionScore]:
        """LLM 评估非重复性"""
        prompt = PROMPTS["repetition"].format(text=text[:3000])
        response = self.llm_client.call(prompt, max_tokens=800)
        return self._parse_llm_response("非重复性", response)

    def _llm_score_ooc(self, text: str) -> Optional[DimensionScore]:
        """LLM 评估人设一致性"""
        # 读取角色档案
        profiles = ""
        profiles_file = self.project_dir / "角色档案.md"
        if profiles_file.exists():
            profiles = profiles_file.read_text(encoding="utf-8")[:1000]

        prompt = PROMPTS["ooc"].format(
            text=text[:3000],
            character_profiles=profiles or "（无）"
        )
        response = self.llm_client.call(prompt, max_tokens=800)
        return self._parse_llm_response("人设一致性", response)

    def _parse_llm_response(self, name: str, response: str) -> Optional[DimensionScore]:
        """解析 LLM 响应"""
        if not response or response.startswith("["):
            return None  # 错误响应

        # 提取 SCORE
        score_match = re.search(r"SCORE:\s*(\d+\.?\d*)", response)
        if not score_match:
            return None

        score = float(score_match.group(1))
        score = max(0.0, min(10.0, score))

        # 提取 ISSUES
        issues = []
        issues_match = re.search(r"ISSUES:\s*\n(.*?)(?:PASSES:|```|$)",
                                 response, re.DOTALL)
        if issues_match:
            issues = [
                line.strip().lstrip("- ").strip()
                for line in issues_match.group(1).split("\n")
                if line.strip().startswith("-")
            ]

        # 提取 PASSES
        passes = []
        passes_match = re.search(r"PASSES:\s*\n(.*?)(?:```|$)",
                                 response, re.DOTALL)
        if passes_match:
            passes = [
                line.strip().lstrip("- ").strip()
                for line in passes_match.group(1).split("\n")
                if line.strip().startswith("-")
            ]

        return DimensionScore(
            name=name,
            score=round(score, 2),
            issues=issues,
            passes=passes,
            weight=self.WEIGHTS.get(name, 0.0)
        )


# ==================== CLI 入口 ====================


def main():
    parser = argparse.ArgumentParser(description="5 维评分器（LLM 增强版）")
    parser.add_argument("chapter", help="章节文件路径")
    parser.add_argument("--project-dir", default=".", help="小说项目目录")
    parser.add_argument("--mode", choices=["rule", "llm", "hybrid"],
                        default="hybrid",
                        help="评分模式（rule=仅规则，llm=仅 LLM，hybrid=综合）")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    print("=" * 70)
    print("📊 Auto-Novel · 5 维评分器（LLM 增强版）")
    print("=" * 70)

    chapter_path = Path(args.chapter)
    if not chapter_path.exists():
        print(f"❌ 文件不存在: {args.chapter}")
        sys.exit(1)

    text = chapter_path.read_text(encoding="utf-8")
    chinese_chars = re.findall(r"[\u4e00-\u9fff]", text)

    print(f"📄 章节: {chapter_path.name}")
    print(f"📏 字数: {len(chinese_chars)}")
    print(f"🔧 模式: {args.mode}")

    # 显示 LLM 状态
    if args.mode in ["llm", "hybrid"]:
        client = LLMClient()
        status = client.get_status()
        any_key = any(status["api_key_set"].values())
        print(f"🔑 API Key: {'已配置' if any_key else '未配置（将自动降级为规则版）'}")
        print(f"🤖 当前 provider: {status['provider']}")
        print()

    # 评分
    use_llm = args.mode in ["llm", "hybrid"]
    scorer = LLMEnhancedScorer(args.project_dir, use_llm=use_llm)
    result = scorer.score_chapter(text, chapter_path.name)

    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(f"\n【5 维评分结果】")
        print(f"总评: {result.overall} {result.status}")
        print()
        for name, dim in result.dimensions.items():
            weight_pct = int(dim["weight"] * 100)
            print(f"  {name} ({weight_pct}%): {dim['score']}/10")
            for issue in dim["issues"]:
                print(f"    ❌ {issue}")
            for pass_item in dim["passes"]:
                print(f"    ✅ {pass_item}")
            print()

    print("=" * 70)


if __name__ == "__main__":
    main()