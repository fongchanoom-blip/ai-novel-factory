#!/usr/bin/env python3
"""
事实提取器（Fact Extractor）

从章节正文中提取事实，生成事实锁（fact_locks/）。
实现 [REF:protocol.fact_lock] 的核心功能。

用法：
    python3 fact_extractor.py <chapter_file> [--project-dir <dir>]

示例：
    python3 fact_extractor.py chapter_001.md
    python3 fact_extractor.py chapter_001.md --project-dir ~/my-novel/

设计参考：
    - 8 大事实类别（资源/时间/地点/角色认知/信息传播/能力/身份/伤势）
    - SHA-256 哈希证据链
    - 冲突检测（vs 已存在事实锁）
"""

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Optional


# ==================== 数据模型 ====================


@dataclass
class Fact:
    """单条事实锁"""
    id: str
    content: str
    category: str
    source_file: str
    source_line: int
    source_hash: str
    anchor_chapter: int
    anchor_paragraph: int
    anchor_hash: str
    confidence: float = 100.0
    created_at: str = ""
    status: str = "active"
    related_facts: list = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


# ==================== 8 大类别正则模式 ====================


PATTERNS = {
    "resources": [
        # 灵石/金钱/资源
        (r"(\d+)\s*(灵石|银两|金币|元石|仙晶)", "数量 + 货币"),
        (r"拥有[了]?\s*(\d+)\s*(件|把|颗|枚|本|张)([^，。\s]+)", "物品"),
        (r"获得了?\s*([^，。\s]{2,8}(?:符箓|剑|刀|丹|法器|灵器|法宝))", "获得物品"),
    ],
    "time": [
        (r"第?\s*(\d+)\s*(天|日|年|月|个时辰|柱香)[时后]", "时间"),
        (r"(清晨|傍晚|夜晚|白天|深夜|凌晨|正午|子时|午时|申时)", "时段"),
        (r"(春天|夏天|秋天|冬天|春季|夏季|秋季|冬季)", "季节"),
    ],
    "location": [
        (r"(在|来到|抵达|进入|到达)\s*([^，。]{2,12}(?:宗|派|殿|城|山|谷|楼|阁|院|府|宫|塔))", "地点"),
        (r"距离[最近]?\s*([^，。]{2,8})\s*(?:约|大概)?\s*(\d+)\s*(天|日|里|步|丈)", "距离"),
    ],
    "character_knowledge": [
        (r"([^，。]{1,6})知道([^，。]{2,30})的(?:真相|秘密|来历)", "知道秘密"),
        (r"([^，。]{1,6})不知道([^，。]{2,30})", "不知道信息"),
        (r"([^，。]{1,6})发现[了]?([^，。]{2,30})", "发现"),
        (r"([^，。]{1,6})怀疑([^，。]{2,30})", "怀疑"),
    ],
    "information_propagation": [
        (r"([^，。]{1,6})告诉[了]?([^，。]{1,6})([^，。]{2,30})", "信息传递"),
        (r"([^，。]{1,6})隐瞒[了]?([^，。]{1,6})([^，。]{2,30})", "信息隐瞒"),
        (r"([^，。]{1,6})从未告诉([^，。]{2,30})", "未告知"),
    ],
    "powers": [
        (r"(修为|境界|等级)[:：]?\s*(筑基期|金丹期|元婴期|化神期|练气期|凡人[境]?)", "修为等级"),
        (r"每日[最多]?\s*(?:可[以]?)?(?:使用)?\s*(\d+)\s*次", "使用次数"),
        (r"(天赋|血脉|异能|能力)[:：]?\s*([^，。]{2,12})", "能力"),
        (r"(修炼|突破|升级)[到至]?\s*([^，。]{2,8})", "修为变化"),
    ],
    "identity": [
        (r"身份[:：]?\s*([^，。]{2,20})", "身份"),
        (r"是\s*(青云宗|玄天宗|魔教|正派|反派)(|的)?\s*([^，。]{2,8})", "门派身份"),
        (r"(?:真实|真正)的身份是([^，。]{2,20})", "真实身份"),
    ],
    "injuries": [
        (r"(中毒|受伤|负伤|中剑|中招)[了]?\s*([^，。]{2,20})", "受伤"),
        (r"(右臂|左臂|右腿|左腿|胸口|背部)\s*(?:中毒|受伤|疼痛)", "部位受伤"),
        (r"(康复|痊愈|恢复)[了]?\s*(\d+%)?", "伤势恢复"),
    ],
}


