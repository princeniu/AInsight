# AI热点新闻自动化采集与文章生成

这个项目可以自动从多个来源获取AI领域的热点新闻，筛选出高质量的内容，然后使用GPT-4o生成可读性强的文章，最后将文章存储为Markdown格式和保存到SQLite数据库中。

## 目录

- [功能特点](#功能特点)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [使用方法](#使用方法)
  - [创建虚拟环境](#创建虚拟环境)
  - [安装依赖](#安装依赖)
  - [配置API密钥](#配置api密钥)
  - [配置Telegram通知](#配置telegram通知)
  - [运行程序](#运行程序)
  - [选择模型](#选择模型)
  - [可视化进度](#可视化进度)
- [Docker部署](#docker部署)
  - [使用Docker运行](#使用docker运行)
  - [环境变量配置](#环境变量配置)
  - [数据持久化](#数据持久化)
  - [定时任务配置](#定时任务配置)
  - [常见问题排除](#常见问题排除)
- [模块说明](#模块说明)
- [示例输出](#示例输出)
- [故障排除](#故障排除)
- [未来计划](#未来计划)
- [性能说明](#性能说明)
- [依赖库](#依赖库)
- [许可证](#许可证)

## 功能特点

1. **多源新闻获取**：从多个AI资讯来源（RSS、网站爬虫、API）获取最新新闻
2. **智能筛选**：通过关键词过滤、去重和热度排序筛选高质量新闻
3. **AI文章生成**：调用OpenAI模型自动生成结构清晰、可读性强的文章
4. **多风格文章生成**：支持多种文章风格，避免连续文章风格重复
5. **多格式存储**：将生成的文章保存为Markdown文件和纯文本文件，并存入SQLite数据库
6. **定时执行**：支持每天定时自动运行，可配置是否在首次启动时立即执行
7. **模型选择**：支持选择不同的OpenAI模型来生成文章
8. **可视化进度**：提供彩色输出和进度条，实时显示程序执行状态
9. **数据库查重**：自动检查新闻是否已存在于数据库中，避免重复生成文章
10. **智能文本清理**：针对性去除Markdown格式符号，生成干净的纯文本版本
11. **Telegram通知**：通过Telegram机器人实时通知文章生成状态和结果
12. **Docker支持**：提供完整的Docker部署方案，支持不同的启动模式

## 项目结构

```
ai_news_generator/
├── src/                  # 源代码目录
│   ├── core/             # 核心功能模块
│   │   ├── news_fetcher.py     # 新闻获取模块
│   │   ├── news_filter.py      # 新闻筛选模块
│   │   └── article_generator.py # 文章生成模块
│   ├── storage/          # 存储相关模块
│   │   └── article_storage.py  # 文章存储模块
│   ├── utils/            # 工具函数和辅助模块
│   │   └── analyze_webpage.py  # 网页分析工具
│   ├── scheduler/        # 定时任务相关模块
│   │   └── scheduler.py        # 定时任务模块
│   └── main.py           # 主程序入口
├── config/               # 配置文件目录
│   ├── config.py         # 配置文件（需要自行创建）
│   └── config.example.py # 配置文件示例
├── data/                 # 数据目录
│   ├── articles/         # 生成的文章存储目录
│   └── database/         # SQLite数据库目录
├── logs/                 # 日志文件目录
│   ├── ai_news_generator.log # 主程序日志
│   └── scheduler.log     # 定时任务日志
├── docker/               # Docker部署相关文件
│   ├── Dockerfile        # Docker镜像构建文件
│   ├── docker-compose.yml # Docker Compose配置文件
│   ├── .dockerignore     # Docker构建忽略文件
│   ├── .env.example      # 环境变量示例文件
│   ├── README.md         # Docker部署说明
│   └── scripts/          # Docker相关脚本
│       ├── start.sh          # 启动容器（立即执行任务）
│       ├── start-scheduled.sh # 启动容器（仅按计划时间执行）
│       ├── stop.sh           # 停止容器
│       ├── logs.sh           # 查看日志
│       ├── rebuild.sh        # 重建镜像
│       └── test.sh           # 测试容器
├── tests/                # 测试代码目录
│   └── test_news_sources.py # 新闻源测试
├── setup.py              # 安装脚本
└── requirements.txt      # 项目依赖
```

## 快速开始

如果你想快速开始使用本项目，可以按照以下步骤操作：

```bash
# 克隆项目
git clone https://github.com/princeniu/AInsight.git
cd AInsight

# 创建并激活虚拟环境
python -m venv aInsight
source aInsight/bin/activate  # Linux/macOS
# 或 aInsight\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 创建配置文件
cp config/config.example.py config/config.py
# 编辑config/config.py，设置你的OpenAI API密钥

# 运行程序（带可视化进度）
python src/main.py --verbose
```

## 使用方法

### 创建虚拟环境

推荐使用虚拟环境来运行此项目，以避免依赖冲突：

```bash
# 创建虚拟环境
python -m venv aInsight

# 在Windows上激活虚拟环境
aInsight\Scripts\activate

# 在macOS/Linux上激活虚拟环境
source aInsight/bin/activate

# 退出虚拟环境
# 退出虚拟环境

# 在Windows上退出虚拟环境
# aInsight\Scripts\deactivate

# 在macOS/Linux上退出虚拟环境
# deactivate
```

### 安装依赖

在激活的虚拟环境中安装所需依赖：

```bash
pip install -r requirements.txt
```

### 配置API密钥

本项目使用配置文件来存储API密钥和其他设置，这样可以避免将敏感信息提交到版本控制系统：

1. 复制配置文件示例：

```bash
cp config/config.example.py config/config.py
```

2. 编辑config/config.py文件，设置你的OpenAI API密钥：

```python
# OpenAI API配置
OPENAI_API_KEY = "your-openai-api-key-here"

# 模型配置
MODEL_CONFIG = {
    "default_model": "gpt-4o",  # 默认使用的模型
    "available_models": [
        "gpt-4o",        # 最强大的多模态模型
        "gpt-4-turbo",   # 强大的文本模型
        "gpt-3.5-turbo"  # 经济实惠的模型
    ]
}

# 定时任务配置
SCHEDULE_TIME = "08:00"  # 每天运行的时间

# 文章生成配置
MAX_ARTICLES_PER_RUN = 5  # 每次运行最多生成的文章数量
```

注意：config.py文件已添加到.gitignore中，不会被提交到Git仓库。

### 配置Telegram通知

本项目支持通过Telegram机器人发送文章生成完成的通知，让您实时了解程序的运行状态。

#### 设置步骤

1. 在Telegram中创建机器人
   - 与BotFather (@BotFather) 聊天
   - 发送 `/newbot` 命令
   - 按照提示设置机器人名称和用户名
   - 获取API令牌 (token)

2. 获取聊天ID
   - 与您创建的机器人开始聊天
   - 发送任意消息
   - 访问 `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - 从响应中找到 `chat_id` 值

3. 配置Telegram通知
   - 创建 `config/telegram_config.json` 文件
   - 填入您的机器人令牌和聊天ID
   ```json
   {
       "token": "YOUR_BOT_TOKEN",
       "chat_id": "YOUR_CHAT_ID",
       "include_preview": true,
       "send_full_article": false
   }
   ```

#### 通知内容

程序将发送两种类型的通知：

1. **文章生成通知** - 每生成一篇文章就发送一条通知，包含：
   - 文章标题
   - 新闻来源
   - 文章字数
   - 使用的模型
   - 保存的文件名
   - 文章内容预览（可配置）

2. **批量处理通知** - 程序执行完成后发送一条汇总通知，包含：
   - 获取的新闻总数
   - 过滤后的新闻数量
   - 生成的文章数量
   - 使用的模型列表
   - 程序执行时间

#### 配置选项

在 `telegram_config.json` 文件中，您可以配置以下选项：

- `include_preview`: 设置为 `true` 可在通知中包含文章内容预览（默认300字符）
- `send_full_article`: 设置为 `true` 可发送完整文章内容（分段发送）

注意：为了保护您的隐私和安全，请将 `telegram_config.json` 添加到 `.gitignore` 文件中，避免将敏感信息提交到版本控制系统。

### 运行程序

手动运行：

```bash
python src/main.py
```

定时运行（按照config.py中设置的时间自动执行）：

```bash
python src/scheduler/scheduler.py
```

命令行参数：

```bash
# 显示帮助信息
python src/main.py --help

# 使用特定模型运行
python src/main.py --model gpt-4-turbo

# 限制生成的文章数量
python src/main.py --max-articles 3

# 显示详细进度
python src/main.py --verbose

# 指定使用特定风格生成文章
python src/main.py --style 2  # 使用风格2（知乎专业分析风格）

# 自定义风格历史记录长度
python src/main.py --history-size 2  # 记录最近2种风格，避免连续使用

# 组合使用多个参数
python src/main.py --model gpt-4o --max-articles 5 --verbose --style 3 --history-size 2
```

可用的文章风格：
1. 今日头条爆款风格：情绪化、互动性强，使用爆款标题和表情符号
2. 知乎专业分析风格：专业、客观、理性，深度分析和多角度思考
3. 微信公众号科普风格：友好、通俗易懂，适合科普和知识传播
4. 商业分析报告风格：专业、分析性强，适合商业决策和市场分析

### 选择模型

本项目支持选择不同的OpenAI模型来生成文章。你可以通过以下方式选择模型：

1. **在配置文件中设置默认模型**：

```python
MODEL_CONFIG = {
    "default_model": "gpt-4o",  # 修改为你想要的默认模型
    "available_models": [
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-3.5-turbo"
    ]
}
```

2. **通过命令行参数指定模型**：

```bash
# 使用特定模型运行
python src/main.py --model gpt-4-turbo

# 查看可用模型列表
python src/main.py --list-models

# 使用特定模型运行定时任务
python src/scheduler/scheduler.py --model gpt-3.5-turbo
```

3. **不同模型的特点**：

- **gpt-4o**：最强大的多模态模型，生成质量最高，但API调用成本较高
- **gpt-4-turbo**：强大的文本模型，生成质量高，API调用成本中等
- **gpt-3.5-turbo**：经济实惠的模型，生成质量良好，API调用成本低

选择模型时，可以根据你的需求和预算进行平衡。生成的文章会自动记录使用的模型信息。

### 可视化进度

本项目支持可视化进度显示，让你能够实时了解程序的执行状态。使用以下命令启用可视化进度：

```bash
# 运行主程序并显示详细进度
python src/main.py --verbose

# 运行定时任务并显示详细进度
python src/scheduler/scheduler.py --verbose

# 测试文章生成模块并显示详细进度
python src/core/article_generator.py --verbose
```

可视化进度功能包括：

1. **彩色状态输出**：不同类型的信息使用不同颜色显示，例如：
   - 绿色：成功信息
   - 黄色：警告和处理中的状态
   - 红色：错误信息
   - 蓝色：一般信息

2. **进度条**：显示各个步骤的完成百分比，包括：
   - 新闻获取进度
   - 新闻筛选进度
   - 文章生成总进度
   - 单篇文章生成进度
   - 文章保存进度

3. **实时状态更新**：
   - 显示当前正在处理的任务
   - 显示API请求状态
   - 显示操作耗时
   - 显示文章预览

4. **定时任务状态**：
   - 显示下一次执行时间和倒计时
   - 实时显示主程序的输出
   - 显示任务执行结果

这些可视化功能使你能够更好地了解程序的运行状态，特别是在生成文章这样耗时的操作中，你可以实时看到进度而不是等待黑盒操作完成。

## Docker部署

本项目提供了完整的Docker支持，使用Docker可以更简单地部署和运行定时任务，避免环境配置问题。所有Docker相关文件都集中在`docker/`目录下，便于管理和维护。

### 使用Docker运行

1. **确保已安装Docker和Docker Compose**

   如果尚未安装，请参考[Docker官方文档](https://docs.docker.com/get-docker/)和[Docker Compose官方文档](https://docs.docker.com/compose/install/)。

2. **配置文件准备**

   确保已经创建并配置了`config/config.py`文件：
   
   ```bash
   cp config/config.example.py config/config.py
   # 然后编辑config/config.py，填入你的OpenAI API密钥和其他配置
   ```

3. **使用启动脚本运行**

   我们提供了简便的启动脚本：
   
   ```bash
   # 给脚本添加执行权限
   chmod +x docker/scripts/*.sh
   
   # 立即执行任务并按计划时间执行
   ./docker/scripts/start.sh
   
   # 仅按计划时间执行（不立即执行）
   ./docker/scripts/start-scheduled.sh
   
   # 查看日志
   ./docker/scripts/logs.sh
   
   # 停止服务
   ./docker/scripts/stop.sh
   
   # 重建Docker镜像
   ./docker/scripts/rebuild.sh
   ```

### 环境变量配置

你可以通过复制并修改`docker/.env.example`文件来配置Docker环境变量：

```bash
cp docker/.env.example docker/.env
```

然后编辑`docker/.env`文件：

```
# 时区设置
TIMEZONE=Asia/Shanghai

# 使用的模型
MODEL=gpt-4o

# 是否在启动时立即执行任务
IMMEDIATE_RUN=false
```

这些环境变量会覆盖`docker-compose.yml`中的默认值。

### 数据持久化

Docker配置已经设置了数据持久化，所有数据都会保存在本地的以下目录中：

- `./data`：存储生成的文章和数据库
- `./logs`：存储日志文件
- `./config`：存储配置文件

这意味着即使容器被删除，你的数据也不会丢失。

### 定时任务配置

本项目支持两种定时任务启动模式：

1. **立即执行模式**：容器启动后立即执行一次任务，然后按计划时间执行
   ```bash
   ./docker/scripts/start.sh
   ```

2. **仅计划执行模式**：容器启动后不立即执行任务，只在计划时间执行
   ```bash
   ./docker/scripts/start-scheduled.sh
   ```

计划执行时间在`config/config.py`中的`SCHEDULE_TIME`变量中设置，格式为`HH:MM`，例如：
```python
SCHEDULE_TIME = "08:00"  # 每天早上8点执行
```

时区设置在Docker环境变量`TIMEZONE`中配置，例如：
```
TIMEZONE=Asia/Shanghai  # 使用中国标准时间
```

### 常见问题排除

#### 容器启动失败

1. 检查配置文件是否存在：
   ```bash
   ls -la ../config/config.py
   ```

2. 检查环境变量是否正确设置：
   ```bash
   cat docker/.env
   ```

3. 查看容器日志：
   ```bash
   ./docker/scripts/logs.sh
   ```

#### 文件权限问题

如果遇到文件权限问题，可以尝试：
```bash
chmod -R 755 data logs config
```

#### 定时任务不按预期执行

1. 检查环境变量`IMMEDIATE_RUN`的设置：
   ```bash
   # 查看docker-compose配置
   cd docker && docker-compose config
   
   # 查看容器中的环境变量
   docker exec ai-news-scheduler env | grep IMMEDIATE
   ```

2. 如果使用`start-scheduled.sh`脚本但任务仍然立即执行，请尝试重新构建镜像：
   ```bash
   ./docker/scripts/rebuild.sh
   ./docker/scripts/start-scheduled.sh
   ```

3. 检查容器日志中的执行计划：
   ```bash
   ./docker/scripts/logs.sh
   ```
   应该能看到类似以下的输出：
   ```
   首次立即执行: 关闭
   已禁用首次启动立即执行，将仅在计划时间运行
   ```

更多Docker部署相关的详细说明，请参考`docker/README.md`文件。

## 模块说明

### 1. news_fetcher.py

从多个来源获取AI相关新闻，包括：
- OpenAI官方博客
- DeepMind
- TechCrunch AI频道
- Reddit AI话题
- Hacker News AI相关帖子

**输出格式**：JSON格式的新闻列表

### 2. news_filter.py

筛选高质量新闻，功能包括：
- 去重：过滤相似新闻
- 关键词匹配：确保内容与AI相关
- 时间排序：优先处理最新新闻
- 热度排序：优先处理热门新闻
- 数据库查重：检查新闻是否已存在于数据库中，避免重复处理

**输入/输出**：JSON格式的新闻列表

### 3. article_generator.py

使用OpenAI模型生成高质量文章，特点包括：

#### 提示词系统
- **多风格文章生成**：支持多种文章风格，包括：
  - 今日头条爆款风格：情绪化、互动性强，使用爆款标题和表情符号
  - 知乎专业分析风格：专业、客观、理性，深度分析和多角度思考
  - 微信公众号科普风格：友好、通俗易懂，适合科普和知识传播
  - 商业分析报告风格：专业、分析性强，适合商业决策和市场分析
- **风格记忆功能**：
  - 自动记录最近使用的风格，避免连续文章使用相同风格
  - 可配置的历史记录长度，默认记录最近3种风格
  - 支持通过命令行参数`--style`指定特定风格
  - 支持通过命令行参数`--history-size`自定义历史记录长度
- **标题优化**：使用"震惊！"、"重磅！"等爆款标题公式
- **结构优化**：
  - 开头设置悬念，第一段直击痛点
  - 短段落设计，每段不超过3句话
  - 情绪化表达，使用"爆"、"绝了"等词增加传播性
  - 大量使用表情符号增加亲和力
  
#### 内容策略
- **可读性**：将复杂AI概念转化为通俗易懂的解释
- **互动性**：设置3-5个引导读者思考或评论的问题
- **传播性**：
  - 制造信息差和独家感
  - 添加虚构的"知情人士"观点增加可信度
  - 强调新闻对普通人的影响
  - 结合热点话题和流行梗
  
#### 技术特点
- 支持多个OpenAI模型（gpt-4o、gpt-4-turbo、gpt-3.5-turbo）
- 智能重试机制和错误处理
- 实时显示生成进度和预览
- 自动优化标题吸引力

**输出格式**：结构化的文章内容，包含标题、正文和元数据

### 4. article_storage.py

存储生成的文章，支持：
- Markdown格式（保存到articles目录）
- 纯文本格式（去除Markdown符号，保存到articles目录）
- SQLite数据库（ID、标题、内容、发布日期、使用的模型）
- 文件名安全处理：自动将标题转换为安全的文件名
- 数据库查重：提供API检查文章是否已存在于数据库中
- 智能文本清理：只去除特定的Markdown符号（**、---、##、###），保留其他格式

**输入**：文章标题、内容、原始链接、发布日期、使用的模型

### 5. scheduler.py

定时运行任务，支持：
- 使用schedule库设置定时任务
- 适配cron定时任务
- 支持指定使用的模型
- 彩色输出和实时状态显示
- 显示下一次执行时间和倒计时

### 6. config.py

配置文件，包含：
- OpenAI API密钥
- 模型配置（默认模型和可用模型列表）
- 定时任务配置
- 文章生成配置

### 7. telegram_notifier.py

Telegram通知模块，功能包括：
- 发送文章生成通知
- 发送批量处理完成通知
- 发送文章内容预览或完整内容
- 支持HTML格式的消息
- 配置化的通知内容控制

## 示例输出

以下是使用本项目生成的文章示例：

```markdown
# GPT-4o震撼发布：AI多模态能力迎来质的飞跃

📅 2023-05-20  
🔗 [阅读原文](https://example.com/news/1)  
模型: gpt-4o

## 引言

你是否曾想过，人工智能能否真正理解我们的语言、图像和声音？🤔 OpenAI最新发布的GPT-4o模型或许给出了肯定的答案。这款全新模型不仅在性能上全面超越前代产品，更在多模态理解能力上实现了质的飞跃。

## GPT-4o：超越想象的多模态能力

GPT-4o最大的突破在于其强大的多模态能力。它可以同时处理文本、图像、音频和视频，并在这些不同形式的信息之间建立联系。这意味着你可以向它展示一张照片，它不仅能识别照片中的内容，还能理解照片背后的故事和情感。

实时语音交互是GPT-4o的另一大亮点。与以往的模型相比，GPT-4o的响应速度提升了10倍，使得与AI的对话体验更加自然流畅，就像与真人交谈一样。

## 技术背后的突破

GPT-4o采用了全新的神经网络架构，通过创新的训练方法，使模型能够更好地理解不同模态之间的关联。这种架构不仅提高了模型的理解能力，还大幅降低了推理延迟。

## 行业专家怎么看？

著名AI研究员李明教授表示："GPT-4o代表了大语言模型的一个重要里程碑。它的多模态能力已经接近人类水平，这将彻底改变人机交互的未来。"

微软AI部门负责人张伟博士则指出："GPT-4o的商业价值不可估量。它将使企业能够开发更自然、更直观的AI应用，为用户提供前所未有的体验。"

## 未来展望

GPT-4o的发布无疑将加速AI在各行各业的应用。从医疗诊断到教育辅导，从客户服务到创意设计，我们将看到AI承担越来越重要的角色。

然而，这也带来了新的挑战。随着AI变得越来越强大，如何确保它的安全、公平和负责任使用将变得更加重要。

## 结论

GPT-4o的发布标志着AI发展的新纪元。它不仅展示了技术的进步，也预示着人类与AI关系的新阶段。在这个阶段，AI将成为我们更加可靠、透明和强大的合作伙伴。

你认为GPT-4o会如何改变你的工作和生活？AI的这些进步是否让你感到兴奋或担忧？欢迎在评论区分享你的想法！
```

生成的文章将同时保存为：
1. Markdown文件（`articles/YYYYMMDD_HHMMSS_文章标题.md`）- 保留完整格式
2. 纯文本文件（`articles/YYYYMMDD_HHMMSS_文章标题.txt`）- 去除Markdown符号
3. 数据库记录 - 存储在SQLite数据库中

## 故障排除

### OpenAI API密钥问题
- **问题**: `未设置API密钥，请在config.py中设置OPENAI_API_KEY`
- **解决方案**: 确保已正确创建并配置config.py文件：
  ```python
  # 在config.py中设置
  OPENAI_API_KEY = "your-openai-api-key-here"
  ```

### 依赖安装问题
- **问题**: 安装依赖时出现错误
- **解决方案**: 尝试更新pip后再安装：`pip install --upgrade pip`

### 网络连接问题
- **问题**: 无法获取新闻或API调用失败
- **解决方案**: 检查网络连接，确保能够访问相关网站和OpenAI API

### RSS源失效问题
- **问题**: 某些RSS源无法获取新闻
- **解决方案**: 程序设计为容错的，即使某些源失效也不会影响整体运行。可以在`news_fetcher.py`中更新或添加新的RSS源

### 模型选择问题
- **问题**: 指定的模型不可用
- **解决方案**: 确保在config.py的MODEL_CONFIG中正确配置了可用模型，或者使用`--list-models`参数查看可用模型列表

### 可视化进度问题
- **问题**: 进度条显示异常或颜色不正确
- **解决方案**: 确保终端支持ANSI颜色，或者尝试更新colorama库：`pip install --upgrade colorama`

### 数据库管理问题
- **问题**: 数据库中出现重复文章
- **解决方案**: 系统已内置数据库查重功能，如需清空数据库可以：
  ```bash
  # 备份并删除数据库文件
  cp database/articles.db database/articles.db.backup && rm database/articles.db
  # 下次运行程序时会自动创建新的空数据库
  ```

### Telegram通知问题
- **问题**: 无法发送Telegram通知
- **解决方案**: 
  - 确保已正确配置 `config/telegram_config.json` 文件
  - 检查机器人令牌和聊天ID是否正确
  - 确保您的网络可以访问Telegram API
  - 尝试运行测试脚本: `python tests/test_telegram.py`

## 未来计划

- [ ] 添加Web界面，方便查看和管理文章
- [ ] 支持更多新闻来源
- [ ] 实现自动发布到社交媒体平台
- [ ] 添加文章质量评估系统
- [ ] 优化文章生成速度
- [ ] 支持多语言新闻采集和文章生成
- [ ] 添加更多OpenAI模型的支持
- [x] 实现多风格文章生成和风格记忆功能，避免连续文章风格重复
- [x] 完善Docker部署方案，支持不同的启动模式
- [ ] 增强可视化界面，添加更多交互功能
- [ ] 增强数据库功能，支持更复杂的查询和统计
- [ ] 优化文本清理算法，支持自定义清理规则
- [ ] 扩展Telegram通知功能，支持交互式命令和查询

## 性能说明

- **硬件需求**: 本项目不需要特殊硬件，普通PC即可运行
- **运行时间**: 完整流程（获取新闻、筛选、生成5篇文章）大约需要3-5分钟
- **API用量**: 每生成一篇文章约消耗2000-3000 tokens，请注意OpenAI API的使用限制和费用
  - gpt-4o: 约$0.05-0.10/文章
  - gpt-4-turbo: 约$0.03-0.06/文章
  - gpt-3.5-turbo: 约$0.01-0.02/文章
- **存储需求**: 数据库和文章存储通常不会超过几MB，除非长期运行收集大量文章

## 依赖库

- feedparser：解析RSS源
- requests：发送HTTP请求
- beautifulsoup4：解析HTML页面
- openai：调用OpenAI API
- schedule：定时任务管理
- python-dateutil：日期处理
- nltk & scikit-learn：文本相似度计算
- sqlite3：数据库操作（Python标准库）
- tqdm：显示进度条
- colorama：终端彩色输出

## 许可证

本项目采用 MIT 许可证 - 详情请查看 [LICENSE](LICENSE) 文件 