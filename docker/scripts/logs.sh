#!/bin/bash

# 切换到项目根目录
cd "$(dirname "$0")/../.." || exit

# 查看Docker容器日志
echo "正在查看AI新闻自动化定时任务日志..."
cd docker && docker-compose logs -f 