# ==================== 核心类 ====================


class FactExtractor:
    """事实提取器"""

    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.fact_locks_dir = self.project_dir / "fact_locks"
        self.active_dir = self.fact_locks_dir / "active"
        self.superseded_dir = self.fact_locks_dir / "superseded"
        self.contested_dir = self.fact_locks_dir / "contested"
        self.archive_dir = self.project_dir / "archives"

        # 创建目录
        for d in [self.active_dir, self.superseded_dir, self.contested_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.existing_facts: dict = {}
        self._load_existing_facts()

    def _load_existing_facts(self):
        """加载已存在的事实锁"""
        for fact_file in self.active_dir.glob("FL-*.yaml"):
            try:
                with open(fact_file, encoding="utf-8") as f:
                    fact = yaml.safe_load(f)
                    if fact and "id" in fact:
                        self.existing_facts[fact["id"]] = fact
            except Exception:
                pass

    def _compute_hash(self, text: str) -> str:
        """计算 SHA-256 哈希（取前 16 字符）"""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

    def _generate_id(self) -> str:
        """生成事实锁 ID"""
        n = len(self.existing_facts) + 1
        return f"FL-{n:04d}"

    def extract_from_chapter(self, chapter_path: Path) -> list:
        """从章节中提取事实"""
        if not chapter_path.exists():
            raise FileNotFoundError(f"章节文件不存在: {chapter_path}")

        text = chapter_path.read_text(encoding="utf-8")
        lines = text.split("\n")
        chapter_num = self._extract_chapter_num(chapter_path.name)

        facts = []
        for category, patterns in PATTERNS.items():
            for pattern, _desc in patterns:
                for match in re.finditer(pattern, text):
                    start = match.start()
                    line_num = text[:start].count("\n") + 1
                    paragraph_num = self._line_to_paragraph(lines, line_num)

                    content = match.group(0)
                    fact = Fact(
                        id=self._generate_id(),
                        content=content,
                        category=category,
                        source_file=chapter_path.name,
                        source_line=line_num,
                        source_hash=self._compute_hash(content),
                        anchor_chapter=chapter_num,
                        anchor_paragraph=paragraph_num,
                        anchor_hash=self._compute_hash(lines[line_num - 1]),
                        created_at=datetime.now().isoformat(),
                        confidence=85.0,  # 正则匹配的默认置信度
                    )
                    facts.append(fact)

        return facts

    def _extract_chapter_num(self, filename: str) -> int:
        """从文件名提取章节号"""
        match = re.search(r"chapter[_\s]*(\d+)|第\s*(\d+)\s*章", filename)
        if match:
            return int(match.group(1) or match.group(2))
        return 0

    def _line_to_paragraph(self, lines: list, line_num: int) -> int:
        """行号转段号"""
        para = 1
        for i in range(line_num - 1):
            if lines[i].strip() == "" and i > 0 and lines[i - 1].strip() != "":
                para += 1
        return para

    def detect_conflicts(self, new_facts: list) -> list:
        """检测新事实 vs 已有事实的冲突"""
        conflicts = []
        for new_fact in new_facts:
            for old_id, old_fact in self.existing_facts.items():
                if self._is_conflict(new_fact, old_fact):
                    conflicts.append((new_fact, old_fact))
        return conflicts

    def _is_conflict(self, new: Fact, old: dict) -> bool:
        """判断两条事实是否冲突"""
        # 同一类别的相似内容才可能冲突
        if new.category != old.get("category"):
            return False

        # 简化：同类别 + 相似关键词 = 冲突
        new_words = set(new.content)
        old_words = set(old.get("content", ""))
        overlap = new_words & old_words
        if len(overlap) >= 2:  # 至少 2 个词相同
            # 检查是否有数字冲突
            new_nums = re.findall(r"\d+", new.content)
            old_nums = re.findall(r"\d+", old.get("content", ""))
            if new_nums and old_nums and new_nums != old_nums:
                return True
        return False

    def save_facts(self, facts: list, conflicts: list = None):
        """保存事实锁"""
        saved = 0
        superseded = 0
        contested = 0

        for fact in facts:
            # 检查是否与已有事实冲突
            has_conflict = False
            if conflicts:
                for new_f, old_f in conflicts:
                    if new_f.id == fact.id:
                        fact.status = "contested"
                        has_conflict = True
                        contested += 1
                        break

            if not has_conflict:
                # 保存到 active/
                path = self.active_dir / f"{fact.id}.yaml"
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self._fact_to_yaml(fact))
                saved += 1
                self.existing_facts[fact.id] = fact.to_dict()
            else:
                # 保存到 contested/
                path = self.contested_dir / f"{fact.id}.yaml"
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self._fact_to_yaml(fact))
                saved += 1

        return {
            "saved": saved,
            "contested": contested,
            "total_existing": len(self.existing_facts)
        }

    def _fact_to_yaml(self, fact: Fact) -> str:
        """事实锁 → YAML（手动实现，避免依赖）"""
        lines = [
            f"id: {fact.id}",
            f"content: \"{fact.content}\"",
            f"category: {fact.category}",
            f"source:",
            f"  file: {fact.source_file}",
            f"  line: {fact.source_line}",
            f"  hash: {fact.source_hash}",
            f"anchor:",
            f"  chapter: {fact.anchor_chapter}",
            f"  paragraph: {fact.anchor_paragraph}",
            f"  hash: {fact.anchor_hash}",
            f"confidence: {fact.confidence}",
            f"created_at: \"{fact.created_at}\"",
            f"status: {fact.status}",
            "related_facts: []",
        ]
        return "\n".join(lines) + "\n"


