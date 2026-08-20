#!/usr/bin/env python3
"""
同步脚本（从自用版到发布版）

用法:
    python3 sync_publish.py                    # 默认路径
    python3 sync_publish.py --dry-run          # 仅显示差异
    python3 sync_publish.py --source <path>    # 自定义源
    python3 sync_publish.py --target <path>    # 自定义目标
    python3 sync_publish.py --check            # 检查一致性

设计:
    - 同步 core/protocols/constants/references/kb-templates/scripts/web
    - 不同步 SKILL.md, META_TAGS.md, README.md, CHANGELOG.md（发布版独有）
    - 自动检测新增/修改/删除
"""

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


DEFAULT_SOURCE = Path.home() / ".hermes/profiles/cont/skills/auto-novel"
DEFAULT_TARGET = Path.home() / "projects/auto-novel-public"

# 同步目录（双向一致）
SYNC_DIRS = [
    "core",
    "protocols",
    "constants",
    "references",
    "kb-templates",
    "scripts",
    "web",
    "examples",
    "docs",
]


def file_hash(path: Path) -> str:
    """计算文件 MD5"""
    content = path.read_bytes()
    return hashlib.md5(content).hexdigest()


def collect_files(directory: Path) -> dict:
    """收集目录下所有文件的相对路径 -> 哈希"""
    files = {}
    if not directory.exists():
        return files
    for f in directory.rglob("*"):
        if f.is_file():
            rel = f.relative_to(directory)
            files[str(rel)] = file_hash(f)
    return files


def sync(source: Path, target: Path, dry_run: bool = False, verbose: bool = True):
    """执行同步"""
    print(f"📂 源目录: {source}")
    print(f"📂 目标目录: {target}")
    print()

    if not source.exists():
        print(f"❌ 源目录不存在: {source}")
        return False

    if not target.exists():
        if dry_run:
            print(f"❌ 目标目录不存在（dry-run 不会创建）: {target}")
            return False
        target.mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目标目录: {target}")

    # 收集源/目标文件
    source_files = {}
    target_files = {}

    for d in SYNC_DIRS:
        src_d = source / d
        tgt_d = target / d

        if src_d.exists():
            for f in src_d.rglob("*"):
                if f.is_file():
                    rel = str(f.relative_to(src_d))
                    source_files[f"{d}/{rel}"] = file_hash(f)

        if tgt_d.exists():
            for f in tgt_d.rglob("*"):
                if f.is_file():
                    rel = str(f.relative_to(tgt_d))
                    target_files[f"{d}/{rel}"] = file_hash(f)

    # 计算差异
    to_add = []
    to_update = []
    to_delete = []

    for f, h in source_files.items():
        if f not in target_files:
            to_add.append(f)
        elif target_files[f] != h:
            to_update.append(f)

    for f in target_files:
        if f not in source_files:
            to_delete.append(f)

    # 输出差异
    print(f"📊 同步差异:")
    print(f"  新增: {len(to_add)}")
    print(f"  修改: {len(to_update)}")
    print(f"  删除: {len(to_delete)}")
    print()

    if to_add:
        print(f"📄 新增文件:")
        for f in sorted(to_add)[:10]:
            print(f"  + {f}")
        if len(to_add) > 10:
            print(f"  ... 还有 {len(to_add) - 10} 个")
        print()

    if to_update:
        print(f"📝 修改文件:")
        for f in sorted(to_update)[:10]:
            print(f"  ~ {f}")
        if len(to_update) > 10:
            print(f"  ... 还有 {len(to_update) - 10} 个")
        print()

    if to_delete:
        # 发布版独有的文件，不删除
        PROTECTED_FILES = {
            "docs/API.md",
            "docs/LLM_SETUP.md",
            "docs/QUICKSTART.md",
        }
        filtered_delete = [f for f in to_delete if f not in PROTECTED_FILES]

        if filtered_delete:
            print(f"🗑️ 删除文件:")
            for f in sorted(filtered_delete)[:10]:
                print(f"  - {f}")
            if len(filtered_delete) > 10:
                print(f"  ... 还有 {len(filtered_delete) - 10} 个")
            print()

        if len(filtered_delete) != len(to_delete):
            protected = [f for f in to_delete if f in PROTECTED_FILES]
            if protected:
                print(f"🔒 受保护文件（发布版独有，不删除）:")
                for f in protected:
                    print(f"  ⊘ {f}")
                print()

    if dry_run:
        print("🔍 dry-run：不实际复制")
        return True

    # 执行同步
    copied = 0
    for f in to_add + to_update:
        src_file = source / f
        tgt_file = target / f
        tgt_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src_file, tgt_file)
        copied += 1

    deleted = 0
    for f in filtered_delete:
        tgt_file = target / f
        if tgt_file.exists():
            tgt_file.unlink()
            deleted += 1

    print(f"✅ 同步完成: 复制 {copied} 个，删除 {deleted} 个")

    return True


def check(source: Path, target: Path) -> bool:
    """检查一致性"""
    print(f"🔍 检查一致性: {source} ↔ {target}")
    print()

    diff_count = 0

    for d in SYNC_DIRS:
        src_d = source / d
        tgt_d = target / d

        if not src_d.exists():
            continue

        src_files = collect_files(src_d)
        tgt_files = collect_files(tgt_d)

        for rel, h in src_files.items():
            key = f"{d}/{rel}"
            if key not in tgt_files:
                print(f"  ❌ 缺失: {key}")
                diff_count += 1
            elif tgt_files[key] != h:
                print(f"  ⚠️ 不一致: {key}")
                diff_count += 1

    if diff_count == 0:
        print("✅ 完全一致")
        return True
    else:
        print(f"\n❌ 发现 {diff_count} 处差异")
        return False


def main():
    parser = argparse.ArgumentParser(description="同步自用版到发布版")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE), help="源目录（自用版）")
    parser.add_argument("--target", default=str(DEFAULT_TARGET), help="目标目录（发布版）")
    parser.add_argument("--dry-run", action="store_true", help="仅显示差异")
    parser.add_argument("--check", action="store_true", help="仅检查一致性")
    args = parser.parse_args()

    source = Path(args.source)
    target = Path(args.target)

    print("=" * 70)
    print(f"🔄 Auto-Novel Skill · 同步脚本")
    print("=" * 70)
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    if args.check:
        success = check(source, target)
    else:
        success = sync(source, target, dry_run=args.dry_run)

    print("=" * 70)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())