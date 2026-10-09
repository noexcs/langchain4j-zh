#!/usr/bin/env bash
# 本地预览 LangChain4j 中文文档（默认 http://127.0.0.1:8000）
set -euo pipefail
cd "$(dirname "$0")"

PY="${PYTHON:-.venv/bin/python}"
if [ ! -x "$PY" ]; then
  echo "未找到 .venv，先执行: uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt" >&2
  exit 1
fi

exec "$PY" -m mkdocs serve -f mkdocs.zh.yml "$@"
