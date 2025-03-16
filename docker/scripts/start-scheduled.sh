#!/bin/bash

# 切换到项目根目录
cd "$(dirname "$0")/../.." || exit

# 确保配置文件存在
if [ ! -f "config/config.py" ]; then
  echo "错误: 配置文件不存在，请先复制config.example.py为config.py并填写配置"
  echo "cp config/config.example.py config/config.py"
  exit 1
fi

# 确保.env文件存在
if [ ! -f "docker/.env" ]; then
  echo "警告: Docker环境变量文件不存在，正在复制示例文件..."
  cp docker/.env.example docker/.env
  echo "请根据需要编辑docker/.env文件"
fi

# 设置环境变量，禁止首次启动立即执行
export IMMEDIATE_RUN=false

# 启动Docker容器
echo "正在启动AI新闻自动化定时任务（仅按计划时间执行，不立即执行）..."
cd docker && docker-compose up -d

# 显示容器状态
echo "容器状态:"
docker-compose ps

# 显示日志
echo "查看日志: cd docker && docker-compose logs -f" 