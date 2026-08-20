"""Auto-Novel CLI 入口"""

import sys
import argparse
from pathlib import Path


def main():
    """CLI 主入口"""
    parser = argparse.ArgumentParser(
        prog="auto-novel",
        description="Auto-Novel Skill - AI 中文长篇创作"
    )
    subparsers = parser.add_subparsers(dest="command")

    # init
    init_parser = subparsers.add_parser("init", help="初始化新项目")
    init_parser.add_argument("project_dir", help="项目目录")
    init_parser.add_argument(
        "--genre",
        choices=["玄幻仙侠", "都市现代", "言情古风", "悬疑推理", "科幻未来"],
        default=None,
        help="题材模板"
    )

    # score
    score_parser = subparsers.add_parser("score", help="评分章节")
    score_parser.add_argument("chapter", help="章节文件")

    # web
    web_parser = subparsers.add_parser("web", help="启动 Web 界面")

    args = parser.parse_args()

    if args.command == "init":
        from scripts.kb_manager import init_templates
        skill_dir = Path(__file__).parent.parent
        templates_dir = skill_dir / "kb-templates"
        init_templates(args.project_dir, str(templates_dir), genre=args.genre)
    elif args.command == "score":
        from scripts.chapter_scorer import main as score_main
        sys.argv = ["chapter_scorer.py", args.chapter]
        score_main()
    elif args.command == "web":
        from web.app import main
        main()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()