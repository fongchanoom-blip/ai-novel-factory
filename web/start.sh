#!/usr/bin/env bash
# Auto-Novel Web 界面启动脚本

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SKILL_DIR="$( dirname "$SCRIPT_DIR" )"

echo "============================================================"
echo "📖 Auto-Novel Skill · Web 界面启动器"
echo "============================================================"
echo "📂 Skill 目录: $SKILL_DIR"
echo "🌐 启动地址: http://localhost:7860"
echo "============================================================"

# 检查 gradio
if ! python3 -c "import gradio" 2>/dev/null; then
  echo "❌ 未安装 gradio"
  echo "📦 正在安装..."
  pip install gradio --quiet
fi

# 启动 Web 服务
cd "$SCRIPT_DIR"
python3 app.py