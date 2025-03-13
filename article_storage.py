#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文章存储模块

将生成的文章存储为Markdown文件和保存到SQLite数据库。
"""

import os
import logging
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import re

# 配置日志
logger = logging.getLogger(__name__)

# 数据库文件路径
DB_PATH = os.path.join("database", "articles.db")

# 确保目录存在
os.makedirs("articles", exist_ok=True)
os.makedirs("database", exist_ok=True)


def sanitize_filename(title: str) -> str:
    """
    将标题转换为安全的文件名
    
    Args:
        title: 文章标题
        
    Returns:
        安全的文件名
    """
    # 移除非法字符
    filename = re.sub(r'[\\/*?:"<>|]', "", title)
    # 将空格替换为下划线
    filename = re.sub(r'\s+', "_", filename)
    # 限制长度
    if len(filename) > 100:
        filename = filename[:100]
    return filename


def get_db_connection() -> sqlite3.Connection:
    """
    获取数据库连接
    
    Returns:
        SQLite数据库连接
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # 创建文章表（如果不存在）
    conn.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        source_url TEXT NOT NULL,
        published_date TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    ''')
    
    return conn


def save_article_to_markdown(article_data: Dict[str, Any]) -> str:
    """
    将文章保存为Markdown文件
    
    Args:
        article_data: 文章数据，包含title, content, source_url, published_date
        
    Returns:
        保存的文件路径
    """
    title = article_data.get("title", "未命名文章")
    content = article_data.get("content", "")
    source_url = article_data.get("source_url", "")
    published_date = article_data.get("published_date", datetime.now().strftime("%Y-%m-%d"))
    
    # 生成安全的文件名
    date_prefix = datetime.now().strftime("%Y%m%d")
    filename = f"{date_prefix}_{sanitize_filename(title)}.md"
    file_path = os.path.join("articles", filename)
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            # 写入Markdown格式的文章
            f.write(f"# {title}\n\n")
            f.write(f"📅 {published_date}  \n")
            f.write(f"🔗 [阅读原文]({source_url})\n\n")
            
            # 写入文章内容
            f.write(content)
            
            # 添加讨论部分（如果内容中没有）
            if "## 讨论" not in content and "# 讨论" not in content:
                f.write("\n\n## 讨论\n\n")
                f.write("你怎么看这个AI新闻？欢迎留言讨论！\n")
        
        logger.info(f"文章已保存为Markdown: {file_path}")
        return file_path
    
    except Exception as e:
        logger.error(f"保存Markdown文件时出错: {str(e)}")
        return ""


def save_article_to_db(article_data: Dict[str, Any]) -> int:
    """
    将文章保存到SQLite数据库
    
    Args:
        article_data: 文章数据，包含title, content, source_url, published_date
        
    Returns:
        文章ID
    """
    title = article_data.get("title", "未命名文章")
    content = article_data.get("content", "")
    source_url = article_data.get("source_url", "")
    published_date = article_data.get("published_date", datetime.now().strftime("%Y-%m-%d"))
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查是否已存在相同标题的文章
        cursor.execute("SELECT id FROM articles WHERE title = ?", (title,))
        existing = cursor.fetchone()
        
        if existing:
            logger.warning(f"数据库中已存在标题为 '{title}' 的文章")
            article_id = existing["id"]
            
            # 更新现有文章
            cursor.execute('''
            UPDATE articles
            SET content = ?, source_url = ?, published_date = ?, created_at = ?
            WHERE id = ?
            ''', (content, source_url, published_date, created_at, article_id))
        else:
            # 插入新文章
            cursor.execute('''
            INSERT INTO articles (title, content, source_url, published_date, created_at)
            VALUES (?, ?, ?, ?, ?)
            ''', (title, content, source_url, published_date, created_at))
            article_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        logger.info(f"文章已保存到数据库，ID: {article_id}")
        return article_id
    
    except Exception as e:
        logger.error(f"保存到数据库时出错: {str(e)}")
        return -1


def get_article_by_id(article_id: int) -> Optional[Dict[str, Any]]:
    """
    根据ID从数据库获取文章
    
    Args:
        article_id: 文章ID
        
    Returns:
        文章数据，如果不存在则返回None
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(row)
        else:
            return None
    
    except Exception as e:
        logger.error(f"从数据库获取文章时出错: {str(e)}")
        return None


def get_recent_articles(limit: int = 10) -> list:
    """
    获取最近的文章列表
    
    Args:
        limit: 返回的文章数量
        
    Returns:
        文章列表
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, title, published_date, created_at
        FROM articles
        ORDER BY created_at DESC
        LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    except Exception as e:
        logger.error(f"获取最近文章列表时出错: {str(e)}")
        return []


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 测试数据
    test_article = {
        "title": "GPT-5震撼发布！AI领域迎来重大突破",
        "content": """
# GPT-5震撼发布！AI领域迎来重大突破

## 引言

你是否曾想过，人工智能会在何时真正理解人类的思维方式？🤔 OpenAI最新发布的GPT-5模型或许正在向这一目标迈进一大步。这款全新模型不仅在性能上全面超越前代产品，更在多个关键能力上实现了质的飞跃。

## GPT-5：超越想象的AI能力

GPT-5采用了全新的神经网络架构，参数规模达到惊人的10万亿，是GPT-4的5倍。这使得它能够处理更复杂的推理任务，理解更细微的语言差异。

最令人印象深刻的是，GPT-5展示了前所未有的"思维链"能力，它不仅能给出答案，还能清晰地解释推理过程，就像人类专家一样逐步分析问题。这意味着AI不再是一个黑盒，用户可以理解它是如何得出结论的。

## 多模态理解：打破感知壁垒

GPT-5的另一大突破在于多模态能力的大幅提升。它可以同时理解文本、图像、音频和视频，并在这些不同形式的信息之间建立联系。想象一下，你可以向它展示一张照片，它不仅能识别照片中的内容，还能理解照片背后的故事和情感。

## 行业专家怎么看？

著名AI研究员李明教授表示："GPT-5代表了大语言模型的一个重要里程碑。它的推理能力已经接近人类专家水平，这将彻底改变知识工作的未来。"

微软AI部门负责人张伟博士则指出："GPT-5的商业价值不可估量。它将使企业能够自动化更多复杂的知识工作，同时提供前所未有的透明度和可解释性。"

## 未来展望

GPT-5的发布无疑将加速AI在各行各业的应用。从医疗诊断到法律咨询，从教育辅导到科学研究，我们将看到AI承担越来越重要的角色。

然而，这也带来了新的挑战。随着AI变得越来越强大，如何确保它的安全、公平和负责任使用将变得更加重要。

## 结论

GPT-5的发布标志着AI发展的新纪元。它不仅展示了技术的进步，也预示着人类与AI关系的新阶段。在这个阶段，AI将成为我们更加可靠、透明和强大的合作伙伴。

你认为GPT-5会如何改变你的工作和生活？AI的这些进步是否让你感到兴奋或担忧？欢迎在评论区分享你的想法！
        """,
        "source_url": "https://example.com/news/gpt5-release",
        "published_date": "2023-05-20"
    }
    
    # 测试保存为Markdown
    md_path = save_article_to_markdown(test_article)
    print(f"Markdown文件已保存: {md_path}")
    
    # 测试保存到数据库
    article_id = save_article_to_db(test_article)
    print(f"文章已保存到数据库，ID: {article_id}")
    
    # 测试获取最近文章
    recent_articles = get_recent_articles(5)
    print("\n最近的文章:")
    for article in recent_articles:
        print(f"ID: {article['id']}, 标题: {article['title']}, 发布日期: {article['published_date']}") 