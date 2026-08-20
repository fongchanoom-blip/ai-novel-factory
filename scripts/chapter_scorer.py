#!/usr/bin/env python3
"""
5 维评分器（Chapter Scorer）

基于规则的 5 维评分系统（无需调用 LLM）。
实现 [REF:protocol.quality_scoring] 的核心功能。

5 维：
  - 人设一致性（OOC）：30%
  - 世界观一致性（Lore）：25%
  - 逻辑性（Logic）：20%
  - 文风一致性（Style）：15%
  - 非重复性（Non-Repetition）：10%

用法：
    python3 chapter_scorer.py <chapter_file>
    python3 chapter_scorer.py <chapter_file> --project-dir <dir>
    python3 chapter_scorer.py <chapter_file> --json  # JSON 输出
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path


# ==================== 评分维度 ====================


@dataclass
class DimensionScore:
    """单个维度的评分"""
    name: str
    score: float
    issues: list  # 问题列表
    passes: list  # 通过的检查项
    weight: float = 0.0

    def to_dict(self):
        return asdict(self)


@dataclass
class OverallScore:
    """总评分"""
    overall: float
    status: str  # auto_pass / review / rewrite
    dimensions: dict
    timestamp: str
    chapter_file: str
    word_count: int = 0

    def to_dict(self):
        return asdict(self)


# ==================== 5 维评分逻辑 ====================


class ChapterScorer:
    """5 维评分器（基于规则，无需 LLM）"""

    WEIGHTS = {
        "人设一致性": 0.30,
        "世界观一致性": 0.25,
        "逻辑性": 0.20,
        "文风一致性": 0.15,
        "非重复性": 0.10,
    }

    # 常见 AI 味信号
    AI_SMELL_PATTERNS = [
        r"然而.{0,20}的(?:时候|瞬间)",
        r"与此同时",
        r"因此.{0,15}的(?:原因|理由)",
        r"综上所述",
        r"这一刻.{0,15}，(?:他|她|我)(?:明白|懂[得了]|终于)",
        r"瞳孔一缩",
        r"震惊[无比]?",
        r"简直不敢相信",
    ]

    # 文风信号（禁用表达）
    DISABLED_PATTERNS = [
        r"\b(?:YYDS|绝绝子|666|emo)\b",
        r"\b(?:小仙女|集美们)\b",
        r"\b(?:我(?:太|超)爱)\b",
    ]

    # 爽点关键词
    ENJOYMENT_KEYWORDS = [
        "一巴掌", "打脸", "震惊", "逆转", "突破",
        "反杀", "揭露", "领悟", "进阶", "翻盘"
    ]

    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)

    def score_chapter(self, chapter_text: str) -> OverallScore:
        """对章节进行 5 维评分"""
        scores = {
            "人设一致性": self._score_ooc(chapter_text),
            "世界观一致性": self._score_lore(chapter_text),
            "逻辑性": self._score_logic(chapter_text),
            "文风一致性": self._score_style(chapter_text),
            "非重复性": self._score_repetition(chapter_text),
        }

        # 加权计算总分
        overall = sum(
            s.score * self.WEIGHTS[name]
            for name, s in scores.items()
        )

        # 状态判断
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
            chapter_file="",
            word_count=word_count,
        )

    # ----- 维度 1：人设一致性（OOC）-----
    def _score_ooc(self, text: str) -> DimensionScore:
        issues = []
        passes = []

        # 检查 1：角色对话语气（如果有对话）
        dialogues = re.findall(r'["""]([^"""]+)["""]', text)
        if dialogues:
            # 短对话通常更自然（AI 喜欢写长对话）
            long_dialogues = [d for d in dialogues if len(d) > 100]
            if len(long_dialogues) > len(dialogues) * 0.5:
                issues.append("半数以上对话超过 100 字（可能 AI 化）")
            else:
                passes.append("对话长度合理")

        # 检查 2：心理活动过度描写（AI 味标志）
        psychology = re.findall(r"(?:心中|心里)[，,]?\s*(?:想|暗想|喃喃|暗自)(.{0,30})", text)
        if len(psychology) > 10:
            issues.append(f"心理活动描写 {len(psychology)} 次（过多，AI 味）")
        else:
            passes.append(f"心理活动 {len(psychology)} 次（合理）")

        # 检查 3：角色情绪变化是否铺垫
        emotion_changes = re.findall(r"(?:突然|忽然|霎时)(.{0,15}?(?:愤怒|悲伤|欣喜|惊恐))", text)
        if len(emotion_changes) > 3:
            issues.append(f"情绪突变 {len(emotion_changes)} 次（铺垫不足）")
        else:
            passes.append("情绪变化有铺垫")

        # 评分
        n_checks = 3
        n_pass = len(passes)
        n_issue = len(issues)
        score = 10 - (n_issue / n_checks) * 4
        score = max(5.0, min(10.0, score))

        return DimensionScore(
            name="人设一致性",
            score=round(score, 2),
            issues=issues,
            passes=passes,
            weight=self.WEIGHTS["人设一致性"]
        )

    # ----- 维度 2：世界观一致性（Lore）-----
    def _score_lore(self, text: str) -> DimensionScore:
        issues = []
        passes = []

        # 检查 1：力量体系（玄幻常见）
        levels = re.findall(r"(筑基|金丹|元婴|化神|练气|凡人)期", text)
        if levels:
            level_nums = [self._level_to_num(l) for l in levels]
            if len(set(level_nums)) > 3:
                issues.append(f"章节内出现 {len(set(level_nums))} 个不同境界（可能混乱）")
            else:
                passes.append(f"境界层级一致（{len(set(level_nums))} 个）")

        # 检查 2：物品/资源数字一致性
        numbers = re.findall(r"\d+\s*(?:灵石|银两|金币|元石|仙晶)", text)
        if numbers:
            # 检查数字是否矛盾（同一物品多个不同数字）
            if len(set(numbers)) > 2:
                issues.append(f"资源数字有 {len(set(numbers))} 个不同值")
            else:
                passes.append("资源数字一致")

        # 检查 3：地理距离合理性（如果有）
        distances = re.findall(r"(\d+)\s*(?:天|日|里|公里|时辰)", text)
        # 距离不应太小（< 1）也不应太大（> 1000）
        extreme_distances = [d for d in distances if int(d) < 1 or int(d) > 1000]
        if extreme_distances:
            issues.append(f"距离数值异常: {extreme_distances}")
        else:
            passes.append("地理距离合理")

        # 评分
        n_checks = 3
        n_issue = len(issues)
        score = 10 - (n_issue / n_checks) * 5
        score = max(5.0, min(10.0, score))

        return DimensionScore(
            name="世界观一致性",
            score=round(score, 2),
            issues=issues,
            passes=passes,
            weight=self.WEIGHTS["世界观一致性"]
        )

    # ----- 维度 3：逻辑性（Logic）-----
    def _score_logic(self, text: str) -> DimensionScore:
        issues = []
        passes = []

        # 检查 1：因果连接词
        causal = re.findall(r"(因为|所以|因此|由于|导致)", text)
        if len(causal) >= 3:
            passes.append(f"因果连接词 {len(causal)} 处（逻辑清晰）")
        else:
            issues.append("因果连接词不足")

        # 检查 2：时间线合理性
        time_markers = re.findall(r"(?:第?\s*\d+\s*[天日刻]|随后|接着|然后|次日|翌日)", text)
        if len(time_markers) >= 2:
            passes.append(f"时间标记 {len(time_markers)} 处")
        else:
            issues.append("时间标记不足（可能混乱）")

        # 检查 3：动机合理性（角色行为是否有解释）
        motivation = re.findall(r"(因为|为了|想要|打算|决心)(.{0,15})", text)
        if len(motivation) >= 1:
            passes.append(f"动机说明 {len(motivation)} 处")
        else:
            issues.append("动机说明不足（角色行为可能无解释）")

        # 评分
        n_checks = 3
        n_issue = len(issues)
        score = 10 - (n_issue / n_checks) * 4
        score = max(5.0, min(10.0, score))

        return DimensionScore(
            name="逻辑性",
            score=round(score, 2),
            issues=issues,
            passes=passes,
            weight=self.WEIGHTS["逻辑性"]
        )

    # ----- 维度 4：文风一致性（Style）-----
    def _score_style(self, text: str) -> DimensionScore:
        issues = []
        passes = []

        # 检查 1：AI 味信号
        ai_smells = []
        for pattern in self.AI_SMELL_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                ai_smells.extend(matches)
        if len(ai_smells) >= 3:
            issues.append(f"AI 味信号 {len(ai_smells)} 处（典型套路）")
        else:
            passes.append(f"AI 味信号 {len(ai_smells)} 处（合理）")

        # 检查 2：禁用表达
        disabled = []
        for pattern in self.DISABLED_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                disabled.extend(matches)
        if disabled:
            issues.append(f"禁用表达: {disabled[:5]}")
        else:
            passes.append("无禁用表达")

        # 检查 3：段落长度分布
        paragraphs = [p for p in text.split("\n\n") if p.strip()]
        if paragraphs:
            para_lens = [len(p) for p in paragraphs]
            avg_len = sum(para_lens) / len(para_lens)
            if avg_len < 30:
                issues.append(f"段落过短（平均 {avg_len:.0f} 字）")
            elif avg_len > 300:
                issues.append(f"段落过长（平均 {avg_len:.0f} 字）")
            else:
                passes.append(f"段落长度合理（平均 {avg_len:.0f} 字）")

        # 评分
        n_checks = 3
        n_issue = len(issues)
        score = 10 - (n_issue / n_checks) * 5
        score = max(5.0, min(10.0, score))

        return DimensionScore(
            name="文风一致性",
            score=round(score, 2),
            issues=issues,
            passes=passes,
            weight=self.WEIGHTS["文风一致性"]
        )

    # ----- 维度 5：非重复性（Non-Repetition）-----
    def _score_repetition(self, text: str) -> DimensionScore:
        issues = []
        passes = []

        # 检查 1：连续同句式
        sentences = re.split(r"[。！？]", text)
        sentences = [s for s in sentences if s.strip()]
        consecutive_same = 0
        max_consecutive = 0
        for i in range(1, len(sentences)):
            # 简化：检查前 5 个字符是否相同
            if sentences[i][:5] == sentences[i - 1][:5] and sentences[i][:5]:
                consecutive_same += 1
                max_consecutive = max(max_consecutive, consecutive_same)
            else:
                consecutive_same = 0
        if max_consecutive >= 3:
            issues.append(f"连续 {max_consecutive} 句同结构开头")
        else:
            passes.append("句式多样")

        # 检查 2：形容词重复
        adjectives = re.findall(r"[\u4e00-\u9fff]{2}(?=的|地|得)", text)
        from collections import Counter
        adj_counts = Counter(adjectives)
        overused = [(a, c) for a, c in adj_counts.items() if c > 3]
        if overused:
            issues.append(f"过度使用的形容词: {overused[:3]}")
        else:
            passes.append("形容词使用合理")

        # 检查 3：爽点密度
        enjoyment_count = sum(text.count(k) for k in self.ENJOYMENT_KEYWORDS)
        word_count = len(re.findall(r"[\u4e00-\u9fff]", text))
        if word_count > 0:
            density = enjoyment_count / (word_count / 1000)
            if 5 <= density <= 30:
                passes.append(f"爽点密度合理（{density:.1f} / 千字）")
            elif density < 5:
                issues.append(f"爽点偏少（{density:.1f} / 千字）")
            else:
                issues.append(f"爽点过多（{density:.1f} / 千字）")

        # 评分
        n_checks = 3
        n_issue = len(issues)
        score = 10 - (n_issue / n_checks) * 4
        score = max(5.0, min(10.0, score))

        return DimensionScore(
            name="非重复性",
            score=round(score, 2),
            issues=issues,
            passes=passes,
            weight=self.WEIGHTS["非重复性"]
        )

    def _level_to_num(self, level: str) -> int:
        """境界 → 数字"""
        mapping = {
            "练气": 1, "筑基": 2, "金丹": 3,
            "元婴": 4, "化神": 5, "凡人": 0
        }
        for k, v in mapping.items():
            if k in level:
                return v
        return 0


# ==================== CLI 入口 ====================


def main():
    parser = argparse.ArgumentParser(description="5 维章节评分")
    parser.add_argument("chapter", help="章节文件路径")
    parser.add_argument("--project-dir", default=".",
                        help="小说项目目录（默认当前）")
    parser.add_argument("--json", action="store_true",
                        help="输出 JSON 格式")
    args = parser.parse_args()

    print("=" * 70)
    print("📊 Auto-Novel · 5 维评分器")
    print("=" * 70)

    chapter_path = Path(args.chapter)
    if not chapter_path.exists():
        print(f"❌ 文件不存在: {args.chapter}")
        sys.exit(1)

    text = chapter_path.read_text(encoding="utf-8")
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    print(f"📄 章节: {chapter_path.name}")
    print(f"📏 字数: {len(chinese_chars)}")

    scorer = ChapterScorer(args.project_dir)
    result = scorer.score_chapter(text)
    result.chapter_file = chapter_path.name

    if args.json:
        print()
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print()
        print(f"【5 维评分结果】")
        print(f"总评: {result.overall} {result.status}")
        print()
        for name, dim in result.dimensions.items():
            weight_pct = int(dim['weight'] * 100)
            print(f"  {name} ({weight_pct}%): {dim['score']}/10")
            for issue in dim['issues']:
                print(f"    ❌ {issue}")
            for pass_item in dim['passes']:
                print(f"    ✅ {pass_item}")
            print()

    print("=" * 70)


if __name__ == "__main__":
    main()