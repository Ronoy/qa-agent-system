#!/bin/bash
# 后端启动脚本
cd "$(dirname "$0")/backend"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "已创建 .env 文件，请填写 DEEPSEEK_API_KEY"
fi

if [ ! -d venv ]; then
  python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt -q

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