# ==================== YAML 简化实现 ====================


class SimpleYAML:
    """极简 YAML 解析器（仅支持读取，避免外部依赖）"""

    @staticmethod
    def safe_load(text: str) -> dict:
        """解析 YAML 为 dict（仅支持键值对）"""
        result = {}
        current_key = None
        current_dict = result
        stack = [(result, -1)]
        indent_stack = [0]

        for line in text.split("\n"):
            if not line.strip() or line.strip().startswith("#"):
                continue
            indent = len(line) - len(line.lstrip())
            content = line.strip()

            # 处理列表项
            if content.startswith("- "):
                continue

            if ":" in content:
                key, _, value = content.partition(":")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                current_dict[key] = value

        return result


yaml = SimpleYAML()


# ==================== CLI 入口 ====================


def main():
    parser = argparse.ArgumentParser(description="从章节提取事实锁")
    parser.add_argument("chapter", help="章节文件路径")
    parser.add_argument("--project-dir", default=".",
                        help="小说项目目录（默认当前）")
    parser.add_argument("--no-conflict-check", action="store_true",
                        help="跳过冲突检测")
    args = parser.parse_args()

    print("=" * 70)
    print("📋 Auto-Novel · 事实提取器")
    print("=" * 70)
    print(f"📂 项目目录: {args.project_dir}")
    print(f"📄 章节文件: {args.chapter}")
    print()

    try:
        extractor = FactExtractor(args.project_dir)
        chapter_path = Path(args.chapter)
        facts = extractor.extract_from_chapter(chapter_path)
        print(f"✅ 提取到 {len(facts)} 条事实")

        conflicts = []
        if not args.no_conflict_check and facts:
            conflicts = extractor.detect_conflicts(facts)
            if conflicts:
                print(f"⚠️  发现 {len(conflicts)} 处冲突")

        if facts:
            stats = extractor.save_facts(facts, conflicts)
            print(f"\n📊 保存结果：")
            print(f"   新增事实: {stats['saved']}")
            print(f"   冲突事实: {stats['contested']}")
            print(f"   已有事实总数: {stats['total_existing']}")

            print(f"\n📁 输出位置：")
            print(f"   active/: {extractor.active_dir}")
            print(f"   superseded/: {extractor.superseded_dir}")
            print(f"   contested/: {extractor.contested_dir}")

            # 显示前 5 条事实
            print(f"\n📋 前 5 条事实预览：")
            for f in facts[:5]:
                    print(f"  [{f.id}] {f.category}: {f.content[:50]}")

        print("\n" + "=" * 70)
        print("✅ 完成")
        print("=" * 70)

    except FileNotFoundError as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()