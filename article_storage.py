#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文章存储模块

将生成的文章保存为Markdown格式和存储到SQLite数据库。
"""

import os
import sqlite3
from datetime import datetime
from typing import Dict, Any
import logging
import re

# 配置日志
logger = logging.getLogger(__name__)

def clean_markdown_text(markdown_text: str) -> str:
    """
    清理Markdown文本中的特殊符号和格式标记
    
    Args:
        markdown_text: 原始的Markdown文本
        
    Returns:
        清理后的纯文本
    """
    # 保存原始的换行，用特殊标记替代
    text = markdown_text.replace('\n\n', '[PARAGRAPH]')
    text = text.replace('\n', ' ')
    
    # 移除Markdown标题标记 (# 号)
    text = re.sub(r'#{1,6}\s+', '', text)
    
    # 移除粗体和斜体标记
    text = re.sub(r'\*\*|__', '', text)
    text = re.sub(r'\*|_', '', text)
    
    # 移除列表标记
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # 移除链接，只保留文本
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # 移除图片标记
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', text)
    
    # 移除代码块
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', '', text)
    
    # 移除引用标记
    text = re.sub(r'^\s*>\s+', '', text, flags=re.MULTILINE)
    
    # 移除水平分割线
    text = re.sub(r'\n\s*[-*_]{3,}\s*\n', '\n\n', text)
    
    # 恢复段落换行
    text = text.replace('[PARAGRAPH]', '\n\n')
    
    # 清理多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    
    # 清理首尾空白
    text = text.strip()
    
    return text

def save_article_to_markdown(article: Dict[str, Any], output_dir: str = "articles", clean: bool = True) -> str:
    """
    将文章保存为Markdown格式和纯文本格式
    
    Args:
        article: 包含文章信息的字典
        output_dir: 输出目录
        clean: 是否同时生成清理后的纯文本版本
        
    Returns:
        保存的Markdown文件路径
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    date_str = datetime.now().strftime("%Y%m%d")
    safe_title = "".join(x for x in article["title"] if x.isalnum() or x in (' ', '-', '_'))
    safe_title = safe_title[:50]  # 限制标题长度
    filename = f"{date_str}-{safe_title}.md"
    filepath = os.path.join(output_dir, filename)
    
    # 构建Markdown内容
    content = f"""# {article['title']}

📅 {article.get('published_date', datetime.now().strftime("%Y-%m-%d"))}  
🔗 [阅读原文]({article.get('original_link', '')})  
🤖 模型: {article.get('model', 'unknown')}

{article['content']}
"""
    
    try:
        # 保存原始Markdown版本
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"已保存Markdown文件: {filepath}")
        
        # 如果需要清理Markdown格式
        if clean:
            cleaned_content = clean_markdown_text(content)
            clean_filepath = os.path.join(output_dir, f"{date_str}-{safe_title}.txt")
            with open(clean_filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            logger.info(f"已保存纯文本文件: {clean_filepath}")
    
    except Exception as e:
        logger.error(f"保存文件时出错: {str(e)}")
        raise
    
    return filepath

def save_article_to_db(article: Dict[str, Any], db_path: str = "database/articles.db") -> int:
    """
    将文章保存到SQLite数据库
    
    Args:
        article: 包含文章信息的字典
        db_path: 数据库文件路径
        
    Returns:
        新插入记录的ID
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # 创建数据库连接
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 创建文章表（如果不存在）
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            original_link TEXT,
            published_date TEXT,
            model TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 准备纯文本版本的内容
        cleaned_content = clean_markdown_text(article['content'])
        
        # 插入文章
        cursor.execute("""
        INSERT INTO articles (title, content, original_link, published_date, model)
        VALUES (?, ?, ?, ?, ?)
        """, (
            article['title'],
            cleaned_content,  # 使用清理后的内容
            article.get('original_link', ''),
            article.get('published_date', datetime.now().strftime("%Y-%m-%d")),
            article.get('model', 'unknown')
        ))
        
        # 获取新插入记录的ID
        article_id = cursor.lastrowid
        
        # 提交事务
        conn.commit()
        logger.info(f"已将文章保存到数据库，ID: {article_id}")
        
        return article_id
    
    except Exception as e:
        conn.rollback()
        logger.error(f"保存到数据库时出错: {str(e)}")
        raise
    
    finally:
        conn.close()

def save_article(article: Dict[str, Any], output_dir: str = "articles", 
                db_path: str = "database/articles.db", clean: bool = True) -> tuple:
    """
    保存文章到Markdown文件和数据库
    
    Args:
        article: 包含文章信息的字典
        output_dir: Markdown文件输出目录
        db_path: 数据库文件路径
        clean: 是否生成清理后的纯文本版本
        
    Returns:
        (文件路径, 数据库ID)的元组
    """
    try:
        # 保存为Markdown文件
        filepath = save_article_to_markdown(article, output_dir, clean)
        
        # 保存到数据库
        article_id = save_article_to_db(article, db_path)
        
        return filepath, article_id
    
    except Exception as e:
        logger.error(f"保存文章时出错: {str(e)}")
        raise

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 测试文章
    test_article = {
        "title": "测试文章：AI最新突破",
        "content": """
# AI领域重大突破

## 主要更新

- 更强的理解能力
- 更快的响应速度

**重要提示**：这是一个重大更新。

> 引用：这是一个测试引用

```python
print("这是一个代码块")
```

详情请看[这里](https://example.com)
""",
        "original_link": "https://example.com",
        "published_date": "2024-02-20",
        "model": "gpt-4o"
    }
    
    # 测试保存功能
    try:
        filepath, article_id = save_article(test_article)
        print(f"文章已保存：\n- Markdown文件：{filepath}\n- 数据库ID：{article_id}")
    except Exception as e:
        print(f"保存文章时出错：{str(e)}") 