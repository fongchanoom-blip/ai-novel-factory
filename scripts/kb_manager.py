#!/usr/bin/env python3
"""
5 件知识库管理器（KB Manager）

管理 5 件知识库文件 + 能力降级检测。
实现 [REF:protocol.knowledge_base_contract] 的核心功能。

5 件文件：
  1. 世界基石.md（World Foundation）
  2. 世界观规则.md（World Rules）
  3. 角色档案.md（Character Profiles）
  4. 档案事件.md（Event Archive）
  5. 文风样本.md（Style Samples）

用法：
    python3 kb_manager.py <project_dir> init      # 初始化 5 件模板
    python3 kb_manager.py <project_dir> status    # 检查状态
    python3 kb_manager.py <project_dir> validate # 验证完整性
    python3 kb_manager.py <project_dir> missing   # 列出缺失
"""

import argparse
import shutil
import sys
from pathlib import Path


KB_FILES = {
    "世界基石.md": "world_foundation",
    "世界观规则.md": "world_rules",
    "角色档案.md": "character_profiles",
    "档案事件.md": "event_archive",
    "文风样本.md": "style_samples",
}

# 能力降级表
ABILITY_MATRIX = {
    "选题": (0, []),
    "大纲": (1, ["世界观规则.md"]),
    "目录": (4, ["世界基石.md", "世界观规则.md", "角色档案.md", "档案事件.md"]),
    "草案": (3, ["世界基石.md", "角色档案.md", "文风样本.md"]),
    "正文": (5, ["世界基石.md", "世界观规则.md", "角色档案.md", "档案事件.md", "文风样本.md"]),
    "质检": (1, ["世界基石.md"]),
    "存档": (0, []),
}

MIN_SIZE = 100  # 文件至少 100 字节才算"已填"


def init_templates(project_dir: str, templates_dir: str, genre: str = None):
    """初始化 5 件知识库模板

    Args:
        project_dir: 项目目录
        templates_dir: 基础模板目录（kb-templates/）
        genre: 可选题材（玄幻仙侠/都市现代/言情古风/悬疑推理/科幻未来）
    """
    project_path = Path(project_dir)
    templates_path = Path(templates_dir)

    # 自动创建项目目录（如果不存在）
    project_path.mkdir(parents=True, exist_ok=True)

    print(f"📂 项目目录: {project_path}")
    print(f"📋 模板源: {templates_path}")
    if genre:
        print(f"🎨 题材模板: {genre}")
    print()

    # 1. 复制基础 5 件 KB
    created = 0
    skipped = 0
    for filename in KB_FILES.keys():
        target = project_path / filename
        source = templates_path / filename

        if target.exists():
            print(f"  ⏭️  {filename}: 已存在，跳过")
            skipped += 1
        else:
            if source.exists():
                shutil.copy(source, target)
                print(f"  ✅ {filename}: 已创建")
                created += 1
            else:
                target.touch()
                print(f"  ⚠️  {filename}: 模板不存在，已创建空文件")

    # 2. 如果指定 genre，复制题材特定配置
    if genre:
        genre_file = templates_path / "genre" / f"{genre}.md"
        if genre_file.exists():
            genre_target = project_path / "题材设定.md"
            if not genre_target.exists():
                shutil.copy(genre_file, genre_target)
                print(f"  ✅ 题材设定.md ({genre}): 已创建")
                created += 1
            else:
                print(f"  ⏭️  题材设定.md: 已存在，跳过")
        else:
            print(f"  ⚠️  题材模板不存在: {genre_file}")

    print()
    print(f"✅ 完成：创建 {created} 个，跳过 {skipped} 个")
    if genre:
        print(f"💡 提示：请编辑项目目录中的 题材设定.md 以适配你的故事")


