#!/bin/bash

# 切换到项目根目录
cd "$(dirname "$0")/../.." || exit

# 停止并删除现有容器
echo "正在停止并删除现有容器..."
cd docker && docker-compose down

# 重新构建镜像
echo "正在重新构建Docker镜像..."
docker-compose build --no-cache

# 启动新容器
echo "正在启动新容器..."
docker-compose up -d

# 显示容器状态
echo "容器状态:"
docker-compose ps

# 显示日志
echo "查看日志: cd docker && docker-compose logs -f" 