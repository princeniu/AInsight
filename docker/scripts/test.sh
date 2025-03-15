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

# 构建测试镜像
echo "正在构建测试镜像..."
cd docker && docker-compose build

# 运行测试容器（非后台模式，便于查看输出）
echo "正在运行测试容器..."
docker-compose run --rm ai-news-scheduler python src/main.py --verbose --max-articles 1

echo "测试完成" 