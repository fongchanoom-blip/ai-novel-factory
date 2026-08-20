"""Auto-Novel Skill · Python 包入口"""

__version__ = "1.0.7"
__author__ = "Auto-Novel Contributors"
__license__ = "MIT"


def get_skill_dir():
    """获取 skill 根目录"""
    from pathlib import Path
    return Path(__file__).parent.parent


def get_protocols_dir():
    """获取协议目录"""
    return get_skill_dir() / "protocols"


def get_kb_templates_dir():
    """获取知识库模板目录"""
    return get_skill_dir() / "kb-templates"


def get_scripts_dir():
    """获取脚本目录"""
    return get_skill_dir() / "scripts"