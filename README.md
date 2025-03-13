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
  - [运行程序](#运行程序)
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

# 设置API密钥
export OPENAI_API_KEY="your-api-key"
# 或 set OPENAI_API_KEY=your-api-key  # Windows

# 运行程序
python main.py
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
```

### 安装依赖

在激活的虚拟环境中安装所需依赖：

```bash
pip install -r requirements.txt
```

### 配置API密钥

在使用前，请确保配置好OpenAI API密钥：

```bash
export OPENAI_API_KEY="your-api-key"

# 在Windows上使用以下命令
# set OPENAI_API_KEY=your-api-key
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

## 示例输出

以下是使用本项目生成的文章示例：

```markdown
# GPT-4o震撼发布：AI多模态能力迎来质的飞跃

📅 2023-05-20  
🔗 [阅读原文](https://example.com/news/1)

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

生成的文章将保存在`articles`目录下，并同时存储在SQLite数据库中。

## 故障排除

### OpenAI API密钥问题
- **问题**: `未设置OPENAI_API_KEY环境变量，无法生成文章`
- **解决方案**: 确保已正确设置环境变量，可以尝试在Python代码中直接设置：
  ```python
  import os
  os.environ["OPENAI_API_KEY"] = "your-api-key"
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

## 未来计划

- [ ] 添加Web界面，方便查看和管理文章
- [ ] 支持更多新闻来源
- [ ] 实现自动发布到社交媒体平台
- [ ] 添加文章质量评估系统
- [ ] 优化文章生成速度
- [ ] 支持多语言新闻采集和文章生成

## 性能说明

- **硬件需求**: 本项目不需要特殊硬件，普通PC即可运行
- **运行时间**: 完整流程（获取新闻、筛选、生成5篇文章）大约需要3-5分钟
- **API用量**: 每生成一篇文章约消耗2000-3000 tokens，请注意OpenAI API的使用限制和费用
- **存储需求**: 数据库和文章存储通常不会超过几MB，除非长期运行收集大量文章

## 依赖库

- feedparser：解析RSS源
- requests：发送HTTP请求
- beautifulsoup4：解析HTML页面
- openai：调用GPT-4o API
- schedule：定时任务管理
- python-dateutil：日期处理
- nltk & scikit-learn：文本相似度计算
- sqlite3：数据库操作（Python标准库）

## 许可证

本项目采用 MIT 许可证 - 详情请查看 [LICENSE](LICENSE) 文件 