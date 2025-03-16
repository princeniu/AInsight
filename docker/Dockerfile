FROM python:3.12-slim

WORKDIR /app

# 设置时区
ENV TZ=America/Chicago
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pytz

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p data/articles data/database logs

# 设置环境变量
ENV PYTHONPATH=/app
ENV IMMEDIATE_RUN=true

# 创建启动脚本
RUN echo '#!/bin/bash\n\
if [ "$IMMEDIATE_RUN" = "true" ]; then\n\
  python src/scheduler/scheduler.py --verbose "$@"\n\
else\n\
  python src/scheduler/scheduler.py --verbose --no-immediate-run "$@"\n\
fi' > /app/docker-entrypoint.sh && chmod +x /app/docker-entrypoint.sh

# 设置入口点
ENTRYPOINT ["/app/docker-entrypoint.sh"] 