def status(project_dir: str):
    """检查 5 件知识库状态"""
    project_path = Path(project_dir)

    print(f"📂 项目目录: {project_path}")
    print(f"📊 5 件知识库状态：\n")

    for filename, kb_id in KB_FILES.items():
        path = project_path / filename
        if not path.exists():
            print(f"  ❌ {filename}: 不存在")
        elif path.stat().st_size < MIN_SIZE:
            print(f"  ⚠️  {filename}: 存在但过小（{path.stat().st_size} 字节，需 ≥ {MIN_SIZE}）")
        else:
            print(f"  ✅ {filename}: 已就绪（{path.stat().st_size:,} 字节）")

    print()
    print(f"【能力状态评估】\n")
    for ability, (required_count, required_files) in ABILITY_MATRIX.items():
        missing = [f for f in required_files if not (project_path / f).exists()]
        if not missing:
            print(f"  ✅ {ability}: 可用")
        elif required_count == 0:
            print(f"  ✅ {ability}: 可用（无需文件）")
        else:
            print(f"  ⚠️  {ability}: 降级（缺失: {missing}）")


def validate(project_dir: str):
    """验证知识库完整性"""
    project_path = Path(project_dir)
    all_ok = True

    print(f"📂 项目目录: {project_path}\n")
    print(f"【完整性检查】\n")

    for filename, kb_id in KB_FILES.items():
        path = project_path / filename
        if not path.exists():
            print(f"  ❌ {filename}: 缺失")
            all_ok = False
        elif path.stat().st_size < MIN_SIZE:
            print(f"  ⚠️  {filename}: 内容过少（{path.stat().st_size} < {MIN_SIZE}）")
            all_ok = False
        else:
            # 检查文件内容（简单检查）
            content = path.read_text(encoding="utf-8")
            n_lines = len([l for l in content.split("\n") if l.strip()])
            print(f"  ✅ {filename}: {path.stat().st_size:,} bytes, {n_lines} 行")

    print()
    if all_ok:
        print("✅ 所有 5 件知识库完整")
        return 0
    else:
        print("❌ 部分知识库缺失或不完整")
        return 1


def missing(project_dir: str):
    """列出缺失的文件"""
    project_path = Path(project_dir)
    missing_files = []

    for filename in KB_FILES.keys():
        path = project_path / filename
        if not path.exists() or path.stat().st_size < MIN_SIZE:
            missing_files.append(filename)

    if not missing_files:
        print("✅ 没有缺失的知识库文件")
    else:
        print(f"❌ 缺失的文件：")
        for f in missing_files:
            print(f"  - {f}")


# ==================== CLI 入口 ====================


def main():
    parser = argparse.ArgumentParser(description="5 件知识库管理器")
    parser.add_argument("project_dir", help="小说项目目录")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init 子命令
    init_parser = subparsers.add_parser("init", help="初始化 5 件模板")
    init_parser.add_argument(
        "--templates",
        default=str(Path.home() / ".hermes/profiles/cont/skills/auto-novel/kb-templates"),
        help="模板目录"
    )
    init_parser.add_argument(
        "--genre",
        choices=["玄幻仙侠", "都市现代", "言情古风", "悬疑推理", "科幻未来"],
        default=None,
        help="题材模板（可选）"
    )

    # status 子命令
    subparsers.add_parser("status", help="检查状态")

    # validate 子命令
    subparsers.add_parser("validate", help="验证完整性")

    # missing 子命令
    subparsers.add_parser("missing", help="列出缺失")

    args = parser.parse_args()

    print("=" * 70)
    print("📚 Auto-Novel · 5 件知识库管理器")
    print("=" * 70)

    try:
        if args.command == "init":
            init_templates(args.project_dir, args.templates, genre=args.genre)
        elif args.command == "status":
            status(args.project_dir)
        elif args.command == "validate":
            sys.exit(validate(args.project_dir))
        elif args.command == "missing":
            missing(args.project_dir)
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

    print("=" * 70)


if __name__ == "__main__":
    main()