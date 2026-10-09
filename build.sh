#!/usr/bin/env bash
# 构建 LangChain4j 中文文档站点（CI 与本地共用，保证产物一致）
set -euo pipefail
cd "$(dirname "$0")"

PY="${PYTHON:-}"
if [ -z "$PY" ]; then
  if [ -x ".venv/bin/python" ]; then
    PY=".venv/bin/python"
  elif command -v python3 >/dev/null 2>&1; then
    PY="python3"
  else
    echo "未找到 python3" >&2
    exit 1
  fi
fi
# 1. 生成 LLM 上下文文件（llms.txt / llms-full.txt / robots.txt）
"$PY" scripts/generate-llm-context-zh.py

# 2. 构建静态站点
"$PY" -m mkdocs build -f mkdocs.zh.yml --clean

# 3. 根级文件放入站点根目录
cp -f llms.txt llms-full.txt robots.txt site-zh/

echo "构建完成: $(find site-zh -name '*.html' | wc -l | tr -d ' ') 个页面 -> site-zh/"
