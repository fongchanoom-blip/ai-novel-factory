"""
LLM 客户端包装（Web 界面用）

提供 settings 获取/设置 + 评分调用 + 提取调用
"""

import os
import sys
from pathlib import Path

# 复用 scripts/
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from llm_client import LLMClient, DEFAULT_CONFIG


def get_settings() -> dict:
    """获取当前 LLM 配置"""
    client = LLMClient()
    return client.get_status()


def update_settings(provider: str, model: str, api_key: str = "") -> str:
    """更新 LLM 配置

    Args:
        provider: deepseek / anthropic / openai / zhipu
        model: 模型名
        api_key: API Key（可选，留空则复用环境变量）

    Returns:
        状态消息
    """
    # API Key 写入环境变量
    if api_key.strip():
        env_var = f"{provider.upper()}_API_KEY"
        os.environ[env_var] = api_key

    # 校验
    client = LLMClient({"provider": provider, "model": model})
    status = client.get_status()

    if status["api_key_set"][provider]:
        return f"✅ 已切换到 {provider} ({model})"
    else:
        return f"⚠️ {provider} 未配置 API Key（请设置环境变量 {provider.upper()}_API_KEY）"


def call_llm_for_score(chapter_text: str, dimension: str, project_dir: str = ".") -> str:
    """用 LLM 评分单个维度"""
    client = LLMClient()
    status = client.get_status()

    if not any(status["api_key_set"].values()):
        return "❌ 请先配置 API Key"

    # 读取项目上下文
    style_sample = ""
    profiles = ""
    style_file = Path(project_dir) / "文风样本.md"
    profiles_file = Path(project_dir) / "角色档案.md"
    if style_file.exists():
        style_sample = style_file.read_text(encoding="utf-8")[:1000]
    if profiles_file.exists():
        profiles = profiles_file.read_text(encoding="utf-8")[:1000]

    prompts = {
        "style": f"作为网文编辑，评估以下章节的文风一致性（0-10 分）。\n\n文风样本：\n{style_sample or '（无）'}\n\n章节：\n{chapter_text[:3000]}\n\n输出格式：SCORE: X.X\n理由：...",
        "repetition": f"作为网文编辑，评估以下章节的非重复性（0-10 分）。\n\n章节：\n{chapter_text[:3000]}\n\n输出格式：SCORE: X.X\n理由：...",
        "ooc": f"作为网文编辑，评估以下章节的人设一致性（OOC，0-10 分）。\n\n角色设定：\n{profiles or '（无）'}\n\n章节：\n{chapter_text[:3000]}\n\n输出格式：SCORE: X.X\n理由：...",
    }

    if dimension not in prompts:
        return f"❌ 未知维度: {dimension}"

    response = client.call(prompts[dimension], max_tokens=800)
    return response


def call_llm_for_extract(chapter_text: str, project_dir: str = ".") -> str:
    """用 LLM 提取事实"""
    client = LLMClient()
    if not any(client.get_status()["api_key_set"].values()):
        return "❌ 请先配置 API Key"

    # 读取已有事实
    existing = ""
    active_dir = Path(project_dir) / "fact_locks" / "active"
    if active_dir.exists():
        facts = []
        for f in list(active_dir.glob("FL-*.yaml"))[:10]:
            try:
                content = f.read_text(encoding="utf-8")
                for line in content.split("\n"):
                    if line.startswith("content:"):
                        facts.append(line.split(":", 1)[1].strip())
                        break
            except Exception:
                pass
        existing = "\n".join(facts)

    prompt = f"""从以下章节中提取最多 10 条关键事实（已存在的事无需重复）：

【已有事实】
{existing or '（无）'}

【章节】
{chapter_text[:3000]}

输出 JSON 数组，每项含 category（8 大类之一）和 content。"""

    response = client.call(prompt, max_tokens=2000)
    return response


def call_llm_for_chapter(prompt: str, target_words: int, project_dir: str = ".") -> str:
    """用 LLM 生成章节"""
    client = LLMClient()
    if not any(client.get_status()["api_key_set"].values()):
        return "❌ 请先配置 API Key"

    # 读取文风样本 + 角色档案
    style_sample = ""
    profiles = ""
    style_file = Path(project_dir) / "文风样本.md"
    profiles_file = Path(project_dir) / "角色档案.md"
    if style_file.exists():
        style_sample = style_file.read_text(encoding="utf-8")[:1500]
    if profiles_file.exists():
        profiles = profiles_file.read_text(encoding="utf-8")[:1500]

    system = f"""你是一位专业网文作者。

【文风样本】
{style_sample or '（无）'}

【角色档案】
{profiles or '（无）'}

请基于以上设定，生成章节正文。"""

    full_prompt = f"{prompt}\n\n目标字数：约 {target_words} 字"

    response = client.call(full_prompt, system=system, max_tokens=target_words * 2)
    return response
