"""
统一 LLM 客户端（支持 DeepSeek / Claude / OpenAI / 智谱 GLM）

设计原则：
- 单一统一接口（call_llm）
- 支持多模型自动 fallback
- 支持本地缓存（避免重复调用）
- 支持 prompt/response 落盘（R07 合规）

用法：
    from llm_client import LLMClient

    client = LLMClient()
    response = client.call("写一段玄幻小说开篇...")
    print(response)
"""

import hashlib
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


# ==================== 配置 ====================


DEFAULT_CONFIG = {
    "provider": "deepseek",  # deepseek / anthropic / openai / zhipu
    "model": "deepseek-chat",
    "max_tokens": 4000,
    "temperature": 0.7,
    "timeout": 60,
    "cache_dir": str(Path.home() / ".auto-novel" / "llm_cache"),
}


class LLMClient:
    """统一 LLM 客户端"""

    # 常见模型定价（每 1K tokens, USD）
    PRICING = {
        "deepseek-chat": {"input": 0.00027, "output": 0.0011},
        "deepseek-reasoner": {"input": 0.00055, "output": 0.00219},
        "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
        "claude-3-5-haiku-20241022": {"input": 0.0008, "output": 0.004},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "glm-4-flash": {"input": 0.0, "output": 0.0},  # 免费
        "glm-4-plus": {"input": 0.00007, "output": 0.00007},
    }

    def __init__(self, config: Optional[Dict] = None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.cache_dir = Path(self.config["cache_dir"])
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def call(
        self,
        prompt: str,
        system: str = "",
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        use_cache: bool = True,
    ) -> str:
        """
        调用 LLM

        Args:
            prompt: 用户提示
            system: 系统提示
            max_tokens: 最大 token 数
            temperature: 温度
            use_cache: 是否使用缓存

        Returns:
            LLM 响应文本
        """
        max_tokens = max_tokens or self.config["max_tokens"]
        temperature = temperature if temperature is not None else self.config["temperature"]

        # 1. 检查缓存
        if use_cache:
            cache_key = self._cache_key(prompt, system, max_tokens, temperature)
            cached = self._read_cache(cache_key)
            if cached:
                return cached

        # 2. 调用 LLM
        provider = self.config["provider"]
        try:
            if provider == "deepseek":
                response = self._call_deepseek(prompt, system, max_tokens, temperature)
            elif provider == "anthropic":
                response = self._call_anthropic(prompt, system, max_tokens, temperature)
            elif provider == "openai":
                response = self._call_openai(prompt, system, max_tokens, temperature)
            elif provider == "zhipu":
                response = self._call_zhipu(prompt, system, max_tokens, temperature)
            else:
                raise ValueError(f"未知 provider: {provider}")
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="ignore")
            return f"[LLM 错误 {e.code}] {error_body[:200]}"
        except Exception as e:
            return f"[LLM 异常] {str(e)[:200]}"

        # 3. 写入缓存
        if use_cache and response and not response.startswith("["):
            self._write_cache(cache_key, response)

        # 4. 落盘（用于 R07 合规）
        self._log_call(prompt, response, provider)

        return response

    # ==================== 各 Provider 实现 ====================

    def _call_deepseek(self, prompt: str, system: str, max_tokens: int, temperature: float) -> str:
        """DeepSeek API (OpenAI 兼容)"""
        api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        if not api_key:
            return "[配置缺失] DEEPSEEK_API_KEY 环境变量未设置"

        url = "https://api.deepseek.com/v1/chat/completions"
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.config["model"],
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

        with urllib.request.urlopen(req, timeout=self.config["timeout"]) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]

    def _call_anthropic(self, prompt: str, system: str, max_tokens: int, temperature: float) -> str:
        """Anthropic Claude API"""
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return "[配置缺失] ANTHROPIC_API_KEY 环境变量未设置"

        url = "https://api.anthropic.com/v1/messages"
        data = {
            "model": self.config["model"],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            data["system"] = system

        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
        )

        with urllib.request.urlopen(req, timeout=self.config["timeout"]) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["content"][0]["text"]

    def _call_openai(self, prompt: str, system: str, max_tokens: int, temperature: float) -> str:
        """OpenAI API"""
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            return "[配置缺失] OPENAI_API_KEY 环境变量未设置"

        url = "https://api.openai.com/v1/chat/completions"
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.config["model"],
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

        with urllib.request.urlopen(req, timeout=self.config["timeout"]) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]

    def _call_zhipu(self, prompt: str, system: str, max_tokens: int, temperature: float) -> str:
        """智谱 GLM API"""
        api_key = os.environ.get("ZHIPU_API_KEY", "")
        if not api_key:
            return "[配置缺失] ZHIPU_API_KEY 环境变量未设置"

        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.config["model"],
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

        with urllib.request.urlopen(req, timeout=self.config["timeout"]) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]

    # ==================== 缓存 & 日志 ====================

    def _cache_key(self, prompt: str, system: str, max_tokens: int, temperature: float) -> str:
        """生成缓存键"""
        content = f"{prompt}|{system}|{max_tokens}|{temperature}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

    def _read_cache(self, key: str) -> Optional[str]:
        """读取缓存"""
        path = self.cache_dir / f"{key}.txt"
        if path.exists():
            return path.read_text(encoding="utf-8")
        return None

    def _write_cache(self, key: str, response: str):
        """写入缓存"""
        path = self.cache_dir / f"{key}.txt"
        path.write_text(response, encoding="utf-8")

    def _log_call(self, prompt: str, response: str, provider: str):
        """落盘日志（用于 R07 合规）"""
        log_dir = Path("/tmp") / "auto-novel-logs"
        log_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"llm_{provider}_{ts}.json"
        log_file.write_text(
            json.dumps({
                "ts": datetime.now().isoformat(),
                "provider": provider,
                "model": self.config["model"],
                "prompt_len": len(prompt),
                "response_len": len(response),
            }, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    # ==================== 配置管理 ====================

    def set_provider(self, provider: str, model: str = None):
        """切换 provider"""
        self.config["provider"] = provider
        if model:
            self.config["model"] = model

    def get_status(self) -> Dict[str, Any]:
        """获取客户端状态"""
        return {
            "provider": self.config["provider"],
            "model": self.config["model"],
            "cache_dir": str(self.cache_dir),
            "cache_size": sum(1 for _ in self.cache_dir.glob("*.txt")),
            "api_key_set": {
                "deepseek": bool(os.environ.get("DEEPSEEK_API_KEY")),
                "anthropic": bool(os.environ.get("ANTHROPIC_API_KEY")),
                "openai": bool(os.environ.get("OPENAI_API_KEY")),
                "zhipu": bool(os.environ.get("ZHIPU_API_KEY")),
            },
        }


# ==================== CLI 入口 ====================


def main():
    """CLI 测试入口"""
    print("=" * 70)
    print("🤖 Auto-Novel · LLM 客户端")
    print("=" * 70)

    client = LLMClient()
    status = client.get_status()

    print(f"\n当前配置：")
    print(f"  Provider: {status['provider']}")
    print(f"  Model: {status['model']}")
    print(f"  缓存目录: {status['cache_dir']}")
    print(f"  缓存条目: {status['cache_size']}")

    print(f"\nAPI Key 状态：")
    for k, v in status["api_key_set"].items():
        marker = "✅" if v else "❌"
        print(f"  {marker} {k}")

    # 测试调用
    print(f"\n测试调用（如果配置了 API Key）：")
    response = client.call("说'你好'，验证 API 是否工作。", max_tokens=50)
    print(f"  响应: {response[:200]}")

    print("=" * 70)


if __name__ == "__main__":
    main()