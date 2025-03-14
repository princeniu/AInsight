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
import re

# 配置日志
logger = logging.getLogger(__name__)

# 数据库路径
DB_PATH = os.path.join("database", "articles.db")

def format_filename(title: str) -> str:
    """
    格式化标题为合法的文件名
    
    Args:
        title: 原始标题
        
    Returns:
        格式化后的文件名
    """
    # 替换特殊字符为下划线或空字符
    # 1. 替换常见中文标点
    title = re.sub(r'[【】《》「」『』（）、，。：；？！]', '', title)
    # 2. 替换常见英文标点
    title = re.sub(r'[,.!@#$%^&*(){}\[\]<>?|/\\~`\'";:+=]', '', title)
    # 3. 替换空白字符为下划线
    title = re.sub(r'\s+', '_', title)
    # 4. 移除任何剩余的不可见字符
    title = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', title)
    # 5. 转换为小写并限制长度
    title = title.lower()[:50]
    # 6. 确保文件名不以点或下划线开头
    title = title.lstrip('._')
    # 7. 如果文件名为空，使用默认名称
    if not title:
        title = 'article'
    return title

def clean_text_content(text: str) -> str:
    """
    清理文本内容，只去除特定的Markdown格式符号
    
    Args:
        text: 原始文本
        
    Returns:
        清理后的文本
    """
    # 1. 移除特定的Markdown标记符号
    text = re.sub(r'\*\*', '', text)  # 移除加粗标记 **
    text = re.sub(r'---+', '', text)  # 移除分隔线 ---
    text = re.sub(r'###\s+', '', text)  # 移除三级标题标记
    text = re.sub(r'##\s+', '', text)  # 移除二级标题标记
    
    # 2. 规范化空白字符
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # 将多个连续空行替换为两个换行
    text = text.strip()  # 移除首尾空白
    
    return text

def save_article_to_markdown(article_data: Dict[str, Any]) -> tuple[str, str]:
    """
    将文章保存为Markdown文件和纯文本文件
    
    Args:
        article_data: 文章数据，包含title, content, source_url, published_date, model_used(可选)
        
    Returns:
        (markdown文件路径, 文本文件路径)的元组
    """
    # 确保articles目录存在
    os.makedirs("articles", exist_ok=True)
    
    # 格式化标题作为文件名
    safe_title = format_filename(article_data["title"])
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_filename = f"{timestamp}_{safe_title}.md"
    txt_filename = f"{timestamp}_{safe_title}.txt"
    md_path = os.path.join("articles", md_filename)
    txt_path = os.path.join("articles", txt_filename)
    
    # 准备Markdown内容
    model_info = f"模型: {article_data.get('model_used', 'unknown')}" if 'model_used' in article_data else ""
    
    markdown_content = f"""# {article_data['title']}

📅 {article_data['published_date']}  
🔗 [阅读原文]({article_data['source_url']})  
{model_info}

{article_data['content']}
"""
    
    # 准备纯文本内容
    text_content = f"""{clean_text_content(article_data['title'])}

发布日期：{article_data['published_date']}
原文链接：{article_data['source_url']}
{model_info}

{clean_text_content(article_data['content'])}
"""
    
    try:
        # 保存Markdown文件
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        logger.info(f"文章已保存为Markdown: {md_path}")
        
        # 保存纯文本文件
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text_content)
        logger.info(f"文章已保存为纯文本: {txt_path}")
        
        return md_path, txt_path
    except Exception as e:
        logger.error(f"保存文件时出错: {str(e)}")
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


def check_news_exists(title: str, source_url: str = None) -> bool:
    """
    检查新闻是否已经存在于数据库中
    
    Args:
        title: 新闻标题
        source_url: 新闻源URL（可选）
        
    Returns:
        如果新闻已存在返回True，否则返回False
    """
    try:
        # 连接到数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 首先检查标题是否完全匹配
        cursor.execute('SELECT COUNT(*) FROM articles WHERE title = ?', (title,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return True
            
        # 如果有source_url，也检查URL是否匹配
        if source_url:
            cursor.execute('SELECT COUNT(*) FROM articles WHERE source_url = ?', (source_url,))
            if cursor.fetchone()[0] > 0:
                conn.close()
                return True
        
        conn.close()
        return False
        
    except Exception as e:
        logger.error(f"检查新闻是否存在时出错: {str(e)}")
        return False


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
    md_path, txt_path = save_article_to_markdown(test_article)
    print(f"文章已保存为Markdown: {md_path}")
    print(f"文章已保存为纯文本: {txt_path}")
    
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