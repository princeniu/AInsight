#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文章存储模块

将生成的文章保存为Markdown文件和存储到SQLite数据库。
"""

import os
import sqlite3
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# 配置日志
logger = logging.getLogger(__name__)

# 数据库路径
DB_PATH = os.path.join("database", "articles.db")

def save_article_to_markdown(article_data: Dict[str, Any]) -> str:
    """
    将文章保存为Markdown文件
    
    Args:
        article_data: 文章数据，包含title, content, source_url, published_date, model_used(可选)
        
    Returns:
        保存的文件路径
    """
    # 确保articles目录存在
    os.makedirs("articles", exist_ok=True)
    
    # 格式化标题作为文件名（移除不允许的字符）
    safe_title = "".join(c for c in article_data["title"] if c.isalnum() or c in " -_").strip()
    safe_title = safe_title.replace(" ", "_")[:50]  # 限制长度
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{safe_title}.md"
    file_path = os.path.join("articles", filename)
    
    # 准备Markdown内容
    model_info = f"模型: {article_data.get('model_used', 'unknown')}" if 'model_used' in article_data else ""
    
    markdown_content = f"""# {article_data['title']}

📅 {article_data['published_date']}  
🔗 [阅读原文]({article_data['source_url']})  
{model_info}

{article_data['content']}
"""
    
    # 写入文件
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        logger.info(f"文章已保存为Markdown: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"保存Markdown文件时出错: {str(e)}")
        raise


def save_article_to_db(article_data: Dict[str, Any]) -> Optional[int]:
    """
    将文章保存到SQLite数据库
    
    Args:
        article_data: 文章数据，包含title, content, source_url, published_date, model_used(可选)
        
    Returns:
        文章ID，如果保存失败则返回None
    """
    # 确保database目录存在
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    try:
        # 连接到数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 创建表（如果不存在）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            source_url TEXT,
            published_date TEXT,
            model_used TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 插入文章数据
        cursor.execute('''
        INSERT INTO articles (title, content, source_url, published_date, model_used)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            article_data["title"],
            article_data["content"],
            article_data["source_url"],
            article_data["published_date"],
            article_data.get("model_used", "unknown")
        ))
        
        # 提交事务并获取文章ID
        conn.commit()
        article_id = cursor.lastrowid
        
        # 关闭连接
        conn.close()
        
        logger.info(f"文章已保存到数据库，ID: {article_id}")
        return article_id
    
    except Exception as e:
        logger.error(f"保存到数据库时出错: {str(e)}")
        return None


def get_article_from_db(article_id: int) -> Optional[Dict[str, Any]]:
    """
    从数据库中获取文章
    
    Args:
        article_id: 文章ID
        
    Returns:
        文章数据，如果未找到则返回None
    """
    try:
        # 连接到数据库
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
        cursor = conn.cursor()
        
        # 查询文章
        cursor.execute('SELECT * FROM articles WHERE id = ?', (article_id,))
        row = cursor.fetchone()
        
        # 关闭连接
        conn.close()
        
        if row:
            # 将行转换为字典
            article = {key: row[key] for key in row.keys()}
            return article
        else:
            logger.warning(f"未找到ID为{article_id}的文章")
            return None
    
    except Exception as e:
        logger.error(f"从数据库获取文章时出错: {str(e)}")
        return None


def list_articles(limit: int = 10) -> list:
    """
    列出最近的文章
    
    Args:
        limit: 要返回的最大文章数量
        
    Returns:
        文章列表，每个文章包含id, title, published_date, model_used
    """
    try:
        # 连接到数据库
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 查询最近的文章
        cursor.execute('''
        SELECT id, title, published_date, model_used, created_at
        FROM articles
        ORDER BY created_at DESC
        LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        
        # 关闭连接
        conn.close()
        
        # 将行转换为字典列表
        articles = [{key: row[key] for key in row.keys()} for row in rows]
        return articles
    
    except Exception as e:
        logger.error(f"列出文章时出错: {str(e)}")
        return []


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 测试数据
    test_article = {
        "title": "GPT-4o震撼发布：AI多模态能力迎来质的飞跃",
        "content": "这是一篇测试文章的内容...",
        "source_url": "https://example.com/news/1",
        "published_date": "2023-05-20",
        "model_used": "gpt-4o"
    }
    
    # 测试保存文章
    md_path = save_article_to_markdown(test_article)
    print(f"文章已保存为Markdown: {md_path}")
    
    article_id = save_article_to_db(test_article)
    print(f"文章已保存到数据库，ID: {article_id}")
    
    # 测试获取文章
    if article_id:
        article = get_article_from_db(article_id)
        if article:
            print(f"从数据库获取的文章标题: {article['title']}")
            print(f"使用的模型: {article['model_used']}")
    
    # 测试列出文章
    articles = list_articles(5)
    print(f"最近的{len(articles)}篇文章:")
    for article in articles:
        print(f"- {article['id']}: {article['title']} (模型: {article['model_used']})") 