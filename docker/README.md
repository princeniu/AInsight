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
    ├── start.sh          # 启动Docker容器
    ├── stop.sh           # 停止Docker容器
    ├── logs.sh           # 查看Docker日志
    ├── rebuild.sh        # 重建Docker镜像
    └── test.sh           # 测试Docker容器
```

## 快速开始

1. 复制环境变量示例文件：

```bash
cp .env.example .env
```

2. 编辑`.env`文件，根据需要修改环境变量：

```
# 时区设置
TIMEZONE=Asia/Shanghai

# 使用的模型
MODEL=gpt-4o
```

3. 确保项目根目录下的配置文件已正确设置：

```bash
cd ..
cp config/config.example.py config/config.py
# 编辑config/config.py，设置OpenAI API密钥和其他配置
```

4. 使用脚本启动Docker容器：

```bash
# 确保脚本有执行权限
chmod +x scripts/*.sh

# 启动服务
./scripts/start.sh

# 查看日志
./scripts/logs.sh

# 停止服务
./scripts/stop.sh
```

## 环境变量说明

- `TIMEZONE`: 容器的时区设置，默认为`America/Chicago`
- `MODEL`: 使用的OpenAI模型，默认为`gpt-4o`

## 数据持久化

Docker配置已设置数据持久化，所有数据会保存在项目根目录的以下目录中：

- `../data`: 存储生成的文章和数据库
- `../logs`: 存储日志文件
- `../config`: 存储配置文件

## 常见问题

1. **容器无法启动**

检查日志以获取详细错误信息：

```bash
./scripts/logs.sh
```

2. **文件权限问题**

如果遇到文件权限问题，可以尝试以下命令：

```bash
# 确保脚本有执行权限
chmod +x scripts/*.sh

# 确保数据目录有正确的权限
cd ..
chmod -R 755 data logs
```

3. **自定义Docker配置**

如果需要自定义Docker配置，可以编辑`Dockerfile`和`docker-compose.yml`文件。 