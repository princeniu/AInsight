# AI热点新闻自动化采集与文章生成

这个项目可以自动从多个来源获取AI领域的热点新闻，筛选出高质量的内容，然后使用GPT-4o生成可读性强的文章，最后将文章存储为Markdown格式和保存到SQLite数据库中。

## 功能特点

1. **多源新闻获取**：从多个AI资讯来源（RSS、网站爬虫、API）获取最新新闻
2. **智能筛选**：通过关键词过滤、去重和热度排序筛选高质量新闻
3. **AI文章生成**：调用GPT-4o自动生成结构清晰、可读性强的文章
4. **多格式存储**：将生成的文章保存为Markdown文件和SQLite数据库
5. **定时执行**：支持每天定时自动运行

## 项目结构

```
ai_news_generator/
├── main.py                # 主程序入口
├── news_fetcher.py        # 新闻获取模块
├── news_filter.py         # 新闻筛选模块
├── article_generator.py   # 文章生成模块
├── article_storage.py     # 文章存储模块
├── scheduler.py           # 定时任务模块
├── articles/              # 生成的文章存储目录
├── database/              # SQLite数据库目录
└── requirements.txt       # 项目依赖
```

## 使用方法

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置API密钥

在使用前，请确保配置好OpenAI API密钥：

```bash
export OPENAI_API_KEY="your-api-key"
```

### 运行程序

手动运行：

```bash
python main.py
```

定时运行（每天8:00自动执行）：

```bash
python scheduler.py
```

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

**输入/输出**：JSON格式的新闻列表

### 3. article_generator.py

调用GPT-4o生成高质量文章，特点：
- 吸引人的标题
- 清晰的结构（引言、正文、专家观点、结论）
- 适当的长度（800-1200字）
- 良好的可读性（短段落、表情符号）

**输入**：JSON格式的新闻信息
**输出**：生成的文章文本

### 4. article_storage.py

存储生成的文章，支持：
- Markdown格式（保存到articles目录）
- SQLite数据库（ID、标题、内容、发布日期）

**输入**：文章标题、内容、原始链接、发布日期

### 5. scheduler.py

定时运行任务，支持：
- 使用schedule库设置定时任务
- 适配cron定时任务

## 依赖库

- feedparser：解析RSS源
- requests：发送HTTP请求
- beautifulsoup4：解析HTML页面
- openai：调用GPT-4o API
- schedule：定时任务管理
- sqlite3：数据库操作（Python标准库） 