#!/usr/bin/env python3
"""
事实提取器 - LLM 增强版（Fact Extractor LLM-Enhanced）

v1.0.6 新增：可选 LLM 增强事实提取

相比基础版（fact_extractor.py）：
- ✅ 调用 LLM 深度理解正文
- ✅ 提取更准确的事实（不依赖正则）
- ✅ 自动分类到 8 大类别
- ✅ 自动检测冲突

兼容模式：
- 默认：fallback 到规则版（无需 API Key）
- --mode llm：使用 LLM 提取
- --mode hybrid：先规则后 LLM 补充

用法：
    python3 fact_extractor_llm.py <chapter_file> --mode llm
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

# 复用基础版
sys.path.insert(0, str(Path(__file__).parent))
from fact_extractor import Fact, FactExtractor, SimpleYAML, yaml

# 复用 LLM 客户端
from llm_client import LLMClient


EXTRACTION_PROMPT = """你是一位严谨的小说事实核查员，正在从章节中提取**关键事实**。

【章节正文】
{text}

【已有事实锁】（避免重复）
{existing_facts}

请从章节中提取最多 10 条最重要的新事实，覆盖以下类型：
- resources（资源）：灵石/装备/物品
- time（时间）：天数/时段
- location（地点）：地名/距离
- character_knowledge（角色认知）：谁知道了什么
- information_propagation（信息传递）：谁告诉谁
- powers（能力）：境界/技能/限制
- identity（身份）：身份/门派
- injuries（伤势）：受伤/恢复

输出严格按以下 JSON 格式：

```json
[
  {{
    "category": "resources",
    "content": "100 灵石",
    "context": "张三在坊市购买时付出"
  }},
  ...
]
```

只输出 JSON，不要其他文字。"""


class LLMFactExtractor(FactExtractor):
    """LLM 增强版事实提取器"""

    def __init__(self, project_dir: str, use_llm: bool = True):
        super().__init__(project_dir)
        self.use_llm = use_llm
        self.llm_client = LLMClient() if use_llm else None

    def extract_from_chapter(self, chapter_path: Path) -> list:
        """从章节提取事实（LLM + 规则 fallback）"""
        # 1. 先用规则版（确保至少有结果）
        rule_facts = super().extract_from_chapter(chapter_path)

        if not self.use_llm or not self.llm_client:
            return rule_facts

        # 2. 检查 API Key
        status = self.llm_client.get_status()
        if not any(status["api_key_set"].values()):
            return rule_facts  # 降级

        # 3. LLM 增强
        text = chapter_path.read_text(encoding="utf-8")
        existing = [f"{f['content']}" for f in self.existing_facts.values()]
        existing_text = "\n".join(existing[:20]) if existing else "（无）"

        prompt = EXTRACTION_PROMPT.format(
            text=text[:3000],
            existing_facts=existing_text
        )

        response = self.llm_client.call(prompt, max_tokens=2000)
        if not response or response.startswith("["):
            return rule_facts

        # 4. 解析 LLM 响应
        llm_facts = self._parse_llm_response(response, chapter_path)
        if not llm_facts:
            return rule_facts

        # 5. 合并（LLM 提取的优先级更高）
        all_facts = llm_facts + rule_facts

        # 6. 去重（基于 content）
        seen = set()
        unique_facts = []
        for f in all_facts:
            key = f.content[:30]
            if key not in seen:
                seen.add(key)
                unique_facts.append(f)

        # 重新分配 ID
        for i, f in enumerate(unique_facts):
            f.id = f"FL-{len(self.existing_facts) + i + 1:04d}"

        return unique_facts

    def _parse_llm_response(self, response: str, chapter_path: Path) -> list:
        """解析 LLM 响应为 Fact 列表"""
        # 提取 JSON 块
        json_match = re.search(r"```json\s*\n(.*?)\n```", response, re.DOTALL)
        if not json_match:
            json_match = re.search(r"\[\s*\{.*?\}\s*\]", response, re.DOTALL)

        if not json_match:
            return []

        try:
            data = json.loads(json_match.group(1) if "```" in response else json_match.group(0))
        except json.JSONDecodeError:
            return []

        if not isinstance(data, list):
            return []

        # 转换为 Fact
        chapter_num = self._extract_chapter_num(chapter_path.name)
        facts = []
        for item in data[:10]:  # 限制最多 10 条
            if not isinstance(item, dict):
                continue

            content = item.get("content", "").strip()
            if not content:
                continue

            category = item.get("category", "unknown")
            if category not in [
                "resources", "time", "location", "character_knowledge",
                "information_propagation", "powers", "identity", "injuries"
            ]:
                category = "unknown"

            # 找到 content 在原文中的位置
            text = chapter_path.read_text(encoding="utf-8")
            pos = text.find(content[:20])
            if pos == -1:
                # 尝试部分匹配
                pos = text.find(content[:10])
            line_num = text[:pos].count("\n") + 1 if pos >= 0 else 1

            fact = Fact(
                id="FL-TEMP",  # 稍后重新分配
                content=content,
                category=category,
                source_file=chapter_path.name,
                source_line=line_num,
                source_hash=self._compute_hash(content),
                anchor_chapter=chapter_num,
                anchor_paragraph=1,
                anchor_hash=self._compute_hash(text.split("\n")[0]) if text else "",
                created_at=datetime.now().isoformat(),
                confidence=95.0,  # LLM 提取的置信度更高
            )
            facts.append(fact)

        return facts


def main():
    parser = argparse.ArgumentParser(description="事实提取器（LLM 增强版）")
    parser.add_argument("chapter", help="章节文件")
    parser.add_argument("--project-dir", default=".", help="项目目录")
    parser.add_argument("--mode", choices=["rule", "llm", "hybrid"],
                        default="hybrid", help="模式")
    args = parser.parse_args()

    print("=" * 70)
    print("📋 Auto-Novel · 事实提取器（LLM 增强版）")
    print("=" * 70)

    extractor = LLMFactExtractor(args.project_dir, use_llm=args.mode != "rule")
    chapter_path = Path(args.chapter)

    if args.mode in ["llm", "hybrid"]:
        client = LLMClient()
        status = client.get_status()
        any_key = any(status["api_key_set"].values())
        print(f"🔑 API Key: {'已配置' if any_key else '未配置（将降级为规则版）'}")

    facts = extractor.extract_from_chapter(chapter_path)

    if facts:
        # 冲突检测
        conflicts = extractor.detect_conflicts(facts)
        stats = extractor.save_facts(facts, conflicts)
        print(f"\n✅ 提取到 {len(facts)} 条事实")
        print(f"📊 保存: {stats['saved']}, 冲突: {stats['contested']}")

    print("=" * 70)


if __name__ == "__main__":
    main()