#!/bin/bash
# 前端启动脚本
cd "$(dirname "$0")/frontend"

if [ ! -d node_modules ]; then
  npm install
fi

npm run dev
