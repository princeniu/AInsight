# Docker部署说明

本目录包含AI热点新闻自动化采集与文章生成项目的Docker部署相关文件。

## 目录结构

```
docker/
├── Dockerfile            # Docker镜像构建文件
├── docker-compose.yml    # Docker Compose配置文件
├── .dockerignore         # Docker构建忽略文件
├── .env.example          # 环境变量示例文件
└── scripts/              # Docker相关脚本
    ├── start.sh          # 启动Docker容器（立即执行任务）
    ├── start-scheduled.sh # 启动Docker容器（仅按计划时间执行）
    ├── start-immediate.sh # 启动Docker容器（立即执行一次，并按计划时间执行）
    ├── stop.sh           # 停止Docker容器
    ├── logs.sh           # 查看Docker日志
    ├── rebuild.sh        # 重建Docker镜像
    └── test.sh           # 测试Docker容器
```

## 快速开始

1. 复制并编辑环境变量文件：

```bash
cp .env.example .env
# 编辑.env文件，设置必要的环境变量
```

2. 确保配置文件已正确设置：

```bash
# 确保项目根目录下的config/config.py文件已正确配置
```

3. 启动容器：

```bash
# 立即执行任务并按计划时间执行
./scripts/start.sh

# 或者仅按计划时间执行（不立即执行）
./scripts/start-scheduled.sh
```

## 环境变量说明

在`.env`文件中可以设置以下环境变量：

- `TIMEZONE`: 容器时区，默认为`America/Chicago`
- `MODEL`: 使用的OpenAI模型，默认为`gpt-4o`
- `IMMEDIATE_RUN`: 是否在启动时立即执行任务，可选值为`true`或`false`
  - 使用`start.sh`脚本启动时，此值设为`true`
  - 使用`start-scheduled.sh`脚本启动时，此值设为`false`

## 数据持久化

Docker配置已设置数据持久化，所有数据会保存在项目根目录的以下目录中：

- `../data`: 存储生成的文章和数据库
- `../logs`: 存储日志文件
- `../config`: 存储配置文件

## 常见问题排除

### 容器启动失败

1. 检查配置文件是否存在：

```bash
ls -la ../config/config.py
```

2. 检查环境变量是否正确设置：

```bash
cat .env
```

3. 查看容器日志：

```bash
./scripts/logs.sh
```

### 文件权限问题

如果遇到文件权限问题，可以尝试：

```bash
chmod -R 755 ../data ../logs ../config
```

### 定时任务不按预期执行

1. 检查环境变量`IMMEDIATE_RUN`的设置：

```bash
# 查看docker-compose配置
docker-compose config

# 查看容器中的环境变量
docker exec ai-news-scheduler env | grep IMMEDIATE
```

2. 如果使用`start-scheduled.sh`脚本但任务仍然立即执行，请尝试重新构建镜像：

```bash
./scripts/rebuild.sh
./scripts/start-scheduled.sh
```

3. 检查容器日志中的执行计划：

```bash
./scripts/logs.sh
```

应该能看到类似以下的输出：

```
首次立即执行: 关闭
已禁用首次启动立即执行，将仅在计划时间运行
```

## 注意事项

1. 修改Dockerfile后需要重新构建镜像：

```bash
./scripts/rebuild.sh
```

2. 时区设置会影响定时任务的执行时间，请确保设置正确的时区 