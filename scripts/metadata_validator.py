#!/usr/bin/env python3
"""
元数据验证器（Metadata Validator）

验证所有协议文件的 frontmatter 元数据完整性。
实现架构师评审的"TD-001"修复项。

要求：
  必填字段：ID, SCOPE, LOAD
  推荐字段：PRIORITY, TRIGGER, PHASE, DEPENDS, VERSION

用法：
    python3 metadata_validator.py <skill_dir>
    python3 metadata_validator.py <skill_dir> --strict
"""

import argparse
import re
import sys
from pathlib import Path


REQUIRED_FIELDS = ["ID", "SCOPE", "LOAD"]
RECOMMENDED_FIELDS = ["PRIORITY", "TRIGGER", "PHASE", "VERSION"]
ALL_FIELDS = REQUIRED_FIELDS + RECOMMENDED_FIELDS


def parse_frontmatter(text: str) -> dict:
    """解析 YAML frontmatter"""
    match = re.match(r"^---\n(.+?)\n---", text, re.DOTALL)
    if not match:
        return {}
    fm = match.group(1)
    result = {}
    for line in fm.split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result


def validate_protocol(file_path: Path) -> dict:
    """验证单个协议文件"""
    text = file_path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)

    missing_required = [f for f in REQUIRED_FIELDS if f not in fm]
    missing_recommended = [f for f in RECOMMENDED_FIELDS if f not in fm]

    return {
        "file": file_path.name,
        "path": str(file_path),
        "is_protocol": bool(fm),
        "missing_required": missing_required,
        "missing_recommended": missing_recommended,
        "id": fm.get("ID", ""),
        "scope": fm.get("SCOPE", ""),
        "load": fm.get("LOAD", ""),
    }


def main():
    parser = argparse.ArgumentParser(description="元数据验证器")
    parser.add_argument("skill_dir", help="Skill 目录路径")
    parser.add_argument("--strict", action="store_true",
                        help="严格模式（推荐字段也必须填）")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir)
    if not skill_dir.exists():
        print(f"❌ 目录不存在: {args.skill_dir}")
        sys.exit(1)

    print("=" * 70)
    print(f"📋 Auto-Novel · 元数据验证器")
    print("=" * 70)
    print(f"📂 验证目录: {skill_dir}")
    print(f"🔒 严格模式: {'是' if args.strict else '否'}")
    print()

    protocols_dir = skill_dir / "protocols"
    if not protocols_dir.exists():
        print(f"❌ protocols 目录不存在: {protocols_dir}")
        sys.exit(1)

    results = []
    for p in sorted(protocols_dir.glob("*.md")):
        results.append(validate_protocol(p))

    # 统计
    n_total = len(results)
    n_with_fm = sum(1 for r in results if r["is_protocol"])
    n_complete = sum(
        1 for r in results
        if not r["missing_required"] and (not args.strict or not r["missing_recommended"])
    )
    n_missing_required = sum(1 for r in results if r["missing_required"])

    # 输出详细结果
    print(f"【验证结果】\n")
    for r in results:
        if not r["is_protocol"]:
            print(f"  ⚠️  {r['file']}: 不是协议文件（无 frontmatter）")
            continue

        status = "✅" if (not r["missing_required"] and
                          (not args.strict or not r["missing_recommended"])) else "❌"

        print(f"  {status} {r['file']}")
        print(f"     ID: {r['id']}")
        print(f"     SCOPE: {r['scope']}")
        print(f"     LOAD: {r['load']}")

        if r["missing_required"]:
            print(f"     缺少必填: {r['missing_required']}")
        if r["missing_recommended"]:
            print(f"     缺少推荐: {r['missing_recommended']}")
        print()

    # 汇总
    print("=" * 70)
    print(f"【汇总】")
    print(f"  协议文件总数: {n_total}")
    print(f"  有 frontmatter: {n_with_fm}")
    print(f"  完整 ({'严格' if args.strict else '宽松'}): {n_complete}")
    print(f"  缺少必填字段: {n_missing_required}")

    if n_missing_required == 0 and (not args.strict or n_complete == n_total):
        print(f"\n✅ 所有协议文件元数据完整")
        sys.exit(0)
    else:
        print(f"\n❌ 部分协议文件元数据不完整")
        sys.exit(1)


if __name__ == "__main__":
    main()