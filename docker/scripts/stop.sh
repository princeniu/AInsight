#!/bin/bash

# 切换到项目根目录
cd "$(dirname "$0")/../.." || exit

# 停止Docker容器
echo "正在停止AI新闻自动化定时任务..."
cd docker && docker-compose down

# 显示容器状态
echo "容器状态:"
docker-compose ps 